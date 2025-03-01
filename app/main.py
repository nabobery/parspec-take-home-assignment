from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.models import URLInput, URLResponse, URLStats
from app.shortener_service import (
    shorten_given_url,
    redirect_to_original_url,
    get_url_stats_for_given_short_code,
    cleanup_expired_urls
)

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
async def read_root():
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
async def shorten_url(url_input: URLInput, request: Request):
    """Create a shortened URL."""
    return await shorten_given_url(url_input, request)

@app.get("/{short_code}")
async def redirect_to_original(short_code: str):
    """Redirect to the original URL."""
    return await redirect_to_original_url(short_code)

@app.get("/stats/{short_code}", response_model=URLStats)
async def get_url_stats(short_code: str):
    """Get statistics for a shortened URL."""
    return await get_url_stats_for_given_short_code(short_code)

@app.post("/cleanup")
async def cleanup_urls():
    """Admin endpoint to manually trigger cleanup of expired URLs."""
    count = await cleanup_expired_urls()
    return {"message": f"Cleaned up {count} expired URLs"}