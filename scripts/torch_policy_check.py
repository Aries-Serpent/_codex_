#!/usr/bin/env python3
"""Torch CPU policy checker.

Success when:
- torch imports and reports a real version (not "0.0.0-offline"),
- CUDA is absent (CPU-only posture),
- and either the version has "+cpu" OR the environment enforces the PyTorch CPU index.

Heuristic relaxation:
- Accept plain "MAJ.MIN.PATCH" (no +cpu suffix) when:
  * PIP_INDEX_URL or PIP_EXTRA_INDEX_URL contains "/whl/cpu", or
  * CODEX_FORCE_CPU=1

Outputs compact JSON to stdout and a human hint to stderr.
Exit codes:
- 0 OK (may WARN if +cpu missing and CPU index not detected)
- 1 FAIL (import error, offline sentinel version, or CUDA detected)

Refs:
- PyTorch CPU index & install: https://pytorch.org/get-started/locally/  # CPU platform + pip
- CPU wheel index URL: https://download.pytorch.org/whl/cpu
"""
from __future__ import annotations

import json
import os
import re
import sys
from typing import Any, Dict


CPU_SUFFIX_RE = re.compile(r"\+cpu\b")


def _cpu_index_enabled() -> bool:
    index_url = os.getenv("PIP_INDEX_URL", "")
    extra_index_url = os.getenv("PIP_EXTRA_INDEX_URL", "")
    if "/whl/cpu" in index_url or "/whl/cpu" in extra_index_url:
        return True
    return os.getenv("CODEX_FORCE_CPU", "0") == "1"


def _policy_template() -> Dict[str, Any]:
    return {
        "torch_import_ok": False,
        "torch_version": "",
        "cuda_build": None,
        "cuda_available": False,
        "policy_ok": False,
        "policy_reason": "",
    }


def main() -> int:
    info = _policy_template()

    try:
        import torch  # type: ignore

        info["torch_import_ok"] = True
        info["torch_version"] = getattr(torch, "__version__", "")
        torch_version_module = getattr(torch, "version", None)
        info["cuda_build"] = getattr(torch_version_module, "cuda", None)
        cuda_attr = getattr(torch, "cuda", None)
        info["cuda_available"] = bool(
            cuda_attr and getattr(cuda_attr, "is_available", None) and torch.cuda.is_available()
        )
    except Exception as exc:  # pragma: no cover - defensive path for runtime errors
        info["policy_reason"] = f"torch import failed: {exc}"
        print(json.dumps(info, sort_keys=True), flush=True)
        print("[torch][FAIL] import failed", file=sys.stderr, flush=True)
        return 1

    version = info["torch_version"]
    if not version or version == "0.0.0-offline":
        info["policy_reason"] = "torch version sentinel/offline detected"
        print(json.dumps(info, sort_keys=True), flush=True)
        print("[torch][FAIL] version 0.0.0-offline (not usable)", file=sys.stderr, flush=True)
        return 1

    cuda_build = info["cuda_build"]
    if info["cuda_available"] or (isinstance(cuda_build, str) and cuda_build):
        info["policy_reason"] = "CUDA detected in CPU-only posture"
        print(json.dumps(info, sort_keys=True), flush=True)
        print("[torch][FAIL] CUDA present under CPU policy", file=sys.stderr, flush=True)
        return 1

    has_cpu_suffix = bool(CPU_SUFFIX_RE.search(version))
    cpu_index_mode = _cpu_index_enabled()
    if has_cpu_suffix or cpu_index_mode:
        info["policy_ok"] = True
        info["policy_reason"] = "ok: +cpu suffix or CPU index mode"
        print(json.dumps(info, sort_keys=True), flush=True)
        if not has_cpu_suffix and cpu_index_mode:
            print(
                "[torch][OK] CPU wheel accepted via CPU index (no +cpu suffix required)",
                file=sys.stderr,
                flush=True,
            )
        else:
            print("[torch][OK] CPU wheel accepted", file=sys.stderr, flush=True)
        return 0

    info["policy_reason"] = "no +cpu suffix and CPU index not detected"
    print(json.dumps(info, sort_keys=True), flush=True)
    print(
        "[torch][WARN] wheel missing +cpu tag and CPU index not detected",
        file=sys.stderr,
        flush=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
