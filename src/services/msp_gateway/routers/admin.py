"""
Admin Router
Admin operations for tenant management and system configuration
"""

import logging

from fastapi import APIRouter, HTTPException, Response, status

from src.utils.log_sanitizer import sanitize_log_input

from ..config import settings
from ..middleware.tenant_context import tenant_registry
from ..schemas.requests import TenantCreateRequest, TenantUpdateRequest
from ..schemas.responses import TenantResponse

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
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin API is disabled")

    logger.info("Creating tenant")

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

        logger.info("Tenant created successfully")
        return response

    except ValueError as e:
        logger.error("Error creating tenant: %s", sanitize_log_input(str(e)))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(
            "Unexpected error creating tenant: %s",
            sanitize_log_input(str(e)),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
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
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin API is disabled")

    tenant_data = tenant_registry.get_tenant(tenant_id)
    if not tenant_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Tenant not found: {tenant_id}"
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


@router.get("/tenants", response_model=list[TenantResponse])
async def list_tenants():
    """List all tenants

    Returns:
        List of TenantResponse objects
    """
    if not settings.admin_api_enabled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin API is disabled")

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
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin API is disabled")

    try:
        updated_tenant = tenant_registry.update_tenant(
            tenant_id=tenant_id,
            name=update_request.name,
            quota=update_request.quota,
            policies=update_request.policies,
            metadata=update_request.metadata,
            active=update_request.active,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    if not updated_tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Tenant not found: {tenant_id}"
        )

    logger.info("Tenant updated")

    return TenantResponse(
        tenant_id=updated_tenant["tenant_id"],
        name=updated_tenant["name"],
        quota=updated_tenant["quota"],
        policies=updated_tenant["policies"],
        active=updated_tenant["active"],
        created_at=updated_tenant["created_at"],
        updated_at=updated_tenant["updated_at"],
        metadata=updated_tenant["metadata"],
    )


@router.delete("/tenants/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(tenant_id: str):
    """Delete (deactivate) a tenant

    Args:
        tenant_id: Tenant identifier
    """
    if not settings.admin_api_enabled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin API is disabled")

    # Delete (deactivate) tenant using registry method (persists to database and revokes API key)
    try:
        tenant_registry.delete_tenant(tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    logger.info("Tenant deactivated")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
