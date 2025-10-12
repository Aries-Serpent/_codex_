from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import hydra
from common.mlflow_guard import ensure_local_tracking, log_artifacts_safe, start_run_with_tags
from common.randomness import set_seed
from hhg_logistics.model.peft_utils import (
    apply_lora,
    freeze_base_weights,
    load_hf_llm,
    tokenize_for_causal_lm,
)
from hydra.utils import to_absolute_path
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


def _train_loop(model, dataloader, epochs: int, lr: float, log_every_n: int = 1):
    if torch is None or AdamW is None:
        logger.warning("Torch not available; skipping training loop.")
        return {"loss": None}

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    model.train()
    optimiser = AdamW(model.parameters(), lr=lr)
    global_step = 0
    last_loss = None

    for _ in range(epochs):  # pragma: no branch - simple outer loop
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

        features_csv = Path(to_absolute_path(str(cfg.pipeline.features.output_path)))
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
            )
        logger.info("Training metrics: %s", metrics)

        save_dir_value = getattr(cfg.train, "save_dir", None)
        if save_dir_value is None:
            models_dir = getattr(cfg.data, "models_dir", "data/models")
            save_dir_value = Path(models_dir) / "baseline"
        output_dir = Path(to_absolute_path(str(save_dir_value)))
        save_adapters = bool(getattr(cfg.train, "save_adapters", True))
        _save_adapters(model, output_dir, save_adapters=save_adapters)
        logger.info("Saved adapters (if any) to %s", output_dir)

        log_artifacts_safe({"adapters": output_dir})
        return {"save_dir": str(output_dir), "loss": metrics.get("loss")}


if __name__ == "__main__":
    main()
