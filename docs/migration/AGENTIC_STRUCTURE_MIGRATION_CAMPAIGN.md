---
title: Agentic-Only Repository Structure Migration Campaign
type: plan
category: infrastructure
status: active
version: 1.0.0
last_updated: 2026-07-19T17:28:14Z
owner: orchestrator-agent
tags:
  - migration
  - agentic-structure
  - repository-governance
  - multi-lane-campaign
audience: agent
summary: Comprehensive multi-lane implementation plan for transitioning Aries-Serpent/_codex_ from mixed agentic documentation to strict agentic-only repository structure optimized for machine execution and autonomous agent operations.
depends_on: []
related_docs:
  - docs/AGENTIC_REPO_SYSTEM_GUIDE.md
  - docs/templates/CANONICAL_TEMPLATE.md
---

# Agentic-Only Repository Structure Migration Campaign

## Purpose

Transform `Aries-Serpent/_codex_` from a general agentic documentation standard to a **strict agentic-only repository structure** optimized exclusively for machine execution, deterministic parsing, and low-context autonomous agent decision-making.

## Scope

This campaign encompasses:
- 285+ GitHub Actions workflows with unified governance standards
- 152+ custom agents managed through structured registries
- ~100+ documentation directories spanning docs/, scripts/, .codex/, and configuration
- All markdown, YAML, JSON, and scripting artifacts that support agentic operations
- Link integrity, schema validation, and registry consistency
- Multi-phase execution across 7 parallel work lanes over 60 days

**Out of Scope**: Human-facing documentation, public API contracts, external CI/CD integrations

## Inputs

- Current repository structure (docs/, .codex/, scripts/, configs/)
- Existing validation tooling (tools/validate.py, tools/schema_diff.py, scripts/validate_*.py)
- CODEX_MANIFEST.json and AGENT_REGISTRY.yaml (current registries)
- Repository conventions and governance policies
- Custom agent roster (152 active agents with E-model autonomy)
- Problem statement source material on agentic-only standards

## Procedure

