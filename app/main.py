from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from .models import URLInput, URLResponse, URLStats
from .utils import generate_short_code, cleanup_expired_urls, get_url_mapping
from .config import DEFAULT_EXPIRATION_DAYS

app = FastAPI(title="URL Shortener Service", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

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
    
    url_mapping = get_url_mapping()
    
    # Normalize the URL
    original_url = str(url_input.url)
    
    # Check if the URL has already been shortened
    for code, data in url_mapping.items():
        if data["original_url"] == original_url and not (data.get("expiration_date") and data["expiration_date"] < datetime.now()):
            # Update expiration if it's changed
            if url_input.expiration_days:
                data["expiration_date"] = datetime.now() + timedelta(days=url_input.expiration_days)
            
            base_url = f"{request.url.scheme}://{request.url.netloc}"
            short_url = f"{base_url}/{code}"
            
            return URLResponse(
                original_url=original_url,
                short_url=short_url,
                expiration_date=data["expiration_date"],
                access_count=data["access_count"]
            )
    
    # Generate a new short code 
    short_code = generate_short_code()
    
    # Check if custom code is already in use
    if short_code in url_mapping:
        raise HTTPException(status_code=400, detail="Custom code already in use")
    
    # Calculate expiration date
    expiration_date = datetime.now() + timedelta(days=url_input.expiration_days or DEFAULT_EXPIRATION_DAYS)
    
    # Store the mapping
    url_mapping[short_code] = {
        "original_url": original_url,
        "created_at": datetime.now(),
        "expiration_date": expiration_date,
        "access_count": 0
    }
    
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
    url_mapping = get_url_mapping()
    
    # Check if the short code exists
    if short_code not in url_mapping:
        raise HTTPException(status_code=404, detail="URL not found")
    
    # Check if the URL has expired
    url_data = url_mapping[short_code]
    if url_data.get("expiration_date") and url_data["expiration_date"] < datetime.now():
        del url_mapping[short_code]
        raise HTTPException(status_code=404, detail="URL has expired")
    
    # Increment access count
    url_mapping[short_code]["access_count"] += 1
    
    # Redirect to the original URL
    return RedirectResponse(url_data["original_url"])

@app.get("/stats/{short_code}", response_model=URLStats)
def get_url_stats(short_code: str):
    """Get statistics for a shortened URL."""
    url_mapping = get_url_mapping()
    
    if short_code not in url_mapping:
        raise HTTPException(status_code=404, detail="URL not found")
    
    url_data = url_mapping[short_code]
    
    # Check if the URL has expired
    if url_data.get("expiration_date") and url_data["expiration_date"] < datetime.now():
        del url_mapping[short_code]
        raise HTTPException(status_code=404, detail="URL has expired")
    
    return URLStats(
        original_url=url_data["original_url"],
        short_code=short_code,
        expiration_date=url_data["expiration_date"],
        access_count=url_data["access_count"],
        created_at=url_data["created_at"]
    )

@app.post("/cleanup")
def cleanup_urls():
    """Admin endpoint to manually trigger cleanup of expired URLs."""
    count = cleanup_expired_urls()
    return {"message": f"Cleaned up {count} expired URLs"}