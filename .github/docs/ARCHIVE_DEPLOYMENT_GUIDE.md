# Archive Improvements Deployment Guide
> Generated: 2025-10-17 13:22:36 | Author: mbaetiong

## Pre-Deployment Checklist
### Code Review
- [ ] All 6 improvement modules reviewed (config, logging, retry, batch, perf, cli)
- [ ] Tests passing: `pytest tests/archive/test_*.py -q`
- [ ] Coverage 87% on new modules: `pytest --cov=codex.archive --cov-report=term-missing`
- [ ] Pre-commit clean: `pre-commit run --all-files`

### Backward Compatibility
- [ ] Existing env vars still work (backward compatible)
- [ ] Single restore unchanged (no performance penalty)
- [ ] Evidence logs still recorded (new fields added, old ones preserved)
- [ ] No breaking API changes to existing services

### Documentation
- [ ] Config guide updated (`.github/docs/ARCHIVE_CONFIG_ADR.md`)
- [ ] Usage guide updated (`.github/docs/ARCHIVE_IMPROVEMENTS_USAGE.md`)
- [ ] CLI help text updated (`codex archive --help`)
- [ ] Team trained on new features

---

## Deployment Steps
### Phase 1: Staging Deployment (Day 1)
1. **Create staging branch**
```bash
git checkout -b deploy/archive-improvements
git merge origin/main
```
2. **Run full test suite**
```bash
pytest tests/archive/ -q --maxfail=1
coverage report --skip-covered
```
3. **Deploy to staging environment**
```bash
make build-staging
make deploy-staging ENVIRONMENT=staging
```
4. **Smoke tests on staging**
```bash
codex archive config-show
codex archive health-check
codex archive batch-restore small_manifest.json --by staging_user
tail .codex/evidence/archive_ops.jsonl
```

### Phase 2: Production Deployment (Day 2-3)
1. **Create production PR**
```bash
git push origin deploy/archive-improvements
```
2. **Production canary (5% of users)**
```bash
make deploy-prod ENVIRONMENT=prod CANARY=true CANARY_PERCENT=5
```
3. **Monitor metrics**
```bash
curl https://metrics.example.com/archive?period=1h
grep "FAIL" .codex/evidence/archive_ops.jsonl
```
4. **Full production rollout (Day 3)**
```bash
make deploy-prod ENVIRONMENT=prod
```

---

## Rollback Plan
If issues detected:
### Quick Rollback
```bash
git revert HEAD
make deploy-prod ENVIRONMENT=prod
```
### Feature Flags
```bash
export CODEX_ARCHIVE_RETRY_ENABLED=false
export CODEX_ARCHIVE_CONFIG_DISABLED=true
export CODEX_ARCHIVE_BATCH_CONCURRENT=1
export CODEX_ARCHIVE_PERF_ENABLED=false
```

### Rollback Validation
```bash
codex archive restore <tombstone> output.txt --by user
```
Ensure evidence logs show no new event types:
```bash
grep "BATCH_RESTORE" .codex/evidence/archive_ops.jsonl
```

---

## Post-Deployment Validation
### Day 1 (Production)
- [ ] No increase in error rates (< 0.1%)
- [ ] Restore latency unchanged (p99 < 500ms)
- [ ] Evidence logs being written correctly
- [ ] New CLI commands accessible
- [ ] No database migration issues

### Day 2-3 (Monitoring)
- [ ] Batch operations being used (check manifests)
- [ ] Retry logic triggering appropriately (check events)
- [ ] Config files being adopted (check `.codex/archive.toml` files)
- [ ] Performance metrics being collected

### Week 1 (Stability)
- [ ] No unexpected errors in logs
- [ ] Restore latency stable or improved
- [ ] User adoption of new features
- [ ] No production incidents related to changes

---

## Configuration Migration Guide
### For Existing Deployments
**Option 1: Keep Current Setup** (no action needed)
```bash
export CODEX_ARCHIVE_BACKEND=sqlite
export CODEX_ARCHIVE_URL=sqlite:///./.codex/archive.sqlite
```

**Option 2: Adopt Config Files** (recommended)
```bash
mkdir -p .codex
cat > .codex/archive.toml <<'EOF'
[backend]
type = "sqlite"
url = "sqlite:///./.codex/archive.sqlite"
[retry]
enabled = true
max_attempts = 3
[batch]
max_concurrent = 5
EOF
codex archive config-show
unset CODEX_ARCHIVE_BACKEND CODEX_ARCHIVE_URL
```

---

## Monitoring & Alerts
### Key Metrics
| Metric | Threshold | Action |
|--------|-----------|--------|
| Restore Error Rate | > 1% | Page on-call |
| Restore Latency (p99) | > 1s | Investigate database |
| Retry Count (per day) | > 100 | Review transient errors |
| Batch Operations | < 1 | Ensure adoption |
| Config File Usage | > 50% | Confirm migration |

### Log Queries
```bash
grep "RESTORE_FAIL" .codex/evidence/archive_ops.jsonl | tail -20
jq '.duration_ms' .codex/evidence/archive_ops.jsonl | sort -n | tail -20
```

---

## Success Criteria Checklist
- [ ] All tests passing in production
- [ ] Config system working (file + env var precedence)
- [ ] Structured logging enabled (JSON format)
- [ ] Retry logic handling transient errors
- [ ] Batch operations processing manifests
- [ ] Performance metrics recorded in evidence
- [ ] Multi-backend support validated
- [ ] Documentation complete and accurate
- [ ] Team trained and confident
- [ ] No regressions in existing functionality
