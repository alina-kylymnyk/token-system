"""
Full API test suite:
- Internal API (setup)
- Public API (user-facing)
- Admin API (management)

IMPORTANT:
- FastAPI server must be running on http://localhost:8000
- INTERNAL_SERVICE_TOKEN and ADMIN_TOKEN must be valid
"""

import requests
import uuid
from app.core.config import settings

BASE_URL = "http://localhost:8000"
SERVICE_TOKEN = settings.INTERNAL_SERVICE_TOKEN
ADMIN_TOKEN = settings.ADMIN_TOKEN


def test_public_api():
    """
    Test all PUBLIC (user-facing) API endpoints.
    """
    print("\n" + "=" * 60)
    print("TESTING PUBLIC API")
    print("=" * 60)

    test_user_id = f"user_{uuid.uuid4().hex[:8]}"

    # ------------------------------------------------------------------
    # Create test user via Internal API
    # ------------------------------------------------------------------
    print(f"\nCreating test user via Internal API: {test_user_id}")

    requests.post(
        f"{BASE_URL}/api/internal/subscription/update",
        headers={
            "X-Service-Token": SERVICE_TOKEN,
            "Content-Type": "application/json",
        },
        json={
            "user_id": test_user_id,
            "subscription_tier": "premium",
            "credits_to_add": 289900,
            "operation_id": f"op_{uuid.uuid4().hex[:8]}",
        },
    )

    # DEMO authentication: user_id is used as Bearer token
    user_headers = {
        "Authorization": f"Bearer {test_user_id}",
        "Content-Type": "application/json",
    }

    # ------------------------------------------------------------------
    # 1. GET /api/v1/subscription
    # ------------------------------------------------------------------
    print("\n1. GET /api/v1/subscription - subscription info:")
    response = requests.get(
        f"{BASE_URL}/api/v1/subscription",
        headers=user_headers,
    )
    print(f"   Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"   Subscription: {data['subscription']['name']}")
        print(f"   Balance: {data['credits']['balance']}")

    # ------------------------------------------------------------------
    # 2. GET /api/v1/subscription/plans
    # ------------------------------------------------------------------
    print("\n2. GET /api/v1/subscription/plans - available plans:")
    response = requests.get(f"{BASE_URL}/api/v1/subscription/plans")
    print(f"   Status: {response.status_code}")
    if response.ok:
        plans = response.json()["plans"]
        print(f"   Plans count: {len(plans)}")
        for plan in plans:
            print(f"   - {plan['name']}: {plan['total_credits']} credits")

    # ------------------------------------------------------------------
    # 3. GET /api/v1/transactions
    # ------------------------------------------------------------------
    print("\n3. GET /api/v1/transactions - transaction history:")
    response = requests.get(
        f"{BASE_URL}/api/v1/transactions?limit=10",
        headers=user_headers,
    )
    print(f"   Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"   Total transactions: {data['total']}")

    # ------------------------------------------------------------------
    # 4. POST /api/v1/credits/purchase
    # ------------------------------------------------------------------
    print("\n4. POST /api/v1/credits/purchase - credit purchase:")
    response = requests.post(
        f"{BASE_URL}/api/v1/credits/purchase",
        headers=user_headers,
        json={
            "amount_usd": 10.00,
            "payment_method_id": "pm_test_123",
        },
    )
    print(f"   Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"   Credits added: {data['credits_added']}")
        print(f"   New balance: {data['new_balance']}")


def test_admin_api():
    """
    Test all ADMIN API endpoints.
    """
    print("\n" + "=" * 60)
    print("TESTING ADMIN API")
    print("=" * 60)

    admin_headers = {
        "X-Admin-Token": ADMIN_TOKEN,
        "Content-Type": "application/json",
    }

    # ------------------------------------------------------------------
    # 1. GET /api/admin/subscription-plans
    # ------------------------------------------------------------------
    print("\n1. GET /api/admin/subscription-plans - plans list:")
    response = requests.get(
        f"{BASE_URL}/api/admin/subscription-plans",
        headers=admin_headers,
    )
    print(f"   Status: {response.status_code}")
    if response.ok:
        plans = response.json()["plans"]
        for plan in plans:
            print(f"   - {plan['name']}: {plan['users_count']} users")

    # ------------------------------------------------------------------
    # 2. PATCH /api/admin/subscription-plans/basic/multiplier
    # ------------------------------------------------------------------
    print("\n2. PATCH /api/admin/subscription-plans/basic/multiplier:")
    response = requests.patch(
        f"{BASE_URL}/api/admin/subscription-plans/basic/multiplier",
        headers=admin_headers,
        json={"multiplier": 2.0},
    )
    print(f"   Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"   Updated: {data['old_multiplier']} -> {data['new_multiplier']}")

    # ------------------------------------------------------------------
    # 3. GET /api/admin/statistics
    # ------------------------------------------------------------------
    print("\n3. GET /api/admin/statistics - system statistics:")
    response = requests.get(
        f"{BASE_URL}/api/admin/statistics",
        headers=admin_headers,
    )
    print(f"   Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"   Total users: {data['total_users']}")
        print(f"   Subscriptions: {data['subscriptions']}")
        print(f"   Transactions: {data['transactions']['total']}")


if __name__ == "__main__":
    print("\nStarting full API test suite...")
    test_public_api()
    test_admin_api()
    print("\n✓ ALL API TESTS COMPLETED SUCCESSFULLY!")
