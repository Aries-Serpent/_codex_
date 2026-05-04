"""
FastAPI RAG API Server

Provides RESTful API endpoints for RAG operations:
- Build indices
- Query indices
- List/manage indices
- Get statistics and metrics
"""

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="RAG API",
    description="Retrieval-Augmented Generation API with offline TF-IDF support",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# Base directory that all client-supplied file paths must reside under.
# Set RAG_FILES_BASE_DIR to restrict to a specific directory; defaults to CWD.
_RAG_FILES_BASE: Path = Path(os.environ.get("RAG_FILES_BASE_DIR", str(Path.cwd()))).resolve()


def _ensure_subpath(base: Path, candidate: Path) -> Path:
    """
    Resolve *candidate* against the filesystem and ensure it is located under *base*.

    Raises HTTPException(400) if the resolved path escapes the base directory.
    """
    try:
        base_resolved = base.resolve(strict=False)
        candidate_resolved = candidate.resolve(strict=False)
    except RuntimeError as err:
        # Fallback in pathological resolution cases
        raise HTTPException(status_code=400, detail="Invalid path") from err

    # Require that the candidate is the base or a descendant of it.
    if candidate_resolved == base_resolved or base_resolved in candidate_resolved.parents:
        return candidate_resolved

    raise HTTPException(status_code=400, detail="Path escapes allowed root directory")


# NOTE: _rate_limit_exceeded_handler is typed as (Request, RateLimitExceeded) -> Response  # noqa: E501
# but add_exception_handler expects (Request, Exception) -> Response.
# The wrapper below widens the signature to satisfy mypy without losing runtime behaviour.
def _rate_limit_handler(request: Request, exc: Exception) -> Response:
    return _rate_limit_exceeded_handler(request, exc)


# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)


# === Request/Response Models ===


class BuildIndexRequest(BaseModel):
    """Request to build an index."""

    files: list[str] = Field(..., description="Concrete file paths to index")
    index_name: str = Field(..., description="Name for the index")
    tenant_id: str = Field(default="default", description="Tenant ID")
    chunk_size: int = Field(default=1000, ge=100, le=10000, description="Chunk size")
    overlap: int = Field(default=128, ge=0, description="Chunk overlap")
    provider: Optional[str] = Field(
        default=None,
        description=(
            "(Deprecated — accepted for backward compatibility, ignored. "
            "Multi-provider routing not yet implemented. "
            "Will be removed in a future major release.)"
        ),
    )


class BuildIndexResponse(BaseModel):
    """Response from building an index."""

    success: bool
    index_name: str
    tenant_id: str
    chunks_count: Optional[int] = None
    index_path: Optional[str] = None
    message: str


class QueryRequest(BaseModel):
    """Request to query an index."""

    query: str = Field(..., min_length=1, description="Query text")
    index_name: str = Field(..., description="Index to query")
    tenant_id: str = Field(default="default", description="Tenant ID")
    top_k: int = Field(default=5, ge=1, le=100, description="Number of results")
    min_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Minimum similarity score")


class QueryResult(BaseModel):
    """Single query result."""

    text: str
    file: str
    score: float
    metadata: Optional[dict] = None


class QueryResponse(BaseModel):
    """Response from querying an index."""

    query: str
    results: list[QueryResult]
    count: int
    elapsed_ms: float


class IndexInfo(BaseModel):
    """Information about an index."""

    name: str
    tenant_id: str
    chunks_count: int
    embedding_dim: int
    created_at: str
    size_bytes: Optional[int] = None


class ListIndicesResponse(BaseModel):
    """Response listing indices."""

    indices: list[IndexInfo]
    count: int


class DeleteIndexRequest(BaseModel):
    """Request to delete an index."""

    index_name: str
    tenant_id: str = "default"
    force: bool = False


class DeleteIndexResponse(BaseModel):
    """Response from deleting an index."""

    success: bool
    index_name: str
    tenant_id: str
    message: str


class MergeIndicesRequest(BaseModel):
    """Request to merge indices."""

    source_indices: list[str] = Field(..., min_length=2)
    target_index: str
    tenant_id: str = "default"


class MergeIndicesResponse(BaseModel):
    """Response from merging indices."""

    success: bool
    target_index: str
    tenant_id: str
    chunks_count: Optional[int] = None
    message: str


class StatsResponse(BaseModel):
    """Index statistics response."""

    index_name: str
    tenant_id: str
    chunks_count: int
    embedding_dim: int
    created_at: str
    size_mb: float
    metadata: dict


class MetricsResponse(BaseModel):
    """Metrics response."""

    metrics: dict
    timestamp: str


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    timestamp: str
    components: dict[str, str]


