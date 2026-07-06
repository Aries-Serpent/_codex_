# Integration Guide

## Embedding in an External Repository

1. Install core wheel into project virtualenv.
2. Copy `.codex/network-policy.yaml` and keep fail-closed defaults.
3. Configure local persistence paths for session data.
4. Run smoke checks before enabling optional integrations.

## Cognitive Brain API Surface (Stable)

- `ObservationData`
- `OrientationResult`
- `Decision`
- `ActionResult`
- `Planner`
- `MemoryInterface`
- `MemoryPattern`
- `QuantumMemoryManager`
- `Pattern`
- `PatternSet`

## Example Import

```python
from cognitive_brain import ActionResult, Decision, ObservationData, OrientationResult, Planner
```

If your environment uses a prefixed package layout, resolve imports via your
installed distribution path (for example, through repository `src/`-mapped
packages) and keep this API surface consistent.

## Safe Networking Integration

Always gate outbound calls:

```python
from safety.network_policy import enforce_network_policy

enforce_network_policy("https://approved-host.example")
```
