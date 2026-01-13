import pytest
import requests
from app.core.config import settings

BASE_URL = "http://localhost:8000"
SERVICE_TOKEN = settings.INTERNAL_SERVICE_TOKEN


class TestInternalAPI:
    """Integration tests for the Internal API"""
    
    @pytest.fixture
    def headers(self):
        return {
            "X-Service-Token": SERVICE_TOKEN,
            "Content-Type": "application/json"
        }
    
    @pytest.fixture
    def test_user(self, headers):
        """Create a test user"""
        import uuid
        user_id = f"test_{uuid.uuid4().hex[:8]}"
        
        # Create user
        response = requests.post(
            f"{BASE_URL}/api/internal/subscription/update",
            headers=headers,
            json={
                "user_id": user_id,
                "subscription_tier": "premium",
                "credits_to_add": 289900,
                "operation_id": f"op_{uuid.uuid4().hex[:8]}"
            }
        )
        
        assert response.status_code == 200
        return user_id
    
    def test_check_credits(self, headers, test_user):
        """Test GET /api/internal/credits/check/{user_id}"""
        response = requests.get(
            f"{BASE_URL}/api/internal/credits/check/{test_user}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["user_id"] == test_user
        assert data["has_subscription"] is True
        assert data["balance"] > 0
    
    def test_calculate_credits(self, headers, test_user):
        """Test POST /api/internal/credits/calculate"""
        response = requests.post(
            f"{BASE_URL}/api/internal/credits/calculate",
            headers=headers,
            json={
                "user_id": test_user,
                "cost_usd": 0.5412
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["cost_usd"] == 0.5412
        assert data["credits_to_charge"] == 9742
        assert data["multiplier"] == 1.8
    
    def test_charge_credits(self, headers, test_user):
        """Test POST /api/internal/credits/charge"""
        import uuid
        
        response = requests.post(
            f"{BASE_URL}/api/internal/credits/charge",
            headers=headers,
            json={
                "user_id": test_user,
                "cost_usd": 0.5412,
                "operation_id": f"op_{uuid.uuid4().hex[:12]}",
                "description": "Integration test charge"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["credits_charged"] == 9742
    
    def test_unauthorized_access(self):
        """Test request without token - should return 403"""
        response = requests.get(
            f"{BASE_URL}/api/internal/credits/check/test_user"
        )
        
        assert response.status_code == 403
