"""
Test Schema Validate Cli

Test module for schema validate cli.
"""

import subprocess
import sys
from pathlib import Path

import pytest

SCHEMA = Path("docs/templates/status/codex_status_template.schema_v1.2.json")
DATA = Path("docs/templates/status/example_report_v1.2.json")
TOOL = Path("tools/schema_validate.py")


@pytest.mark.skipif(not TOOL.exists(), reason="schema_validate tool missing")
@pytest.mark.skipif(not SCHEMA.exists() or not DATA.exists(), reason="schema or example missing")
def test_cli_passes_on_example(tmp_path):
    proc = subprocess.run(
        [sys.executable, str(TOOL), "--data", str(DATA), "--schema", str(SCHEMA)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout
    assert "[PASS]" in proc.stdout, "Condition must be true"
