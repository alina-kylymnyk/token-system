from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from app.db.session import get_db
from app.core.security import require_user
from app.services import credit_service
from app.schemas import (
    CreditPurchaseRequest,
    CreditPurchaseResponse
)

router = APIRouter()

@router.post("/purchase", response_model=CreditPurchaseResponse)
async def purchase_credits(
    request: CreditPurchaseRequest,
    user_id: str = Depends(require_user),
    db: Session = Depends(get_db)
):
    """
    Credits replenishment

    - **amount_usd**: Purchase amount in dollars (1-1000)
    - **payment_method_id**: Payment method ID from the payment system

    NOTE: In production, there should be integration with Stripe/PayPal

    Returns:
    Information about added credits and new balance
    """
    try:
        # In production this should be:
        # 1. Creating a payment intent in Stripe
        # 2. Payment confirmation
        # 3. Webhook processing

        # DEMO: Just adding credits
        operation_id = f"purchase_{uuid.uuid4().hex[:12]}"

        add_response = credit_service.add_credits(
            user_id=user_id,
            amount_usd=request.amount_usd,
            source="purchase",
            operation_id=operation_id,
            description=f"Credit purchase: ${request.amount_usd}",
            metadata={
                "payment_method_id": request.payment_method_id,
                "amount_usd": request.amount_usd
            },
            db=db
        )

        return CreditPurchaseResponse(
            success=True,
            transaction_id=add_response.transaction_id,
            amount_usd=request.amount_usd,
            credits_added=add_response.credits_added,
            new_balance=add_response.balance_after
        )
    
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
    
    



