# [Copilot Space Spec]: Traversal & Capability Audit Workflow (v1.1.0)
> Generated: 2025-10-10 04:31:26 UTC | Author: mbaetiong

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
| Docs Synonyms | Broader keyword matching via `DOCS_SYNONYMS_MAP` | Improve doc signal recall |
| Component Caps | Optional `scoring.component_caps` clamps | Bound component influence deterministically |

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
| Path | Description | Added In |
|------|-------------|----------|
| `scripts/space_traversal/` | Orchestration, scoring, detectors | v1.0 |
| `scripts/space_traversal/detectors/` | Drop-in capability detectors | v1.1 |
| `templates/audit/` | Jinja2 templates | v1.0 |
| `audit_artifacts/` | Intermediate JSON outputs | v1.0 |
| `reports/` | Published markdown matrices | v1.0 |
| `.copilot-space/workflow.yaml` | Declarative pipeline config | v1.0 |

## 6. Scoring Components (Weights Default)
| Component | Weight | Definition | Signals |
|-----------|-------:|------------|---------|
| functionality | 0.25 | Presence & minimal viability | Required pattern hits |
| consistency | 0.20 | Non-duplication & single-source | Dup ratio inverse |
| tests | 0.25 | Breadth of direct + indirect test coverage | Test file/evidence ratio |
| safeguards | 0.15 | Integrity, reproducibility, offline gating | Keyword presence map |
| documentation | 0.15 | Clear doc references | Doc corpus incidence |

Weights must sum to 1.0; normalization occurs if drift detected (manifest notes warning).

## 7. Duplicate Implementation Heuristic
| Criterion | Rule |
|----------|------|
| File Stem Overlap | Same stem appears >1 time inside capability evidence |
| Adjusted Dup Ratio | `(duplicate_instances) / total_evidence_files` (clamped) |
| Similarity Path Check (future) | Planned introduction of token-level similarity (Phase II) |

## 8. Safeguard Signals
| Keyword | Category | Example |
|---------|----------|---------|
| `sha256` | Integrity | Checkpoint hashing |
| `checksum` | Integrity | Dataset manifest |
| `rng` | Repro | RNG state persistence |
| `seed` | Repro | Deterministic seeding |
| `offline` | Network guard | W&B / MLflow offline |
| `WANDB_MODE` | Network guard | Force offline mode |

## 9. Execution Entrypoints
| Command | Function |
|---------|----------|
| `python scripts/space_traversal/audit_runner.py run` | Full pipeline S1→S7 |
| `python scripts/space_traversal/audit_runner.py stage S4` | Run single stage |
| `python scripts/space_traversal/audit_runner.py diff --old A --new B` | Compare two reports / score JSON |
| `python scripts/space_traversal/audit_runner.py explain <cap_id>` | Print component breakdown |
| `make space-audit` | Convenience wrapper |
| `make space-audit-fast` | Minimal subset (S1,S3,S4,S6) |

## 10. YAML Configuration Keys
| Path | Type | Example | Description |
|------|------|---------|-------------|
| `version` | semver | `1.1.0` | Workflow spec version |
| `stages` | list | IDs S1..S7 | Execution ordering |
| `weights` | map | component weights | Overrides defaults |
| `scoring.thresholds.low` | float | `0.70` | Low maturity gating |
| `scoring.thresholds.medium` | float | `0.85` | Higher maturity label |
| `capability_map.overrides` | map | merge arrays | ID merging / aliasing |
| `capability_map.dynamic` | bool | `true` | Enable detector discovery |
| `output.reports_dir` | str | `reports` | Where matrix saved |
| `output.artifacts_dir` | str | `audit_artifacts` | Intermediates location |

## 11. Integrity Chain (Manifest)
| Field | Meaning |
|-------|---------|
| `repo_root_sha` | SHA256 of sorted file listing |
| `artifacts[].sha` | Hash per intermediate JSON |
| `template_hash` | Concatenated hash of all Jinja templates |
| `weights` | Effective normalized weights |
| `warnings` | Normalization / missing stage notes |

## 12. Extending with a Detector
| Step | Action |
|------|--------|
| 1 | Create `scripts/space_traversal/detectors/<id>.py` |
| 2 | Implement `def detect(file_index: dict) -> dict:` returning capability object |
| 3 | Ensure unique `id`, include `required_patterns` list |
| 4 | Re-run S3 (auto-load) |
| 5 | Validate presence in `capabilities_raw.json` then final matrix |

Detector Return Contract:
```python
{
  "id": "inference-serving",
  "evidence_files": ["src/.../server.py"],
  "found_patterns": ["fastapi"],
  "required_patterns": ["server", "fastapi"],
  "meta": {"layer":"serving"}
}
```

## 13. Failure Mode Radar
| Symptom | Stage | Root Cause | Remediation |
|---------|-------|-----------|-------------|
| Missing capability in matrix | S3 | Detector not loaded / dynamic disabled | Enable `capability_map.dynamic` or fix import error |
| Score = 0 unexpectedly | S4 | Patterns mismatched or renamed | Adjust `required_patterns` / update detector |
| Template hash mismatch | S7 | Template edited post-run | Re-run full pipeline |
| High duplication inflation | S4 | Broad facet pattern capturing unrelated files | Refine regex domain patterns |
| No low maturity flagged but expected | S5 | Threshold too low | Adjust `scoring.thresholds.low` |

## 14. Quality Gates (Optional Policy)
| Gate | Condition | Action |
|------|-----------|--------|
| Fail Build (Low) | Any capability < low threshold | Exit non-zero |
| Warn Drift | >5% delta vs last manifest | Print diff summary |
| Warn Weight Normalize | Provided weights sum != 1 | Log normalization warning |
| Fail Missing Detector | Detector referenced but not loaded | Exit non-zero |

## 15. Prompt Hints (Copilot Space)
| Intent | Prompt |
|--------|--------|
| Regenerate audit | "Run the space audit workflow now." |
| List weak areas | "List all capabilities below threshold." |
| Show provenance | "Display manifest integrity chain." |
| Explain score | "Explain capability checkpointing score." |

## 16. Security & Offline Policy
| Concern | Measure |
|---------|---------|
| Network avoidance | No external imports beyond installed libs |
| Hash tamper detection | Manifest + template hash chain |
| Controlled writes | Paths restricted to configured output dirs |
| Execution isolation | Stage-specific invocation possible |

## 17. Determinism Validation Steps
1. Run full pipeline twice with no code changes.
2. Compare JSON artifact hashes (excluding timestamp).
3. Expect identical `repo_root_sha` & identical `capabilities_scored.json` content.
4. If diverged → inspect nondeterministic detector logic (e.g., random ordering).

## 18. Maintenance Cadence
| Interval | Tasks |
|----------|-------|
| Weekly | Run audit; review deltas; commit if material |
| Monthly | Rebalance weights; refine detectors |
| Quarterly | Validate duplication heuristic vs manual review; rotate safeguard keywords |

## 19. Upgrade Path (Future)
| Version | Planned Feature |
|---------|-----------------|
| 1.2.x | Token-level similarity duplicate heuristic |
| 1.3.x | Coverage XML ingestion for real test depth |
| 1.4.x | Multi-report trend aggregation & sparkline rendering |
| 2.0.0 | Multi-repo federated capability indexing |

## 20. Pre-Commit Checklist
- [ ] All stages S1–S7 succeeded
- [ ] Weight normalization produced no warnings (or justified)
- [ ] Manifest integrity chain verified
- [ ] Diff summary appended in commit message
- [ ] New detectors documented in Appendix (if added)

*End of Spec*
