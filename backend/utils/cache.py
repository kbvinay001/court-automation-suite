"""
Cache utility - Redis-based caching for scraped data and API responses.
"""

import os
import json
import hashlib
import logging
from typing import Optional, Any
from datetime import timedelta

logger = logging.getLogger(__name__)

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DEFAULT_TTL = int(os.getenv("CACHE_TTL_SECONDS", "3600"))  # 1 hour default

# Cache singleton
_redis_client = None


async def init_cache():
    """Initialize Redis connection."""
    global _redis_client
    if not REDIS_AVAILABLE:
        logger.warning("⚠ redis package not installed, caching disabled")
        return

    try:
        _redis_client = aioredis.from_url(
            REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
        )
        await _redis_client.ping()
        logger.info("✅ Connected to Redis cache")
    except Exception as e:
        logger.warning(f"⚠ Redis connection failed (caching disabled): {e}")
        _redis_client = None


async def close_cache():
    """Close Redis connection."""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
        logger.info("Redis connection closed")


def get_cache():
    """Get Redis client instance."""
    return _redis_client


def _make_key(prefix: str, identifier: str) -> str:
    """Generate a cache key with prefix and hashed identifier.

    MD5 is used purely as a non-cryptographic key shortener (nosec B324).
    """
    key_hash = hashlib.md5(identifier.encode(), usedforsecurity=False).hexdigest()[:12]  # nosec B324
    return f"court:{prefix}:{key_hash}"


async def cache_get(key: str) -> Optional[Any]:
    """Get a value from cache. Returns None if not found or cache unavailable."""
    if not _redis_client:
        return None
    try:
        value = await _redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        logger.debug(f"Cache get failed for {key}: {e}")
        return None


async def cache_set(key: str, value: Any, ttl: int = DEFAULT_TTL) -> bool:
    """Set a value in cache with TTL in seconds."""
    if not _redis_client:
        return False
    try:
        serialized = json.dumps(value, default=str)
        await _redis_client.setex(key, ttl, serialized)
        return True
    except Exception as e:
        logger.debug(f"Cache set failed for {key}: {e}")
        return False


async def cache_delete(key: str) -> bool:
    """Delete a key from cache."""
    if not _redis_client:
        return False
    try:
        await _redis_client.delete(key)
        return True
    except Exception:
        return False


async def cache_clear_pattern(pattern: str) -> int:
    """Delete all keys matching a pattern (e.g., 'court:cases:*')."""
    if not _redis_client:
        return 0
    try:
        keys = []
        async for key in _redis_client.scan_iter(match=pattern):
            keys.append(key)
        if keys:
            await _redis_client.delete(*keys)
        return len(keys)
    except Exception as e:
        logger.debug(f"Cache clear pattern failed: {e}")
        return 0


async def cache_case(case_number: str, data: dict, ttl: int = 1800):
    """Cache case data (30 min default)."""
    key = _make_key("case", case_number)
    await cache_set(key, data, ttl)


async def get_cached_case(case_number: str) -> Optional[dict]:
    """Get cached case data."""
    key = _make_key("case", case_number)
    return await cache_get(key)  # type: ignore[misc]


async def cache_causelist(court: str, date_str: str, data: dict, ttl: int = 900):
    """Cache cause list data (15 min default)."""
    key = _make_key("causelist", f"{court}:{date_str}")
    await cache_set(key, data, ttl)


async def get_cached_causelist(court: str, date_str: str) -> Optional[dict]:
    """Get cached cause list data."""
    key = _make_key("causelist", f"{court}:{date_str}")
    return await cache_get(key)  # type: ignore[misc]
