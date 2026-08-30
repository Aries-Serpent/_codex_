"""
Legacy API Endpoints with RFC 8594 Deprecation Headers

This module provides deprecated API endpoints from earlier versions with proper
RFC 8594 compliant deprecation headers to guide clients to their replacements.

RFC 8594 Headers:
    - Deprecation: Marks endpoint as deprecated
    - Sunset: Date when endpoint will be removed
    - Link: Successor version endpoint
    - Warning: Human-readable reason for deprecation
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["legacy"])


# =============================================================================
# Legacy Authentication Endpoints (v1.0 format)
# =============================================================================


class LegacyLoginRequest(BaseModel):
    """Legacy login request (pre-v0.2.0 format).

    NOTE: Use POST /api/auth/login instead.
    """

    username: str = Field(..., min_length=1, max_length=150)
    password: str = Field(..., min_length=8, max_length=128)


class LegacyLoginResponse(BaseModel):
    """Legacy login response (pre-v0.2.0 format)."""

    status: str
    token: str
    user_id: str


def _add_deprecation_headers(
    response: JSONResponse,
    *,
    successor_url: str,
    sunset_date: str = "Mon, 01 Jan 2027 00:00:00 GMT",
    reason: str = "Use successor endpoint instead",
) -> JSONResponse:
    """Add RFC 8594 deprecation headers to response.

    Args:
        response: FastAPI JSONResponse to augment
        successor_url: URL of the successor endpoint (relative or absolute)
        sunset_date: RFC 5322 date when endpoint will be removed
        reason: Human-readable reason for deprecation

    Returns:
        Updated response with deprecation headers
    """
    # RFC 8594: Deprecation header (must be "true")
    response.headers["Deprecation"] = "true"

    # RFC 8594: Sunset header (RFC 5322 date format)
    response.headers["Sunset"] = sunset_date

    # RFC 8594: Link header with successor-version relation
    if not successor_url.startswith("http"):
        successor_url = f"<{successor_url}>"
    else:
        successor_url = f"<{successor_url}>"
    response.headers["Link"] = f'{successor_url}; rel="successor-version"'

    # RFC 8594: Warning header (complementary, not required but recommended)
    response.headers["Warning"] = f'299 - "{reason}"'

    # Additional headers for client guidance
    response.headers["X-API-Lifecycle"] = "deprecated"
    response.headers["X-Sunset-Date"] = sunset_date

    return response


@router.post(
    "/login",
    response_model=LegacyLoginResponse,
    summary="[DEPRECATED] Login endpoint (v1.0 format)",
    description="Legacy login endpoint. Use POST /api/auth/login instead.",
    deprecated=True,
)
async def legacy_login_v1(body: LegacyLoginRequest, request: Request) -> JSONResponse:
    """Legacy login endpoint (v1.0 format) - DEPRECATED.

    This endpoint is deprecated as of Codex v0.2.0. Clients should migrate to
    POST /api/auth/login which provides improved token management and MFA support.

    Returns:
        200 OK with legacy response format and RFC 8594 deprecation headers

    Raises:
        401: If credentials are invalid
        429: If rate limit exceeded
    """
    # For compatibility, we reject the request but include deprecation headers
    response_data = {
        "status": "deprecated",
        "message": "This endpoint is deprecated. Use POST /api/auth/login instead.",
        "token": "",
        "user_id": "",
    }

    response = JSONResponse(status_code=410, content=response_data)
    return _add_deprecation_headers(
        response,
        successor_url="/api/auth/login",
        reason="Use /api/auth/login for modern token management",
    )


# =============================================================================
# Legacy Training Endpoints (v0.1.0 format)
# =============================================================================


class LegacyTrainRequest(BaseModel):
    """Legacy training request format (pre-v0.2.0)."""

    data_path: str = Field(..., description="Path to training data")
    model_name: str = Field(..., description="Model identifier")
    epochs: int = Field(default=10, ge=1, le=1000)


class LegacyTrainResponse(BaseModel):
    """Legacy training response format."""

    training_id: str
    status: str
    estimated_time: int


@router.post(
    "/train",
    response_model=LegacyTrainResponse,
    summary="[DEPRECATED] Training endpoint (v0.1.0 format)",
    description="Legacy training endpoint. Use POST /api/v2/training instead.",
    deprecated=True,
)
async def legacy_train_v1(body: LegacyTrainRequest, request: Request) -> JSONResponse:
    """Legacy training endpoint (v0.1.0 format) - DEPRECATED.

    This endpoint is deprecated as of Codex v0.2.0. The new training API
    (POST /api/v2/training) provides enhanced monitoring, progress tracking,
    and multi-model support.

    Returns:
        410 Gone with RFC 8594 deprecation headers
    """
    response_data = {
        "training_id": "",
        "status": "deprecated",
        "estimated_time": 0,
    }

    response = JSONResponse(status_code=410, content=response_data)
    return _add_deprecation_headers(
        response,
        successor_url="/api/v2/training",
        reason="Use /api/v2/training for enhanced training monitoring",
    )


# =============================================================================
# Legacy Prediction Endpoints (direct model format)
# =============================================================================


class LegacyPredictRequest(BaseModel):
    """Legacy prediction request (pre-v0.2.0)."""

    text: str = Field(..., description="Input text for prediction")
    model_id: Optional[str] = Field(None, description="Optional model ID")


class LegacyPredictResponse(BaseModel):
    """Legacy prediction response."""

    prediction: str
    confidence: float


@router.post(
    "/predict",
    response_model=LegacyPredictResponse,
    summary="[DEPRECATED] Prediction endpoint (legacy format)",
    description="Legacy prediction endpoint. Use POST /predict instead.",
    deprecated=True,
)
async def legacy_predict_v1(body: LegacyPredictRequest, request: Request) -> JSONResponse:
    """Legacy prediction endpoint (v0.1.0 format) - DEPRECATED.

    This endpoint is deprecated as of Codex v0.2.0. Use the modern
    POST /predict endpoint which provides better security, moderation,
    and denylist enforcement.

    Returns:
        410 Gone with RFC 8594 deprecation headers
    """
    response_data = {
        "prediction": "",
        "confidence": 0.0,
    }

    response = JSONResponse(status_code=410, content=response_data)
    return _add_deprecation_headers(
        response,
        successor_url="/predict",
        reason="Use /predict for enhanced security and moderation",
    )


# =============================================================================
# Deprecation Helper Endpoints
# =============================================================================


class DeprecationInfo(BaseModel):
    """Information about deprecated endpoints."""

    endpoint: str
    deprecated_date: str
    sunset_date: str
    successor_url: str
    reason: str
    migration_notes: str


@router.get(
    "/deprecation-info",
    response_model=dict[str, list[DeprecationInfo]],
    summary="Get deprecation information",
    description="Retrieve information about all deprecated endpoints and their successors.",
)
async def get_deprecation_info() -> dict[str, list[DeprecationInfo]]:
    """Get information about deprecated endpoints.

    Returns:
        Dictionary containing deprecation information for all legacy endpoints
    """
    return {
        "deprecated_endpoints": [
            DeprecationInfo(
                endpoint="POST /api/v1/login",
                deprecated_date="2024-06-01",
                sunset_date="2027-01-01",
                successor_url="/api/auth/login",
                reason="Modern auth with MFA support",
                migration_notes="Response format has changed. Use new endpoint.",
            ),
            DeprecationInfo(
                endpoint="POST /api/v1/train",
                deprecated_date="2024-06-01",
                sunset_date="2027-01-01",
                successor_url="/api/v2/training",
                reason="Enhanced monitoring and multi-model support",
                migration_notes="New endpoint provides better progress tracking.",
            ),
            DeprecationInfo(
                endpoint="POST /api/v1/predict",
                deprecated_date="2024-06-01",
                sunset_date="2027-01-01",
                successor_url="/predict",
                reason="Improved security, moderation, and denylist",
                migration_notes="Modern endpoint with content policy enforcement.",
            ),
        ]
    }
