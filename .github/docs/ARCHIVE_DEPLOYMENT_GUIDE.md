# Archive Improvements Deployment Guide
> Generated: 2024-05-29 | Author: mbaetiong

---

## Pre-Deployment Checklist
- [ ] Code reviewed (config, logging, retry, batch, perf, CLI).
- [ ] Tests green: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/archive -q`.
- [ ] Optional: `pytest --cov=codex.archive --cov-report=term-missing`.
- [ ] Docs reviewed: `ARCHIVE_CONFIG_ADR`, `ARCHIVE_IMPROVEMENTS_USAGE`.

---

## Deployment Steps
### 1. Staging
```bash
git checkout -b deploy/archive-improvements
nox -s tests  # or pytest -q
make build-staging
make deploy-staging ENVIRONMENT=staging
```

Validate on staging:
```bash
codex archive config-show
codex archive health-check
codex archive batch-restore fixtures/dr_manifest.json --by staging-user --continue-on-error
```

### 2. Production (Canary)
```bash
git push origin deploy/archive-improvements
# Open PR, obtain approvals
make deploy-prod ENVIRONMENT=prod CANARY=true CANARY_PERCENT=5
```

Monitor:
```bash
codex archive health-check --debug
jq 'select(.action=="RESTORE_FAIL")' .codex/evidence/archive_ops.jsonl | tail -20
```

### 3. Production (Full)
```bash
make deploy-prod ENVIRONMENT=prod
```

---

## Rollback Plan
1. Re-deploy previous tag/commit: `make deploy-prod ENVIRONMENT=prod VERSION=<previous>`.
2. Disable new features temporarily:
   ```bash
   export CODEX_ARCHIVE_RETRY_ENABLED=false
   export CODEX_ARCHIVE_BATCH_CONCURRENT=1
   export CODEX_ARCHIVE_PERF_ENABLED=false
   ```
3. Re-run health check and smoke restores.

---

## Post-Deployment Validation
- [ ] Error rate < 1% for restore operations.
- [ ] `codex archive batch-restore` tested with production manifest.
- [ ] Evidence logs contain `BATCH_RESTORE_COMPLETE` events.
- [ ] Restore latency (p95) within target (< 500 ms).
- [ ] Team notified of new CLI commands (`config-show`, `batch-restore`).

---

## Monitoring Tips
```bash
# Count restore failures
grep 'RESTORE_FAIL' .codex/evidence/archive_ops.jsonl | wc -l

# Review recent batch summaries
tail -20 batch_restore_*.json

# Average restore duration (ms)
jq '.duration_ms' .codex/evidence/archive_ops.jsonl | jq -s 'add/length'
```

---

## Support
For production incidents contact `#codex-archive` or page the archive on-call engineer.
