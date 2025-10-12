from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from omegaconf import DictConfig

from .clean import clean_rows, write_clean_csv
from .features import build_features, write_features_csv
from .ingest import ingest_rows

logger = logging.getLogger(__name__)


def run_modular_pipeline(cfg: DictConfig) -> dict[str, Any]:
    """
    Orchestrate ingest -> clean -> features.
    Returns dict with output paths and row counts.
    """
    ingest_path = Path(cfg.pipeline.ingest.input_path)
    rows: list[dict[str, Any]] = ingest_rows(ingest_path)
    logger.info("Ingested %d rows from %s", len(rows), ingest_path)

    cleaned = clean_rows(
        rows,
        required_columns=list(cfg.pipeline.clean.required_columns),
        value_minmax=tuple(cfg.pipeline.clean.value_minmax),
        drop_na=bool(cfg.pipeline.clean.drop_na),
    )
    clean_out = Path(cfg.pipeline.clean.output_path)
    write_clean_csv(cleaned, clean_out)
    logger.info("Wrote cleaned CSV to %s (%d rows)", clean_out, len(cleaned))

    feats = build_features(
        cleaned,
        even_flag=bool(cfg.pipeline.features.even_flag),
        passthrough=list(cfg.pipeline.features.passthrough),
    )
    feat_out = Path(cfg.pipeline.features.output_path)
    write_features_csv(feats, feat_out)
    logger.info("Wrote features CSV to %s (%d rows)", feat_out, len(feats))

    return {
        "clean_csv": str(clean_out),
        "features_csv": str(feat_out),
        "num_rows": len(feats),
    }
