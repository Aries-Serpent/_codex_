"""
CI dependency sanity assertions.
Run early (optional) to surface broken wheels before coverage collection.
"""
from __future__ import annotations
import importlib
import sys

CRITICAL = [
    "torch",
    "torch.nn.functional",
    "transformers",
    "hydra.core",
]

def _import(name: str) -> bool:
    try:
        importlib.import_module(name)
        return True
    except Exception as e:
        print(f"[sanity] FAILED import '{name}': {e}", file=sys.stderr)
        return False

def main():
    failures = [n for n in CRITICAL if not _import(n)]
    if failures:
        print(f"[sanity] Critical imports missing: {failures}", file=sys.stderr)
        sys.exit(2)
    print("[sanity] All critical imports OK.")

if __name__ == "__main__":
    main()
