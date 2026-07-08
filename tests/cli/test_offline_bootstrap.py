"""
Test Offline Bootstrap

Test module for offline bootstrap.
"""

from __future__ import annotations

from pathlib import Path


def test_track_bootstrap(tmp_path: Path) -> None:
    root = tmp_path / "runs"

    from codex_ml.cli import offline_bootstrap

    rc = offline_bootstrap.main(
        [
            "bootstrap",
            "--root",
            str(root),
            "--backend",
            "both",
            "--mode",
            "offline",
            "--write-env",
            str(tmp_path / "env"),
        ]
    )

    assert rc == 0, "rc is not valid"
    env_path = tmp_path / "env"
    assert env_path.exists(), "Condition must be true"
    content = env_path.read_text(encoding="utf-8")
    assert "MLFLOW_TRACKING_URI=file:" in content, "Content must not be empty"
    assert "WANDB_MODE=offline" in content, "Content must not be empty"
