# Parspec Take Home Assignment

An URL shortener service built with FastAPI that allows users to shorten long URLs, redirect to the original URLs, and track access statistics.

## Features

- **URL Shortening**: Convert long URLs into short, manageable links
- **Redirection**: Redirect short URLs to their original destinations
- **Access Statistics**: Track how many times each shortened URL has been accessed
- **Expiration (TTL)**: Set expiration dates for URLs with automatic cleanup
- **Validation**: Ensure URLs are valid
- **Persistent Storage**: Utilizes Redis for storing URL mappings, ensuring data persistence across service restarts

## Design Decisions

### Architecture

The service is built with a clean, modular architecture:

- **FastAPI** as the web framework for its speed, simplicity, and built-in validation
- **Pydantic models** for request/response validation and data modeling
- **Redis** for persistent storage of URL mappings, allowing for automatic cleanup of expired URLs
- **Clean separation** between API endpoints and business logic

### Architecture Diagram

![Architecture Diagram](assets/Architecture%20Diagram.png)

### URL Shortening Strategy

- Generate random alphanumeric codes of configurable length (default: 6 characters)
- Automatic reuse of existing short URLs for the same long URL

### Scalability Considerations

- The current implementation uses Redis for persistent storage, making it suitable for production use
- The code structure makes it easy to replace or extend the storage mechanism if needed
- Background cleanup of expired URLs to maintain storage efficiency
- Proper error handling and validation to ensure system stability

### Extensibility

The service is designed with extensibility in mind:

- Modular code structure makes it easy to add new features
- Configuration variables for key parameters
- Clean separation of concerns making it easy to modify or replace components

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- Redis instance (e.g., Upstash)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/nabobery/parspec-take-home-assignment.git
cd url-shortener
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the dependencies:

```bash
pip install -r requirements.txt
```

4. Set up your Redis configuration in a `.env` file:

```env
UPSTASH_REDIS_REST_URL=<your-rest-url>
UPSTASH_REDIS_REST_TOKEN=<your-token>

```

### Running the Service

Start the service with:

```bash
python app/main.py
```

The service will be available at `http://localhost:8000`.

### API Documentation

Once the service is running, you can access the interactive API documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Create a Shortened URL

```bash
POST /shorten
```

Request body:

```json
{
  "url": "https://example.com/very/long/url/that/needs/shortening",
  "expiration_days": 30 // Optional, defaults to 7
}
```

Response:

```json
{
  "original_url": "https://example.com/very/long/url/that/needs/shortening",
  "short_url": "http://localhost:8000/mycode",
  "expiration_date": "2023-12-15T12:30:45.123456",
  "access_count": 0
}
```

### Redirect to Original URL

```bash
GET /{short_code}
```

This endpoint redirects to the original URL associated with the provided short code.

### Get URL Statistics

```bash
GET /stats/{short_code}
```

Response:

```json
{
  "original_url": "https://example.com/very/long/url/that/needs/shortening",
  "short_code": "mycode",
  "expiration_date": "2023-12-15T12:30:45.123456",
  "access_count": 42,
  "created_at": "2023-11-15T12:30:45.123456"
}
```

### Cleanup Expired URLs

```bash
GET /cleanup
```

Response:

```json
{
  "message": "Cleaned up 5 expired URLs"
}
```

## Running Tests

The service includes a comprehensive test suite. To run the tests:

```bash
pytest
```

## Challenges and Solutions

1. **URL Validation**: Used Pydantic's `HttpUrl` type for robust URL validation
2. **Concurrency**: Designed with thread safety in mind for multi-user access
3. **Collision Handling**: Implemented a loop to ensure unique short codes
4. **Expiration Logic**: Created an efficient cleanup mechanism for expired URLs
5. **Persistent Storage**: Integrated Redis for data persistence

## Future Improvements

1. **User Authentication**: Add user accounts and API keys
2. **Analytics**: More detailed access statistics (referrers, geography, etc.)
3. **Rate Limiting**: Prevent abuse with rate limiting
4. **Custom Domains**: Support for custom domains for shortened URLs

