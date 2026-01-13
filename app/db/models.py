from sqlalchemy import (
    Column, String, Float, Integer, Boolean, 
    DateTime, ForeignKey, Text, Enum as SQLEnum,
    Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime
import enum
from app.db.database import Base

#Enum
class TransactionType(str, enum.Enum):
    CHARGE = "charge"
    ADD = "add"
    SUBSCRIPTION = "subscription"
    BONUS = "bonus"
    REFUND = "refund"

class SubscriptionTier(str, enum.Enum):
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"

# Models
class SubscriptionPlan(Base):
    """Subscription Plans"""
    __tablename__ = "subscription_plans"

    tier = Column(
        SQLEnum(SubscriptionTier, name="subscription_tier_enum"),
        primary_key=True,
        index=True
    )
    name = Column(String(100), nullable=False)
    monthly_cost = Column(Float, nullable=False)
    fixed_cost = Column(Float, nullable=False, default=5.00)
    credits_included = Column(Integer, nullable=False)
    bonus_credits = Column(Integer, nullable=False, default=0)
    multiplier = Column(Float, nullable=False)
    purchase_rate = Column(Float, nullable=False, default=1.0)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="subscription_plan")

    # Constraints
    __table_args__ = (
        CheckConstraint('monthly_cost > 0', name='check_monthly_cost_positive'),
        CheckConstraint('fixed_cost >= 0', name='check_fixed_cost_non_negative'),
        CheckConstraint('credits_included >= 0', name='check_credits_included_non_negative'),
        CheckConstraint('bonus_credits >= 0', name='check_bonus_credits_non_negative'),
        CheckConstraint('multiplier > 0', name='check_multiplier_positive'),
        CheckConstraint('purchase_rate >= 1.0', name='check_purchase_rate_min'),
    )

    def __repr__(self):
        return f"<SubscriptionPlan(tier={self.tier}, name={self.name})>"
    
    @property
    def total_credits(self):
        """Total number of credits (base + bonus)"""
        return self.credits_included + self.bonus_credits
    
class User(Base):
    """System users"""
    __tablename__ = "users"

    user_id = Column(String(100), primary_key=True, index=True)
    subscription_tier = Column(
        SQLEnum(SubscriptionTier, name="subscription_tier_enum"),
        ForeignKey("subscription_plans.tier"),
        nullable=True
    )
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscription_plan = relationship("SubscriptionPlan", back_populates="users")
    credit_balance = relationship("CreditBalance", back_populates="user",uselist=False)
    transactions = relationship("Transaction", back_populates="user", order_by="Transaction.created_at.desc()")

    
    def __repr__(self):
        return f"<CreditBalance(user_id={self.user_id}, balance={self.balance})>"

class CreditBalance(Base):
    """User Credit Balance"""
    __tablename__ = "credit_balances"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), ForeignKey("users.user_id"), unique=True, nullable=False, index=True)
    balance = Column(Integer, nullable=False, default=0)
    total_earned = Column(Integer, nullable=False, default=0)
    total_spent = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="credit_balance")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('balance >= 0', name='check_balance_non_negative'),
        CheckConstraint('total_earned >= 0', name='check_total_earned_non_negative'),
        CheckConstraint('total_spent >= 0', name='check_total_spent_non_negative'),
    )
    
    def __repr__(self):
        return f"<CreditBalance(user_id={self.user_id}, balance={self.balance})>"



class Transaction(Base):
    """Credit transaction history"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String(100), unique=True, nullable=False, index=True)
    user_id = Column(String(100), ForeignKey("users.user_id"), nullable=False, index=True)
    type = Column(
        SQLEnum(TransactionType, name="transaction_type_enum"),
        nullable=False,
        index=True
    )
    operation_id = Column(String(100), unique=True, nullable=False, index=True)
    cost_usd = Column(Float, nullable=True)  # NULL for operations with no cost
    credits = Column(Integer, nullable=False)  # Can be negative for billing
    balance_after = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    meta_info = Column(JSON, nullable=True, default={})
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('balance_after >= 0', name='check_balance_after_non_negative'),
        Index('ix_transactions_user_created', 'user_id', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, user_id={self.user_id}, type={self.type}, credits={self.credits})>"

class SystemSettings(Base):
    """System Settings"""
    __tablename__ = "system_settings"

    key = Column(String(100), primary_key=True, index=True)
    value = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<SystemSettings(key={self.key}, value={self.value})>"
