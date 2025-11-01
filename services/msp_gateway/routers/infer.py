"""
Inference Router
Handles model inference requests with optional RAG
"""

import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, Request, HTTPException, status

from ..schemas.requests import InferRequest
from ..schemas.responses import InferResponse, AuditRef, EvidenceTag
from ..providers.model_adapter import create_model_adapter
from ..providers.retrieval_adapter import RetrievalAdapter
from ..config import settings
from ..security import validate_prompt, redact_content, offline_guard

from codex.rag.prompt import build_prompt
from codex.rag.postprocess import postprocess_output

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["inference"])

# Global adapters
model_adapter = create_model_adapter(
    backend=settings.model_backend,
    model_path=settings.model_path,
    device=settings.model_device,
)

retrieval_adapter = RetrievalAdapter(
    index_base_dir=settings.faiss_index_dir,
    embedding_model=settings.embedding_model,
    cache_dir=settings.embedding_cache_dir,
)


@router.post("/infer", response_model=InferResponse)
async def infer(request: Request, infer_request: InferRequest):
    """Generate inference response, optionally using RAG
    
    Args:
        request: FastAPI request object (contains tenant from middleware)
        infer_request: Inference request
    
    Returns:
        InferResponse with generated text
    """
    # Enforce offline mode
    if settings.offline:
        try:
            offline_guard.block_external_call("model_inference")
        except RuntimeError:
            # Continue with local inference
            pass
    
    # Get tenant from request state (may be None if API key not required)
    tenant = getattr(request.state, "tenant", None)
    
    # Determine tenant_id: use from tenant context or from request
    if tenant:
        tenant_id = tenant["tenant_id"]
        # Verify tenant_id matches if tenant context exists
        if infer_request.tenant_id != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant ID mismatch"
            )
    else:
        # No tenant context (API key not required), use tenant_id from request
        tenant_id = infer_request.tenant_id
    
    request_id = str(uuid.uuid4())
    
    logger.info(f"Inference request {request_id} from tenant {tenant_id}")
    
    # Validate prompt
    is_valid, error_msg = validate_prompt(infer_request.prompt, tenant_id)
    if not is_valid:
        logger.warning(f"Invalid prompt for request {request_id}: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid prompt: {error_msg}"
        )
    
    # Redact sensitive content from prompt
    redacted_prompt, redactions = redact_content(infer_request.prompt, tenant_id)
    if redactions:
        logger.info(f"Applied {len(redactions)} redactions to prompt")
    
    try:
        # Check if RAG is enabled for this tenant
        use_rag = infer_request.options.get("use_rag", True) if infer_request.options else True
        
        retrieved_docs = []
        if use_rag and settings.kb_query_enabled:
            # Retrieve relevant documents
            try:
                top_k = infer_request.options.get("rag_top_k", 3) if infer_request.options else 3
                results = retrieval_adapter.query(
                    tenant_id=tenant_id,
                    query=redacted_prompt,
                    top_k=top_k,
                )
                
                retrieved_docs = [
                    {
                        "content": r["content"],
                        "score": r["score"],
                        "metadata": {
                            "source_id": r["document_id"],
                            **r.get("metadata", {})
                        }
                    }
                    for r in results
                ]
                
                logger.info(f"Retrieved {len(retrieved_docs)} documents for RAG")
            except Exception as e:
                logger.warning(f"Error retrieving documents for RAG: {e}")
                # Continue without RAG
        
        # Build prompt
        system_prompt = infer_request.options.get("system_prompt") if infer_request.options else None
        full_prompt = build_prompt(
            query=redacted_prompt,
            retrieved_docs=retrieved_docs if use_rag else None,
            system_prompt=system_prompt,
            use_rag=use_rag and len(retrieved_docs) > 0,
        )
        
        # Generate response
        generation_result = model_adapter.generate(
            prompt=full_prompt,
            max_tokens=infer_request.max_tokens or 512,
            temperature=infer_request.temperature or 0.7,
            top_p=infer_request.top_p or 0.9,
        )
        
        generated_text = generation_result["text"]
        tokens_used = generation_result["tokens_used"]
        # Make tokens available to downstream middleware for quota enforcement
        try:
            request.state.tokens_used = int(tokens_used)
        except (TypeError, ValueError):
            # If tokens_used isn't numeric, fall back to 0 to avoid quota drift
            request.state.tokens_used = 0
        model_name = generation_result["model"]
        
        # Post-process output
        processed_text, evidence = postprocess_output(
            output=generated_text,
            retrieved_docs=retrieved_docs if use_rag else None,
            include_citations=True,
        )
        
        # Redact output if needed
        final_text, output_redactions = redact_content(processed_text, tenant_id)
        if output_redactions:
            logger.info(f"Applied {len(output_redactions)} redactions to output")
        
        # Create audit reference
        audit = AuditRef(
            request_id=request_id,
            timestamp=datetime.utcnow(),
            tenant_id=tenant_id,
            endpoint="/v1/infer",
        )
        
        # Convert evidence to EvidenceTag
        evidence_tags = [
            EvidenceTag(
                source_id=ev["source_id"],
                chunk_id=ev.get("chunk_id"),
                score=ev["score"],
                metadata=ev.get("metadata", {}),
            )
            for ev in evidence
        ]
        
        response = InferResponse(
            request_id=request_id,
            tenant_id=tenant_id,
            generated_text=final_text,
            tokens_used=tokens_used,
            model=model_name,
            audit=audit,
            evidence=evidence_tags,
            metadata={
                "rag_enabled": use_rag and len(retrieved_docs) > 0,
                "retrieved_docs_count": len(retrieved_docs),
                "redactions_applied": len(redactions) + len(output_redactions),
            }
        )
        
        logger.info(f"Inference {request_id} completed, tokens: {tokens_used}")
        return response
    
    except Exception as e:
        logger.error(f"Error processing inference {request_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating inference: {str(e)}"
        )
