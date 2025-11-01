"""
Main entry point for MSP Gateway
Run with: uvicorn services.msp_gateway.main:app --host 127.0.0.1 --port 8080
"""

import logging

from .app import app
from .config import settings

logger = logging.getLogger(__name__)

# Log startup configuration
logger.info("=" * 60)
logger.info("MSP Gateway Starting")
logger.info("=" * 60)
logger.info(f"Host: {settings.host}")
logger.info(f"Port: {settings.port}")
logger.info(f"Offline Mode: {settings.offline}")
logger.info(f"Model Backend: {settings.model_backend}")
logger.info(f"Vector Backend: {settings.vector_backend}")
logger.info(f"Rate Limiting: {settings.rate_limit_enabled}")
logger.info(f"Admin API: {settings.admin_api_enabled}")
logger.info(f"KB Query: {settings.kb_query_enabled}")
logger.info("=" * 60)

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )
