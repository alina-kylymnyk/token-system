from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import subscription_service
from app.schemas import (
    SubscriptionUpdateRequest,
    SubscriptionUpdateResponse
)

from app.core.security import require_service_token


router = APIRouter()


@router.post("/update", response_model=SubscriptionUpdateResponse)
async def update_subscription(
    request: SubscriptionUpdateRequest,
    db: Session = Depends(get_db),
    _token: str = Depends(require_service_token)
):
    """
    User Subscription Update

    - **user_id**: User ID
    - **subscription_tier**: New subscription tier (basic, standard, premium)
    - **credits_to_add**: Number of credits to add
    - **operation_id**: Unique operation ID
    """
    try:
        response = subscription_service.update_subscription(
            user_id=request.user_id,
            subscription_tier=request.subscription_tier,
            credits_to_add=request.credits_to_add,
            operation_id=request.operation_id,
            db=db
        )
        return response
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