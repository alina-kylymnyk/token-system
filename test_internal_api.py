import requests
import uuid
from app.core.config import settings

BASE_URL = "http://localhost:8000"
SERVICE_TOKEN = settings.INTERNAL_SERVICE_TOKEN

headers = {"X-Service-Token": SERVICE_TOKEN, "Content-Type": "application/json"}


def test_internal_api():
    print("=" * 60)
    print("INTERNAL API TESTING")
    print("=" * 60)

    test_user_id = f"test_{uuid.uuid4().hex[:8]}"

    # 1. Update subscription
    print(f"\n1. Updating subscription for {test_user_id}:")
    response = requests.post(
        f"{BASE_URL}/api/internal/subscription/update",
        headers=headers,
        json={
            "user_id": test_user_id,
            "subscription_tier": "premium",
            "credits_to_add": 289900,
            "operation_id": f"op_{uuid.uuid4().hex[:8]}",
        },
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

    # 2. Check balance
    print("\n2. Checking balance:")
    response = requests.get(
        f"{BASE_URL}/api/internal/credits/check/{test_user_id}", headers=headers
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

    # 3. Calculate operation cost
    print("\n3. Calculating operation cost ($0.5412):")
    response = requests.post(
        f"{BASE_URL}/api/internal/credits/calculate",
        headers=headers,
        json={"user_id": test_user_id, "cost_usd": 0.5412},
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

    # 4. Charge credits
    print("\n4. Charging credits:")
    response = requests.post(
        f"{BASE_URL}/api/internal/credits/charge",
        headers=headers,
        json={
            "user_id": test_user_id,
            "cost_usd": 0.5412,
            "operation_id": f"op_{uuid.uuid4().hex[:8]}",
            "description": "Test charge",
            "metadata": {"test": True},
        },
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

    # 5. Get full balance
    print("\n5. Retrieving full balance:")
    response = requests.get(
        f"{BASE_URL}/api/internal/credits/balance/{test_user_id}", headers=headers
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

    # 6. Test without token (should return 403)
    print("\n6. Test without token (expecting 403):")
    response = requests.get(f"{BASE_URL}/api/internal/credits/balance/{test_user_id}")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

    # 7. Test with invalid token (should return 403)
    print("\n7. Test with invalid token (expecting 403):")
    response = requests.get(
        f"{BASE_URL}/api/internal/credits/balance/{test_user_id}",
        headers={"X-Service-Token": "invalid_token"},
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

    print("\n" + "=" * 60)
    print("✓ INTERNAL API TESTING COMPLETED!")
    print("=" * 60)


if __name__ == "__main__":
    test_internal_api()
