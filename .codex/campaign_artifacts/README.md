# Campaign Artifacts Directory Structure & Retention Policy

**Directory:** `.codex/campaign_artifacts/`

## Overview

This directory contains all artifacts generated during Phase 8-9 production deployment campaign execution. All artifacts are retained for compliance review and historical documentation (90-day retention minimum).

---

## Directory Structure

```
.codex/campaign_artifacts/
├── canary_logs/              # Canary deployment logs (2-4 hour window)
│   ├── error_logs.txt
│   ├── latency_logs.txt
│   ├── health_check_logs.txt
│   └── metrics_summary.json
│
├── regional_logs/            # Regional rollout logs (6-8 hour window)
│   ├── regional_error_logs.txt
│   ├── regional_latency_logs.txt
│   └── regional_metrics.json
│
├── production_logs/          # Production deployment logs (24+ hour window)
│   ├── production_error_logs.txt
│   ├── production_latency_logs.txt
│   ├── production_metrics.json
│   ├── memory_analysis.txt
│   └── test_results.json
│
└── post_campaign/            # Post-campaign documentation
    ├── CAMPAIGN_COMPLETION_REPORT.md
    ├── CAMPAIGN_LESSONS_LEARNED.md
    └── CAMPAIGN_AUDIT_TRAIL.md
```

---

## Artifact Retention Policy

| Artifact Type | Retention Period | Storage Location | Purpose |
|---|---|---|---|
| **Canary Logs** | 30 days | `.codex/campaign_artifacts/canary_logs/` | Audit trail, troubleshooting |
| **Regional Logs** | 30 days | `.codex/campaign_artifacts/regional_logs/` | Audit trail, troubleshooting |
| **Production Logs** | 90 days | `.codex/campaign_artifacts/production_logs/` | Compliance, incident investigation |
| **Approval Forms** | 90 days | `.codex/PHASE_*_GATE_*_APPROVAL_FORM.md` | Compliance, audit trail |
| **Status Trackers** | 30 days | `.codex/PHASE_*_STATUS_TRACKER.json` | Reference, metrics |
| **Reports** | 180 days | `.codex/campaign_artifacts/post_campaign/` | Historical record |
| **Audit Trail** | 365 days | `.codex/campaign_artifacts/post_campaign/CAMPAIGN_AUDIT_TRAIL.md` | Legal/compliance |

---

## Artifact Management

### Before Campaign (Pre-Execution)
- [ ] Create campaign artifacts directory structure (automation)
- [ ] Initialize status tracker JSON files
- [ ] Prepare approval form templates
- [ ] Configure monitoring log collection

### During Campaign (Execution)
- [ ] Continuously update status trackers (hourly)
- [ ] Collect deployment logs to appropriate directories
- [ ] Record escalations and decisions in real-time
- [ ] Archive approval form signatures

### After Campaign (Post-Execution)
- [ ] Finalize all status trackers
- [ ] Generate completion report
- [ ] Conduct lessons learned session
- [ ] Create comprehensive audit trail
- [ ] Archive all artifacts
- [ ] Verify retention compliance

---

## Access Control

| Group | Access Level | Purpose |
|---|---|---|
| **Campaign Lead** | Full access | Campaign oversight, approvals |
| **Track Leads** | Read-only | Status monitoring |
| **Engineering Team** | Read-only | Reference material |
| **Compliance** | Full access (90+ days) | Audit trail verification |
| **Archive** | Archive-only | Long-term retention |

---

## Integration Points

1. **CampaignOrchestrator**: Auto-archives artifacts from agent execution
2. **GitHub Actions**: Workflow logs automatically collected to `production_logs/`
3. **Monitoring System**: Metrics exported to `*_metrics.json` files
4. **Approval Forms**: Electronic signatures captured in `.codex/PHASE_*_APPROVAL.md`

---

## Example Artifact Lifecycle

```
Canary Deployment (Day 2)
└─> canary_logs/error_logs.txt created
    ↓
    (monitored continuously for 2-4 hours)
    ↓
Gate 2 Decision (Day 2, 22:00 UTC)
└─> PHASE_9_GATE_2_CANARY_APPROVAL.md signed
    ↓
    (stored in .codex/ - not campaign_artifacts)
    ↓
End of Campaign (Day 12)
└─> Post-Campaign Processing
    ├─ canary_logs/ → Archive (30 days retention)
    ├─ Approval forms → Campaign_artifacts/post_campaign/ (90 days)
    └─ Audit trail → Permanent archive (365 days)
```

---

## Cleanup Schedule

**Every 30 days (Canary/Regional logs):**
```bash
find .codex/campaign_artifacts/canary_logs/ -type f -mtime +30 -delete
find .codex/campaign_artifacts/regional_logs/ -type f -mtime +30 -delete
```

**Every 90 days (Status trackers, standard artifacts):**
```bash
find .codex/campaign_artifacts/post_campaign/ -name "*STATUS_TRACKER*" -mtime +90 -delete
```

**Every 365 days (Audit trail review):**
- Manual review by compliance team
- Determine if extended retention needed
- Archive to long-term storage if required

---

## Questions?

For artifact management questions, contact: @mbaetiong (Campaign Lead)
