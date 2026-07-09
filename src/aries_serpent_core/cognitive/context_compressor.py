"""
Context Compressor - Phase 4.2 of Long-term Plan 4.

This module provides context compression capabilities for summarizing
session information and prioritizing relevant context for efficient
cross-session knowledge transfer.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class CompressionStrategy(Enum):
    """Strategies for compressing context."""

    EXTRACTIVE = "extractive"  # Extract key sentences
    ABSTRACTIVE = "abstractive"  # Generate summaries
    HYBRID = "hybrid"  # Combine both approaches


class ContextType(Enum):
    """Types of context that can be compressed."""

    SESSION_LOG = "session_log"
    COMMIT_HISTORY = "commit_history"
    FILE_CHANGES = "file_changes"
    DECISIONS = "decisions"
    PENDING_WORK = "pending_work"
    ERRORS_FIXES = "errors_fixes"


@dataclass
class CompressedContext:
    """A compressed version of session context."""

    context_id: str
    context_type: ContextType
    original_size: int  # Approximate token count
    compressed_size: int
    compression_ratio: float
    summary: str
    key_points: list[str]
    preserved_items: list[str]  # Critical items preserved verbatim
    created_at: datetime
    source_session: str
    relevance_score: float = 1.0
    expiry_weight: float = 1.0  # Decays over time

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "context_id": self.context_id,
            "context_type": self.context_type.value,
            "original_size": self.original_size,
            "compressed_size": self.compressed_size,
            "compression_ratio": self.compression_ratio,
            "summary": self.summary,
            "key_points": self.key_points,
            "preserved_items": self.preserved_items,
            "created_at": self.created_at.isoformat(),
            "source_session": self.source_session,
            "relevance_score": self.relevance_score,
            "expiry_weight": self.expiry_weight,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CompressedContext:
        """Create from dictionary."""
        return cls(
            context_id=data["context_id"],
            context_type=ContextType(data["context_type"]),
            original_size=data["original_size"],
            compressed_size=data["compressed_size"],
            compression_ratio=data["compression_ratio"],
            summary=data["summary"],
            key_points=data["key_points"],
            preserved_items=data.get("preserved_items", []),
            created_at=datetime.fromisoformat(data["created_at"]),
            source_session=data["source_session"],
            relevance_score=data.get("relevance_score", 1.0),
            expiry_weight=data.get("expiry_weight", 1.0),
        )


class TokenEstimator:
    """Estimate token counts for text."""

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Estimate token count (approximate: ~4 chars per token)."""
        return len(text) // 4

    @staticmethod
    def estimate_tokens_list(items: list[str]) -> int:
        """Estimate tokens for a list of strings."""
        return sum(TokenEstimator.estimate_tokens(item) for item in items)


class KeyPointExtractor:
    """Extract key points from text using pattern matching."""

    # Patterns for important content
    IMPORTANCE_PATTERNS = [
        (r"(?:fix|fixed|fixes)\s+(.+)", "fix"),
        (r"(?:implement|implemented|add|added)\s+(.+)", "feature"),
        (r"(?:error|issue|bug):\s*(.+)", "issue"),
        (r"(?:decision|decided|chose):\s*(.+)", "decision"),
        (r"(?:important|critical|note):\s*(.+)", "note"),
        (r"(?:todo|pending|remaining):\s*(.+)", "todo"),
    ]

    def __init__(self) -> None:
        """Initialize extractor."""
        self._patterns = [
            (re.compile(p, re.IGNORECASE), tag) for p, tag in self.IMPORTANCE_PATTERNS
        ]

    def extract(self, text: str, max_points: int = 10) -> list[tuple[str, str]]:
        """Extract key points with their type tags."""
        points = []
        seen = set()

        for line in text.split("\n"):
            line = line.strip()
            if not line or len(line) < 10:
                continue

            for pattern, tag in self._patterns:
                match = pattern.search(line)
                if match:
                    point = match.group(1) if match.groups() else line
                    if point not in seen:
                        points.append((point, tag))
                        seen.add(point)
                        break

            if len(points) >= max_points:
                break

        return points


