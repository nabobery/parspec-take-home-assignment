from upstash_redis import Redis
import json
from datetime import datetime
from app.config import settings

# Initialize Redis client with settings
redis = Redis(url=settings.UPSTASH_REDIS_REST_URL, token=settings.UPSTASH_REDIS_REST_TOKEN)


def set_url_data(short_code: str, data: dict):
    """Store url data as JSON string in Redis"""
    redis.set(short_code, json.dumps(data))


def get_url_data(short_code: str):
    """Retrieve url data from Redis and parse it as a dict"""
    value = redis.get(short_code)
    if value is None:
        return None
    return json.loads(value)


def delete_url_data(short_code: str):
    """Delete a URL mapping from Redis"""
    redis.delete(short_code)


def get_all_keys():
    """Return all keys from Redis"""
    return redis.keys("*")


def cleanup_expired_urls():
    """Cleanup expired URLs stored in Redis and return count of deleted items"""
    count = 0
    keys = get_all_keys()
    for key in keys:
        data = get_url_data(key)
        if data and data.get("expiration_date"):
            expiration = datetime.fromisoformat(data["expiration_date"])
            if expiration < datetime.now():
                delete_url_data(key)
                count += 1
    return count 