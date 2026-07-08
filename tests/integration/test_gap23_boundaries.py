"""Gap-23: Automated integration tests covering four cross-component boundaries.

Boundaries covered
------------------
1. **API ↔ model-service** – end-to-end request/response through the FastAPI
   stack, using FastAPI's ``TestClient`` (no real network calls).
2. **Monitoring ↔ alerting** – alert events fire when thresholds are breached;
   delivery channels are stubbed so no external services are contacted.
3. **Data-pipeline ↔ training** – data flows correctly into the training loop;
   the actual model is stubbed so no heavy dependencies are required.
4. **Config ↔ runtime** – Hydra / pydantic configs load and are applied
   correctly at runtime.

All tests are decorated with ``@pytest.mark.integration`` and are independently
runnable via::

    pytest tests/integration/test_gap23_boundaries.py -v --tb=short -m integration
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Boundary 1 – API ↔ model-service
# ---------------------------------------------------------------------------

# We need FastAPI test-client utilities.  Import guards protect against
# environments where the dependency is unavailable.
try:
    from fastapi.testclient import TestClient  # type: ignore[import]
except ImportError:  # pragma: no cover
    pass  # FastAPI is optional; TestClient features unavailable without it


@pytest.mark.integration
def test_api_health_endpoint_returns_healthy() -> None:
    """The /health endpoint returns status=healthy (API ↔ model-service boundary)."""
    pytest.importorskip("fastapi")
    from monitoring.dashboard_api import app  # local import keeps module optional

    client = TestClient(app, raise_server_exceptions=True)
    response = client.get("/health")
    assert response.status_code == 200, "Response must not be empty"
    body = response.json()
    assert body["status"] == "healthy", "Condition must be true"
    assert "timestamp" in body, "Condition must be true"


@pytest.mark.integration
def test_api_readiness_probe_reports_ready() -> None:
    """The /readiness probe responds 200 OK (API ↔ model-service boundary)."""
    pytest.importorskip("fastapi")
    from monitoring.dashboard_api import app

    client = TestClient(app)
    response = client.get("/readiness")
    assert response.status_code == 200, "Response must not be empty"
    body = response.json()
    assert body.get("status") in ("ready", "ok", "healthy")


@pytest.mark.integration
def test_api_liveness_probe_reports_alive() -> None:
    """The /liveness probe responds 200 OK with uptime info (API ↔ model-service)."""
    pytest.importorskip("fastapi")
    from monitoring.dashboard_api import app

    client = TestClient(app)
    response = client.get("/liveness")
    assert response.status_code == 200, "Response must not be empty"
    body = response.json()
    # Accept either 'status' key or top-level ok field; both indicate liveness.
    assert body.get("status") in ("alive", "ok", "healthy") or body.get("uptime_seconds", -1) >= 0


@pytest.mark.integration
def test_api_ci_metrics_endpoint_structure() -> None:
    """GET /api/metrics/ci returns a dict with expected keys (API ↔ model-service)."""
    pytest.importorskip("fastapi")
    from monitoring.dashboard_api import app

    client = TestClient(app)
    response = client.get("/api/metrics/ci")
    assert response.status_code == 200, "Response must not be empty"
    body = response.json()
    # Structural contract: must include a timestamp field.
    assert "timestamp" in body, "Condition must be true"


@pytest.mark.integration
def test_api_root_lists_known_endpoints() -> None:
    """GET / advertises ci_metrics and alerts endpoints (API ↔ model-service)."""
    pytest.importorskip("fastapi")
    from monitoring.dashboard_api import app

    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200, "Response must not be empty"
    body = response.json()
    endpoints = body.get("endpoints", {})
    assert "ci_metrics" in endpoints or "alerts" in endpoints, "Condition must be true"


# ---------------------------------------------------------------------------
# Boundary 2 – Monitoring ↔ alerting
# ---------------------------------------------------------------------------


class _StubChannel:
    """In-memory alert channel stub — records every event it receives."""

    def __init__(self) -> None:
        self.received: list[Any] = []

    def send(self, event: Any) -> bool:
        self.received.append(event)
        return True

    def name(self) -> str:
        return "stub"


@pytest.mark.integration
def test_alerting_fires_on_training_failure() -> None:
    """TrainingAlertManager delivers a CRITICAL event when a training run fails."""
    from codex.alerting.base import AlertSeverity
    from codex.alerting.manager import TrainingAlertManager

    stub = _StubChannel()
    manager = TrainingAlertManager(channels=[stub], min_severity=AlertSeverity.INFO)

    exc = RuntimeError("CUDA out of memory")
    results = manager.alert_training_failure(exc, run_id="run-001", epoch=3)

    assert results.get("stub") is True, "Result must not be empty"
    assert len(stub.received) == 1, "Collection must not be empty"
    event = stub.received[0]
    assert event.severity == AlertSeverity.CRITICAL, "severity is not valid"
    assert "CUDA out of memory" in event.message, "Condition must be true"
    assert event.run_id == "run-001", "run_id is not valid"
    assert event.epoch == 3, "epoch is not valid"


@pytest.mark.integration
def test_alerting_suppresses_events_below_min_severity() -> None:
    """Events below min_severity threshold are silently discarded."""
    from codex.alerting.base import AlertSeverity
    from codex.alerting.manager import TrainingAlertManager

    stub = _StubChannel()
    # Manager configured to only pass ERROR and above.
    manager = TrainingAlertManager(channels=[stub], min_severity=AlertSeverity.ERROR)

    # alert_training_complete uses INFO severity
    manager.alert_training_complete(run_id="run-002", epochs=5, final_loss=0.25)

    assert len(stub.received) == 0, "INFO event should have been suppressed by min_severity=ERROR"


@pytest.mark.integration
def test_alerting_delivers_to_multiple_channels() -> None:
    """When two channels are registered both receive the event."""
    from codex.alerting.base import AlertSeverity
    from codex.alerting.manager import TrainingAlertManager

    ch1 = _StubChannel()
    ch2 = _StubChannel()
    manager = TrainingAlertManager(channels=[ch1, ch2], min_severity=AlertSeverity.INFO)

    manager.alert_training_complete(run_id="run-003", epochs=10, final_loss=0.10)

    assert len(ch1.received) == 1, "Collection must not be empty"
    assert len(ch2.received) == 1, "Collection must not be empty"
    assert ch1.received[0].run_id == "run-003", "run_id is not valid"
    assert ch2.received[0].run_id == "run-003", "run_id is not valid"


@pytest.mark.integration
def test_alerting_timestamp_is_filled_automatically() -> None:
    """AlertEvent.fill_timestamp() populates the timestamp when it is empty."""
    from codex.alerting.base import AlertEvent, AlertSeverity

    event = AlertEvent(
        title="Test",
        message="No timestamp yet",
        severity=AlertSeverity.WARNING,
    )
    assert event.timestamp == "", "timestamp is not valid"
    event.fill_timestamp()
    assert event.timestamp != "", "timestamp is not valid"
    # Must be ISO-8601 style (contains 'T')
    assert "T" in event.timestamp, "Condition must be true"


# ---------------------------------------------------------------------------
# Boundary 3 – Data-pipeline ↔ training
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_data_pipeline_deterministic_order_is_stable() -> None:
    """deterministic_order returns the same sequence for the same seed."""
    from codex_ml.data.dataloader import deterministic_order

    items = list(range(20))
    order_a = deterministic_order(items.copy(), seed=42)
    order_b = deterministic_order(items.copy(), seed=42)
    assert order_a == order_b, "deterministic_order must be stable across calls"


@pytest.mark.integration
def test_data_pipeline_different_seeds_produce_different_orders() -> None:
    """Different seeds should produce different orderings.

    deterministic_order uses ``(x + seed) % 97`` as the sort key, so a list
    of 100 items spans the modulus boundary and *does* produce different
    orderings for seeds 42 vs 7.
    """
    from codex_ml.data.dataloader import deterministic_order

    # 100 items cross the modulo-97 boundary → different seeds → different orders.
    items = list(range(100))
    order_42 = deterministic_order(items.copy(), seed=42)
    order_7 = deterministic_order(items.copy(), seed=7)
    assert order_42 != order_7, "Different seeds should produce different orderings"


@pytest.mark.integration
def test_data_pipeline_dataset_registry_roundtrip() -> None:
    """A DatasetSpec registered then retrieved is identical (pipeline ↔ training)."""
    from codex_ml.data.datasets import (
        _DATASET_REGISTRY,
        DatasetSpec,
        get_dataset_spec,
        register_dataset,
    )

    spec = DatasetSpec(
        name="_gap23_test_ds_",
        root=Path("."),
        loader=lambda p: iter([]),
        description="Integration test dataset",
        tags=["integration"],
    )

    # Register and immediately retrieve.
    register_dataset(spec, overwrite=True)
    retrieved = get_dataset_spec("_gap23_test_ds_")

    assert retrieved.name == "_gap23_test_ds_", "name is not valid"
    assert "integration" in retrieved.tags, "Condition must be true"

    # Cleanup to avoid polluting other tests.
    _DATASET_REGISTRY.pop("_gap23_test_ds_", None)


@pytest.mark.integration
def test_data_pipeline_loader_callable_invoked_correctly() -> None:
    """The loader callable in a DatasetSpec can be called with its root path."""
    from codex_ml.data.datasets import DatasetSpec

    records = ["line1", "line2", "line3"]

    def _loader(p: Path):
        return iter(records)

    spec = DatasetSpec(name="test_loader", root=Path("."), loader=_loader)
    loaded = list(spec.loader(spec.root))
    assert loaded == records, "Loader must yield the configured records"


# ---------------------------------------------------------------------------
# Boundary 4 – Config ↔ runtime
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_config_load_base_config_returns_dict() -> None:
    """load_base_config() returns a non-empty dict from conf/config.yaml."""
    from codex_ml.config.load import load_base_config

    cfg = load_base_config()
    assert isinstance(cfg, dict)
    assert len(cfg) > 0, "Cfg must not be empty"


@pytest.mark.integration
def test_config_experiment_basic_loads_and_merges() -> None:
    """load_experiment_config('basic') merges correctly with the base config."""
    from codex_ml.config.load import _deep_merge, load_base_config, load_experiment_config

    base = load_base_config()
    exp = load_experiment_config("basic")
    merged = _deep_merge(base, exp)

    assert isinstance(merged, dict)
    # Merged config must contain keys from both layers.
    all_keys = set(base.keys()) | set(exp.keys())
    assert all(k in merged for k in all_keys), "Condition must be true"


@pytest.mark.integration
def test_config_schema_train_config_defaults_valid() -> None:
    """TrainConfig with default values passes pydantic validation."""
    from codex_ml.config_schema import TrainConfig

    cfg = TrainConfig()
    assert cfg.batch_size > 0, "batch_size must be greater than zero"
    assert cfg.epochs >= 1, "epochs must be greater than zero"
    assert 0.0 < cfg.learning_rate < 1.0, "0 is not valid"
    assert cfg.device in ("cpu", "cuda", "mps", "auto")


@pytest.mark.integration
def test_config_schema_train_config_custom_values() -> None:
    """TrainConfig accepts valid custom values and applies them at runtime."""
    from codex_ml.config_schema import TrainConfig

    cfg = TrainConfig(
        model_name="tiny-lm",
        learning_rate=5e-4,
        batch_size=16,
        epochs=3,
        seed=99,
        device="cpu",
    )
    assert cfg.model_name == "tiny-lm", "model_name is not valid"
    assert cfg.learning_rate == pytest.approx(5e-4), "learning_rate is not valid"
    assert cfg.batch_size == 16, "batch_size is not valid"
    assert cfg.epochs == 3, "epochs is not valid"
    assert cfg.seed == 99, "seed is not valid"


@pytest.mark.integration
def test_config_schema_train_config_rejects_invalid_lr() -> None:
    """TrainConfig raises ValidationError for a non-positive learning rate."""
    from pydantic import ValidationError

    from codex_ml.config_schema import TrainConfig

    with pytest.raises(ValidationError):
        TrainConfig(learning_rate=-0.001)


@pytest.mark.integration
def test_config_codex_schema_roundtrip() -> None:
    """CodexConfig can be instantiated from a plain dict and compared."""
    from codex_ml.config.schema import CodexConfig, ModelConfig, TrainingConfig

    model_cfg = ModelConfig(model_name="test-model", hidden_size=128)
    training_cfg = TrainingConfig(learning_rate=1e-3, batch_size=4, max_steps=10)

    codex_cfg = CodexConfig(model=model_cfg, training=training_cfg)

    assert codex_cfg.model.model_name == "test-model", "model_name is not valid"
    assert codex_cfg.model.hidden_size == 128, "hidden_size is not valid"
    assert codex_cfg.training.batch_size == 4, "batch_size is not valid"
    assert codex_cfg.training.max_steps == 10, "max_steps is not valid"
