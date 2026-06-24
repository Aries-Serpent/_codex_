# Campaign Track-Specific Delegation Prompts
## Ready for Days 3-20 Parallel Execution

**Generated:** 2026-06-16T13:15Z  
**Campaign:** Production Readiness 2026  
**Execution Model:** 8 parallel tracks × 3+ agents per track

---

## TRACK 1: COVERAGE RATCHET (10.7% → 15%+)

### Prompt 1.1: unified-coverage-agent (Primary)
```
Campaign: Production Readiness 2026, Track 1 (Coverage Ratchet)
Objective: Increase code coverage from 10.7% to 15%+ through systematic gap-filling

Context:
- Current coverage: 10.7% (212 test runs, 314K test LOC)
- Target coverage: 15%+ (ratchet roadmap: 10→12→15→20%)
- Test files: 2,672 total across all modules
- Strategy: Lane-based coverage targeting (Lanes 1-5 parallel execution)

Lanes to Execute:
1. Lane 1: Module coverage (50+ codex submodules) — autonomous-test-healer-agent
2. Lane 2: CLI & handler coverage — test-enhancement-agent
3. Lane 3: Bridge & agent protocol coverage — test-enhancement-agent
4. Lane 4: Cognitive brain & memory coverage — mutation-testing-agent
5. Lane 5: Integration & end-to-end coverage — mutation-testing-agent

Deliverables:
- Per-lane coverage delta reports (lines added, branches covered, mutation score)
- Final coverage report with verification (15%+ confirmed)
- Autonomous healer execution log (test failures fixed during execution)
- Mutation testing validation (75%+ mutation score achieved)

Success Criteria:
- Coverage ≥15% achieved
- Zero regression in existing tests
- All 2,212 test files validated
- <5 test collection errors
- Mutation score ≥75%

Timeline: Days 3-16 (parallel lanes 1-5)
Status: Ready for delegation
```

### Prompt 1.2: autonomous-test-healer-agent (Sub-agent, Lane 1)
```
Campaign: Production Readiness 2026, Track 1, Lane 1
Objective: Detect and fix failing tests in codex module coverage targets

Focus: 50+ codex submodules (codex/*, codex_*/*, agent/*)
Constraints:
- Fix test collection errors first (P19 shadow import awareness)
- Detect flaky tests with @pytest.mark.flaky annotation
- Apply standard fixes (missing imports, timeout increases, mock corrections)
- Generate mermaid test-cycle diagrams for complex patterns

Deliverables:
- Lane 1 coverage delta report (module breakdown)
- Fixed test count + error reduction metrics
- Autonomous healer execution log (fix patterns applied)

Timeline: Days 3-9 (parallel with lanes 2-5)
```

### Prompt 1.3: test-enhancement-agent (Sub-agent, Lanes 2-3)
```
Campaign: Production Readiness 2026, Track 1, Lanes 2-3
Objective: Add edge cases and improve assertions in CLI/handler and bridge coverage

Lanes:
- Lane 2: CLI & handler coverage (src/codex/cli/*, src/codex_cli/*)
- Lane 3: Bridge & agent protocol coverage (src/codex/bridge*.py)

Tasks:
- Identify low-coverage code paths (branch coverage <50%)
- Add edge case tests (error handling, boundary conditions)
- Improve assertion quality (parametrized tests, exception matching)
- Document test patterns for future maintenance

Deliverables:
- Lanes 2-3 coverage delta reports (CLI/bridge breakdown)
- New test case documentation
- Edge case coverage validation

Timeline: Days 3-12 (parallel with lanes 1, 4-5)
```

