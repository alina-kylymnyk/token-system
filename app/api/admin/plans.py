from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import get_db
from app.core.security import require_admin_token
from app.services import subscription_service
from app.db.models import SubscriptionPlan, SystemSettings
from app.schemas import (
    SubscriptionPlanCreate,
    SubscriptionPlanUpdate,
    SubscriptionPlanRead,
    AdminPlansListResponse,
    PlanDeleteResponse,
    MultiplierUpdateRequest,
    MultiplierUpdateResponse,
    PurchaseRateUpdateRequest,
    PurchaseRateUpdateResponse
)

router = APIRouter()


@router.get("/", response_model=AdminPlansListResponse)
async def get_all_plans(
    active_only: bool = Query(False, description="Тільки активні плани"),
    db: Session = Depends(get_db),
    _token: str = Depends(require_admin_token)
):
    """
    Get a list of all tariff plans with extended information

    - **active_only**: Show only active plans

    Returns:
    List of plans with number of users
    """
    try:
        plans = subscription_service.get_admin_plans(active_only=active_only, db=db)
        return plans
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
@router.post("/", response_model=SubscriptionPlanRead, status_code=status.HTTP_201_CREATED)
async def create_plan(
    plan_data: SubscriptionPlanCreate,
    db: Session = Depends(get_db),
    _token: str = Depends(require_admin_token)
):
    """
    Create a new plan

    - **tier**: Subscription level (basic, standard, premium)
    - **name**: Plan name
    - **monthly_cost**: Monthly cost
    - **credits_included**: Basic credits
    - **bonus_credits**: Bonus credits
    - **multiplier**: Deduction multiplier
    - **purchase_rate**: Credit purchase rate

    Returns:
    Plan created
    """
    try:
        plan = subscription_service.create_plan(plan_data=plan_data, db=db)
        return plan
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
@router.put("/{tier}", response_model=SubscriptionPlanRead)
async def update_plan(
    tier: str,
    plan_data: SubscriptionPlanUpdate,
    db: Session = Depends(get_db),
    _token: str = Depends(require_admin_token)
):
    """
    Updating a tariff plan

    - **tier**: Subscription level to update
    - All fields are optional - only the values ​​passed are updated

    Returns:
    Updated tariff plan
    """
    try:
        plan = subscription_service.update_plan(tier=tier, plan_data=plan_data, db=db)
        return plan
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
    
@router.delete("/{tier}", response_model=PlanDeleteResponse)
async def delete_plan(
    tier: str,
    db: Session = Depends(get_db),
    _token: str = Depends(require_admin_token)
):
    """
    Deleting a plan

    - **tier**: Subscription level to delete

    NOTE: You cannot delete a plan if there are users with this subscription

    Returns:
    Confirmation of deletion
    """
    try:
        subscription_service.delete_plan(tier=tier, db=db)
        return PlanDeleteResponse(
            success=True,
            message="Subscription plan deleted",
            tier=tier
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
@router.patch("/{tier}/multiplier", response_model=MultiplierUpdateResponse)
async def update_multiplier(
    tier: str,
    request: MultiplierUpdateRequest,
    db: Session = Depends(get_db),
    _token: str = Depends(require_admin_token)
):
    """
    Update charge multiplier for a plan

    - **tier**: Subscription tier
    - **multiplier**: New multiplier (must be > 0)

    Returns:
    Update information
    """
    try:
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.tier == tier
        ).first()

        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subscription plan not found: {tier}"
            )
        
        old_multiplier = plan.multiplier
        plan.multiplier = request.multiplier
        plan.updated_at = datetime.utcnow()

        db.commit()

        return MultiplierUpdateRequest(
            success=True,
            tier=tier,
            old_multiplier=old_multiplier,
            new_multiplier=request.multiplier,
            updated_at=plan.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
@router.patch("/{tier}/purchase-rate", response_model=PurchaseRateUpdateResponse)
async def update_purchase_rate(
    tier: str,
    request: PurchaseRateUpdateRequest,
    db: Session = Depends(get_db),
    _token: str = Depends(require_admin_token)
):
    """
    Update credit purchase rate for a plan

    - **tier**: Subscription tier
    - **purchase_rate**: New rate (must be >= 1.0)

    Returns:
    Update information
    """
    try:
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.tier == tier
        ).first()

        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subscription plan not found: {tier}"
            )
        
        old_purchase_rate = plan.purchase_rate
        plan.purchase_rate = request.purchase_rate
        plan.updated_at = datetime.utcnow()
        
        db.commit()

        return PurchaseRateUpdateResponse(
            success=True,
            tier=tier,
            old_purchase_rate=old_purchase_rate,
            new_purchase_rate=request.purchase_rate,
            updated_at=plan.updated_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
    
    
    
    