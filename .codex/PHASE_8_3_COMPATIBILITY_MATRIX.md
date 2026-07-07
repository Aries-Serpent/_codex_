# 📋 PHASE 8.3 — WINDOWS COMPATIBILITY MATRIX

**Workstream:** 8.3.2 — Compatibility Planning  
**Track Lead:** cross-platform-filename-validator (Track 8.3)  
**Authority:** @mbaetiong (D-tier autonomy)  
**Input:** PHASE_8_3_PLATFORM_AUDIT_REPORT.md (WS1 deliverable)  
**Generated:** 2026-07-07T14:26Z  
**Status:** Planning Phase (WS2) — Ready for WS3 (Execution)

---

## 1. EXECUTIVE SUMMARY

This matrix documents **13 blocking case-collision file groups** (28 total files) identified in the WS1 
audit. It establishes:

1. **Canonical file selection** for each collision group
2. **De-collision sequence** (dependencies and ordering)
3. **Reference update scope** (which files must be updated)
4. **Blast radius** per group
5. **Coordination points** with Track 8.1 and 8.2

**Key insight:** All 13 groups are Markdown documentation files in `docs/`, `.codex/reports/`, and 
`reports/` directories. **None are source code**, limiting functional impact to documentation 
link integrity. However, case collisions cause **silent file loss** on Windows/macOS checkouts, 
making them a **BLOCKING** issue for cross-platform support.

**De-collision must happen FIRST** before Track 8.2 bulk directory moves to avoid cascading 
reference failures.

---

## 2. CASE-COLLISION MATRIX (13 Groups)

Each group is ranked by:
- **Internal links affected** (pages within repo linking to this file)
- **External backlinks** (external projects linking to GitHub docs)
- **Documentation hierarchy** (root-level vs. deeply nested)

### GROUP 1: ARCHITECTURE.md (3-way collision — HIGHEST PRIORITY)

| Collision Set | Canonical Choice | Rationale | Link Count |
|---------------|------------------|-----------|-----------|
| `docs/ARCHITECTURE.md`<br/>`docs/Architecture.md`<br/>`docs/architecture.md` | **`docs/architecture.md`** | Lowercase convention is standard in modern docs (see GNU/Python/MDN); minimizes case inconsistency across remaining files. 3-way collision is unique — higher risk. | TBD |

**Content merge strategy:**
- Examine all three files for content gaps.
- If `ARCHITECTURE.md` and `Architecture.md` are duplicates, consolidate into `architecture.md`.
- If they have unique sections, merge into canonical file.

**Internal references to update:**
- Grep for `ARCHITECTURE.md`, `Architecture.md` in `.md` files and `.py` docstrings.
- Check `mkdocs.yml` navigation entries.

**External backlinks:** Likely (architecture docs frequently linked externally).

**Blast radius:** **MEDIUM** (core architectural doc; many internal cross-refs expected).

---

### GROUP 2: CI.md (2-way collision)

| Collision Set | Canonical Choice | Rationale | Link Count |
|---------------|------------------|-----------|-----------|
| `docs/CI.md`<br/>`docs/ci.md` | **`docs/ci.md`** | Consistency with lowercase convention. | TBD |

**Merge strategy:** Likely duplicates (both document CI). Consolidate.

**Blast radius:** **LOW–MEDIUM** (CI docs are specialized; fewer cross-refs expected).

---

### GROUP 3: CLI.md (2-way collision)

| Collision Set | Canonical Choice | Rationale | Link Count |
|---------------|------------------|-----------|-----------|
| `docs/CLI.md`<br/>`docs/cli.md` | **`docs/cli.md`** | Consistency with lowercase convention. | TBD |

**Merge strategy:** Likely duplicates. Consolidate.

**Blast radius:** **LOW–MEDIUM** (CLI docs are specialized).

---

### GROUP 4: QUALITY_GATES.md (2-way collision)

| Collision Set | Canonical Choice | Rationale | Link Count |
|---------------|------------------|-----------|-----------|
| `docs/QUALITY_GATES.md`<br/>`docs/quality_gates.md` | **`docs/quality_gates.md`** | Consistency with lowercase convention. | TBD |

