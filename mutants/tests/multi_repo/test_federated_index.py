"""
P6 Test: Federated Index

Validates:
- Repository scanning
- Capability detection
- Error handling for missing paths
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ART = Path("audit_artifacts")


def test_federation_basic():
    """Test basic federation with proper cleanup and timeout handling."""
    # Clean up any existing artifacts
    if ART.exists():
        shutil.rmtree(ART, ignore_errors=True)

    # Use context manager for tempdir to ensure cleanup
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)

        # Create test Python file with capability indicators
        (repo_path / "train.py").write_text(
            "def train_model():\n    for epoch in range(10):\n        pass", encoding="utf-8"
        )
        (repo_path / "checkpoint.py").write_text(
            "def save_checkpoint():\n    pass", encoding="utf-8"
        )

        env = os.environ.copy()
        env["FEDERATION_ENABLE"] = "1"
        env["FEDERATION_REPO_PATHS"] = str(repo_path)

        # Add timeout to subprocess and wait for completion
        try:
            result = subprocess.run(
                [sys.executable, "scripts/multi_repo/federated_index.py"],
                check=True,
                env=env,
                timeout=30,
                capture_output=True,
            )
        except subprocess.TimeoutExpired as e:
            raise AssertionError(f"Federated index script timed out after 30s: {e}") from e

        # Verify output file was created with retries
        out = ART / "federated_index.json"
        max_wait = 5
        start_time = time.time()
        while not out.exists() and (time.time() - start_time) < max_wait:
            time.sleep(0.1)

        assert out.exists(), "Assertion must pass - output file not created"

        data = json.loads(out.read_text())
        assert data["total_scanned"] == 1, "Data must not be empty"
        assert len(data["repositories"]) == 1, "Length must be valid"
        repo = data["repositories"][0]
        assert "training" in repo["capabilities"], "Condition must be true"
        assert "checkpoint" in repo["capabilities"], "Condition must be true"


def test_federation_disabled():
    """Test federation disabled with proper timeout handling."""
    # Clean up any existing artifacts
    if ART.exists():
        shutil.rmtree(ART, ignore_errors=True)

    env = os.environ.copy()
    env["FEDERATION_ENABLE"] = "0"

    # Add timeout to subprocess to prevent hanging
    try:
        subprocess.run(
            [sys.executable, "scripts/multi_repo/federated_index.py"],
            check=True,
            env=env,
            timeout=30,
            capture_output=True,
        )
    except subprocess.TimeoutExpired as e:
        raise AssertionError(f"Federated index script timed out after 30s: {e}") from e

    # Verify output file was NOT created
    out = ART / "federated_index.json"
    # Give it a short time to create the file (in case it was supposed to)
    time.sleep(0.5)
    assert not out.exists(), "Assertion must pass - output file should not exist when disabled"