class SentenceScorer:
    """Score sentences by importance for extractive summarization."""

    # Words that indicate importance
    IMPORTANCE_WORDS = {
        "critical",
        "important",
        "must",
        "required",
        "error",
        "fix",
        "bug",
        "security",
        "breaking",
        "urgent",
        "blocked",
        "failed",
        "resolved",
        "implemented",
    }

    def score(self, sentence: str) -> float:
        """Score a sentence by importance (0-1)."""
        sentence_lower = sentence.lower()
        words = set(re.findall(r"\w+", sentence_lower))

        # Base score from length (prefer medium length)
        length_score = min(len(words) / 20, 1.0)

        # Importance word boost
        importance_score = len(words.intersection(self.IMPORTANCE_WORDS)) / len(
            self.IMPORTANCE_WORDS
        )

        # Position bias (first sentences often more important)
        # This is applied externally based on position

        return 0.4 * length_score + 0.6 * importance_score


class ExtractiveSummarizer:
    """Summarize text by extracting important sentences."""

    def __init__(self, target_ratio: float = 0.2):
        """
        Initialize summarizer.

        Args:
            target_ratio: Target compression ratio (0.2 = 20% of original)
        """
        self.target_ratio = target_ratio
        self.scorer = SentenceScorer()

    def summarize(self, text: str, max_sentences: int = 10) -> str:
        """Summarize text by extracting key sentences."""
        # Split into sentences
        sentences = re.split(r"[.!?]\s+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return ""

        # Score each sentence
        scored = []
        for i, sentence in enumerate(sentences):
            score = self.scorer.score(sentence)
            # Position bias: first and last sentences get boost
            if i < 3:
                score += 0.2
            if i >= len(sentences) - 2:
                score += 0.1
            scored.append((score, i, sentence))

        # Sort by score and take top N
        scored.sort(reverse=True)
        target_count = max(1, min(max_sentences, int(len(sentences) * self.target_ratio)))
        selected = sorted(scored[:target_count], key=lambda x: x[1])  # Restore order

        return ". ".join(s[2] for s in selected) + "."


class ContextPrioritizer:
    """Prioritize context items by relevance and recency."""

    def __init__(self, decay_factor: float = 0.95):
        """
        Initialize prioritizer.

        Args:
            decay_factor: How much relevance decays per day
        """
        self.decay_factor = decay_factor

    def calculate_relevance(
        self,
        created_at: datetime,
        access_count: int = 0,
        base_priority: float = 1.0,
    ) -> float:
        """Calculate current relevance score."""
        now = datetime.now(timezone.utc)
        days_old = (now - created_at).days

        # Apply time decay
        time_factor = self.decay_factor**days_old

        # Access frequency boost
        access_factor = min(1 + access_count * 0.1, 2.0)

        return base_priority * time_factor * access_factor

    def prioritize(
        self,
        items: list[CompressedContext],
        max_items: int = 10,
    ) -> list[CompressedContext]:
        """Prioritize and filter context items."""
        # Update relevance scores
        for item in items:
            item.relevance_score = self.calculate_relevance(
                item.created_at,
                base_priority=item.expiry_weight,
            )

        # Sort by relevance and return top N
        items.sort(key=lambda x: x.relevance_score, reverse=True)
        return items[:max_items]


class ContextIndex:
    """Index for fast context retrieval."""

    def __init__(self, index_path: Path | None = None):
        """Initialize index."""
        self.index_path = index_path or Path(".codex/knowledge/context_index.json")
        self._contexts: dict[str, CompressedContext] = {}
        self._tag_index: dict[str, set[str]] = {}  # tag -> context_ids
        self._type_index: dict[ContextType, set[str]] = {}  # type -> context_ids
        self._load()

    def _load(self) -> None:
        """Load index from disk."""
        if self.index_path.exists():
            try:
                with open(self.index_path) as f:
                    data = json.load(f)
                    for ctx_data in data.get("contexts", []):
                        ctx = CompressedContext.from_dict(ctx_data)
                        self._contexts[ctx.context_id] = ctx
                        self._index_context(ctx)
            except (json.JSONDecodeError, KeyError):
                # Index file is corrupted - will reinitialize
                logger.debug("Suppressed exception in handler", exc_info=True)

    def _index_context(self, ctx: CompressedContext) -> None:
        """Add context to indexes."""
        # Type index
        if ctx.context_type not in self._type_index:
            self._type_index[ctx.context_type] = set()
        self._type_index[ctx.context_type].add(ctx.context_id)

    def save(self) -> None:
        """Save index to disk."""
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.index_path, "w") as f:
            json.dump(
                {
                    "version": "1.0",
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "contexts": [ctx.to_dict() for ctx in self._contexts.values()],
                },
                f,
                indent=2,
            )

    def add(self, ctx: CompressedContext) -> None:
        """Add a compressed context."""
        self._contexts[ctx.context_id] = ctx
        self._index_context(ctx)
        self.save()

    def get(self, context_id: str) -> CompressedContext | None:
        """Get context by ID."""
        return self._contexts.get(context_id)

    def get_by_type(self, context_type: ContextType) -> list[CompressedContext]:
        """Get all contexts of a type."""
        ids = self._type_index.get(context_type, set())
        return [self._contexts[cid] for cid in ids if cid in self._contexts]

    def get_recent(self, limit: int = 10) -> list[CompressedContext]:
        """Get most recent contexts."""
        contexts = list(self._contexts.values())
        contexts.sort(key=lambda x: x.created_at, reverse=True)
        return contexts[:limit]

    def count(self) -> int:
        """Get total count."""
        return len(self._contexts)


