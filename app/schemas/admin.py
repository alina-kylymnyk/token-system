from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict
from .base import BaseSchema, SubscriptionTierEnum


class MultiplierUpdateRequest(BaseSchema):
    """Request to update the credit multiplier"""

    multiplier: float = Field(..., gt=0, description="New credit deduction multiplier")

    model_config = {"json_schema_extra": {"example": {"multiplier": 1.75}}}


class MultiplierUpdateResponse(BaseSchema):
    """Response after updating the multiplier"""

    success: bool = True
    tier: SubscriptionTierEnum
    old_multiplier: float
    new_multiplier: float
    updated_at: datetime

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "tier": "premium",
                "old_multiplier": 1.8,
                "new_multiplier": 1.75,
                "updated_at": "2025-01-15T10:00:00Z",
            }
        }
    }


class PurchaseRateUpdateRequest(BaseSchema):
    """Request to update the credit purchase rate"""

    purchase_rate: float = Field(..., ge=1.0, description="New credit purchase rate")

    model_config = {"json_schema_extra": {"example": {"purchase_rate": 1.2}}}


class PurchaseRateUpdateResponse(BaseSchema):
    """Response after updating the purchase rate"""

    success: bool = True
    tier: SubscriptionTierEnum
    old_purchase_rate: float
    new_purchase_rate: float
    updated_at: datetime

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "tier": "premium",
                "old_purchase_rate": 1.15,
                "new_purchase_rate": 1.2,
                "updated_at": "2025-01-15T10:00:00Z",
            }
        }
    }


class ExchangeRateUpdateRequest(BaseSchema):
    """Request to update the base exchange rate"""

    base_rate: int = Field(..., gt=0, description="New base rate ($1 = X credits)")

    model_config = {"json_schema_extra": {"example": {"base_rate": 10000}}}


class ExchangeRateUpdateResponse(BaseSchema):
    """Response after updating the base exchange rate"""

    success: bool = True
    old_base_rate: int
    new_base_rate: int
    updated_at: datetime

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "old_base_rate": 10000,
                "new_base_rate": 10000,
                "updated_at": "2025-01-15T10:00:00Z",
            }
        }
    }


class PlanDeleteResponse(BaseSchema):
    """Response after deleting a subscription plan"""

    success: bool = True
    message: str
    tier: SubscriptionTierEnum

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Subscription plan deleted",
                "tier": "premium",
            }
        }
    }


class AdminPlanRead(BaseSchema):
    """Extended subscription plan schema for administrators"""

    tier: SubscriptionTierEnum
    name: str
    monthly_cost: float
    fixed_cost: float
    credits_included: int
    bonus_credits: int
    multiplier: float
    purchase_rate: float
    active: bool
    users_count: int = Field(default=0, description="Number of users")
    created_at: datetime
    updated_at: datetime

    model_config = {
        "json_schema_extra": {
            "example": {
                "tier": "basic",
                "name": "Basic",
                "monthly_cost": 9.99,
                "fixed_cost": 5.00,
                "credits_included": 49900,
                "bonus_credits": 0,
                "multiplier": 2.0,
                "purchase_rate": 1.0,
                "active": True,
                "users_count": 1250,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-15T10:00:00Z",
            }
        }
    }


class AdminPlansListResponse(BaseSchema):
    """List of subscription plans for administrators"""

    plans: list[AdminPlanRead]


class StatisticsResponse(BaseSchema):
    """System usage statistics"""

    period: Dict[str, datetime] = Field(..., description="Statistics period")
    total_users: int
    subscriptions: Dict[str, int] = Field(
        ..., description="Distribution by subscription tier"
    )
    credits: Dict[str, int] = Field(..., description="Credits statistics")
    transactions: Dict[str, int] = Field(..., description="Transaction statistics")

    model_config = {
        "json_schema_extra": {
            "example": {
                "period": {
                    "start": "2025-01-01T00:00:00Z",
                    "end": "2025-01-31T23:59:59Z",
                },
                "total_users": 5000,
                "subscriptions": {"basic": 2000, "standard": 2000, "premium": 1000},
                "credits": {
                    "total_earned": 50000000,
                    "total_spent": 35000000,
                    "current_balance": 15000000,
                },
                "transactions": {
                    "total": 150000,
                    "charges": 120000,
                    "additions": 30000,
                },
            }
        }
    }
