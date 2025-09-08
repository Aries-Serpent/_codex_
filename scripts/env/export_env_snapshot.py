#!/usr/bin/env python3
"""Write environment metadata and variables to JSON."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from codex_ml.utils import environment_summary


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("env_snapshot.json")
    info = environment_summary()
    info["env"] = dict(os.environ)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(info, indent=2))
    print(f"Environment snapshot written to {out}")


if __name__ == "__main__":
    main()
