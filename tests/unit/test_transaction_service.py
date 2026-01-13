import pytest
from app.services import transaction_service
from app.db.models import User, CreditBalance, TransactionType, SubscriptionTier


class TestTransactionService:
    """Unit tests for TransactionService"""

    def test_ensure_idempotency_no_operation(self, test_db, operation_id):
        """Test idempotency when the operation does not exist"""
        result = transaction_service.ensure_idempotency(operation_id, test_db)
        assert result is None

    def test_create_transaction(self, test_db, test_user_id, operation_id):
        """Test transaction creation"""
        # Create user
        user = User(user_id=test_user_id, subscription_tier=SubscriptionTier.PREMIUM)
        test_db.add(user)
        test_db.commit()

        transaction = transaction_service.create_transaction(
            transaction_id=f"txn_{operation_id}",
            user_id=test_user_id,
            transaction_type=TransactionType.CHARGE,
            operation_id=operation_id,
            credits=-10000,
            balance_after=90000,
            cost_usd=0.50,
            description="Test transaction",
            db=test_db,
        )

        assert transaction.transaction_id == f"txn_{operation_id}"
        assert transaction.user_id == test_user_id
        assert transaction.credits == -10000
        assert transaction.balance_after == 90000

    def test_get_user_transactions(self, test_db, test_user_id):
        """Test retrieving transaction history"""
        # Create user and balance
        user = User(user_id=test_user_id, subscription_tier=SubscriptionTier.PREMIUM)
        test_db.add(user)

        balance = CreditBalance(user_id=test_user_id, balance=100000)
        test_db.add(balance)
        test_db.commit()

        # Create multiple transactions
        for i in range(5):
            transaction_service.create_transaction(
                transaction_id=f"txn_{i}",
                user_id=test_user_id,
                transaction_type=TransactionType.CHARGE,
                operation_id=f"op_{i}",
                credits=-1000,
                balance_after=100000 - (i + 1) * 1000,
                db=test_db,
            )
        test_db.commit()

        # Retrieve transactions
        response = transaction_service.get_user_transactions(
            user_id=test_user_id, limit=10, offset=0, db=test_db
        )

        assert response.total == 5
        assert len(response.transactions) == 5
