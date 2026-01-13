import pytest
import requests
from app.core.config import settings

BASE_URL = "http://localhost:8000"
ADMIN_TOKEN = settings.ADMIN_TOKEN


class TestAdminAPI:
    """Integration tests for the Admin API"""

    @pytest.fixture
    def headers(self):
        return {"X-Admin-Token": ADMIN_TOKEN, "Content-Type": "application/json"}

    def test_get_subscription_plans(self, headers):
        """Test GET /api/admin/subscription-plans"""
        response = requests.get(
            f"{BASE_URL}/api/admin/subscription-plans", headers=headers
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["plans"]) >= 3
        assert "users_count" in data["plans"][0]

    def test_update_multiplier(self, headers):
        """Test PATCH /api/admin/subscription-plans/{tier}/multiplier"""
        response = requests.patch(
            f"{BASE_URL}/api/admin/subscription-plans/basic/multiplier",
            headers=headers,
            json={"multiplier": 2.0},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["new_multiplier"] == 2.0

    def test_get_statistics(self, headers):
        """Test GET /api/admin/statistics"""
        response = requests.get(f"{BASE_URL}/api/admin/statistics", headers=headers)

        assert response.status_code == 200
        data = response.json()

        assert "total_users" in data
        assert "subscriptions" in data
        assert "credits" in data
        assert "transactions" in data
