# Phase B Tracks 4-8 Invocation Prompts (Ready for Parallel Execution)

These prompts are prepared for immediate launch as agent capacity becomes available.

---

## TRACK 4: DOCUMENTATION AUDIT PROMPT

**PHASE B TRACK 4: DOCUMENTATION AUDIT (45% → 90%+ coverage)**
**Campaign:** Production Readiness 2026
**Timeline:** Days 3-18 (parallel with all 8 tracks)
**Authorization:** COPILOT_AGENT_AUTH_ENABLED=true, autonomy level D

**OBJECTIVE:** Increase documentation coverage and link validity from 45% to 90%+

**PARALLEL SUB-AGENTS:**
- doc-freshness-checker (staleness audit)
- link-validator-agent (broken links remediation)
- terminology-consistency-agent (glossary enforcement)

**IMMEDIATE ACTIONS (Today, Days 3+):**
1. Full documentation audit:
   - Scan all .md files in docs/ (20+ files)
   - Check link validity (internal + external)
   - Validate against current source code state
   - Check terminology consistency
2. Generate coverage report (by doctype: API, CLI, architecture, guides)
3. Identify stale/outdated sections
4. Apply fixes in parallel for:
   - Broken links (internal references)
   - API documentation drift
   - CLI command changes
   - Architecture misalignment
5. Consolidate glossary and terminology

**DELIVERABLES:**
- Documentation coverage report (45% baseline → 90%+ target)
- Link validation matrix (broken links identified and fixed)
- Freshness audit (updated timestamps, staleness flags)
- Terminology consistency report
- Documentation-to-code alignment matrix

**SUCCESS CRITERIA:**
- Documentation coverage ≥90%
- <5 broken internal links remaining
- All external links verified or marked for review
- Terminology consistent across 20+ docs
- API/CLI docs aligned with current source

**CONSTRAINTS:**
- All doc-checking agents run in parallel
- Daily updates to `.codex/campaign-artifacts/track-4-documentation/` (repository path, NOT /tmp)
- No deferred issues (fix all discovered problems same session)
- Preserve document structure and navigation

**REPORT LOCATION:** `.codex/campaign-artifacts/track-4-documentation/TRACK_4_DAILY_REPORT_$(date +%Y%m%d).md`

---

## TRACK 5: DEPLOYMENT READINESS PROMPT

**PHASE B TRACK 5: DEPLOYMENT READINESS (80% → 100%)**
**Campaign:** Production Readiness 2026
**Timeline:** Days 10-18 (parallel with all 8 tracks, may start after base setup)
**Authorization:** COPILOT_AGENT_AUTH_ENABLED=true, autonomy level D

**OBJECTIVE:** Achieve 100% production deployment readiness through validation and rollback testing

