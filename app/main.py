from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


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
            "GET /cleanup": "Cleanup expired URLs (admin endpoint)"
        }
    }


@app.get("/api/health")
def health_check():
    return {"status": "ok"}