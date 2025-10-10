# [Doc]: Copilot Space Traversal Workflow (v1.1.0)
> Generated: 2025-10-10 04:02:13 UTC | Author: mbaetiong
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

## 4. Evidence Prioritization Heuristics
| Signal | Priority | Notes |
|--------|----------|-------|
| Direct pattern hit | High | Immediately increases functionality |
| Keyword variant (pluralization) | Medium | Future enhancement |
| Detector meta (e.g., layer tags) | Informational | Not scored yet |

## 5. Safeguard Keywords (Current Set)
`sha256`, `checksum`, `rng`, `seed`, `offline`, `WANDB_MODE`

## 6. Adding a Dynamic Detector
1) Place file under `scripts/space_traversal/detectors/`.
2) Implement `detect(file_index: dict) -> dict`.
3) Return contract MUST include: `id`, `evidence_files`, `found_patterns`, `required_patterns`.
4) Re-run: `python scripts/space_traversal/audit_runner.py stage S3`.

## 7. Determinism Guard Rails
| Guard | Implementation |
|-------|----------------|
| Sorted traversal | Use `sorted(Path.rglob())` |
| Read truncation | Cap file read length (200KB) |
| Hash chain | Manifest collects per-artifact SHA |
| Template fingerprint | Concatenate `.j2` files → SHA |
| Weight normalization | Auto-correct + record warning |

## 8. Diff & Explain
```bash
python scripts/space_traversal/audit_runner.py diff --old reports/capability_matrix_A.md --new reports/capability_matrix_B.md
python scripts/space_traversal/audit_runner.py explain checkpointing
```

## 9. Failure Mode Reference
| Issue | Likely Root | Mitigation |
|-------|-------------|------------|
| Missing capability ID | Detector file syntax error | Run S3 & inspect stderr |
| Score suppression | Required pattern rename | Update pattern list |
| High duplication ratio | Over-broad facet regex | Narrow facet patterns |
| Zero docs score | No doc token mention | Add docs anchor or synonyms list |

## 10. Manifest Anatomy (Excerpt)
```json
{
  "repo_root_sha": "<sha>",
  "artifacts": [{"name":"context_index.json","sha":"<sha>"}],
  "template_hash": "<sha>",
  "weights": {"functionality":0.25,"consistency":0.2,"tests":0.25,"safeguards":0.15,"documentation":0.15},
  "warnings": []
}
```

*End of Workflow Doc*
