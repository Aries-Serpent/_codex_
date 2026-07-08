"""
Hf Revision Module

This module provides functionality for hf revision.

Usage:
    from utils.hf_revision import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging
import os
from typing import Optional

_LOG = logging.getLogger(__name__)


def get_hf_revision(env_var: str = "HF_REVISION") -> Optional[str]:
    """Return the pinned Hugging Face revision to use for downloads."""

    rev = os.getenv(env_var) or os.getenv("HF_MODEL_REVISION") or os.getenv("CODEX_HF_REVISION")
    if not rev:
        _LOG.warning(
            "No HF revision found in environment (%s/HF_MODEL_REVISION/CODEX_HF_REVISION). "
            "Bandit B615 recommends pinning models by commit. Set HF_REVISION to a commit SHA in CI.",  # noqa: E501
            env_var,
        )
    return rev


__all__ = ["get_hf_revision"]
