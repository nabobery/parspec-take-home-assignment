from pydantic import BaseModel, HttpUrl, field_validator
from typing import Optional
from datetime import datetime

class URLInput(BaseModel):
    url: HttpUrl
    expiration_days: Optional[int] = None
    
    @field_validator('expiration_days')
    def validate_expiration(cls, v):
        if v is not None and (v <= 0 or v > 365):
            raise ValueError("Expiration days must be between 1 and 365")
        return v

class URLResponse(BaseModel):
    original_url: str
    short_url: str
    expiration_date: datetime
    access_count: int

class URLStats(BaseModel):
    original_url: str
    short_code: str
    expiration_date: datetime
    access_count: int
    created_at: datetime