from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from codex_ml.utils.optional import optional_import
from common.mlflow_guard import (
    ensure_local_tracking,
    log_artifacts_safe,
    log_dict_safe,
    start_run_with_tags,
)
from common.ndjson_tools import append_event_ndjson, make_run_metrics_path
from common.provenance import write_provenance
from common.validate import run_clean_checkpoint

from .pipeline_nodes import run_modular_pipeline

logger = logging.getLogger(__name__)

hydra_utils, _HAS_HYDRA_UTILS = optional_import("hydra.utils")
hydra_core_global, _ = optional_import("hydra.core.global_hydra")
GlobalHydra = getattr(hydra_core_global, "GlobalHydra", None)


def _resolve_relative_path(path: Path) -> Path:
    """Resolve a potentially relative path using Hydra's original working directory."""

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


def _resolve_metrics_root(metrics_dir: Path) -> Path:
    """Resolve the metrics directory relative to the original working directory."""

    return _resolve_relative_path(metrics_dir)


def run_pipeline(cfg) -> Any:
    """Use modular data pipeline prior to any training."""
    logger.info("Running modular pipeline: ingest -> clean -> features")
    # Ensure MLflow is in file: mode unless explicitly allowed
    ensure_local_tracking(cfg)
    # Track a run with codex tags; still execute even if mlflow not installed
    with start_run_with_tags(cfg, run_name="pipeline"):
        outputs = run_modular_pipeline(cfg)
        # Fail-fast data validation with Great Expectations
        clean_csv = Path(outputs["clean_csv"])
        logger.info("Validating cleaned data via Great Expectations: %s", clean_csv)
        run_clean_checkpoint(clean_csv)

        drift_summary = None
        drift_html: Path | None = None
        drift_json: Path | None = None
        monitor_cfg = getattr(cfg, "monitor", None)
        data_cfg = getattr(monitor_cfg, "data", None) if monitor_cfg is not None else None
        if data_cfg is not None and bool(getattr(data_cfg, "enable", False)):
            from hhg_logistics.monitor.data_gate import run_data_drift_gate

            reference_csv = _resolve_relative_path(Path(data_cfg.reference_csv))
            drift_html = Path(data_cfg.report_html)
            drift_json = Path(data_cfg.report_json)
            thresholds = dict(getattr(data_cfg, "thresholds", {}))
            abort_on_critical = bool(getattr(data_cfg, "abort_on_critical", False))
            tracked = list(getattr(data_cfg, "tracked_columns", []))
            tracked_columns = tracked or None
            logger.info("Running data drift gate (ref=%s, cur=%s)", reference_csv, clean_csv)
            drift_summary = run_data_drift_gate(
                reference_csv,
                clean_csv,
                drift_html,
                drift_json,
                thresholds,
                abort_on_critical,
                tracked_columns,
            )
            log_dict_safe(
                drift_summary, artifact_path=Path(".codex") / "reports" / "data_drift_summary.json"
            )

        # write reproducibility metadata
        prov_path = write_provenance(cfg, stage="prepare")
        logger.info("Provenance written to %s", prov_path)
        # log small artifacts (optional)
        feats_csv = Path(outputs["features_csv"])
        artifacts = {
            "data": clean_csv,
            "features": feats_csv,
            "provenance": Path(".codex") / "provenance.json",
        }
        if drift_summary is not None and drift_html is not None and drift_json is not None:
            artifacts.update({"data_drift_html": drift_html, "data_drift_json": drift_json})
        log_artifacts_safe(artifacts)
        # write NDJSON event for quick comparisons (P4.3)
        metrics_root = Path(getattr(getattr(cfg, "monitor", {}), "metrics_dir", ".codex/metrics"))
        metrics_root = _resolve_metrics_root(metrics_root)
        metrics_path = make_run_metrics_path(metrics_root)
        append_event_ndjson(
            metrics_path,
            {
                "event": "pipeline_complete",
                "outputs.clean_csv": str(clean_csv),
                "outputs.features_csv": str(feats_csv),
                "metrics": {"rows": int(outputs.get("num_rows", 0))},
            },
        )
    logger.info("Pipeline complete: %s", outputs)
    return outputs
