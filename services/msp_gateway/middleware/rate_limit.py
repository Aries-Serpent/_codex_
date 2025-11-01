"""
Rate limiting middleware
Per-tenant token bucket rate limiting (in-memory)
"""

import time
import logging
import json
from typing import Dict, Optional
from dataclasses import dataclass

from fastapi import Request, HTTPException, status
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
    
    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens
        
        Returns:
            True if tokens consumed, False if insufficient tokens
        """
        # Refill tokens based on elapsed time
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.refill_rate
        )
        self.last_refill = now
        
        # Try to consume
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False


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
        
        return bucket.consume(tokens)


# Global rate limiter
rate_limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce per-tenant rate limits"""
    
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
        # This prevents requests from being processed if no tokens are available
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
            
            # Refill tokens based on elapsed time (same logic as consume)
            now = time.time()
            elapsed = now - token_bucket.last_refill
            available_tokens = min(
                token_bucket.capacity,
                token_bucket.tokens + elapsed * token_bucket.refill_rate
            )
            
            # If no tokens available, reject the request
            if available_tokens < 1:
                logger.warning(f"Token quota exhausted for tenant: {tenant_id}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Token quota exceeded. Please try again later.",
                    headers={"Retry-After": "60"},
                )
        
        # Process request
        response = await call_next(request)
        
        # Check if this is an inference endpoint and extract token usage
        if request.url.path == "/v1/infer" and isinstance(response, Response):
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
                    # Consume tokens from the bucket
                    if not rate_limiter.check_token_limit(tenant_id, tokens_used, quota):
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
