"""Minimal command-line interface for running Codex training loops."""

from __future__ import annotations

import argparse
import importlib
import importlib.machinery
import logging
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Optional

from data.registry import build as build_registered_dataset
from logging_utils import LoggingConfig
from metrics import accuracy as metrics_accuracy
from omegaconf import OmegaConf
from training.trainer import CheckpointConfig, Trainer, TrainerConfig

logger = logging.getLogger(__name__)

try:
    from hydra import compose, initialize_config_dir
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
    from config_legacy import compose, initialize_config_dir

CLI_PACKAGE_PATH = Path(__file__).resolve().parent.parent / "cli"
PROJECT_ROOT = CLI_PACKAGE_PATH.parent
# Keep project root importable but avoid shadowing installed third-party packages.
# Remove cwd aliases to prevent local stub packages from shadowing site-packages.
for candidate in ("", ".", str(PROJECT_ROOT)):
    while candidate in sys.path:
        sys.path.remove(candidate)
sys.path.append(str(PROJECT_ROOT))

TOKENIZATION_DIR = PROJECT_ROOT / "tokenization"
tokenization_pkg = sys.modules.get("tokenization")
if tokenization_pkg is None:
    tokenization_pkg = importlib.util.module_from_spec(
        importlib.machinery.ModuleSpec("tokenization", loader=None, is_package=True)
    )
    tokenization_pkg.__path__ = [str(TOKENIZATION_DIR)]
    sys.modules["tokenization"] = tokenization_pkg

tokenization_spec = importlib.util.spec_from_file_location(
    "tokenization.loader",
    TOKENIZATION_DIR / "loader.py",
    submodule_search_locations=[str(TOKENIZATION_DIR)],
)
if tokenization_spec is None or tokenization_spec.loader is None:
    raise ImportError(f"Unable to load tokenization.loader from {TOKENIZATION_DIR}")
tokenization_loader = importlib.util.module_from_spec(tokenization_spec)
sys.modules["tokenization.loader"] = tokenization_loader
tokenization_spec.loader.exec_module(tokenization_loader)
TRAIN_CODEX_PATH = CLI_PACKAGE_PATH / "train_codex.py"
if not TRAIN_CODEX_PATH.exists():
    raise ImportError(f"train_codex module not found at {TRAIN_CODEX_PATH}")

spec = importlib.util.spec_from_file_location("cli.train_codex", TRAIN_CODEX_PATH)
if spec is None or spec.loader is None:
    raise ImportError(f"Unable to load train_codex module from {TRAIN_CODEX_PATH}")
train_codex = importlib.util.module_from_spec(spec)
sys.modules["cli.train_codex"] = train_codex
spec.loader.exec_module(train_codex)


def _ensure_real_torch() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, "__version__", "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def _resolve_callable(target: str) -> Any:
    module_name, _, attr = target.rpartition(".")
    if not module_name:
        raise ValueError(f"Target '{target}' must include a module path")
    if module_name.startswith("torch"):
        _ensure_real_torch()
    module = importlib.import_module(module_name)
    try:
        resolved = getattr(module, attr)
    except AttributeError as exc:  # pragma: no cover - defensive
        raise AttributeError(f"Module '{module_name}' has no attribute '{attr}'") from exc
    if not callable(resolved):
        raise TypeError(f"'{module_name}.{attr}' is not callable")
    return resolved


def _section_to_dict(section: Any) -> dict[str, Any]:
    if isinstance(section, Mapping):
        return dict(section)
    return {}


def simple_synthetic_data(**params: Any) -> tuple[Any, Optional[Any]]:
    """Expose the built-in synthetic dataset via a convenience wrapper."""

    return build_registered_dataset("synthetic_classification", **params)


def classification_accuracy(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def _instantiate_model(model_cfg: Mapping[str, Any]) -> Any:
    target = model_cfg.get("target")
    if not target:
        raise ValueError("model.target is required")
    params = _section_to_dict(model_cfg.get("params"))
    factory = _resolve_callable(str(target))
    return factory(**params)


def _instantiate_optimizer(optimizer_cfg: Mapping[str, Any], model: Any) -> Any:
    target = optimizer_cfg.get("target")
    if not target:
        raise ValueError("optimizer.target is required")
    params = _section_to_dict(optimizer_cfg.get("params"))
    factory = _resolve_callable(str(target))
    return factory(model.parameters(), **params)


def _resolve_loss(loss_cfg: Optional[Mapping[str, Any]]) -> Any:
    if not loss_cfg:
        import torch.nn.functional as F

        return F.cross_entropy
    target = loss_cfg.get("target")
    params = _section_to_dict(loss_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    raise ValueError("loss configuration must provide a target")


def _resolve_metric(metric_cfg: Optional[Mapping[str, Any]]) -> Any:
    if not metric_cfg:
        return None
    target = metric_cfg.get("target")
    params = _section_to_dict(metric_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    name = metric_cfg.get("name")
    if name == "accuracy":
        return classification_accuracy
    return None


def _resolve_dataloaders(data_cfg: Mapping[str, Any]) -> tuple[Any, Optional[Any]]:
    if not data_cfg:
        raise ValueError("data configuration is required")
    params = _section_to_dict(data_cfg.get("params"))
    target = data_cfg.get("target")
    if target:
        builder = _resolve_callable(str(target))
        loaders = builder(**params)
    else:
        name = data_cfg.get("name")
        if not name:
            raise ValueError("data configuration must provide 'target' or 'name'")
        loaders = build_registered_dataset(str(name), **params)
    if isinstance(loaders, tuple) and len(loaders) == 2:
        return loaders
    return loaders, None


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: Optional[CheckpointConfig] = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
