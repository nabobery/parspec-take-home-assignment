import random
from datetime import datetime
from typing import Dict
from app.config import SHORT_URL_LENGTH, CHARACTERS

# In-memory storage
url_mapping: Dict[str, dict] = {}

def generate_short_code() -> str:
    """Generate a random short code for the URL."""
    while True:
        code = ''.join(random.choice(CHARACTERS) for _ in range(SHORT_URL_LENGTH))
        if code not in url_mapping:
            return code

def cleanup_expired_urls() -> int:
    """Remove expired URLs from the mapping."""
    current_time = datetime.now()
    expired_codes = [code for code, data in url_mapping.items() 
                    if data.get("expiration_date") and data["expiration_date"] < current_time]
    
    for code in expired_codes:
        del url_mapping[code]
    
    return len(expired_codes)

def get_url_mapping() -> Dict[str, dict]:
    """Get the URL mapping dictionary."""
    return url_mapping