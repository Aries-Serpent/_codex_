# 🤖 SESSIONS 2–4 AGENT BRIEFING DOCUMENT

**Purpose:** Quick-reference guide for all agents executing Sessions 2–4  
**Created:** 2026-07-03T02:49:19Z  
**Authority:** @mbaetiong (D-tier autonomy, GO CONTINUE)  

---

## 📋 QUICK START FOR AGENTS

### Session 2: Cross-Platform Compatibility Remediation (2–4 hours)

**Lead Agent:** `cross-platform-filename-validator`  
**Support Agent:** `workflow-ci-fixer`  
**Scope:** Track 8.3 Phases 2–4 (616 files, HIGH/MEDIUM/LOW issues)

#### Your Briefing:
1. **Read first:** `.codex/PHASE_8_3_3_PHASE_1_COMPLETION.md` (Session 1 context)
2. **Load config:** `.codex/PHASE_8_3_REGRESSION_DETECTION_CONFIG.json`
3. **Reference:** `.codex/PHASE_8_3_3_RENAMES.json` (Phase 1 rename mappings)
4. **Execute:** Follow `.codex/SESSIONS_2_4_CONTINUATION_CAMPAIGN_PLAN.md` Session 2 section
5. **Timeline:** 3 phases × 45 min each = 135 min nominal

#### Phase 2: HIGH-Priority Issues (45–75 min)
- **Scan for:** Windows-reserved names (CON, PRN, AUX, NUL, LPT1-9, COM1-9)
- **Fix:** Rename files with canonical mappings; update all references
- **Validate:** Windows NTFS checkout (native Windows, no WSL)
- **Commit:** `git commit -m "Phase 8.3.2: Resolve HIGH-priority platform issues - 150+ files"`
- **Output:** `.codex/PHASE_8_3_2_HIGH_PRIORITY_COMPLETION.md`

#### Phase 3: MEDIUM-Priority Issues (45–60 min)
- **Scan for:** Paths exceeding 260 chars (Windows MAX_PATH limit)
- **Fix:** Refactor deep nesting; optimize path lengths
- **Validate:** Symlink handling across Windows/macOS/Linux
- **Commit:** `git commit -m "Phase 8.3.3: Resolve MEDIUM-priority issues - path optimization, symlinks"`
- **Output:** `.codex/PHASE_8_3_3_MEDIUM_PRIORITY_COMPLETION.md`

#### Phase 4: LOW-Priority Issues (30–45 min)
- **Establish:** Naming convention standards (from Phases 2–3 patterns)
- **Fix:** Batch-rename ~150–200 files; update documentation
- **Validate:** Post-rename scan ≤5 issues
- **Commit:** `git commit -m "Phase 8.3.4: LOW-priority polish - naming consistency, future-proofing"`
- **Output:** `.codex/PHASE_8_3_4_LOW_PRIORITY_COMPLETION.md`

#### Success Gate:
✅ All 616 files processed  
✅ Windows/macOS/Linux validation: PASS  
✅ 3 phase reports delivered  

**Support Agent (workflow-ci-fixer):** Update CI references after file renames; ensure all workflows still reference correct artifact paths.

---

### Session 3: Root Configuration Consolidation (1–2 hours)

**Lead Agent:** `repository-organization-agent`  
**Support Agent:** `config-validator`  
**Scope:** Batch 4 — Root config files (50–100 files)

#### Your Briefing:
1. **Read first:** All Session 2 completion reports
2. **Load config:** `.codex/PHASE_8_2_ROUTING_RULES.json`
3. **Review renames:** Load all rename mappings from Session 2 (all 3 phases)
4. **Execute:** Follow `.codex/SESSIONS_2_4_CONTINUATION_CAMPAIGN_PLAN.md` Session 3 section
5. **Timeline:** ~90 min (parallel execution of 5 subtasks)

#### Consolidation Tasks (parallel where possible):
1. **Hydra Config (20 min)**
   - Merge `configs/` and `config/` directories
   - Validate all against Hydra schema
   - Test: `python -m codex.cli <task> --help` for all tasks

2. **CI/CD Workflows (15 min)**
   - Extract duplicate workflow logic to `.github/workflows/templates/`
   - Update all workflow references
   - Validate YAML syntax

3. **Python Environment (10 min)**
   - Pin all transitive dependencies
   - Regenerate lock files: `pip-compile`, `poetry.lock`
   - Validate dependency resolution

4. **Build Tooling (10 min)**
   - Consolidate Makefile targets
   - Validate nox sessions
   - Update pre-commit hooks

5. **Validation (5 min)**
   - Test: `pre-commit run`, `nox -s tests`, `make build`
   - Verify CI/CD health

#### Commit:
```bash
git commit -m "Phase 8.4: Batch 4 config consolidation - root setup standardized"
```

#### Output:
`.codex/PHASE_8_4_BATCH_4_COMPLETION.md`

#### Success Gate:
✅ All root configs consolidated  
✅ Key workflows pass: `pre-commit`, `nox`, `make`  
✅ Lock files regenerated & validated  

**Support Agent (config-validator):** Validate all configs post-consolidation; ensure no schema violations or path references broken by Session 2 file renames.

---

### Session 4: Full Validation & Release Readiness (2–3 hours, Optional)

**Lead Agents:** All 4 track leads (parallel)  
**Coordinator:** `artifact-monitor-agent`  
**Test Lead:** `autonomous-test-healer-agent`  
**Security Lead:** `unified-security-scanner`

