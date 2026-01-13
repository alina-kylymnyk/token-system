from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from .base import BaseSchema, TransactionTypeEnum


class TransactionRead(BaseSchema):
    """Schema for reading a transaction"""
    id: int
    transaction_id: str
    type: TransactionTypeEnum
    date: datetime = Field(..., alias="created_at")
    cost_usd: Optional[float] = None
    credits: int
    balance_after: int
    description: Optional[str] = None
    operation_id: str
    
    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "transaction_id": "txn_xyz789",
                "type": "charge",
                "date": "2025-01-15T10:30:00Z",
                "cost_usd": 0.5412,
                "credits": -9742,
                "balance_after": 280158,
                "description": "AI generation template",
                "operation_id": "op_abc123"
            }
        }
    }


class TransactionListResponse(BaseSchema):
    """List of transactions with pagination"""
    total: int = Field(..., description="Total number of transactions")
    limit: int = Field(..., description="Page limit")
    offset: int = Field(..., description="Offset for pagination")
    transactions: list[TransactionRead]
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "total": 150,
                "limit": 50,
                "offset": 0,
                "transactions": [
                    {
                        "id": 1,
                        "transaction_id": "txn_xyz789",
                        "type": "charge",
                        "date": "2025-01-15T10:30:00Z",
                        "cost_usd": 0.5412,
                        "credits": -9742,
                        "balance_after": 280158,
                        "description": "AI generation template",
                        "operation_id": "op_abc123"
                    }
                ]
            }
        }
    }
