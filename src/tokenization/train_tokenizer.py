from __future__ import annotations

import hashlib
import json
import random
import sys
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


def _expand_files(patterns: Sequence[str] | str) -> List[str]:
    pats = [patterns] if isinstance(patterns, str) else list(patterns)
    files: List[str] = []
    for pat in pats:
        files.extend(sorted(glob(pat, recursive=True)))
    return files


def _iter_text(files: Sequence[str]) -> Iterable[str]:
    for path in files:
        txt = ingest(path, encoding="auto")
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
        spm.SentencePieceTrainer.Train(
            input=",".join(files),
            model_prefix=str(model_prefix),
            vocab_size=cfg.vocab_size,
            character_coverage=cfg.character_coverage,
            model_type="unigram",
            seed_sentencepiece=cfg.seed,
            num_threads=cfg.workers,
            shuffle_input_sentence=False,
            normalization_rule_name=cfg.normalization_rule or "nmt_nfkc_cf",
            pad_id=0,
            unk_id=1,
            bos_id=2,
            eos_id=3,
            pad_piece="[PAD]",
            unk_piece="[UNK]",
            bos_piece="[BOS]",
            eos_piece="[EOS]",
        )
        tok = SentencePieceUnigramTokenizer(str(model_prefix) + ".model")
        tok.save(str(tokenizer_path))
    else:
        tokenizer = Tokenizer(models.BPE(unk_token="[UNK]"))
        tokenizer.normalizer = normalizers.NFKC()
        tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel()
        trainer = trainers.BpeTrainer(
            vocab_size=cfg.vocab_size,
            special_tokens=["[PAD]", "[UNK]", "[BOS]", "[EOS]"],
        )
        tokenizer.train_from_iterator(_iter_text(files), trainer=trainer)
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
