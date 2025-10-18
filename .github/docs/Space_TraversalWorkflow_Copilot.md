# [Copilot Space Spec]: Traversal & Capability Audit Workflow (v1.1.0)
> Generated: 2025-10-18 09:19:02 UTC | Author: mbaetiong

 Roles: [Primary: Audit Orchestrator], [Secondary: Capability Cartographer]  Energy: 5

## 1. Purpose
Define a deterministic, introspectable, extensible audit workflow for this Copilot Space to:
(a) harvest repository structure → (b) classify semantic facets → (c) extract capabilities → (d) score maturity → (e) surface gaps → (f) synthesize human + machine artifacts → (g) chain integrity metadata.

## 2. Update Highlights (v1.1.0)
| Area | Improvement | Rationale |
|------|------------|-----------|
| Dynamic Detectors | Auto-loading from `scripts/space_traversal/detectors/*.py` | Extensibility without core edits |
| Diff Command | `audit_runner.py diff --old A --new B` | Compare matrices/JSON |
| Explain Command | `audit_runner.py explain <cap_id>` | Transparent scoring breakdown |
| Determinism Guard | Weight normalization warnings | Prevent silent drift |
| Template Inputs | `template_hash` injection | Tamper detection |
| Scoring Refinement | Component caps (optional) | Control component influence |
| Consistency Heuristic | Optional token-similarity (scaffold) | Smoother duplication signal |

## 3. High-Level Stages
| Stage | ID | Inputs | Core Actions | Outputs | Idempotency |
|-------|----|--------|--------------|---------|-------------|
| Context Harvest | S1 | File tree | Enumerate, hash sample | `context_index.json` | Sorted list + SHA |
| Semantic Facets | S2 | Index | Regex domain clustering | `facets.json` | Static regex map |
| Capability Extraction | S3 | Facets + detectors | Merge static + dynamic | `capabilities_raw.json` | Alphabetic ID ordering |
| Scoring | S4 | Raw capabilities | Caps + weighting (auto-normalize) | `capabilities_scored.json` | Pure function |
| Gap Analysis | S5 | Scored capabilities | Threshold segmentation | `gaps.json` | Deterministic thresholds |
| Artifact Render | S6 | Scored + gaps + template | Jinja compile → markdown | `reports/capability_matrix_<ts>.md` | Template hash |
| Provenance Manifest | S7 | All artifacts | Integrity chain + template hash | `audit_run_manifest.json` | SHA aggregation |

## 4. New Options (v1.1.0)
```yaml
scoring:
  component_caps:
    functionality: 1.0
    consistency: 1.0
    tests: 1.0
    safeguards: 1.0
    documentation: 1.0
  dup:
    heuristic: simple  # or token_similarity (experimental)
```

## 5. Meta Rendering
- Detectors may return `meta` (dictionary) along with evidence/patterns.
- Meta is informational only (not scored) and renders under each capability.

## 6. Integrity Chain (Manifest)
| Field | Meaning |
|-------|---------|
| `repo_root_sha` | SHA256 of sorted file listing |
| `artifacts[].sha` | Hash per intermediate JSON |
| `template_hash` | Concatenated Jinja templates hash |
| `weights` | Effective normalized weights |
| `warnings` | Scoring normalization or stage notes |

*End of Spec*
