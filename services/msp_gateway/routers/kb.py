"""
Knowledge Base Query Router
Handles retrieval queries against tenant knowledge bases
"""

import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, Request, HTTPException, status

from ..schemas.requests import KBQueryRequest
from ..schemas.responses import KBQueryResponse, KBSearchResult, AuditRef
from ..providers.retrieval_adapter import RetrievalAdapter
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["knowledge-base"])

# Global retrieval adapter
retrieval_adapter = RetrievalAdapter(
    index_base_dir=settings.faiss_index_dir,
    embedding_model=settings.embedding_model,
    cache_dir=settings.embedding_cache_dir,
)


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
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Knowledge base queries are disabled"
        )
    
    # Get tenant from request state (may be None if API key not required)
    tenant = getattr(request.state, "tenant", None)
    
    # Determine tenant_id: use from tenant context or from request
    if tenant:
        tenant_id = tenant["tenant_id"]
        # Verify tenant_id matches if tenant context exists
        if kb_request.tenant_id != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant ID mismatch"
            )
    else:
        # No tenant context (API key not required), use tenant_id from request
        tenant_id = kb_request.tenant_id
    
    request_id = str(uuid.uuid4())
    
    logger.info(f"KB query request {request_id} from tenant {tenant_id}")
    
    try:
        # Query the knowledge base
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
    
    except Exception as e:
        logger.error(f"Error processing KB query {request_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error querying knowledge base: {str(e)}"
        )
