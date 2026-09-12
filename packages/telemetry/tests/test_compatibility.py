from __future__ import annotations

import codex_ml_telemetry


def test_legacy_telemetry_surface_is_available() -> None:
    expected = {
        "EXAMPLES_PROCESSED",
        "REQUEST_LATENCY",
        "TRAIN_STEP_DURATION",
        "start_metrics_server",
        "track_time",
    }

    assert expected.issubset(set(codex_ml_telemetry.__all__))
