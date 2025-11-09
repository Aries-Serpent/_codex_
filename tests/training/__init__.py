"""Training test package with optional dependency guards."""

from tests.helpers.optional_dependencies import import_optional_dependency

import_optional_dependency("torch", allow_stub=False)