class ContextCompressor:
    """Main class for compressing session context."""

    def __init__(
        self,
        index_path: Path | None = None,
        target_compression: float = 0.2,
    ):
        """
        Initialize compressor.

        Args:
            index_path: Path to context index
            target_compression: Target compression ratio
        """
        self.index = ContextIndex(index_path)
        self.summarizer = ExtractiveSummarizer(target_ratio=target_compression)
        self.key_point_extractor = KeyPointExtractor()
        self.prioritizer = ContextPrioritizer()
        self._next_id = self.index.count() + 1

    def _generate_id(self) -> str:
        """Generate unique context ID."""
        ctx_id = f"CTX-{self._next_id:05d}"
        self._next_id += 1
        return ctx_id

    def compress_session_log(
        self,
        log_content: str,
        session_id: str,
        preserve_patterns: list[str] | None = None,
    ) -> CompressedContext:
        """Compress a session log."""
        original_tokens = TokenEstimator.estimate_tokens(log_content)

        # Extract key points
        key_points_raw = self.key_point_extractor.extract(log_content, max_points=15)
        key_points = [point for point, _ in key_points_raw]

        # Preserve items matching patterns
        preserved = []
        if preserve_patterns:
            for pattern in preserve_patterns:
                matches = re.findall(pattern, log_content, re.IGNORECASE)
                preserved.extend(matches[:3])  # Limit preserved per pattern

        # Generate summary
        summary = self.summarizer.summarize(log_content, max_sentences=8)

        compressed_tokens = TokenEstimator.estimate_tokens(summary)
        compressed_tokens += TokenEstimator.estimate_tokens_list(key_points)
        compressed_tokens += TokenEstimator.estimate_tokens_list(preserved)

        ctx = CompressedContext(
            context_id=self._generate_id(),
            context_type=ContextType.SESSION_LOG,
            original_size=original_tokens,
            compressed_size=compressed_tokens,
            compression_ratio=(compressed_tokens / original_tokens if original_tokens > 0 else 0),
            summary=summary,
            key_points=key_points,
            preserved_items=preserved,
            created_at=datetime.now(timezone.utc),
            source_session=session_id,
        )

        self.index.add(ctx)
        return ctx

    def compress_commit_history(
        self,
        commits: list[dict[str, str]],
        session_id: str,
    ) -> CompressedContext:
        """Compress commit history."""
        # Format commits as text
        text_parts = []
        for commit in commits:
            msg = commit.get("message", "")
            sha = commit.get("sha", "")[:7]
            text_parts.append(f"{sha}: {msg}")

        full_text = "\n".join(text_parts)
        original_tokens = TokenEstimator.estimate_tokens(full_text)

        # Extract key changes
        key_points = []
        for commit in commits[:10]:  # Limit to 10 most recent
            msg = commit.get("message", "")
            if msg:
                # Truncate long messages
                key_points.append(msg[:100])

        # Summary is just the count and key themes
        summary = f"Session included {len(commits)} commits. Key changes: "
        summary += "; ".join(key_points[:5])

        compressed_tokens = TokenEstimator.estimate_tokens(summary)

        ctx = CompressedContext(
            context_id=self._generate_id(),
            context_type=ContextType.COMMIT_HISTORY,
            original_size=original_tokens,
            compressed_size=compressed_tokens,
            compression_ratio=(compressed_tokens / original_tokens if original_tokens > 0 else 0),
            summary=summary,
            key_points=key_points,
            preserved_items=[],
            created_at=datetime.now(timezone.utc),
            source_session=session_id,
        )

        self.index.add(ctx)
        return ctx

    def compress_file_changes(
        self,
        files_added: list[str],
        files_modified: list[str],
        files_deleted: list[str],
        session_id: str,
    ) -> CompressedContext:
        """Compress file change information."""
        total_files = len(files_added) + len(files_modified) + len(files_deleted)

        # Group by directory for compression
        dirs_affected: set[str] = set()
        for f in files_added + files_modified + files_deleted:
            dir_path = str(Path(f).parent)
            dirs_affected.add(dir_path)

        summary = (
            f"Changed {total_files} files: "
            f"{len(files_added)} added, {len(files_modified)} modified, "
            f"{len(files_deleted)} deleted. "
            f"Affected directories: {', '.join(sorted(dirs_affected)[:5])}"
        )

        key_points = []
        if files_added:
            key_points.append(f"Added: {', '.join(files_added[:5])}")
        if files_modified:
            key_points.append(f"Modified: {', '.join(files_modified[:5])}")
        if files_deleted:
            key_points.append(f"Deleted: {', '.join(files_deleted[:5])}")

        original_tokens = TokenEstimator.estimate_tokens_list(
            files_added + files_modified + files_deleted
        )
        compressed_tokens = TokenEstimator.estimate_tokens(summary)

        ctx = CompressedContext(
            context_id=self._generate_id(),
            context_type=ContextType.FILE_CHANGES,
            original_size=original_tokens,
            compressed_size=compressed_tokens,
            compression_ratio=(compressed_tokens / original_tokens if original_tokens > 0 else 0),
            summary=summary,
            key_points=key_points,
            preserved_items=[],
            created_at=datetime.now(timezone.utc),
            source_session=session_id,
        )

        self.index.add(ctx)
        return ctx

    def get_session_startup_context(
        self,
        max_tokens: int = 2000,
        include_types: list[ContextType] | None = None,
    ) -> str:
        """Get compressed context for session startup."""
        if include_types is None:
            include_types = list(ContextType)

        # Gather recent contexts
        all_contexts = []
        for ctx_type in include_types:
            all_contexts.extend(self.index.get_by_type(ctx_type))

        # Prioritize
        prioritized = self.prioritizer.prioritize(all_contexts, max_items=20)

        # Build context string within token budget
        parts = ["## Recent Context\n"]
        current_tokens = TokenEstimator.estimate_tokens(parts[0])

        for ctx in prioritized:
            ctx_text = f"\n### {ctx.context_type.value} ({ctx.source_session})\n"
            ctx_text += f"{ctx.summary}\n"
            if ctx.key_points:
                ctx_text += "Key points:\n"
                ctx_text += "\n".join(f"- {p}" for p in ctx.key_points[:3])

            ctx_tokens = TokenEstimator.estimate_tokens(ctx_text)
            if current_tokens + ctx_tokens > max_tokens:
                break

            parts.append(ctx_text)
            current_tokens += ctx_tokens

        return "\n".join(parts)

    def get_compression_stats(self) -> dict[str, Any]:
        """Get compression statistics."""
        contexts = list(self.index._contexts.values())

        if not contexts:
            return {
                "total_contexts": 0,
                "total_original_tokens": 0,
                "total_compressed_tokens": 0,
                "average_compression_ratio": 0,
            }

        total_original = sum(c.original_size for c in contexts)
        total_compressed = sum(c.compressed_size for c in contexts)
        avg_ratio = sum(c.compression_ratio for c in contexts) / len(contexts)

        return {
            "total_contexts": len(contexts),
            "total_original_tokens": total_original,
            "total_compressed_tokens": total_compressed,
            "average_compression_ratio": avg_ratio,
            "space_saved_percent": (1 - avg_ratio) * 100,
        }
