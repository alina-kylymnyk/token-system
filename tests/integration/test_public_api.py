import pytest
import requests
import uuid

BASE_URL = "http://localhost:8000"


class TestPublicAPI:
    """Integration tests for the Public API"""

    @pytest.fixture
    def test_user_token(self):
        """Create a test user and return the token"""
        from app.core.config import settings

        user_id = f"user_{uuid.uuid4().hex[:8]}"

        # Create user via internal API
        requests.post(
            f"{BASE_URL}/api/internal/subscription/update",
            headers={"X-Service-Token": settings.INTERNAL_SERVICE_TOKEN},
            json={
                "user_id": user_id,
                "subscription_tier": "premium",
                "credits_to_add": 289900,
                "operation_id": f"op_{uuid.uuid4().hex[:8]}",
            },
        )

        return user_id

    @pytest.fixture
    def auth_headers(self, test_user_token):
        return {"Authorization": f"Bearer {test_user_token}"}

    def test_get_subscription(self, auth_headers):
        """Test GET /api/v1/subscription"""
        response = requests.get(f"{BASE_URL}/api/v1/subscription", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert "subscription" in data
        assert "credits" in data
        assert data["subscription"]["tier"] == "premium"

    def test_get_subscription_plans(self):
        """Test GET /api/v1/subscription/plans"""
        response = requests.get(f"{BASE_URL}/api/v1/subscription/plans")

        assert response.status_code == 200
        data = response.json()

        assert len(data["plans"]) == 3

    def test_get_transactions(self, auth_headers):
        """Test GET /api/v1/transactions"""
        response = requests.get(
            f"{BASE_URL}/api/v1/transactions?limit=10", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "transactions" in data
        assert "total" in data

    def test_purchase_credits(self, auth_headers):
        """Test POST /api/v1/credits/purchase"""
        response = requests.post(
            f"{BASE_URL}/api/v1/credits/purchase",
            headers=auth_headers,
            json={"amount_usd": 10.0, "payment_method_id": "pm_test_123"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["credits_added"] == 115000
