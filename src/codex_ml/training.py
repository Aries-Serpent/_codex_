"""Compatibility wrapper for :mod:`codex_ml.training` package exports."""

from __future__ import annotations

import sys
from pathlib import Path

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
                        "rules": list(exc.decision.blocked_rules),
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
