from __future__ import annotations

from pathlib import Path

from hhg_logistics.pipeline_nodes.clean import clean_rows, write_clean_csv
from hhg_logistics.pipeline_nodes.features import build_features, write_features_csv
from hhg_logistics.pipeline_nodes.ingest import ingest_rows


def test_ingest_creates_default(tmp_path: Path) -> None:
    path = tmp_path / "input.csv"
    rows = ingest_rows(path)
    assert len(rows) == 10
    assert set(rows[0].keys()) == {"id", "value"}


def test_clean_filters_and_coerces(tmp_path: Path) -> None:
    rows = [{"id": "1", "value": "2"}, {"id": "2", "value": "99"}]
    cleaned = clean_rows(rows, required_columns=["id", "value"], value_minmax=(0, 2))
    assert len(cleaned) == 1
    assert isinstance(cleaned[0]["id"], int)
    assert isinstance(cleaned[0]["value"], int)

    out_path = tmp_path / "clean.csv"
    write_clean_csv(cleaned, out_path)
    assert out_path.exists()
    assert out_path.read_text().strip().splitlines()[0] == "id,value"


def test_features_writes_csv(tmp_path: Path) -> None:
    cleaned = [{"id": 1, "value": 2}]
    feats = build_features(cleaned, even_flag=True, passthrough=["id", "value"])
    assert feats
    assert feats[0]["value_is_even"] is True

    out_path = tmp_path / "features.csv"
    write_features_csv(feats, out_path)
    assert out_path.exists()
