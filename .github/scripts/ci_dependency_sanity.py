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
    "typer",
    "hydra.core.config_store",
    "transformers",
]


def _import(name: str) -> object | None:
    try:
        mod = importlib.import_module(name)
        # Print module path for diagnostics
        if hasattr(mod, "__file__") and mod.__file__:
            print(f"[sanity] ✓ {name}: {mod.__file__}")
        else:
            print(f"[sanity] ✓ {name}: (built-in)")
        return mod
    except Exception as e:
        print(f"[sanity] ✗ FAILED import '{name}': {e}", file=sys.stderr)
        return None


def main():
    print("[sanity] Checking critical imports...")

    # Import all critical modules
    modules = {}
    failures = []
    for name in CRITICAL:
        mod = _import(name)
        if mod is None:
            failures.append(name)
        else:
            modules[name] = mod

    # Specific API checks
    if "typer" in modules:
        typer_mod = modules["typer"]
        if not hasattr(typer_mod, "Typer"):
            print("[sanity] ✗ ERROR: typer.Typer not found (API mismatch)", file=sys.stderr)
            sys.exit(2)
        else:
            print("[sanity] ✓ typer.Typer: present")

    if "hydra.core.config_store" in modules:
        print("[sanity] ✓ hydra.core.ConfigStore: importable")

    if failures:
        print(f"[sanity] ✗ Critical imports missing: {failures}", file=sys.stderr)
        sys.exit(2)

    print("[sanity] ✓ All critical imports OK.")
    sys.exit(0)


if __name__ == "__main__":
    main()
