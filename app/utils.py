import random
from app.redis_client import get_all_keys
from app.config import settings


# Function to generate a unique short code
def generate_short_code(length=settings.SHORT_URL_LENGTH):
    """Generate a random short code of specified length."""
    characters = settings.CHARACTERS
    while True:
        short_code = ''.join(random.choices(characters, k=length))
        if short_code not in get_all_keys():
            return short_code
