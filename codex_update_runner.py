#!/usr/bin/env python3
"""Codex sequential updater implementing audit remediation tasks."""

from __future__ import annotations

import ast
import json
import os
import re
import textwrap
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable

import yaml
from codex_ml.utils.hf_pinning import load_from_pretrained  # noqa: F401

CHANGE_LOG = Path(".codex/change_log.md")
ERROR_LOG = Path(".codex/errors.ndjson")


def _timestamp() -> str:
    return datetime.utcnow().isoformat() + "Z"


def log_change(message: str) -> None:
    CHANGE_LOG.parent.mkdir(parents=True, exist_ok=True)
    with CHANGE_LOG.open("a", encoding="utf-8") as fh:
        fh.write(message + "\n")


def log_error(phase: str, substep: str, exc: BaseException, context: str) -> None:
    ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": _timestamp(),
        "step": f"{phase}:{substep}",
        "error": str(exc),
        "context": context,
        "question": (
            "What are the possible causes, and how can this be resolved while preserving "
            "intended functionality?"
        ),
    }
    with ERROR_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")


def _append_phase_heading(title: str) -> None:
    log_change(f"\n### {title}\n")


def phase_preparation() -> None:
    phase = "Phase1"
    _append_phase_heading("Phase 1 – Preparation")
    try:
        repo_root = Path.cwd()
        log_change(f"- Repository root: `{repo_root}`")
        workflows = repo_root / ".github" / "workflows"
        if workflows.exists():
            log_change("- Detected .github/workflows; will avoid modifying workflow YAML files.")
        else:
            log_change("- No .github/workflows directory present.")
    except Exception as exc:
        log_error(phase, "detect_root", exc, "Determining repository root and workflows")

    for doc in ["README.md", "docs/modules/training_engine.md", "docs/repro.md"]:
        try:
            path = Path(doc)
            if not path.exists():
                log_change(f"- Document missing: {doc}")
                continue
            text = path.read_text(encoding="utf-8")
            references = [line for line in text.splitlines() if "configs/" in line]
            if references:
                sample = ", ".join(references[:3])
                log_change(f"- {doc} references configs: {sample}")
                if len(references) > 3:
                    log_change(f"  … (+{len(references) - 3} more lines)")
            else:
                log_change(f"- {doc} contains no direct config references.")
        except Exception as exc:
            log_error(phase, f"read_{doc}", exc, f"Reading {doc}")


def _categorize(path: Path) -> Iterable[str]:
    taxonomy = {
        "token": "tokenisation",
        "train": "training",
        "safety": "safety",
        "eval": "evaluation",
        "monitor": "monitoring",
        "checkpoint": "checkpointing",
        "data": "data",
        "cli": "cli",
        "config": "configuration",
        "model": "modeling",
        "telemetry": "telemetry",
    }
    lower = str(path).lower()
    matched = {name for key, name in taxonomy.items() if key in lower}
    return matched or {"misc"}


def phase_search_and_mapping() -> None:
    phase = "Phase2"
    _append_phase_heading("Phase 2 – Search & Mapping")
    repo_root = Path.cwd()
    mapping: Dict[str, list[str]] = defaultdict(list)
    try:
        for root, dirs, files in os.walk(repo_root):
            root_path = Path(root)
            if ".git" in root_path.parts:
                continue
            if Path(".github") in root_path.parents or root_path.name == "workflows":
                continue
            for name in files:
                if name.endswith((".py", ".md")):
                    rel = str((root_path / name).relative_to(repo_root))
                    for category in _categorize(Path(rel)):
                        mapping[category].append(rel)
    except Exception as exc:
        log_error(phase, "walk", exc, "Enumerating repository files")

    for category, files in sorted(mapping.items()):
        preview = ", ".join(files[:3])
        suffix = f" (+{len(files) - 3} more)" if len(files) > 3 else ""
        log_change(f"- {category}: {preview}{suffix}")

    stub_markers = ("TODO", "NotImplementedError", "pass  # TODO")
    try:
        for path in repo_root.rglob("*.py"):
            if ".git" in path.parts:
                continue
            if Path(".github") in path.parents:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except Exception as exc:
                log_error(phase, "read_stub", exc, f"Reading {path}")
                continue
            for marker in stub_markers:
                if marker in text:
                    rel = path.relative_to(repo_root)
                    log_change(f"- Stub marker `{marker}` in {rel}")
                    break
    except Exception as exc:
        log_error(phase, "scan_stubs", exc, "Scanning for stub markers")

    expected_configs = [
        "configs/training/base.yaml",
        "configs/data/base.yaml",
        "configs/tokenization/base.yaml",
    ]
    for rel in expected_configs:
        path = Path(rel)
        status = "present" if path.exists() else "missing"
        log_change(f"- Config {rel}: {status}")


