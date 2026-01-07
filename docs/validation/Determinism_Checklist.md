# [Validation]: Determinism Checklist

> Generated: 2024-11-06 11:59:51 | Author: mbaetiong

Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

## Steps

1. Run full pipeline twice with no source changes.

```bash
python scripts/space_traversal/audit_runner.py run
python scripts/canonicalize_artifacts.py --out audit_artifacts/canonical_A.json

python scripts/space_traversal/audit_runner.py run
python scripts/canonicalize_artifacts.py --out audit_artifacts/canonical_B.json
```text

2. Compare sidecars.

```bash
diff -q audit_artifacts/canonical_A.json audit_artifacts/canonical_B.json && echo "Deterministic ✅"
```text

## Gates

| Gate | Condition | Outcome |
|------|-----------|---------|
| Canonical SHAs equal | true | Pass |
| Weight normalize warning | present | Acknowledge in manifest |
| Template hash drift | changed | Re-run full pipeline |

## Notes

- Ignore timestamps/paths; canonicalizer normalizes metadata.
- Investigate dynamic detector ordering if mismatch persists.
