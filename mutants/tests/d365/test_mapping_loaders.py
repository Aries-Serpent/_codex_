"""
Test Mapping Loaders

Test module for mapping loaders.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from codex.mapping.load import load_all_mappings, load_sla


@pytest.fixture(autouse=True)
def _evidence_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CODEX_EVIDENCE_DIR", (tmp_path / "evidence").as_posix())


def test_load_all_mappings_valid() -> None:
    payload = load_all_mappings(Path("configs/deployment/mapping"))
    assert payload["routing"]["count"] >= 1, "Value must be greater than zero"
    assert payload["routing"]["deferred"] == 0, "Condition must be true"
    assert payload["sla"]["count"] >= 1, "Value must be greater than zero"


def test_invalid_sla_row_deferred(tmp_path: Path) -> None:
    bad_csv = tmp_path / "bad_sla.csv"
    bad_csv.write_text(
        "cdm_metric,zd_target_minutes,d365_target_minutes\nfirst_response,sixty,60\n",
        encoding="utf-8",
    )
    result = load_sla(bad_csv)
    assert result.deferred == 1, "Result must not be empty"
    evidence_path = tmp_path / "evidence" / "deferred.jsonl"
    record = json.loads(evidence_path.read_text(encoding="utf-8").strip().splitlines()[-1])
    assert record["phase"] == "mapping-validation", "rec is not valid"
    assert record["meta"]["commit"], "rec is not valid"
