# [Doc]: Copilot Space Traversal Workflow (v1.1.0)

 Roles: [Primary: Knowledge Ops], [Secondary: ML Platform Auditor]  Energy: 5

## 1. Objective
Codify a reproducible, explainable capability maturity assessment pipeline with deterministic outputs.

## 2. Flow (Conceptual)
```text
FILES
  ↓ (S1 Index: enumerate + hash)
FACETS
  ↓ (S2 Regex cluster)
CAPABILITIES_RAW
  ↓ (S3 Static + dynamic detectors)
CAPABILITIES_SCORED
  ↓ (S4 Component weighting)
GAPS
  ↓ (S5 Threshold segmentation)
REPORT (Markdown)
  ↓ (S6 Jinja rendering)
MANIFEST
  ↓ (S7 Integrity chain)
```

## 3. Component Score Formula
`score = Σ_i ( weight_i * clamp(component_i, 0, 1) )`
Weights normalized if Σ != 1.0 (warning added to manifest).

| Component | Computation |
|-----------|-------------|
| functionality | Hits / Required Patterns |
| consistency | 1 - duplication_ratio(evidence_files) |
| tests | (# test-linked files) / (# evidence files) (clamped) |
| safeguards | (# safeguard keywords with ≥1 hit) / (total safeguard keywords) |
| documentation | (# doc files containing capability token) / scaled corpus |

## 4. Safeguard Keywords
`sha256`, `checksum`, `rng`, `seed`, `offline`, `WANDB_MODE`

Extend by editing `SAFEGUARD_KEYWORDS` in `audit_runner.py`.

## 5. Determinism Guard Rails
| Guard | Implementation |
|-------|----------------|
| Sorted traversal | Use `sorted(Path.rglob())` |
| Read truncation | Cap file read length (200KB) |
| Hash chain | Manifest collects per-artifact SHA |
| Template fingerprint | Concatenate `.j2` files → SHA |
| Weight normalization | Auto-correct + record warning |

## 6. Commands
| Task | Command |
|------|---------|
| Full run | `python scripts/space_traversal/audit_runner.py run` |
| Single stage | `python scripts/space_traversal/audit_runner.py stage S4` |
| Explain score | `python scripts/space_traversal/audit_runner.py explain checkpointing` |
| Diff | `python scripts/space_traversal/audit_runner.py diff --old A --new B` |
| Fast path | `make space-audit-fast` |

*End of workflow doc*
