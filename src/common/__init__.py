"""
Common utilities shared across domain packages.
"""

from .error_handling import safe_execute, logger as error_logger

__all__ = ["safe_execute", "error_logger"]
