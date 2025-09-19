"""FastAPI application powering the Internal Tools API."""

from __future__ import annotations

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

app = FastAPI(
    title="Internal Tools API (ITA)",
    description=(
        "Bridge endpoints used by both ChatGPT-Codex and GitHub Copilot. The API enforces "
        "API keys, request identifiers, and confirmation gates for state-changing actions."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    try:
        request.state.context = _authenticate_request(
            x_request_id=request.headers.get("X-Request-Id"),
            x_api_key=request.headers.get("X-API-Key"),
        )
    except HTTPException as exc:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    response = await call_next(request)
    response.headers["X-Request-Id"] = request.state.context.request_id
    return response


@app.get("/healthz", response_model=HealthResponse, tags=["system"])
async def healthz(context: RequestContext = Depends(get_request_context)) -> HealthResponse:
    _ = context  # context is validated by middleware, nothing else to do
    return HealthResponse()


@app.post("/kb/search", response_model=KnowledgeSearchResponse, tags=["knowledge"])
async def kb_search(
    payload: KnowledgeSearchRequest,
    context: RequestContext = Depends(get_request_context),
) -> KnowledgeSearchResponse:
    _ = context
    results = search_knowledge(payload)
    return KnowledgeSearchResponse(results=results)


@app.post("/repo/hygiene", response_model=RepoHygieneResponse, tags=["repo"])
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


@app.post("/tests/run", response_model=TestsRunResponse, tags=["tests"])
async def tests_run(
    payload: TestsRunRequest,
    context: RequestContext = Depends(get_request_context),
) -> TestsRunResponse:
    _ = context
    return simulate_test_execution(payload)


@app.post("/git/create-pr", response_model=GitCreatePullRequestResponse, tags=["git"])
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
