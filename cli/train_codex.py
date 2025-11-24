from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import torch
import yaml
from tokenization.loader import load_tokenizer
from torch.utils.data import Dataset
from transformers import (
    AutoModelForCausalLM,
    DataCollatorForLanguageModeling,
    GPT2Config,
    Trainer,
    TrainingArguments,
)

from codex_ml.utils import checkpointing


@dataclass
class TrainingResult:
    output_dir: Path
    checkpoint_path: Path
    trainer_state_path: Path | None


def _load_config(path: str | Path | None) -> Mapping[str, Any]:
    if path is None:
        return {}
    candidate = Path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Config file not found: {candidate}")
    if candidate.suffix.lower() in {".yaml", ".yml"}:
        return yaml.safe_load(candidate.read_text(encoding="utf-8")) or {}
    return json.loads(candidate.read_text(encoding="utf-8"))


def _merge(namespace: argparse.Namespace, config: Mapping[str, Any]) -> dict[str, Any]:
    merged = {**config}
    for key, value in vars(namespace).items():
        if value is not None:
            merged[key] = value
    return merged


def _build_dataset(tokenizer, train_file: Path, block_size: int) -> Dataset:
    lines = [line.strip() for line in train_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        raise ValueError("Training file is empty")
    encodings = tokenizer(
        lines,
        padding="max_length",
        truncation=True,
        max_length=block_size,
        return_tensors="pt",
    )

    class _LineDataset(Dataset):
        def __len__(self) -> int:
            return len(lines)

        def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
            return {
                "input_ids": encodings["input_ids"][idx],
                "attention_mask": encodings["attention_mask"][idx],
                "labels": encodings["input_ids"][idx],
            }

    return _LineDataset()


def _build_model(config: dict[str, Any], tokenizer) -> AutoModelForCausalLM:
    model_name = config.get("model_name") or config.get("model_name_or_path")
    allow_remote = bool(config.get("allow_remote", False))
    cache_dir = config.get("cache_dir", "artifacts/model_cache")
    if model_name:
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            local_files_only=not allow_remote,
        )
    else:
        model_config = config.get("model_config") or {}
        vocab_size = tokenizer.vocab_size if tokenizer.vocab_size is not None else 256
        hf_config = GPT2Config(
            vocab_size=vocab_size,
            n_embd=model_config.get("hidden_size", 64),
            n_layer=model_config.get("num_layers", 2),
            n_head=model_config.get("num_heads", 2),
        )
        model = AutoModelForCausalLM.from_config(hf_config)
    return model


def _apply_lora_if_requested(model: AutoModelForCausalLM, config: dict[str, Any]) -> AutoModelForCausalLM:
    if not config.get("use_lora"):
        return model
    import importlib.util

    if importlib.util.find_spec("peft") is None:
        raise ImportError("peft is required when --use-lora is enabled")
    from peft import LoraConfig, get_peft_model

    lora_config = LoraConfig(
        r=int(config.get("lora_r", 8)),
        lora_alpha=int(config.get("lora_alpha", 16)),
        target_modules=config.get("lora_target_modules"),
        lora_dropout=float(config.get("lora_dropout", 0.05)),
        bias="none",
        task_type="CAUSAL_LM",
    )
    return get_peft_model(model, lora_config)


