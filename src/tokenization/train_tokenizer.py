from __future__ import annotations

import hashlib
import json
import random
import sys
import warnings
from dataclasses import asdict, dataclass
from glob import glob
from pathlib import Path
from typing import Callable, Iterable, Iterator, List, Optional, Sequence, Tuple, Union

from ingestion import ingest

try:  # pragma: no cover - optional dependency
    import hydra
    from omegaconf import MISSING
except Exception:  # pragma: no cover - optional dependency
    hydra = None  # type: ignore
    MISSING = object()  # type: ignore


if hydra is not None:
    _HYDRA_AVAILABLE = any(
        callable(getattr(hydra, attr, None))
        for attr in ("compose", "initialize", "initialize_config_dir")
    )
else:
    _HYDRA_AVAILABLE = False

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

DEFAULT_STREAM_CHUNK_SIZE = 1024 * 1024  # 1 MiB chunks when streaming


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
    streaming: bool = False
    stream_chunk_size: int | None = None


def _expand_files(patterns: Sequence[str] | str) -> List[str]:
    pats = [patterns] if isinstance(patterns, str) else list(patterns)
    files: List[str] = []
    for pat in pats:
        files.extend(sorted(glob(pat, recursive=True)))
    return files


def _resolve_streaming_options(cfg: TrainTokenizerConfig) -> Tuple[bool, Optional[int]]:
    streaming = bool(cfg.streaming or cfg.stream_chunk_size is not None)
    chunk_size = cfg.stream_chunk_size
    if chunk_size is not None and chunk_size <= 0:
        raise ValueError("stream_chunk_size must be a positive integer")
    if streaming and chunk_size is None:
        chunk_size = DEFAULT_STREAM_CHUNK_SIZE
    return streaming, chunk_size


def _yield_lines(source: Union[str, Iterable[str]]) -> Iterator[str]:
    if isinstance(source, str):
        yield source
        return

    buffer = ""
    for chunk in source:
        buffer += chunk.replace("\r\n", "\n").replace("\r", "\n")
        while True:
            newline_index = buffer.find("\n")
            if newline_index == -1:
                break
            line = buffer[: newline_index + 1]
            yield line
            buffer = buffer[newline_index + 1 :]
    if buffer:
        yield buffer


def _iter_text(files: Sequence[str], cfg: TrainTokenizerConfig) -> Iterable[str]:
    _, chunk_size = _resolve_streaming_options(cfg)
    for path in files:
        streamed = ingest(path, encoding="auto", chunk_size=chunk_size)
        yield from _yield_lines(streamed)


def _spm_sentence_iterator(files: Sequence[str], *, chunk_size: int) -> Iterable[str]:
    for path in files:
        file_path = Path(path)
        with file_path.open("r", encoding="utf-8", errors="replace") as fh:
            buffer = ""
            while True:
                chunk = fh.read(chunk_size)
                if not chunk:
                    break
                buffer += chunk.replace("\r\n", "\n").replace("\r", "\n")
                while True:
                    newline_index = buffer.find("\n")
                    if newline_index == -1:
                        break
                    yield buffer[: newline_index + 1]
                    buffer = buffer[newline_index + 1 :]
            if buffer:
                yield buffer
                buffer = ""


def train(cfg: TrainTokenizerConfig) -> Path:
    files = _expand_files(cfg.corpus_glob)
    if not files:
        patterns = [cfg.corpus_glob] if isinstance(cfg.corpus_glob, str) else list(cfg.corpus_glob)
        raise FileNotFoundError(
            "No training files found for tokenizer training. " f"Checked patterns: {patterns}"
        )
    streaming_enabled, chunk_size = _resolve_streaming_options(cfg)
    cfg.streaming = streaming_enabled
    cfg.stream_chunk_size = chunk_size
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
        sentence_iterator_factory: Callable[[], Iterable[str]] | None = None
        if streaming_enabled:
            if chunk_size is None:
                raise RuntimeError("chunk_size must be resolved when streaming is enabled")

            def sentence_iterator_factory() -> Iterable[str]:
                return _spm_sentence_iterator(files, chunk_size=chunk_size)

            train_kwargs["sentence_iterator"] = sentence_iterator_factory()
        else:
            train_kwargs["input"] = ",".join(files)
        try:
            spm.SentencePieceTrainer.Train(**train_kwargs)
        except OSError as exc:
            if "seed_sentencepiece" not in str(exc):
                raise
            train_kwargs.pop("seed_sentencepiece", None)
            warnings.warn("sentencepiece trainer does not support seed_sentencepiece; falling back")
            if streaming_enabled and sentence_iterator_factory is not None:
                train_kwargs["sentence_iterator"] = sentence_iterator_factory()
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
        try:
            tok = SentencePieceUnigramTokenizer.from_spm(str(model_path))
        except Exception:
            processor = spm.SentencePieceProcessor()
            processor.Load(str(model_path))
            tok = SentencePieceUnigramTokenizer.from_spm(processor)
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


if _HYDRA_AVAILABLE:  # pragma: no cover - optional dependency

    @hydra.main(config_path="../../configs", config_name="tokenization/base", version_base=None)
    def main(cfg: TrainTokenizerConfig) -> None:  # type: ignore[misc]
        train(cfg)

else:  # pragma: no cover - fallback when hydra missing

    def main() -> None:  # type: ignore[override]
        cfg = TrainTokenizerConfig(corpus_glob="")
        train(cfg)


__all__ = ["TrainTokenizerConfig", "train", "main"]
