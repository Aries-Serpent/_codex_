from __future__ import annotations

from pathlib import Path
from shutil import copyfile

from hhg_logistics.pipeline import run_pipeline
from omegaconf import OmegaConf


def test_pipeline_with_sample_data(tmp_path: Path, monkeypatch) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    repo_raw = repo_root / "data" / "sample" / "raw.csv"
    raw_path = tmp_path / "raw.csv"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    copyfile(repo_raw, raw_path)

    processed_dir = tmp_path / "processed"
    clean_out = processed_dir / "clean.csv"
    feats_out = processed_dir / "features.csv"

    cfg = OmegaConf.create(
        {
            "data": {
                "raw_dir": str(tmp_path),
                "processed_dir": str(processed_dir),
            },
            "pipeline": {
                "ingest": {"input_path": str(raw_path)},
                "clean": {
                    "output_path": str(clean_out),
                    "drop_na": True,
                    "required_columns": ["id", "value"],
                    "value_minmax": [0, 2],
                },
                "features": {
                    "output_path": str(feats_out),
                    "even_flag": True,
                    "passthrough": ["id", "value"],
                },
            },
        }
    )

    monkeypatch.chdir(tmp_path)
    result = run_pipeline(cfg)
    assert Path(result["clean_csv"]).exists()
    assert Path(result["features_csv"]).exists()
