"""Compatibility wrapper for legacy ``cognitive`` imports."""

from scripts.cognitive.session_resume_engine import *  # noqa: F401,F403
from scripts.cognitive.session_resume_engine import __all__ as _resume_all

__all__ = list(_resume_all) if isinstance(_resume_all, list) else [
    "ContextProvider",
    "SessionContext",
    "RecoveryMetadata",
    "SessionResumeError",
    "ContextInjectionError",
    "DependencyResolutionError",
    "WarmupError",
    "SessionResumeEngine",
    "resume_session",
]
