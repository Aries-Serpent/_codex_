"""Compatibility package for legacy cognitive module imports.

The repository historically published checkpoint/resume utilities under a
``cognitive`` package layout. Keep that surface available alongside the newer
``scripts.cognitive`` package so both import paths resolve consistently.
"""

__all__ = ["session_checkpoint_manager", "session_resume_engine"]
