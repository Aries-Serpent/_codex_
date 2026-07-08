"""
Test Dataset Cli

Test module for dataset cli.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_dataset_cli_validate_and_metadata(tmp_path: Path):
    # Create simple jsonl
    data = tmp_path / "samples.jsonl"
    data.write_text('{"text":"a","label":0}\n{"text":"b","label":1}\n', encoding="utf-8")

    # Validate
    proc = subprocess.run(
        [sys.executable, "-m", "src.codex_ml.data.cli", "validate", str(data)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, "returncode is not valid"
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True, "Condition must be true"

    # Metadata
    proc2 = subprocess.run(
        [sys.executable, "-m", "src.codex_ml.data.cli", "metadata", str(data)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc2.returncode == 0, "returncode is not valid"
    meta = json.loads(proc2.stdout)
    assert meta["path"].endswith("samples.jsonl"), "Condition must be true"
    assert meta["kind"] in {"generic", "parquet", "arrow", "hdf5"}
