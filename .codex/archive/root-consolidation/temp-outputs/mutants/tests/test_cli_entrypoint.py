"""
Test Cli Entrypoint

Test module for cli entrypoint.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src import cli


@pytest.mark.usefixtures("tmp_path")
def test_cli_runs_with_simple_config(tmp_path: Path) -> None:
    torch = pytest.importorskip("torch")
    if not hasattr(torch, "nn") or not hasattr(torch.nn, "Linear"):
        pytest.skip("torch.nn.Linear is unavailable in this environment")

    config_dir = Path(__file__).resolve().parents[1] / "configs" / "simple"
    metrics_path = tmp_path / "cli_metrics.ndjson"
    overrides = [
        f"trainer.metrics_ndjson_path={metrics_path}",
        f"logging.fallback_metrics_path={tmp_path / 'fallback.ndjson'}",
        "data.params.num_samples=8",
        "data.params.batch_size=4",
    ]

    exit_code = cli.main(["--config-path", str(config_dir), "--config-name", "train", *overrides])
    assert exit_code == 0, "exit_code is not valid"
    assert metrics_path.exists(), "Condition must be true"
    payload = metrics_path.read_text(encoding="utf-8")
    assert '"epoch": 1' in payload, "Condition must be true"
