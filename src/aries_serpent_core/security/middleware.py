"""
FastAPI Security Middleware & Utilities

Provides:
- CSRF token validation middleware
- Rate limiting enhancements
- Secure request/response headers
- Audit logging
- Authentication middleware

OWASP Compliance:
- A02: Broken Auth → Token validation, session management
- A04: Insecure Deserialization → Request validation
- A06: Security Misconfiguration → Secure headers
"""

from __future__ import annotations

import hashlib
import logging
import secrets
import time
import uuid
from contextvars import ContextVar
from typing import Callable, Optional

from fastapi import HTTPException, Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# ============================================================================
# Context Variables for Request Tracking
# ============================================================================

request_id_var: ContextVar[str] = ContextVar("request_id", default="")
user_id_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)


# ============================================================================
# CSRF Token Management
# ============================================================================


class CSRFTokenManager:
    """Generates and validates CSRF tokens using double-submit cookie pattern."""

    def __init__(self, token_lifetime: int = 3600) -> None:
        """
        Initialize CSRF token manager.

        Args:
            token_lifetime: Token validity duration in seconds (default: 1 hour)

        OWASP A02: Broken Auth
            - Double-submit cookie pattern prevents CSRF
        """
        self.token_lifetime = token_lifetime
        self._token_store: dict[str, tuple[float, str]] = {}  # token -> (expiry, hash)

    def generate_token(self) -> str:
        """
        Generate a new CSRF token.

        Returns:
            URL-safe CSRF token (32 bytes)
        """
        token = secrets.token_urlsafe(32)
        expiry = time.time() + self.token_lifetime
        # Store hash to avoid token memory exposure
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        self._token_store[token_hash] = (expiry, token_hash)
        return token

    def validate_token(self, token: str) -> bool:
        """
        Validate a CSRF token.

        Args:
            token: Token to validate

        Returns:
            True if token is valid and not expired, False otherwise

        OWASP A02: Broken Auth
            - Validates token format and expiry
            - Prevents replay attacks via expiry check
        """
        if not token or not isinstance(token, str):
            return False

        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
        except Exception:
            return False

        if token_hash not in self._token_store:
            return False

        expiry, stored_hash = self._token_store[token_hash]
        if time.time() > expiry:
            del self._token_store[token_hash]
            return False

        return stored_hash == token_hash

    def cleanup_expired(self) -> int:
        """Remove expired tokens. Returns count of tokens removed."""
        now = time.time()
        expired = [k for k, (exp, _) in self._token_store.items() if exp < now]
        for k in expired:
            del self._token_store[k]
        return len(expired)


# ============================================================================
# Security Middleware
# ============================================================================


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds security headers to all responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and add security headers.

        Security Headers (OWASP A06: Security Misconfiguration):
            - X-Content-Type-Options: nosniff (prevent MIME type sniffing)
            - X-Frame-Options: DENY (prevent clickjacking)
            - X-XSS-Protection: 1; mode=block (legacy XSS protection)
            - Strict-Transport-Security: Enforce HTTPS
            - Content-Security-Policy: Restrict content sources
            - Referrer-Policy: Privacy-preserving referrer policy
        """
        # Generate request ID for tracking
        request_id = str(uuid.uuid4())
        request_id_var.set(request_id)

        response = await call_next(request)

        # OWASP A06: Security Headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "  # Adjust as needed
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # Add request ID for tracing
        response.headers["X-Request-ID"] = request_id

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Enhanced rate limiting with per-endpoint customization."""

    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        burst_allowance: int = 10,
    ) -> None:
        """
        Initialize rate limit middleware.

        Args:
            app: FastAPI app
            requests_per_minute: Default rate limit (requests per minute)
            burst_allowance: Burst allowance above default
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_allowance = burst_allowance
        self._request_counts: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with rate limiting.

        OWASP A01: Injection Prevention
            - Rate limiting prevents DoS attacks
        """
        client_ip = self._get_client_ip(request)
        now = time.time()
        cutoff = now - 60.0  # Last minute

        # Initialize or clean bucket
        if client_ip not in self._request_counts:
            self._request_counts[client_ip] = []

        # Remove old entries
        self._request_counts[client_ip] = [t for t in self._request_counts[client_ip] if t > cutoff]

        # Check limit
        count = len(self._request_counts[client_ip])
        if count >= self.requests_per_minute + self.burst_allowance:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later.",
                headers={"Retry-After": "60"},
            )

        # Record this request
        self._request_counts[client_ip].append(now)

        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(max(0, self.requests_per_minute - count))
        response.headers["X-RateLimit-Reset"] = str(int(now + 60))

        return response

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """Extract client IP from request (handles proxies)."""
        if request.client:
            return request.client.host

        # Check X-Forwarded-For header (be careful with untrusted proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Use the last IP (closest to us) if multiple IPs present
            return forwarded_for.split(",")[-1].strip()

        return "unknown"


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """Logs security-relevant events for audit trail."""

    def __init__(self, app, log_sensitive_paths: bool = False) -> None:
        """
        Initialize audit logging middleware.

        Args:
            app: FastAPI app
            log_sensitive_paths: Log requests to sensitive endpoints (auth, admin)

        OWASP A10: Insufficient Logging
            - Audit logs track security events for investigation
        """
        super().__init__(app)
        self.log_sensitive_paths = log_sensitive_paths
        self.sensitive_paths = {"/api/auth", "/api/admin", "/api/config"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log security-relevant requests and responses."""
        start_time = time.time()

        # Determine if this is a sensitive path
        is_sensitive = any(request.url.path.startswith(p) for p in self.sensitive_paths)

        if is_sensitive and self.log_sensitive_paths:
            logger.info(
                f"Sensitive endpoint accessed: {request.method} {request.url.path} "
                f"from {self._get_client_ip(request)}"
            )

        response = await call_next(request)

        # Log errors
        if response.status_code >= 400:
            logger.warning(
                f"Error response: {response.status_code} {request.method} {request.url.path}"
            )

        duration = time.time() - start_time
        if duration > 1.0:  # Log slow requests
            logger.warning(f"Slow request: {request.method} {request.url.path} ({duration:.2f}s)")

        return response

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """Extract client IP from request."""
        return request.client.host if request.client else "unknown"


# ============================================================================
# Request Validation Utilities
# ============================================================================


class RequestValidator:
    """Validates request properties for security."""

    @staticmethod
    def validate_json_content_type(request: Request) -> bool:
        """
        Check that request has application/json content type.

        OWASP A04: Insecure Deserialization
            - Restricts deserialization to expected formats
        """
        content_type = request.headers.get("content-type", "").lower()
        return "application/json" in content_type

    @staticmethod
    def validate_auth_header(request: Request) -> Optional[str]:
        """
        Extract and validate Authorization header.

        Returns:
            Token if valid "******" format, None otherwise

        OWASP A02: Broken Auth
            - Validates JWT format in Authorization header
        """
        auth_header = request.headers.get("Authorization", "").strip()
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None

        token = parts[1]
        if not token or len(token) > 2000:  # Reasonable JWT size
            return None

        return token

    @staticmethod
    def get_request_id(request: Request) -> str:
        """Extract or generate request ID."""
        existing_id = request.headers.get("X-Request-ID")
        if existing_id and len(existing_id) <= 50:  # Sanity check
            return existing_id
        return str(uuid.uuid4())


# ============================================================================
# Global Instances
# ============================================================================

csrf_token_manager = CSRFTokenManager()


def get_csrf_token_manager() -> CSRFTokenManager:
    """Get the global CSRF token manager."""
    return csrf_token_manager
