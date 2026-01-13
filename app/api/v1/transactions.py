from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.core.security import require_user
from app.services import transaction_service
from app.schemas import TransactionListResponse

router = APIRouter()

@router.get(f"/", response_model=TransactionListResponse)
async def get_transactions(
    limit: int = Query(50, ge=1, le=100, description="Number of records"),
    offset: int = Query(0, ge=0, description="Offset"),
    type: Optional[str] = Query(None, description="Filter by transaction type"),
    user_id: str = Depends(require_user),
    db: Session = Depends(get_db)
):
    """
    Get transaction history of current user

    - **limit**: Maximum number of records (1-100)
    - **offset**: Offset for pagination
    - **type**: Optional filter by type (charge, add, subscription, bonus, refund)

    Returns:
    List of transactions with pagination
    """
    try:
        transactions = transaction_service.get_user_transactions(
            user_id=user_id,
            limit=limit,
            offset=offset,
            transaction_type=type,
            db=db
        )
        return transactions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
