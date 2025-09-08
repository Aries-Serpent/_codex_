#!/usr/bin/env python3
"""Export environment and version info as JSON."""
import json
import os
import platform
import sys
from typing import Any

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
    info["torch"] = None
    info["cuda"] = None
print(json.dumps(info, indent=2))
