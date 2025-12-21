# MCP Rate Limiting

## Overview

The MCP (Model Context Protocol) rate limiting capability provides comprehensive request throttling for MCP services, including token bucket algorithms, sliding window counters, quota management, and abuse prevention mechanisms.

**Keywords**: rate-limiting, throttling, rate-limiter, token-bucket, sliding-window, quota, requests-per-second, 429, too-many-requests, retry-after, mcp, safeguards, protection, abuse-prevention, api-limits, capacity

## Purpose

Manages MCP rate limiting through:
- **Token Bucket**: Classic rate limiting algorithm
- **Sliding Window**: Smooth rate limiting over time
- **Quota Management**: Per-user and per-tenant limits
- **Burst Handling**: Allow controlled request bursts
- **Graceful Degradation**: Handle limit exceeded scenarios

## Architecture

### Rate Limiting Layers

```
┌─────────────────────────────────────┐
│   Global Rate Limiter               │
│   (Service-wide protection)         │
└─────────────┬───────────────────────┘
              │ applies
              ▼
┌─────────────────────────────────────┐
│   Per-User Rate Limiter             │
│   (User/API key specific)           │
└─────────────┬───────────────────────┘
              │ applies
              ▼
┌─────────────────────────────────────┐
│   Per-Endpoint Rate Limiter         │
│   (Resource-specific limits)        │
└─────────────────────────────────────┘
```

### Rate Limiting Flow

```python
# Pseudocode for rate limiting flow
async def handle_request(request):
    # 1. Identify client
    client_id = get_client_id(request)
    
    # 2. Check global limits
    if not global_limiter.allow(request):
        return rate_limit_response(retry_after=60)
    
    # 3. Check per-client limits
    if not client_limiter.allow(client_id):
        return rate_limit_response(retry_after=30)
    
    # 4. Check endpoint-specific limits
    if not endpoint_limiter.allow(request.path):
        return rate_limit_response(retry_after=10)
    
    # 5. Process request
    return await process(request)
```

## Implementation

### Token Bucket Algorithm

Implement the classic token bucket rate limiter:

