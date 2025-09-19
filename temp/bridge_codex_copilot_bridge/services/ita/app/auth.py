
from fastapi import Header, HTTPException, status
import os

API_KEY_ENV = "ITA_API_KEY"

def require_api_key(x_api_key: str | None = Header(default=None)):
    expected = os.getenv(API_KEY_ENV)
    if not expected:
        # In development allow missing key for local testing, but log loudly.
        return
    if x_api_key != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

def require_request_id(x_request_id: str | None = Header(default=None)):
    # Strongly recommended for tracing; not strictly enforced here.
    return x_request_id
