# Owner Approval Gate — Timeboxed Enablement
> Generated: 2025-10-20 19:43:52 UTC | Author: mbaetiong

This repository supports temporarily enabling cost-incurring workflows (e.g., Docker build/push) via a timeboxed owner approval.

24h duration (file-based)
```yaml
enabled: true
reason: "24h test window for cost-incurring workflows"
approved_by: "OWNER"
mode: "duration"
duration: "24h"
cost_workflows:
  - docker-build-push
created_at: "2025-10-20T19:43:52Z"
```

24h duration (repository variable; no commit)
```bash
gh variable set OWNER_APPROVED_DURATION -b "24h"
# Clear later:
gh variable delete OWNER_APPROVED_DURATION
```

Quick local test
```bash
# File mode
make owner-approve-24h
bash scripts/ci/owner_approval_test.sh docker-build-push

# Env var mode
OWNER_APPROVED_DURATION=24h bash scripts/ci/owner_approval_test.sh docker-build-push
```

Notes
- cost_workflows may be ["all"] or specific keys (e.g., "docker-build-push").
- The guard logs the computed expiry as an ISO timestamp for auditability.
- To disable: make owner-approve-clear or remove repo variables.
