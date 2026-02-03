import redis
from config import Config
from logger import get_logger

logger = get_logger()


# ===== INIT REDIS =====
try:
    r = redis.from_url(Config.REDIS_URL)
    logger.info("Redis cache connected")

except Exception as e:
    logger.error(f"Redis init failed: {e}")
    r = None  # graceful fallback


# ===== SAVE CACHE =====
def cache_history(user_id, text):
    if not r:
        return

    try:
        key = f"chat:{user_id}"

        logger.debug(f"Caching message for {user_id}")

        r.lpush(key, text)
        r.ltrim(key, 0, 9)

    except Exception as e:
        logger.error(f"Redis cache save failed: {e}")


# ===== GET CACHE =====
def get_cache(user_id):
    if not r:
        return ""

    try:
        key = f"chat:{user_id}"

        items = r.lrange(key, 0, 9)

        if not items:
            logger.debug("Cache miss")
            return ""

        logger.debug("Cache hit")

        return "\n".join(i.decode() for i in reversed(items))

    except Exception as e:
        logger.error(f"Redis fetch failed: {e}")
        return ""
