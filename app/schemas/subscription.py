from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from .base import BaseSchema, SubscriptionTierEnum


class SubscriptionPlanBase(BaseSchema):
    """Base schema for a subscription plan"""

    name: str = Field(..., min_length=1, max_length=100, description="Plan name")
    monthly_cost: float = Field(..., gt=0, description="Monthly cost")
    fixed_cost: float = Field(default=5.00, ge=0, description="Fixed cost portion")
    credits_included: int = Field(..., ge=0, description="Included credits")
    bonus_credits: int = Field(default=0, ge=0, description="Bonus credits")
    multiplier: float = Field(..., gt=0, description="Credit deduction multiplier")
    purchase_rate: float = Field(
        default=1.0, ge=1.0, description="Credit purchase rate"
    )
    active: bool = Field(default=True, description="Active status")


class SubscriptionPlanCreate(SubscriptionPlanBase):
    """Schema for creating a subscription plan"""

    tier: SubscriptionTierEnum = Field(..., description="Subscription tier")

    model_config = {
        "json_schema_extra": {
            "example": {
                "tier": "premium",
                "name": "Premium",
                "monthly_cost": 29.99,
                "fixed_cost": 5.00,
                "credits_included": 249900,
                "bonus_credits": 40000,
                "multiplier": 1.8,
                "purchase_rate": 1.15,
                "active": True,
            }
        }
    }


class SubscriptionPlanUpdate(BaseSchema):
    """Schema for updating a subscription plan"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    monthly_cost: Optional[float] = Field(None, gt=0)
    fixed_cost: Optional[float] = Field(None, ge=0)
    credits_included: Optional[int] = Field(None, ge=0)
    bonus_credits: Optional[int] = Field(None, ge=0)
    multiplier: Optional[float] = Field(None, gt=0)
    purchase_rate: Optional[float] = Field(None, ge=1.0)
    active: Optional[bool] = None


class SubscriptionPlanRead(SubscriptionPlanBase):
    """Schema for reading a subscription plan"""

    tier: SubscriptionTierEnum
    total_credits: int = Field(..., description="Total credits including bonus")
    created_at: datetime
    updated_at: datetime

    model_config = {
        "json_schema_extra": {
            "example": {
                "tier": "premium",
                "name": "Premium",
                "monthly_cost": 29.99,
                "fixed_cost": 5.00,
                "credits_included": 249900,
                "bonus_credits": 40000,
                "total_credits": 289900,
                "multiplier": 1.8,
                "purchase_rate": 1.15,
                "active": True,
                "created_at": "2025-01-15T10:00:00Z",
                "updated_at": "2025-01-15T10:00:00Z",
            }
        }
    }


class SubscriptionPlansListResponse(BaseSchema):
    """Schema for a list of subscription plans"""

    plans: list[SubscriptionPlanRead]

    model_config = {
        "json_schema_extra": {
            "example": {
                "plans": [
                    {
                        "tier": "basic",
                        "name": "Basic",
                        "monthly_cost": 9.99,
                        "fixed_cost": 5.00,
                        "credits_included": 49900,
                        "bonus_credits": 0,
                        "total_credits": 49900,
                        "multiplier": 2.0,
                        "purchase_rate": 1.0,
                        "active": True,
                        "created_at": "2025-01-15T10:00:00Z",
                        "updated_at": "2025-01-15T10:00:00Z",
                    }
                ]
            }
        }
    }


class SubscriptionUpdateRequest(BaseSchema):
    """Request to update a user's subscription"""

    user_id: str = Field(..., min_length=1, description="User ID to update")
    subscription_tier: SubscriptionTierEnum = Field(
        ..., description="New subscription tier"
    )
    credits_to_add: int = Field(
        ..., ge=0, description="Credits to add to the user's balance"
    )
    operation_id: str = Field(..., min_length=1, description="Unique operation ID")

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "user_123",
                "subscription_tier": "premium",
                "credits_to_add": 289900,
                "operation_id": "op_sub_789",
            }
        }
    }


class SubscriptionUpdateResponse(BaseSchema):
    """Response after updating a user's subscription"""

    success: bool = True
    user_id: str
    previous_tier: Optional[SubscriptionTierEnum] = Field(
        None, description="Previous subscription tier"
    )
    new_tier: SubscriptionTierEnum = Field(..., description="New subscription tier")
    credits_added: int = Field(..., description="Number of credits added")
    new_balance: int = Field(..., description="New total credit balance")
    multiplier: float = Field(..., description="Applied multiplier for credits")
    purchase_rate: float = Field(..., description="Applied credit purchase rate")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "user_id": "user_123",
                "previous_tier": "standard",
                "new_tier": "premium",
                "credits_added": 289900,
                "new_balance": 579800,
                "multiplier": 1.8,
                "purchase_rate": 1.15,
            }
        }
    }
