from app.db.database import engine
from app.core.cache import cache

print("Testing PostgreSQL connection...")
try:
    with engine.connect() as conn:
        print("✓ PostgreSQL connected successfully!")
except Exception as e:
    print(f"✗ PostgreSQL connection failed: {e}")

print("\nTesting Redis connection...")
if cache.ping():
    print("✓ Redis connected successfully!")
else:
    print("✗ Redis connection failed")