def _build_training_config() -> dict[str, Any]:
    shared = {
        "seed": 42,
        "learning_rate": 3e-4,
        "batch_size": 32,
        "max_epochs": 5,
        "scheduler": "linear",
        "warmup_steps": 0,
        "gradient_accumulation": 1,
        "tensorboard": True,
        "mlflow_enable": False,
    }
    training_block = {
        "seed": shared["seed"],
        "lr": shared["learning_rate"],
        "batch_size": shared["batch_size"],
        "epochs": shared["max_epochs"],
        "grad_accum": shared["gradient_accumulation"],
        "warmup_steps": shared["warmup_steps"],
        "save_every": 50,
        "log_every": 10,
        "checkpoint_dir": "runs/default/checkpoints",
        "texts": [],
        "val_texts": [],
    }
    hf_block = {
        "output_dir": "runs/default",
        "num_train_epochs": shared["max_epochs"],
        "per_device_train_batch_size": shared["batch_size"],
        "per_device_eval_batch_size": shared["batch_size"],
        "learning_rate": shared["learning_rate"],
        "weight_decay": 0.01,
        "gradient_accumulation_steps": shared["gradient_accumulation"],
        "logging_steps": 10,
        "save_steps": 50,
        "evaluation_strategy": "steps",
        "eval_steps": 50,
        "fp16": False,
        "lora": {"enable": False, "r": 4, "alpha": 16, "dropout": 0.1},
        "privacy": {
            "enabled": False,
            "noise_multiplier": 1.0,
            "max_grad_norm": 1.0,
            "target_delta": 1e-5,
            "accountant": "rdp",
        },
    }
    data = {
        **shared,
        "model": "minilm",
        "output_dir": "runs/default",
        "training": training_block,
        "logging": {
            "enable_tensorboard": shared["tensorboard"],
            "mlflow_enable": shared["mlflow_enable"],
        },
        "hf_trainer": hf_block,
    }
    return data


def task_create_training_config() -> None:
    phase = "Phase3A"
    _append_phase_heading("Phase 3 – Task A: Training config")
    cfg_path = Path("configs/training/base.yaml")
    try:
        data = _build_training_config()
        cfg_path.parent.mkdir(parents=True, exist_ok=True)
        with cfg_path.open("w", encoding="utf-8") as fh:
            yaml.safe_dump(data, fh, sort_keys=False)
        log_change(f"- Wrote training config to {cfg_path}")
    except Exception as exc:
        log_error(phase, "write_config", exc, f"Writing {cfg_path}")


def _ensure_typing_import(file_text: str) -> str:
    if "from typing import Optional" in file_text:
        return file_text
    sentinel = "from __future__ import annotations\n\n"
    if sentinel in file_text:
        return file_text.replace(
            sentinel,
            "from __future__ import annotations\n\nfrom typing import Optional\n\n",
            1,
        )
    if "import click" in file_text:
        return file_text.replace(
            "import click",
            "import click\nfrom typing import Optional",
            1,
        )
    return file_text


def task_update_cli() -> None:
    phase = "Phase3B"
    _append_phase_heading("Phase 3 – Task B: CLI train command")
    cli_path = Path("src/codex_ml/cli/codex_cli.py")
    try:
        text = cli_path.read_text(encoding="utf-8")
    except Exception as exc:
        log_error(phase, "read_cli", exc, f"Reading {cli_path}")
        return

    text = _ensure_typing_import(text)

    new_impl = textwrap.dedent(
        """
        @codex.command()
        @click.option(
            "--config",
            default="configs/training/base.yaml",
            show_default=True,
            type=click.Path(exists=True, dir_okay=False, path_type=str),
            help="Path to the training YAML configuration.",
        )
        @click.option("--resume", is_flag=True, help="Resume from the latest checkpoint if available.")
        @click.option("--seed", type=int, default=None, help="Override the random seed from the config.")
        def train(config: str, resume: bool, seed: Optional[int]) -> None:
            \"\"\"Train a language model using the Codex functional trainer.\"\"\"
            from codex_ml.utils.config_loader import load_config
            from codex_ml.training import run_functional_training
            from codex_ml.utils.error_log import log_error as log_training_error

            try:
                cfg = load_config(config_path=config)
                if seed is not None:
                    if "training" in cfg and hasattr(cfg.training, "seed"):
                        cfg.training.seed = seed
                    else:
                        cfg.seed = seed
                run_functional_training(config=cfg, resume=resume)
                click.echo("training complete")
            except Exception as exc:  # pragma: no cover - Click handles presentation
                log_training_error("cli.train", str(exc), f"config={config} resume={resume}")
                raise click.ClickException(str(exc))
        """
    ).strip("\n")

    pattern = re.compile(
        r"@codex\.command\(\)\n@click\.option\(\"--text\",.*?\n"  # decorator portion
        r"def train\([^)]*\):\n(?:    .*(?:\n|$))+?"  # body
        r"(?=\n@codex\.command|\nif __name__ == \"__main__\"|\Z)",
        re.DOTALL,
    )
    if not pattern.search(text):
        log_error(phase, "pattern", ValueError("train stub not found"), str(cli_path))
        return
    text = pattern.sub(new_impl + "\n\n", text)

    try:
        cli_path.write_text(text, encoding="utf-8")
        log_change("- Updated train CLI implementation in codex_cli.py")
    except Exception as exc:
        log_error(phase, "write_cli", exc, f"Writing {cli_path}")