### Prompt 1.4: mutation-testing-agent (Sub-agent, Lanes 4-5)
```
Campaign: Production Readiness 2026, Track 1, Lanes 4-5
Objective: Validate test quality through mutation testing (Lanes 4-5)

Lanes:
- Lane 4: Cognitive brain & memory coverage (src/codex/cognitive_brain/*)
- Lane 5: Integration & end-to-end coverage (tests/integration/*)

Tasks:
- Run mutation testing to assess test effectiveness
- Identify weak test coverage areas (low mutation kill rate)
- Recommend assertions to catch more mutations
- Generate mutation score report (target: 75%+)

Deliverables:
- Lanes 4-5 mutation testing reports
- Test quality assessment (75%+ mutation kill rate)
- Recommendations for assertion improvements

Timeline: Days 10-16 (follows lanes 1-3, validates all coverage)
```

---

## TRACK 2: SECURITY HARDENING (0 critical/high verified)

### Prompt 2.1: unified-security-scanner (Primary)
```
Campaign: Production Readiness 2026, Track 2 (Security Hardening)
Objective: Verify 0 critical/high security findings and 26 fixed CVEs

Context:
- IP-005 completion status: CVEs 1-26 eliminated
- Current baseline: 0 critical + 0 high (needs re-verification)
- Scan scope: Full codebase, dependencies, secrets baseline

Scanning Tasks:
1. CodeQL: Re-scan all Python files, verify codeql-alert-resolution-agent fixes
2. Semgrep: Validate security patterns (custom rules + rulesets)
3. Bandit: Check for common security issues
4. Secrets baseline: Verify 11 pragma allowlist pragmas, detect new leaks
5. Dependency scan: Confirm 26 CVEs fixed (no new vulnerabilities)

Deliverables:
- Full security scan results (CodeQL, Semgrep, Bandit, secrets)
- CVE verification matrix (26 fixed CVEs confirmed)
- False positive analysis (pragma allowlist cleanup if needed)
- Final security audit report (0 critical/high confirmed)

Success Criteria:
- 0 critical findings
- 0 high findings
- <5 medium findings (acceptable risk)
- 26 CVEs fixed and verified
- 0 new secrets detected

Timeline: Days 3-14 (parallel verification across 4 scanners)
Status: Ready for delegation
```

### Prompt 2.2: codeql-alert-resolution-agent (Sub-agent)
```
Campaign: Production Readiness 2026, Track 2
Objective: Re-verify CodeQL alert remediation (42 fixed findings)

Context:
- PR #4863 fixed 3 CodeQL alerts (codeql[py/rule-id] format)
- Need to verify all 42 historic fixes remain applied
- Check for any new alerts introduced by recent PRs

Tasks:
- Run CodeQL on latest commit
- Verify 42 historic fixes still applied
- Detect any new critical/high alerts (should be 0)
- Validate suppression format (`# codeql[py/rule-id]`)

Deliverables:
- CodeQL re-scan results
- Remediation verification checklist
- New alert detection report (0 expected)

Timeline: Days 3-8 (parallel with secrets scan)
```

### Prompt 2.3: code-scanning-remediation-agent (Sub-agent)
```
Campaign: Production Readiness 2026, Track 2
Objective: Verify code scanning findings remediation (GHAS alerts)

Tasks:
- Re-scan with GitHub code scanning (SAST tools)
- Validate all remediated findings remain fixed
- Check for any new vulnerabilities

Deliverables:
- Code scanning verification report
- GHAS alert status (0 critical + 0 high expected)

Timeline: Days 8-12 (follows CodeQL scan)
```

### Prompt 2.4: dependency-security-review-agent (Sub-agent)
```
Campaign: Production Readiness 2026, Track 2
Objective: Verify 26 CVEs fixed, no new dependencies with known vulnerabilities

Tasks:
- Scan dependencies (pip audit, pip-audit output verification)
- Verify all 26 CVEs eliminated
- Check for version pins preventing new CVEs
- Validate lock files (uv.lock, package-lock.json)

Deliverables:
- CVE verification matrix (26 fixed + timestamp of fix)
- Dependency vulnerability report (0 active CVEs)
- Lock file validation report

