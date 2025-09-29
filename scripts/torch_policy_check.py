#!/usr/bin/env python3
"""Torch CPU policy checker.

OK when:
- torch imports and reports a real version (not "0.0.0-offline"),
- CUDA is absent (CPU-only posture),
- and either the version has "+cpu" OR the environment enforces the PyTorch CPU index.
"""

from __future__ import annotations

import json
import os
import re
import sys
from typing import Any, Dict

CPU_SUFFIX_RE = re.compile(r"\+cpu\b")


def _cpu_index_enabled() -> bool:
    idx = os.getenv("PIP_INDEX_URL", "") or ""
    ex = os.getenv("PIP_EXTRA_INDEX_URL", "") or ""
    return ("/whl/cpu" in idx) or ("/whl/cpu" in ex) or (os.getenv("CODEX_FORCE_CPU") == "1")


def _template() -> Dict[str, Any]:
    return {
        "torch_import_ok": False,
        "torch_version": "",
        "cuda_build": None,
        "cuda_available": False,
        "policy_ok": False,
        "policy_reason": "",
    }


def main() -> int:
    info = _template()
    try:
        import torch  # type: ignore

        info["torch_import_ok"] = True
        info["torch_version"] = getattr(torch, "__version__", "")
        tv = getattr(torch, "version", None)
        info["cuda_build"] = getattr(tv, "cuda", None)
        cuda = getattr(torch, "cuda", None)
        info["cuda_available"] = bool(
            cuda and getattr(cuda, "is_available", None) and torch.cuda.is_available()
        )
    except Exception as exc:  # pragma: no cover - defensive
        info["policy_reason"] = f"torch import failed: {exc}"
        print(json.dumps(info, sort_keys=True))
        print("[torch][FAIL] import failed", file=sys.stderr)
        return 1

    ver = info["torch_version"]
    if not ver or ver == "0.0.0-offline":
        info["policy_reason"] = "torch version sentinel/offline detected"
        print(json.dumps(info, sort_keys=True))
        print("[torch][FAIL] offline stub", file=sys.stderr)
        return 1

    if info["cuda_available"] or (isinstance(info["cuda_build"], str) and info["cuda_build"]):
        info["policy_reason"] = "CUDA detected in CPU-only posture"
        print(json.dumps(info, sort_keys=True))
        print("[torch][FAIL] CUDA present", file=sys.stderr)
        return 1

    cpu_ok = CPU_SUFFIX_RE.search(ver) or _cpu_index_enabled()
    if cpu_ok:
        info["policy_ok"] = True
        info["policy_reason"] = "ok: +cpu or CPU index mode"
        print(json.dumps(info, sort_keys=True))
        print("[torch][OK] CPU wheel accepted", file=sys.stderr)
        return 0

    info["policy_reason"] = "no +cpu tag and CPU index not detected"
    print(json.dumps(info, sort_keys=True))
    print("[torch][WARN] missing +cpu tag", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
