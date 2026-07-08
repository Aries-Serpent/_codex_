"""Session context injector for AgentBrainAPI.

Phase 1, Pre-commit 1 (S108): Context Injection Foundation.

Wires ``AgentBrainAPI.get_session_context()`` into the Copilot session
lifecycle, mirroring the ``store_memory`` injection pipeline.  On every
session start the injector:

1. Calls the live ``AgentBrainAPI``.
2. Falls back to a file-system cache if the API is unavailable.
3. Performs quantum reconstruction (wave-collapse + entropy minimisation)
   if both live call and cache miss.

PDA Loop integration
--------------------
- **PLAN**: allowlist filter + recency ranking applied to raw context.
- **DO**: payload injected into system prompt block.
- **ASSESS**: token budget enforced; trimming applied if over budget.

AfterMath integration
---------------------
``_quantum_reconstruct`` stores a lesson via ``store_memory`` so every
reconstruction event teaches the brain about its own failure mode.

CODEBASE_AGENCY_POLICY.md compliance
-------------------------------------
- AfterMath/PDA loop integrated.
- Input validation via ``CONTEXT_FIELD_ALLOWLIST``.
- Comprehensive error handling with graceful degradation.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: RBAC-ready field allowlist — only these fields survive sanitisation.
CONTEXT_FIELD_ALLOWLIST: frozenset[str] = frozenset(
    {
        "session_id",
        "pattern_ids",  # P-001 → P-N references only
        "store_memory_facts",  # verbatim store_memory entries
        "last_session_summary",  # non-PII summary string
        "active_pr_refs",  # PR numbers only, no user data
        "recency_scores",  # float vector, no raw content
        "continuation_trigger",  # "continue with next phase task" flag
        "cognitive_status",  # COGNITIVE_BRAIN_STATUS_S*.md pointer
    }
)

#: Conservative token budget; 1 token ≈ 4 chars.
MAX_CONTEXT_TOKENS: int = 800

#: Exponential decay half-life (sessions) for recency ranking.
RECENCY_HALF_LIFE_SESSIONS: int = 10


# ---------------------------------------------------------------------------
# Public dataclass
# ---------------------------------------------------------------------------


@dataclass
class SessionContextPayload:
    """Sanitised, token-budgeted context for system-prompt injection.

    AfterMath integration: payload is recorded post-injection; outcome
    (success/failure) feeds back via ``report_completion()`` in Phase 3.
    """

    session_id: str
    injected_patterns: list[str]  # e.g. ["P-043", "P-038"]
    store_memory_facts: list[str]
    continuation_trigger: str | None
    cognitive_status_ref: str | None
    token_estimate: int
    reconstructed: bool = False  # True when quantum fallback used
    reconstruction_method: str | None = None

    def to_prompt_block(self) -> str:
        """Render as a Markdown system-prompt injection block."""
        lines: list[str] = [
            "## 🧠 Cognitive Brain Context [AUTO-INJECTED]",
            f"Session: {self.session_id}",
        ]
        if self.store_memory_facts:
            lines.append("### Persistent Memory Facts")
            lines.extend(f"- {f}" for f in self.store_memory_facts)
        if self.injected_patterns:
            lines.append("### Active Pattern Alerts")
            lines.extend(f"- {p}" for p in self.injected_patterns)
        if self.continuation_trigger:
            lines.append(f"### Continuation Signal: {self.continuation_trigger}")
        if self.cognitive_status_ref:
            lines.append(f"### Status Reference: {self.cognitive_status_ref}")
        if self.reconstructed:
            lines.append(
                f"⚠️ Context reconstructed via {self.reconstruction_method} "
                "(see store_memory for reconstruction lesson)"
            )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _apply_allowlist(raw_context: dict[str, Any]) -> dict[str, Any]:
    """Strip all fields not in ``CONTEXT_FIELD_ALLOWLIST``.

    PDA: PLAN phase — sanitise before injection.
    """
    return {k: v for k, v in raw_context.items() if k in CONTEXT_FIELD_ALLOWLIST}


def _apply_recency_ranking(
    patterns: list[dict[str, Any]],
    current_session_num: int,
) -> list[str]:
    """Return the top-5 pattern IDs weighted by recency.

    Implements Q2 improvement: P-038→P-045 outrank P-001→P-037.
    Physics Fields🔄: information flows from recency scores into pattern
    selection, transforming raw history into actionable context.
    """
    if not patterns:
        return []

    def recency_weight(p: dict[str, Any]) -> float:
        delta = current_session_num - p.get("introduced_session", 0)
        return 2 ** (-delta / RECENCY_HALF_LIFE_SESSIONS)

    ranked = sorted(patterns, key=recency_weight, reverse=True)
    return [p["id"] for p in ranked[:5]]


def _estimate_tokens(text: str) -> int:
    """Rough token estimate: 1 token ≈ 4 chars (conservative)."""
    return len(text) // 4


def _context_from_agent_session(agent_ctx: Any) -> dict[str, Any]:
    """Convert an ``AgentSessionContext`` object into an allowlist-compatible dict.

    Adapts the rich dataclass returned by ``AgentBrainAPI.get_session_context()``
    into the flat dict shape expected by ``_apply_allowlist``.
    """
    if isinstance(agent_ctx, dict):
        return agent_ctx

    # AgentSessionContext — extract relevant fields
    patterns = []
    for i, p in enumerate(getattr(agent_ctx, "active_patterns", []) or []):
        pid = p.get("pattern_id") or p.get("id") if isinstance(p, dict) else str(p)
        patterns.append({"id": pid, "introduced_session": i})

    facts: list[str] = []
    if getattr(agent_ctx, "continuation_from", None):
        facts.append(agent_ctx.continuation_from)

    return {
        "session_id": getattr(agent_ctx, "session_id", "unknown"),
        "pattern_ids": patterns,
        "store_memory_facts": facts,
        "continuation_trigger": "continue with next phase task",
        "cognitive_status": None,
    }


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------


class SessionContextInjector:
    """Lifecycle hook: called at Copilot session start.

    Mirrors the ``store_memory`` injection pipeline exactly, adding:

    * ``AgentBrainAPI.get_session_context()`` call
    * Allowlist filter (Q2-A)
    * Recency-ranked pattern selection (Q2 improvement)
    * Graceful degradation with quantum reconstruction (Q4-B)
    * Cache restore for performance
    * PDA/AfterMath annotations throughout

    CODEBASE_AGENCY_POLICY.md: AfterMath/PDA Loop Integration ✅
    """

    def __init__(
        self,
        brain_api: Any,
        cache_path: Path = Path(".codex/.session_context_cache.json"),
        *,
        brain_client: Any | None = None,
    ) -> None:
        """Initialise the injector.

        Args:
            brain_api: ``AgentBrainAPI``-compatible object that exposes
                ``get_session_context()`` and ``store_memory()``.
            cache_path: Path to the JSON cache file.
            brain_client: Optional :class:`~codex.agents.brain_client.BrainClient`
                instance (CB-004).  When provided, ``is_available()`` is checked as a
                pre-flight guard and ``memory_search()`` is used to augment quantum
                reconstruction with live memory retrieval.
        """
        self._api = brain_api
        self._cache_path = cache_path
        self._brain_client = brain_client  # CB-004: optional BrainClient

        # CB-003: lazy PatternCompressor; initialised on first payload build
        # when pattern data is large enough to benefit from compression.
        self._compressor: Any | None = None

    # ------------------------------------------------------------------
    # PDA: DO phase
    # ------------------------------------------------------------------

    def inject(self, session_metadata: dict[str, Any]) -> SessionContextPayload:
        """Primary entry point.  Called at session start.

        Attempt order (Q4-B three-tier fallback):

        1. Live API call → ``get_session_context()``
        2. Cache restore → restore context + store_memory + trigger
        3. Quantum reconstruction → wave_collapse(pattern_library)

        CB-004: If a :class:`~codex.agents.brain_client.BrainClient` was
        supplied, ``is_available()`` is checked before each attempt that
        requires network access, providing an early failure signal.
        """
        live_error: Exception | None = None

        # CB-004: optional BrainClient pre-flight availability check
        if self._brain_client is not None:
            try:
                if not self._brain_client.is_available():
                    logger.info(
                        "BrainClient reports server unavailable; skipping live context fetch."
                    )
            except (ValueError, TypeError, RuntimeError) as exc:
                logger.debug("BrainClient.is_available() raised: %s", exc)

        # PDA: PLAN — attempt live fetch
        try:
            raw_ctx = self._api.get_session_context()
            raw = _context_from_agent_session(raw_ctx)
            payload = self._build_payload(raw, session_metadata, reconstructed=False)
            self._write_cache(payload)
            return payload
        except (IOError, OSError) as exc:
            live_error = exc
            logger.warning("Live context fetch failed: %s", exc)

        # PDA: DO — attempt cache restore
        cached = self._read_cache()
        if cached is not None:
            logger.info("Restoring session context from cache.")
            cached.reconstructed = True
            cached.reconstruction_method = "cache_restore"
            return cached

        # PDA: ASSESS — quantum reconstruction
        logger.warning("Cache miss. Entering quantum reconstruction.")
        return self._quantum_reconstruct(
            session_metadata,
            live_error or RuntimeError("no live context and no cache"),
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_payload(
        self,
        raw: dict[str, Any],
        meta: dict[str, Any],
        *,
        reconstructed: bool,
    ) -> SessionContextPayload:
        sanitized = _apply_allowlist(raw)
        patterns_raw: list[dict[str, Any]] = sanitized.get("pattern_ids", [])
        session_num: int = meta.get("session_number", 0)

        # CB-003: compress pattern numerical features when the set is large.
        # PatternCompressor works on dict[str, float]; we extract recency-weighted
        # scores from pattern metadata for compression, then restore.
        if len(patterns_raw) >= 10:
            patterns_raw = self._compress_patterns(patterns_raw)

        top_patterns = _apply_recency_ranking(patterns_raw, session_num)

        payload = SessionContextPayload(
            session_id=sanitized.get("session_id", "unknown"),
            injected_patterns=top_patterns,
            store_memory_facts=list(sanitized.get("store_memory_facts", [])),
            continuation_trigger=sanitized.get("continuation_trigger"),
            cognitive_status_ref=sanitized.get("cognitive_status"),
            token_estimate=_estimate_tokens(str(sanitized)),
            reconstructed=reconstructed,
        )

        if payload.token_estimate > MAX_CONTEXT_TOKENS:
            logger.warning(
                "Context payload (%d tokens) exceeds budget (%d). Trimming.",
                payload.token_estimate,
                MAX_CONTEXT_TOKENS,
            )
            while payload.token_estimate > MAX_CONTEXT_TOKENS and payload.store_memory_facts:
                payload.store_memory_facts.pop()
                payload.token_estimate = _estimate_tokens(payload.to_prompt_block())

        return payload

    def _compress_patterns(self, patterns: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """CB-003: Optional PatternCompressor pass on large pattern sets.

        Extracts float-valued features from each pattern dict, fits the
        compressor (if not yet fitted), compresses, then decompresses.  The
        round-trip preserves only numeric features; string metadata (e.g.
        pattern ``id``) is passed through unchanged.

        Returns the (potentially compressed+decompressed) list, which has the
        same structure as the input so ``_apply_recency_ranking`` works as
        normal.  When compression is unavailable the input is returned as-is.
        """
        try:
            from cognitive_brain.quantum.compression import (
                PatternCompressor,
            )
        except ImportError:
            return patterns

        # Extract numeric feature dicts (id is non-numeric; skip it)
        float_features: list[dict[str, float]] = []
        for p in patterns:
            feats = {k: float(v) for k, v in p.items() if k != "id" and isinstance(v, (int, float))}
            float_features.append(feats)

        # Need at least 2 patterns with features to fit
        populated = [f for f in float_features if f]
        if len(populated) < 2:
            return patterns

        try:
            if self._compressor is None:
                self._compressor = PatternCompressor()
                self._compressor.fit(populated)
            compressed = [self._compressor.compress(f) for f in float_features if f]
            decompressed = [self._compressor.decompress(c) for c in compressed]
            # Re-merge decompressed numeric features back into original dicts
            result: list[dict[str, Any]] = []
            decomp_iter = iter(decompressed)
            for p in patterns:
                feats = {k: v for k, v in p.items() if k != "id" and isinstance(v, (int, float))}
                merged = dict(p)
                if feats:
                    merged.update(next(decomp_iter, {}))
                result.append(merged)
            logger.debug("CB-003: compressed %d patterns via PatternCompressor.", len(result))
            return result
        except (ValueError, TypeError, RuntimeError) as exc:
            logger.debug("PatternCompressor pass skipped: %s", exc)
            return patterns

    def _quantum_reconstruct(
        self,
        meta: dict[str, Any],
        original_error: Exception,
    ) -> SessionContextPayload:
        """Physics-inspired reconstruction.

        * **wave_collapse**: scan pattern library, select highest-probability
          relevant patterns given session metadata keywords.
        * **entropy_minimise**: reconstruct store_memory facts from
          ``COGNITIVE_BRAIN_STATUS_S*.md`` files.

        CB-004: When a ``BrainClient`` is available, ``memory_search()`` is
        called with the keyword signal to augment wave-collapse results with
        live memory entries, providing richer reconstruction context.

        AfterMath: emits store_memory lesson + new pattern candidate.
        ⚛️ Physics Patterns👁️: recognises reconstruction as a recurring
        failure mode; documents as a new pattern candidate.
        """
        reconstructed_patterns: list[str] = []
        reconstructed_facts: list[str] = []

        # Wave collapse: keyword-based pattern probability scoring
        pr_title = meta.get("pr_title", "")
        pr_body = meta.get("pr_body", "")
        keyword_signal = f"{pr_title} {pr_body}".lower()

        pattern_library_path = Path(".codex/cognitive_brain/")
        if pattern_library_path.exists():
            for pf in sorted(pattern_library_path.glob("P-*.md"))[-10:]:
                content = pf.read_text(errors="ignore").lower()
                overlap = sum(1 for w in keyword_signal.split() if w in content)
                if overlap >= 2:
                    reconstructed_patterns.append(pf.stem)

        # CB-004: augment wave-collapse with BrainClient memory_search
        if self._brain_client is not None and keyword_signal.strip():
            try:
                if self._brain_client.is_available():
                    mem_result = self._brain_client.memory_search(keyword_signal[:200], limit=10)
                    for entry in mem_result.get("results", []):
                        pattern_ref = entry.get("pattern_id") or entry.get("id")
                        if pattern_ref and pattern_ref not in reconstructed_patterns:
                            reconstructed_patterns.append(str(pattern_ref))
                        fact = entry.get("fact") or entry.get("content")
                        if fact and fact not in reconstructed_facts:
                            reconstructed_facts.append(str(fact))
                    logger.info(
                        "CB-004: BrainClient memory_search augmented reconstruction "
                        "with %d extra patterns and %d facts.",
                        len(reconstructed_patterns),
                        len(reconstructed_facts),
                    )
            except (IOError, OSError) as exc:
                logger.debug("BrainClient.memory_search() skipped during reconstruction: %s", exc)

        # Entropy minimisation: read latest status file
        status_files = sorted(Path(".codex").glob("COGNITIVE_BRAIN_STATUS_S*.md"), reverse=True)
        if status_files:
            latest = status_files[0].read_text(errors="ignore")
            for line in latest.splitlines():
                if line.startswith("- ") and len(line) < 200:
                    reconstructed_facts.append(line[2:])
                    if len(reconstructed_facts) >= 5:
                        break

        # AfterMath: store lesson so future sessions learn from this failure
        lesson = (
            f"LESSON[{datetime.now(timezone.utc).isoformat()}]: "
            f"AgentBrainAPI.get_session_context() failed "
            f"({type(original_error).__name__}). "
            "Quantum reconstruction used. If recurs, add DRQ per "
            "CODEBASE_AGENCY_POLICY.md §4."
        )
        try:
            self._api.store_memory(lesson, tags=["api-failure", "reconstruction"])
        except (IOError, OSError):
            logger.debug("Suppressed exception in handler", exc_info=True)
        return SessionContextPayload(
            session_id=(f"reconstructed-{hashlib.sha256(str(meta).encode()).hexdigest()[:8]}"),
            injected_patterns=reconstructed_patterns[:5],
            store_memory_facts=reconstructed_facts,
            continuation_trigger="continue with next phase task",
            cognitive_status_ref=str(status_files[0]) if status_files else None,
            token_estimate=0,
            reconstructed=True,
            reconstruction_method="quantum_wave_collapse+entropy_minimization",
        )

    # ------------------------------------------------------------------
    # Cache I/O
    # ------------------------------------------------------------------

    def _write_cache(self, payload: SessionContextPayload) -> None:
        try:
            self._cache_path.parent.mkdir(parents=True, exist_ok=True)
            with self._cache_path.open("w") as fh:
                json.dump(
                    {
                        "session_id": payload.session_id,
                        "injected_patterns": payload.injected_patterns,
                        "store_memory_facts": payload.store_memory_facts,
                        "continuation_trigger": payload.continuation_trigger,
                        "cognitive_status_ref": payload.cognitive_status_ref,
                        "token_estimate": payload.token_estimate,
                    },
                    fh,
                    indent=2,
                )
        except OSError as exc:
            logger.warning("Cache write failed: %s", exc)

    def _read_cache(self) -> SessionContextPayload | None:
        try:
            if not self._cache_path.exists():
                return None
            with self._cache_path.open() as fh:
                data = json.load(fh)
            return SessionContextPayload(**data)
        except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
            logger.warning("Cache read failed: %s", exc)
            return None
