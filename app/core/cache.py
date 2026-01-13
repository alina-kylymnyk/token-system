import redis
from typing import Optional, Any
import json
from app.core.config import settings

# Redis client
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True,
)


class CacheService:
    """Caching Service"""

    # Prefixes for different data types
    BALANCE_PREFIX = "balance:"
    USER_PREFIX = "user:"

    @staticmethod
    def get(key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None

    @staticmethod
    def set(key: str, value: Any, ttl: int = settings.REDIS_CACHE_TTL) -> bool:
        """Set value in cache with TTL"""
        try:
            redis_client.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            print(f"Cache set error: {e}")  
            return False

    @staticmethod
    def delete(key: str) -> bool:
        """Delete key from cache"""
        try:
            redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False

    @staticmethod
    def ping() -> bool:
        """Check Redis connection"""
        try:
            return redis_client.ping()
        except Exception:
            return False

    # ===== METHODS FOR CREDIT BALANCE =====

    @staticmethod
    def cache_balance(user_id: str, balance: int) -> bool:
        """
        Cache user's credit balance

        Args:
            user_id: User ID
            balance: Amount of credits

        Returns:
            bool: Operation success
        """
        key = f"{CacheService.BALANCE_PREFIX}{user_id}"
        return CacheService.set(key, balance, ttl=settings.REDIS_CACHE_TTL)

    @staticmethod
    def get_cached_balance(user_id: str) -> Optional[int]:  
        """
        Get user's cached credit balance

        Args:
            user_id: User ID

        Returns:
            balance if exists, else None
        """
        key = f"{CacheService.BALANCE_PREFIX}{user_id}"
        return CacheService.get(key)

    @staticmethod
    def invalidate_balance(user_id: str) -> bool:
        """
        Invalidate user's cached balance

        Args:
            user_id: User ID

        Returns:
            bool: Operation success
        """
        key = f"{CacheService.BALANCE_PREFIX}{user_id}"
        return CacheService.delete(key)

    @staticmethod
    def clear_user_cache(user_id: str) -> bool:
        """
        Clear all user cache

        Args:
            user_id: User ID

        Returns:
            bool: Operation success
        """
        try:
            # Delete all keys with user prefix
            pattern = f"*{user_id}*"  
            keys = redis_client.keys(pattern)

            if keys:
                redis_client.delete(*keys)

            return True
        except Exception as e:
            print(f"Clear user cache error: {e}")
            return False


cache = CacheService()
cache_service = CacheService()  # Alias ​​for compatibility