# === API Endpoints ===


@app.get("/health", response_model=HealthResponse, tags=["Health"])
@limiter.limit("100/minute")
async def health_check(request: Request) -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now(tz=timezone.utc).isoformat(),
        components={
            "api": "healthy",
            "rag": "healthy",
            "embeddings": "healthy",
        },
    )


@app.post("/rag/build", response_model=BuildIndexResponse, tags=["RAG"])
@limiter.limit("10/minute")
async def build_index(request: Request, build_request: BuildIndexRequest) -> BuildIndexResponse:
    """Build a new RAG index."""
    try:
        from codex.rag import build_index_from_files

        # Validate every supplied path stays within _RAG_FILES_BASE to prevent
        # path-traversal attacks (e.g. a client passing "/etc/passwd").
        safe_files = [_ensure_subpath(_RAG_FILES_BASE, Path(f)) for f in build_request.files]

        index_path = build_index_from_files(
            files=safe_files,
            index_name=build_request.index_name,
            tenant_id=build_request.tenant_id,
            chunk_size=build_request.chunk_size,
            overlap=build_request.overlap,
        )

        # Get metadata
        metadata_file = index_path / "metadata.json"
        chunks_count = None
        if metadata_file.exists():
            import json

            with open(metadata_file) as f:
                metadata = json.load(f)
                chunks_count = metadata.get("num_chunks")

        return BuildIndexResponse(
            success=True,
            index_name=build_request.index_name,
            tenant_id=build_request.tenant_id,
            chunks_count=chunks_count,
            index_path=str(index_path),
            message=f"Index '{build_request.index_name}' built successfully",
        )

    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"Missing dependencies: {e}") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build index: {e}") from e


@app.post("/rag/query", response_model=QueryResponse, tags=["RAG"])
@limiter.limit("60/minute")
async def query_index(request: Request, query_request: QueryRequest) -> QueryResponse:
    """Query a RAG index."""
    import time

    start_time = time.time()

    try:
        from codex.rag import Retriever

        # Create retriever
        retriever = Retriever(
            index_name=query_request.index_name,
            tenant_id=query_request.tenant_id,
        )

        # Query
        results = retriever.query(
            q=query_request.query,
            top_k=query_request.top_k,
            min_score=query_request.min_score,
        )

        # Format results
        query_results = [
            QueryResult(
                text=r.get("text", ""),
                file=r.get("file", ""),
                score=r.get("score", 0.0),
                metadata=r.get("metadata"),
            )
            for r in results
        ]

        elapsed_ms = (time.time() - start_time) * 1000

        return QueryResponse(
            query=query_request.query,
            results=query_results,
            count=len(query_results),
            elapsed_ms=elapsed_ms,
        )

    except FileNotFoundError as err:
        msg = f"Index '{query_request.index_name}' not found"
        raise HTTPException(status_code=404, detail=msg) from err


@app.get("/rag/indices", response_model=ListIndicesResponse, tags=["RAG"])
@limiter.limit("30/minute")
async def list_indices(
    request: Request, tenant_id: str = "default", index_dir: Optional[str] = None
) -> ListIndicesResponse:
    """List all indices for a tenant."""
    try:
        import json
        from pathlib import Path

        # Basic tenant_id validation to avoid traversal or weird characters.
        # Allow simple identifiers composed of letters, digits, underscore and dash.
        if not tenant_id.replace("-", "").replace("_", "").isalnum():
            raise HTTPException(status_code=400, detail="Invalid tenant_id")

        # Establish a fixed root directory for all indices
        base_index_root = Path.home() / ".codex" / "rag_indices"

        # If index_dir is provided, treat it only as a subdirectory name under the base root,
        # not as an arbitrary filesystem path.
        if index_dir:
            # Prevent path separators in index_dir to keep it a single path segment.
            if any(sep in index_dir for sep in ("/", "\\")):
                raise HTTPException(status_code=400, detail="Invalid index_dir")
            requested_root = base_index_root / index_dir
        else:
            requested_root = base_index_root

        safe_index_root = _ensure_subpath(base_index_root, requested_root)
        tenant_dir = _ensure_subpath(safe_index_root, safe_index_root / tenant_id)

        if not tenant_dir.exists():
            return ListIndicesResponse(indices=[], count=0)

        indices = []
        for index_path in tenant_dir.iterdir():
            if not index_path.is_dir():
                continue

            metadata_file = index_path / "metadata.json"
            if not metadata_file.exists():
                continue

            with open(metadata_file) as f:
                metadata = json.load(f)

            # Calculate size
            size_bytes = sum(f.stat().st_size for f in index_path.rglob("*") if f.is_file())

            indices.append(
                IndexInfo(
                    name=index_path.name,
                    tenant_id=tenant_id,
                    chunks_count=metadata.get("num_chunks", 0),
                    embedding_dim=metadata.get("embedding_dim", 0),
                    created_at=metadata.get("created_at", ""),
                    size_bytes=size_bytes,
                )
            )

        return ListIndicesResponse(indices=indices, count=len(indices))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list indices: {e}") from e


