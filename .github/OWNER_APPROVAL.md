# Owner Approval Gate — Timeboxed Enablement
> Generated: 2025-10-20 18:34:03 UTC | Author: mbaetiong

This repository supports temporarily enabling cost-incurring workflows (e.g., Docker build/push) via a timeboxed owner approval.

## Methods
- Repository variables (no commit):
  - OWNER_APPROVED_UNTIL="2025-10-21T04:00:00Z"
  - OWNER_APPROVED_DURATION="4h" (supports s/m/h/d/w)
- File-based approval (commit):
  - .github/OWNER_APPROVAL.yml with:
    - enabled: true
    - mode: "duration" and duration: "4h" with a valid created_at (ISO), OR
    - mode: "until" and until: "2025-10-21T04:00:00Z"
    - cost_workflows: ["all"] or specific keys like ["docker-build-push"]

The workflow calls scripts/ci/owner_approval_guard.sh and fails fast if the window is not active.

## Examples
Repository variable (no commit):
```bash
gh variable set OWNER_APPROVED_DURATION -b "8h"
```
File (commit):
```yaml
enabled: true
mode: "until"
until: "2025-10-21T04:00:00Z"
cost_workflows: ["all"]
created_at: "2025-10-20T16:00:00Z"
```
