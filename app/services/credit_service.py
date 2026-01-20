from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, Tuple
from decimal import Decimal
import uuid
import logging

from app.db.models import User, CreditBalance, Transaction, SubscriptionPlan
from app.db.models import TransactionType
from app.schemas import (
    CreditChargeResponse,
    CreditChargeErrorResponse,
    CreditAddResponse,
    CreditCalculateResponse,
    CreditCheckResponse,
    CreditBalanceResponse
)
from app.core.config import settings
from app.core.cache import cache_service

from app.utils.database import atomic_transaction, pessimistic_lock
from app.utils.idempotency import idempotency_manager

logger = logging.getLogger(__name__)

class CreditService:
    """
    Service responsible for all credit-related operations:
    - conversion between USD and credits
    - balance checks
    - charging credits
    - adding credits
    """
    @staticmethod
    def calculate_credits_from_usd(
        amount_usd: float,
        multiplier: float = 1.0
    ) -> int:
        """
        Convert USD amount to credits.

        Args:
            amount_usd: Amount in USD
            multiplier: Multiplier depending on subscription or purchase rate

        Returns:
            Integer number of credits
        """
        credits = amount_usd * multiplier * settings.BASE_EXCHANGE_RATE
        return round(credits)
    
    @staticmethod
    def calculate_credits_to_charge(
        cost_usd: int,
        subscription_tier: str,
        db: Session
    ) -> Tuple[int, float]:
        """
        Calculate how many credits should be charged for an operation.

        Args:
            cost_usd: Operation cost in USD
            subscription_tier: User subscription tier
            db: Database session

        Returns:
            Tuple (credits_to_charge, multiplier)
        """
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.tier == subscription_tier
        ).first()

        if not plan:
            raise ValueError(f"Subscription plan not found: {subscription_tier}")
        
        multiplier = plan.multiplier
        credits = CreditService.calculate_credits_from_usd(cost_usd, multiplier)

        return credits, multiplier

    @staticmethod
    def check_sufficient_credits(
        user_id: str,
        required_credits: int,
        db: Session
    ) -> CreditCheckResponse:
        """
        Check if a user has enough credits.

        Args:
            user_id: User ID
            required_credits: Required credits
            db: Database session

        Returns:
            CreditCheckResponse

        Raises:
            ValueError: If user not found
        """
        # First check if user exists (consistent with get_balance behavior)
        user = db.query(User).filter(User.user_id == user_id).first()

        if not user:
            raise ValueError(f"User not found: {user_id}")

        # Try to get balance from cache
        cached_balance = cache_service.get_cached_balance(user_id)

        if cached_balance is not None:
            balance = cached_balance
        else:
            credit_balance = db.query(CreditBalance).filter(
                CreditBalance.user_id == user_id
            ).first()

            balance = credit_balance.balance if credit_balance else 0
            cache_service.cache_balance(user_id, balance)

        # User exists but has no subscription
        if not user.subscription_tier:
            return CreditCheckResponse(
                user_id=user_id,
                has_subscription=False,
                subscription_tier=None,
                balance=balance,
                sufficient=balance >= required_credits if required_credits else True,
                multiplier=None
            )
        
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.tier == user.subscription_tier
        ).first()

        return CreditCheckResponse(
            user_id=user_id,
            has_subscription=True,
            subscription_tier=user.subscription_tier,
            balance=balance,
            sufficient=balance >= required_credits if required_credits else True,
            multiplier=plan.multiplier if plan else None
        )


    @staticmethod
    def get_balance(user_id: str, db: Session) -> CreditBalanceResponse:
        """
        Get full credit balance information for a user.

        Args:
            user_id: User ID
            db: Database session

        Returns:
            CreditBalanceResponse
        """
        user = db.query(User).filter(User.user_id == user_id).first()

        if not user:
            raise ValueError(f"User not found: {user_id}")
        
        credit_balance = db.query(CreditBalance).filter(
            CreditBalance.user_id == user_id
        ).first()

        if not credit_balance:
            credit_balance = CreditBalance(
                user_id=user_id,
                balance=0,
                total_earned=0,
                total_spent=0
            )
            db.add(credit_balance)
            db.commit()
            db.refresh(credit_balance)

        subscription_info = None
        if user.subscription_tier:
            plan = db.query(SubscriptionPlan).filter(
                SubscriptionPlan.tier == user.subscription_tier
            ).first()

            if plan:
                subscription_info = {
                    "tier": plan.tier,
                    "monthly_cost": plan.monthly_cost,
                    "multiplier": plan.multiplier,
                    "purchase_rate": plan.purchase_rate
                }

        return CreditBalanceResponse(
            user_id=user_id,
            subscription=subscription_info,
            credits={
                "balance": credit_balance.balance,
                "total_earned": credit_balance.total_earned,
                "total_spent": credit_balance.total_spent
            }
        )

    
    @staticmethod
    def calculate(
        user_id: str,
        cost_usd: float,
        db: Session
    ) -> CreditCalculateResponse:
        """
        Calculate credit cost without charging.

        Args:
            user_id: User ID
            cost_usd: Cost in USD
            db: Database session

        Returns:
            CreditCalculateResponse
        """
        user = db.query(User).filter(User.user_id == user_id).first()

        if not user:
            raise ValueError(f"User not found: {user_id}")
        
        if not user.subscription_tier:
            raise ValueError(f"User has no subscription: {user_id}")
        
        credits_to_charge, multiplier = CreditService.calculate_credits_to_charge(
            cost_usd=cost_usd, 
            subscription_tier=user.subscription_tier,
            db=db
        )

        credit_balance = db.query(CreditBalance).filter(
            CreditBalance.user_id == user_id
        ).first()

        current_balance = credit_balance.balance if credit_balance else 0
        balance_after = current_balance - credits_to_charge

        return CreditCalculateResponse(
            user_id=user_id,
            cost_usd=cost_usd,
            credits_to_charge=credits_to_charge,
            multiplier=multiplier,
             current_balance=current_balance,
             balance_after=balance_after, 
             sufficient=balance_after >=0
        )
        
        
    @staticmethod
    def charge_credits(
        user_id: str,
        cost_usd: float,
        operation_id: str,
        description: Optional[str] = None,
        metadata: Optional[dict] = None,
        db: Session = None

    )-> CreditChargeResponse | CreditChargeErrorResponse:
        """
        Atomically charge credits from a user's balance.

        This operation is:
        - idempotent (safe to retry)
        - transactional
        - protected from race conditions

        Args:
            user_id: User ID
            cost_usd: Operation cost in USD
            operation_id: Unique operation identifier (idempotency key)
            description: Optional description
            metadata: Optional metadata
            db: Database session

        Returns:
            CreditChargeResponse or CreditChargeErrorResponse        
        """
        from app.services.transaction_service import TransactionService

        # Idempotence check (with user_id to prevent Idempotency Hijacking)
        existing_transaction = idempotency_manager.check_operation(operation_id, db, user_id=user_id)

        if existing_transaction:
            logger.info(f"Idempotent charge operation: {operation_id}")
            return CreditChargeResponse(
                success=True,
                transaction_id=existing_transaction.transaction_id,
                user_id=existing_transaction.user_id,
                cost_usd=existing_transaction.cost_usd,
                credits_charged=abs(existing_transaction.credits),
                balance_before=existing_transaction.balance_after + abs(existing_transaction.credits),
                balance_after=existing_transaction.balance_after,
                operation_id=existing_transaction.operation_id
            )
        
        try:
            with atomic_transaction(db):
                # Get the user
                user = db.query(User).filter(User.user_id == user_id).first()

                if not user:
                    raise ValueError(f"User not found: {user_id}")

                if not user.subscription_tier:
                    raise ValueError(f"User has no subscription: {user_id}")

                # Calculate credits for charging
                credits_to_charge, multiplier = CreditService.calculate_credits_to_charge(
                    cost_usd=cost_usd,
                    subscription_tier=user.subscription_tier,
                    db=db
                )

                with pessimistic_lock(db, CreditBalance, CreditBalance.user_id == user_id) as credit_balance:

                    if not credit_balance:
                        # Create balance if it doesn't exist
                        credit_balance = CreditBalance(
                            user_id=user_id,
                            balance=0,
                            total_earned=0,
                            total_spent=0
                        )
                        db.add(credit_balance)
                        db.flush()

                    balance_before = credit_balance.balance

                    if credit_balance.balance < credits_to_charge:
                        deficit = credits_to_charge - credit_balance.balance
                        logger.warning(
                            f"Insufficient credits: user={user_id}, "
                            f"required={credits_to_charge}, available={credit_balance.balance}"
                        )
                        return CreditChargeErrorResponse(
                            success=False,
                            error="insufficient_credits",
                            user_id=user_id,
                            required_credits=credits_to_charge,
                            current_balance=credit_balance.balance,
                            deficit=deficit
                        )

                    credit_balance.balance -= credits_to_charge
                    credit_balance.total_spent += credits_to_charge
                    balance_after = credit_balance.balance

                    transaction_id = f"txn_{uuid.uuid4().hex[:12]}"
                    transaction = TransactionService.create_transaction(
                        transaction_id=transaction_id,
                        user_id=user_id,
                        transaction_type=TransactionType.CHARGE,
                        operation_id=operation_id,
                        cost_usd=cost_usd,
                        credits=-credits_to_charge,
                        balance_after=balance_after,
                        description=description,
                        meta_info=metadata or {},
                        db=db
                    )

            # Invalidate cache after successful transaction
            cache_service.invalidate_balance(user_id)

            logger.info(
                f"Credits charged successfully: user={user_id}, "
                f"amount={credits_to_charge}, operation={operation_id}"
            )

            return CreditChargeResponse(
                success=True,
                transaction_id=transaction_id,
                user_id=user_id,
                cost_usd=cost_usd,
                credits_charged=credits_to_charge,
                balance_before=balance_before,
                balance_after=balance_after,
                operation_id=operation_id
            )
        
        except ValueError as e:
        # ValueError is a business logic error, not a DB error
            raise e
        except Exception as e:
            logger.error(f"Error charging credits: {e}")
            raise e
        

    @staticmethod
    def add_credits(
        user_id: str,
        amount_usd: float,
        source: str,
        operation_id: str,
        description: Optional[str] = None,
        metadata: Optional[dict] = None,
        db: Session = None
    ) -> CreditAddResponse:
        """
        Adding Credits

        Args:
        user_id: User ID
        amount_usd: Amount in dollars
        source: Source (purchase, subscription, bonus, refund)
        operation_id: Unique operation ID
        description: Description
        metadata: Additional data
        db: Database session

        Returns:
        CreditAddResponse
        """
        from app.services.transaction_service import TransactionService

        # Idempotence check (with user_id to prevent Idempotency Hijacking)
        existing_transaction = idempotency_manager.check_operation(operation_id, db, user_id=user_id)

        if existing_transaction:
            logger.info(f"Idempotent add operation: {operation_id}")
            purchase_rate = existing_transaction.meta_info.get('purchase_rate', 1.0) if existing_transaction.meta_info else 1.0
            return CreditAddResponse(
                success=True,
                transaction_id=existing_transaction.transaction_id,
                user_id=existing_transaction.user_id,
                amount_usd=existing_transaction.cost_usd or amount_usd,
                credits_added=existing_transaction.credits,
                purchase_rate=1.0,  # Можна витягнути з metadata
                balance_before=existing_transaction.balance_after - existing_transaction.credits,
                balance_after=existing_transaction.balance_after,
                operation_id=existing_transaction.operation_id
            )
        
        try:
            with atomic_transaction(db):
                user = db.query(User).filter(User.user_id == user_id).first()

                if not user:
                    raise ValueError(f"User not found: {user_id}")
            
                # Get purchase_rate from subscription
                purchase_rate = 1.0
                if user.subscription_tier:
                    plan = db.query(SubscriptionPlan).filter(
                        SubscriptionPlan.tier == user.subscription_tier
                    ).first()

                    if plan:
                        purchase_rate = plan.purchase_rate

            
                # Calculate credits
                credits_to_add = CreditService.calculate_credits_from_usd(
                    amount_usd=amount_usd,
                    multiplier=purchase_rate
                )

                # Get or create a balance
                credit_balance = db.query(CreditBalance).filter(
                    CreditBalance.user_id == user_id
                    ).with_for_update().first()
                
                if not credit_balance:
                    credit_balance = CreditBalance(
                        user_id=user_id,
                        balance=0,
                        total_earned=0,
                        total_spent=0
                    )
                    db.add(credit_balance)
                    db.flush()

                balance_before = credit_balance.balance

                # Add credits
                credit_balance.balance += credits_to_add
                credit_balance.total_earned += credits_to_add
                balance_after = credit_balance.balance

            # Determine the transaction type
                transaction_type_map = {
                    "purchase": TransactionType.ADD,
                    "subscription": TransactionType.SUBSCRIPTION,
                    "bonus": TransactionType.BONUS,
                    "refund": TransactionType.REFUND
                }
                transaction_type = transaction_type_map.get(source, TransactionType.ADD)

                # Create transaction
                transaction_id = f"txn_{uuid.uuid4().hex[:12]}"
                transaction = TransactionService.create_transaction(
                    transaction_id=transaction_id,
                    user_id=user_id,
                    transaction_type=transaction_type,
                    operation_id=operation_id,
                    cost_usd=amount_usd if source == "purchase" else None,
                    credits=credits_to_add,
                    balance_after=balance_after,
                    description=description,
                    meta_info={**(metadata or {}), "source": source, "purchase_rate": purchase_rate},
                    db=db
                )

                db.commit()

            cache_service.invalidate_balance(user_id)

            logger.info(
                f"Credits added successfully: user={user_id}, "
                f"amount={credits_to_add}, operation={operation_id}"
            )

            return CreditAddResponse(
                success=True,
                transaction_id=transaction_id,
                user_id=user_id,
                amount_usd=amount_usd,
                credits_added=credits_to_add,
                purchase_rate=purchase_rate,
                balance_before=balance_before,
                balance_after=balance_after,
                operation_id=operation_id
            )
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error adding credits: {e}")
            raise e
        

credit_service = CreditService()








        




        















        
