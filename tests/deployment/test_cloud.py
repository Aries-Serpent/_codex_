import json
from pathlib import Path

import pytest

from codex_ml.deployment.cloud import provision_stack
from codex_ml.monitoring.health import HEALTH_LOG_ENV


@pytest.fixture()
def health_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    destination = tmp_path / "health"
    monkeypatch.setenv(HEALTH_LOG_ENV, str(destination))
    return destination


def _read_events(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def test_provision_stack_dry_run_records_health(tmp_path: Path, health_dir: Path) -> None:
    summary = provision_stack(project="demo", metadata={"source": "tests"})

    assert summary["status"] == "deferred"
    assert summary["project"] == "demo"
    assert summary["dry_run"] is True

    log_path = health_dir / "deployment.cloud.ndjson"
    events = _read_events(log_path)
    assert events, "expected a health event to be recorded"
    assert events[-1]["event"] == "dry_run"


def test_provision_stack_materialises_manifest(tmp_path: Path, health_dir: Path) -> None:
    output_dir = tmp_path / "deployments"
    summary = provision_stack(project="demo", output_dir=output_dir, dry_run=False)

    assert Path(summary["manifest"]).is_file()
    manifest = json.loads(Path(summary["manifest"]).read_text(encoding="utf-8"))
    assert manifest["project"] == "demo"
    assert Path(manifest["sandbox"]).is_dir()

    log_path = health_dir / "deployment.cloud.ndjson"
    events = _read_events(log_path)
    assert any(event["event"] == "materialised" for event in events)
