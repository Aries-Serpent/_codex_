# [Copilot Space Spec]: Traversal & Capability Audit Workflow (v1.1.0)

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

## 4. Source Enumeration Exclusions (S1)
The following directory prefixes are ignored to prevent evidence pollution:
`.git/`, `.venv/`, `venv/`, `.tox/`, `.mypy_cache/`, `.pytest_cache/`, `.cache/`, `node_modules/`, `dist/`, `build/`, `audit_artifacts/`, `reports/`.

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

Weights must sum to 1.0; normalization occurs if drift detected (manifest notes warning).

## 7. Execution Entrypoints
| Command | Function |
|---------|----------|
| `python scripts/space_traversal/audit_runner.py run` | Full pipeline S1→S7 |
| `python scripts/space_traversal/audit_runner.py stage S4` | Run single stage |
| `python scripts/space_traversal/audit_runner.py diff --old A --new B` | Compare two reports / score JSON |
| `python scripts/space_traversal/audit_runner.py explain <cap_id>` | Print component breakdown |
| `make space-audit-fast` | Minimal subset (S1,S3,S4,S6) |

## 8. Integrity Chain (Manifest)
| Field | Meaning |
|-------|---------|
| `repo_root_sha` | SHA256 of sorted file listing |
| `artifacts[].sha` | Hash per intermediate JSON |
| `template_hash` | Concatenated hash of all Jinja templates |
| `weights` | Effective normalized weights |
| `warnings` | Normalization / missing stage notes |

*End of Spec*
