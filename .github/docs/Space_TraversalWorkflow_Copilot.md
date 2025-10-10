# [Copilot Space Spec]: Traversal & Capability Audit Workflow (v1.1.0)
> Generated: 2025-10-10 03:27:51 UTC | Author: mbaetiong

Roles: [Primary: Audit Orchestrator], [Secondary: Capability Cartographer]  Energy: 5

## 1. Purpose
Define a deterministic, introspectable, extensible audit workflow for this Copilot Space to:
(a) harvest repository structure → (b) classify semantic facets → (c) extract capabilities → (d) score maturity → (e) surface gaps → (f) synthesize human + machine artifacts → (g) chain integrity metadata.

## 2. Update Highlights (v1.1.0)
| Area | Improvement | Rationale |
|------|------------|-----------|
| Dynamic Detectors | Automatic loading from `scripts/space_traversal/detectors/*.py` | Extensibility without core file edits |
| Diff Command | `audit_runner.py diff --old A --new B` | Direct matrix or JSON comparison |
| Explain Command | `audit_runner.py explain <cap_id>` | Transparent scoring breakdown |
| Determinism Guard | Hash sanity & weight normalization warnings | Prevent silent drift |
| Template Inputs | Added `template_hash` injection & artifact chain | Tamper detection |
| Enhanced Docs | “Failure Mode Radar” & “Quality Gates” sections | Faster troubleshooting |
| Scoring Refinement | Safeguard & test weighting validation | More stable maturity signals |
| Configurable Output | YAML fields for enabling/disabling stages | Customizable pipeline |

## 3. High-Level Stages
| Stage | ID | Inputs | Core Actions | Outputs | Idempotency |
|-------|----|--------|--------------|---------|-------------|
| Context Harvest | S1 | File tree | Enumerate, hash sample | `context_index.json` | Sorted list + SHA |
| Semantic Facets | S2 | Index | Pattern-based domain clustering | `facets.json` | Static regex map |
| Capability Extraction | S3 | Facets + detectors | Merge static rules + dynamic detectors | `capabilities_raw.json` | Alphabetic ID ordering |
| Scoring | S4 | Raw capabilities | Component scoring (weights normalized) | `capabilities_scored.json` | Pure function |
| Gap Analysis | S5 | Scored capabilities | Threshold segmentation & deficit tagging | `gaps.json` | Deterministic thresholds |
| Artifact Render | S6 | Scored + gaps + template | Jinja compile → markdown report | `reports/capability_matrix_<ts>.md` | Template hash |
| Provenance Manifest | S7 | All artifacts | Integrity chain & template fingerprint | `audit_run_manifest.json` | SHA aggregation |

## 4. Core Principles
| Principle | Enforcement Mechanism |
|-----------|-----------------------|
| Determinism | Sorted traversal, truncated safe reads, normalized weights |
| Transparency | Explain command + JSON component breakdown |
| Extensibility | Pluggable detectors directory + YAML toggles |
| Safety | Offline only, no network calls, hash provenance |
| Minimal Mutation | Only writes under `audit_artifacts/`, `reports/`, manifest root file |
| Fast Feedback | Single-stage invocations for iterative tuning |

## 5. Directory Layout
| Path | Description |
|------|-------------|
| `scripts/space_traversal/` | Orchestration, scoring, detectors |
| `scripts/space_traversal/detectors/` | Drop-in capability detectors |
| `templates/audit/` | Jinja2 templates |
| `audit_artifacts/` | Intermediate JSON outputs |
| `reports/` | Published markdown matrices |
| `.copilot-space/workflow.yaml` | Declarative pipeline config |

## 6. Scoring Components (Weights Default)
| Component | Weight | Definition | Signals |
|-----------|-------:|------------|---------|
| functionality | 0.25 | Presence & minimal viability | Required pattern hits |
| consistency | 0.20 | Non-duplication & single-source | Dup ratio inverse |
| tests | 0.25 | Breadth of direct + indirect test coverage | Test file/evidence ratio |
| safeguards | 0.15 | Integrity, reproducibility, offline gating | Keyword presence map |
| documentation | 0.15 | Clear doc references | Doc corpus incidence |

## 7. Integrity Chain (Manifest)
| Field | Meaning |
|-------|---------|
| `repo_root_sha` | SHA256 of sorted file listing |
| `artifacts[].sha` | Hash per intermediate JSON |
| `template_hash` | Concatenated hash of all Jinja templates |
| `weights` | Effective normalized weights |
| `warnings` | Normalization / missing stage notes |

## 8. Extending with a Detector
| Step | Action |
|------|--------|
| 1 | Create `scripts/space_traversal/detectors/<id>.py` |
| 2 | Implement `def detect(file_index: dict) -> dict:` returning capability object |
| 3 | Ensure unique `id`, include `required_patterns` list |
| 4 | Re-run S3 (auto-load) |
| 5 | Validate presence in `capabilities_raw.json` then final matrix |

*End of Spec*
