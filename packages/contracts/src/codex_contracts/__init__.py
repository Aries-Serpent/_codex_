"""Public interoperability contracts for federated Codex packages."""

from .__about__ import __version__
from .artifacts import ArtifactReference
from .errors import ContractValidationError, ErrorEnvelope
from .events import EventEnvelope
from .plugins import CodexPlugin

__all__ = [
    "ArtifactReference",
    "CodexPlugin",
    "ContractValidationError",
    "ErrorEnvelope",
    "EventEnvelope",
    "__version__",
]
