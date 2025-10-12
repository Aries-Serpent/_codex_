import logging
from typing import Any

from common.provenance import write_provenance

logger = logging.getLogger(__name__)


def step_load_data(cfg) -> dict:
    logger.info("Loading data from %s", cfg.data.path)
    # placeholder: implement later iterations
    return {"train": [], "valid": []}


def step_train_model(cfg, data) -> dict:
    logger.info(
        "Training model=%s epochs=%s lr=%s",
        cfg.model.type,
        cfg.training.epochs,
        cfg.training.lr,
    )
    # placeholder: implement later iterations
    return {"metrics": {"loss": 0.0}}


def run_pipeline(cfg) -> Any:
    logger.info("Running pipeline steps: load_data -> train_model")
    data = step_load_data(cfg)
    outputs = step_train_model(cfg, data)
    provenance_path = write_provenance(cfg, stage="prepare")
    logger.info("Pipeline provenance recorded at %s", provenance_path)
    logger.info("Pipeline complete: %s", outputs)
    return outputs
