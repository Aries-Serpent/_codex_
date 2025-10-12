from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import hydra
from common.hooks import CheckpointHook, EMAHook, HookManager, NDJSONLogHook
from common.mlflow_guard import ensure_local_tracking, log_artifacts_safe, start_run_with_tags
from common.randomness import set_seed
from hhg_logistics.model.peft_utils import (
    apply_lora,
    freeze_base_weights,
    load_hf_llm,
    tokenize_for_causal_lm,
)
from hhg_logistics.plugins import load_plugins
from omegaconf import DictConfig, OmegaConf

logger = logging.getLogger(__name__)

try:  # pragma: no cover - optional dependency
    import torch
    from torch.optim import AdamW
    from torch.utils.data import DataLoader, Dataset
except Exception:  # pragma: no cover
    torch = None  # type: ignore
    AdamW = None  # type: ignore
    DataLoader = None  # type: ignore
    Dataset = object  # type: ignore

try:  # pragma: no cover - optional dependency
    import pandas as pd
except Exception:  # pragma: no cover
    pd = None  # type: ignore


class ToyTextDataset(Dataset):  # type: ignore[misc]
    def __init__(self, texts: list[str], tokenizer, max_length: int = 64):
        encodings, labels = tokenize_for_causal_lm(tokenizer, texts, max_length=max_length)
        self.encodings = encodings
        self.labels = labels

    def __len__(self) -> int:  # pragma: no cover - trivial
        return int(self.encodings["input_ids"].shape[0])

    def __getitem__(self, idx: int) -> dict[str, Any]:
        item = {key: value[idx] for key, value in self.encodings.items()}
        item["labels"] = self.labels[idx]
        return item


def _make_texts_from_features_csv(csv_path: Path, id_col: str, value_col: str) -> list[str]:
    if pd is None:
        raise RuntimeError("pandas missing")

    if not csv_path.exists():
        logger.warning("features.csv not found at %s; using fallback texts", csv_path)
        return ["Hello world."] * 8

    df = pd.read_csv(csv_path)
    texts: list[str] = []
    for _, row in df.iterrows():
        rid = str(row[id_col])
        val = str(row[value_col])
        even_flag = row.get("value_is_even", "")
        even_str = "even" if str(even_flag).lower() in {"true", "1"} or even_flag == 1 else "odd"
        texts.append(f"Item {rid}: value {val} is {even_str}.")
    if not texts:
        texts = ["Hello world."] * 8
    return texts


def _build_hook_manager(hooks_cfg: DictConfig | None) -> HookManager:
    manager = HookManager([])
    if hooks_cfg is None or not bool(getattr(hooks_cfg, "enable", True)):
        return manager

    try:
        if getattr(hooks_cfg, "ema", None) and bool(getattr(hooks_cfg.ema, "enable", False)):
            manager.add(EMAHook(decay=float(getattr(hooks_cfg.ema, "decay", 0.999))))
    except Exception:  # pragma: no cover - best effort
        logger.warning("Failed to configure EMA hook", exc_info=True)

    try:
        if getattr(hooks_cfg, "checkpoint", None) and bool(
            getattr(hooks_cfg.checkpoint, "enable", False)
        ):
            manager.add(
                CheckpointHook(
                    every_steps=int(getattr(hooks_cfg.checkpoint, "every_steps", 10)),
                    out_dir=str(
                        getattr(hooks_cfg.checkpoint, "out_dir", "data/models/checkpoints")
                    ),
                )
            )
    except Exception:  # pragma: no cover
        logger.warning("Failed to configure checkpoint hook", exc_info=True)

    try:
        ndjson_cfg = getattr(hooks_cfg, "ndjson_log", None)
        if ndjson_cfg is None:
            ndjson_cfg = getattr(hooks_cfg, "log", None)
        if ndjson_cfg is not None and bool(getattr(ndjson_cfg, "enable", True)):
            manager.add(
                NDJSONLogHook(file=str(getattr(ndjson_cfg, "file", ".codex/metrics/train.ndjson")))
            )
    except Exception:  # pragma: no cover
        logger.warning("Failed to configure NDJSON log hook", exc_info=True)

    return manager


def _train_loop(
    model,
    dataloader,
    epochs: int,
    lr: float,
    log_every_n: int = 1,
    hooks_cfg: DictConfig | None = None,
):
    if torch is None or AdamW is None:
        logger.warning("Torch not available; skipping training loop.")
        return {"loss": None}

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    model.train()
    optimiser = AdamW(model.parameters(), lr=lr)
    global_step = 0
    last_loss = None

    hooks = _build_hook_manager(hooks_cfg)
    state = {"model": model, "global_step": global_step, "epoch": 0, "last_loss": last_loss}
    hooks.dispatch("on_init", state)

    for epoch in range(epochs):  # pragma: no branch - simple outer loop
        state["epoch"] = epoch
        for batch in dataloader:
            batch = {key: value.to(device) for key, value in batch.items()}
            outputs = model(**batch)
            loss = outputs.loss
            loss.backward()
            optimiser.step()
            optimiser.zero_grad()
            global_step += 1
            last_loss = float(loss.detach().cpu().item())
            if log_every_n and global_step % log_every_n == 0:
                logger.info("step=%s loss=%.4f", global_step, last_loss)
            state.update({"global_step": global_step, "last_loss": last_loss})
            hooks.dispatch("on_step_end", state)
            hooks.dispatch("on_checkpoint", state)
        hooks.dispatch("on_epoch_end", state)
    hooks.dispatch("on_finish", state)
    return {"loss": last_loss}