Timeline: Days 10-14 (final verification phase)
```

---

## TRACK 3: CI STABILITY (<5% failure rate)

### Prompt 3.1: ci-auto-healer-agent (Primary)
```
Campaign: Production Readiness 2026, Track 3 (CI Stability)
Objective: Reduce CI failure rate from 6.8% to <5% through RP pattern application

Context:
- Current failure rate: 6.8% (acceptable but room for improvement)
- Target failure rate: <5% (Grade A+ = 95/100)
- RP Patterns: 35+ documented patterns (RP-001 through RP-035+)
- 49 active workflows to monitor

RP Pattern Categories:
1. RP-001: Unused imports (ruff F401) — Auto-fix via ruff
2. RP-002: Type annotation errors (mypy) — Detect + recommend
3. RP-003: YAML indentation (actionlint) — Auto-fix indentation
4. RP-004: Coverage threshold drift — Standardize to 70%
5. RP-005-009: Docker, Python, secrets patterns
6. RP-035: Markdown false positives (pragma allowlist)

Healing Strategy:
1. Days 3-5: RP-001, RP-004, RP-008, RP-035 (auto-fixable patterns)
2. Days 6-10: RP-002, RP-003, RP-006 (semi-manual patterns)
3. Days 11-15: Full RP catalog validation, edge case handling
4. Days 16-20: Failure rate trend analysis, final optimization

Deliverables:
- RP pattern catalog (35+ patterns documented)
- Healer execution log (patterns applied, workflows tested)
- Failure rate trend analysis (6.8% → <5% progression)
- Workflow compliance report (49 workflows validated)
- CI health scorecard (target: 95/100)

Success Criteria:
- CI failure rate <5%
- All RP patterns validated
- 49 workflows healthy
- Zero blocking CI failures
- Grade A+ CI score (95/100)

Timeline: Days 3-20 (continuous healing + trending)
Status: Ready for delegation
```

### Prompt 3.2: ci-emergency-response-agent (Sub-agent)
```
Campaign: Production Readiness 2026, Track 3
Objective: Escalate and resolve blocking CI failures (critical path)

Responsibilities:
- Monitor for critical workflow failures (blocking PR merges)
- Escalate to human review if 3+ attempts fail
- Apply emergency fixes (e.g., runner config, timeout increases)
- Document root cause + permanent fix recommendation

Trigger Criteria:
- Workflow failure blocking PR merge >4 hours
- Repeated failure in same workflow >3 consecutive runs
- New critical failure pattern not in RP catalog

Timeline: Days 3-20 (on-demand escalation)
```

### Prompt 3.3: ci-testing-agent (Sub-agent)
```
Campaign: Production Readiness 2026, Track 3
Objective: Debug test collection errors, import issues, build problems

Focus Areas:
- P19 shadow import failures (special awareness required)
- Test collection errors (conftest.py issues, fixture conflicts)
- Import path errors (sys.path issues, relative imports)
- Build failures (package discovery, missing dependencies)

Deliverables:
- Test collection diagnostic report
- Import error resolution log
- Build error summary + fixes

Timeline: Days 3-15 (parallel with healer execution)
```

### Prompt 3.4: workflow-ci-fixer (Sub-agent)
```
Campaign: Production Readiness 2026, Track 3
Objective: Validate and fix YAML workflow syntax errors (actionlint)

Tasks:
- Run actionlint on all 49 active workflows
- Fix syntax errors (indentation, duplicate keys, type mismatches)
- Validate job names, step conditions, action versions
- Enforce Node.js 22+ baseline (memory fact: setup-node/deploy-pages v5+)

Deliverables:
- YAML validation report (pre/post actionlint)
- Fixed workflow files (committed)
- Action version compliance check (checkout>=v5, setup-python>=v6, etc.)

Timeline: Days 8-12 (YAML hardening phase)
```

---

## TRACK 4: DOCUMENTATION ALIGNMENT (45% → 90%+ coverage)

### Prompt 4.1: unified-doc-agent (Primary)
```
Campaign: Production Readiness 2026, Track 4 (Documentation Alignment)
Objective: Increase doc link coverage from 45% to 90%+, consolidate documentation

