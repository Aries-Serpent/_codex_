# codex-cognitive-sdk

Dependency-light contracts for integrating cognitive components without importing
the Codex monolith. The alpha boundary contains only immutable data contracts and
structural protocols for:

- governance authorization decisions;
- memory storage and retrieval; and
- Observe–Orient–Decide–Act (OODA) stages.

## Installation

This alpha package is not published on public PyPI. From the repository root,
install it from the checked-out source tree:

```console
python -m pip install ./packages/cognitive_sdk
```

The base package has no runtime dependencies. Implementations are supplied by
consumers through Python protocols; this distribution does not provide policy
engines, memory backends, orchestrators, or legacy adapters.

## Public API

Import supported contracts from the package root:

```python
from codex_cognitive_sdk import GovernanceProtocol, MemoryProtocol, OODAProtocol
```

Root exports are loaded lazily. The package never imports `codex`, `codex_ml`,
`cognitive_brain`, or `aries_serpent_core`.
