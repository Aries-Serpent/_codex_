# Owner-Approved CI Validation — Docker Build/Push
> Generated: 2024-10-20 21:43:01 UTC | Author: mbaetiong

Goal
- Validate the OWNER-approved Docker workflow in CI with a 24h window and optional multi-arch, with concurrency and timeouts configured for safety.

Pre-checks
- Actions permissions allow packages: write (repo settings).
- Runner has Docker Buildx; QEMU will be set up automatically when needed.
- No extra secrets required; GHCR login uses GITHUB_TOKEN.

Paths to approval
1) Repo variables
- Set OWNER_APPROVED_DURATION="24h" (or OWNER_APPROVED_UNTIL="…Z") in repo variables.
- Trigger the workflow (push to main, PR to main, or manual dispatch without inputs).

2) Per-run overrides (no repo var changes)
- Manually dispatch workflow with:
  - approval_duration="24h"
  - approval_until="" (leave empty) OR provide a future ISO8601 Z
  - push_platforms="linux/amd64,linux/arm64" (optional)
  - check_only=true (optional for validation-only run)

Expected results
- approval-check:
  - Shows approval context and status
  - Passes guard when within window
  - Writes decision to the Job summary and uploads owner_approval.jsonl
  - Respects timeout-minutes (10m) and benefits from workflow-level permissions and concurrency guard
- build-and-smoke:
  - Passes guard when within window
  - Builds and smokes image (local load)
  - Applies OCI metadata labels (source, revision, ref.name)
  - Respects timeout-minutes (45m)
- push (main only):
  - Logs into GHCR with GITHUB_TOKEN
  - Uses lowercase image refs
  - Applies OCI metadata labels (source, revision, ref.name)
  - Pushes tags sha-<12> and latest/branch
  - Writes pushed tags to the GitHub Step Summary for auditability
  - Respects timeout-minutes (45m) and concurrency guard (docker-${{ github.ref }})

Operational safety
- Concurrency: docker-${{ github.ref }} cancels overlapping runs on the same ref to avoid registry conflicts.
- Timeouts: approval-check (10m); build-and-smoke (45m); push (45m).

Artifacts
- owner-approval-evidence-*: .codex/evidence/owner_approval.jsonl (approve/deny decisions)
- container-smoke-logs: smoke logs
- docker-security-artifacts (optional): SBOM/scan outputs

Troubleshooting
- Guard denies with “enabled=false” or “expired”:
  - File mode: refresh created_at or adjust duration
  - Env mode: ensure inputs/vars are set and valid
- Multi-arch fails: confirm QEMU step executed (push_platforms not empty), and the builder supports emulation
- GHCR rejects tag: ensure repository path and branch tag are lowercased (workflow enforces lowercase)
- Step summary missing tags: ensure push job ran (not skipped by check_only or PR event)