Context:
- Current coverage: 45% (many internal links break)
- Target coverage: 90%+ (<5 broken links acceptable)
- Doc scope: 20+ top-level files, 50+ supporting docs
- GitHub Pages: Needs post-merge alignment after fixes

Consolidation Strategy:
1. Link validation (internal + external URLs)
2. Freshness audit (stale content >30 days identification)
3. Taxonomy consolidation (organize docs hierarchy)
4. GitHub Pages generation + deployment

Deliverables:
- Link validation report (broken links, fix status)
- Freshness audit (stale content, update recommendations)
- Consolidation index (new doc taxonomy)
- Updated GitHub Pages (live deployment ready)
- Documentation quality scorecard

Success Criteria:
- Link coverage ≥90%
- Broken links <5
- Stale content >30 days: 0
- Doc taxonomy consolidated
- GitHub Pages synced

Timeline: Days 3-18 (parallel link validation + consolidation)
Status: Ready for delegation
```

### Prompt 4.2: doc-freshness-checker (Sub-agent)
```
Campaign: Production Readiness 2026, Track 4
Objective: Identify and remediate stale documentation

Tasks:
- Audit all 70+ doc files for:
  - Last-modified timestamps (>30 days = stale)
  - Code example accuracy (match current implementation)
  - Link accuracy (internal references valid)
- Generate freshness report with recommendations

Deliverables:
- Freshness audit report (per-file breakdown)
- Stale content recommendations (update vs. deprecate vs. delete)

Timeline: Days 3-10 (parallel with link validation)
```

### Prompt 4.3: link-validator-agent (Sub-agent)
```
Campaign: Production Readiness 2026, Track 4
Objective: Detect and fix broken links (internal + external)

Tasks:
- Scan all 70+ markdown files for:
  - Internal links (broken paths, wrong anchors)
  - External links (dead URLs, redirects)
- Generate fix report (automated fixes where possible)
- Validate GitHub Pages navigation

Deliverables:
- Link validation report (broken, redirect, valid categorized)
- Fixed markdown files (automated corrections)
- GitHub Pages navigation validation

Timeline: Days 3-12 (continuous validation)
```

### Prompt 4.4: terminology-consistency-agent (Sub-agent)
```
Campaign: Production Readiness 2026, Track 4
Objective: Enforce consistent terminology across documentation

Tasks:
- Build glossary from existing docs (codex-ml terminology)
- Identify inconsistent usage (code vs code-ml, agent vs custom-agent)
- Apply consistent terminology across all files
- Document terminology standards

Deliverables:
- Glossary document (20+ key terms, approved spellings)
- Consistency report (before/after fixes)

Timeline: Days 12-18 (follows initial link validation)
```

---

## TRACK 5: DEPLOYMENT READINESS (80% → 100%)

### Prompt 5.1: self-healing-orchestrator-agent (Primary)
```
Campaign: Production Readiness 2026, Track 5 (Deployment Readiness)
Objective: Validate Phase 8 (Days 1-5) deployment procedures, test rollback

Context:
- Phase 8-10 documented in PHASE_8_10_DETAILED_IMPLEMENTATION_PLAN.md (780 lines)
- Phase 8 focus: backup, infrastructure validation, quality gates (5 days)
- Phase 9: canary deployment + regional rollout (5 days)
- Phase 10: full production + monitoring (5+ days)

Phase 8 Dry-Run Tasks:
1. Environment validation (infra specs, database, storage)
2. Backup procedures (full backup, test restore)
3. Quality gate checks (all CI passing, coverage >15%, security 0 critical)
4. Pre-deployment checklist (32 items from PRODUCTION_READINESS_CHECKLIST.md)
5. Rollback procedure testing (automatic triggers: error rate >5%, p99 >10s)

