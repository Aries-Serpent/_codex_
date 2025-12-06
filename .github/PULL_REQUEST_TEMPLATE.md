---
name: Pull Request
about: Submit changes to the Codex ML repository
title: ''
labels: ''
assignees: ''

---

# Pull Request Template

> **Version:** 2.0.0  
> **Generated:** $(date +%Y-%m-%d)  
> **System Status:** 71/71 Azure MLOps Capabilities (100%) ✅

---

## ⚠️ REQUIRED Safety Confirmations

- [ ] **Network Safety Acknowledgment** (`NETWORK_SAFETY_ACK`) - No unauthorized network operations
- [ ] **Offline Mode Confirmation** (`OFFLINE_MODE_CONFIRM`) - Respects offline-first design
- [ ] **Security Review** - No secrets or credentials in code
- [ ] **Backward Compatibility** - No breaking changes without migration path

---

## 📋 Change Summary

### Type of Change
- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to change)
- [ ] 📝 Documentation update
- [ ] 🏗️ Infrastructure change (K8s, CI/CD, deployment)
- [ ] 🔒 Security fix
- [ ] ⚡ Performance improvement
- [ ] ♻️ Refactoring (no functional changes)

### Scope

| Field | Value |
|-------|-------|
| **Component(s)** | (e.g., Feature Store, Events, K8s, Training, etc.) |
| **Impact Level** | (Low/Medium/High) |
| **Azure MLOps Rows** | (e.g., Rows 14-16, Row 27, etc.) |

### Description

<!-- Provide a clear and concise description of what this PR does -->

**What changed:**


**Why this change:**


**Related issues/PRs:**


---

## 🏗️ Infrastructure Impact

### Kubernetes Changes
- [ ] Modified K8s manifests (`manifests/k8s/`)
- [ ] Updated deployment script (`scripts/k8s_deploy.sh`)
- [ ] Changed resource limits or HPA configuration
- [ ] Added new services or endpoints

**If yes, describe changes:**


### Feature Store Changes
- [ ] Modified feature store core (`src/codex_ml/features/`)
- [ ] Added new features or feature groups
- [ ] Updated feature health monitoring
- [ ] Changed CLI commands

**If yes, describe changes:**


### Event System Changes
- [ ] Modified event base classes (`src/codex_ml/events/base.py`)
- [ ] Updated Azure Event Grid integration
- [ ] Updated AWS EventBridge integration
- [ ] Added new event types

**If yes, describe changes:**


### Monitoring & Observability Changes
- [ ] Modified health probes
- [ ] Updated Prometheus metrics
- [ ] Changed feature freshness monitoring
- [ ] Added new monitoring endpoints

**If yes, describe changes:**


---

## ✅ Testing & Verification

### Pre-Submission Checklist
- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] Linting passes (`ruff check .` and `black --check .`)
- [ ] Type checking passes (`mypy src/ --config-file pyproject.toml`)
- [ ] Pre-commit hooks pass (`pre-commit run --all-files`)
- [ ] Security scans clean (`./maintenance.sh security`)

### Test Coverage
- [ ] Added tests for new functionality
- [ ] Updated existing tests as needed
- [ ] Test coverage maintained or improved (target: >70%)
- [ ] All tests pass (100% pass rate required)

**Test Results:**
```bash
# Paste pytest output here
```

### Verification Commands Run

```bash
# Core functionality
python3 -c "import codex_ml; print('✓ Import successful')"

# Feature store (if applicable)
codex-ml features list-features

# K8s validation (if applicable)
kubectl apply --dry-run=client -k manifests/k8s/base

# Health check (if applicable)
./maintenance.sh health

# Full verification (recommended)
./maintenance.sh all
```

---

## 📚 Documentation

### Documentation Updates
- [ ] Updated README.md
- [ ] Updated AGENTS.md
- [ ] Updated relevant docs in `docs/`
- [ ] Updated API documentation (if applicable)
- [ ] Added/updated code comments and docstrings
- [ ] Updated CHANGELOG.md

### New Documentation Created
- [ ] Implementation guide
- [ ] User guide
- [ ] API reference
- [ ] Architecture diagram
- [ ] Runbook or operational guide

**Documentation locations:**


---

## 🔒 Security

### Security Checklist
- [ ] No secrets or credentials in code
- [ ] No hardcoded passwords or API keys
- [ ] Secrets use environment variables or secret management
- [ ] Input validation implemented where needed
- [ ] No SQL injection vulnerabilities
- [ ] No command injection vulnerabilities
- [ ] Dependencies scanned for CVEs (`pip-audit --desc`)

