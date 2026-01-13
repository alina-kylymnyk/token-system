from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional

from app.db.session import get_db
from app.core.security import require_admin_token
from app.db.models import User, CreditBalance, Transaction, TransactionType
from app.schemas import StatisticsResponse

router = APIRouter()

@router.get("/", response_model=StatisticsResponse)
async def get_statistics(
    start_date: Optional[str] = Query(None, description="Start date(ISO 8601)"),
    end_date: Optional[str] = Query(None, description="End date (ISO 8601)"),
    tier: Optional[str] = Query(None, description="Filter by subscription type"),
    db: Session = Depends(get_db),
    _token: str = Depends(require_admin_token)
):
    """
    Retrieve system usage statistics

    - **start_date**: Start date (optional)
    - **end_date**: End date (optional)
    - **tier**: Filter by subscription type (optional)

    Returns:
    Detailed statistics on users, subscriptions, credits and transactions
    """
    try:
        # Set period
        if start_date:
            period_start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        else:
            period_start = datetime.utcnow() - timedelta(days=30)
        
        if end_date:
            period_end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        else:
            period_end = datetime.utcnow()

        # Total number of users
        total_users_query = db.query(func.count(User.user_id))
        if tier:
            total_users_query = total_users_query.filter(User.subscription_tier == tier)
        total_users = total_users_query.scalar()

        # Distribution by subscriptions
        subscriptions_query = db.query(
            User.subscription_tier,
            func.count(User.user_id)
        ).group_by(User.subscription_tier)

        subscriptions = {
            row[0] if row[0] else "no_subscription": row[1]
            for row in subscriptions_query.all()
        }

        # Statistics on credits
        credits_query = db.query(
            func.sum(CreditBalance.total_earned).label('total_earned'),
            func.sum(CreditBalance.total_spent).label('total_spent'),
            func.sum(CreditBalance.balance).label('current_balance')
        )

        if tier:
            credits_query = credits_query.join(User).filter(User.subscription_tier == tier)

        credits_result = credits_query.first()

        credits_stats = {
            "total_earned": int(credits_result.total_earned or 0),
            "total_spent": int(credits_result.total_spent or 0),
            "current_balance": int(credits_result.current_balance or 0)
        }

        # Transaction statistics
        transactions_query = db.query(Transaction).filter(
            Transaction.created_at >= period_start,
            Transaction.created_at <= period_end
        )

        if tier:
            transactions_query = transactions_query.join(User).filter(
                User.subscription_tier == tier
            )

        total_transactions = transactions_query.count()

        charges = transactions_query.filter(
            Transaction.type == TransactionType.CHARGE
        ).count()

        additions = transactions_query.filter(
            Transaction.type.in_([
                TransactionType.ADD,
                TransactionType.SUBSCRIPTION,
                TransactionType.BONUS,
                TransactionType.REFUND
            ])
        ).count

        transactions_stats = {
            "total": total_transactions,
            "charges": charges,
            "additions": additions
        }

        return StatisticsResponse(
            period={
               "start": period_start,
                "end": period_end 
            },
            total_users=total_users,
            subscriptions=subscriptions,
            credits=credits_stats,
            transactions=transactions_stats
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
    









        


