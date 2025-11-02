"""Export a JSON snapshot of the current Python environment."""
from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
from pathlib import Path

CAPTURE_ENV = ("CUDA_VISIBLE_DEVICES", "CUBLAS_WORKSPACE_CONFIG")


def _run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True)


def main(out_path: str = "artifacts/env_snapshot.json") -> None:
    info = {
        "python": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "env": {k: os.environ.get(k) for k in CAPTURE_ENV if k in os.environ},
        "pip_list": json.loads(_run([sys.executable, "-m", "pip", "list", "--format=json"])),
        "pip_freeze": _run([sys.executable, "-m", "pip", "freeze"]),
    }
    try:
        info["pip_inspect"] = json.loads(_run([sys.executable, "-m", "pip", "inspect"]))
    except Exception:
        info["pip_inspect"] = None
    target = Path(out_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(info, indent=2), encoding="utf-8")


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
