"""
Admin Router
Admin operations for tenant management and system configuration
"""

import logging
from typing import List

from fastapi import APIRouter, HTTPException, status

from ..schemas.requests import TenantCreateRequest, TenantUpdateRequest
from ..schemas.responses import TenantResponse
from ..middleware.tenant_context import tenant_registry
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/tenants", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(tenant_request: TenantCreateRequest):
    """Create a new tenant
    
    Args:
        tenant_request: Tenant creation request
    
    Returns:
        TenantResponse with created tenant information
    """
    if not settings.admin_api_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin API is disabled"
        )
    
    logger.info(f"Creating tenant: {tenant_request.tenant_id}")
    
    try:
        tenant_data = tenant_registry.create_tenant(
            tenant_id=tenant_request.tenant_id,
            name=tenant_request.name,
            api_key=tenant_request.api_key,
            quota=tenant_request.quota,
            policies=tenant_request.policies,
            metadata=tenant_request.metadata,
        )
        
        response = TenantResponse(
            tenant_id=tenant_data["tenant_id"],
            name=tenant_data["name"],
            quota=tenant_data["quota"],
            policies=tenant_data["policies"],
            active=tenant_data["active"],
            created_at=tenant_data["created_at"],
            updated_at=tenant_data["updated_at"],
            metadata=tenant_data["metadata"],
        )
        
        logger.info(f"Tenant created successfully: {tenant_request.tenant_id}")
        return response
    
    except ValueError as e:
        logger.error(f"Error creating tenant: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error creating tenant: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/tenants/{tenant_id}", response_model=TenantResponse)
async def get_tenant(tenant_id: str):
    """Get tenant information
    
    Args:
        tenant_id: Tenant identifier
    
    Returns:
        TenantResponse with tenant information
    """
    if not settings.admin_api_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin API is disabled"
        )
    
    tenant_data = tenant_registry.get_tenant(tenant_id)
    if not tenant_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant not found: {tenant_id}"
        )
    
    return TenantResponse(
        tenant_id=tenant_data["tenant_id"],
        name=tenant_data["name"],
        quota=tenant_data["quota"],
        policies=tenant_data["policies"],
        active=tenant_data["active"],
        created_at=tenant_data["created_at"],
        updated_at=tenant_data["updated_at"],
        metadata=tenant_data["metadata"],
    )


@router.get("/tenants", response_model=List[TenantResponse])
async def list_tenants():
    """List all tenants
    
    Returns:
        List of TenantResponse objects
    """
    if not settings.admin_api_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin API is disabled"
        )
    
    tenants = tenant_registry.list_tenants()
    
    return [
        TenantResponse(
            tenant_id=t["tenant_id"],
            name=t["name"],
            quota=t["quota"],
            policies=t["policies"],
            active=t["active"],
            created_at=t["created_at"],
            updated_at=t["updated_at"],
            metadata=t["metadata"],
        )
        for t in tenants
    ]


@router.patch("/tenants/{tenant_id}", response_model=TenantResponse)
async def update_tenant(tenant_id: str, update_request: TenantUpdateRequest):
    """Update tenant information
    
    Args:
        tenant_id: Tenant identifier
        update_request: Tenant update request
    
    Returns:
        TenantResponse with updated tenant information
    """
    if not settings.admin_api_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin API is disabled"
        )
    
    # Get existing tenant
    tenant_data = tenant_registry.get_tenant(tenant_id)
    if not tenant_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant not found: {tenant_id}"
        )
    
    # Update tenant data (simple in-memory update for now)
    # In production, this would update the database
    if update_request.name is not None:
        tenant_data["name"] = update_request.name
    if update_request.quota is not None:
        tenant_data["quota"] = update_request.quota
    if update_request.policies is not None:
        tenant_data["policies"] = update_request.policies
    if update_request.metadata is not None:
        tenant_data["metadata"] = update_request.metadata
    if update_request.active is not None:
        tenant_data["active"] = update_request.active
    
    from datetime import datetime
    tenant_data["updated_at"] = datetime.utcnow().isoformat()
    
    logger.info(f"Tenant updated: {tenant_id}")
    
    return TenantResponse(
        tenant_id=tenant_data["tenant_id"],
        name=tenant_data["name"],
        quota=tenant_data["quota"],
        policies=tenant_data["policies"],
        active=tenant_data["active"],
        created_at=tenant_data["created_at"],
        updated_at=tenant_data["updated_at"],
        metadata=tenant_data["metadata"],
    )


@router.delete("/tenants/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(tenant_id: str):
    """Delete (deactivate) a tenant
    
    Args:
        tenant_id: Tenant identifier
    """
    if not settings.admin_api_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin API is disabled"
        )
    
    tenant_data = tenant_registry.get_tenant(tenant_id)
    if not tenant_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant not found: {tenant_id}"
        )
    
    # Deactivate tenant (soft delete)
    tenant_data["active"] = False
    
    logger.info(f"Tenant deactivated: {tenant_id}")
    return None
