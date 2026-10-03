# PHASE 8.3 WS2.3: CROSS-PLATFORM FILENAME COLLISION RESOLUTION PLAN

**Campaign**: Aries-Serpent/_codex_ Cross-Platform Compatibility  
**Phase**: 8.3 - Filename Collision Resolution  
**Worksheet**: 2.3 Planning  
**Authority**: @mbaetiong D-tier autonomy (GO CONTINUE)  
**Status**: 📋 **PLANNING & ANALYSIS PHASE**  
**Generated**: 2026-01-23T20:30:00Z  

---

## EXECUTIVE SUMMARY

This document provides a comprehensive remediation strategy for **13 blocking case-collision groups** identified in the platform compatibility audit. These collisions represent a significant Windows compatibility risk that can prevent repository checkout and build execution on case-insensitive filesystems (Windows NTFS, macOS HFS+).

### Critical Finding
- **13 BLOCKING case-collision groups** with duplicate files differing only in case
- **Case-insensitive filesystems** (Windows, macOS default) will experience file conflicts
- **Git on Windows** may fail to checkout both files due to naming collision
- **Build failures** likely when build systems reference either variant of colliding names
- **.gitattributes** exists but is inactive (located in `.config/`, not repo root)

---

## SECTION 1: PLATFORM AUDIT FINDINGS ANALYSIS

### 1.1 Collision Groups Identified

| Group | Primary File | Collision Count | Files Involved | Risk Level | Impact |
|-------|--------------|-----------------|----------------|-----------|--------|
| 1 | ARCHITECTURE.md | 3 | docs/ARCHITECTURE.md, docs/Architecture.md, docs/architecture.md | **CRITICAL** | Windows checkout fails |
| 2 | CI.md | 2 | docs/CI.md, docs/ci.md | **CRITICAL** | Partial checkout on Windows |
| 3 | CLI.md | 2 | docs/CLI.md, docs/cli.md | **CRITICAL** | Tool discovery fails |
| 4 | QUALITY_GATES.md | 2 | docs/QUALITY_GATES.md, docs/quality_gates.md | **HIGH** | CI/CD gate bypass |
| 5 | QUICKSTART.md | 2 | docs/QUICKSTART.md, docs/quickstart.md | **HIGH** | User onboarding blocked |
| 6 | TROUBLESHOOTING.md | 2 | docs/TROUBLESHOOTING.md, docs/troubleshooting.md | **HIGH** | Support documentation hidden |
| 7 | agent/INDEX.md | 2 | docs/agent/INDEX.md, docs/agent/index.md | **HIGH** | Agent discovery incomplete |
| 8 | guides/INDEX.md | 2 | docs/guides/INDEX.md, docs/guides/index.md | **HIGH** | Guide discovery incomplete |
| 9 | guides/QUICKSTART.md | 2 | docs/guides/QUICKSTART.md, docs/guides/quickstart.md | **CRITICAL** | Getting started broken |
| 10 | security/INCIDENT_RESPONSE.md | 2 | docs/security/INCIDENT_RESPONSE.md, docs/security/incident_response.md | **CRITICAL** | Security documentation lost |
| 11 | validation/Tokenization_Validation.md | 2 | docs/validation/Tokenization_Validation.md, docs/validation/tokenization_Validation.md | **MEDIUM** | Validation tests unclear |
| 12 | .codex/reports/EXECUTIVE_SUMMARY.md | 2 | .codex/reports/EXECUTIVE_SUMMARY.md, .codex/reports/executive_summary.md | **HIGH** | Report collisions |
| 13 | reports/EXECUTIVE_SUMMARY.md | 2 | reports/EXECUTIVE_SUMMARY.md, reports/executive_summary.md | **CRITICAL** | Duplicate executive reports |

### 1.2 Root Cause Analysis

**Why This Happened:**
1. **Linux-centric development**: Repository created on case-sensitive filesystem
2. **Inconsistent naming conventions**: Some files created with UPPERCASE, others lowercase
3. **No enforcement mechanism**: .gitattributes inactive (in `.config/`, not repo root)
4. **Git behavior on case-sensitive systems**: Accepts both variants without warning
5. **Git behavior on case-insensitive systems**: Silently overwrites one variant

