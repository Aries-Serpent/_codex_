from __future__ import annotations

import hashlib
import json
import random
import sys
import warnings
from dataclasses import asdict, dataclass
from glob import glob
from pathlib import Path
from typing import Iterable, List, Sequence

from ingestion import ingest

try:  # pragma: no cover - optional dependency
    import hydra
    from omegaconf import MISSING
except Exception:  # pragma: no cover - optional dependency
    hydra = None  # type: ignore
    MISSING = object()  # type: ignore

try:  # pragma: no cover - optional dependency
    import sentencepiece as spm
except Exception as exc:  # pragma: no cover
    spm = None
    _SPM_ERROR = exc
else:  # pragma: no cover - import succeeded
    _SPM_ERROR = None

from tokenizers import (
    SentencePieceUnigramTokenizer,
    Tokenizer,
    models,
    normalizers,
    pre_tokenizers,
    trainers,
)

DEFAULT_STREAM_CHUNK_SIZE = 1024 * 1024  # 1 MiB chunks by default


@dataclass
class TrainTokenizerConfig:
    corpus_glob: Sequence[str] | str = MISSING  # type: ignore[assignment]
    model_type: str = "unigram"  # "bpe" or "unigram"
    vocab_size: int = 8000
    character_coverage: float = 0.9995
    normalization_rule: str | None = None
    seed: int = 42
    workers: int = 4
    out_dir: str = "artifacts/tokenizers/default"
    name: str = "default"
    dry_run: bool = False
    stream_chunk_size: int | None = None


def _expand_files(patterns: Sequence[str] | str) -> List[str]:
    pats = [patterns] if isinstance(patterns, str) else list(patterns)
    files: List[str] = []
    for pat in pats:
        files.extend(sorted(glob(pat, recursive=True)))
    return files


def _iter_text(files: Sequence[str], cfg: TrainTokenizerConfig) -> Iterable[str]:
    configured_chunk = cfg.stream_chunk_size
    if configured_chunk is not None:
        if configured_chunk <= 0:
            raise ValueError("stream_chunk_size must be a positive integer")
        chunk_size = configured_chunk
    else:
        chunk_size = DEFAULT_STREAM_CHUNK_SIZE
    for path in files:
        txt = ingest(path, encoding="auto", chunk_size=chunk_size)
        if isinstance(txt, str):
            yield txt
        else:
            yield from txt


def train(cfg: TrainTokenizerConfig) -> Path:
    files = _expand_files(cfg.corpus_glob)
    if not files:
        patterns = [cfg.corpus_glob] if isinstance(cfg.corpus_glob, str) else list(cfg.corpus_glob)
        raise FileNotFoundError(
            "No training files found for tokenizer training. " f"Checked patterns: {patterns}"
        )
    if cfg.dry_run:
        print("Training plan:")
        print(json.dumps({"config": asdict(cfg), "files": files}, indent=2))
        return Path(cfg.out_dir) / cfg.name

    random.seed(cfg.seed)
    out_dir = Path(cfg.out_dir) / cfg.name
    out_dir.mkdir(parents=True, exist_ok=True)

    tokenizer_path = out_dir / "tokenizer.json"

    if cfg.model_type.lower() == "unigram":
        if spm is None:  # pragma: no cover - dependency missing
            raise ImportError("sentencepiece is not installed") from _SPM_ERROR
        model_prefix = out_dir / "spm"
        train_kwargs = {
            "input": ",".join(files),
            "model_prefix": str(model_prefix),
            "vocab_size": cfg.vocab_size,
            "character_coverage": cfg.character_coverage,
            "model_type": "unigram",
            "seed_sentencepiece": cfg.seed,
            "num_threads": cfg.workers,
            "shuffle_input_sentence": False,
            "normalization_rule_name": cfg.normalization_rule or "nmt_nfkc_cf",
            "hard_vocab_limit": False,
            "pad_id": 0,
            "unk_id": 1,
            "bos_id": 2,
            "eos_id": 3,
            "pad_piece": "[PAD]",
            "unk_piece": "[UNK]",
            "bos_piece": "[BOS]",
            "eos_piece": "[EOS]",
        }
        try:
            spm.SentencePieceTrainer.Train(**train_kwargs)
        except OSError as exc:
            if "seed_sentencepiece" not in str(exc):
                raise
            train_kwargs.pop("seed_sentencepiece", None)
            warnings.warn("sentencepiece trainer does not support seed_sentencepiece; falling back")
            spm.SentencePieceTrainer.Train(**train_kwargs)
        model_path = model_prefix.with_suffix(".model")
        if "sentencepiece_model_pb2" not in sys.modules:
            try:  # pragma: no cover - optional dependency handling
                import sentencepiece_model_pb2  # type: ignore # noqa: F401
            except Exception:
                try:
                    from sentencepiece import sentencepiece_model_pb2 as _sp_model_pb2
                except Exception:  # pragma: no cover - dependency still missing
                    _sp_model_pb2 = None
                else:
                    sys.modules.setdefault("sentencepiece_model_pb2", _sp_model_pb2)
        tok = SentencePieceUnigramTokenizer.from_spm(str(model_path))
        tok.save(str(tokenizer_path))
    else:
        tokenizer = Tokenizer(models.BPE(unk_token="[UNK]"))
        tokenizer.normalizer = normalizers.NFKC()
        tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel()
        trainer = trainers.BpeTrainer(
            vocab_size=cfg.vocab_size,
            special_tokens=["[PAD]", "[UNK]", "[BOS]", "[EOS]"],
        )
        tokenizer.train_from_iterator(_iter_text(files, cfg), trainer=trainer)
        tokenizer.save(str(tokenizer_path))

    sha = hashlib.sha256(tokenizer_path.read_bytes()).hexdigest()
    manifest = {
        "config": asdict(cfg),
        "hash": sha,
        "command": " ".join(sys.argv),
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), "utf-8")
    return out_dir


if hydra is not None:  # pragma: no cover - optional dependency

    @hydra.main(config_path="../../configs", config_name="tokenization/base", version_base=None)
    def main(cfg: TrainTokenizerConfig) -> None:  # type: ignore[misc]
        train(cfg)

else:  # pragma: no cover - fallback when hydra missing

    def main() -> None:  # type: ignore[override]
        cfg = TrainTokenizerConfig(corpus_glob="")
        train(cfg)


__all__ = ["TrainTokenizerConfig", "train", "main"]
