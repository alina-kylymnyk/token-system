import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.db.database import SessionLocal
from app.services import credit_service, subscription_service
from app.db.models import User, CreditBalance, Transaction, SubscriptionTier


def setup_test_user() -> str:
    db = SessionLocal()
    test_user_id = f"test_{uuid.uuid4().hex[:8]}"
    try:
        subscription_service.update_subscription(
            user_id=test_user_id,
            subscription_tier=SubscriptionTier.PREMIUM,
            credits_to_add=100_000,
            operation_id=f"op_setup_{uuid.uuid4().hex[:8]}",
            db=db,
        )
        db.commit()
        return test_user_id
    finally:
        db.close()


def cleanup_test_user(user_id: str):
    db = SessionLocal()
    try:
        db.query(Transaction).filter(Transaction.user_id == user_id).delete()
        db.query(CreditBalance).filter(CreditBalance.user_id == user_id).delete()
        db.query(User).filter(User.user_id == user_id).delete()
        db.commit()
    finally:
        db.close()


def test_idempotency():
    print("\n" + "=" * 70)
    print("TEST 1: IDEMPOTENCY")
    print("=" * 70)

    user_id = setup_test_user()
    operation_id = f"op_idem_{uuid.uuid4().hex[:8]}"

    try:
        db1 = SessionLocal()
        response1 = credit_service.charge_credits(
            user_id=user_id,
            cost_usd=0.50,
            operation_id=operation_id,
            description="Test idempotency - first",
            db=db1,
        )
        db1.close()

        db2 = SessionLocal()
        response2 = credit_service.charge_credits(
            user_id=user_id,
            cost_usd=0.50,
            operation_id=operation_id,
            description="Test idempotency - second",
            db=db2,
        )
        db2.close()

        assert response1.balance_after == response2.balance_after
        assert response1.credits_charged == response2.credits_charged

        print("✓ IDEMPOTENCY TEST PASSED!")

    finally:
        cleanup_test_user(user_id)


def test_concurrent_operations():
    print("\n" + "=" * 70)
    print("TEST 2: CONCURRENT OPERATIONS (RACE CONDITIONS)")
    print("=" * 70)

    user_id = setup_test_user()

    try:
        db = SessionLocal()
        initial_balance = (
            db.query(CreditBalance)
            .filter(CreditBalance.user_id == user_id)
            .first()
            .balance
        )
        db.close()

        def charge_in_thread(thread_id: int):
            db = SessionLocal()
            try:
                operation_id = f"op_thread_{thread_id}_{uuid.uuid4().hex[:4]}"
                response = credit_service.charge_credits(
                    user_id=user_id,
                    cost_usd=0.10,
                    operation_id=operation_id,
                    description=f"Concurrent charge from thread {thread_id}",
                    db=db,
                )
                db.commit()
                return {
                    "success": response.success,
                    "credits_charged": response.credits_charged,
                }
            except Exception as e:
                return {"error": str(e)}
            finally:
                db.close()

        num_threads = 10
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(charge_in_thread, i) for i in range(num_threads)]
            results = [future.result() for future in as_completed(futures)]

        successful = [r for r in results if r.get("success")]

        db = SessionLocal()
        final_balance = (
            db.query(CreditBalance)
            .filter(CreditBalance.user_id == user_id)
            .first()
            .balance
        )
        db.close()

        total_charged = sum([r["credits_charged"] for r in successful])
        assert final_balance == initial_balance - total_charged

        print("✓ CONCURRENT OPERATIONS TEST PASSED!")

    finally:
        cleanup_test_user(user_id)


def test_rollback_on_error():
    print("\n" + "=" * 70)
    print("TEST 3: AUTOMATIC ROLLBACK ON ERROR")
    print("=" * 70)

    user_id = setup_test_user()

    try:
        db = SessionLocal()
        balance_before = (
            db.query(CreditBalance)
            .filter(CreditBalance.user_id == user_id)
            .first()
            .balance
        )
        db.close()

        db = SessionLocal()
        try:
            credit_service.charge_credits(
                user_id=user_id,
                cost_usd=999_999.99,
                operation_id=f"op_fail_{uuid.uuid4().hex[:8]}",
                description="Test rollback",
                db=db,
            )
            db.commit()
        except:
            db.rollback()
        finally:
            db.close()

        db = SessionLocal()
        balance_after = (
            db.query(CreditBalance)
            .filter(CreditBalance.user_id == user_id)
            .first()
            .balance
        )
        transactions_count = (
            db.query(Transaction)
            .filter(
                Transaction.user_id == user_id,
                Transaction.description == "Test rollback",
            )
            .count()
        )
        db.close()

        assert balance_before == balance_after
        assert transactions_count == 0

        print("✓ ROLLBACK TEST PASSED!")

    finally:
        cleanup_test_user(user_id)


def test_pessimistic_locking():
    print("\n" + "=" * 70)
    print("TEST 4: PESSIMISTIC LOCKING")
    print("=" * 70)

    user_id = setup_test_user()

    try:
        db = SessionLocal()
        initial_balance = (
            db.query(CreditBalance)
            .filter(CreditBalance.user_id == user_id)
            .first()
            .balance
        )
        db.close()

        def charge_in_thread(thread_id: int):
            time.sleep(0.01 * thread_id)
            db = SessionLocal()
            try:
                operation_id = f"op_lock_{thread_id}_{uuid.uuid4().hex[:4]}"
                response = credit_service.charge_credits(
                    user_id=user_id,
                    cost_usd=0.50,
                    operation_id=operation_id,
                    description=f"Pessimistic lock test thread {thread_id}",
                    db=db,
                )
                db.commit()
                return {
                    "success": response.success,
                    "balance_after": response.balance_after,
                }
            except Exception as e:
                return {"error": str(e)}
            finally:
                db.close()

        num_threads = 5
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(charge_in_thread, i) for i in range(num_threads)]
            results = [future.result() for future in as_completed(futures)]

        db = SessionLocal()
        final_balance = (
            db.query(CreditBalance)
            .filter(CreditBalance.user_id == user_id)
            .first()
            .balance
        )
        db.close()

        # Перевірка: фінальний баланс зменшився правильно
        expected_min_balance = (
            initial_balance - 0.50 * num_threads * 18000
        )  # припустимо 1 USD = 18000 credits
        assert final_balance <= initial_balance
        assert final_balance >= expected_min_balance

        print("✓ PESSIMISTIC LOCKING TEST PASSED!")

    finally:
        cleanup_test_user(user_id)


if __name__ == "__main__":
    test_idempotency()
    test_concurrent_operations()
    test_rollback_on_error()
    test_pessimistic_locking()

    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 70)
