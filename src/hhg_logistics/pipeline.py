from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from common.mlflow_guard import ensure_local_tracking, log_artifacts_safe, start_run_with_tags
from common.ndjson_tools import append_event_ndjson, make_run_metrics_path
from common.provenance import write_provenance
from common.validate import run_clean_checkpoint

from .pipeline_nodes import run_modular_pipeline

logger = logging.getLogger(__name__)


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
        # write reproducibility metadata
        prov_path = write_provenance(cfg, stage="prepare")
        logger.info("Provenance written to %s", prov_path)
        # log small artifacts (optional)
        feats_csv = Path(outputs["features_csv"])
        log_artifacts_safe(
            {
                "data": clean_csv,
                "features": feats_csv,
                "provenance": Path(".codex") / "provenance.json",
            }
        )
        # write NDJSON event for quick comparisons (P4.3)
        metrics_root = Path(getattr(getattr(cfg, "monitor", {}), "metrics_dir", ".codex/metrics"))
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
