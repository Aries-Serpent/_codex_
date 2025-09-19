"""Tokenizer pipeline utilities exposed via the Codex CLI."""

from __future__ import annotations

from dataclasses import asdict, fields
from glob import glob
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

import yaml
from tokenizers import Tokenizer

from tokenization.train_tokenizer import TrainTokenizerConfig, train


class TokenizerPipelineError(RuntimeError):
    """Raised when tokenizer CLI pipeline operations fail."""


def _load_yaml_config(path: Path) -> Dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except FileNotFoundError as exc:  # pragma: no cover - Click handles presentation
        raise TokenizerPipelineError(f"config not found: {path}") from exc
    except yaml.YAMLError as exc:
        raise TokenizerPipelineError(f"failed to parse config {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise TokenizerPipelineError("tokenizer config must be a mapping")
    payload = data.get("tokenization", data)
    if not isinstance(payload, dict):
        raise TokenizerPipelineError("tokenization section must be a mapping")
    return payload


def load_train_config(config_path: str) -> TrainTokenizerConfig:
    """Load ``TrainTokenizerConfig`` from a YAML configuration file."""

    path = Path(config_path)
    payload = _load_yaml_config(path)
    valid_fields = {field.name for field in fields(TrainTokenizerConfig)}
    kwargs = {key: value for key, value in payload.items() if key in valid_fields}
    return TrainTokenizerConfig(**kwargs)


def _resolve_corpus_files(cfg: TrainTokenizerConfig) -> List[str]:
    values = cfg.corpus_glob
    patterns: Iterable[str]
    if isinstance(values, str):
        patterns = (values,)
    else:
        patterns = values
    files: List[str] = []
    for pattern in patterns:
        files.extend(sorted(glob(pattern, recursive=True)))
    return files


def run_train(
    config_path: str,
    *,
    stream_chunk_size: Optional[int] = None,
    dry_run: Optional[bool] = None,
) -> Path:
    """Train a tokenizer according to the provided configuration."""

    cfg = load_train_config(config_path)
    if stream_chunk_size is not None:
        cfg.stream_chunk_size = stream_chunk_size
    if dry_run is not None:
        cfg.dry_run = dry_run
    try:
        return train(cfg)
    except Exception as exc:  # pragma: no cover - surfaced via CLI
        raise TokenizerPipelineError(str(exc)) from exc


def run_validate(config_path: str) -> Dict[str, Any]:
    """Validate configuration and corpus files referenced by ``config_path``."""

    cfg = load_train_config(config_path)
    files = _resolve_corpus_files(cfg)
    if not files:
        raise TokenizerPipelineError("no corpus files resolved; check corpus_glob")
    missing = [path for path in files if not Path(path).exists()]
    out_dir = Path(cfg.out_dir) / cfg.name
    tokenizer_path = out_dir / "tokenizer.json"
    manifest_path = out_dir / "manifest.json"
    return {
        "config": asdict(cfg),
        "files": files,
        "num_files": len(files),
        "missing_files": missing,
        "tokenizer_path": str(tokenizer_path),
        "tokenizer_exists": tokenizer_path.exists(),
        "manifest_exists": manifest_path.exists(),
    }


def _load_tokenizer(path: str) -> Tokenizer:
    tokenizer_path = Path(path)
    if not tokenizer_path.exists():
        raise TokenizerPipelineError(f"tokenizer file not found: {tokenizer_path}")
    try:
        return Tokenizer.from_file(str(tokenizer_path))
    except Exception as exc:  # pragma: no cover - delegated to caller
        raise TokenizerPipelineError(f"failed to load tokenizer {tokenizer_path}: {exc}") from exc


def run_encode(tokenizer_path: str, text: str) -> List[int]:
    """Encode ``text`` using the tokenizer at ``tokenizer_path``."""

    tokenizer = _load_tokenizer(tokenizer_path)
    try:
        return tokenizer.encode(text).ids
    except Exception as exc:  # pragma: no cover - delegated to caller
        raise TokenizerPipelineError(f"encoding failed: {exc}") from exc


def run_decode(tokenizer_path: str, token_ids: Sequence[int]) -> str:
    """Decode ``token_ids`` using the tokenizer at ``tokenizer_path``."""

    tokenizer = _load_tokenizer(tokenizer_path)
    try:
        return tokenizer.decode(list(token_ids), skip_special_tokens=False)
    except Exception as exc:  # pragma: no cover - delegated to caller
        raise TokenizerPipelineError(f"decoding failed: {exc}") from exc


__all__ = [
    "TokenizerPipelineError",
    "load_train_config",
    "run_train",
    "run_validate",
    "run_encode",
    "run_decode",
]