```python
import time
from threading import Lock
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TokenBucket:
    """
    Token bucket rate limiter implementation.
    
    Provides:
    - Configurable rate and burst capacity
    - Thread-safe operation
    - Smooth rate limiting
    
    Safeguards:
    - Bounds checking on parameters
    - Thread-safe token updates
    - Overflow protection
    """
    
    def __init__(
        self,
        rate: float,
        capacity: int,
        initial_tokens: Optional[int] = None
    ):
        """
        Initialize token bucket.
        
        Args:
            rate: Tokens added per second
            capacity: Maximum bucket capacity
            initial_tokens: Starting token count (defaults to capacity)
        """
        # Parameter validation (safeguard)
        if rate <= 0:
            raise ValueError("Rate must be positive")
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        if capacity > 1000000:  # Bounds check (safeguard)
            raise ValueError("Capacity exceeds maximum")
        
        self._rate = rate
        self._capacity = capacity
        self._tokens = initial_tokens if initial_tokens is not None else capacity
        self._last_update = time.monotonic()
        self._lock = Lock()
    
    def consume(self, tokens: int = 1) -> bool:
        """
        Attempt to consume tokens from the bucket.
        
        Thread-safe token consumption with automatic refill.
        
        Safeguards:
        - Token count validation
        - Overflow protection
        - Thread-safe operations
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            True if tokens consumed, False if insufficient
        """
        if tokens <= 0:
            return True
        if tokens > self._capacity:  # Bounds check (safeguard)
            return False
        
        with self._lock:
            self._refill()
            
            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            return False
    
    def _refill(self):
        """Refill tokens based on elapsed time."""
        now = time.monotonic()
        elapsed = now - self._last_update
        
        # Calculate tokens to add
        tokens_to_add = elapsed * self._rate
        
        # Update tokens (with overflow protection - safeguard)
        self._tokens = min(self._capacity, self._tokens + tokens_to_add)
        self._last_update = now
    
    @property
    def available_tokens(self) -> float:
        """Get current available tokens."""
        with self._lock:
            self._refill()
            return self._tokens


class RateLimiter:
    """
    Rate limiter using token bucket algorithm.
    
    Provides per-client rate limiting with configurable policies.
    
    Safeguards:
    - Client ID validation
    - Memory bounds on buckets
    - Cleanup of old buckets
    """
    
    MAX_BUCKETS = 100000  # Safeguard: limit memory usage
    
    def __init__(
        self,
        requests_per_second: float = 10.0,
        burst_size: int = 20
    ):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_second: Rate limit
            burst_size: Maximum burst capacity
        """
        self._rate = requests_per_second
        self._burst = burst_size
        self._buckets: dict[str, TokenBucket] = {}
        self._lock = Lock()
    
    def allow(self, client_id: str) -> bool:
        """
        Check if request is allowed for client.
        
        Args:
            client_id: Client identifier
            
        Returns:
            True if request allowed, False if rate limited
        """
        # Input validation (safeguard)
        if not client_id or not isinstance(client_id, str):
            return False
        
        # Sanitize client ID (safeguard)
        client_id = client_id[:100]
        
        bucket = self._get_or_create_bucket(client_id)
        return bucket.consume(1)
    
    def _get_or_create_bucket(self, client_id: str) -> TokenBucket:
        """Get or create bucket for client."""
        with self._lock:
            if client_id not in self._buckets:
                # Enforce memory limit (safeguard)
                if len(self._buckets) >= self.MAX_BUCKETS:
                    self._cleanup_old_buckets()
                
                self._buckets[client_id] = TokenBucket(
                    rate=self._rate,
                    capacity=self._burst
                )
            
            return self._buckets[client_id]
    
    def _cleanup_old_buckets(self):
        """Remove old buckets to free memory."""
        # Remove 10% of oldest buckets
        to_remove = len(self._buckets) // 10
        for key in list(self._buckets.keys())[:to_remove]:
            del self._buckets[key]
    
    def get_retry_after(self, client_id: str) -> int:
        """
        Get recommended retry-after time in seconds.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Seconds to wait before retrying
        """
        bucket = self._get_or_create_bucket(client_id)
        tokens_needed = 1 - bucket.available_tokens
        if tokens_needed <= 0:
            return 0
        return int(tokens_needed / self._rate) + 1
```

### Sliding Window Counter

Implement sliding window rate limiting:

```python
from collections import defaultdict
import time

class SlidingWindowCounter:
    """
    Sliding window counter rate limiter.
    
    More accurate than fixed window, prevents burst at window boundaries.
    
    Safeguards:
    - Memory-efficient counter storage
    - Automatic cleanup of old entries
    - Thread-safe operations
    """
    
    def __init__(
        self,
        limit: int,
        window_seconds: int = 60
    ):
        """
        Initialize sliding window counter.
        
        Args:
            limit: Maximum requests per window
            window_seconds: Window duration in seconds
        """
        self._limit = limit
        self._window = window_seconds
        self._counters: dict[str, dict[int, int]] = defaultdict(dict)
        self._lock = Lock()
    
    def allow(self, client_id: str) -> bool:
        """
        Check if request is allowed using sliding window.
        
        Args:
            client_id: Client identifier
            
        Returns:
            True if allowed, False if rate limited
        """
        now = int(time.time())
        current_window = now // self._window
        previous_window = current_window - 1
        
        with self._lock:
            counters = self._counters[client_id]
            
            # Get counts for current and previous windows
            current_count = counters.get(current_window, 0)
            previous_count = counters.get(previous_window, 0)
            
            # Calculate weighted count
            window_position = (now % self._window) / self._window
            weighted_previous = previous_count * (1 - window_position)
            total_count = weighted_previous + current_count
            
            if total_count >= self._limit:
                return False
            
            # Increment counter
            counters[current_window] = current_count + 1
            
            # Cleanup old windows (safeguard - memory management)
            self._cleanup(client_id, current_window)
            
            return True
    
    def _cleanup(self, client_id: str, current_window: int):
        """Remove old window counters."""
        counters = self._counters[client_id]
        old_windows = [w for w in counters.keys() if w < current_window - 1]
        for w in old_windows:
            del counters[w]
```