Deliverables:
- Phase 8 validation report (environment + backup verification)
- Rollback test results (automatic triggers executed)
- Environment checklist (all 32 items validated)
- Deployment readiness gate (GO/NO-GO recommendation)

Success Criteria:
- All Phase 8 procedures validated
- Rollback tested successfully (0 data loss)
- Quality gates all PASS
- Deployment readiness 100%

Timeline: Days 10-18 (deployment validation phase)
Status: Ready for delegation
```

### Prompt 5.2-5.4: Infrastructure Validation Specialists
```
Campaign: Production Readiness 2026, Track 5
Objective: Validate infrastructure components (3 specialist areas)

Specialists:
1. Infrastructure validator: Environment specs, networking, compute resources
2. Backup verifier: Backup procedures, restore verification, RTO/RPO validation
3. Rollback tester: Automatic triggers, manual rollback procedures, data safety

Deliverables:
- Infrastructure validation report (all components checked)
- Backup/restore verification (tested recovery from 7-day-old backup)
- Rollback test results (automatic + manual triggers validated)

Timeline: Days 10-16 (parallel infrastructure validation)
```

---

## TRACK 6: MEMORY OPTIMIZATION (286 → 320+ PDA iterations)

### Prompt 6.1: memory-sync-agent (Primary)
```
Campaign: Production Readiness 2026, Track 6 (Memory Optimization)
Objective: Consolidate STM→LTM memory, promote high-confidence patterns

Context:
- Current PDA iterations: 286 (from .codex/aftermath/pda_iterations.jsonl)
- Target PDA iterations: 320+ (+12% growth)
- Memory health: 10/10 current baseline (maintain)
- Session tracking: 1,400 sessions recorded (analyze patterns)

Memory Consolidation Tasks:
1. STM→LTM promotion: Consolidate high-confidence patterns
2. Stale entry eviction: Remove patterns unused >30 days
3. Pattern confidence tagging: Assign ImprovementArea tags
4. Session intelligence: Extract session 1400+ patterns

PDA Entry Creation (Target: +34 new entries):
- Type: memory_consolidation
- Pattern: Promote 34 high-confidence patterns from sessions
- Timestamp: Mark each with discovery session + confidence score

Deliverables:
- Updated PDA iterations snapshot (.jsonl with 320+ entries)
- Memory health report (STM/LTM balance, confidence distribution)
- Pattern promotion log (34 promoted patterns documented)
- Session intelligence index (sessions 1-1400 pattern analysis)

Success Criteria:
- PDA iterations ≥320
- Memory health score 10/10
- <5% stale entries
- 34+ patterns promoted

Timeline: Days 8-16 (memory consolidation phase)
Status: Ready for delegation
```

### Prompt 6.2: session-analysis-agent (Sub-agent)
```
Campaign: Production Readiness 2026, Track 6
Objective: Analyze commit patterns across sessions 1-1400

Tasks:
- Analyze 1,400 sessions for common patterns
- Identify high-impact fixes (applied across multiple PRs)
- Extract recurring issue types (coverage, security, CI)
- Generate session intelligence recommendations

Deliverables:
- Session pattern analysis (recurring issues + solutions)
- High-impact fix recommendations
- Session intelligence index

Timeline: Days 8-12
```

### Prompt 6.3: cognitive-brain-session-injector (Sub-agent)
```
Campaign: Production Readiness 2026, Track 6
Objective: Inject session context and close AfterMath/PDA loop

Tasks:
- Call AgentBrainAPI.get_session_context() at phase boundaries
- Inject recency-ranked patterns into system prompt
- Close AfterMath loop with report_completion() after Track 6

Deliverables:
- Session context injection logs
- PDA loop closure confirmation

Timeline: Days 14-16 (integration point)
```

---

## TRACK 7: GOVERNANCE & COMPLIANCE (85/100 → 95/100)

### Prompt 7.1: unified-governance-gate (Primary)
```
Campaign: Production Readiness 2026, Track 7 (Governance & Compliance)
Objective: Increase governance compliance from 85/100 to 95/100

