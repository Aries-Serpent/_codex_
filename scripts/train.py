"""
Train

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/train.py [options]
    
    Examples:
    $ python scripts/train.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""


from __future__ import annotations
import logging
logger = logging.getLogger(__name__)
#!/usr/bin/env python
"""CLI wrapper around :func:`src.training.engine_hf_trainer.run_hf_trainer`."""


import argparse
import importlib
import importlib.util
import json
import random
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Mapping

from src.training.config import TrainingConfig
from src.training.engine_hf_trainer import run_hf_trainer


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run HF Trainer with dataclass config")
    parser.add_argument("--config", type=Path, help="Optional JSON/YAML config file")
    parser.add_argument(
        "--config-from-env",
        action="store_true",
        help="Seed defaults from TRAIN_* environment variables",
    )
    parser.add_argument("--output", type=Path, help="Override output directory")
    parser.add_argument("--val-split", type=float, help="Override validation split ratio")
    parser.add_argument("--dry-run", action="store_true", help="Print resolved config and exit")
    return parser.parse_args(argv)


def _load_config_file(path: Path) -> Mapping[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        if path.suffix.lower() not in {".yml", ".yaml"}:
            raise
        if importlib.util.find_spec("yaml") is None:
            raise RuntimeError(
                "YAML config supplied but PyYAML is not installed; install it or use JSON."
            ) from exc
        yaml_module = importlib.import_module("yaml")
        data = yaml_module.safe_load(text)
        return data or {}


def _config_to_dict(cfg: TrainingConfig) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in cfg.as_dict().items():
        if isinstance(value, Path):
            result[key] = str(value)
        else:
            result[key] = value
    return result


def _load_texts(path: Path) -> list[str]:
    lines: list[str] = []
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            text = raw.strip()
            if text:
                lines.append(text)
    return lines


def _split_texts(
    texts: list[str], val_split: float, seed: int
) -> tuple[list[str], list[str] | None]:
    if val_split <= 0 or not texts:
        return texts, None
    shuffled = list(texts)
    random.Random(seed).shuffle(shuffled)
    val_count = max(1, int(len(shuffled) * val_split))
    val_subset = shuffled[:val_count]
    train_subset = shuffled[val_count:]
    if not train_subset:
        train_subset = val_subset
        val_subset = []
    return train_subset, val_subset or None


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    cfg = TrainingConfig.from_env() if args.config_from_env else TrainingConfig()
    data = cfg.as_dict()
    if args.config:
        file_cfg = _load_config_file(args.config)
        data.update(file_cfg)
    if args.output:
        data["output_dir"] = args.output
    if args.val_split is not None:
        data["val_split"] = args.val_split
    cfg = TrainingConfig.from_mapping(data)

    if args.dry_run:
        print(json.dumps(_config_to_dict(cfg), indent=2, sort_keys=True))
        return 0

    if not cfg.dataset_path.exists():
        raise FileNotFoundError(f"Dataset file not found: {cfg.dataset_path}")
    train_texts = _load_texts(cfg.dataset_path)
    if not train_texts:
        raise RuntimeError("Dataset is empty after filtering blank lines")

    if cfg.eval_dataset_path is not None:
        if not cfg.eval_dataset_path.exists():
            raise FileNotFoundError(f"Eval dataset file not found: {cfg.eval_dataset_path}")
        val_texts = _load_texts(cfg.eval_dataset_path)
    else:
        train_texts, val_texts = _split_texts(train_texts, cfg.val_split, cfg.seed)

    cfg.output_dir.mkdir(parents=True, exist_ok=True)

    metrics = run_hf_trainer(
        train_texts,
        cfg.output_dir,
        model_name=cfg.model_name,
        tokenizer_name=cfg.tokenizer_name,
        precision=cfg.precision,
        seed=cfg.seed,
        gradient_accumulation_steps=cfg.gradient_accumulation_steps,
        val_texts=val_texts,
        val_split=0.0,
        deterministic=cfg.deterministic,
        lora_r=cfg.lora_r if cfg.use_lora else None,
        lora_alpha=cfg.lora_alpha if cfg.use_lora else None,
        lora_dropout=cfg.lora_dropout if cfg.use_lora else None,
        lora_task_type=cfg.lora_task_type if cfg.use_lora else None,
        mlflow_tracking_uri=cfg.mlflow_tracking_uri,
        distributed=False,
        config_path=args.config,
        hydra_cfg=_config_to_dict(cfg),
    )
    print(json.dumps(metrics, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
