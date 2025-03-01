from fastapi import HTTPException
from datetime import datetime, timedelta
from app.redis_client import (
    set_url_data,
    get_url_data,
    delete_url_data,
    get_all_keys,
    cleanup_expired_urls_from_redis
)
from app.models import URLResponse, URLStats
from fastapi.responses import RedirectResponse
from app.utils import generate_short_code
from app.config import settings


async def shorten_given_url(url_input, request):
    """Create a shortened URL."""
    try:
        # Cleanup expired URLs in the background
        await cleanup_expired_urls()

        # Normalize the URL
        original_url = str(url_input.url)

        # Check if the URL has already been shortened
        for key in await get_all_keys():
            data = await get_url_data(key)
            if data and data.get("original_url") == original_url:
                exp_date = data.get("expiration_date")
                if exp_date and datetime.fromisoformat(exp_date) < datetime.now():
                    continue
                if url_input.expiration_days:
                    new_expiration = datetime.now() + timedelta(days=url_input.expiration_days)
                    data["expiration_date"] = new_expiration.isoformat()
                    await set_url_data(key, data)
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
        expiration_date = datetime.now() + timedelta(days=url_input.expiration_days or settings.DEFAULT_EXPIRATION_DAYS)

        url_data = {
            "original_url": original_url,
            "created_at": datetime.now().isoformat(),
            "expiration_date": expiration_date.isoformat(),
            "access_count": 0
        }
        await set_url_data(short_code, url_data)

        base_url = f"{request.url.scheme}://{request.url.netloc}"
        short_url = f"{base_url}/{short_code}"
        return URLResponse(
            original_url=original_url,
            short_url=short_url,
            expiration_date=expiration_date,
            access_count=0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while shortening the URL: {str(e)}")

async def redirect_to_original_url(short_code: str):
    """Redirect to the original URL."""
    try:
        data = await get_url_data(short_code)
        if not data:
            raise HTTPException(status_code=404, detail="URL not found")

        exp_date = data.get("expiration_date")
        if exp_date and datetime.fromisoformat(exp_date) < datetime.now():
            await delete_url_data(short_code)
            raise HTTPException(status_code=404, detail="URL has expired")

        data["access_count"] = data.get("access_count", 0) + 1
        await set_url_data(short_code, data)

        return RedirectResponse(data["original_url"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while redirecting: {str(e)}")

async def get_url_stats_for_given_short_code(short_code: str):
    """Get statistics for a shortened URL."""
    try:
        data = await get_url_data(short_code)
        if not data:
            raise HTTPException(status_code=404, detail="URL not found")
        exp_date = data.get("expiration_date")
        if exp_date and datetime.fromisoformat(exp_date) < datetime.now():
            await delete_url_data(short_code)
            raise HTTPException(status_code=404, detail="URL has expired")
        return URLStats(
            original_url=data["original_url"],
            short_code=short_code,
            expiration_date=datetime.fromisoformat(data["expiration_date"]),
            access_count=data.get("access_count", 0),
            created_at=datetime.fromisoformat(data["created_at"])
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching URL stats: {str(e)}")

async def cleanup_expired_urls():
    """Admin endpoint to manually trigger cleanup of expired URLs."""
    try:
        count = await cleanup_expired_urls_from_redis()
        return count
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during cleanup: {str(e)}") 