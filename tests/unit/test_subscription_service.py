import pytest
from app.services import subscription_service
from app.db.models import User, SubscriptionTier


class TestSubscriptionService:
    """Unit tests for SubscriptionService"""

    def test_get_all_plans(self, test_db):
        """Test retrieving all plans"""
        response = subscription_service.get_all_plans(active_only=True, db=test_db)

        assert len(response.plans) == 3
        assert response.plans[0].tier in [
            SubscriptionTier.BASIC,
            SubscriptionTier.STANDARD,
            SubscriptionTier.PREMIUM,
        ]

    def test_get_subscription_details(self, test_db):
        """Test retrieving subscription plan details"""
        plan = subscription_service.get_subscription_details(
            tier=SubscriptionTier.PREMIUM, db=test_db
        )

        assert plan.tier == SubscriptionTier.PREMIUM
        assert plan.name == "Premium"
        assert plan.monthly_cost == 29.99
        assert plan.multiplier == 1.8
        assert plan.total_credits == 289900

    def test_update_subscription_new_user(self, test_db, test_user_id, operation_id):
        """Test subscription update for a new user"""
        response = subscription_service.update_subscription(
            user_id=test_user_id,
            subscription_tier=SubscriptionTier.PREMIUM,
            credits_to_add=289900,
            operation_id=operation_id,
            db=test_db,
        )

        assert response.success is True
        assert response.user_id == test_user_id
        assert response.previous_tier is None
        assert response.new_tier == SubscriptionTier.PREMIUM
        assert response.credits_added == 289900
        assert response.new_balance == 289900

    def test_update_subscription_upgrade(self, test_db, test_user_id, operation_id):
        """Test subscription upgrade"""
        # Create a user with a basic subscription
        user = User(user_id=test_user_id, subscription_tier=SubscriptionTier.BASIC)
        test_db.add(user)
        test_db.commit()

        # Upgrade to premium
        response = subscription_service.update_subscription(
            user_id=test_user_id,
            subscription_tier=SubscriptionTier.PREMIUM,
            credits_to_add=289900,
            operation_id=operation_id,
            db=test_db,
        )

        assert response.previous_tier == SubscriptionTier.BASIC
        assert response.new_tier == SubscriptionTier.PREMIUM
