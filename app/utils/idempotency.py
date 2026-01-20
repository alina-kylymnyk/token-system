from sqlalchemy.orm import Session
from typing import Optional, Callable, Any
from functools import wraps
import logging

from app.db.models import Transaction

logger = logging.getLogger(__name__)

class IdempotencyManager:
    """Operation Idempotence Manager"""

    @staticmethod
    def check_operation(operation_id: str, db: Session, user_id: Optional[str] = None) -> Optional[Transaction]:
        """
        Check if the operation has already been executed

        Args:
        operation_id: Unique operation ID
        db: Database session
        user_id: User ID (required for security - prevents Idempotency Hijacking)

        Returns:
        Transaction if the operation has already been executed for this user, None if not

        Security Note:
        Always provide user_id to prevent attackers from hijacking idempotency keys
        belonging to other users.
        """
        query = db.query(Transaction).filter(
            Transaction.operation_id == operation_id
        )

        # Security: verify user_id matches to prevent Idempotency Hijacking
        if user_id is not None:
            query = query.filter(Transaction.user_id == user_id)

        return query.first()
    
    @staticmethod
    def ensure_unique_operation(operation_id: str, db: Session) -> None:
        """
        Make sure operation_id is unique

        Args:
        operation_id: Unique operation ID
        db: Database session

        Raises:
        ValueError: If operation_id is already in use
        """
        existing = IdempotencyManager.check_operation(operation_id, db)
        if existing:
            raise ValueError(
                f"Operation with id '{operation_id}' already exists. "
                f"Transaction ID: {existing.transaction_id}"
            )
        
    def idempotent_operation(operation_type: str):
        """
        Decorator for ensuring idempotence of operations

        Args:
        operation_type: Operation type (charge, add, etc.)

        Example:
        @idempotent_operation("charge")
        def charge_credits(...):
        pass
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                operation_id = kwargs.get('operation_id')
                user_id = kwargs.get('user_id')
                db = kwargs.get('db')

                if not operation_id:
                    raise ValueError("operation_id is required for idempotent operations")

                if not user_id:
                    raise ValueError("user_id is required for idempotent operations")

                if not db:
                    raise ValueError("db session is required")

                # Idempotence check (with user_id to prevent Idempotency Hijacking)
                existing = IdempotencyManager.check_operation(operation_id, db, user_id=user_id)

                if existing:
                    logger.info(
                        f"Idempotent operation detected: {operation_type}, "
                        f"operation_id={operation_id}, user_id={user_id}, returning cached result"
                    )
                    # Return the result of the previous operation
                    return _reconstruct_response(existing, operation_type)

                # Perform operation
                return func(*args, **kwargs)

            return wrapper
        return decorator

                    
def _reconstruct_response(transaction: Transaction, operation_type: str) -> Any:
    """Reconstruct response from existing transaction"""
    from app.schemas import CreditChargeResponse, CreditAddResponse

    if operation_type == "charge":
        return CreditChargeResponse(
            success=True,
            transaction_id=transaction.transaction_id,
            user_id=transaction.user_id,
            cost_usd=transaction.cost_usd or 0,
            credits_charged=abs(transaction.credits),
            balance_before=transaction.balance_after + abs(transaction.credits),
            balance_after=transaction.balance_after,
            operation_id=transaction.operation_id
        )
    elif operation_type == "add":
        purchase_rate = transaction.meta_info.get('purchase_rate', 1.0) if transaction.meta_info else 1.0
        return CreditAddResponse(
            success=True,
            transaction_id=transaction.transaction_id,
            user_id=transaction.user_id,
            amount_usd=transaction.cost_usd or 0,
            credits_added=transaction.credits,
            purchase_rate=purchase_rate,
            balance_before=transaction.balance_after - transaction.credits,
            balance_after=transaction.balance_after,
            operation_id=transaction.operation_id
        )
    else:
        raise ValueError(f"Unknown operation type: {operation_type}")

idempotency_manager = IdempotencyManager()
        





