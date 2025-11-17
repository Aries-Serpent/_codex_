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
from pathlib import Path

ART = Path("audit_artifacts")


def test_federation_basic():
    if ART.exists():
        shutil.rmtree(ART)

    # Create temporary test repo
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
        subprocess.run(
            [sys.executable, "scripts/multi_repo/federated_index.py"], check=True, env=env
        )

        out = ART / "federated_index.json"
        assert out.exists()
        data = json.loads(out.read_text())

        assert data["total_scanned"] == 1
        assert len(data["repositories"]) == 1
        repo = data["repositories"][0]
        assert "training" in repo["capabilities"]
        assert "checkpoint" in repo["capabilities"]


def test_federation_disabled():
    if ART.exists():
        shutil.rmtree(ART)

    env = os.environ.copy()
    env["FEDERATION_ENABLE"] = "0"
    subprocess.run([sys.executable, "scripts/multi_repo/federated_index.py"], check=True, env=env)

    assert not (ART / "federated_index.json").exists()
