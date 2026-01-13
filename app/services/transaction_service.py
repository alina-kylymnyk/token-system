from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.db.models import Transaction, TransactionType
from app.schemas import TransactionRead, TransactionListResponse

class TransactionService:
    """Service for working with transactions"""

    @staticmethod
    def ensure_idempotency(
        operation_id: str,
        db: Session
    ) -> Optional[Transaction]:
        """
        Check operation_id for idempotence

        Args:
        operation_id: Unique operation ID
        db: Database session

        Returns:
        Transaction if the operation has already been executed, None if not
        """
        return db.query(Transaction).filter(
            Transaction.operation_id == operation_id
        ).first()
    
    @staticmethod
    def create_transaction(
        transaction_id: str,
        user_id: str,
        transaction_type: TransactionType,
        operation_id: str,
        credits: int,
        balance_after: int,
        cost_usd: Optional[float] = None,
        description: Optional[str] = None,
        metadata: Optional[dict] = None,
        db: Session = None
    ) -> Transaction:
        """
        Create a transaction

        Args:
        transaction_id: Transaction ID
        user_id: User ID
        transaction_type: Transaction type
        operation_id: Operation ID (for idempotence)
        credits: Number of credits (+/-)
        balance_after: Balance after the operation
        cost_usd: Cost in dollars (optional)
        description: Description
        metadata: Additional data
        db: Database session

        Returns:
        Transaction
        """
        transaction = Transaction(
            transaction_id=transaction_id,
            user_id=user_id,
            type=transaction_type,
            operation_id=operation_id,
            cost_usd=cost_usd,
            credits=credits,
            balance_after=balance_after,
            description=description,
            metadata=metadata or {}
        )

        db.add(transaction)
        db.flush()

        return transaction
    
    @staticmethod
    def get_user_transactions(
         user_id: str,
        limit: int = 50,
        offset: int = 0,
        transaction_type: Optional[str] = None,
        db: Session = None
    ) -> TransactionListResponse:
        """
        Getting history 

        Args:
        user_id: User ID
        limit: Number of records
        offset: Offset
        transaction_type: Filter by type (optional)
        db: Database session

        Returns:
        TransactionListResponse
        """
        query = db.query(Transaction).filter(
            Transaction.user_id ==user_id
        )
        # Filter by type
        if transaction_type:
            query = query.filter(Transaction.type == transaction_type)

        # Total number
        total = query.count()

        # Отримати транзакції з пагінацією
        transactions = query.order_by(
            Transaction.created_at.desc()
        ).limit(limit).offset(offset).all()

        # Convert to schemas
        transactions_read = [
            TransactionRead(
                id=t.id,
                transaction_id=t.transaction_id,
                type=t.type,
                created_at=t.created_at,
                cost_usd=t.cost_usd,
                credits=t.credits,
                balance_after=t.balance_after,
                description=t.description,
                operation_id=t.operation_id
            )
            for t in transactions
        ]

        return TransactionListResponse(
            total=total,
            limit=limit, 
            offset=offset,
            transactions=transactions_read
        )

transaction_service=TransactionService()




    