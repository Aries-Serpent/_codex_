import logging
from logging.handlers import RotatingFileHandler


def configure_logging(
    level: int = logging.INFO,
    to_file: str | None = None,
    max_bytes: int = 5_000_000,
    backup_count: int = 3,
):
    logger = logging.getLogger()
    logger.setLevel(level)
    if to_file:
        fh = RotatingFileHandler(to_file, maxBytes=max_bytes, backupCount=backup_count)
        logger.addHandler(fh)
    ch = logging.StreamHandler()
    logger.addHandler(ch)
    return logger
