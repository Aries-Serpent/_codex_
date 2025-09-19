"""Tokenizer pipeline utilities exposed via the Codex CLI."""

from __future__ import annotations

import json
from dataclasses import asdict, fields
from glob import glob
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import yaml
from tokenizers import Tokenizer

from .sentencepiece_adapter import SentencePieceAdapter
from .train_tokenizer import TrainTokenizerConfig, train


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
    try:
        return TrainTokenizerConfig(**kwargs)
    except TypeError as exc:
        raise TokenizerPipelineError(f"invalid tokenizer config: {exc}") from exc


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
    streaming: Optional[bool] = None,
    stream_chunk_size: Optional[int] = None,
    dry_run: Optional[bool] = None,
) -> Path:
    """Train a tokenizer according to the provided configuration."""

    cfg = load_train_config(config_path)
    if streaming is not None:
        cfg.streaming = streaming
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
    tokenizer_path = _normalise_tokenizer_path(out_dir / "tokenizer.json")
    manifest_path = out_dir / "manifest.json"
    provenance_dir = out_dir / "provenance"
    manifest: Optional[Dict[str, Any]] = None
    manifest_error: Optional[str] = None
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            manifest_error = f"failed to parse manifest.json: {exc}"
    return {
        "config": asdict(cfg),
        "files": files,
        "num_files": len(files),
        "missing_files": missing,
        "tokenizer_path": str(tokenizer_path),
        "tokenizer_exists": tokenizer_path.exists(),
        "manifest_path": str(manifest_path),
        "manifest_exists": manifest_path.exists(),
        "manifest": manifest,
        "manifest_error": manifest_error,
        "provenance_path": str(provenance_dir),
        "provenance_exists": provenance_dir.exists(),
    }


def _normalise_tokenizer_path(path: Path) -> Path:
    """Resolve ``path`` to a concrete tokenizer file.

    ``tokenizers.Tokenizer`` expects a JSON file.  Some workflows pass a
    directory containing ``tokenizer.json`` or a raw SentencePiece ``.model``
    file.  This helper resolves those inputs into a single ``Path`` so calling
    code can focus on IO rather than format quirks.
    """

    target = Path(path)
    if target.is_dir():
        json_path = target / "tokenizer.json"
        if json_path.exists():
            return json_path
        model_path = target / "tokenizer.model"
        if model_path.exists():
            return model_path
    if target.suffix:
        if target.exists():
            return target
        alt_json = target.with_suffix(".json")
        if alt_json.exists():
            return alt_json
        alt_model = target.with_suffix(".model")
        if alt_model.exists():
            return alt_model
    else:
        json_path = target.with_suffix(".json")
        if json_path.exists():
            return json_path
        model_path = target.with_suffix(".model")
        if model_path.exists():
            return model_path
    return target


def _load_sentencepiece_tokenizer(path: Path) -> SentencePieceAdapter:
    try:
        adapter = SentencePieceAdapter(path)
    except ImportError as exc:  # pragma: no cover - dependency missing
        raise TokenizerPipelineError(
            "loading SentencePiece models requires the optional 'sentencepiece' dependency"
        ) from exc
    return adapter.load()


def _load_tokenizer(path: str) -> Tuple[str, object]:
    tokenizer_path = _normalise_tokenizer_path(Path(path))
    if not tokenizer_path.exists():
        raise TokenizerPipelineError(f"tokenizer file not found: {tokenizer_path}")
    suffix = tokenizer_path.suffix.lower()
    if suffix == ".json":
        try:
            tokenizer = Tokenizer.from_file(str(tokenizer_path))
        except Exception as exc:  # pragma: no cover - delegated to caller
            raise TokenizerPipelineError(
                f"failed to load tokenizer {tokenizer_path}: {exc}"
            ) from exc
        return "hf", tokenizer
    if suffix == ".model":
        adapter = _load_sentencepiece_tokenizer(tokenizer_path)
        return "spm", adapter
    raise TokenizerPipelineError(
        f"unsupported tokenizer format for {tokenizer_path}; expected .json or .model"
    )


def run_encode(tokenizer_path: str, text: str) -> List[int]:
    """Encode ``text`` using the tokenizer at ``tokenizer_path``."""

    kind, tokenizer = _load_tokenizer(tokenizer_path)
    try:
        if kind == "hf":
            return tokenizer.encode(text).ids  # type: ignore[operator]
        encoded = tokenizer.encode(text)
        return list(encoded)
    except Exception as exc:  # pragma: no cover - delegated to caller
        raise TokenizerPipelineError(f"encoding failed: {exc}") from exc


def run_decode(tokenizer_path: str, token_ids: Sequence[int]) -> str:
    """Decode ``token_ids`` using the tokenizer at ``tokenizer_path``."""

    kind, tokenizer = _load_tokenizer(tokenizer_path)
    try:
        if kind == "hf":
            return tokenizer.decode(list(token_ids), skip_special_tokens=False)  # type: ignore[call-arg]
        return tokenizer.decode(list(token_ids))
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
