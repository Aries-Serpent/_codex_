"""FastAPI application powering the Internal Tools API."""

from __future__ import annotations

import os

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .git_ops import simulate_pull_request
from .hygiene import run_hygiene_checks
from .knowledge_base import search_knowledge
from .models import (
    GitCreatePullRequestBody,
    GitCreatePullRequestResponse,
    HealthResponse,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
    RepoHygieneRequest,
    RepoHygieneResponse,
    RequestContext,
    TestsRunRequest,
    TestsRunResponse,
)
from .security import ApiKeyStore, verify_api_key
from .tests_runner import simulate_test_execution

# Import MCP modules for integration
try:
    from mcp.errors import MCPError
    from mcp.rate_limit import MCPRateLimiter

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

app = FastAPI(
    title="Internal Tools API (ITA)",
    description=(
        "Bridge endpoints used by both ChatGPT-Codex and GitHub Copilot. The API enforces "
        "API keys, request identifiers, and confirmation gates for state-changing actions."
    ),
    version="0.1.0",
)

# Environment-aware CORS configuration
# Security: Configure CORS origins based on environment to prevent unauthorized access
cors_origins_env = os.getenv("CORS_ORIGINS", "")
if cors_origins_env:
    # Use explicit CORS_ORIGINS from environment
    cors_origins = [origin.strip() for origin in cors_origins_env.split(",")]
elif os.getenv("ENVIRONMENT", "development") == "production":
    # Production: Restrict to specific domains.
    # ⚠️ IMPORTANT: These are placeholder domains that MUST be replaced before production deployment.
    # For production use, you MUST either:
    #   1. Set CORS_ORIGINS environment variable to your actual domains (recommended), OR
    #   2. Replace example.com below with your real frontend/API domains
    # Leaving these placeholder values will cause legitimate production requests to be rejected by CORS.
    cors_origins = [
        "https://example.com",
        "https://api.example.com"
    ]
else:
    # Development: Allow localhost only (more secure than wildcard)
    cors_origins = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,  # Keep False for security (API key auth instead)
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-Request-Id"],
)

# MCP Error Handler - Unified error responses
if MCP_AVAILABLE:

    @app.exception_handler(MCPError)
    async def mcp_error_handler(request: Request, exc: MCPError):
        """Handle MCP-specific errors with consistent JSON responses."""
        return JSONResponse(
            status_code=exc.http_status,
            content=exc.to_dict(),
            headers={"X-Request-Id": _get_request_id(request)},
        )

    # Initialize rate limiter (5 requests/sec, burst 20)
    _rate_limiter = MCPRateLimiter(rate=5.0, capacity=20)


def _get_request_id(request: Request) -> str:
    """
    Helper to safely extract the X-Request-Id value from the request context.
    If no RequestContext has been attached yet, returns "unknown".
    """
    ctx = getattr(request.state, "context", None)
    if isinstance(ctx, RequestContext) and ctx.request_id:
        return ctx.request_id
    return "unknown"


def _authenticate_request(x_request_id: str | None, x_api_key: str | None) -> RequestContext:
    if not x_request_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Request-Id header is required for traceability",
        )

    hashed = verify_api_key(x_api_key, store=ApiKeyStore())
    return RequestContext(request_id=x_request_id, api_key_hash=hashed)


async def get_request_context(request: Request) -> RequestContext:
    context = getattr(request.state, "context", None)
    if context is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Request context missing"
        )
    return context


@app.middleware("http")
async def inject_request_context(request: Request, call_next):
    headers: dict[str, str] | None = None
    try:
        request.state.context = _authenticate_request(
            x_request_id=request.headers.get("X-Request-Id"),
            x_api_key=request.headers.get("X-API-Key"),
        )

        headers = {"X-Request-Id": _get_request_id(request)}

        # MCP Rate Limiting - check if request is allowed
        if MCP_AVAILABLE:
            principal_id = request.state.context.api_key_hash  # Use full hash for identity
            endpoint = request.url.path
            if not _rate_limiter.allow(principal_id, endpoint):
                from mcp.errors import RateLimitExceeded

                raise RateLimitExceeded(f"Rate limit exceeded for {endpoint}")

    except HTTPException as exc:
        headers = headers or {"X-Request-Id": _get_request_id(request)}
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=headers,
        )
    except Exception as exc:
        headers = headers or {"X-Request-Id": _get_request_id(request)}
        # Handle MCP errors in middleware
        if MCP_AVAILABLE and isinstance(exc, MCPError):
            return JSONResponse(
                status_code=exc.http_status,
                content=exc.to_dict(),
                headers=headers,
            )
        # Security: Don't expose internal exception details to clients
        logger.error("Unhandled exception: %s", exc, exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
            headers=headers,
        )

    response = await call_next(request)
    request_id_header = headers or {"X-Request-Id": _get_request_id(request)}
    response.headers["X-Request-Id"] = request_id_header["X-Request-Id"]
    return response


@app.get("/healthz", response_model=HealthResponse, tags=["system"], operation_id="healthz")
async def healthz(context: RequestContext = Depends(get_request_context)) -> HealthResponse:
    _ = context  # context is validated by middleware, nothing else to do
    return HealthResponse()


@app.post(
    "/kb/search",
    response_model=KnowledgeSearchResponse,
    tags=["knowledge"],
    operation_id="kbSearch",
)
async def kb_search(
    payload: KnowledgeSearchRequest,
    context: RequestContext = Depends(get_request_context),
) -> KnowledgeSearchResponse:
    _ = context
    results = search_knowledge(payload)
    return KnowledgeSearchResponse(results=results)


@app.post(
    "/repo/hygiene",
    response_model=RepoHygieneResponse,
    tags=["repo"],
    operation_id="repoHygiene",
)
async def repo_hygiene(
    payload: RepoHygieneRequest,
    context: RequestContext = Depends(get_request_context),
) -> RepoHygieneResponse:
    _ = context
    try:
        issues = run_hygiene_checks(payload)
    except ValueError as exc:  # invalid checks requested
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return RepoHygieneResponse(issues=issues)


@app.post(
    "/tests/run",
    response_model=TestsRunResponse,
    tags=["tests"],
    operation_id="testsRun",
)
async def tests_run(
    payload: TestsRunRequest,
    context: RequestContext = Depends(get_request_context),
) -> TestsRunResponse:
    _ = context
    return simulate_test_execution(payload)


@app.post(
    "/git/create-pr",
    response_model=GitCreatePullRequestResponse,
    tags=["git"],
    operation_id="gitCreatePr",
)
async def git_create_pr(
    payload: GitCreatePullRequestBody,
    confirm: bool = False,
    dry_run: bool = True,
    context: RequestContext = Depends(get_request_context),
) -> GitCreatePullRequestResponse:
    _ = context
    if dry_run is False and confirm is False:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="confirm=true is required when dry_run=false",
        )
    try:
        response = simulate_pull_request(payload, dry_run=dry_run, confirm=confirm)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED, detail=str(exc)
        ) from exc
    return response


__all__ = ["app"]
