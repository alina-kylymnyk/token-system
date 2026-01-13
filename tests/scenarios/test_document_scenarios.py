import pytest
import uuid
from app.db.database import SessionLocal
from app.services import credit_service, subscription_service
from app.db.models import User, CreditBalance, SubscriptionTier


class TestDocumentScenarios:
    """Test scenarios based on the product document"""

    @pytest.fixture
    def db(self):
        """Database session"""
        session = SessionLocal()
        yield session
        session.close()

    def test_scenario_1_basic_subscription(self, db):
        """
        Scenario 1: User with a Basic subscription

        Subscription: Basic ($9.99/month)
        Available credits: 49,900
        """
        print("\n" + "=" * 70)
        print("SCENARIO 1: User with Basic subscription")
        print("=" * 70)

        user_id = f"scenario1_{uuid.uuid4().hex[:8]}"

        # Create subscription
        subscription_service.update_subscription(
            user_id=user_id,
            subscription_tier=SubscriptionTier.BASIC,
            credits_to_add=49900,
            operation_id=f"op_{uuid.uuid4().hex[:8]}",
            db=db,
        )

        # Check initial balance
        balance_info = credit_service.get_balance(user_id, db)
        assert balance_info.credits["balance"] == 49900
        print(f"Initial balance: {balance_info.credits['balance']} credits")

        # Generation 1: $0.5412
        print("\nGeneration 1 ($0.5412):")
        response1 = credit_service.charge_credits(
            user_id=user_id,
            cost_usd=0.5412,
            operation_id=f"op_{uuid.uuid4().hex[:8]}",
            description="Generation 1",
            db=db,
        )

        assert response1.credits_charged == 10824
        assert response1.balance_after == 39076
        print(f"  Charged: {response1.credits_charged} credits")
        print(f"  Remaining balance: {response1.balance_after} credits")

        # Generation 2: $0.88
        print("\nGeneration 2 ($0.88):")
        response2 = credit_service.charge_credits(
            user_id=user_id,
            cost_usd=0.88,
            operation_id=f"op_{uuid.uuid4().hex[:8]}",
            description="Generation 2",
            db=db,
        )

        assert response2.credits_charged == 17600
        assert response2.balance_after == 21476
        print(f"  Charged: {response2.credits_charged} credits")
        print(f"  Remaining balance: {response2.balance_after} credits")

        # Generation 3: $0.32
        print("\nGeneration 3 ($0.32):")
        response3 = credit_service.charge_credits(
            user_id=user_id,
            cost_usd=0.32,
            operation_id=f"op_{uuid.uuid4().hex[:8]}",
            description="Generation 3",
            db=db,
        )

        assert response3.credits_charged == 6400
        assert response3.balance_after == 15076
        print(f"  Charged: {response3.credits_charged} credits")
        print(f"  Remaining balance: {response3.balance_after} credits")

        print("\n✓ SCENARIO 1 PASSED")

    def test_scenario_2_premium_subscription(self, db):
        """
        Scenario 2: User with Premium subscription

        Subscription: Premium ($29.99/month)
        Available credits: 289,900
        """
        print("\n" + "=" * 70)
        print("SCENARIO 2: User with Premium subscription")
        print("=" * 70)

        user_id = f"scenario2_{uuid.uuid4().hex[:8]}"

        # Create subscription
        subscription_service.update_subscription(
            user_id=user_id,
            subscription_tier=SubscriptionTier.PREMIUM,
            credits_to_add=289900,
            operation_id=f"op_{uuid.uuid4().hex[:8]}",
            db=db,
        )

        balance_info = credit_service.get_balance(user_id, db)
        assert balance_info.credits["balance"] == 289900
        print(f"Initial balance: {balance_info.credits['balance']} credits")

        # Generation 1
        response1 = credit_service.charge_credits(
            user_id=user_id,
            cost_usd=0.5412,
            operation_id=f"op_{uuid.uuid4().hex[:8]}",
            description="Generation 1",
            db=db,
        )

        assert response1.credits_charged == 9742
        assert response1.balance_after == 280158

        # Generation 2
        response2 = credit_service.charge_credits(
            user_id=user_id,
            cost_usd=0.88,
            operation_id=f"op_{uuid.uuid4().hex[:8]}",
            description="Generation 2",
            db=db,
        )

        assert response2.credits_charged == 15840
        assert response2.balance_after == 264318

        # Generation 3
        response3 = credit_service.charge_credits(
            user_id=user_id,
            cost_usd=0.32,
            operation_id=f"op_{uuid.uuid4().hex[:8]}",
            description="Generation 3",
            db=db,
        )

        assert response3.credits_charged == 5760
        assert response3.balance_after == 258558

        # Premium advantage: ~10% savings
        basic_total = 10824 + 17600 + 6400
        premium_total = 9742 + 15840 + 5760
        savings_percent = (basic_total - premium_total) / basic_total * 100

        print(f"\nSavings compared to Basic: {savings_percent:.1f}%")
        assert savings_percent >= 9.5

        print("\n✓ SCENARIO 2 PASSED")

    def test_scenario_3_credit_purchase(self, db):
        """
        Scenario 3: Purchasing additional credits

        Subscription: Basic
        Initial balance: 5,000 credits
        Required: $0.60 (12,000 credits)
        """
        print("\n" + "=" * 70)
        print("SCENARIO 3: Credit purchase")
        print("=" * 70)

        user_id = f"scenario3_{uuid.uuid4().hex[:8]}"

        user = User(user_id=user_id, subscription_tier=SubscriptionTier.BASIC)
        db.add(user)

        balance = CreditBalance(
            user_id=user_id,
            balance=5000,
            total_earned=5000,
            total_spent=0,
        )
        db.add(balance)
        db.commit()

        print("Initial balance: 5,000 credits")

        # Purchase credits
        add_response = credit_service.add_credits(
            user_id=user_id,
            amount_usd=1.0,
            source="purchase",
            operation_id=f"op_{uuid.uuid4().hex[:8]}",
            description="Credit purchase",
            db=db,
        )

        assert add_response.credits_added == 10000
        assert add_response.balance_after == 15000

        # Generate after purchase
        charge_response = credit_service.charge_credits(
            user_id=user_id,
            cost_usd=0.60,
            operation_id=f"op_{uuid.uuid4().hex[:8]}",
            description="Generation after purchase",
            db=db,
        )

        assert charge_response.success is True
        assert charge_response.credits_charged == 12000
        assert charge_response.balance_after == 3000

        print("\n✓ SCENARIO 3 PASSED")


def test_all_calculation_examples():
    """Validate all calculation examples from the document"""
    print("\n" + "=" * 70)
    print("VALIDATING ALL CALCULATION EXAMPLES")
    print("=" * 70)

    examples = [
        (0.5412, 2.0, 10824),
        (0.5412, 1.9, 10283),
        (0.5412, 1.8, 9742),
        (0.98, 2.0, 19600),
        (0.98, 1.9, 18620),
        (0.98, 1.8, 17640),
    ]

    for cost, multiplier, expected in examples:
        calculated = round(cost * multiplier * 10000)
        print(f"${cost} x {multiplier} x 10,000 = {calculated}")
        assert calculated == expected

    print("\n✓ ALL CALCULATIONS ARE CORRECT")