### Security Scan Results

```bash
# Bandit (SAST)
bandit -r src/ training/ cli/ -ll

# pip-audit (CVE scan)
pip-audit --desc

# detect-secrets (credential leak detection)
detect-secrets scan --baseline .secrets.baseline
```

**Results:** (Clean/Issues Found - describe any issues)


---

## 🎯 Azure MLOps Capability Impact

### Capability Changes

**Before this PR:**
- Current capability score: X/71

**After this PR:**
- New capability score: Y/71
- Capabilities added/improved: (list rows)

### Capability Verification

- [ ] Capability assessment updated (if applicable)
- [ ] New capabilities documented with evidence
- [ ] Comparison rating updated (if score changed)
- [ ] No regression in existing capabilities

**Updated files:**
- [ ] `.github/prompts/followup_execution_plan/AZURE_MLOPS_CAPABILITY_ASSESSMENT.md`
- [ ] `.github/prompts/followup_execution_plan/COMPARISON_RATING.md`

---

## 🚀 Deployment

### Deployment Impact
- [ ] Requires database migration
- [ ] Requires configuration changes
- [ ] Requires environment variable updates
- [ ] Requires K8s redeployment
- [ ] Requires service restart
- [ ] Zero downtime deployment possible

### Deployment Steps

1. 
2. 
3. 

### Rollback Plan

<!-- Describe how to rollback if issues arise -->


---

## 📊 Performance Impact

### Performance Considerations
- [ ] Performance tested
- [ ] No significant performance degradation
- [ ] Benchmarks included (if applicable)
- [ ] Resource usage documented

**Performance metrics:**


---

## ♻️ Backward Compatibility

### Compatibility Checklist
- [ ] Backward compatible with previous version
- [ ] Migration path provided (if breaking change)
- [ ] Deprecation warnings added (if applicable)
- [ ] Legacy shims maintained (if needed)

### Migration Guide

<!-- If breaking change, provide migration steps -->


---

## 👥 Review Checklist

### For Reviewers
- [ ] Code follows repository style guidelines
- [ ] Changes are well-documented
- [ ] Tests are comprehensive and pass
- [ ] No unnecessary complexity
- [ ] Security considerations addressed
- [ ] Performance impact acceptable
- [ ] Documentation is clear and complete

### Review Focus Areas

<!-- Highlight specific areas that need careful review -->


---

## 📝 Additional Notes

### Known Issues

<!-- List any known issues or limitations -->


### Future Work

<!-- List any follow-up work needed -->


### Dependencies

<!-- List any dependency changes or requirements -->


---

## 🔗 References

### Related Documents
- [ ] Implementation: `docs/IMPLEMENTATION_COMPLETE.md`
- [ ] Assessment: `.github/prompts/followup_execution_plan/AZURE_MLOPS_CAPABILITY_ASSESSMENT.md`
- [ ] Agent Guide: `AGENTS.md`
- [ ] ChatGPT Guide: `docs/CHATGPT_ASSISTANT_GUIDE.md`

### External References
- [ ] Azure MLOps Maturity Model
- [ ] Related Issues: #
- [ ] Related PRs: #
- [ ] Documentation: (links)

---

## ✍️ Commit Information

### Commit Quality
- [ ] Commits are atomic and well-described
- [ ] Commit messages follow conventional commits format
- [ ] Co-authors properly attributed

### Commit Summary

**Number of commits:** 
**Lines added:** 
**Lines removed:** 
**Files changed:** 

---

## 🏆 Status Validation

### System Health Post-Change
```bash
# Run maintenance check
./maintenance.sh health

# Verify capabilities
grep -c "✅ Met" .github/prompts/followup_execution_plan/AZURE_MLOPS_CAPABILITY_ASSESSMENT.md
# Expected: 71

# Check feature store
codex-ml features check-health

# Verify K8s manifests
kubectl apply --dry-run=client -k manifests/k8s/base
```

**Current Status:** 71/71 Azure MLOps Capabilities (100%) ✅

---

## 📋 Final Checklist

- [ ] All required sections completed
- [ ] All checkboxes reviewed
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Security verified
- [ ] Ready for review

---

**PR Author:** @
**Date Submitted:** $(date +%Y-%m-%d)
**Target Branch:** main
**Source Branch:** 

<!-- 
Thank you for contributing to Codex ML!
Please ensure all sections are completed before requesting review.
-->
