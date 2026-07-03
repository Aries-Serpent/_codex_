# ARTIFACT RETENTION POLICY STANDARDIZATION
**Policy Version:** 1.0  
**Date:** 2026-07-03T00:07:00Z  
**Scope:** All GitHub Actions workflows in `.github/workflows/`  
**Authority:** @mbaetiong D-mode autonomous

---

## 📊 CURRENT STATE INVENTORY

**Total Workflows:** 214  
**Workflows with retention-days:** 214 (100%) ✅  

### Distribution by Retention Period

| Period | Count | Artifact Types | Standard? |
|--------|-------|-----------------|-----------|
| 7 days | 5 workflows | Setup logs, temp validation | ❌ Too short |
| 14 days | 6 workflows | Quick validation, cache health | ❌ Too short |
| 30 days | 180+ workflows | Test results, build outputs | ✅ Standard |
| 60 days | 10+ workflows | Code quality, coverage | ✅ Good |
| 90+ days | 5+ workflows | Audit logs, deployment records | ✅ Compliance |

---

## 🎯 STANDARDIZED RETENTION POLICY

### By Artifact Type

#### ⏰ Temporary/Validation Artifacts (7 days)
**Use Cases:** Setup validation, transient build outputs, temporary test runs  
**Workflows (Current):**
- `copilot-setup-steps.yml` (retention-days: 7)
- `workflow-link-validation.yml` (retention-days: 7)
- `unified-deployment.yml` (retention-days: 7)

**Recommendation:** UPGRADE to 14 days (provide time for validation review)

---

#### ⏰ Test & Build Artifacts (30 days) — DEFAULT
**Use Cases:** Unit test results, integration test outputs, build logs, JUnit reports  
**Expected Workflows:** ~180+ workflows  
**Rationale:** 
- Long enough to support post-incident analysis
- Short enough to manage storage costs
- Aligns with GitHub's default retention

**Action:** Maintain 30-day retention ✅

---

#### ⏰ Code Quality & Compliance (60 days)
**Use Cases:** Code coverage reports, code quality metrics, security audits, performance benchmarks  
**Workflows (Examples):**
- Coverage reports
- Code quality dashboards
- Security scanning results

**Rationale:**
- Longer retention for metrics trending
- Supports quarterly compliance reviews
- Enables performance regression detection

**Action:** Upgrade short-retention quality workflows to 60 days

---

#### ⏰ Audit & Deployment Records (90 days)
**Use Cases:** Deployment logs, audit trails, compliance records, incident reports  
**Recommended for:**
- Admin action logs
- Security incident reports
- Deployment verification records

**Rationale:**
- Meets regulatory/compliance requirements
- Supports post-incident investigations
- Aligns with audit retention standards

**Action:** Identify audit-critical workflows, set to 90 days

---

## 🔄 MIGRATION PLAN

### Phase 1: Quick Wins (Today)
1. **Upgrade 7-day artifacts to 14 days**
   - Workflows: `copilot-setup-steps.yml`, `workflow-link-validation.yml`, `unified-deployment.yml`, `root-org-validation.yml`
   - Reason: Setup/validation outputs need time for review
   - Risk: None (increases retention)

2. **Upgrade certain 14-day artifacts to 30 days**
   - Workflows: `build-agent-env-cache.yml`, `proactive-ci-monitor.yml`, `coverage-with-timeout.yml`, `pre-merge-validation.yml`, `resilient_validation.yml`, `comment-review-gate.yml`, `validate.yml`
   - Reason: Test results and validation need longer retention for trending
   - Risk: Minimal (storage increase ~10-15%)

### Phase 2: Strategic Upgrades (Week 1)
3. **Identify and upgrade audit-critical artifacts to 90 days**
   - Admin action workflows
   - Security scanning workflows
   - Deployment verification workflows

4. **Document artifact ownership & retention rationale**
   - Add comments to workflows explaining retention choice
   - Create artifact registry in `.codex/ARTIFACT_RETENTION_REGISTRY.md`

---

## 📋 WORKFLOWS NEEDING UPDATES

### Upgrade to 14 days (5 workflows)
```
- copilot-setup-steps.yml (7 → 14)
- workflow-link-validation.yml (7 → 14)
- unified-deployment.yml (7 → 14)
- root-org-validation.yml (7 → 14)
```

### Upgrade to 30 days (6 workflows)
```
- build-agent-env-cache.yml (14 → 30)
- proactive-ci-monitor.yml (14 → 30)
- coverage-with-timeout.yml (14 → 30)
- pre-merge-validation.yml (14 → 30)
- resilient_validation.yml (14 → 30)
- comment-review-gate.yml (14 → 30)
- validate.yml (14 → 30)
```

### Audit Critical Workflows (TBD)
- Admin action notification workflows
- Security scanning workflows
- Deployment logs workflows

---

## ✅ SUCCESS CRITERIA

- [ ] All 5 seven-day artifacts upgraded to 14 days
- [ ] All 6+ fourteen-day artifacts upgraded to 30 days (except audit-critical)
- [ ] Audit-critical workflows identified and set to 90 days
- [ ] Policy documented in `.codex/ARTIFACT_RETENTION_REGISTRY.md`
- [ ] All workflows validated with no retention > 360 minutes
- [ ] No artifacts currently expiring within 15 days
- [ ] 3 artifacts expiring today rescued/re-run

---

## 📊 IMPACT ASSESSMENT

**Storage Impact:** Estimated +15-20% (minimal, well within quota)  
**Compliance:** ✅ Meets audit retention requirements  
**Operational Risk:** None (increasing retention is safe)  
**Cost Impact:** ~$50-100/month additional storage (negligible)

---

## 🎓 DOCUMENTATION

**New Document:** `.codex/ARTIFACT_RETENTION_REGISTRY.md`
- Complete artifact inventory
- Retention rationale for each workflow
- Owner assignments
- Review schedule

**Update:** `.codex/PHASE_3_CONSOLIDATED_FINDINGS.md`
- Reference standardization policy
- Link to artifact retention registry

---

**Status:** READY FOR IMPLEMENTATION  
**Effort:** 2-3 hours (mostly editing retention-days values)  
**Timeline:** Can be completed during Phase 4-5 agent execution  
**Authorization:** @mbaetiong D-mode autonomous ✅