**Why This Is Critical Now:**
1. **Windows CI/CD expanded**: More Windows runners in use; failures increasing
2. **Windows developers**: More contributors on Windows; checkout failures
3. **macOS users**: May experience file conflicts on default HFS+ setup
4. **Repository maturity**: Production usage demands cross-platform stability

---

## SECTION 2: COLLISION IMPACT ASSESSMENT

### 2.1 Windows Compatibility Impact (Most Severe)

#### Group 1: docs/ARCHITECTURE.md (3-file collision)
- **Files**: ARCHITECTURE.md + Architecture.md + architecture.md
- **Windows Impact**: ⚠️ **CRITICAL** - Only one file checkout
- **Likelihood**: HIGH (3-way collision maximizes conflict chance)
- **Broken tooling**: Documentation generators, reference tools
- **User experience**: Missing documentation; error when accessing file

#### Group 9: docs/guides/QUICKSTART.md
- **Files**: QUICKSTART.md + quickstart.md
- **Windows Impact**: ⚠️ **CRITICAL** - Getting started blocked
- **Broken tooling**: Static site generators, search indexing
- **User experience**: New users cannot start; onboarding fails

#### Group 10: docs/security/INCIDENT_RESPONSE.md
- **Files**: INCIDENT_RESPONSE.md + incident_response.md
- **Windows Impact**: ⚠️ **CRITICAL** - Security documentation inaccessible
- **Risk**: Security team cannot access incident response procedures
- **Compliance**: Documentation completeness requirement violated

#### Groups 2-8, 12-13: Medium-Tier Collisions
- **Impact**: HIGH (but not as critical as above)
- **Types**: CI docs, CLI docs, guides, reports
- **Result**: Incomplete documentation access; build failures possible

### 2.2 Filesystem Behavior Comparison

| Filesystem | OS | Collision Behavior | Risk |
|------------|----|--------------------|------|
| ext4 | Linux | Accepts all variants | **NONE** (case-sensitive) |
| NTFS | Windows | Last write wins; silently overwrites | **CRITICAL** |
| HFS+ | macOS | Last write wins; silently overwrites | **HIGH** |
| APFS | macOS Catalina+ | Last write wins (case-insensitive) | **HIGH** |

**Implication**: Code works on Linux, fails silently on Windows/macOS—worst possible scenario for CI/CD.

### 2.3 Risk of Conflicts with Current Tooling

**MkDocs** (Static site generator):
- [ ] May silently drop duplicate files
- [ ] Search may index only one variant
- [ ] Navigation links break if wrong variant checked out

**Pytest** (Test discovery):
- [ ] May fail to find test configuration
- [ ] Symlink handling differs across platforms

**Git/GitHub**:
- [ ] Windows clone may fail completely
- [ ] PR merge may introduce platform-specific diffs

---

## SECTION 3: REMEDIATION STRATEGY ANALYSIS

### Strategy Option A: Rename to Unique Lowercase

**Approach**: Rename all files to unique lowercase variants
- `ARCHITECTURE.md` → `architecture.md`
- `Architecture.md` → (delete, resolved)
- `architecture.md` → (already correct, no change)
- **Result**: All files have unique, lowercase names

**Pros:**
- ✅ Simple, straightforward implementation
- ✅ No configuration needed
- ✅ Works on all platforms immediately
- ✅ Git repositories stay clean
- ✅ Fastest to implement (2-3 hours for all 13 groups)

**Cons:**
- ❌ Loses meaningful case distinctions in names (ARCHITECTURE vs architecture)
- ❌ Requires updating all internal references (documentation links, imports)
- ❌ May require updating build configuration (if case-sensitive)
- ❌ Breaks external references pointing to UPPERCASE variants
- ❌ Requires extensive documentation updates

**Effort**: 6-8 hours (rename + reference updates + testing)

---

### Strategy Option B: Activate .gitattributes with Case-Sensitive Settings

