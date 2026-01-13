from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.security import require_service_token
from app.db.session import get_db
from app.services import credit_service
from app.schemas import (
    CreditCheckResponse,
    CreditCalculateRequest,
    CreditCalculateResponse,
    CreditChargeRequest,
    CreditChargeResponse,
    CreditChargeErrorResponse,
    CreditAddRequest,
    CreditAddResponse,
    CreditBalanceResponse
)

router = APIRouter()

@router.get("/check/{user_id}", response_model=CreditCheckResponse)
async def check_credits(
    user_id: str,
    required_credits: Optional[int] = Query(None, description="Minimum number of credits"),
    db: Session = Depends(get_db),
    _token: str = Depends(require_service_token)
):
    """
    Checking for user credits

    - **user_id**: User ID
    - **required_credits**: Optional - minimum amount to check
    """
    try:
        response = credit_service.check_sufficient_credits(
            user_id=user_id,
            required_credits=required_credits or 0,
            db=db
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/calculate", response_model=CreditCalculateResponse)
async def calculate_credits(
    request: CreditCalculateRequest,
    db: Session = Depends(get_db),
    _token: str = Depends(require_service_token)
):
    """
    Calculation of the cost of the transaction WITHOUT writing off

    - **user_id**: User ID
    - **cost_usd**: Cost of the transaction in dollars
    """
    try:
        response = credit_service.calculate(
            user_id=request.user_id,
            cost_usd=request.cost_usd,
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
    
@router.post("/charge")
async def charge_credits(
    request: CreditChargeRequest,
    db: Session = Depends(get_db),
    _token: str = Depends(require_service_token)
):
    """
    Credit Charge (ATOMIC operation with idempotence)

    - **user_id**: User ID
    - **cost_usd**: Operation cost
    - **operation_id**: Unique operation ID (for idempotence)
    - **description**: Operation description
    - **metadata**: Additional data

    Returns:
    CreditChargeResponse (success) or CreditChargeErrorResponse (error)
    """
    try:
        response = credit_service.charge_credits(
            user_id=request.user_id,
            cost_usd=request.cost_usd,
            operation_id=request.operation_id,
            description=request.description,
            metadata=request.metadata,
            db=db
        )

        # If there are not enough credits, return 402 Payment Required
        if isinstance(response, CreditChargeErrorResponse):
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=response.model_dump()
            )
        
        return response
    
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
    

@router.post("/add", response_model=CreditAddResponse)
async def add_credits(
    request: CreditAddRequest,
    db: Session = Depends(get_db),
    _token: str = Depends(require_service_token)
):
    """
    Adding credits

    - **user_id**: User ID
    - **amount_usd**: Amount in dollars
    - **source**: Source (purchase, subscription, bonus, refund)
    - **operation_id**: Unique operation ID
    - **description**: Description
    - **metadata**: Additional data
    """
    try:
        response = credit_service.add_credits(
            user_id=request.user_id,
            amount_usd=request.amount_usd,
            source=request.source,
            operation_id=request.operation_id,
            description=request.description,
            metadata=request.metadata,
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
    

@router.get("/balance/{user_id}", response_model=CreditBalanceResponse)
async def get_balance(
    user_id: str,
    db: Session = Depends(get_db),
    _token: str = Depends(require_service_token)
):
    """
    Get full information about a user's balance

    - **user_id**: User ID
    """
    try:
        response = credit_service.get_balance(user_id=user_id, db=db)
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
    


    
    


    




    

