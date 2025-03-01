import string
from pydantic_settings import BaseSettings

# Configuration
class Settings(BaseSettings):
    DEFAULT_EXPIRATION_DAYS: int = 7   # Default TTL in days
    CHARACTERS: str = string.ascii_letters + string.digits
    UPTASH_REDIS_REST_URL: str
    UPSTASH_REDIS_REST_TOKEN: str
    SHORT_URL_LENGTH: int = 6

    class Config:
        env_file = ".env"


settings = Settings()