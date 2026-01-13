from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from enum import Enum


class TransactionTypeEnum(str, Enum):
    """Transaction types"""
    CHARGE = "charge"
    ADD = "add"
    SUBSCRIPTION = "subscription"
    BONUS = "bonus"
    REFUND = "refund"


class SubscriptionTierEnum(str, Enum):
    """Subscription tiers"""
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"


class BaseSchema(BaseModel):
    """Base schema with shared configuration"""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {}
        }
    )
