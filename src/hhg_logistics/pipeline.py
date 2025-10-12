from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from common.provenance import write_provenance
from common.validate import run_clean_checkpoint

from .pipeline_nodes import run_modular_pipeline

logger = logging.getLogger(__name__)


def run_pipeline(cfg) -> Any:
    """Use modular data pipeline prior to any training."""
    logger.info("Running modular pipeline: ingest -> clean -> features")
    outputs = run_modular_pipeline(cfg)
    clean_csv = Path(outputs["clean_csv"])
    logger.info("Validating cleaned data via Great Expectations: %s", clean_csv)
    run_clean_checkpoint(clean_csv)
    prov_path = write_provenance(cfg, stage="prepare")
    logger.info("Provenance written to %s", prov_path)
    logger.info("Pipeline complete: %s", outputs)
    return outputs
