---
title: Agentic Structure Migration Campaign – Executive Summary
type: report
category: infrastructure
status: active
version: 1.0.0
last_updated: 2026-07-19T17:28:14Z
owner: orchestrator-agent
tags:
  - migration
  - governance
  - campaign-overview
audience: agent
summary: High-level overview of the agentic-only repository structure migration campaign, objectives, timeline, and success criteria.
---

# Agentic Structure Migration Campaign – Executive Summary

## Objective

Transition `Aries-Serpent/_codex_` from a mixed agentic documentation standard to a **strict agentic-only repository structure** optimized for:
- **Machine execution** (deterministic parsing, low context)
- **Autonomous agent operations** (registry-backed discovery, schema validation)
- **Predictable structure** (rigid templates, canonical section order, controlled metadata)

## Current State

- **Documentation**: Mixed conventions, optional frontmatter, inconsistent naming
- **Links**: 108+ reported broken links (many false positives); no comprehensive link graph
- **Registries**: Partial coverage (CODEX_MANIFEST.json, AGENT_REGISTRY.yaml); no per-type indexes
- **Validation**: Scattered tools (validate.py, schema_diff.py, validate_*.py); no unified gate
- **Archive**: Informal policy; no versioning or supersession tracking
- **Agents**: 152 active agents (E-model); registry-based discovery functional but incomplete

## Target State

| Aspect | Target |
|--------|--------|
| **Frontmatter** | Mandatory YAML with 9 required fields (title, type, category, status, version, last_updated, owner, tags, audience) |
| **Templates** | Canonical per document type (plan, report, guide, policy, index); rigid section order (Purpose, Scope, Inputs, Procedure, Outputs, Decisions, Risks, References, Change Log) |
| **Naming** | Deterministic kebab-case with suffixes (.plan.md, .report.md, .guide.md, .policy.md) |
| **Directory** | Canonical lanes (docs/plans/, docs/reports/, docs/guides/, docs/policies/, docs/state/, docs/index/, docs/archive/) |
| **Links** | Comprehensive link graph; validated anchors; alias map for renamed paths; redirect stubs for backward compatibility |
| **Registries** | CODEX_MANIFEST.json v1.1.0; per-type registries (plans, reports, guides, policies); consolidated ALL_ARTIFACTS_REGISTRY; script/config manifests |
| **Validation** | Unified tool (tools/validate_agentic_structure.py); 6 validation layers (schema, template, link, naming, freshness, registry); CI gate; <1% false positive rate |
| **Archive** | Append-only docs/archive/; versioned, indexed; supersession markers; documented policy |

## Campaign Structure

**7 Parallel Lanes** (coordinated via daily standup, shared status tracking):

| Lane | Objective | Duration | Lead |
|------|-----------|----------|------|
| **1** | Inventory & classification | 5 days | recon-scout-agent |
| **2** | Schema & templates | 7 days | documentation-quality-agent |
| **3** | Link safety & references | 10 days | link-validator-agent |
| **4** | Safe migration (7 batches) | 15 days | reference-updater-agent |
| **5** | Validation & CI enforcement | 8 days | code-scanning-remediation-agent |
| **6** | Registries & manifests | 5 days | documentation-consolidator |
| **7** | Archive & cleanup | 5 days | repository-hygiene-agent |
| **8** | Final validation & cutover | 3 days | unified-doc-agent |

**Timeline**: 60 calendar days (wall-clock time with parallelization)  
**Start Date**: 2026-07-19 (after Phase 0 freeze)  
**Cutover Target**: 2026-09-17 (merge to main)

## Key Constraints

✅ **NO broken links** — alias map, redirect stubs, link validation  
✅ **NO content corruption** — code block counts verified, Mermaid/HTML preserved  
✅ **NO uncontrolled renames** — all path changes in manifest before applying  
✅ **NO schema drift** — CI gate enforces compliance post-Phase 5  
✅ **NO agent disruption** — CODEX_MANIFEST, AGENT_REGISTRY, handoff protocols maintained throughout

