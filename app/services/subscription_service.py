from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from app.db.models import SubscriptionPlan, User, CreditBalance
from app.schemas import (
    SubscriptionPlanCreate,
    SubscriptionPlanUpdate,
    SubscriptionPlanRead,
    SubscriptionPlansListResponse,
    SubscriptionUpdateResponse,
    AdminPlanRead,
    AdminPlansListResponse
)
from app.services.credit_service import credit_service

class SubscriptionService:
    """Service for managing subscription plans and user subscriptions"""

    @staticmethod
    def get_all_plans(
        active_only: bool = True,
        db: Session = None
    ) -> SubscriptionPlansListResponse:
        """
        Get a list of all subscription plans

        Args:
            active_only: Return only active plans
            db: Database session

        Returns:
            SubscriptionPlansListResponse
        """
        query = db.query(SubscriptionPlan)

        if active_only:
            query = query.filter(SubscriptionPlan.active == True)

            plans = query.all()

            plans_read = [
                SubscriptionPlanRead(
                tier=plan.tier,
                name=plan.name,
                monthly_cost=plan.monthly_cost,
                fixed_cost=plan.fixed_cost,
                credits_included=plan.credits_included,
                bonus_credits=plan.bonus_credits,
                total_credits=plan.total_credits,
                multiplier=plan.multiplier,
                purchase_rate=plan.purchase_rate,
                active=plan.active,
                created_at=plan.created_at,
                updated_at=plan.updated_at
                )
                for plan in plans
            ]

            return SubscriptionPlansListResponse(plans=plans_read)
        
    @staticmethod
    def get_subscription_details(
        tier: str,
        db: Session
    ) -> SubscriptionPlanRead:
        """
        Get details of a specific subscription plan

        Args:
            tier: Subscription tier
            db: Database session

        Returns:
            SubscriptionPlanRead
        """
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.tier == tier
        ).first()

        if not plan:
            raise ValueError(f"Subscription plan not found: {tier}")
        
        return SubscriptionPlanRead(
            tier=plan.tier,
            name=plan.name,
            monthly_cost=plan.monthly_cost,
            fixed_cost=plan.fixed_cost,
            credits_included=plan.credits_included,
            bonus_credits=plan.bonus_credits,
            total_credits=plan.total_credits,
            multiplier=plan.multiplier,
            purchase_rate=plan.purchase_rate,
            active=plan.active,
            created_at=plan.created_at,
            updated_at=plan.updated_at
        )
    
    @staticmethod
    def create_plan(
        plan_data: SubscriptionPlanCreate,
        db: Session
    ) -> SubscriptionPlanRead:
        """
        Create a new subscription plan (Admin only)

        Args:
            plan_data: Subscription plan data
            db: Database session

        Returns:
            SubscriptionPlanRead
        """
        # Check if the plan already exists
        existing = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.tier == plan_data.tier
        ).first()

        if existing:
            raise ValueError(f"Subscription plan already exists: {plan_data.tier}")
        
        # Create new plan
        plan = SubscriptionPlan(
            tier=plan_data.tier,
            name=plan_data.name,
            monthly_cost=plan_data.monthly_cost,
            fixed_cost=plan_data.fixed_cost,
            credits_included=plan_data.credits_included,
            bonus_credits=plan_data.bonus_credits,
            multiplier=plan_data.multiplier,
            purchase_rate=plan_data.purchase_rate,
            active=plan_data.active
        )

        db.add(plan)
        db.commit()
        db.refresh(plan)

        return SubscriptionPlanRead.model_validate(plan)
    
    @staticmethod
    def update_plan(
        tier: str,
        plan_data: SubscriptionPlanUpdate,
        db: Session
    ) -> SubscriptionPlanRead:
        """
        Update an existing subscription plan (Admin only)

        Args:
            tier: Subscription tier
            plan_data: Updated data
            db: Database session

        Returns:
            SubscriptionPlanRead
        """

        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.tier == tier
        ).first()

        if not plan:
            raise ValueError(f"Subscription plan not found: {tier}")
        
        # Update only provided field
        update_data = plan_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(plan, field, value)

        plan.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(plan)

        return SubscriptionPlanRead.model_validate(plan)
    

    @staticmethod
    def delete_plan(
        tier: str,
        db: Session
    ) -> bool:
        """
        Delete a subscription plan (Admin only)

        Args:
            tier: Subscription tier
            db: Database session

        Returns:
            bool: True if deleted
        """
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.tier == tier
        ).first()

        if not plan:
            raise ValueError(f"Subscription plan not found: {tier}")
        
        # Check if there are users with this plan
        users_count = db.query(User).filter(
            User.subscription_tier == tier
        ).count()

        if users_count > 0:
            raise ValueError(
                f"Cannot delete plan with active users. "
                f"Users with this plan: {users_count}"
            )
        
        db.delete(plan)
        db.commit

        return True
    
    @staticmethod
    def update_subscription(
        user_id: str,
        subscription_tier: str,
        credits_to_add: int,
        operation_id: str,
        db: Session
    ) -> SubscriptionUpdateResponse:
        """
        Update user's subscription and add credits if needed

        Args:
            user_id: User ID
            subscription_tier: New subscription tier
            credits_to_add: Number of credits to add
            operation_id: Operation ID
            db: Database session

        Returns:
            SubscriptionUpdateResponse
        """
        # Get or create user
        user = db.query(User).filter(User.user_id == user_id).first()

        if not user:
            user = User(user_id=user_id, subscription_tier=subscription_tier)
            db.add(user)
            db.flush()
            previous_tier = None

        else:
            previous_tier = user.subscription_tier
            user.subscription_tier = subscription_tier
            user.updated_at = datetime.utcnow()

        # Get subscription plan
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.tier == subscription_tier
        ).first()

        if not plan:
            raise ValueError(f"Subscription plan not found: {subscription_tier}")
        
        # Add credits via CreditService
        if credits_to_add > 0:
            amount_usd = credits_to_add / (plan.purchase_rate * 10000)

            add_response = credit_service.add_credits(
                user_id=user_id,
                amount_usd=amount_usd,
                source="subscription",
                operation_id=operation_id,
                description=f"Subscription credits: {plan.name}",
                metadata={"tier": subscription_tier},
                db=db
            )

            new_balance = add_response.balance_after

        else:
            credit_balance = db.query(CreditBalance).filter(
                CreditBalance.user_id == user_id
            ).first()
            new_balance = credit_balance.balance if credit_balance else 0

        db.commit()

        return SubscriptionUpdateResponse(
            success=True,
            user_id=user_id,
            previous_tier=previous_tier,
            new_tier=subscription_tier,
            credits_added=credits_to_add,
            new_balance=new_balance,
            multiplier=plan.multiplier,
            purchase_rate=plan.purchase_rate
        )
    
    @staticmethod
    def get_admin_plans(
        active_only: bool = False,
        db: Session = None
    ) -> AdminPlansListResponse:
        """
        Get subscription plans with additional admin statistics

        Args:
            active_only: Return only active plans
            db: Database session

        Returns:
            AdminPlansListResponse
        """
        query = db.query(
            SubscriptionPlan,
            func.count(User.user_id).label("users_count")
        ).outerjoin(
            User, User.subscription_tier == SubscriptionPlan.tier
        ).group_by(SubscriptionPlan.tier)

        if active_only:
            query = query.filter(SubscriptionPlan.active == True)

        results = query.all()

        plans = [
            AdminPlanRead(
                tier=plan.tier,
                name=plan.name,
                monthly_cost=plan.monthly_cost,
                fixed_cost=plan.fixed_cost,
                credits_included=plan.credits_included,
                bonus_credits=plan.bonus_credits,
                multiplier=plan.multiplier,
                purchase_rate=plan.purchase_rate,
                active=plan.active,
                users_count=users_count,
                created_at=plan.created_at,
                updated_at=plan.updated_at
            )
            for plan, users_count in results
        ]

        return AdminPlansListResponse(plans=plans)

subscription_service = SubscriptionService()









    
        
    




