"""Security-focused tests for status update generator output handling."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module():
    repo_root = Path(__file__).resolve().parents[2]
    module_path = repo_root / "tools" / "status" / "generate_status_update.py"
    spec = importlib.util.spec_from_file_location("status_gen", module_path)
    assert spec and spec.loader, "spec is not valid"
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except (ValueError, TypeError) as _err:
        sys.modules.pop(spec.name, None)
        raise
    return module


def test_sanitize_for_logging_redacts_secret_patterns() -> None:
    module = _load_module()
    try:
        sample = "token=abc123 SECRET: ghp_abcdefghijklmnopqrstuvwxyz"
        sanitized = module.sanitize_for_logging(sample)
        assert "abc123" not in sanitized, "Condition must be true"
        assert "ghp_" not in sanitized, "Condition must be true"
        assert "[redacted]" in sanitized, "Condition must be true"
    finally:
        sys.modules.pop("status_gen", None)
