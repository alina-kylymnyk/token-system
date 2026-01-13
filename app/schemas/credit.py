from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from .base import BaseSchema, SubscriptionTierEnum


class CreditBalanceRead(BaseSchema):
    """Schema for reading credit balance"""
    balance: int = Field(..., ge=0, description="Current balance")
    total_earned: int = Field(..., ge=0, description="Total earned")
    total_spent: int = Field(..., ge=0, description="Total spent")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "balance": 289900,
                "total_earned": 500000,
                "total_spent": 210100
            }
        }
    }


class CreditCheckResponse(BaseSchema):
    """Response for credit availability check"""
    user_id: str
    has_subscription: bool
    subscription_tier: Optional[SubscriptionTierEnum]
    balance: int
    sufficient: bool
    multiplier: Optional[float] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "user_123",
                "has_subscription": True,
                "subscription_tier": "premium",
                "balance": 289900,
                "sufficient": True,
                "multiplier": 1.8
            }
        }
    }


class CreditCalculateRequest(BaseSchema):
    """Request to calculate operation cost in credits"""
    user_id: str = Field(..., min_length=1)
    cost_usd: float = Field(..., gt=0, description="Cost in USD")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "user_123",
                "cost_usd": 0.5412
            }
        }
    }


class CreditCalculateResponse(BaseSchema):
    """Response with calculated credit cost"""
    user_id: str
    cost_usd: float
    credits_to_charge: int
    multiplier: float
    current_balance: int
    balance_after: int
    sufficient: bool
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "user_123",
                "cost_usd": 0.5412,
                "credits_to_charge": 9742,
                "multiplier": 1.8,
                "current_balance": 289900,
                "balance_after": 280158,
                "sufficient": True
            }
        }
    }


class CreditChargeRequest(BaseSchema):
    """Request to charge credits"""
    user_id: str = Field(..., min_length=1)
    cost_usd: float = Field(..., gt=0)
    operation_id: str = Field(..., min_length=1, description="Unique operation ID")
    description: Optional[str] = Field(None, max_length=500)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "user_123",
                "cost_usd": 0.5412,
                "operation_id": "op_abc123",
                "description": "AI generation template",
                "metadata": {"template_type": "invoice"}
            }
        }
    }


class CreditChargeResponse(BaseSchema):
    """Response for successful credit charge"""
    success: bool = True
    transaction_id: str
    user_id: str
    cost_usd: float
    credits_charged: int
    balance_before: int
    balance_after: int
    operation_id: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "transaction_id": "txn_xyz789",
                "user_id": "user_123",
                "cost_usd": 0.5412,
                "credits_charged": 9742,
                "balance_before": 289900,
                "balance_after": 280158,
                "operation_id": "op_abc123"
            }
        }
    }


class CreditChargeErrorResponse(BaseSchema):
    """Response for failed credit charge"""
    success: bool = False
    error: str
    user_id: str
    required_credits: int
    current_balance: int
    deficit: int
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": False,
                "error": "insufficient_credits",
                "user_id": "user_123",
                "required_credits": 9742,
                "current_balance": 5000,
                "deficit": 4742
            }
        }
    }


class CreditAddRequest(BaseSchema):
    """Request to add credits"""
    user_id: str = Field(..., min_length=1)
    amount_usd: float = Field(..., gt=0, description="Amount in USD")
    source: str = Field(..., description="Source: purchase, subscription, bonus, refund")
    operation_id: str = Field(..., min_length=1)
    description: Optional[str] = Field(None, max_length=500)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "user_123",
                "amount_usd": 10.00,
                "source": "purchase",
                "operation_id": "op_purchase_456",
                "description": "Credit purchase",
                "metadata": {"payment_method": "stripe"}
            }
        }
    }


class CreditAddResponse(BaseSchema):
    """Response for adding credits"""
    success: bool = True
    transaction_id: str
    user_id: str
    amount_usd: float
    credits_added: int
    purchase_rate: float
    balance_before: int
    balance_after: int
    operation_id: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "transaction_id": "txn_add_789",
                "user_id": "user_123",
                "amount_usd": 10.00,
                "credits_added": 115000,
                "purchase_rate": 1.15,
                "balance_before": 5000,
                "balance_after": 120000,
                "operation_id": "op_purchase_456"
            }
        }
    }


class CreditBalanceResponse(BaseSchema):
    """Full information about user's balance"""
    user_id: str
    subscription: Optional[Dict[str, Any]] = None
    credits: CreditBalanceRead
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "user_123",
                "subscription": {
                    "tier": "premium",
                    "monthly_cost": 29.99,
                    "multiplier": 1.8,
                    "purchase_rate": 1.15
                },
                "credits": {
                    "balance": 289900,
                    "total_earned": 500000,
                    "total_spent": 210100
                }
            }
        }
    }


class CreditPurchaseRequest(BaseSchema):
    """Request to purchase credits (Public API)"""
    amount_usd: float = Field(..., gt=0, le=1000, description="Purchase amount")
    payment_method_id: str = Field(..., min_length=1, description="Payment method ID")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "amount_usd": 10.00,
                "payment_method_id": "pm_123"
            }
        }
    }


class CreditPurchaseResponse(BaseSchema):
    """Response for credit purchase"""
    success: bool = True
    transaction_id: str
    amount_usd: float
    credits_added: int
    new_balance: int
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "transaction_id": "txn_purchase_789",
                "amount_usd": 10.00,
                "credits_added": 115000,
                "new_balance": 404900
            }
        }
    }
