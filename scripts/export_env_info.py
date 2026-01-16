#!/usr/bin/env python3
"""
Export Env Info

Purpose:
    Export environment and version info as JSON.

Usage:
    python scripts/export_env_info.py [options]
    
    Examples:
    $ python scripts/export_env_info.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""

import json
import logging
import os
import platform
import sys
from typing import Any

logger = logging.getLogger(__name__)

info: dict[str, Any] = {
    "python": sys.version.split()[0],
    "platform": platform.platform(),
    "env": {k: v for k, v in os.environ.items() if k.startswith("CODEX_")},
}
try:
    import torch  # type: ignore

    info["torch"] = torch.__version__
    info["cuda"] = torch.version.cuda if torch.cuda.is_available() else None
except Exception:
    logger.warning("Exception occurred", exc_info=True)
    logger.warning("Exception occurred", exc_info=True)
    info["torch"] = None
    info["cuda"] = None
print(json.dumps(info, indent=2))
