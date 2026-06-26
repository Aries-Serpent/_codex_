"""
Test Training Configs Validate

Test module for training configs validate.
"""

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "configs/schemas/training.schema.yaml"
CFG_ROOT = ROOT / "configs/training"
TOOL = ROOT / "tools/validate_configs.py"

pytestmark = pytest.mark.skipif(not TOOL.exists(), reason="validation tool missing")


def test_example_configs_validate():
    if not SCHEMA.exists() or not CFG_ROOT.exists():
        pytest.skip("config schema or config root missing")
    if importlib.util.find_spec("jsonschema") is None:
        pytest.skip("jsonschema is required for config validation")
    code = subprocess.call(
        [sys.executable, str(TOOL), "--root", str(CFG_ROOT), "--schema", str(SCHEMA)]
    )
    assert code == 0, "code is not valid"