## Success Criteria

- ✅ 100% of canonical docs use mandatory frontmatter with required fields
- ✅ 100% of canonical docs follow canonical section order
- ✅ 100% of internal links resolve correctly (no broken references)
- ✅ 0 code fence / Mermaid block corruption
- ✅ All registries validated; checksums match actual files
- ✅ All agents report: lane complete, no outstanding issues
- ✅ CI gate active; validation <1% false positive rate
- ✅ @mbaetiong + orchestrator-agent sign-off on cutover

## Deliverables (Grouped by Lane)

### Lane 2 (Schema & Templates)
- `docs/templates/CANONICAL_TEMPLATE.md` — master template
- `docs/templates/TEMPLATE_TYPES.md` — type-specific variants
- `.codex/schemas/document_frontmatter.schema.json` — validation contract
- `.codex/schemas/enum_definitions.yaml` — controlled vocabulary

### Lane 3 (Link Safety)
- `.codex/lane3_link_graph.json` — complete dependency graph
- `.codex/lane3_alias_map.json` — old_path → new_path mappings
- `docs/archive/REDIRECT_STUBS/` — prepared redirect templates
- `docs/migration/LINK_SAFETY_PLAN.md` — detailed strategy

### Lane 4 (Migration)
- Migrated .md files in canonical directories
- Redirect stubs in original locations (backward compatibility)
- Updated CODEX_MANIFEST.json
- `.codex/lane4_migration_log.jsonl` — operation audit trail

### Lane 5 (Validation)
- `tools/validate_agentic_structure.py` — unified validator
- `.github/workflows/validate-agentic-structure.yml` — CI gate
- `.codex/validation_profiles.yaml` — rule profiles
- `docs/validation/VALIDATION_RULES.md` — rule documentation

### Lane 6 (Registries)
- Updated CODEX_MANIFEST.json (v1.1.0)
- `docs/index/plans-registry.json`, `reports-registry.json`, `guides-registry.json`, `policies-registry.json`
- `docs/index/ALL_ARTIFACTS_REGISTRY.json` — consolidated
- `scripts/.manifest.json`, `docs/state/.manifest.json` — script/config inventory

### Lane 7 (Archive)
- `docs/archive/` (versioned, indexed)
- `docs/archive/INDEX.md` + `.json`
- `.codex/archive_policy.yaml` — policy documentation

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Broken links | Lane 3 builds link graph; Lane 4 validates all links before commit; pre-commit hook catches remaining |
| Content corruption | Lane 4 counts fenced blocks before/after; regex validation for syntax; manual spot-checks |
| Registry mismatch | Lane 6 validates all entries against files; checksums verify integrity |
| Validation false positives | Tune profiles (strict/lenient/report); document exemptions; iterate based on PR feedback |
| Agent autonomy disruption | Maintain backward-compatible manifest; alias map keeps old paths working |

## Governance & Authority

- **Authority**: @mbaetiong D-tier autonomous; all agent decisions binding
- **Coordination**: Daily standup with all lane leads; shared `.codex/lane_status.json`
- **Freezing**: Phase 0 moratorium on doc changes (48 hours)
- **Phase Gates**: Each phase requires predecessor completion; rollback available per lane
- **Sign-Off**: orchestrator-agent + @mbaetiong approval required before main cutover

## Next Steps

1. **Phase 0 (Days 1-2)**: Freeze docs; snapshot state; brief agent team
2. **Phase 1-3 (Days 3-24)**: Lanes 1-3 execute in parallel (inventory, schema, link safety)
3. **Phase 4 (Days 25-39)**: Lane 4 executes migration (batches can parallelize)
4. **Phase 5-7 (Days 40-57)**: Lanes 5-7 execute in parallel (validation, registries, archive)
5. **Phase 8 (Days 58-60)**: Final validation and cutover to main

---

**Document Version**: 1.0.0  
**Last Updated**: 2026-07-19T17:28:14Z  
**Campaign Status**: PLANNING → READY FOR PHASE 0 EXECUTION
