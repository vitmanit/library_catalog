from redis.asyncio import Redis
import json
from typing import Optional, Any
from functools import wraps


class CacheService:
    def __init__(self, redis: Redis):
        self.redis = redis
        self.default_ttl = 300  # 5 minutes

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(self, key: str, value: Any, ttl: int = None):
        """Set value in cache"""
        ttl = ttl or self.default_ttl
        await self.redis.setex(
            key,
            ttl,
            json.dumps(value, default=str)
        )

    async def delete(self, key: str):
        """Delete key from cache"""
        await self.redis.delete(key)

    async def delete_pattern(self, pattern: str):
        """Delete keys by pattern"""
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)


def cache_response(key_prefix: str, ttl: int = 300):
    """Decorator for caching endpoint responses"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Получаем cache service из dependencies
            cache: CacheService = kwargs.get('cache')
            if not cache:
                return await func(*args, **kwargs)

            # Создаем ключ кеша
            cache_key = f"{key_prefix}:{json.dumps(kwargs, default=str)}"

            # Проверяем кеш
            cached = await cache.get(cache_key)
            if cached:
                return cached

            # Вызываем функцию
            result = await func(*args, **kwargs)

            # Сохраняем в кеш
            await cache.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator