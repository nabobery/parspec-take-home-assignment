from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from app.models import URLInput, URLResponse, URLStats
from app.redis_client import (
    set_url_data,
    get_url_data,
    delete_url_data,
    get_all_keys,
    cleanup_expired_urls
)
from app.config import settings
from app.utils import generate_short_code

# APP definition
app = FastAPI(title="URL Shortener Service", version="1.0.0")

# Added CORS middleware to app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Welcome endpoint to get details of all available endpoints
@app.get("/")
def read_root():
    """Welcome endpoint with basic service information."""
    return {
        "service": "URL Shortener Service",
        "version": "1.0.0",
        "endpoints": {
            "GET /": "Service information",
            "POST /shorten": "Create a shortened URL",
            "GET /{short_code}": "Redirect to the original URL",
            "GET /stats/{short_code}": "Get statistics for a shortened URL",
            "POST /cleanup": "Cleanup expired URLs (admin endpoint)"
        }
    }

@app.post("/shorten", response_model=URLResponse)
def shorten_url(url_input: URLInput, request: Request):
    """Create a shortened URL."""
    # Cleanup expired URLs in the background
    cleanup_expired_urls()

    # Normalize the URL
    original_url = str(url_input.url)

    # Check if the URL has already been shortened
    # TODO: Have to optimize this by using reverse lookup of original url and short code
    for key in get_all_keys():
        data = get_url_data(key)
        if data and data.get("original_url") == original_url:
            exp_date = data.get("expiration_date")
            # if expired, go to generate short code
            if exp_date and datetime.fromisoformat(exp_date) < datetime.now():
                continue
            # Update expiration if it's changed
            if url_input.expiration_days:
                new_expiration = datetime.now() + timedelta(days=url_input.expiration_days)
                data["expiration_date"] = new_expiration.isoformat()
                set_url_data(key, data)
            # just return the shortened url after we found it
            base_url = f"{request.url.scheme}://{request.url.netloc}"
            short_url = f"{base_url}/{key}"
            return URLResponse(
                original_url=original_url,
                short_url=short_url,
                expiration_date=datetime.fromisoformat(data["expiration_date"]),
                access_count=data.get("access_count", 0)
            )

    # Generate a new short code 
    short_code = generate_short_code()

    # Calculate expiration date
    expiration_date = datetime.now() + timedelta(days=url_input.expiration_days or settings.DEFAULT_EXPIRATION_DAYS)

    # Store the mapping in Redis
    url_data = {
        "original_url": original_url,
        "created_at": datetime.now().isoformat(),
        "expiration_date": expiration_date.isoformat(),
        "access_count": 0
    }
    set_url_data(short_code, url_data)

    base_url = f"{request.url.scheme}://{request.url.netloc}"
    short_url = f"{base_url}/{short_code}"
    return URLResponse(
        original_url=original_url,
        short_url=short_url,
        expiration_date=expiration_date,
        access_count=0
    )

@app.get("/{short_code}")
def redirect_to_original(short_code: str):
    """Redirect to the original URL."""
    data = get_url_data(short_code)
    if not data:
        raise HTTPException(status_code=404, detail="URL not found")

    # Check if the URL has expired
    exp_date = data.get("expiration_date")
    if exp_date and datetime.fromisoformat(exp_date) < datetime.now():
        delete_url_data(short_code)
        raise HTTPException(status_code=404, detail="URL has expired")

    # Increment access count
    data["access_count"] = data.get("access_count", 0) + 1
    set_url_data(short_code, data)

    return RedirectResponse(data["original_url"])

@app.get("/stats/{short_code}", response_model=URLStats)
def get_url_stats(short_code: str):
    """Get statistics for a shortened URL."""
    data = get_url_data(short_code)
    if not data:
        raise HTTPException(status_code=404, detail="URL not found")
    exp_date = data.get("expiration_date")
    if exp_date and datetime.fromisoformat(exp_date) < datetime.now():
        delete_url_data(short_code)
        raise HTTPException(status_code=404, detail="URL has expired")
    return URLStats(
        original_url=data["original_url"],
        short_code=short_code,
        expiration_date=datetime.fromisoformat(data["expiration_date"]),
        access_count=data.get("access_count", 0),
        created_at=datetime.fromisoformat(data["created_at"])
    )

@app.post("/cleanup")
def cleanup_urls():
    """Admin endpoint to manually trigger cleanup of expired URLs."""
    count = cleanup_expired_urls()
    return {"message": f"Cleaned up {count} expired URLs"}