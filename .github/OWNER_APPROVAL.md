# Owner Approval Gate — Timeboxed Enablement
> Generated: 2025-10-20 20:50:36 UTC | Author: mbaetiong

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

CI enablement (OWNER APPROVED)
- The workflow is enabled at .github/workflows/docker-build-push.yml and is hard-gated by scripts/ci/owner_approval_guard.sh.
- You can supply an approval window via:
  - Repo variables: OWNER_APPROVED_DURATION="24h" or OWNER_APPROVED_UNTIL="2025-10-21T00:00:00Z"
  - Per-run overrides: workflow_dispatch inputs approval_duration/approval_until
  - Validation only: workflow_dispatch input check_only=true (skips build and push)
- Multi-arch (optional): repo var or input push_platforms="linux/amd64,linux/arm64"
- Permissions: Actions “packages: write” must be allowed. GHCR uses the default GITHUB_TOKEN via docker/login-action.
- GHCR note: image repository and tags are lowercased automatically in CI.

Quick local test
```bash
# File mode
make owner-approve-24h
bash scripts/ci/owner_approval_test.sh docker-build-push
make owner-approve-status

# Env var mode
OWNER_APPROVED_DURATION=24h bash scripts/ci/owner_approval_test.sh docker-build-push
make owner-approve-status

# Extend window (refresh created_at)
make owner-approve-extend-24h
make owner-approve-status
```

Notes
- cost_workflows may be ["all"] or specific keys (e.g., "docker-build-push").
- The guard logs the computed expiry as an ISO timestamp for auditability and includes CI metadata in evidence.
- To disable: make owner-approve-clear or remove repo variables.
