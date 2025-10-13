from __future__ import annotations

import json
from pathlib import Path

import pytest

from codex.dynamics.apply_logging import apply_routing_stub, apply_slas_stub


@pytest.fixture(autouse=True)
def _clear_evidence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("CODEX_EVIDENCE_DIR", tmp_path.as_posix())
    yield


def _last_record(path: Path) -> dict:
    content = path.read_text(encoding="utf-8").strip().splitlines()
    return json.loads(content[-1])


def test_apply_sla_stub_logs_metadata(tmp_path: Path) -> None:
    summary = apply_slas_stub(
        {
            "operations": [
                {
                    "resource": "sla",
                    "action": "add",
                    "name": "standard",
                    "data": {"metric": "first_response", "target_minutes": 60},
                }
            ]
        },
        dry_run=True,
    )
    assert summary["processed"] == 1
    evidence_path = tmp_path / "d365_slas.jsonl"
    record = _last_record(evidence_path)
    assert record["meta"]["commit"]
    assert record["meta"]["python"]
    assert record["meta"]["os"]
    assert record["resource"] == "sla"
    assert record["action"] == "Create"


def test_apply_routing_stub_logs_non_dry_run(tmp_path: Path) -> None:
    summary = apply_routing_stub(
        {
            "operations": [
                {
                    "resource": "routing",
                    "action": "update",
                    "name": "assignment_auto_route",
                    "data": {"queue": "Relocation CSR Queue"},
                }
            ]
        },
        dry_run=False,
    )
    assert summary["dry_run"] is False
    evidence_path = tmp_path / "d365_routing.jsonl"
    record = _last_record(evidence_path)
    assert record["dry_run"] is False
    assert record["action"] == "Update"
    assert record["meta"]["commit"]
