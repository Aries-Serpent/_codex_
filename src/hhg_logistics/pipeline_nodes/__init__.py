from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from codex_ml.utils.optional import optional_import
from omegaconf import DictConfig

from .clean import clean_rows, write_clean_csv
from .features import build_features, write_features_csv
from .ingest import ingest_rows

logger = logging.getLogger(__name__)

hydra_utils, _HAS_HYDRA_UTILS = optional_import("hydra.utils")
hydra_core_global, _ = optional_import("hydra.core.global_hydra")
GlobalHydra = getattr(hydra_core_global, "GlobalHydra", None)


def _resolve_pipeline_path(path: Path) -> Path:
    """Resolve pipeline paths relative to Hydra's original working directory."""

    if path.is_absolute():
        return path

    hydra_initialized = False
    if GlobalHydra is not None:
        try:
            hydra_initialized = bool(GlobalHydra.instance().is_initialized())
        except Exception:
            hydra_initialized = False

    if _HAS_HYDRA_UTILS and hydra_initialized:
        to_absolute_path = getattr(hydra_utils, "to_absolute_path", None)
        if callable(to_absolute_path):
            return Path(to_absolute_path(str(path)))

        get_original_cwd = getattr(hydra_utils, "get_original_cwd", None)
        if callable(get_original_cwd):
            return Path(get_original_cwd()) / path

    return (Path.cwd() / path).resolve()


def run_modular_pipeline(cfg: DictConfig) -> dict[str, Any]:
    """
    Orchestrate ingest -> clean -> features.
    Returns dict with output paths and row counts.
    """
    ingest_path = _resolve_pipeline_path(Path(cfg.pipeline.ingest.input_path))
    rows: list[dict[str, Any]] = ingest_rows(ingest_path)
    logger.info("Ingested %d rows from %s", len(rows), ingest_path)

    cleaned = clean_rows(
        rows,
        required_columns=list(cfg.pipeline.clean.required_columns),
        value_minmax=tuple(cfg.pipeline.clean.value_minmax),
        drop_na=bool(cfg.pipeline.clean.drop_na),
    )
    clean_out = _resolve_pipeline_path(Path(cfg.pipeline.clean.output_path))
    write_clean_csv(cleaned, clean_out)
    logger.info("Wrote cleaned CSV to %s (%d rows)", clean_out, len(cleaned))

    feats = build_features(
        cleaned,
        even_flag=bool(cfg.pipeline.features.even_flag),
        passthrough=list(cfg.pipeline.features.passthrough),
    )
    feat_out = _resolve_pipeline_path(Path(cfg.pipeline.features.output_path))
    write_features_csv(feats, feat_out)
    logger.info("Wrote features CSV to %s (%d rows)", feat_out, len(feats))

    return {
        "clean_csv": str(clean_out),
        "features_csv": str(feat_out),
        "num_rows": len(feats),
    }