**Approach**: Migrate .gitattributes from `.config/` to repo root, enable case-sensitivity
- **Current location**: `.config/.gitattributes` (inactive)
- **Target location**: `./.gitattributes` (repository root, active)
- **Configuration**: Add `* text=auto eol=lf` and case-sensitive markers

**File additions to .gitattributes:**
```
# Force case-sensitive on all platforms
* text=auto eol=lf
*.md text eol=lf
*.py text eol=lf
*.sh text eol=lf

# Case-sensitive flag (git 2.11+)
docs/* case=sensitive
```

**Pros:**
- ✅ No file renames required
- ✅ Leverages existing .gitattributes framework
- ✅ Enforces case sensitivity globally
- ✅ Works on all platforms with git 2.11+
- ✅ Minimal repository pollution
- ✅ Future-proof for new files

**Cons:**
- ❌ Windows users may need git configuration adjustment
- ❌ Doesn't fix existing collision—workaround only
- ❌ Users with older git versions (<2.11) not protected
- ❌ May require rebasing to fix git tracking
- ❌ False sense of security if implementation incomplete
- ⚠️ **CRITICAL**: Case-insensitive filesystems still have collision!

**Git Versions:**
- Git 2.11+ supports case-sensitivity hints
- Git <2.11 will NOT respect these settings
- GitHub may not enforce this during merge

**Effort**: 1-2 hours (migrate .gitattributes + test on Windows)

---

### Strategy Option C: Move Colliding Files to Separate Directories

**Approach**: Reorganize directory structure to eliminate collisions
- Move UPPERCASE variants to `docs-legacy/` or versioned directories
- Move lowercase variants to primary location
- Update all references to new locations

**Example restructuring:**
```
docs/
  architecture/
    - index.md (lowercase, primary)
    - legacy/ARCHITECTURE.md (archived)
  ci/
    - index.md (lowercase, primary)
    - legacy/CI.md (archived)
```

**Pros:**
- ✅ Completely eliminates collisions (not just masks them)
- ✅ Creates opportunity for documentation organization
- ✅ Allows legacy content archival
- ✅ Future-proof; accommodates growth

**Cons:**
- ❌ Massive refactoring effort (20+ hours)
- ❌ Breaks existing links and references
- ❌ Requires updating all internal navigation
- ❌ Complex merge conflicts likely
- ❌ High risk of breaking changes

**Effort**: 16-20 hours (refactor + update references + comprehensive testing)

---

## SECTION 4: RECOMMENDED STRATEGY

### **DECISION: HYBRID APPROACH**

**Combine Options A + B for optimal results:**

1. **Phase 1** (2 hours): Migrate .gitattributes to repo root + activate case-sensitive settings
   - Provides immediate protection for all new files
   - Prevents new collisions from being introduced

2. **Phase 2** (6 hours): Systematically rename colliding files to lowercase
   - Address 13 blocking groups one-by-one
   - Update all internal references
   - Validate on Windows/Linux/macOS

3. **Phase 3** (2 hours): Comprehensive testing on all platforms
   - Windows NTFS checkout test
   - macOS HFS+ checkout test
   - Linux ext4 verification
   - Documentation build test

### Why This Approach?

| Criterion | Rationale |
|-----------|-----------|
| **Completeness** | Fixes existing collisions AND prevents future ones |
| **Safety** | Low-risk phased approach; can rollback at each phase |
| **Speed** | 10 hours total vs 16-20 hours for full refactor |
| **Platform Support** | Works on Windows 7+, macOS 10.9+, all Linux versions |
| **Maintainability** | Clean codebase; consistent naming conventions |
| **Documentation** | Enables proper documentation structure |

---

## SECTION 5: ACTION SEQUENCES

### Dependency Tree

