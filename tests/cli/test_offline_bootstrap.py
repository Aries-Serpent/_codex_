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

    assert rc == 0
    env_path = tmp_path / "env"
    assert env_path.exists()
    content = env_path.read_text(encoding="utf-8")
    assert "MLFLOW_TRACKING_URI=file:" in content
    assert "WANDB_MODE=offline" in content
