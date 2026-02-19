import redis
from config.config import Config
from config.logger import get_logger
import json

logger = get_logger()

try:
    # Handle Redis URL with SSL (rediss://)
    redis_url = Config.REDIS_URL
    
    if redis_url.startswith("rediss://"):
        # For SSL connections, disable certificate verification if needed
        r = redis.from_url(
            redis_url,
            ssl_certfile=None,
            ssl_keyfile=None,
            ssl_cert_reqs="none",
            decode_responses=True
        )
    else:
        r = redis.from_url(redis_url, decode_responses=True)
    
    # Test connection
    r.ping()
    logger.info("✅ Redis cache connected successfully")

except Exception as e:
    logger.error(f"❌ Redis init failed: {e}")
    r = None


def cache_history(user_id: str, text: str) -> bool:
    """
    Cache a message (user or assistant) in Redis.
    
    Args:
        user_id: User identifier
        text: Message text to cache
    
    Returns:
        True if successful, False otherwise
    """
    if not r:
        logger.warning("Redis not available, skipping cache")
        return False

    try:
        key = f"chat:{user_id}"
        logger.debug(f"Caching message for {user_id}: {text[:50]}...")
        
        # Add the message to the list
        r.lpush(key, text)
        
        # Keep only last 20 messages
        r.ltrim(key, 0, 19)
        
        # Set expiration (24 hours)
        r.expire(key, 86400)
        
        logger.debug(f"✅ Message cached for {user_id}")
        return True

    except Exception as e:
        logger.error(f"❌ Redis cache save failed: {e}")
        return False


def get_cache(user_id: str, limit: int = 10) -> str:
    """
    Retrieve cached conversation history for a user.
    
    Args:
        user_id: User identifier
        limit: Number of recent messages to retrieve
    
    Returns:
        Formatted conversation history string
    """
    if not r:
        logger.warning("Redis not available, returning empty cache")
        return ""

    try:
        key = f"chat:{user_id}"
        
        # Get the messages (most recent first)
        items = r.lrange(key, 0, limit - 1)

        if not items:
            logger.debug(f"Cache miss for {user_id}")
            return ""

        logger.debug(f"✅ Cache hit for {user_id} - {len(items)} messages")
        
        # Reverse to get chronological order
        history = "\n".join(reversed(items))
        return history

    except Exception as e:
        logger.error(f"❌ Redis fetch failed: {e}")
        return ""


def clear_cache(user_id: str) -> bool:
    """Clear conversation history for a user."""
    if not r:
        return False
    
    try:
        key = f"chat:{user_id}"
        r.delete(key)
        logger.info(f"✅ Cache cleared for {user_id}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to clear cache: {e}")
        return False