def _save_adapters(model, out_dir: Path, save_adapters: bool = True) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    if not save_adapters:
        return
    if hasattr(model, "save_pretrained"):
        try:  # pragma: no cover - optional path
            model.save_pretrained(str(out_dir))
        except Exception as exc:  # pragma: no cover
            logger.warning("Saving adapters failed: %s", exc)


def _resolve_model_value(model_cfg: DictConfig, key: str, default: Any = None):
    for path in (key, f"model.{key}"):
        value = OmegaConf.select(model_cfg, path)
        if value is not None:
            return value
    return default


def _peft_config(cfg: DictConfig) -> DictConfig:
    for path in ("peft", "model.peft", "model.model.peft"):
        value = OmegaConf.select(cfg, path)
        if value is None:
            continue
        if isinstance(value, DictConfig):
            return value
        if isinstance(value, dict):
            return DictConfig(value)
    return DictConfig({})


@hydra.main(config_path="conf", config_name="config", version_base="1.3")
def main(cfg: DictConfig):
    if not bool(getattr(cfg.train, "enable", False)):
        logger.info("train.enable is false; skipping training.")
        return {}

    if torch is None:
        logger.warning("Torch not available; skipping training run.")
        return {}

    seed_value = int(getattr(cfg.train, "seed", getattr(cfg, "seed", 0)))
    set_seed(seed_value)
    ensure_local_tracking(cfg)

    if "plugins" in cfg and bool(getattr(cfg.plugins, "enable", False)):
        modules = list(getattr(cfg.plugins, "modules", []))
        if modules:
            load_plugins(modules)

    with start_run_with_tags(cfg, run_name="train"):
        pretrained = _resolve_model_value(cfg.model, "pretrained", default="sshleifer/tiny-gpt2")
        tokenizer_name = _resolve_model_value(cfg.model, "tokenizer", default=pretrained)
        dtype = _resolve_model_value(cfg.model, "dtype", default="float32")
        trust_remote_code = bool(
            _resolve_model_value(cfg.model, "trust_remote_code", default=False)
        )
        low_cpu_mem_usage = bool(_resolve_model_value(cfg.model, "low_cpu_mem_usage", default=True))

        if pretrained in (None, "None"):
            pretrained = "sshleifer/tiny-gpt2"

        bundle = load_hf_llm(
            pretrained=str(pretrained),
            tokenizer_name=str(tokenizer_name) if tokenizer_name is not None else None,
            dtype=str(dtype),
            trust_remote_code=trust_remote_code,
            low_cpu_mem_usage=low_cpu_mem_usage,
        )
        model, tokenizer = bundle.model, bundle.tokenizer

        peft_cfg = _peft_config(cfg)
        if bool(getattr(peft_cfg, "enable", True)):
            model = apply_lora(
                model,
                r=int(getattr(peft_cfg, "lora_r", 8)),
                alpha=int(getattr(peft_cfg, "lora_alpha", 16)),
                dropout=float(getattr(peft_cfg, "lora_dropout", 0.05)),
            )

        if bool(getattr(cfg.train, "freeze_base", True)):
            freeze_base_weights(model)

        features_csv = Path(cfg.pipeline.features.output_path)
        id_column = str(getattr(cfg.train, "id_column", "id"))
        value_column = str(getattr(cfg.train, "value_column", "value"))
        texts = _make_texts_from_features_csv(
            features_csv, id_col=id_column, value_col=value_column
        )

        dataset = ToyTextDataset(texts, tokenizer=tokenizer, max_length=64)
        if DataLoader is None:
            logger.warning("torch DataLoader unavailable; skipping training loop.")
            metrics = {"loss": None}
        else:
            batch_size = int(getattr(cfg.train, "batch_size", 4))
            dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
            metrics = _train_loop(
                model=model,
                dataloader=dataloader,
                epochs=int(getattr(cfg.train, "epochs", 1)),
                lr=float(getattr(cfg.train, "lr", 5e-4)),
                log_every_n=int(getattr(cfg.train, "log_every_n", 1)),
                hooks_cfg=getattr(cfg, "hooks", None),
            )
        logger.info("Training metrics: %s", metrics)

        output_dir = Path(getattr(cfg.train, "save_dir", Path(cfg.data.models_dir) / "baseline"))
        save_adapters = bool(getattr(cfg.train, "save_adapters", True))
        _save_adapters(model, output_dir, save_adapters=save_adapters)
        logger.info("Saved adapters (if any) to %s", output_dir)

        log_artifacts_safe({"adapters": output_dir})
        return {"save_dir": str(output_dir), "loss": metrics.get("loss")}


if __name__ == "__main__":
    main()
