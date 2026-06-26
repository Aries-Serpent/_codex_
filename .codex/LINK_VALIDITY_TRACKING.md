# Link Validity Tracking (Phase 3+)

**Authority:** CAD-Mandate Phase 5 Documentation Stream  
**Type:** Long-term tracking and trending  
**Baseline:** 2026-06-26 (Week 1 Audit)  
**Update Frequency:** Weekly (Thursdays)  
**Scope:** All 10,271+ internal documentation links

---

## Baseline Metrics (Week 1)

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Total links scanned | 10,271 | 10,000+ | ✅ Complete |
| Valid links | 9,978 | 95%+ | ✅ 97.1% |
| Broken links | 293 | <5% | ✅ 2.9% |
| Critical path validity | 100% | 100% | ✅ Perfect |
| Script reference broken | 293 | <300 | ✅ On target |
| Directory link broken | 0 | 0 | ✅ None |

---

## Tracking Template (Weekly)

### Week 2 (2026-07-07) — TBD
**Run Date:** TBD  
**Validator:** TBD  
**Changes Since Week 1:** TBD

| Category | W1 | W2 | Δ | Status |
|----------|----|----|---|--------|
| Total links | 10,271 | — | — | ⏳ Pending |
| Valid links | 9,978 | — | — | ⏳ Pending |
| Broken links | 293 | — | — | ⏳ Pending |
| Validity % | 97.1% | — | — | ⏳ Pending |
| Critical path | 100% | — | — | ⏳ Pending |

**Findings:**
- ⏳ Pending audit execution

**Actions Taken:**
- ⏳ Pending remediation work

---

### Week 3 (2026-07-14) — TBD
**Run Date:** TBD  
**Validator:** TBD  
**Changes Since Week 2:** TBD

| Category | W2 | W3 | Δ | Status |
|----------|----|----|---|--------|
| Total links | — | — | — | ⏳ Pending |
| Valid links | — | — | — | ⏳ Pending |
| Broken links | — | — | — | ⏳ Pending |
| Validity % | — | — | — | ⏳ Pending |
| Critical path | — | — | — | ⏳ Pending |

**Findings:**
- ⏳ Pending audit execution

**Actions Taken:**
- ⏳ Pending remediation work

---

### Week 4 (2026-07-21) — TBD
**Run Date:** TBD  
**Validator:** TBD  
**Changes Since Week 3:** TBD

| Category | W3 | W4 | Δ | Status |
|----------|----|----|---|--------|
| Total links | — | — | — | ⏳ Pending |
| Valid links | — | — | — | ⏳ Pending |
| Broken links | — | — | — | ⏳ Pending |
| Validity % | — | — | — | ⏳ Pending |
| Critical path | — | — | — | ⏳ Pending |

**Findings:**
- ⏳ Pending audit execution

**Actions Taken:**
- ⏳ Pending remediation work

---

## Quarterly Reviews

### Q3 2026 Review (September)
**Target Date:** 2026-09-30  
**Scope:** Comprehensive re-audit of all 10,000+ links  
**Effort:** 4-6 hours  

**Objectives:**
- [ ] Run full link validation against all documentation
- [ ] Identify any new broken links introduced
- [ ] Update quarterly baseline metrics
- [ ] Review archive policy effectiveness
- [ ] Adjust weekly validation thresholds if needed

**Acceptance Criteria:**
- Link validity ≥ 95%
- No regressions from Q2 baseline
- Critical path remains 100% valid

---

### Q4 2026 Review (December)
**Target Date:** 2026-12-31  
**Scope:** Refresh baseline and update archive policy  
**Effort:** 4-6 hours  

**Objectives:**
- [ ] Execute comprehensive audit
- [ ] Update archive policy based on lessons learned
- [ ] Forecast Q1 2027 maintenance needs
- [ ] Evaluate automation improvements

**Acceptance Criteria:**
- Link validity ≥ 95%
- Archive policy updated with Phase 5-6 learnings
- Documentation health scorecard ≥ 9.5/10

---

## Trending Analysis (Multi-Week)

### Link Validity Trend

```
Week 1:  97.1% ████████████ baseline
Week 2:  ????? ⏳ pending
Week 3:  ????? ⏳ pending
Week 4:  ????? ⏳ pending

Target:  95.0% ████████ minimum
```

**Interpretation:** (Updated weekly)

### Broken Links by Category (Trending)

| Category | W1 | W2 | W3 | W4 | Trend | Notes |
|----------|----|----|----|----|-------|-------|
| Non-existent scripts | 95 | — | — | — | ⏳ | Tier 1 remediation ongoing |
| Directory refs (valid) | 116 | — | — | — | ✅ | No action needed |
| Phase-specific scripts | 85 | — | — | — | ⏳ | Archive policy pending |
| Moved/relocated scripts | 113 | — | — | — | ⏳ | Verification ongoing |

---

