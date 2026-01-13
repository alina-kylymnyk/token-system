from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import SubscriptionPlan, SystemSettings, SubscriptionTier


def seed_subscription_plans(db: Session):
    """Creating tariff plans"""
    plans = [
        {
            "tier": SubscriptionTier.BASIC,
            "name": "Базова",
            "monthly_cost": 9.99,
            "fixed_cost": 5.00,
            "credits_included": 49900,
            "bonus_credits": 0,
            "multiplier": 2.0,
            "purchase_rate": 1.0,
            "active": True
        },
        {
            "tier": SubscriptionTier.STANDARD,
            "name": "Середня",
            "monthly_cost": 19.99,
            "fixed_cost": 5.00,
            "credits_included": 149900,
            "bonus_credits": 20000,
            "multiplier": 1.9,
            "purchase_rate": 1.1,
            "active": True
        },
        {
            "tier": SubscriptionTier.PREMIUM,
            "name": "Преміум",
            "monthly_cost": 29.99,
            "fixed_cost": 5.00,
            "credits_included": 249900,
            "bonus_credits": 40000,
            "multiplier": 1.8,
            "purchase_rate": 1.15,
            "active": True
        }
    ]
    
    for plan_data in plans:
        # Check if a plan exists
        existing = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.tier == plan_data["tier"]
        ).first()
        
        if not existing:
            plan = SubscriptionPlan(**plan_data)
            db.add(plan)
            print(f"✓ Created plan: {plan_data['name']}")
        else:
            print(f"○ Plan already exists: {plan_data['name']}")
    
    db.commit()


def seed_system_settings(db: Session):
    """Creating system settings"""
    
    settings = [
        {
            "key": "exchange_rate",
            "value": "10000",
            "description": "Базовий курс конвертації: $1 = 10,000 кредитів"
        }
    ]
    
    for setting_data in settings:
        existing = db.query(SystemSettings).filter(
            SystemSettings.key == setting_data["key"]
        ).first()
        
        if not existing:
            setting = SystemSettings(**setting_data)
            db.add(setting)
            print(f"✓ Created setting: {setting_data['key']}")
        else:
            print(f"○ Setting already exists: {setting_data['key']}")
    
    db.commit()


def seed_all():
    """Run all seed functions"""
    print("Starting database seeding...")
    
    db = SessionLocal()
    
    try:
        seed_subscription_plans(db)
        seed_system_settings(db)
        print("\n✓ Database seeding completed successfully!")
    except Exception as e:
        print(f"\n✗ Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_all()