#### Your Briefing:
1. **Read first:** All Session 2 & 3 completion reports
2. **Execute:** Follow `.codex/SESSIONS_2_4_CONTINUATION_CAMPAIGN_PLAN.md` Session 4 section
3. **Timeline:** ~120–180 min (fully parallel execution)
4. **Authority:** Optional but recommended for full Phase 8 completion

#### Phase 1: Cross-Track Integration Validation (30 min, parallel)
```bash
nox -s tests                    # Full test suite
pre-commit run --all-files      # Code quality
ruff check . && mypy src/       # Linters
<doc-link-validation>           # Full documentation scan
<github-actions-validation>     # Workflow YAML syntax
```

#### Phase 2: Platform Validation (30 min, parallel)
```bash
pytest tests/test_windows_compat.py --verbose  # Windows NTFS
pytest tests/test_macos_compat.py --verbose    # macOS APFS
pytest tests/test_linux_compat.py --verbose    # Linux ext4
<artifact-path-tests>                           # MAX_PATH compliance
```

#### Phase 3: Security & Dependency Validation (30 min, parallel)
```bash
bandit -r src/ --skip B101           # Security audit
pip-audit                             # Dependency audit
detect-secrets scan --baseline .secrets.baseline  # Secrets
pip-licenses --format=csv             # License compliance
```

#### Phase 4: Release Readiness Verification (30 min)
- Version consistency: All `__version__` match
- CHANGELOG: Latest entries dated today
- README: All code examples pass validation
- CI Health: All 45+ workflows green
- Artifacts: Release artifacts ready

#### Outputs (all parallel):
- `.codex/PHASE_8_4_1_INTEGRATION_VALIDATION_REPORT.md`
- `.codex/PHASE_8_4_2_PLATFORM_VALIDATION_REPORT.md`
- `.codex/PHASE_8_4_3_SECURITY_VALIDATION_REPORT.md`
- `.codex/PHASE_8_4_4_RELEASE_READINESS_REPORT.md`
- `.codex/PHASE_8_COMPLETION_FINAL_SUMMARY.md`
- `.codex/PHASE_9_STAGING_BRIEF.md` (if all gates pass)

#### Success Gate:
✅ All cross-track integrations validated  
✅ Windows/macOS/Linux tests: PASS  
✅ Security & dependency audits: PASS  
✅ Release readiness: ALL GATES PASS  

---

## 🔄 INTER-SESSION HANDOFF PROTOCOL

### Session 2 → Session 3 Handoff
**Transfer These Artifacts:**
- 3 phase completion reports from Track 8.3
- All file rename mappings (embedded in commits)
- Updated `.gitattributes` (if created)

**Session 3 Agent Must:**
- [ ] Load all 3 phase reports
- [ ] Parse rename mappings from git history
- [ ] Pre-validate that config paths reference updated filenames
- [ ] Proceed with config consolidation

### Session 3 → Session 4 Handoff
**Transfer These Artifacts:**
- Batch 4 completion report
- Updated `pyproject.toml`, lock files
- New workflow templates (if created)

**Session 4 Agents Must:**
- [ ] Load Batch 4 completion report
- [ ] Verify all config consolidations are reflected in CI/CD tests
- [ ] Validate that new config paths are correct
- [ ] Run full validation suite

---

## 🚨 CRITICAL NOTES FOR ALL AGENTS

### Token Usage
- All operations use `CODEX_MASTER_KEY` (authorized by @mbaetiong)
- Conservative token budget: plan uses ~60K tokens per session
- Track token usage in session logs

### File Storage
- **ALWAYS** store artifacts in `.codex/` (repository-tracked)
- **NEVER** use `/tmp/` for working files or deliverables
- Validate all artifact paths before committing

### Git Hygiene
- Atomic commits per major task (Phase 2, 3, 4 each get 1–2 commits)
- Commit messages must reference phase/batch (e.g., "Phase 8.3.2")
- All commits traceable to `.codex/` artifacts

### Cross-Platform Validation
- **Windows:** Use native Windows validation (not WSL)
- **macOS:** APFS filesystem testing
- **Linux:** ext4 filesystem testing
- All three must PASS before session completion

### Escalation Path
- Critical issues → Create issue with [PHASE-8-ESCALATION] tag
- Notify @mbaetiong with full context
- Wait for approval before proceeding past blocker

---

## 📞 AUTHORITY REFERENCE

**Campaign Owner:** @mbaetiong  
**Authority Level:** D-tier autonomy, GO CONTINUE on all gates  
**Token:** CODEX_MASTER_KEY authorized for elevated operations  
**Branch:** `copilot/deploy-phase-8-agents`  

**All agent decisions are pre-approved.** Proceed autonomously. Escalate only if critical blocker encountered.

---

## 🎯 EXECUTION CHECKLIST TEMPLATE

### Pre-Session Validation
- [ ] Branch correct: `copilot/deploy-phase-8-agents`
- [ ] Prior session artifacts loaded
- [ ] Config files accessible
- [ ] Tokens available (CODEX_MASTER_KEY)

### During-Session Execution
- [ ] Follow phase checklist from continuation plan
- [ ] Generate required outputs
- [ ] Commit regularly (atomic commits)
- [ ] Monitor token usage

### Post-Session Validation
- [ ] All success gates checked
- [ ] Artifacts generated and committed
- [ ] Next-session handoff artifacts prepared
- [ ] Session summary updated

---

**Ready to execute? Load the full continuation campaign plan: `.codex/SESSIONS_2_4_CONTINUATION_CAMPAIGN_PLAN.md`**

