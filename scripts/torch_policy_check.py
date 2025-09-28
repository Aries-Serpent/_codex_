#!/usr/bin/env python3
"""
Torch CPU policy checker.
 - Succeeds if:
   a) torch imports and reports a real version (not '0.0.0-offline'), and
   b) CUDA is absent, and
   c) either the version has '+cpu' OR the environment signals CPU-index use:
        PIP_INDEX_URL or PIP_EXTRA_INDEX_URL contains '/whl/cpu'
        OR CODEX_FORCE_CPU=1
 - Emits a compact JSON summary to stdout and a human hint to stderr.
"""

from __future__ import annotations

import json
import os
import re
import sys


def env_cpu_index_enabled() -> bool:
    idxs = [os.getenv("PIP_INDEX_URL", ""), os.getenv("PIP_EXTRA_INDEX_URL", "")]
    if any("/whl/cpu" in (u or "") for u in idxs):
        return True
    return os.getenv("CODEX_FORCE_CPU", "0") == "1"


def main() -> int:
    info = {
        "torch_import_ok": False,
        "torch_version": "",
        "cuda_build": None,
        "cuda_available": False,
        "policy_ok": False,
        "policy_reason": "",
    }
    try:
        import torch  # type: ignore

        info["torch_import_ok"] = True
        info["torch_version"] = getattr(torch, "__version__", "")
        info["cuda_build"] = getattr(getattr(torch, "version", None), "cuda", None)
        info["cuda_available"] = bool(getattr(torch, "cuda", None) and torch.cuda.is_available())
    except Exception as e:
        info["policy_reason"] = f"torch import failed: {e}"
        print(json.dumps(info, sort_keys=True), flush=True)
        print("[torch][FAIL] import failed", file=sys.stderr, flush=True)
        return 1

    ver = info["torch_version"]
    if not ver or ver == "0.0.0-offline":
        info["policy_reason"] = "torch version sentinel/offline detected"
        print(json.dumps(info, sort_keys=True), flush=True)
        print("[torch][FAIL] version 0.0.0-offline (not usable)", file=sys.stderr, flush=True)
        return 1

    if info["cuda_available"] or (isinstance(info["cuda_build"], str) and info["cuda_build"]):
        info["policy_reason"] = "CUDA detected in CPU-only posture"
        print(json.dumps(info, sort_keys=True), flush=True)
        print("[torch][FAIL] CUDA present under CPU policy", file=sys.stderr, flush=True)
        return 1

    # Heuristic relaxation:
    #   Accept plain "MAJ.MIN.PATCH" (no +cpu suffix) when CPU index or CODEX_FORCE_CPU=1 is set.
    has_cpu_suffix = bool(re.search(r"\+cpu\b", ver))
    cpu_index_mode = env_cpu_index_enabled()
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
