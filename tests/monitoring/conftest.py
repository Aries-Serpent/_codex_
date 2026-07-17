"""
Conftest Module

This module provides functionality for conftest.

Usage:
    from monitoring.conftest import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""


# Skip modules if not available (but don't fail test collection)
try:
    import omegaconf  # noqa: F401
except ImportError:
    pass

try:
    import hydra  # noqa: F401
except ImportError:
    pass
