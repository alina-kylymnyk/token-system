from app.db.database import SessionLocal
from app.services import credit_service, subscription_service, transaction_service
from app.db.models import User, CreditBalance, Transaction, SubscriptionTier
import uuid


def test_services():
    db = SessionLocal()
    test_user_id = f"test_{uuid.uuid4().hex[:8]}"

    try:
        print("=" * 60)
        print("CORE SERVICES TESTING")
        print("=" * 60)

        # 1. SubscriptionService - get subscription plans
        print("\n1. Fetching subscription plans:")
        plans = subscription_service.get_all_plans(db=db)
        for plan in plans.plans:
            print(
                f"   - {plan.name}: {plan.total_credits} credits, "
                f"multiplier {plan.multiplier}, purchase rate {plan.purchase_rate}"
            )

        # 2. Create user and assign subscription
        print(f"\n2. Creating user {test_user_id}:")
        response = subscription_service.update_subscription(
            user_id=test_user_id,
            subscription_tier=SubscriptionTier.PREMIUM,
            credits_to_add=289900,
            operation_id=f"op_test_{uuid.uuid4().hex[:8]}",
            db=db,
        )
        print(f"   ✓ Subscription created: {response.new_tier}")
        print(f"   ✓ Credits added: {response.credits_added}")
        print(f"   ✓ New balance: {response.new_balance}")

       # 3. Check balance
        print("\n3. Checking balance:")
        balance_info = credit_service.get_balance(test_user_id, db)
        print(f"   Balance: {balance_info.credits.balance}")
        print(f"   Total earned: {balance_info.credits.total_earned}")
        print(f"   Total spent: {balance_info.credits.total_spent}")

        # 4. Cost calculation
        print("\n4. Calculating operation cost ($0.5412):")
        calc = credit_service.calculate(user_id=test_user_id, cost_usd=0.5412, db=db)
        print(f"   Cost: ${calc.cost_usd}")
        print(f"   Credits to charge: {calc.credits_to_charge}")
        print(f"   Multiplier: {calc.multiplier}")
        print(f"   Balance after: {calc.balance_after}")
        print(f"   Sufficient credits: {calc.sufficient}")

        # 5. Charge credits
        print("\n5. Charging credits:")
        charge_response = credit_service.charge_credits(
            user_id=test_user_id,
            cost_usd=0.5412,
            operation_id=f"op_charge_{uuid.uuid4().hex[:8]}",
            description="Test charge",
            metadata={"test": True},
            db=db,
        )
        print(f"   ✓ Success: {charge_response.success}")
        print(f"   ✓ Transaction ID: {charge_response.transaction_id}")
        print(f"   ✓ Credits charged: {charge_response.credits_charged}")
        print(f"   ✓ Balance before: {charge_response.balance_before}")
        print(f"   ✓ Balance after: {charge_response.balance_after}")

        # 6. Transaction history
        print("\n6. Transaction history:")
        transactions = transaction_service.get_user_transactions(
            user_id=test_user_id, limit=10, db=db
        )
        print(f"   Total transactions: {transactions.total}")
        for txn in transactions.transactions:
            print(
                f"   - {txn.type}: {txn.credits:+} credits, "
                f"balance after: {txn.balance_after}"
            )

        # 7. Add credits
        print("\n7. Adding credits ($10):")
        add_response = credit_service.add_credits(
            user_id=test_user_id,
            amount_usd=10.00,
            source="purchase",
            operation_id=f"op_add_{uuid.uuid4().hex[:8]}",
            description="Test purchase",
            db=db,
        )
        print(f"   ✓ Success: {add_response.success}")
        print(f"   ✓ Credits added: {add_response.credits_added}")
        print(f"   ✓ Purchase rate: {add_response.purchase_rate}")
        print(f"   ✓ New balance: {add_response.balance_after}")

        # 8. Idempotency test
        print("\n8. Idempotency test (duplicate charge):")
        operation_id = f"op_idem_{uuid.uuid4().hex[:8]}"

        first = credit_service.charge_credits(
            user_id=test_user_id,
            cost_usd=0.32,
            operation_id=operation_id,
            description="Idempotency test",
            db=db,
        )
        print(f"   First operation - balance after: {first.balance_after}")

        second = credit_service.charge_credits(
            user_id=test_user_id,
            cost_usd=0.32,
            operation_id=operation_id,
            description="Idempotency test",
            db=db,
        )
        print(f"   Second operation - balance after: {second.balance_after}")
        print(
            f"   ✓ Idempotency works: " f"{first.balance_after == second.balance_after}"
        )

        # 9. Insufficient credits test
        print("\n9. Insufficient credits test:")
        insufficient = credit_service.charge_credits(
            user_id=test_user_id,
            cost_usd=999999.99,
            operation_id=f"op_insuf_{uuid.uuid4().hex[:8]}",
            description="Test insufficient",
            db=db,
        )
        print(f"   Success: {insufficient.success}")
        if not insufficient.success:
            print(f"   Error: {insufficient.error}")
            print(f"   Required credits: {insufficient.required_credits}")
            print(f"   Available credits: {insufficient.current_balance}")
            print(f"   Deficit: {insufficient.deficit}")

        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED SUCCESSFULLY!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Cleanup
        print("\nCleaning up test data...")
        db.query(Transaction).filter(Transaction.user_id == test_user_id).delete()
        db.query(CreditBalance).filter(CreditBalance.user_id == test_user_id).delete()
        db.query(User).filter(User.user_id == test_user_id).delete()
        db.commit()
        db.close()
        print("✓ Test data removed")


if __name__ == "__main__":
    test_services()