RUN_FUNCTIONAL_STUB = textwrap.dedent(
    """from __future__ import annotations

import json
import random
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from typing import Any


def _deterministic_seed(value: int) -> None:
    random.seed(value)
    try:  # numpy is optional in minimal environments
        import numpy as _np  # type: ignore

        _np.random.seed(value % (2**32 - 1))
    except Exception:  # pragma: no cover - numpy may not be installed
        pass


def run_functional_training(
    config: Mapping[str, Any] | None,
    *,
    resume: bool = False,
) -> dict[str, Any]:
    \"\"\"Fallback functional training entrypoint used during bootstrapping.\"\"\"

    if config is None:
        config = {}
    if not isinstance(config, Mapping):
        raise TypeError("config must be a mapping")

    seed = int(config.get("seed", 42) or 42)
    _deterministic_seed(seed)

    output_root = Path(config.get("output_dir", "runs/fallback"))
    output_root.mkdir(parents=True, exist_ok=True)
    state_path = output_root / "state.json"

    state = {
        "seed": seed,
        "resume": bool(resume),
        "timestamp": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "config_keys": sorted(str(key) for key in config.keys()),
    }
    state_path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "status": "ok",
        "resume": bool(resume),
        "state_file": str(state_path),
    }
"""
)


def _ensure_training_module() -> None:
    path = Path("src/codex_ml/training/__init__.py")
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(RUN_FUNCTIONAL_STUB, encoding="utf-8")