**Merge strategy:** Likely duplicates. Consolidate.

**Blast radius:** **LOW** (specialized QA doc).

---

### GROUP 5: QUICKSTART.md (2-way collision)

| Collision Set | Canonical Choice | Rationale | Link Count |
|---------------|------------------|-----------|-----------|
| `docs/QUICKSTART.md`<br/>`docs/quickstart.md` | **`docs/quickstart.md`** | Consistency with lowercase convention. Also check for `QUICKSTART_BY_PROFILE.md` at repo root (may be canonical source). | TBD |

**Merge strategy:** Consolidate. Note: Repo root `QUICKSTART_BY_PROFILE.md` (uppercase) may be the primary quickstart — verify it doesn't need downcase rename too.

**Blast radius:** **MEDIUM** (quickstart is entry point for developers).

---

### GROUP 6: TROUBLESHOOTING.md (2-way collision)

| Collision Set | Canonical Choice | Rationale | Link Count |
|---------------|------------------|-----------|-----------|
| `docs/TROUBLESHOOTING.md`<br/>`docs/troubleshooting.md` | **`docs/troubleshooting.md`** | Consistency with lowercase convention. | TBD |

**Merge strategy:** Consolidate.

**Blast radius:** **LOW–MEDIUM** (troubleshooting is high-traffic for users).

---

### GROUP 7: docs/agent/INDEX.md (2-way collision)

| Collision Set | Canonical Choice | Rationale | Link Count |
|---------------|------------------|-----------|-----------|
| `docs/agent/INDEX.md`<br/>`docs/agent/index.md` | **`docs/agent/index.md`** | Lowercase convention; `index.md` is standard for directory landing pages. | TBD |

**Merge strategy:** Consolidate.

**Blast radius:** **LOW–MEDIUM** (agent docs are substantial subsection).

---

### GROUP 8: docs/guides/INDEX.md (2-way collision)

| Collision Set | Canonical Choice | Rationale | Link Count |
|---------------|------------------|-----------|-----------|
| `docs/guides/INDEX.md`<br/>`docs/guides/index.md` | **`docs/guides/index.md`** | Lowercase convention; `index.md` is standard directory landing page. | TBD |

**Merge strategy:** Consolidate.

**Blast radius:** **LOW–MEDIUM** (guides subsection).

---

### GROUP 9: docs/guides/QUICKSTART.md (2-way collision)

| Collision Set | Canonical Choice | Rationale | Link Count |
|---------------|------------------|-----------|-----------|
| `docs/guides/QUICKSTART.md`<br/>`docs/guides/quickstart.md` | **`docs/guides/quickstart.md`** | Consistency with lowercase convention + Groups 5 & 9 should use same casing. | TBD |

**Merge strategy:** Consolidate.

**Blast radius:** **MEDIUM** (guides are high-traffic).

---

### GROUP 10: docs/security/INCIDENT_RESPONSE.md (2-way collision)

| Collision Set | Canonical Choice | Rationale | Link Count |
|---------------|------------------|-----------|-----------|
| `docs/security/INCIDENT_RESPONSE.md`<br/>`docs/security/incident_response.md` | **`docs/security/incident_response.md`** | Consistency with lowercase convention. | TBD |

**Merge strategy:** Consolidate.

**Blast radius:** **LOW–MEDIUM** (security docs are specialized).

---

### GROUP 11: docs/validation/Tokenization_Validation.md (2-way collision)

| Collision Set | Canonical Choice | Rationale | Link Count |
|---------------|------------------|-----------|---------|
| `docs/validation/Tokenization_Validation.md`<br/>`docs/validation/tokenization_Validation.md` | **`docs/validation/tokenization_validation.md`** | **Note:** Neither existing file is fully lowercase. Recommend standardize to `tokenization_validation.md` (all lowercase). Unusual case-mix suggests accidental duplication. | TBD |

**Merge strategy:** Consolidate both files into `tokenization_validation.md`.