@app.delete("/rag/indices/{index_name}", response_model=DeleteIndexResponse, tags=["RAG"])
@limiter.limit("10/minute")
async def delete_index(
    request: Request, index_name: str, tenant_id: str = "default", force: bool = False
) -> DeleteIndexResponse:
    """Delete an index."""
    try:
        import shutil
        from pathlib import Path

        index_dir = Path.home() / ".codex" / "rag_indices"
        tenant_path = _ensure_subpath(index_dir, index_dir / tenant_id)
        index_path = _ensure_subpath(tenant_path, tenant_path / index_name)

        if not index_path.exists():
            raise HTTPException(status_code=404, detail=f"Index '{index_name}' not found")

        if not force:
            raise HTTPException(status_code=400, detail="Set force=true to confirm deletion")

        shutil.rmtree(index_path)

        return DeleteIndexResponse(
            success=True,
            index_name=index_name,
            tenant_id=tenant_id,
            message=f"Index '{index_name}' deleted successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete index: {e}") from e


@app.post("/rag/merge", response_model=MergeIndicesResponse, tags=["RAG"])
@limiter.limit("5/minute")
async def merge_indices(request: Request, merge_request: MergeIndicesRequest):
    """Merge multiple indices."""
    try:
        from codex.rag import IndexOperation, manage_tenant_indices

        result = manage_tenant_indices(
            operation=IndexOperation.MERGE,
            tenant_id=merge_request.tenant_id,
            source_names=merge_request.source_indices,
            merge_name=merge_request.target_index,
        )

        chunks_count = None
        if result.details:
            chunks_count = result.details.get("chunks_count")

        return MergeIndicesResponse(
            success=result.success,
            target_index=merge_request.target_index,
            tenant_id=merge_request.tenant_id,
            chunks_count=chunks_count,
            message=result.message,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Merge failed: {e}") from e


@app.get("/rag/stats/{index_name}", response_model=StatsResponse, tags=["RAG"])
@limiter.limit("30/minute")
async def get_stats(request: Request, index_name: str, tenant_id: str = "default"):
    """Get statistics for an index."""
    try:
        import json
        from pathlib import Path

        index_dir = Path.home() / ".codex" / "rag_indices"
        tenant_path = _ensure_subpath(index_dir, index_dir / tenant_id)
        index_path = _ensure_subpath(tenant_path, tenant_path / index_name)

        if not index_path.exists():
            raise HTTPException(status_code=404, detail=f"Index '{index_name}' not found")

        metadata_file = index_path / "metadata.json"
        if not metadata_file.exists():
            raise HTTPException(status_code=404, detail="Index metadata not found")

        with open(metadata_file) as f:
            metadata = json.load(f)

        # Calculate size
        size_bytes = sum(f.stat().st_size for f in index_path.rglob("*") if f.is_file())

        return StatsResponse(
            index_name=index_name,
            tenant_id=tenant_id,
            chunks_count=metadata.get("num_chunks", 0),
            embedding_dim=metadata.get("embedding_dim", 0),
            created_at=metadata.get("created_at", ""),
            size_mb=size_bytes / (1024 * 1024),
            metadata=metadata,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {e}") from e


@app.get("/rag/metrics", response_model=MetricsResponse, tags=["RAG"])
@limiter.limit("30/minute")
async def get_metrics(request: Request):
    """Get RAG system metrics."""
    try:
        from codex.rag import get_metrics

        metrics = get_metrics()

        return MetricsResponse(
            metrics=metrics,
            timestamp=datetime.now(tz=timezone.utc).isoformat(),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {e}") from e


# === Error Handlers ===


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Handle 404 errors."""
    return JSONResponse(status_code=404, content={"detail": str(exc.detail), "status": "not_found"})


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    """Handle 500 errors."""
    return JSONResponse(status_code=500, content={"detail": str(exc.detail), "status": "error"})


# === Startup/Shutdown ===


@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    print("🚀 RAG API Server starting...")
    print("📚 Documentation: http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("👋 RAG API Server shutting down...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)  # nosec B104