def task_update_run_functional_training() -> None:
    phase = "Phase3C"
    _append_phase_heading("Phase 3 – Task C: run_functional_training resume support")
    module_path = Path("src/codex_ml/training/__init__.py")
    try:
        _ensure_training_module()
        source = module_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        target = None
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == "run_functional_training":
                target = node
                break
        if target is None:
            raise RuntimeError("run_functional_training not found")
        start = target.lineno - 1
        end = target.end_lineno
        new_function = textwrap.dedent(
            """
            def run_functional_training(
                config: DictConfig | Mapping[str, Any],
                *,
                resume: bool = False,
            ) -> dict[str, Any]:
                \"\"\"Run the Codex functional training loop with optional resume support.\"\"\"

                from collections.abc import Mapping as _Mapping
                from pathlib import Path as _Path

                import numpy as _np
                from omegaconf import DictConfig as _DictConfig, OmegaConf as _OmegaConf

                try:
                    from datasets import Dataset as _Dataset  # type: ignore
                    from transformers import AutoTokenizer as _AutoTokenizer  # type: ignore
                except Exception as exc:  # pragma: no cover - optional deps
                    raise RuntimeError("datasets and transformers are required for training") from exc

                from codex_ml.models.registry import get_model as _get_model
                from codex_ml.utils.checkpointing import load_training_checkpoint as _load_ckpt
                from training.functional_training import TrainCfg as _TrainCfg, run_custom_trainer as _run_custom_trainer

                if isinstance(config, _DictConfig):
                    container = _OmegaConf.to_container(config, resolve=True)  # type: ignore[arg-type]
                elif isinstance(config, _Mapping):
                    container = dict(config)
                    config = _OmegaConf.create(container)
                else:
                    raise TypeError("config must be a mapping or DictConfig")

                training_section = container.get("training", {}) if isinstance(container, dict) else {}
                if not isinstance(training_section, dict):
                    training_section = {}

                def _pop(keys: Iterable[str], default: Any = None) -> Any:
                    for key in keys:
                        if key in training_section:
                            return training_section[key]
                        if isinstance(container, dict) and key in container:
                            return container[key]
                    return default

                texts = _pop(["texts"]) or []
                if not texts:
                    raise ValueError("training texts are required in the config")
                val_texts = _pop(["val_texts"], None)

                model_cfg = training_section.get("model") or container.get("model") or {"name": "MiniLM"}
                tokenizer_name = model_cfg.get("pretrained_model_name_or_path") or model_cfg.get("name") or "sshleifer/tiny-gpt2"

                checkpoint_dir_value = training_section.get("checkpoint_dir") or container.get("output_dir") or "runs/default/checkpoints"
                checkpoint_dir = _Path(checkpoint_dir_value)
                if checkpoint_dir.suffix:
                    checkpoint_dir.parent.mkdir(parents=True, exist_ok=True)
                else:
                    checkpoint_dir.mkdir(parents=True, exist_ok=True)
                training_section["checkpoint_dir"] = str(checkpoint_dir)

                train_kwargs: dict[str, Any] = {}
                for field in _TrainCfg.__dataclass_fields__:
                    if field in training_section:
                        train_kwargs[field] = training_section[field]
                if "lr" not in train_kwargs:
                    train_kwargs["lr"] = _pop(["learning_rate", "lr"], 5e-4)
                if "batch_size" not in train_kwargs:
                    train_kwargs["batch_size"] = _pop(["batch_size"], 8)
                if "epochs" not in train_kwargs:
                    train_kwargs["epochs"] = _pop(["epochs", "max_epochs"], 1)
                if "grad_accum" not in train_kwargs:
                    train_kwargs["grad_accum"] = _pop(["grad_accum", "gradient_accumulation"], 1)
                train_kwargs.setdefault("checkpoint_dir", str(checkpoint_dir))

                if resume:
                    candidates = sorted(checkpoint_dir.glob("*.pt"))
                    if candidates:
                        latest_ckpt = str(candidates[-1])
                        train_kwargs["resume_from"] = latest_ckpt
                        with contextlib.suppress(Exception):
                            _load_ckpt(latest_ckpt)

                train_cfg = _TrainCfg(**train_kwargs)

                tokenizer = load_from_pretrained(
                    _AutoTokenizer,
                    tokenizer_name,
                )
                if getattr(tokenizer, "pad_token", None) is None:
                    tokenizer.pad_token = tokenizer.eos_token

                tokenized = tokenizer(list(texts), padding=True, return_tensors="pt")
                tokenized["labels"] = tokenized["input_ids"].clone()
                tokenized["labels"][tokenized["attention_mask"] == 0] = -100
                train_ds = _Dataset.from_dict({k: v.numpy() if hasattr(v, "numpy") else _np.array(v) for k, v in tokenized.items()})

                val_ds = None
                if val_texts:
                    val_tok = tokenizer(list(val_texts), padding=True, return_tensors="pt")
                    val_tok["labels"] = val_tok["input_ids"].clone()
                    val_tok["labels"][val_tok["attention_mask"] == 0] = -100
                    val_ds = _Dataset.from_dict({k: v.numpy() if hasattr(v, "numpy") else _np.array(v) for k, v in val_tok.items()})

                model = _get_model(model_cfg.get("name", "MiniLM"), model_cfg)
                return _run_custom_trainer(model, tokenizer, train_ds, val_ds, train_cfg)
            """
        ).strip("\n")

        prefix = source.splitlines()[:start]
        suffix = source.splitlines()[end:]
        new_source = "\n".join(prefix + [new_function] + suffix) + "\n"

        header = (
            "from typing import Any, Mapping\nimport contextlib\nfrom omegaconf import DictConfig\n"
        )
        sentinel = "from __future__ import annotations\n\n"
        if sentinel in new_source:
            new_source = new_source.replace(
                sentinel,
                sentinel + header + "\n",
                1,
            )
        else:
            new_source = "from __future__ import annotations\n\n" + header + "\n" + new_source

        module_path.write_text(new_source, encoding="utf-8")
        log_change("- Added resume support to run_functional_training")
    except Exception as exc:
        log_error(phase, "update_run_functional", exc, f"Updating {module_path}")


def main() -> None:
    phase_preparation()
    phase_search_and_mapping()
    task_create_training_config()
    task_update_cli()
    task_update_run_functional_training()


if __name__ == "__main__":
    main()
