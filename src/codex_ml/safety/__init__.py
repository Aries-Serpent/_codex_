# BEGIN: CODEX_SAFETY_INIT
from .filters import SafetyFilters, SafetyViolation
import logging
logger = logging.getLogger(__name__)
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
except Exception:  # pragma: no cover - fallback for non-POSIX

    def docker_available() -> bool:
        return False

    def firejail_available() -> bool:
        return False

    def run_in_sandbox(*args, **kwargs):
        raise RuntimeError("Sandbox is not available on this platform; run_in_sandbox disabled")


__all__ = [
    "ModerationAdapter",
    "ModerationDecision",
    "ModerationRejection",
    "ModerationSettings",
    "PromptSanitizer",
    "SafetyFilters",
    "run_in_sandbox",
    "docker_available",
    "firejail_available",
    "SafetyConfig",
    "sanitize_prompt",
    "sanitize_output",
    "SafetyViolation",
    "SecretRedactor",
]