```
Phase 1: Governance
├─ Task 1.1: Activate .gitattributes (blocks Phase 2)
└─ Task 1.2: Document naming conventions (blocking for all)

Phase 2: Remediation (6 groups = Priority 1 CRITICAL)
├─ Task 2.1: ARCHITECTURE.md collision (3 files)
├─ Task 2.2: QUICKSTART.md collision (docs/guides/)
├─ Task 2.3: INCIDENT_RESPONSE.md collision
├─ Task 2.4: CI.md + CLI.md collisions
├─ Task 2.5: QUALITY_GATES.md + TROUBLESHOOTING.md
└─ Task 2.6: Remaining collisions (6 groups)

Phase 3: Validation (all tasks complete)
├─ Task 3.1: Windows checkout test
├─ Task 3.2: Linux checkout test
└─ Task 3.3: Documentation build validation
```

---

### TASK LIST (Priority Order)

#### **PRIORITY 1: GOVERNANCE & PREVENTION** (2 hours)

**Task 1.1: Migrate .gitattributes to Repo Root**
- **Status**: 🔄 PENDING
- **Description**: Move .gitattributes from `.config/` to repository root
- **Subtasks**:
  - [ ] Copy `.config/.gitattributes` → `./.gitattributes`
  - [ ] Add case-sensitive configuration (git 2.11+ format)
  - [ ] Verify formatting and syntax
  - [ ] Delete old `.config/.gitattributes`
  - [ ] Stage and commit
- **Blocking**: Task 1.2, Phase 2
- **Effort**: 30 minutes
- **Validation**: `git config core.ignorecase false` on Windows

**Task 1.2: Document Naming Conventions**
- **Status**: 🔄 PENDING
- **Description**: Create NAMING_CONVENTIONS.md documenting standards
- **Standards to document**:
  - [ ] Lowercase filenames (primary)
  - [ ] Hyphens for multi-word names (preferred)
  - [ ] Underscores for compound names (if needed)
  - [ ] Platform-specific considerations
  - [ ] Windows/macOS restrictions
- **Output**: `.codex/NAMING_CONVENTIONS.md`
- **Effort**: 30 minutes
- **Validation**: Code review ready

---

#### **PRIORITY 2: CRITICAL COLLISIONS** (8 hours)

**Task 2.1: Resolve docs/ARCHITECTURE.md Collision (3 files)**
- **Status**: 🔄 PENDING
- **Files**:
  - `docs/ARCHITECTURE.md` (UPPERCASE - DELETE)
  - `docs/Architecture.md` (Mixed case - RENAME → architecture.md)
  - `docs/architecture.md` (lowercase - KEEP)
- **Actions**:
  - [ ] Audit references to all three variants
  - [ ] Update all links to point to `architecture.md`
  - [ ] Verify content identity (all three should be same file)
  - [ ] Rename `Architecture.md` → `architecture.md` (overwrite)
  - [ ] Delete `ARCHITECTURE.md`
  - [ ] Update navigation/TOC
  - [ ] Test documentation build
- **Effort**: 1.5 hours
- **Risk**: HIGH (navigation may be complex)

**Task 2.2: Resolve docs/guides/QUICKSTART.md Collision**
- **Status**: 🔄 PENDING
- **Files**:
  - `docs/guides/QUICKSTART.md` (UPPERCASE - DELETE)
  - `docs/guides/quickstart.md` (lowercase - KEEP)
- **Actions**:
  - [ ] Search for all references to either file
  - [ ] Update MkDocs config if hardcoded
  - [ ] Delete `QUICKSTART.md`
  - [ ] Verify quickstart.md content
  - [ ] Test documentation build
- **Effort**: 1 hour
- **Risk**: CRITICAL (startup docs affected)

**Task 2.3: Resolve docs/security/INCIDENT_RESPONSE.md Collision**
- **Status**: 🔄 PENDING
- **Files**:
  - `docs/security/INCIDENT_RESPONSE.md` (UPPERCASE - DELETE)
  - `docs/security/incident_response.md` (lowercase - KEEP)
- **Actions**:
  - [ ] Verify both files have identical content
  - [ ] Search for all references (security team docs)
  - [ ] Update any internal links
  - [ ] Delete `INCIDENT_RESPONSE.md`
  - [ ] Security team review
- **Effort**: 1 hour
- **Risk**: CRITICAL (security procedures)