**INFRASTRUCTURE VALIDATORS:**
- Verify Kubernetes manifests (k8s/*.yaml)
- Validate container configurations (Dockerfile*)
- Check infrastructure-as-code (Terraform, CloudFormation)
- Verify backup & recovery procedures
- Test rollback scenarios (Phase 8-10 procedures)

**IMMEDIATE ACTIONS (Days 10+, or Days 3+ if you prefer):**
1. Baseline deployment readiness assessment (80% current)
2. Identify deployment blockers:
   - Missing config validation
   - Untested rollback procedures
   - Undocumented manual steps
   - Missing health checks
3. Execute in parallel:
   - Infrastructure validation suite
   - Rollback procedure testing
   - Recovery procedure validation
   - Load/stress testing (if applicable)
4. Generate deployment checklist

**DELIVERABLES:**
- Deployment readiness scorecard (80% → 100% target)
- Infrastructure validation report (manifests, configs, IAC)
- Rollback procedure test results
- Backup/recovery validation log
- Production deployment checklist (100% items verified)
- Risk mitigation report

**SUCCESS CRITERIA:**
- Deployment readiness score 100%
- 0 blockers in infrastructure
- All rollback procedures tested and documented
- Recovery procedures validated
- Pre-deployment checklist 100% complete

**CONSTRAINTS:**
- Parallel validation and testing agents
- Daily updates to `.codex/campaign-artifacts/track-5-deployment/` (repository path, NOT /tmp)
- No deferred issues (fix all discovered problems same session)
- Preserve production infrastructure safety

**REPORT LOCATION:** `.codex/campaign-artifacts/track-5-deployment/TRACK_5_DAILY_REPORT_$(date +%Y%m%d).md`

---

## TRACK 6: MEMORY SYNC PROMPT

**PHASE B TRACK 6: MEMORY & SESSION ANALYSIS (286 → 320+ PDA)**
**Campaign:** Production Readiness 2026
**Timeline:** Days 8-16 (parallel with all 8 tracks)
**Authorization:** COPILOT_AGENT_AUTH_ENABLED=true, autonomy level D

**OBJECTIVE:** Optimize memory consolidation from 286 to 320+ PDA iterations

**PARALLEL SUB-AGENTS:**
- session-analysis-agent (session event analysis)
- cognitive-brain-session-injector (session injection)

**IMMEDIATE ACTIONS (Days 8+):**
1. Baseline memory state:
   - Count current PDA iterations (target: 286 → 320+)
   - Analyze STM utilization
   - Identify stale/evictable entries
2. Execute memory consolidation:
   - STM → LTM consolidation at 80% capacity
   - Prune stale patterns
   - Tag patterns with ImprovementArea
3. Session injection optimization:
   - Analyze recent session history
   - Optimize recency ranking
   - Test session context injection
4. Update MemoryManagementDashboard metrics

**DELIVERABLES:**
- Memory consolidation report (STM/LTM analysis)
- PDA iteration growth log (286 → 320+)
- Stale pattern pruning report
- Session injection test results
- Memory health metrics dashboard

**SUCCESS CRITERIA:**
- PDA iterations ≥320
- STM utilization <80%
- <10% stale entries remaining
- Session context injection working correctly
- Memory management dashboard updated

**CONSTRAINTS:**
- Parallel sub-agents
- Daily updates to `.codex/campaign-artifacts/track-6-memory/` (repository path, NOT /tmp)
- Preserve backward compatibility
- No data loss during consolidation

**REPORT LOCATION:** `.codex/campaign-artifacts/track-6-memory/TRACK_6_DAILY_REPORT_$(date +%Y%m%d).md`

---

## TRACK 7: GOVERNANCE & COMPLIANCE PROMPT

**PHASE B TRACK 7: GOVERNANCE & COMPLIANCE (85/100 → 95/100)**
**Campaign:** Production Readiness 2026
**Timeline:** Days 10-20 (parallel with all 8 tracks)
**Authorization:** COPILOT_AGENT_AUTH_ENABLED=true, autonomy level D

**OBJECTIVE:** Increase governance score from 85/100 to 95/100

**PARALLEL SUB-AGENTS:**
- workflow-health-monitor (workflow health tracking)
- workflow-compliance-guardian (compliance enforcement)

**IMMEDIATE ACTIONS (Days 10+):**
1. Governance audit:
   - Review 49 active workflows
   - Check branch concurrency + timeout rules (S174 protocol)
   - Verify action version pins (enforce_actions_versions.py requirements)
   - Validate WEC (Workflow Execution Checklist) grouping
2. Identify compliance gaps:
   - Outdated GitHub Actions versions
   - Missing workflow documentation
   - Non-compliant naming conventions
   - Unauthorized workflow patterns
3. Execute fixes in parallel:
   - Action version upgrades (to latest safe versions)
   - Concurrency/timeout rule auto-healing
   - WEC checklist validation and repair
   - Workflow documentation generation
4. Compliance gate verification

**DELIVERABLES:**
- Governance audit report (85 → 95/100 score)
- Workflow compliance matrix (49 workflows × 10 criteria)
- Action version upgrade log
- Concurrency/timeout rule auto-heals
- WEC grouping validation report
- Compliance gate verification results

**SUCCESS CRITERIA:**
- Governance score ≥95/100
- All 49 workflows compliant with rules
- 0 outdated action versions
- WEC checklist 100% accurate
- Branch concurrency + timeout rules enforced on all CI workflows

**CONSTRAINTS:**
- Parallel compliance agents
- Daily updates to `.codex/campaign-artifacts/track-7-governance/` (repository path, NOT /tmp)
- Do not break existing workflows
- Preserve workflow parity

**REPORT LOCATION:** `.codex/campaign-artifacts/track-7-governance/TRACK_7_DAILY_REPORT_$(date +%Y%m%d).md`

---

## TRACK 8: CACHE OPTIMIZATION PROMPT

**PHASE B TRACK 8: CACHE OPTIMIZATION (72% → 85%+ hit rate)**
**Campaign:** Production Readiness 2026
**Timeline:** Days 12-18 (parallel with all 8 tracks)
**Authorization:** COPILOT_AGENT_AUTH_ENABLED=true, autonomy level D

**OBJECTIVE:** Optimize cache hit rate from 72% to 85%+ across 4-layer hierarchy

**PARALLEL SUB-AGENTS:**
- cache-manager-integration (integration and coordination)

**IMMEDIATE ACTIONS (Days 12+):**
1. Cache performance baseline:
   - Analyze hit/miss rates across 4 cache layers
   - Identify cold-start patterns
   - Profile eviction policies
   - Measure cache efficiency
2. Optimization strategy:
   - Layer 1 (Build artifacts): Improve key generation
   - Layer 2 (Python packages): Optimize pip cache keying
   - Layer 3 (Test results): Reduce flaky test cache pollution
   - Layer 4 (ML models): Implement smarter eviction
3. Execute optimization:
   - Adjust cache key strategies
   - Tune TTL/eviction policies
   - Implement better cache warming
   - Add cache efficiency metrics
4. Validation and testing

**DELIVERABLES:**
- Cache performance baseline report (72% hit rate starting)
- Per-layer cache analysis (4 layers × optimization strategies)
- Cache key strategy improvements
- Hit rate trend (72% → 85%+ target)
- Cache efficiency metrics dashboard
- Optimization results (hit rate, savings, performance impact)

**SUCCESS CRITERIA:**
- Cache hit rate ≥85% (target from 72% baseline)
- <10% eviction churn
- Average cache miss penalty <2s
- All 4 layers optimized
- Cache efficiency dashboard updated

**CONSTRAINTS:**
- Parallel optimization agents
- Daily updates to `.codex/campaign-artifacts/track-8-cache/` (repository path, NOT /tmp)
- Do not break build reproducibility
- Maintain cache correctness (no stale cache serves)

**REPORT LOCATION:** `.codex/campaign-artifacts/track-8-cache/TRACK_8_DAILY_REPORT_$(date +%Y%m%d).md`

---

**All 8 prompts are ready for immediate parallel invocation as agent capacity becomes available.**
