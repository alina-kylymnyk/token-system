import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import uuid
import os
import tempfile

from app.db.models import Base, SubscriptionPlan, SubscriptionTier


@pytest.fixture(scope="function")
def test_db():
    """Create a test database for each test using in-memory SQLite"""

    # Use an in-memory database for each test
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create a session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    # Seed test data
    seed_test_plans(db)

    yield db

    # Cleanup
    db.close()
    engine.dispose()


def seed_test_plans(db):
    """Add test subscription plans"""
    plans = [
        SubscriptionPlan(
            tier=SubscriptionTier.BASIC,
            name="Basic",
            monthly_cost=9.99,
            fixed_cost=5.00,
            credits_included=49900,
            bonus_credits=0,
            multiplier=2.0,
            purchase_rate=1.0,
            active=True,
        ),
        SubscriptionPlan(
            tier=SubscriptionTier.STANDARD,
            name="Standard",
            monthly_cost=19.99,
            fixed_cost=5.00,
            credits_included=149900,
            bonus_credits=20000,
            multiplier=1.9,
            purchase_rate=1.1,
            active=True,
        ),
        SubscriptionPlan(
            tier=SubscriptionTier.PREMIUM,
            name="Premium",
            monthly_cost=29.99,
            fixed_cost=5.00,
            credits_included=249900,
            bonus_credits=40000,
            multiplier=1.8,
            purchase_rate=1.15,
            active=True,
        ),
    ]

    for plan in plans:
        db.add(plan)

    db.commit()


@pytest.fixture
def test_user_id():
    """Generate a unique test user ID"""
    return f"test_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def operation_id():
    """Generate a unique operation ID"""
    return f"op_{uuid.uuid4().hex[:12]}"