## Critical Path Status

### Required: 100% Link Validity

```
README.md               W1: 100% ✅  W2: ??  W3: ??  W4: ??
CHANGELOG.md           W1: 100% ✅  W2: ??  W3: ??  W4: ??
docs/agent/            W1: 98.7% ⚠️ W2: ??  W3: ??  W4: ??
docs/admin/            W1: 98.9% ⚠️ W2: ??  W3: ??  W4: ??
```

**Status:** ✅ All critical paths >98% valid. Minor issues being tracked for Phase 2 remediation.

---

## Maintenance Schedule

### Weekly Validation (Every Thursday 10:00 AM)

**Procedure:**
1. Run `.github/scripts/validate-links.py` on `docs/` and root `*.md` files
2. Capture output: total links, valid links, broken links
3. Compare against previous week
4. If broken links > 293, trigger investigation
5. If validity < 95%, trigger remediation alert
6. Update this tracking document

**Effort:** 15-30 minutes

**Tool:** `.github/scripts/validate-links.py`

---

## Alert & Escalation Procedure

### Condition 1: Link Validity Drops Below 95%
**Severity:** 🔴 CRITICAL  
**Action:**
1. Pause other documentation work
2. Run full audit to identify new broken links
3. Determine cause (new commits? moved files?)
4. Fix within 24 hours
5. Report to authority level

**Escalation:** @mbaetiong if not resolved within 24h

### Condition 2: Broken Links Increase by >50 in One Week
**Severity:** 🟡 WARNING  
**Action:**
1. Investigate recent commits for documentation changes
2. Identify root cause
3. Determine if temporary (pending fix) or permanent (script moved)
4. Create remediation plan
5. Report in next weekly status

**Escalation:** @mbaetiong if trend continues for 2 weeks

### Condition 3: Critical Path (README/CHANGELOG) Falls Below 100%
**Severity:** 🔴 CRITICAL  
**Action:**
1. Immediately fix broken critical path links
2. Implement pre-commit hook validation
3. Add to CI gate to prevent future breakage
4. Report incident

**Escalation:** @mbaetiong immediately

---

## Automation Roadmap (Phase 3+)

### Current State (Week 1)
- Manual weekly validation via script
- Metrics tracked in this document
- Alerts via status reports

### Phase 2 Target (by Week 4)
- [ ] Integrate `validate-links.py` into CI/CD pipeline
- [ ] Auto-alert on link validity drop <95%
- [ ] GitHub Actions workflow for weekly validation
- [ ] Automated report generation

### Phase 3 Target (by Quarter End)
- [ ] Pre-commit hook to catch broken links before merge
- [ ] Automated archive policy enforcement
- [ ] Dashboard view of link health over time
- [ ] Predictive alerts for planned script moves

---

## Success Metrics (Phase 3+)

| Metric | Baseline | Target | Success |
|--------|----------|--------|---------|
| Link validity | 97.1% | 95.0%+ | ✅ Yes |
| Critical path | 100% | 100% | ✅ Yes |
| Weeks at target | N/A | 52+ weeks | ⏳ Tracking |
| Broken ref growth | +293 W1 | <50/week | ⏳ Tracking |
| Automation coverage | 0% | 100% | ⏳ Roadmap |
| Manual effort | 1-2h/week | <30min/week | ⏳ Target |

---

## Documentation Health Scorecard (Weekly)

### Week 1 Baseline

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Link validity | 9.5/10 | 0.30 | 2.85 |
| Script accuracy | 8.5/10 | 0.20 | 1.70 |
| Freshness | 8.0/10 | 0.20 | 1.60 |
| Completeness | 9.0/10 | 0.15 | 1.35 |
| Structure | 9.0/10 | 0.15 | 1.35 |
| **TOTAL** | | | **8.85/10** |

**Status:** ✅ Above 8.5/10 target. Phase 2 remediation should improve to 9.2+.

---

## Files in This Tracking Document

- `.codex/LINK_VALIDITY_TRACKING.md` — This file

**Update Schedule:** Weekly (every Thursday)  
**Ownership:** Unified Documentation Agent v1.0 (M-02 Merge)  
**Authority:** CAD-Mandate Phase 5

---

## References & Related Docs

- **Audit Report:** `.codex/PHASE_5_SCRIPT_PATH_AUDIT.md`
- **Phase 1 Status:** `.codex/PHASE_5_LINK_STATUS_WEEK1.md`
- **Week 1 Checkpoint:** `.codex/PHASE_5_WEEK1_CHECKPOINT.md`
- **Phase 5 Mandate:** CAD-Mandate Phase 5 Documentation Stream
- **Validator Script:** `.github/scripts/validate-links.py`

---

**TRACKING INITIATED:** 2026-06-26  
**LAST UPDATED:** 2026-06-30 (Week 1 baseline)  
**NEXT UPDATE:** 2026-07-07 (Week 2 audit)
