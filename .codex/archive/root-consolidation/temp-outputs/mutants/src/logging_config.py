"""
Logging Config Module

This module provides functionality for logging config.

Usage:
    from logging_config import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

import logging
import logging.handlers


def configure_logging(
    level: int = logging.INFO,
    to_file: str | None = None,
    max_bytes: int = 5_000_000,
    backup_count: int = 3,
):
    logger = logging.getLogger()
    logger.setLevel(level)
    if to_file:
        fh = logging.handlers.RotatingFileHandler(
            to_file, maxBytes=max_bytes, backupCount=backup_count
        )
        logger.addHandler(fh)
    ch = logging.StreamHandler()
    logger.addHandler(ch)
    return logger
