"""Routers package for MSP Gateway"""

from .admin import router as admin_router
from .infer import router as infer_router
from .kb import router as kb_router

__all__ = [
    "kb_router",
    "infer_router",
    "admin_router",
]
