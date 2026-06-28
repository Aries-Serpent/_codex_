"""
Safety package public interface.

This module re-exports the primary safety utilities used across codex_ml,
including:
- content moderation adapters, decisions, and settings
- prompt/output sanitization helpers and safety configuration
- secret redaction utilities
- sandbox availability checks and execution helper (with graceful fallback
  on platforms where sandbox support is unavailable)

Typical usage:
    from codex_ml.safety import sanitize_prompt, sanitize_output
"""

# BEGIN: CODEX_SAFETY_INIT
from .filters import SafetyFilters, SafetyViolation
from .moderation import (
    ModerationAdapter,
    ModerationDecision,
    ModerationRejection,
    ModerationSettings,
)
from .prompt_sanitizer import PromptSanitizer
from .redaction import SecretRedactor
from .sanitizers import SafetyConfig, sanitize_output, sanitize_prompt

# On some platforms (e.g., Windows), the sandbox implementation depends on
# POSIX-only modules (like `resource`). Import it defensively and provide
# graceful stubs if unavailable so importing `codex_ml.safety` does not fail.
try:  # pragma: no cover - platform dependent
    from .sandbox import docker_available, firejail_available, run_in_sandbox
except (ImportError, AttributeError):  # pragma: no cover - fallback for non-POSIX

    def docker_available() -> bool:
        return False

    def firejail_available() -> bool:
        return False

    def run_in_sandbox(*args, **kwargs) -> None:  # type: ignore[misc]
        raise RuntimeError("Sandbox is not available on this platform; run_in_sandbox disabled")


__all__ = [
    "ModerationAdapter",
    "ModerationDecision",
    "ModerationRejection",
    "ModerationSettings",
    "PromptSanitizer",
    "SafetyConfig",
    "SafetyFilters",
    "SafetyViolation",
    "SecretRedactor",
    "docker_available",
    "firejail_available",
    "run_in_sandbox",
    "sanitize_output",
    "sanitize_prompt",
]
