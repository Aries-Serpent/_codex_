# 📊 CHECKPOINT MONITORING TEMPLATE

## How to Use This Template

Copy this template to create checkpoint reports as lanes complete:

```
.codex/PHASE_1_CHECKPOINT_REPORT.md (2026-06-21 ~21:00Z)
.codex/PHASE_2_CHECKPOINT_REPORT.md (2026-06-22 ~06:08Z)
.codex/PHASE_3_CHECKPOINT_REPORT.md (2026-06-22 ~12:08Z)
.codex/CAMPAIGN_FINAL_CONSOLIDATION_REPORT.md (2026-06-22 ~14:00Z)
```

---

## CHECKPOINT FORMAT

### Checkpoint Header
```
# 📊 PHASE N CHECKPOINT REPORT
**Checkpoint Time:** [timestamp]
**Duration Since Start:** [hours:minutes]
**Status:** 🟢 ON TRACK | 🟡 MONITORING | 🔴 BLOCKED
```

### Lane Status Table
```
| Lane | Agent | Task | Status | Progress | ETA |
|------|-------|------|--------|----------|-----|
| 1 | unified-coverage-agent | Phase 1A | ⏳/✅ | X% | ... |
| 2 | unified-security-scanner | Audit | ⏳/✅ | X% | ... |
| 3 | ci-auto-healer-agent | Stabilization | ⏳/✅ | X% | ... |
| 4 | unified-doc-agent | Documentation | ⏳/✅ | X% | ... |
| 5 | qa-walkthrough-agent | Readiness | ⏳/✅ | X% | ... |
```

### Metrics Dashboard
```
| Metric | Current | Target | Δ | Status |
|--------|---------|--------|---|--------|
| Coverage | X% | 22% | +Ypp | 🟢/🟡 |
| Security Issues | 0 | 0 | ±0 | ✅ |
| CI Failure Rate | X% | <1% | -Y% | 🟢/🟡 |
| Tests | N | 300 | +N | 🟢/🟡 |
| Governance Gates | 32/32 | 32/32 | ±0 | ✅ |
| Docs Accuracy | X% | 100% | +Y% | 🟢/🟡 |
```

### Issues & Resolutions
```
## 🟡 Issues Detected

### Issue 1: [Title]
- Lane: X
- Status: ⏳ IN PROGRESS
- Severity: 🟡 MEDIUM
- Resolution: [action taken]
- ETA: [timestamp]

## ✅ Resolved This Checkpoint
- [Resolved issue 1]
- [Resolved issue 2]
```

### Next Checkpoint
```
**Next Checkpoint:** [date/time]
**Expected Deliverables:**
- [ ] LANE 1: Phase 1A gap closure
- [ ] LANE 2: Security audit results
- [ ] LANE 3: CI stabilization complete
- [ ] LANE 4: Documentation sync
- [ ] LANE 5: Readiness verification
```

---

## REAL-TIME MONITORING

### Monitor Agent Progress
```bash
# Check individual lane agent
read_agent agent_id=lane-1-coverage-expansion wait=true timeout=300

# List all agents
list_agents include_completed=false
```

### Update Dashboard
```bash
# Update main campaign dashboard
# Manually edit: .codex/CAMPAIGN_PROGRESS_DASHBOARD.md
# Update real-time metrics section
```

### Create Checkpoint
When agents complete:
1. Copy this template
2. Fill in metrics from agent reports
3. Document issues & resolutions
4. Commit checkpoint
5. Update dashboard
