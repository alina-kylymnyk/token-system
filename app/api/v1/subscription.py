from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import require_user
from app.services import subscription_service, credit_service
from app.schemas import (
    UserSubscriptionInfo,
    SubscriptionPlansListResponse,
    SubscriptionPlanRead,
    CreditBalanceRead
)

router = APIRouter()

@router.get("/", response_model=UserSubscriptionInfo)
async def get_user_subscription(
    user_id: str = Depends(require_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's subscription information

    Returns:
    Subscription information and credit balance
    """
    try:
        # Get balance
        balance_info = credit_service.get_balance(user_id=user_id, db=db)
        
        if not balance_info.subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User has no active subscription"
            )
        
        # Get subscription details
        subscription = subscription_service.get_subscription_details(
            tier=balance_info.subscription["tier"],
            db=db
        )
        
        return UserSubscriptionInfo(
            subscription=subscription,
            credits=CreditBalanceRead(**balance_info.credits)
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/plans", response_model=SubscriptionPlansListResponse)
async def get_subscription_plans(
    db: Session = Depends(get_db)
):
    """
    Get a list of available tariff plans

    Returns:
    List of all active tariff plans
    """
    try:
        plans = subscription_service.get_all_plans(active_only=True, db=db)
        return plans
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    

    