**Blast radius:** **LOW** (specialized validation docs).

---

### GROUP 12: .codex/reports/EXECUTIVE_SUMMARY.md (2-way collision)

| Collision Set | Canonical Choice | Rationale | Link Count |
|---------------|------------------|-----------|---------|
| `.codex/reports/EXECUTIVE_SUMMARY.md`<br/>``.codex/reports/executive_summary.md` | **`.codex/reports/executive_summary.md`** | Consistency with lowercase convention; internal artifact docs. | TBD |

**Merge strategy:** Consolidate.

**Blast radius:** **LOW** (internal artifact; limited external links).

---

### GROUP 13: reports/EXECUTIVE_SUMMARY.md (2-way collision)

| Collision Set | Canonical Choice | Rationale | Link Count |
|---------------|------------------|-----------|---------|
| `reports/EXECUTIVE_SUMMARY.md`<br/>`reports/executive_summary.md` | **`reports/executive_summary.md`** | Consistency with lowercase convention; internal artifact docs. | TBD |

**Merge strategy:** Consolidate.

**Blast radius:** **LOW** (internal artifact; limited external links).

---

## 3. DE-COLLISION SEQUENCING

### Execution Order (MUST preserve dependency order)

The de-collision must happen in **two phases:**

#### **Phase A: Analysis & Reference Mapping** (non-destructive)
Before renaming any file, identify all internal references:

1. **Build reference graph:**
   ```bash
   # For each collision group:
   grep -r "ARCHITECTURE\|Architecture\|architecture" --include="*.md" --include="*.py" --include="*.yml" .
   # (Repeat for all 13 groups)
   ```

2. **Document external backlinks:** Check GitHub search for off-repo links.

3. **Create merge plan:** For each group, decide if files are duplicates or contain unique content.

**Deliverable:** `.codex/PHASE_8_3_CASE_COLLISION_REFERENCE_MAP.md`

---

#### **Phase B: Consolidation & De-collision** (file system changes)

Execute in this order to minimize ripple effects:

| Step | Group | Action | Risk |
|------|-------|--------|------|
| 1 | GROUP 1 (3-way) | Consolidate 3 ARCHITECTURE files → `docs/architecture.md` | **HIGH** (most complex) |
| 2 | GROUP 5 (QUICKSTART) | Consolidate → `docs/quickstart.md` | **MEDIUM** (entry point) |
| 3 | GROUP 9 (guides/QUICKSTART) | Consolidate → `docs/guides/quickstart.md` | **MEDIUM** (depends on Group 5 clarity) |
| 4–13 | Remaining 10 groups | Consolidate in any order (all low/medium risk) | **LOW–MEDIUM** |

**Rationale for sequence:**
- **GROUP 1 first:** Highest complexity (3-way); get it right to establish pattern.
- **GROUP 5 before GROUP 9:** Ensures consistency (both are QUICKSTARTs).
- **Remaining groups:** Lower priority; can run in parallel if needed.

---

## 4. REFERENCE UPDATE SCOPE

### Files to Update (by type)

#### **Type A: Markdown cross-references** (`[link](path)` syntax)
- Scan all `.md` files in `docs/`, `.codex/`, `reports/` for case-specific references.
- **Tool:** Markdown link extractor + case-sensitive grep.

#### **Type B: YAML front-matter / nav configs**
- `mkdocs.yml` — likely has `docs/ARCHITECTURE.md`, `docs/CI.md`, etc. in nav.
- Nested `.yamllint.yml` or other config refs.
- **Tool:** YAML parser + grep.

#### **Type C: Python docstrings**
- `:reference:` directives, Sphinx cross-refs.
- **Tool:** `grep -r "docs/ARCHITECTURE\|docs/CI"` in `.py` files.

#### **Type D: GitHub-specific**
- `README.md` → likely links to `docs/quickstart.md`.
- `CONTRIBUTING.md` → likely links to architecture/guides.
- **Tool:** Grep for exact case-sensitive filenames.

---

## 5. COORDINATION WITH OTHER TRACKS

### Track 8.1 (Doc Renames/Moves)

**Dependency:** De-collision (this workstream) must complete **before** Track 8.1 bulk renames.

**Alignment needed:**
- If Track 8.1 is planning to rename `docs/ARCHITECTURE.md` → something else, **coordinate** to ensure the collision is resolved first.
- Recommend: Track 8.1 consumes the canonical names from this matrix.

**Communication:** Once de-collision sequence is finalized, notify Track 8.1 lead of exact canonical paths.

---

### Track 8.2 (Bulk Directory Reorganization)

**Dependency:** De-collision + reference updates must complete **before** bulk moves.

**Rationale:** If `docs/guides/QUICKSTART.md` → `docs/guides/quickstart.md` hasn't been done yet, and 
Track 8.2 tries to move `docs/guides/` to a new location, the reference graph becomes corrupted.

**Communication:** Provide Track 8.2 with final canonical filenames before they run bulk-move operations.

---

## 6. SUPPORTING INFRASTRUCTURE

### Validation Checkpoints (Post De-collision)

After each group's consolidation:

1. **Link integrity check:**
   ```bash
   markdown-link-check docs/**/*.md
   ```

2. **Case-collision re-scan:**
   ```bash
   # Verify no new collisions created
   git ls-files | sort -f | uniq -d
   ```

3. **Git status verification:**
   ```bash
   git status  # Should show only renames, no conflicts
   ```

---

## 7. RISK ASSESSMENT

### Low-Risk Groups (can execute in parallel)
- Groups 4, 7, 8, 10, 12, 13 (specialized docs, limited cross-refs expected)

### Medium-Risk Groups (execute sequentially)
- Groups 2, 3, 6 (moderate cross-refs)
- Group 11 (unusual case-mix requires careful merge)

### High-Risk Groups (execute first, with human review)
- Group 1 (3-way collision; highest complexity)
- Group 5 (entry point; high external backlink risk)
- Group 9 (depends on Group 5 clarity)

---

## 8. GITATTRIBUTES REMEDIATION (Supporting Action)

While case-collision consolidation is underway, **root `.gitattributes` must be activated in parallel:**

| Action | File | Rationale |
|--------|------|-----------|
| **Copy** | `.config/.gitattributes` → `./.gitattributes` | Activate line-ending rules repo-wide. |
| **Verify** | Run `git check-attr text eol -- run_updates.sh` | Confirm rules now apply outside `.config/`. |
| **Commit** | Stage `.gitattributes` + case-collision renames together | Single coordinated commit. |

**Impact:** Protects all 216 bash scripts from CRLF corruption on Windows checkouts.

---

## 9. SUCCESS CRITERIA (WS2 → WS3 Handoff)

✅ **Compatibility matrix created** with all 13 groups documented  
✅ **De-collision sequence planned** with explicit ordering and dependencies  
✅ **Reference update scope identified** (Type A–D files enumerated)  
✅ **Coordination points established** with Track 8.1 and 8.2  
✅ **Validation checkpoints defined** (link integrity, case-collision re-scan, git status)  
✅ **Risk assessment completed** (high/medium/low groups classified)  
✅ **Blast-radius analysis** per group (internal links, external backlinks, hierarchy level)  
✅ **Gitattributes activation plan** included (supporting quick-win)  
✅ **Ready for WS3 execution** phase (all decision points resolved)  

---

## 10. NEXT STEPS (WS3 — Execution)

1. **Execute reference mapping** (Phase A from §3).
2. **Perform content merge** for each collision group.
3. **Update all references** (Phase B from §3).
4. **Activate root `.gitattributes`** (§8).
5. **Validate de-collision** (checkpoints from §6).
6. **Coordinate with Track 8.1 & 8.2** for downstream moves.
7. **Commit all changes** atomically.

---

**Document Status:** ✅ PLANNING COMPLETE (WS2 deliverable)  
**Ready for:** WS3 Execution Phase  
**Maintainer:** Track 8.3 — cross-platform-filename-validator  
**Timestamp:** 2026-07-07T14:26Z
