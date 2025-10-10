# [Doc]: Copilot Space Traversal Workflow (v1.1.0)
> Generated: 2025-10-10 01:58:00 UTC | Author: mbaetiong
Roles: [Knowledge Ops], [ML Platform Auditor]  Energy: 5

## 1) Objective
Codify a reproducible, explainable capability maturity assessment pipeline with deterministic outputs.

## 2) Flow
```text
FILES → (S1 Index) → FACETS → (S2 Regex cluster) → CAPABILITIES_RAW
→ (S3 Detectors) → CAPABILITIES_SCORED → (S4 Weights) → GAPS
→ (S5 Threshold) → REPORT (S6 Jinja) → MANIFEST (S7 Integrity)
```

## 3) Score Formula
score = Σ_i weight_i * clamp(component_i, 0..1) (weights normalized if Σ≠1)

| Component | Computation |
|-----------|-------------|
| functionality | Hits / Required Patterns |
| consistency | 1 − duplication_ratio(evidence_files) |
| tests | (# test-linked files) / (# evidence files) |
| safeguards | (# safeguard keywords with ≥1 hit) / total keywords |
| documentation | doc token hits / scaled corpus |

## 4) Safeguard Keywords
sha256, checksum, rng, seed, offline, WANDB_MODE (see audit_runner.py)

## 5) Determinism Guards
- Sorted traversal, truncated safe reads (200KB)
- Template fingerprint embedded (SHA of all .j2)
- Manifest includes repo_root_sha and per-artifact SHA

## 6) Detectors
Place under scripts/space_traversal/detectors/*.py with:
```python
def detect(file_index: dict) -> dict:
    return {"id":"new-cap","evidence_files":[],"found_patterns":[],"required_patterns":[],"meta":{}}
```

## 7) Diff / Explain
```bash
python scripts/space_traversal/audit_runner.py diff --old A --new B
python scripts/space_traversal/audit_runner.py explain checkpointing
```

## 8) Policy Gates
- Fail build if any score < low threshold
- Optional regression fail via options in workflow.yaml

*End of Workflow Doc*