def run_training(config: Mapping[str, Any] | None = None) -> TrainingResult:
    cfg: dict[str, Any] = dict(config or {})
    output_dir = Path(cfg.get("output_dir", "artifacts/codex-trainer"))
    output_dir.mkdir(parents=True, exist_ok=True)

    tokenizer_config = {"tokenizer_file": cfg.get("tokenizer_file")}
    if cfg.get("tokenizer_model"):
        tokenizer_config["model_name_or_path"] = cfg["tokenizer_model"]
    tokenizer = load_tokenizer(tokenizer_config, allow_remote=bool(cfg.get("allow_remote", False)))

    max_length = tokenizer.model_max_length or 128
    block_size = int(cfg.get("block_size") or min(max_length, 128))
    train_file = Path(cfg.get("train_file", "data/train.txt"))
    dataset = _build_dataset(tokenizer, train_file, block_size)

    model = _build_model(cfg, tokenizer)
    model = _apply_lora_if_requested(model, cfg)

    training_args = TrainingArguments(
        output_dir=str(output_dir),
        overwrite_output_dir=True,
        num_train_epochs=float(cfg.get("num_train_epochs", 1)),
        per_device_train_batch_size=int(cfg.get("per_device_train_batch_size", 1)),
        learning_rate=float(cfg.get("learning_rate", 5e-4)),
        gradient_accumulation_steps=int(cfg.get("gradient_accumulation_steps", 1)),
        fp16=bool(cfg.get("fp16", False)),
        bf16=bool(cfg.get("bf16", False)),
        max_steps=int(cfg.get("max_steps", -1)),
        logging_steps=1,
        save_steps=int(cfg.get("save_steps", 1) or 1),
        save_total_limit=int(cfg.get("save_total_limit", 2)),
        report_to=[],
        disable_tqdm=True,
    )

    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        tokenizer=tokenizer,
        data_collator=data_collator,
    )

    resume_hf = cfg.get("resume_from_checkpoint")
    if cfg.get("codex_resume_checkpoint"):
        checkpointing.load_training_checkpoint(
            cfg["codex_resume_checkpoint"], model=model, optimizer=None, scheduler=None, strict=False
        )

    trainer.train(resume_from_checkpoint=resume_hf)
    trainer.save_model()

    checkpoint_path = output_dir / "checkpoint-final.pt"
    checkpointing.save_checkpoint(
        checkpoint_path,
        model.state_dict(),
        trainer.optimizer.state_dict() if trainer.optimizer else None,
        trainer.lr_scheduler.state_dict() if trainer.lr_scheduler else None,
        epoch=int(cfg.get("num_train_epochs", 1)),
        dataset_paths=[train_file],
    )

    trainer_state = output_dir / "trainer_state.json"
    return TrainingResult(output_dir=output_dir, checkpoint_path=checkpoint_path, trainer_state_path=trainer_state)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train Codex models with HuggingFace Trainer")
    parser.add_argument("--config", help="YAML/JSON config file", default=None)
    parser.add_argument("--train-file", dest="train_file", help="Path to training text file", default=None)
    parser.add_argument("--output-dir", dest="output_dir", help="Output directory for checkpoints", default=None)
    parser.add_argument("--tokenizer-file", dest="tokenizer_file", help="Tokenizer JSON/vocab file", default=None)
    parser.add_argument("--tokenizer-model", dest="tokenizer_model", help="Tokenizer model name or path", default=None)
    parser.add_argument("--model-name", dest="model_name", help="Model name or path", default=None)
    parser.add_argument("--num-train-epochs", dest="num_train_epochs", type=float, default=None)
    parser.add_argument("--learning-rate", dest="learning_rate", type=float, default=None)
    parser.add_argument("--per-device-train-batch-size", dest="per_device_train_batch_size", type=int, default=None)
    parser.add_argument("--gradient-accumulation-steps", dest="gradient_accumulation_steps", type=int, default=None)
    parser.add_argument("--fp16", action="store_true", help="Enable fp16 training")
    parser.add_argument("--bf16", action="store_true", help="Enable bf16 training")
    parser.add_argument("--max-steps", dest="max_steps", type=int, default=None)
    parser.add_argument("--save-steps", dest="save_steps", type=int, default=None)
    parser.add_argument("--save-total-limit", dest="save_total_limit", type=int, default=None)
    parser.add_argument("--block-size", dest="block_size", type=int, default=None)
    parser.add_argument("--resume-from-checkpoint", dest="resume_from_checkpoint", default=None)
    parser.add_argument("--codex-resume-checkpoint", dest="codex_resume_checkpoint", default=None)
    parser.add_argument("--use-lora", action="store_true", help="Enable LoRA/PEFT wrapping")
    parser.add_argument("--lora-r", dest="lora_r", type=int, default=None)
    parser.add_argument("--lora-alpha", dest="lora_alpha", type=int, default=None)
    parser.add_argument("--lora-dropout", dest="lora_dropout", type=float, default=None)
    parser.add_argument("--lora-target-modules", dest="lora_target_modules", nargs="*", default=None)
    parser.add_argument("--allow-remote", dest="allow_remote", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    config = _load_config(args.config)
    merged = _merge(args, config)
    run_training(merged)


if __name__ == "__main__":
    main()