Context:
- WEC (Workflow Execution Checklist): 8 always-required items
- Policy compliance: 8 governance policies to enforce
- Workflow portfolio: 49 active workflows to validate
- Autonomy level: D (full delegation authority)

Governance Validation Tasks:
1. WEC enforcement: Verify all 8 always-required items checked in PRs
2. Policy compliance: Validate 8 governance policies (no violations)
3. Workflow health: Grade all 49 workflows (target: Grade A+)
4. Artifact health: Validate 22 campaign deliverables

WEC Always-Required Items:
- [ ] agent-auth-delegation (auth permanent)
- [ ] auto-approve-workflows (pre-approved for campaign)
- [ ] code-review (PR review gates)
- [ ] codeql-fix (security scanning)
- [ ] coverage-validation (coverage ratchet)
- [ ] documentation (doc quality gates)
- [ ] security-baseline (secrets scanning)
- [ ] test-validation (CI passing)

Policy Validation:
1. Codebase Agency Policy: No deferral language (pre-existing, future PR, out of scope)
2. Authorization Policy: Auth enabled, no approval gates needed
3. Agent Delegation: Custom agents delegated correctly
4. Artifact Storage: All files in .codex/*, never /tmp/
5. Memory Integration: Stored facts applied consistently
6. Review Workflow: Commit SHAs replied on all unresolved comments
7. Progress Tracking: Daily reports via engine-tools-report_progress
8. Zero-Deferral: All discovered issues fixed same session

Deliverables:
- WEC enforcement report (8 items validated)
- Policy compliance matrix (0 violations)
- Workflow health final report (49 workflows graded)
- Governance scorecard (target: 95/100)

Success Criteria:
- Governance score ≥95/100
- 0 policy violations
- All 8 WEC items compliant
- All 49 workflows Grade A+

Timeline: Days 10-20 (governance validation phase)
Status: Ready for delegation
```

### Prompt 7.2: workflow-health-monitor (Sub-agent)
```
Campaign: Production Readiness 2026, Track 7
Objective: Monitor workflow portfolio health (49 active workflows)

Tasks:
- Grade all 49 workflows (performance, reliability, design)
- Identify outdated actions (enforce v5+ baseline)
- Detect unused workflows (unused >60 days)
- Generate workflow health scorecard

Deliverables:
- Workflow health report (per-workflow breakdown)
- Action version compliance check
- Unused workflow detection

Timeline: Days 10-16
```

### Prompt 7.3: workflow-compliance-guardian (Sub-agent)
```
Campaign: Production Readiness 2026, Track 7
Objective: Enforce compliance rules (concurrency, timeout, Node.js baseline)

Tasks:
- Validate concurrency rules (branch-scoped + correct timeouts)
- Enforce Node.js 22+ baseline in all workflows
- Check action version policy (setup-node>=v5, deploy-pages>=v5)
- Auto-heal violations (update workflow files)

Deliverables:
- Compliance audit report
- Auto-healed workflow files
- Compliance gate verification

Timeline: Days 12-18
```

---

## TRACK 8: CACHE OPTIMIZATION (72% → 85%+ hit rate)

### Prompt 8.1: cache-management-agent (Primary)
```
Campaign: Production Readiness 2026, Track 8 (Cache Optimization)
Objective: Increase cache hit rate from 72% to 85%+

Context:
- Current hit rate: 72% (baseline acceptable)
- Target hit rate: 85%+ (Grade A optimization)
- Cache layers: 4-layer hierarchy documented in docs/workflows/CACHE_POLICY.md
- Cache types: artifact, dependency, build, runtime

4-Layer Cache Hierarchy:
1. L1 (Run-level): actions/cache@v5 (per-job, fastest)
2. L2 (Workflow-level): cache keys shared across jobs
3. L3 (Repository-level): shared across all workflows
4. L4 (External): S3/GCS/Azure storage (slowest, persistent)

Optimization Tasks:
1. Analyze cache usage patterns (hit rate by layer)
2. Identify cache misses (poor key design, invalidation)
3. Tune cache keys (optimize specificity vs. generality)
4. Document optimization recommendations

Deliverables:
- Cache hierarchy performance analysis (per-layer hit rates)
- Hit rate improvement recommendations (72% → 85%+ path)
- Configuration optimization guide (cache key tuning)
- Performance gains documentation (latency reduction metrics)

Success Criteria:
- Cache hit rate ≥85%
- L1 hit rate ≥90% (run-level fastest)
- Avg retrieval time <2 seconds
- No cache invalidation failures

Timeline: Days 12-18 (cache performance tuning)
Status: Ready for delegation
```

### Prompt 8.2: cache-manager-integration (Sub-agent)
```
Campaign: Production Readiness 2026, Track 8
Objective: Analyze 4-layer cache hierarchy, recommend integrations

Tasks:
- Audit cache configuration across all 49 workflows
- Identify layer usage patterns (which workflows use which layers)
- Recommend layer integration optimizations
- Test cache invalidation procedures

Deliverables:
- Cache layer integration report
- Optimization recommendations per workflow

Timeline: Days 12-16
```

---

## EXECUTION CHECKLIST (Days 3-20)

### Daily Report Structure
Each track provides daily updates using this format:

```markdown
## Daily Report (Day N)

### Track X: [Track Name]
- **Status:** IN_PROGRESS / BLOCKED / COMPLETE
- **Metric Progress:** [Baseline] → [Current] (% delta)
- **Artifacts Generated:** X of Y (list files)
- **Blockers:** None / [List]
- **Next Steps:** [Day N+1 plan]

Primary Agent Status: [Agent Name] — [% completion]
Sub-Agent Status:
- [Agent 1] — [% completion]
- [Agent 2] — [% completion]
```

### Consolidated Daily Reports
- **Days 3-7:** Individual track reports (8 reports/day)
- **Days 8-14:** Batched track reports (2-3 consolidated reports/day)
- **Days 15-20:** Final track summaries (completion reports)

### Progress Tracking Tool
- Use: `engine-tools-report_progress`
- Frequency: Daily batched updates (2-3 times/day)
- Include: All 8 track summaries in single report
- Commit: Daily artifacts to `.codex/campaign-artifacts/`

---

## DELEGATION INVOCATION TEMPLATE

**For Days 3-20, invoke each track using:**

```bash
task(
    name="campaign-track-[N]-primary",
    agent_type="[primary-agent]",
    mode="background",
    prompt="""
    [Full track prompt above]

    Campaign: Production Readiness 2026
    Track: [Track Name] ([N] of 8)
    Timeline: Days [Start]-[End]
    Deliverables: [Count] artifacts
    Success Criteria: [List]
    """
)

# For sub-agents (execute in parallel):
task(
    name="campaign-track-[N]-sub-1",
    agent_type="[sub-agent-1]",
    mode="background",
    prompt="[Sub-prompt above]"
)

task(
    name="campaign-track-[N]-sub-2",
    agent_type="[sub-agent-2]",
    mode="background",
    prompt="[Sub-prompt above]"
)
```

---

## NEXT STEPS (Day 2, Phase A Completion)

1. **Finalize Delegation Prompts** (this file + Track 1-8 sections)
2. **Get Team Feedback** (discussion #4872 review)
3. **Pre-flight Agent Checks** (verify all 35 agents available)
4. **PDA Entry Creation** (campaign_plan type, snapshot baseline metrics)
5. **Day 3 Kickoff Ready** (all 8 primary agents + 24 sub-agents ready to invoke)

---

**Document Version:** 1.0  
**Last Updated:** 2026-06-16T13:15:39Z  
**Campaign Status:** Phase A — READY FOR DAY 3 PHASE B KICKOFF