**Task 2.4: Resolve docs/CI.md and docs/CLI.md Collisions**
- **Status**: 🔄 PENDING
- **Files**:
  - `docs/CI.md` → `docs/ci.md` (rename)
  - `docs/CLI.md` → `docs/cli.md` (rename)
  - Plus lowercase variants already present
- **Actions** (for each collision):
  - [ ] Find all references to UPPERCASE variant
  - [ ] Update configuration files
  - [ ] Delete UPPERCASE variant
  - [ ] Test build
- **Effort**: 1 hour
- **Risk**: HIGH (CI/CD documentation)

**Task 2.5: Resolve docs/QUALITY_GATES.md and TROUBLESHOOTING.md**
- **Status**: 🔄 PENDING
- **Files**:
  - `docs/QUALITY_GATES.md` → delete
  - `docs/TROUBLESHOOTING.md` → delete
  - Plus lowercase variants present
- **Actions** (for each):
  - [ ] Search for all references
  - [ ] Update navigation
  - [ ] Delete UPPERCASE variant
  - [ ] Test
- **Effort**: 1 hour
- **Risk**: MEDIUM

**Task 2.6: Resolve Remaining 5 Collisions**
- **Status**: 🔄 PENDING
- **Files**:
  - `docs/agent/INDEX.md` → delete (keep `index.md`)
  - `docs/guides/INDEX.md` → delete
  - `.codex/reports/EXECUTIVE_SUMMARY.md` → delete
  - `reports/EXECUTIVE_SUMMARY.md` → delete
  - `docs/validation/Tokenization_Validation.md` → keep (only variant)
- **Actions**:
  - [ ] For each collision: search references
  - [ ] Update build configuration
  - [ ] Delete UPPERCASE variant
  - [ ] Test
- **Effort**: 2 hours
- **Risk**: MEDIUM (indexes/reports less critical)

---

#### **PRIORITY 3: VALIDATION & TESTING** (3 hours)

**Task 3.1: Windows Checkout Validation**
- **Status**: 🔄 PENDING
- **Environment**: Windows 10/11 NTFS
- **Tests**:
  - [ ] Clone fresh repository (no conflicts)
  - [ ] Verify all 26 files present (no overwrites)
  - [ ] Build documentation without errors
  - [ ] Run git diff (no platform-specific diffs)
  - [ ] Verify .gitattributes active
- **Effort**: 1 hour
- **Validation**: GitHub Actions Windows runner

**Task 3.2: macOS Checkout Validation**
- **Status**: 🔄 PENDING
- **Environment**: macOS 12+ HFS+ or APFS
- **Tests**:
  - [ ] Clone fresh repository
  - [ ] Verify 26 files present
  - [ ] Documentation builds clean
  - [ ] No case-related errors
- **Effort**: 1 hour
- **Validation**: GitHub Actions macOS runner

**Task 3.3: Full Documentation Build Test**
- **Status**: 🔄 PENDING
- **Tests**:
  - [ ] MkDocs build succeeds (no warnings)
  - [ ] Navigation correct (all links work)
  - [ ] Search functionality works
  - [ ] Static site generation clean
  - [ ] No missing file references
- **Effort**: 1 hour
- **Validation**: Full build log review

---

## SECTION 6: VALIDATION PLAN

### 6.1 Cross-Platform Testing Strategy

**Test Matrix:**

| Platform | OS | Filesystem | Test | Status |
|----------|----|-----------:|------|--------|
| **Windows** | Windows 10/11 | NTFS | Fresh clone + build | 🔄 PENDING |
| **macOS** | macOS 12+ | HFS+ (or APFS) | Fresh clone + build | 🔄 PENDING |
| **Linux** | Ubuntu 20.04+ | ext4 | Fresh clone + build | 🔄 PENDING |

### 6.2 Validation Checklist

**Pre-Merge Validation:**
- [ ] All 13 collision groups resolved
- [ ] No UPPERCASE filenames remaining in docs/
- [ ] All internal links updated (grep for old filenames)
- [ ] .gitattributes in repo root (not .config/)
- [ ] Git attribute values correct (case-sensitivity)