### Rate Limit Middleware

Implement rate limiting middleware:

```python
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from typing import Callable

class RateLimitMiddleware:
    """
    FastAPI middleware for rate limiting.
    
    Applies rate limiting to all requests with proper headers.
    
    Safeguards:
    - Graceful handling of limit exceeded
    - Proper HTTP headers
    - Client identification
    """
    
    def __init__(
        self,
        app,
        limiter: RateLimiter = None,
        requests_per_minute: int = 60
    ):
        self._app = app
        self._limiter = limiter or RateLimiter(
            requests_per_second=requests_per_minute / 60,
            burst_size=requests_per_minute // 2
        )
    
    async def __call__(self, request: Request, call_next: Callable):
        """Process request with rate limiting."""
        # Get client identifier
        client_id = self._get_client_id(request)
        
        # Check rate limit
        if not self._limiter.allow(client_id):
            retry_after = self._limiter.get_retry_after(client_id)
            
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "message": "Rate limit exceeded",
                    "retry_after": retry_after
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self._limiter._burst),
                    "X-RateLimit-Remaining": "0",
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        bucket = self._limiter._get_or_create_bucket(client_id)
        response.headers["X-RateLimit-Limit"] = str(self._limiter._burst)
        response.headers["X-RateLimit-Remaining"] = str(int(bucket.available_tokens))
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """
        Extract client identifier from request.
        
        Priority:
        1. API key
        2. User ID from auth
        3. IP address
        """
        # Check API key
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"key:{api_key[:32]}"
        
        # Check authenticated user
        if hasattr(request.state, "user"):
            return f"user:{request.state.user.id}"
        
        # Fall back to IP
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"
```

## Configuration

### Environment Variables

Configure rate limiting via environment:

```bash
# Global limits
export MCP_RATE_LIMIT_REQUESTS_PER_SECOND="10"
export MCP_RATE_LIMIT_BURST_SIZE="20"

# Per-endpoint limits
export MCP_RATE_LIMIT_AUTH_REQUESTS_PER_MINUTE="10"
export MCP_RATE_LIMIT_API_REQUESTS_PER_MINUTE="100"

# Throttle settings
export MCP_RATE_LIMIT_THROTTLE_ENABLED="true"
export MCP_RATE_LIMIT_THROTTLE_DELAY_MS="100"
```

### Configuration File

Use YAML for rate limiting configuration:

```yaml
# rate_limit_config.yaml
rate_limiting:
  enabled: true
  algorithm: "token_bucket"  # or "sliding_window"
  
  global:
    requests_per_second: 1000
    burst_size: 2000
  
  per_client:
    requests_per_minute: 60
    burst_size: 20
  
  per_endpoint:
    "/api/auth/login":
      requests_per_minute: 10
      burst_size: 5
    "/api/predict":
      requests_per_minute: 30
      burst_size: 10
  
  tiers:
    free:
      requests_per_day: 1000
      requests_per_minute: 10
    pro:
      requests_per_day: 100000
      requests_per_minute: 100
    enterprise:
      requests_per_day: -1  # unlimited
      requests_per_minute: 1000
  
  response:
    include_headers: true
    retry_after_precision: "seconds"
```

## Usage Examples

### Example 1: Basic Rate Limiting

```python
from fastapi import FastAPI, Depends

app = FastAPI()

# Create rate limiter
rate_limiter = RateLimiter(
    requests_per_second=10,
    burst_size=20
)

def rate_limit(request: Request):
    """Rate limit dependency."""
    client_id = request.client.host
    if not rate_limiter.allow(client_id):
        raise HTTPException(429, "Rate limit exceeded")

@app.get("/api/data", dependencies=[Depends(rate_limit)])
async def get_data():
    return {"data": "value"}
```

### Example 2: Tiered Rate Limits

