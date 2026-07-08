"""
Common utilities shared across domain packages.
"""

from .error_handling import logger as error_logger
from .error_handling import safe_call, safe_execute

__all__ = ["error_logger", "safe_call", "safe_execute"]
