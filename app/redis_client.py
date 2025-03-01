from upstash_redis.asyncio import Redis
import json
from datetime import datetime
from app.config import settings

# Initialize Redis client with settings
redis = Redis(url=settings.UPSTASH_REDIS_REST_URL, token=settings.UPSTASH_REDIS_REST_TOKEN)


async def set_url_data(short_code: str, data: dict):
    """Store url data as JSON string in Redis"""
    await redis.set(short_code, json.dumps(data))


async def get_url_data(short_code: str):
    """Retrieve url data from Redis and parse it as a dict"""
    value = await redis.get(short_code)
    if value is None:
        return None
    return json.loads(value)


async def delete_url_data(short_code: str):
    """Delete a URL mapping from Redis"""
    await redis.delete(short_code)


async def get_all_keys():
    """Return all keys from Redis"""
    return await redis.keys("*")


async def cleanup_expired_urls_from_redis():
    """Cleanup expired URLs stored in Redis and return count of deleted items"""
    count = 0
    keys = await get_all_keys()
    for key in keys:
        data = await get_url_data(key)
        if data and data.get("expiration_date"):
            expiration = datetime.fromisoformat(data["expiration_date"])
            if expiration < datetime.now():
                await delete_url_data(key)
                count += 1
    return count 