"""
LLM Client - OpenAI API wrapper with safety guards and provenance.

Provides a safe interface to LLM APIs with:
- Rate limiting
- Token budget management
- Provenance recording
- Error handling and fallbacks

Author: mbaetiong
Generated: 2025-12-17

Safeguards:
- Token budget enforcement (max 8000)
- Rate limiting between calls
- Provenance recording for all calls
- No private data to external LLM by default
- Temperature set to 0 for determinism
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

# Constants
CHARS_PER_TOKEN = 4  # Approximate character-to-token ratio for English text
from typing import Any, Optional  # noqa: E402

from codex_ml.safety.moderation import (  # noqa: E402
    ModerationAdapter,
    ModerationRejection,
    ModerationSettings,
)

logger = logging.getLogger(__name__)

# Configuration
DEFAULT_MODEL = "gpt-4o"
MAX_TOKENS = 8000
DEFAULT_TEMPERATURE = 0.0
RATE_LIMIT_DELAY = 1.0


@dataclass
class ProvenanceRecord:
    """Record of an LLM API call for auditing."""

    prompt_hash: str
    prompt: str
    response: str
    model: str
    model_version: str
    timestamp: datetime
    temperature: float
    token_count: dict[str, int]
    latency_ms: float
    snapshot_ref: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "prompt_hash": self.prompt_hash,
            "prompt": self.prompt,
            "response": self.response,
            "model": self.model,
            "model_version": self.model_version,
            "timestamp": self.timestamp.isoformat(),
            "temperature": self.temperature,
            "token_count": self.token_count,
            "latency_ms": self.latency_ms,
            "snapshot_ref": self.snapshot_ref,
        }

    def save(self, directory: Path) -> Path:
        """Save provenance record to file."""
        filename = f"{self.prompt_hash[:16]}.json"
        path = directory / filename
        with path.open("w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)
        return path


def _hash_prompt(prompt: str) -> str:
    """Compute SHA256 hash of prompt."""
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def _truncate_context(text: str, max_chars: int = 24000) -> str:
    """Truncate text to fit within token budget.

    Safeguard: Token budget enforcement.
    """
    if len(text) <= max_chars:
        return text

    # Truncate with indicator
    return text[: max_chars - 100] + "\n\n[... truncated for token budget ...]"


class CodexLLMClient:
    """LLM client with safety guards and provenance tracking.

    Provides a safe interface to OpenAI API with:
    - Rate limiting between calls
    - Token budget management
    - Provenance recording for all calls
    - Conservative inference mode

    Example:
        >>> client = CodexLLMClient(provenance_dir=Path("llm_provenance"))
        >>> result = client.infer_intent(context)
        >>> print(f"Goal: {result['goal']}")
    """

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.

        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None

        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI

                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("Initialized OpenAI client with model: %s", model)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                type(e).__name__
                logger.debug("ImportError: <ERROR_TYPE>")
                logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
                logger.warning("openai package not installed, LLM features disabled")

    def _rate_limit(self) -> None:
        """Enforce rate limiting between calls.

        Safeguard: Rate limiting.
        """
        delay = float(os.environ.get("CODEX_LLM_RATE_LIMIT_DELAY", RATE_LIMIT_DELAY))
        elapsed = time.time() - self._last_call_time
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self._last_call_time = time.time()

    def _build_intent_prompt(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.

        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(context.get("static_summary", {}), indent=2)
        imports = ", ".join(context.get("imports", [])[:50])
        source_excerpt = _truncate_context(context.get("source_excerpt", ""))

        return f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""

    def infer_intent(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.

        Args:
            context: Analysis context including static report and source

        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None

        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)

        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)

        # Gap 27: mandatory pre-call moderation (fail-closed) — raises ModerationRejection if blocked  # noqa: E501
        _mod = ModerationAdapter(ModerationSettings(enabled=True, fail_open=False))
        _mod.enforce(prompt, stage="input")

        # Rate limit
        self._rate_limit()

        try:
            start_time = time.time()

            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )

            latency_ms = (time.time() - start_time) * 1000

            # Extract response
            response_text = response.choices[0].message.content or ""

            # Gap 27: post-response moderation (fail-closed)
            try:
                _mod.enforce(response_text, stage="output")
            except ModerationRejection:
                logger.warning("Moderation rejected LLM response in infer_intent")
                raise

            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )

            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)

            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])

                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result

            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None

        except ModerationRejection:
            raise
        except (ValueError, TypeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.error("LLM call failed: %s", e)
            return None

    def summarize_code(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.

        Args:
            source: Source code to summarize

        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None

        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, 8000)}
```

Be concise and factual. Do not invent functionality not present in the code."""

        # Gap 27: mandatory pre-call moderation (fail-closed)
        _mod = ModerationAdapter(ModerationSettings(enabled=True, fail_open=False))
        _mod.enforce(prompt, stage="input")

        self._rate_limit()

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=200,
            )
            result = response.choices[0].message.content
            # Gap 27: post-response moderation (fail-closed)
            try:
                _mod.enforce(result or "", stage="output")
            except ModerationRejection:
                logger.warning("Moderation rejected LLM response in summarize_code")
                raise
            return result
        except ModerationRejection:
            raise
        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.error("Summarization failed: %s", e)
            return None
