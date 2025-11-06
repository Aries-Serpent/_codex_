#!/usr/bin/env python
"""
Nox sessions for API documentation validation.

This module provides isolated sessions for building and validating
API documentation offline.
"""
import nox
from pathlib import Path

# Supported Python versions for documentation builds
# Aligned with repository testing matrix
SUPPORTED_PYTHON_VERSIONS = ["3.10", "3.11", "3.12"]


@nox.session(name="docs_validate", python=SUPPORTED_PYTHON_VERSIONS)
def docs_validate(session: nox.Session) -> None:
    """
    Build and validate API docs offline using pdoc and the validator script.
    Non-blocking: the validator exits 0; rely on textual summary for manual gating.
    """
    session.install("-r", "requirements-dev.txt")
    # Ensure local package import
    session.install("--no-deps", "-e", ".")
    # Try to install pdoc; if unavailable offline, the validator will 'skip' gracefully
    try:
        session.install("pdoc3")
    except Exception:
        session.log("pdoc3 unavailable; proceeding to run validator (will report 'skipped').")

    out_dir = "artifacts/docs/api"
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    session.run(
        "python",
        "tools/validate_api_docs.py",
        "--package",
        "codex.cli",  # Start with smaller package
        "--out",
        out_dir,
        "--allow-optional",
        "wandb",
        "tensorboard",
        "torch",
        "transformers",
        "--summary",
    )


@nox.session(name="docs_validate_full", python=SUPPORTED_PYTHON_VERSIONS)
def docs_validate_full(session: nox.Session) -> None:
    """
    Build and validate API docs for full codex_ml package.
    Requires more dependencies installed.
    """
    session.install("-r", "requirements-dev.txt")
    session.install("--no-deps", "-e", ".")
    try:
        session.install("pdoc3")
    except Exception:
        session.log("pdoc3 unavailable; validator will skip.")

    out_dir = "artifacts/docs/api_full"
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    session.run(
        "python",
        "tools/validate_api_docs.py",
        "--package",
        "codex_ml",
        "--out",
        out_dir,
        "--allow-optional",
        "wandb",
        "tensorboard",
        "torch",
        "transformers",
        "accelerate",
        "peft",
        "--summary",
    )