See **[Detailed Campaign Roadmap](#roadmap)** and **[Multi-Lane Implementation Guide](#lanes)** below.

### Current-State Analysis

**Current State**
- Mixed documentation conventions with optional frontmatter
- Inconsistent file naming and directory structure
- Link validation incomplete (108+ reported broken links, many false positives)
- Registry coverage partial (CODEX_MANIFEST.json, AGENT_REGISTRY.yaml)
- Validation tools scattered across scripts/; no unified framework
- Archive policy informal; no versioning or supersession tracking

**Target State**
- All canonical markdown documents use **mandatory YAML frontmatter** with deterministic metadata fields
- **Rigid templates** per artifact type (plan, report, guide, policy, index) with canonical section order
- **Registry-backed discovery** with hash-based integrity verification
- **Deterministic validation** enforced at CI gates: schema, template, link, naming, freshness, registry consistency
- **Lane-based autonomous execution** with parallel processing and minimal human intervention
- **Compatibility-safe migration** using alias/redirect stubs for all path changes

### Why This Migration Improves Agentic Autonomy

1. **Deterministic Routing**: Agents classify artifacts by metadata without semantic interpretation
2. **Low Context Overhead**: Rigid section order eliminates information search; agents process predictable structure
3. **Fast Retrieval**: Registry-backed discovery replaces full-text search; O(1) artifact lookup
4. **Schema Compliance**: Agents reject malformed documents before processing; prevents error cascades
5. **Cross-Lane Coordination**: Manifest references enable unambiguous handoffs between agents
6. **Autonomous Correction**: Validation gates catch schema drift, missing fields, naming violations automatically
7. **Reproducible Operations**: Identical metadata and structure guarantee deterministic parsing across sessions
8. **Token Efficiency**: Compressed metadata + predictable structure = fewer tokens for same information density

## Outputs

### Canonical Documentation Artifacts
- `docs/templates/CANONICAL_TEMPLATE.md` — master template with all required sections
- `docs/templates/TEMPLATE_TYPES.md` — type-specific templates (plan, report, guide, policy, index)
- `.codex/schemas/document_frontmatter.schema.json` — JSON Schema (strict validation contract)
- `.codex/schemas/document_frontmatter.schema.yaml` — YAML Schema
- `.codex/schemas/enum_definitions.yaml` — controlled vocabulary (types, categories, statuses)
- `.codex/schemas/template_sections.yaml` — canonical section definitions per type

### Migrated Directory Structure
```
docs/
├── index/          # Registries and indexes
├── plans/          # Planning documents (.plan.md)
├── reports/        # Audit and status reports (.report.md)
├── guides/         # Procedural how-to documents (.guide.md)
├── policies/       # Governance and rules (.policy.md)
├── state/          # Configs, registries, snapshots
├── archive/        # Versioned, superseded content
└── validation/     # Validation rules and conformance reports
```

### Registries & Manifests
- Updated `CODEX_MANIFEST.json` (v1.1.0 with artifact_registries subsections)
- `docs/index/plans-registry.json` + `.md`
- `docs/index/reports-registry.json` + `.md`
- `docs/index/guides-registry.json` + `.md`
- `docs/index/policies-registry.json` + `.md`
- `docs/index/ALL_ARTIFACTS_REGISTRY.json` + `.md` (consolidated)
- `scripts/.manifest.json` (script inventory with metadata)
- `docs/state/.manifest.json` (config/state inventory)

### Validation & Enforcement
- `tools/validate_agentic_structure.py` — unified validator (schema, template, link, naming, freshness, registry)
- `.github/workflows/validate-agentic-structure.yml` — CI gate enforcing standards
- `.codex/validation_profiles.yaml` — rule profiles (strict, lenient, report)
- `docs/validation/VALIDATION_RULES.md` — comprehensive validation documentation

### Archive & Governance
- `docs/archive/` — versioned, organized archive with INDEX and metadata
- `.codex/archive_policy.yaml` — documented archival criteria and procedures
- Redirect stubs (backward compatibility for all renamed docs)

## Decisions

| Decision | Rationale | Implication |
|----------|-----------|------------|
| **7-lane parallel execution** | Lanes are independent; parallelism reduces 60-day timeline to actual wall-clock time. Lanes 2-3 can complete while Lane 1 inventory runs. | Requires daily standup coordination; shared `.codex/lane_status.json` for sync |
| **YAML frontmatter mandatory for all canonical docs** | Machine-parseable metadata enables routing, versioning, ownership tracking, and freshness validation without parsing document body. | Breaking change for existing docs; migration via Lane 4 handles normalization |
| **Redirect stubs for all renamed paths** | Preserves backward compatibility; old paths remain functional via alias map and redirect stubs. | Minimal overhead (2-3 lines per stub); enables safe migration |
| **Strict CI gate post-Phase 5** | Prevents schema drift after migration; ensures all new/modified docs conform to standards. | Tuning required for false positive rate (target <1%) |
| **Registry checksums (SHA256)** | Detect unintended modifications to tracked artifacts; ensure integrity across agents. | Requires manifest update on every artifact change; automated in Lane 6 |
| **Archive as append-only** | Historical reference preserved; enables rollback and audit trail. No destructive deletions. | Storage cost minimal for 90-day retention window |

## Risks

| Risk | Mitigation | Owner |
|------|-----------|-------|
| **Broken relative links during migration** | Lane 3 builds comprehensive link graph; Lane 4 validates all links before commit; pre-commit hook catches remaining issues. | link-validator-agent |
| **Anchor drift (headings renamed, anchors break)** | Lane 3 builds anchor inventory; Lane 4 updates headings carefully; validation tool checks all references. | reference-updater-agent |
| **Code fence/Mermaid corruption** | Lane 4 counts fenced blocks before/after; regex validation for syntax; manual spot-checks. | reference-updater-agent |
| **Registry mismatch (stale entries)** | Lane 6 validates all entries against actual files; checksums verify integrity. | documentation-consolidator |
| **Over-aggressive archival** | Manual review of candidates; approval gate; archive as append-only; git history for restore. | repository-hygiene-agent |
| **Validation false positives** | Tune profiles (strict/lenient/report); document exemptions; iterate based on real PR feedback. | code-scanning-remediation-agent |
| **Agent coordination failure** | Daily standups; shared status tracking; phase gates between lanes. | orchestrator-agent |
| **Agent autonomy disruption** | Maintain backward-compatible CODEX_MANIFEST.json; alias map keeps old paths working. | documentation-consolidator |

## References

- **Problem Statement**: Agentic-Only Repository Structure specification (source material for this plan)
- **Existing Standards**: docs/AGENTIC_REPO_SYSTEM_GUIDE.md, docs/quality/BROKEN_LINKS_REPORT.md
- **Validation Tooling**: tools/validate.py, tools/schema_diff.py, scripts/validate_*.py
- **Agent Registry**: .github/agents/AGENT_REGISTRY.yaml (v1.9.0)
- **Governance**: docs/CODEBASE_AGENCY_POLICY.md, .codex/AGENTIC_REPO_STATE.md

---

## Roadmap

### Phase 0: Pre-Migration Freeze (Days 1-2)
- Freeze documentation changes (48-hour moratorium)
- Snapshot current state (git tag: `pre-migration-agentic-structure-2026-07-19`)
- Back up registries (CODEX_MANIFEST.json, AGENT_REGISTRY.yaml → .codex/archive/)
- Verify all tests passing (baseline for regression detection)

**Acceptance Criteria**: No pending doc PRs, all CI green, backups created, agent team briefed

---

### Phase 1: Discovery & Inventory (Days 3-7, Lane 1)
**Lead Agent**: recon-scout-agent

- Enumerate all .md files in docs/ and .codex/
- Classify by type (plan, report, guide, policy, index, template, redirect)
- Audit frontmatter presence and completeness
- Inventory scripts, configs, generated artifacts
- Identify broken link candidates, orphaned files
- Map directory structure and ownership

**Deliverables**:
- `docs/index/CANONICAL_ARTIFACT_INVENTORY.md`
- `.codex/lane1_inventory_classification.json`
- `.codex/lane1_frontmatter_audit.json`
- `.codex/lane1_broken_links_candidates.json`
- `.codex/lane1_orphaned_files_report.md`

**Acceptance Criteria**:
- ✅ 100% artifact enumeration
- ✅ >90% frontmatter coverage in canonical docs
- ✅ <5% broken link false positive rate
- ✅ <10 orphaned files without ownership

---

### Phase 2: Schema & Template Definition (Days 8-14, Lane 2)
**Lead Agent**: documentation-quality-agent

- Define required frontmatter fields: title, type, category, status, version, last_updated, owner, tags, audience
- Define optional fields: summary, depends_on, generated_by, source_ref, validation_profile, expiry, supersedes, related_docs, review_cycle, change_log
- Define enum values for type, category, status, validation_profile
- Create canonical templates for each document type
- Publish JSON Schema and YAML schema definitions
- Define canonical section order and heading structure

**Deliverables**:
- `docs/templates/CANONICAL_TEMPLATE.md`
- `docs/templates/TEMPLATE_TYPES.md`
- `.codex/schemas/document_frontmatter.schema.json`
- `.codex/schemas/document_frontmatter.schema.yaml`
- `.codex/schemas/enum_definitions.yaml`
- `.codex/schemas/template_sections.yaml`

**Acceptance Criteria**:
- ✅ Schema validates with jsonschema library
- ✅ Schema covers 100% of frontmatter fields
- ✅ Templates match schema exactly
- ✅ 5+ sample docs validate successfully

---

### Phase 3: Link Safety & Reference Reconciliation (Days 15-24, Lane 3)
**Lead Agent**: link-validator-agent

- Extract all relative and absolute internal links from .md files
- Extract all anchors (headings, HTML ids)
- Build link graph: source → target with anchor validation
- Categorize broken links (missing file, missing anchor, external, regex/template)
- Create alias map for renamed paths
- Prepare redirect stub templates

**Deliverables**:
- `.codex/lane3_link_graph.json`
- `.codex/lane3_broken_links_detail.json`
- `.codex/lane3_anchor_index.json`
- `.codex/lane3_alias_map.json`
- `docs/migration/LINK_SAFETY_PLAN.md`
- `docs/archive/REDIRECT_STUBS/` (prepared templates)

**Acceptance Criteria**:
- ✅ 100% internal link extraction
- ✅ <5% broken link false positive rate
- ✅ All anchors indexed
- ✅ All renamed paths in alias map

---

### Phase 4: Safe Migration Execution (Days 25-39, Lane 4)
**Lead Agent**: reference-updater-agent

**7 Batches (parallel where possible)**:
- B4.1: Migrate docs/plans/
- B4.2: Migrate docs/reports/
- B4.3: Migrate docs/guides/
- B4.4: Migrate docs/policies/
- B4.5: Migrate docs/state/ (configs)
- B4.6: Migrate docs/archive/
- B4.7: Migrate docs/index/

**Per-batch workflow**:
1. Normalize frontmatter (schema validation)
2. Normalize section headings (canonical order)
3. Update internal links (using Lane 3 alias map)
4. Create redirect stub in original location
5. Validate: schema + links + content integrity
6. Update CODEX_MANIFEST.json
7. Commit with message: `docs(migration): migrate {type} to canonical structure`

**Deliverables**:
- Migrated .md files in target directories
- Redirect stubs in original locations
- Updated CODEX_MANIFEST.json
- `.codex/lane4_migration_log.jsonl`
- `.codex/lane4_migration_report.md`

**Acceptance Criteria**:
- ✅ 100% of batches complete (no rollbacks)
- ✅ All frontmatter normalized and validated
- ✅ All section headings in canonical order
- ✅ All links updated and validated
- ✅ 0 content corruption (code blocks, Mermaid, HTML preserved)
- ✅ CODEX_MANIFEST.json consistent

---

### Phase 5: Validation & CI Enforcement (Days 40-47, Lane 5)
**Lead Agent**: code-scanning-remediation-agent

- Extend tools/validate.py to unified tools/validate_agentic_structure.py
- Implement schema validation, template validation, link validation, naming validation, freshness validation, registry validation
- Integrate pre-commit hook
- Deploy CI gate workflow (.github/workflows/validate-agentic-structure.yml)
- Define validation profiles (strict, lenient, report)
- Tune rules for <1% false positive rate

**Deliverables**:
- `tools/validate_agentic_structure.py`
- Pre-commit hook configuration
- `.github/workflows/validate-agentic-structure.yml`
- `.codex/validation_profiles.yaml`
- `docs/validation/VALIDATION_RULES.md`

**Acceptance Criteria**:
- ✅ Tool validates all 6 layers (schema, template, link, naming, freshness, registry)
- ✅ Pre-commit hook catches violations
- ✅ CI gate blocks non-conformant PRs
- ✅ <1% false positive rate
- ✅ All migrated docs pass strict validation

---

### Phase 6: Registry & Manifest Migration (Days 48-52, Lane 6)
**Lead Agent**: documentation-consolidator

- Update CODEX_MANIFEST.json to v1.1.0 (add artifact_registries, file_paths, checksums)
- Generate per-directory registries (plans, reports, guides, policies)
- Create consolidated ALL_ARTIFACTS_REGISTRY.json + .md
- Create script manifest (scripts/.manifest.json)
- Create config manifest (docs/state/.manifest.json)
- Update all markdown indexes to reference registries

**Deliverables**:
- Updated CODEX_MANIFEST.json (v1.1.0)
- `docs/index/plans-registry.json` + `.md`
- `docs/index/reports-registry.json` + `.md`
- `docs/index/guides-registry.json` + `.md`
- `docs/index/policies-registry.json` + `.md`
- `docs/index/ALL_ARTIFACTS_REGISTRY.json` + `.md`
- `scripts/.manifest.json`
- `docs/state/.manifest.json`
- `.codex/registry_migration_report.md`

**Acceptance Criteria**:
- ✅ All registry entries validated against actual files
- ✅ All checksums (SHA256) verified
- ✅ Manifest v1.1.0 schema valid
- ✅ Backward compatibility preserved (alias map populated)
- ✅ JSON parseable by agents (0 syntax errors)

---

### Phase 7: Archive & Cleanup (Days 53-57, Lane 7)
**Lead Agent**: repository-hygiene-agent

- Review archival candidates (stale, superseded, duplicate docs)
- Move superseded docs to docs/archive/ with versioning
- Add supersession markers (YAML frontmatter field + link to new version)
- Create archive index with metadata
- Document archive policy (criteria, retention windows, procedures)

**Deliverables**:
- `docs/archive/` (populated with versioned docs)
- `docs/archive/INDEX.md` + `.json`
- `.codex/lane7_archival_audit.md`
- `.codex/archive_policy.yaml`

**Acceptance Criteria**:
- ✅ All archived docs marked with `supersedes` field
- ✅ Archive index complete and searchable
- ✅ 0 broken links from current docs to archived docs
- ✅ Archive policy documented and reviewed

---

### Phase 8: Final Validation & Cutover (Days 58-60)
**Lead Agent**: unified-doc-agent

- Run full validation pass (all docs, all checks)
- Regression testing (link resolution, content integrity, schema compliance)
- Agent team sign-off (all lanes complete, no outstanding issues)
- Merge migration PR to main branch

**Deliverables**:
- `.codex/final_validation_report.md`
- `.codex/regression_test_results.json`
- `.codex/migration_completion_summary.md`

**Acceptance Criteria**:
- ✅ 100% strict validation pass
- ✅ 0 broken links
- ✅ 0 content corruption
- ✅ 0 schema drift
- ✅ All registries consistent
- ✅ All agents sign-off

---

## Critical Success Factors

1. **Zero Broken Links**: Every redirect stub and link update validated before commit
2. **No Content Loss**: Code blocks, Mermaid, HTML preserved bit-for-bit
3. **Schema Compliance**: 100% of canonical docs conform post-migration
4. **Agent Autonomy**: CODEX_MANIFEST.json, AGENT_REGISTRY.yaml, CI workflows remain functional
5. **Backward Compatibility**: All old paths resolve via redirects or alias map
6. **Validation Gates Active**: CI prevents non-conformant docs from merging post-Phase 5
7. **Registry Integrity**: All registries have checksums verified; no stale entries
8. **Parallel Coordination**: Lanes complete in order; phase gates enforced
9. **Audit Trail**: `.codex/lane*_*.jsonl` logs capture all operations
10. **Stakeholder Sign-Off**: @mbaetiong + orchestrator-agent approve cutover

---

## Change Log

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-19 | orchestrator-agent | Initial campaign plan published; 8 phases, 7 lanes, 60-day timeline |
