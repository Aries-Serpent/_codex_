"""
Rate limiting middleware
Per-tenant token bucket rate limiting (in-memory)
"""

import json
import logging
import time
from dataclasses import dataclass
from typing import Dict, Optional

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from ..config import settings

logger = logging.getLogger(__name__)


@dataclass
class TokenBucket:
    """Simple token bucket for rate limiting"""

    capacity: int
    tokens: float
    last_refill: float
    refill_rate: float  # tokens per second

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        if elapsed <= 0:
            return

        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.refill_rate,
        )
        self.last_refill = now

    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens

        Returns:
            True if tokens consumed, False if insufficient tokens
        """
        self._refill()

        # Try to consume
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def available_tokens(self) -> float:
        """Return the currently available tokens after refilling."""
        self._refill()
        return self.tokens


class RateLimiter:
    """Per-tenant rate limiter using token buckets"""

    def __init__(self):
        self.request_buckets: Dict[str, TokenBucket] = {}
        self.token_buckets: Dict[str, TokenBucket] = {}

    def _get_or_create_bucket(
        self,
        tenant_id: str,
        bucket_type: str,
        capacity: int,
        refill_rate: float,
    ) -> TokenBucket:
        """Get or create a token bucket for a tenant"""
        buckets = self.request_buckets if bucket_type == "request" else self.token_buckets

        if tenant_id not in buckets:
            buckets[tenant_id] = TokenBucket(
                capacity=capacity,
                tokens=capacity,
                last_refill=time.time(),
                refill_rate=refill_rate,
            )

        return buckets[tenant_id]

    def check_request_limit(self, tenant_id: str, quota: Optional[Dict[str, int]] = None) -> bool:
        """Check if request is within rate limit

        Returns:
            True if request allowed, False if rate limited
        """
        if not settings.rate_limit_enabled:
            return True

        # Get quota
        requests_per_minute = settings.rate_limit_requests_per_minute
        if quota:
            requests_per_minute = quota.get("requests_per_minute", requests_per_minute)

        # Create bucket with refill rate = capacity / 60 (per second)
        bucket = self._get_or_create_bucket(
            tenant_id,
            "request",
            requests_per_minute,
            requests_per_minute / 60.0,
        )

        return bucket.consume(1)

    def check_token_limit(
        self,
        tenant_id: str,
        tokens: int,
        quota: Optional[Dict[str, int]] = None,
    ) -> bool:
        """Check if token usage is within rate limit

        Returns:
            True if tokens allowed, False if rate limited
        """
        if not settings.rate_limit_enabled:
            return True

        # Get quota
        tokens_per_minute = settings.rate_limit_tokens_per_minute
        if quota:
            tokens_per_minute = quota.get("tokens_per_minute", tokens_per_minute)

        # Create bucket with refill rate = capacity / 60 (per second)
        bucket = self._get_or_create_bucket(
            tenant_id,
            "token",
            tokens_per_minute,
            tokens_per_minute / 60.0,
        )

        allowed = bucket.consume(tokens)

        if not allowed:
            # When usage exceeds quota, drain the bucket so future requests block
            bucket.tokens = 0

        return allowed


# Global rate limiter
rate_limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce per-tenant rate limits"""

    @staticmethod
    def _extract_requested_tokens(body_bytes: bytes) -> int:
        """Extract requested tokens from the request body with sane defaults."""
        default_tokens = 512

        if not body_bytes:
            return default_tokens

        try:
            payload = json.loads(body_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return default_tokens

        requested = payload.get("max_tokens", default_tokens)

        try:
            requested_int = int(requested)
        except (TypeError, ValueError):
            return default_tokens

        return max(1, requested_int)

    async def dispatch(self, request: Request, call_next):
        # Skip health check and docs endpoints
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # Get tenant from request state (set by TenantContextMiddleware)
        tenant = getattr(request.state, "tenant", None)
        if not tenant:
            # No tenant context, skip rate limiting
            return await call_next(request)

        tenant_id = tenant["tenant_id"]
        quota = tenant.get("quota", {})

        # Check request rate limit
        if not rate_limiter.check_request_limit(tenant_id, quota):
            logger.warning(f"Request rate limit exceeded for tenant: {tenant_id}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Request rate limit exceeded. Please try again later.",
                headers={"Retry-After": "60"},
            )

        # Pre-flight check: ensure tenant has token quota available
        # This prevents requests from being processed if not enough tokens are available
        requested_tokens = 1
        tokens_per_minute = None
        token_bucket: Optional[TokenBucket] = None
        if settings.rate_limit_enabled:
            tokens_per_minute = settings.rate_limit_tokens_per_minute
            if quota:
                tokens_per_minute = quota.get("tokens_per_minute", tokens_per_minute)

            # Get or create token bucket to check availability
            token_bucket = rate_limiter._get_or_create_bucket(
                tenant_id,
                "token",
                tokens_per_minute,
                tokens_per_minute / 60.0,
            )

            if request.url.path == "/v1/infer" and request.method.upper() == "POST":
                body_bytes = await request.body()
                requested_tokens = self._extract_requested_tokens(body_bytes)
                # Ensure downstream handlers can re-read the body
                request._body = body_bytes
                body_consumed = False

                async def receive_with_body():
                    nonlocal body_consumed
                    if not body_consumed:
                        body_consumed = True
                        return {
                            "type": "http.request",
                            "body": body_bytes,
                            "more_body": False,
                        }
                    return {
                        "type": "http.request",
                        "body": b"",
                        "more_body": False,
                    }

                request._receive = receive_with_body

            available_tokens = token_bucket.available_tokens()

            if available_tokens < requested_tokens:
                logger.warning(
                    "Token quota exhausted for tenant: %s (requested=%s, available=%s)",
                    tenant_id,
                    requested_tokens,
                    available_tokens,
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Token quota exceeded. Please try again later.",
                    headers={"Retry-After": "60"},
                )

        # Process request
        response = await call_next(request)

        # Check if this is an inference endpoint and extract token usage
        if (
            request.url.path == "/v1/infer"
            and isinstance(response, Response)
            and settings.rate_limit_enabled
        ):
            try:
                # Read response body
                response_body = b""
                async for chunk in response.body_iterator:
                    response_body += chunk

                # Parse JSON response
                response_data = json.loads(response_body.decode())

                # Extract tokens used
                tokens_used = response_data.get("tokens_used", 0)

                if tokens_used > 0:
                    post_tokens_per_minute = (
                        tokens_per_minute or settings.rate_limit_tokens_per_minute
                    )
                    if quota:
                        post_tokens_per_minute = quota.get(
                            "tokens_per_minute",
                            post_tokens_per_minute,
                        )

                    # Consume tokens from the bucket
                    token_bucket = rate_limiter._get_or_create_bucket(
                        tenant_id,
                        "token",
                        post_tokens_per_minute,
                        post_tokens_per_minute / 60.0,
                    )

                    if not token_bucket.consume(tokens_used):
                        # Drain remaining tokens to enforce blocking on subsequent requests
                        token_bucket.tokens = 0
                        logger.warning(
                            f"Token limit exceeded after inference for tenant: {tenant_id}, "
                            f"tokens used: {tokens_used}"
                        )
                        # Note: We already processed the request, so we can't reject it now
                        # Future requests will be blocked if bucket is empty

                # Reconstruct response with the same body
                from starlette.responses import JSONResponse

                return JSONResponse(
                    content=response_data,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                )
            except Exception as e:
                logger.error(f"Error processing token usage: {e}")
                # Return original response on error
                return response

        return response
