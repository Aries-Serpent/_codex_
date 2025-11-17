"""
Knowledge Base Query Router
Handles retrieval queries against tenant knowledge bases
"""

import logging
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from fastapi import APIRouter, HTTPException, Request, status

from ..config import settings
from ..schemas.requests import KBQueryRequest
from ..schemas.responses import AuditRef, KBQueryResponse, KBSearchResult

if TYPE_CHECKING:
    from ..providers.retrieval_adapter import RetrievalAdapter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["knowledge-base"])

if TYPE_CHECKING:
    from ..providers.retrieval_adapter import RetrievalAdapter

_retrieval_adapter: Optional["RetrievalAdapter"] = None
_retrieval_adapter_error: Optional[Exception] = None


def get_retrieval_adapter() -> "RetrievalAdapter":
    """Return a retrieval adapter, instantiating it lazily."""

    global _retrieval_adapter, _retrieval_adapter_error

    if _retrieval_adapter is not None:
        return _retrieval_adapter

    if _retrieval_adapter_error is not None:
        raise _retrieval_adapter_error

    from ..providers.retrieval_adapter import RetrievalAdapter

    try:
        _retrieval_adapter = RetrievalAdapter(
            index_base_dir=settings.faiss_index_dir,
            embedding_model=settings.embedding_model,
            cache_dir=settings.embedding_cache_dir,
        )
        return _retrieval_adapter
    except Exception as exc:  # pragma: no cover - optional dependency path
        _retrieval_adapter_error = exc
        logger.error(
            "Failed to initialize retrieval adapter for KB queries: %s",
            exc,
        )
        raise


@router.post("/query_kb", response_model=KBQueryResponse)
async def query_kb(request: Request, kb_request: KBQueryRequest):
    """Query knowledge base for relevant documents

    Args:
        request: FastAPI request object (contains tenant from middleware)
        kb_request: Knowledge base query request

    Returns:
        KBQueryResponse with search results
    """
    if not settings.kb_query_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Knowledge base queries are disabled"
        )

    # Get tenant from request state (may be None if API key not required)
    tenant = getattr(request.state, "tenant", None)

    # Determine tenant_id: use from tenant context or from request
    if tenant:
        tenant_id = tenant["tenant_id"]
        # Verify tenant_id matches if tenant context exists
        if kb_request.tenant_id != tenant_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant ID mismatch")
    else:
        # No tenant context (API key not required), use tenant_id from request
        tenant_id = kb_request.tenant_id

    request_id = str(uuid.uuid4())

    logger.info(f"KB query request {request_id} from tenant {tenant_id}")

    try:
        # Query the knowledge base
        retrieval_adapter = get_retrieval_adapter()
        results = retrieval_adapter.query(
            tenant_id=tenant_id,
            query=kb_request.query,
            top_k=kb_request.top_k or 5,
            filters=kb_request.filters,
        )

        # Format results
        search_results = []
        for result in results:
            search_results.append(
                KBSearchResult(
                    document_id=result["document_id"],
                    content=result["content"],
                    score=result["score"],
                    metadata=result["metadata"] if kb_request.include_metadata else {},
                )
            )

        # Create audit reference
        audit = AuditRef(
            request_id=request_id,
            timestamp=datetime.utcnow(),
            tenant_id=tenant_id,
            endpoint="/v1/query_kb",
        )

        response = KBQueryResponse(
            request_id=request_id,
            tenant_id=tenant_id,
            query=kb_request.query,
            results=search_results,
            total_results=len(search_results),
            audit=audit,
        )

        logger.info(f"KB query {request_id} returned {len(search_results)} results")
        return response

    except ImportError as exc:
        logger.error(
            "KB query %s failed due to missing retrieval dependencies: %s",
            request_id,
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Knowledge base retrieval dependencies are not installed",
        )
    except Exception as e:
        logger.error(f"Error processing KB query {request_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error querying knowledge base: {str(e)}",
        )
