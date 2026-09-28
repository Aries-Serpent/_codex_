"""Compatibility package for legacy `security` imports.

This repository's tests and tooling import the top-level package name
``security``. During the repo's validation runs, the `scripts/security`
package is the one that wins on the import path, so it must re-export the
real implementations from `src.security` rather than exposing an empty stub.
"""

from src.security import *  # noqa: F401,F403
from src.security import __all__  # noqa: F401
