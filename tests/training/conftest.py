"""Training-specific pytest configuration.

The training test suite historically imported optional dependencies at
collection time to ensure the full training stack was present.  That approach
prevented lightweight integrity tests—such as the checkpoint metadata
round-trips—from running in minimal environments.  The repository-level
``tests.conftest`` module now handles optional dependency gating, so this file
intentionally stays minimal.
"""

from __future__ import annotations

# Intentionally empty: per-test optional dependency handling lives in
# ``tests.conftest``.  Keeping the module ensures dotted-path imports such as
# ``tests.training.conftest`` remain valid for external tooling.
