"""File permission constants for secure logging.

Security Policy
---------------
All log files use owner-only permissions (0o600) by default to prevent:
- Unauthorized access to ML experiment data
- Exposure of embedded API keys/tokens
- Cross-user information disclosure

Override via CODEX_LOG_FILE_MODE for shared monitoring deployments.

Security Comment (Referenced in Implementation Files)
-----------------------------------------------------
Use owner-only permissions (0o600) by default to prevent unauthorized access
to ML experiment data, embedded API keys/tokens, and cross-user information
disclosure. Override via CODEX_LOG_FILE_MODE environment variable for shared
monitoring deployments.
"""

import logging
import os

logger = logging.getLogger(__name__)

DEFAULT_LOG_FILE_MODE = 0o600  # Owner read/write only


def get_log_file_mode() -> int:
    """Retrieve log file permission mode from environment or defaults.

    Returns
    -------
    int
        The file permission mode as an octal integer. Defaults to 0o600
        (owner read/write only) if CODEX_LOG_FILE_MODE is not set or invalid.

    Examples
    --------
    >>> import os
    >>> from codex_ml.logging.permissions import get_log_file_mode
    >>> get_log_file_mode()  # Default
    384
    >>> os.environ["CODEX_LOG_FILE_MODE"] = "0o640"
    >>> get_log_file_mode()  # Environment override
    416

    Notes
    -----
    The environment variable CODEX_LOG_FILE_MODE should be specified as an
    octal string (e.g., "0o640"). Invalid values will fall back to the default.
    """
    env_mode = os.getenv("CODEX_LOG_FILE_MODE")
    if env_mode:
        try:
            return int(env_mode, 8)  # Octal conversion
        except ValueError as e:
            type(e).__name__
            logger.debug("ValueError: <ERROR_TYPE>")
            logger.warning("ValueError: <ERROR_TYPE>", exc_info=True)  # Fall through to default
    return DEFAULT_LOG_FILE_MODE
