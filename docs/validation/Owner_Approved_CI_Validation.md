# Owner-Approved CI Validation — Docker Build/Push
> Generated: 2025-10-20 20:50:36 UTC | Author: mbaetiong

Goal
- Validate the OWNER-approved Docker workflow in CI with a 24h window and optional multi-arch.

Pre-checks
- Actions permissions allow packages: write
- Runner has Docker Buildx; QEMU will be set up automatically when needed
- No extra secrets required; GHCR login uses GITHUB_TOKEN

Paths to approval
1) Repo variables
- Set OWNER_APPROVED_DURATION="24h" (or OWNER_APPROVED_UNTIL="…Z") in repo variables.
- Trigger the workflow (push to main, PR to main, or manual dispatch without inputs).

2) Per-run overrides (no repo var changes)
- Manually dispatch workflow with:
  - approval_duration="24h"
  - approval_until="" (leave empty) OR provide a future ISO8601 Z
  - push_platforms="linux/amd64,linux/arm64" (optional)

3) Check-only (no build or push)
- Manually dispatch workflow with:
  - check_only=true
  - approval_duration="24h" (or approval_until="…Z")
- Expectation: approval-check job runs and posts the status to the run summary; build and push jobs are skipped.

Expected results
- approval-check:
  - Shows approval context and status
  - Passes guard when within window
  - Writes decision to the Job summary and uploads owner_approval.jsonl
- build-and-smoke job (when not check-only):
  - Passes guard when within window
  - Builds and smokes image
- push job (main only, when not check-only):
  - Logs into GHCR with GITHUB_TOKEN
  - Uses lowercase image refs
  - Honors push_platforms when provided
  - Pushes tags sha-<12> and latest/branch

Artifacts
- owner-approval-evidence-*: .codex/evidence/owner_approval.jsonl (approve/deny decisions)
- container-smoke-logs: smoke logs
- docker-security-artifacts (optional): SBOM/scan outputs

Troubleshooting
- Guard denies with “enabled=false” or “expired”:
  - For file mode: refresh created_at or set duration accordingly
  - For env mode: ensure inputs/vars are non-empty and valid
- Multi-arch fails: confirm QEMU step executed (push_platforms not empty), and the builder supports emulation
- GHCR rejects tag: ensure repository path and branch tag are lowercased (the workflow now forces lowercase)
