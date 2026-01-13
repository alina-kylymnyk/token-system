from app.db.database import SessionLocal
from app.db.models import SubscriptionPlan, User, CreditBalance, Transaction, SystemSettings
from app.db.models import SubscriptionTier, TransactionType
import uuid


def test_models():
    db = SessionLocal()

    try:
        # 1. Check subscription plans
        print("1. Checking subscription plans:")
        plans = db.query(SubscriptionPlan).all()
        for plan in plans:
            print(f"   - {plan.name}: {plan.total_credits} credits, multiplier {plan.multiplier}")

        # 2. Create test user
        print("\n2. Creating test user:")
        test_user_id = f"test_user_{uuid.uuid4().hex[:8]}"
        user = User(
            user_id=test_user_id,
            subscription_tier=SubscriptionTier.PREMIUM
        )
        db.add(user)
        db.commit()
        print(f"   ✓ User created: {user.user_id}")

        # 3. Create credit balance
        print("\n3. Creating credit balance:")
        balance = CreditBalance(
            user_id=test_user_id,
            balance=289900,
            total_earned=289900,
            total_spent=0
        )
        db.add(balance)
        db.commit()
        print(f"   ✓ Balance created: {balance.balance} credits")

        # 4. Create transaction
        print("\n4. Creating transaction:")
        transaction = Transaction(
            transaction_id=f"txn_{uuid.uuid4().hex[:8]}",
            user_id=test_user_id,
            type=TransactionType.SUBSCRIPTION,
            operation_id=f"op_{uuid.uuid4().hex[:8]}",
            cost_usd=None,
            credits=289900,
            balance_after=289900,
            description="Initial subscription credits",
            metadata={"tier": "premium"}
        )
        db.add(transaction)
        db.commit()
        print(f"   ✓ Transaction created: {transaction.transaction_id}")

        # 5. Check relationships
        print("\n5. Checking relationships:")
        user_from_db = db.query(User).filter(User.user_id == test_user_id).first()
        print(f"   - Subscription plan: {user_from_db.subscription_plan.name}")
        print(f"   - Credit balance: {user_from_db.credit_balance.balance}")
        print(f"   - Transactions count: {len(user_from_db.transactions)}")

        # 6. Check system settings
        print("\n6. Checking system settings:")
        settings = db.query(SystemSettings).all()
        for setting in settings:
            print(f"   - {setting.key}: {setting.value}")

        print("\n✓ All checks passed successfully!")

        # Cleanup test data
        print("\n7. Cleaning up test data...")
        db.query(Transaction).filter(Transaction.user_id == test_user_id).delete()
        db.query(CreditBalance).filter(CreditBalance.user_id == test_user_id).delete()
        db.query(User).filter(User.user_id == test_user_id).delete()
        db.commit()
        print("   ✓ Test data removed")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    test_models()
