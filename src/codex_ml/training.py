from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

from codex_ml.safety import SafetyConfig, SafetyFilters, SafetyViolation, sanitize_prompt
from codex_ml.utils.checkpointing import CheckpointManager
from codex_ml.utils.error_log import log_error
from codex_ml.utils.provenance import export_environment
from codex_ml.utils.seeding import set_reproducible


class _SimpleModel:

    def __init__(self) -> None:
        self.step = 0

    def state_dict(self) -> Dict[str, Any]:
        return {"step": self.step}

    def load_state_dict(self, state: Mapping[str, Any]) -> None:
        self.step = int(state.get("step", 0))


class _SimpleOptimizer:

    def __init__(self) -> None:
        self.state: Dict[str, Any] = {}

    def state_dict(self) -> Dict[str, Any]:
        return {"state": dict(self.state)}

    def load_state_dict(self, state: Mapping[str, Any]) -> None:
        self.state = dict(state.get("state", {}))


class _SimpleScheduler(_SimpleOptimizer):
    """Scheduler stub sharing persistence helpers."""

    pass


@dataclass
class SafetySettings:
    enabled: bool = True
    policy_path: str | None = None
    bypass: bool = False


@dataclass
class TrainingRunConfig:
    seed: int = 42
    model: str = "minilm"
    learning_rate: float = 0.0003
    batch_size: int = 32
    max_epochs: int = 5
    scheduler: str = "linear"
    warmup_steps: int = 0
    gradient_accumulation: int = 1
    tensorboard: bool = True
    mlflow_enable: bool = False
    output_dir: str = "runs/default"
    checkpoint_every_n_steps: int = 100
    dataset: Dict[str, Any] = field(
        default_factory=lambda: {
            "train_path": "data/train_samples.jsonl",
            "eval_path": None,
            "format": "jsonl",
        }
    )
    safety: SafetySettings = field(default_factory=SafetySettings)


def _load_texts(path: str | None, fmt: str = "text") -> List[str]:
    if not path:
        return []
    target = Path(path)
    if not target.exists():
        return []
    fmt_lower = fmt.lower()
    texts: List[str] = []
    if fmt_lower == "jsonl":
        for line in target.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                texts.append(line)
                continue
            if isinstance(item, dict) and "text" in item:
                texts.append(str(item["text"]))
            elif isinstance(item, str):
                texts.append(item)
            else:
                texts.append(line if isinstance(item, (int, float)) else json.dumps(item))
        return texts
    for line in target.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            texts.append(line)
    return texts


def _coerce_safety(raw: Mapping[str, Any] | SafetySettings | None) -> SafetySettings:
    if isinstance(raw, SafetySettings):
        return raw
    base = SafetySettings()
    if not isinstance(raw, Mapping):
        return base
    policy = raw.get("policy_path", base.policy_path)
    policy_path = str(policy) if policy not in (None, "") else None
    return SafetySettings(
        enabled=bool(raw.get("enabled", base.enabled)),
        policy_path=policy_path,
        bypass=bool(raw.get("bypass", base.bypass)),
    )

from __future__ import annotations

import importlib

try:  # pragma: no cover - imported as part of package
    from .training import SafetySettings, TrainingRunConfig, run_functional_training
except ImportError:  # pragma: no cover - imported via file path in tests
    _pkg = importlib.import_module("codex_ml.training")
    SafetySettings = _pkg.SafetySettings
    TrainingRunConfig = _pkg.TrainingRunConfig
    run_functional_training = _pkg.run_functional_training

def run_functional_training(
    config: Mapping[str, Any] | TrainingRunConfig, *, resume: bool = False
) -> Dict[str, Any]:
    """Run a lightweight training loop with checkpointing support."""
    cfg = config if isinstance(config, TrainingRunConfig) else _coerce_config(dict(config))
    set_reproducible(cfg.seed)
    train_texts = _load_texts(cfg.dataset.get("train_path"), cfg.dataset.get("format", "text"))
    if not train_texts:
        msg = "training dataset is empty or missing"
        log_error("train.dataset", msg, json.dumps({"path": cfg.dataset.get("train_path")}))
        raise ValueError(msg)
    safety_filters: SafetyFilters | None = None
    safety_cfg = cfg.safety
    prompt_cfg = SafetyConfig()
    sanitised_texts: List[str] = []
    for text in train_texts:
        prompt_result = sanitize_prompt(text, prompt_cfg)
        sanitised = prompt_result["text"]
        if safety_cfg.enabled:
            safety_filters = safety_filters or SafetyFilters.from_policy_file(
                safety_cfg.policy_path
            )
            try:
                sanitised = safety_filters.enforce(
                    sanitised, stage="prompt", bypass=safety_cfg.bypass
                )
            except SafetyViolation as exc:
                ctx = json.dumps(
                    {
                        "stage": "prompt",
                        "matches": exc.decision.matches,
                        "policy": str(safety_filters.policy_path) if safety_filters else None,
                    }
                )
                log_error("train.safety", str(exc), ctx)
                raise
        sanitised_texts.append(sanitised)
    train_texts = sanitised_texts
    output_dir = Path(cfg.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    export_environment(
        output_dir / "provenance",
        seed=cfg.seed,
        command="train",
        extras={"resume": bool(resume)},
    )
    checkpoint_root = output_dir / "checkpoints"
    checkpoint_root.mkdir(parents=True, exist_ok=True)
    model = _SimpleModel()
    optimizer = _SimpleOptimizer()
    scheduler = _SimpleScheduler()
    manager = CheckpointManager(checkpoint_root, keep_last=max(cfg.max_epochs, 1), keep_best=1)
    start_epoch = 0
    resumed_from = None
    if resume:
        marker = checkpoint_root / "last"
        if marker.exists():
            try:
                resume_path = Path(marker.read_text(encoding="utf-8").strip())
                if resume_path.exists():
                    manager.resume_from(
                        resume_path, model=model, optimizer=optimizer, scheduler=scheduler
                    )
                    resumed_from = resume_path
                    try:
                        start_epoch = int(resume_path.name.split("-")[-1]) + 1
                    except ValueError:
                        start_epoch = 0
            except Exception as exc:
                log_error(
                    "train.resume",
                    f"{exc.__class__.__name__}: {exc}",
                    json.dumps({"path": str(locals().get("resume_path", ""))}),
                )
    metrics: List[Dict[str, Any]] = []
    last_checkpoint: Optional[Path] = None
    total_tokens = sum((len(text.split()) for text in train_texts))
    for epoch in range(start_epoch, cfg.max_epochs):
        model.step += len(train_texts)
        metric = {"epoch": epoch, "tokens": total_tokens, "loss": round(1.0 / (epoch + 1), 4)}
        metrics.append(metric)
        last_checkpoint = manager.save(
            epoch,
            model=model,
            optimizer=optimizer,
            scheduler=scheduler,
            config={
                "seed": cfg.seed,
                "model": cfg.model,
                "learning_rate": cfg.learning_rate,
                "batch_size": cfg.batch_size,
            },
            metrics=metric,
        )
    return {
        "metrics": metrics,
        "checkpoint_dir": str(last_checkpoint) if last_checkpoint else None,
        "resumed_from": str(resumed_from) if resumed_from else None,
    }
