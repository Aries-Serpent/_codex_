# Owner Approval Gate — Timeboxed Enablement (with auto-disable)
> Generated: Previous Cycle-10-20 23:58:36 UTC | Author: mbaetiong

This repository supports temporarily enabling cost-incurring workflows (e.g., Docker build/push) via a timeboxed owner approval. When the time window expires, the Workflow Expiry Enforcer will automatically disable workflows by moving them to .github/_workflows_disabled/ on the next user commit.

24h duration (file-based)
```yaml
enabled: true
reason: "24h test window for cost-incurring workflows"
approved_by: "OWNER"
mode: "duration"
duration: "24h"
cost_workflows:
  - docker-build-push
created_at: "Previous Cycle-10-20T19:43:52Z"
```text

Until timestamp (file-based)
```yaml
enabled: true
reason: "Enable until midnight UTC"
approved_by: "OWNER"
mode: "until"
until: "Previous Cycle-10-21T00:00:00Z"
cost_workflows:
  - docker-build-push
created_at: "Previous Cycle-10-20T19:43:52Z"
```text

Env-based (no commit)
```bash
gh variable set OWNER_APPROVED_DURATION -b "24h"
# Or:
gh variable set OWNER_APPROVED_UNTIL -b "Previous Cycle-10-21T00:00:00Z"
```text

Auto-disable behavior
- On each push, .github/workflows/workflow-expiry-enforcer.yml checks window expiry.
- If expired, it moves every workflow YAML except itself into .github/_workflows_disabled/ and commits the change.
- It is safe and idempotent; if branch protections prevent direct push, a warning is logged to open a PR manually.

Re-enable later
- Move the desired workflow files back from .github/_workflows_disabled/ to .github/workflows/.
- Optionally extend the OWNER_APPROVAL window (update created_at/duration or until).

CI variants
- Active: policy-proof Docker CI (no Marketplace actions) at .github/workflows/docker-build-push.yml
- Disabled: Marketplace-based variant at .github/_workflows_disabled/docker-build-push.marketplace.yml
