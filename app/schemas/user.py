from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from .base import BaseSchema, SubscriptionTierEnum
from .subscription import SubscriptionPlanRead
from .credit import CreditBalanceRead


class UserBase(BaseSchema):
    """Base schema for a user"""
    user_id: str = Field(..., min_length=1, max_length=100, description="Unique identifier of the user")


class UserCreate(UserBase):
    """Schema for creating a user"""
    subscription_tier: Optional[SubscriptionTierEnum] = Field(None, description="User's subscription tier")


class UserRead(UserBase):
    """Schema for reading a user"""
    subscription_tier: Optional[SubscriptionTierEnum]
    created_at: datetime
    updated_at: datetime


class UserSubscriptionInfo(BaseSchema):
    """Full information about a user's subscription"""
    subscription: SubscriptionPlanRead
    credits: "CreditBalanceRead"  # Forward reference for credit balance schema
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "subscription": {
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
                    "updated_at": "2025-01-15T10:00:00Z"
                },
                "credits": {
                    "balance": 289900,
                    "total_earned": 500000,
                    "total_spent": 210100
                }
            }
        }
    }
