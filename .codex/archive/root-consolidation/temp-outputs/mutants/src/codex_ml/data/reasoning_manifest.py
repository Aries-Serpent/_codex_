"""Reasoning corpus manifest and checksum validation utilities."""

from __future__ import annotations

import os
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from .checksums import manifest_for_paths

__all__ = [
    "CorpusArtifact",
    "CorpusValidationResult",
    "ReasoningCorpus",
    "ReasoningCorpusError",
    "available_corpora",
    "build_corpus_selection",
    "get_reasoning_corpus",
    "list_reasoning_corpora",
]


def _normalise_name(name: str) -> str:
    return name.strip().lower().replace(" ", "_").replace("-", "_")


def _discover_repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").is_file():
            return parent
    return current.parents[min(3, len(current.parents) - 1)]


def _default_corpus_root() -> Path:
    env_override = os.environ.get("CODEX_REASONING_DATA_DIR")
    if env_override:
        return Path(env_override).expanduser()
    return _discover_repo_root() / "data" / "sample" / "reasoning"


def _resolve_root(root: str | Path | None) -> Path:
    if root is None:
        return _default_corpus_root().resolve()
    return Path(root).expanduser().resolve()


@dataclass(frozen=True)
class CorpusArtifact:
    """Single file backing a reasoning corpus."""

    filename: str
    sha256: str
    description: str | None = None

    def resolve_path(self, root: Path) -> Path:
        path = Path(self.filename)
        if not path.is_absolute():
            path = root / path
        return path


@dataclass(frozen=True)
class CorpusValidationResult:
    """Result of validating corpus artifacts against recorded checksums."""

    corpus: ReasoningCorpus
    root: Path
    expected_paths: list[Path]
    present_paths: list[Path]
    missing: list[Path]
    mismatched: list[tuple[Path, str, str]]
    manifest_rows: list[Mapping[str, object]]

    @property
    def ok(self) -> bool:
        return not self.missing and not self.mismatched

    def error_message(self) -> str:
        parts: list[str] = []
        if self.missing:
            joined = ", ".join(str(p) for p in self.missing)
            parts.append(f"missing files: {joined}")
        if self.mismatched:
            detail = "; ".join(
                f"{path} expected {expected} got {actual}"
                for path, expected, actual in self.mismatched
            )
            parts.append(f"checksum mismatch: {detail}")
        if not parts:
            return f"{self.corpus.name}: validation passed"
        return f"{self.corpus.name}: " + "; ".join(parts)

    def to_payload(self) -> dict[str, object]:
        return {
            "name": self.corpus.name,
            "category": self.corpus.category,
            "description": self.corpus.description,
            "tags": list(self.corpus.tags),
            "required_keys": list(self.corpus.required_keys),
            "schema": self.corpus.record_schema,
            "paths": [str(path) for path in self.expected_paths],
            "manifest": list(self.manifest_rows),
            "missing": [str(path) for path in self.missing],
            "mismatched": [
                {"path": str(path), "expected": expected, "actual": actual}
                for path, expected, actual in self.mismatched
            ],
            "status": "ok" if self.ok else "error",
        }


@dataclass(frozen=True)
class ReasoningCorpus:
    """Metadata describing a curated reasoning corpus."""

    name: str
    category: str
    description: str
    artifacts: tuple[CorpusArtifact, ...]
    tags: tuple[str, ...] = ()
    required_keys: tuple[str, ...] = ("input", "target")
    aliases: tuple[str, ...] = ()
    record_schema: str | None = "https://codexml.ai/schemas/reasoning_record.v1"
    notes: Mapping[str, object] = field(default_factory=dict)

    def validate(self, root: str | Path | None = None) -> CorpusValidationResult:
        base = _resolve_root(root)
        expected_paths = [artifact.resolve_path(base) for artifact in self.artifacts]
        present: list[tuple[Path, CorpusArtifact]] = []
        missing: list[Path] = []
        for artifact, path in zip(self.artifacts, expected_paths, strict=False):
            if path.exists():
                present.append((path, artifact))
            else:
                missing.append(path)
        manifest_rows = manifest_for_paths(path for path, _artifact in present) if present else []
        manifest_index = {Path(row["path"]).resolve(): row for row in manifest_rows}  # type: ignore[arg-type]
        mismatched: list[tuple[Path, str, str]] = []
        for path, artifact in present:
            row = manifest_index.get(path.resolve())
            if not row:
                continue
            actual = str(row.get("sha256"))
            if artifact.sha256 and actual != artifact.sha256:
                mismatched.append((path, artifact.sha256, actual))
        return CorpusValidationResult(
            corpus=self,
            root=base,
            expected_paths=expected_paths,
            present_paths=[path for path, _artifact in present],
            missing=missing,
            mismatched=mismatched,
            manifest_rows=manifest_rows,  # type: ignore[arg-type]
        )

    def selection_payload(self, root: str | Path | None = None) -> dict[str, object]:
        return self.validate(root=root).to_payload()


