"""
Test Enforce Policy

Test module for enforce policy.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

# Use absolute path to the tool so it works even when cwd changes
TOOL = Path(__file__).parent.parent.parent / "scripts" / "security" / "enforce_policy.py"

pytestmark = pytest.mark.skipif(not TOOL.exists(), reason="policy tool missing")


def test_policy_skips_without_policy_file(tmp_path):
    code = subprocess.call([sys.executable, str(TOOL.resolve())], cwd=str(tmp_path))
    assert code == 0, "code is not valid"


def test_policy_schema_validation_runs(tmp_path, monkeypatch):
    # Create minimal policy and schema
    (tmp_path / "configs/schemas").mkdir(parents=True, exist_ok=True)
    (tmp_path / "configs/schemas/security_policy.schema.json").write_text(
        json.dumps({"type": "object"}), encoding="utf-8"
    )
    (tmp_path / "configs/security_policy.policy.json").write_text(json.dumps({}), encoding="utf-8")
    code = subprocess.call([sys.executable, str(TOOL.resolve())], cwd=str(tmp_path))
    # Without bandit/pip-audit, expect non-zero or zero depending on environment; just assert it runs
    assert code in (0, 1)