```python
class TieredRateLimiter:
    """Rate limiter with different tiers."""
    
    TIERS = {
        "free": {"rate": 1, "burst": 10},
        "pro": {"rate": 10, "burst": 50},
        "enterprise": {"rate": 100, "burst": 200}
    }
    
    def __init__(self):
        self._limiters = {
            tier: RateLimiter(**config)
            for tier, config in self.TIERS.items()
        }
    
    def allow(self, client_id: str, tier: str = "free") -> bool:
        """Check if request allowed for tier."""
        limiter = self._limiters.get(tier, self._limiters["free"])
        return limiter.allow(client_id)

tiered_limiter = TieredRateLimiter()

@app.get("/api/premium")
async def premium_endpoint(request: Request, user: User = Depends(get_user)):
    if not tiered_limiter.allow(user.id, user.tier):
        raise HTTPException(429, "Upgrade your plan for higher limits")
    return {"premium": "data"}
```

### Example 3: Distributed Rate Limiting

```python
import redis

class RedisRateLimiter:
    """
    Distributed rate limiter using Redis.
    
    Enables rate limiting across multiple service instances.
    """
    
    def __init__(
        self,
        redis_client: redis.Redis,
        limit: int,
        window_seconds: int = 60
    ):
        self._redis = redis_client
        self._limit = limit
        self._window = window_seconds
    
    def allow(self, client_id: str) -> bool:
        """Check rate limit using Redis."""
        key = f"rate_limit:{client_id}"
        
        pipe = self._redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, self._window)
        results = pipe.execute()
        
        current_count = results[0]
        return current_count <= self._limit
```

## Best Practices

### 1. Use Appropriate Algorithms

```python
# Token bucket for steady rate with burst allowance
limiter = TokenBucket(rate=10, capacity=20)

# Sliding window for strict per-window limits
limiter = SlidingWindowCounter(limit=100, window_seconds=60)
```

### 2. Implement Rate Limit Headers

```python
def add_rate_limit_headers(response, limiter, client_id):
    """Add standard rate limit headers."""
    response.headers["X-RateLimit-Limit"] = str(limiter.limit)
    response.headers["X-RateLimit-Remaining"] = str(limiter.remaining(client_id))
    response.headers["X-RateLimit-Reset"] = str(limiter.reset_time(client_id))
```

### 3. Graceful Degradation

```python
async def handle_rate_limited(request, retry_after):
    """Handle rate limited request gracefully."""
    # Log for monitoring
    logger.warning(f"Rate limit exceeded for {request.client.host}")
    
    # Return informative response
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please retry later.",
            "retry_after": retry_after,
            "documentation": "https://docs.example.com/rate-limits"
        }
    )
```

## Troubleshooting

### High Rate Limit Errors

**Problem**: Many 429 responses

**Solution**:
1. Review client usage patterns
2. Adjust limits for legitimate traffic
3. Implement request queuing
4. Consider tiered limits

### Memory Issues

**Problem**: Rate limiter memory growing

**Solution**:
1. Enable bucket cleanup
2. Use Redis for distributed limiting
3. Reduce max bucket count
4. Implement LRU eviction

## Security Considerations

### DoS Protection

- Use rate limiting at load balancer level
- Implement progressive delays
- Block repeated offenders
- Monitor for abuse patterns

### Client Identification

- Use multiple identifiers (IP, API key, user)
- Handle proxy headers carefully
- Validate client identifiers
- Log rate limit events

## Related Capabilities

- **mcp-security-safeguards**: Security integration
- **mcp-authz-authn**: API key validation
- **mcp-observability**: Rate limit monitoring
- **mcp-error-handling**: 429 error handling

## References

- [Rate Limiting Algorithms](https://blog.cloudflare.com/counting-things-a-lot-of-different-things/)
- [Token Bucket Algorithm](https://en.wikipedia.org/wiki/Token_bucket)
- [HTTP 429 Too Many Requests](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429)
- [Rate Limiting Best Practices](https://cloud.google.com/architecture/rate-limiting-strategies-techniques)
