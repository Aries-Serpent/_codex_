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
logger.info("Host: %s", settings.host)
logger.info("Port: %s", settings.port)
logger.info("Offline Mode: %s", settings.offline)
logger.info("Model Backend: %s", settings.model_backend)
logger.info("Vector Backend: %s", settings.vector_backend)
logger.info("Rate Limiting: %s", settings.rate_limit_enabled)
logger.info("Admin API: %s", settings.admin_api_enabled)
logger.info("KB Query: %s", settings.kb_query_enabled)
logger.info("=" * 60)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )
