"""Tests for deterministic seeding and environment snapshot reproducibility."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).parent.parent.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"


class TestEnvironmentSnapshot:
    """Tests for enhanced environment snapshot script."""

    def test_snapshot_script_runs(self, tmp_path):
        """Test that environment snapshot script runs successfully."""
        out_file = tmp_path / "test_snapshot.json"

        result = subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "environment_snapshot.py"), "--out", str(out_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Script failed: {result.stderr}"
        assert out_file.exists(), "Snapshot file not created"

        # Verify JSON is valid
        snapshot = json.loads(out_file.read_text())
        assert isinstance(snapshot, dict)

    def test_snapshot_contains_python_version(self, tmp_path):
        """Test that snapshot includes Python version."""
        out_file = tmp_path / "test_snapshot.json"

        subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "environment_snapshot.py"), "--out", str(out_file)],
            check=True,
            capture_output=True,
        )

        snapshot = json.loads(out_file.read_text())
        assert "python" in snapshot, "Condition must be true"
        assert snapshot["python"], "Condition must be true"

    def test_snapshot_with_seed(self, tmp_path):
        """Test that snapshot captures seed value."""
        out_file = tmp_path / "test_snapshot.json"
        test_seed = 42

        subprocess.run(
            [
                sys.executable,
                str(_SCRIPTS_DIR / "environment_snapshot.py"),
                "--out",
                str(out_file),
                "--seed",
                str(test_seed),
            ],
            check=True,
            capture_output=True,
        )

        snapshot = json.loads(out_file.read_text())
        assert "seed" in snapshot, "Condition must be true"
        assert snapshot["seed"] == test_seed, "Condition must be true"

    def test_snapshot_git_info(self, tmp_path):
        """Test that snapshot includes git information if in a git repo."""
        out_file = tmp_path / "test_snapshot.json"

        subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "environment_snapshot.py"), "--out", str(out_file)],
            check=True,
            capture_output=True,
        )

        snapshot = json.loads(out_file.read_text())

        # Git info should be present if we're in a git repo
        # (which we are in CI and local dev)
        if "git" in snapshot:
            git_info = snapshot["git"]
            assert isinstance(git_info, dict)
            # Should have at least commit info
            assert "commit" in git_info or "commit_short" in git_info, "Condition must be true"

    def test_snapshot_reproducible_fields(self, tmp_path):
        """Test that snapshot contains expected reproducibility fields."""
        out_file = tmp_path / "test_snapshot.json"

        subprocess.run(
            [
                sys.executable,
                str(_SCRIPTS_DIR / "environment_snapshot.py"),
                "--out",
                str(out_file),
                "--seed",
                "123",
            ],
            check=True,
            capture_output=True,
        )

        snapshot = json.loads(out_file.read_text())

        # Check for reproducibility-critical fields
        expected_fields = ["python", "platform", "seed"]
        for field in expected_fields:
            assert field in snapshot, f"Missing field: {field}"


class TestDeterministicSeeding:
    """Tests for deterministic seeding behavior."""

    def test_fixed_seed_produces_same_snapshot_structure(self, tmp_path):
        """Test that fixed seed produces consistent snapshot structure."""
        seed = 42

        # Run twice with same seed
        out1 = tmp_path / "snapshot1.json"
        out2 = tmp_path / "snapshot2.json"

        for out_file in [out1, out2]:
            subprocess.run(
                [
                    sys.executable,
                    str(_SCRIPTS_DIR / "environment_snapshot.py"),
                    "--out",
                    str(out_file),
                    "--seed",
                    str(seed),
                ],
                check=True,
                capture_output=True,
            )

        snapshot1 = json.loads(out1.read_text())
        snapshot2 = json.loads(out2.read_text())

        # Seed should be consistent
        assert snapshot1.get("seed") == snapshot2.get("seed") == seed, "Condition must be true"

        # Python version should be same
        assert snapshot1.get("python") == snapshot2.get("python"), "Condition must be true"

        # Platform should be same
        assert snapshot1.get("platform") == snapshot2.get("platform"), "Condition must be true"

    def test_different_seeds_captured_correctly(self, tmp_path):
        """Test that different seeds are captured correctly."""
        seeds = [42, 123, 999]

        for seed in seeds:
            out_file = tmp_path / f"snapshot_{seed}.json"

            subprocess.run(
                [
                    sys.executable,
                    str(_SCRIPTS_DIR / "environment_snapshot.py"),
                    "--out",
                    str(out_file),
                    "--seed",
                    str(seed),
                ],
                check=True,
                capture_output=True,
            )

            snapshot = json.loads(out_file.read_text())
            assert snapshot.get("seed") == seed, "Condition must be true"


class TestReproducibilityRegression:
    """Regression tests for reproducibility guarantees."""

    def test_env_snapshot_includes_git_commit(self, tmp_path):
        """Regression test: env snapshot must include git commit."""
        out_file = tmp_path / "snapshot.json"

        subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "environment_snapshot.py"), "--out", str(out_file)],
            check=True,
            capture_output=True,
        )

        snapshot = json.loads(out_file.read_text())

        # Must have git info if in a git repo
        # In CI/dev, we're always in a git repo
        if (Path(__file__).parent.parent.parent / ".git").exists():
            assert "git" in snapshot, "Git info missing from snapshot"
            assert snapshot["git"].get("commit"), "Git commit missing"

    def test_seed_recording_deterministic(self, tmp_path):
        """Test that seed recording is deterministic across runs."""
        seed = 777
        snapshots = []

        # Run 3 times with same seed
        for i in range(3):
            out_file = tmp_path / f"snapshot_{i}.json"

            subprocess.run(
                [
                    sys.executable,
                    str(_SCRIPTS_DIR / "environment_snapshot.py"),
                    "--out",
                    str(out_file),
                    "--seed",
                    str(seed),
                ],
                check=True,
                capture_output=True,
            )

            snapshots.append(json.loads(out_file.read_text()))

        # All should have same seed
        for snapshot in snapshots:
            assert snapshot.get("seed") == seed, "Condition must be true"

        # Python versions should match (deterministic environment)
        python_versions = [s.get("python") for s in snapshots]
        assert len(set(python_versions)) == 1, "Python version not deterministic"