class ReasoningCorpusError(ValueError):
    """Raised when a requested reasoning corpus cannot be resolved."""


_RECORDED_CORPORA: tuple[ReasoningCorpus, ...] = (
    ReasoningCorpus(
        name="proof_logs",
        aliases=("proof-logs", "proof"),
        category="proof",
        description="Toy natural deduction proof traces with step-by-step reasoning.",
        artifacts=(
            CorpusArtifact(
                "proof_logs.jsonl",
                "65a62f2db28fdca5592e72a5e897862ee2dccae48a9d7608ecd1193f94d4b208",  # pragma: allowlist secret  # noqa: E501
                description="Two-entry sample of proof reasoning records.",
            ),
        ),
        tags=("logic", "chain-of-thought"),
        required_keys=("input", "target", "metadata"),
        notes={
            "curriculum_hint": "Suitable for warm-up proof verification tasks.",
        },
    ),
    ReasoningCorpus(
        name="math_word_problems",
        aliases=("math-word-problems", "math"),
        category="math",
        description="Short math word problems paired with worked solutions.",
        artifacts=(
            CorpusArtifact(
                "math_word_problems.jsonl",
                "bd5cd2727849af8b9fd1d78a7c45b90be11b05ba9989121c34708110e52a7afb",  # pragma: allowlist secret  # noqa: E501
                description="Two solved arithmetic reasoning problems.",
            ),
        ),
        tags=("arithmetic", "reasoning"),
        required_keys=("input", "target", "metadata"),
        notes={
            "curriculum_hint": "Useful for difficulty ramp scheduling based on numeric answers.",
        },
    ),
    ReasoningCorpus(
        name="tool_traces",
        aliases=("tool-traces", "tools"),
        category="tool",
        description="Demonstrations of tool-augmented reasoning with serialized traces.",
        artifacts=(
            CorpusArtifact(
                "tool_traces.jsonl",
                "01aba359a56e1196e08d92f6f019c217b8d03492c702c9393f3f24ed280541d2",  # pragma: allowlist secret  # noqa: E501
                description="Two examples capturing tool calls and natural language rationales.",
            ),
        ),
        tags=("agents", "tools", "reasoning"),
        required_keys=("input", "target", "metadata"),
        notes={
            "curriculum_hint": "Interleave with replay buffers to prevent forgetting tool syntax.",
        },
    ),
)

_CORPUS_INDEX: dict[str, ReasoningCorpus] = {}
for corpus in _RECORDED_CORPORA:
    _CORPUS_INDEX[_normalise_name(corpus.name)] = corpus
    for alias in corpus.aliases:
        _CORPUS_INDEX[_normalise_name(alias)] = corpus


def list_reasoning_corpora() -> list[str]:
    """Return the canonical identifiers for the available corpora."""

    return sorted({corpus.name for corpus in _RECORDED_CORPORA})


def available_corpora() -> tuple[str, ...]:
    """Return the canonical identifiers as a tuple for CLI choices."""

    return tuple(list_reasoning_corpora())


def get_reasoning_corpus(name: str) -> ReasoningCorpus:
    """Resolve *name* to a :class:`ReasoningCorpus` instance."""

    corpus = _CORPUS_INDEX.get(_normalise_name(name))
    if corpus is None:
        raise ReasoningCorpusError(f"unknown reasoning corpus: {name}")
    return corpus


def build_corpus_selection(
    names: Sequence[str],
    root: str | Path | None = None,
    *,
    strict: bool = True,
) -> dict[str, object]:
    """Validate ``names`` and return a manifest payload for downstream config."""

    base = _resolve_root(root)
    if not names:
        return {"root": str(base), "corpora": []}

    seen: set[str] = set()
    results: list[CorpusValidationResult] = []
    for raw_name in names:
        key = _normalise_name(raw_name)
        if not key:
            continue
        if key in seen:
            continue
        seen.add(key)
        corpus = _CORPUS_INDEX.get(key)
        if corpus is None:
            raise ReasoningCorpusError(f"unknown reasoning corpus: {raw_name}")
        validation = corpus.validate(root=base)
        if strict and not validation.ok:
            raise ReasoningCorpusError(validation.error_message())
        results.append(validation)

    return {
        "root": str(base),
        "corpora": [result.to_payload() for result in results],
    }


# Backwards compatibility helper ------------------------------------------------


def iter_corpus_manifests(
    root: str | Path | None = None,
) -> Iterable[Mapping[str, object]]:
    """Yield manifest payloads for all corpora (best-effort)."""

    base = _resolve_root(root)
    for corpus in _RECORDED_CORPORA:
        yield corpus.selection_payload(root=base)


__all__.append("iter_corpus_manifests")