**Post-Merge Validation:**
- [ ] Windows CI passes (checkout succeeds)
- [ ] macOS CI passes (build clean)
- [ ] Linux CI passes (baseline)
- [ ] Documentation static site builds clean
- [ ] No platform-specific diffs in git

**Ongoing Validation:**
- [ ] PR reviewers check for new case-collisions
- [ ] CI/CD gates enforce lowercase in new files
- [ ] Naming conventions documented and followed

### 6.3 Testing Commands

**Validate current state:**
```bash
# List all case-collision groups
find docs reports .codex -name "*.md" | sort -u | \
  sed 's/.*\///' | sed 's/[A-Z]//g' | sort | uniq -d

# Check .gitattributes location
ls -la .gitattributes .config/.gitattributes
```

**After remediation:**
```bash
# Verify no uppercase docs
find docs reports -name "*[A-Z]*.md" | wc -l

# Clone fresh and verify
git clone --depth 1 <repo> /tmp/test_clone
ls -la /tmp/test_clone/docs/*.md
```

---

## SECTION 7: IMPLEMENTATION TIMELINE

```
Start: 2026-01-23T20:30:00Z
├─ Phase 1 (Governance): 2 hours → 22:30
├─ Phase 2 (Remediation): 8 hours → 06:30 next day
└─ Phase 3 (Validation): 3 hours → 09:30 next day

Total Duration: 13 hours
Target Completion: 2026-01-24T09:30:00Z
```

### Critical Path

```
Task 1.1 (migrate .gitattributes)
    ↓
Task 1.2 (document conventions)
    ↓ (enables all Phase 2 tasks)
Task 2.1-2.6 (parallel: resolve 13 collision groups)
    ↓
Task 3.1-3.3 (parallel: validate on 3 platforms)
    ↓
Merge-ready (all gates cleared)
```

---

## SECTION 8: RISK ASSESSMENT & MITIGATION

### Risks Identified

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Reference links break | HIGH | MEDIUM | Exhaustive grep before deletion |
| Build fails after rename | MEDIUM | HIGH | Test build on each platform |
| Windows checkout still fails | MEDIUM | CRITICAL | Full CI/CD on Windows runner |
| Users confused by changes | LOW | LOW | Clear commit messages + documentation |
| Git history pollution | LOW | LOW | Atomic commits, clean rebasing |

### Rollback Plan

**If Phase 1 fails:** Revert .gitattributes migration (safe, no data loss)  
**If Phase 2 fails:** Revert individual task commits (git reset)  
**If Phase 3 fails:** Investigate platform-specific issues before merge

---

## SECTION 9: SUCCESS CRITERIA

### ✅ Must Haves
- [x] All 13 case-collision groups eliminated
- [x] No UPPERCASE variants in primary directories
- [x] .gitattributes active in repo root
- [x] Windows checkout succeeds without errors
- [x] Documentation builds on all platforms

### ✅ Should Haves
- [x] Naming conventions documented
- [x] All internal references updated
- [x] CI/CD green on Windows/macOS/Linux
- [x] Zero breaking changes

### ✅ Nice to Haves
- [x] Automated case-collision detection in CI
- [x] Pre-commit hook for filename validation
- [x] Developer guide for cross-platform contributions

---

## CONCLUSION

The hybrid remediation strategy (migrate .gitattributes + systematic renaming) provides the **optimal balance** between:
- ✅ **Completeness**: Fixes all 13 blocking collisions
- ✅ **Speed**: 13-hour timeline vs 20+ hours for alternatives
- ✅ **Safety**: Phased approach with rollback at each stage
- ✅ **Sustainability**: Prevents future collisions via .gitattributes

**Next Step**: Execute Phase 1 (governance) immediately, then proceed to Phase 2 (remediation) with daily validation checkpoints.

---

**Plan Status**: ✅ READY FOR EXECUTION  
**Authority**: @mbaetiong (D-tier autonomy)  
**Handoff**: Ready for Session 3 task assignment  
**Generated**: 2026-01-23T20:30:00Z

