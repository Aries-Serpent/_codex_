# Owner Approval Validation — 24h Duration Window
> Generated: 2025-10-20 19:43:52 UTC | Author: mbaetiong

This runbook verifies the OWNER approval window for cost-incurring workflows with a 24h duration. CI workflows remain disabled by policy; validation runs locally.

Summary
| Mode | Command | Expected |
|---|---|---|
| File-based (24h) | make owner-approve-24h && bash scripts/ci/owner_approval_test.sh docker-build-push | RESULT: APPROVED |
| Env var (24h) | OWNER_APPROVED_DURATION=24h bash scripts/ci/owner_approval_test.sh docker-build-push | RESULT: APPROVED |
| Expired (file) | Edit .github/OWNER_APPROVAL.yml created_at to >24h past, rerun test | RESULT: DENIED |
| Wrong tool key | TOOL_KEY=security-scans with file only listing docker-build-push | RESULT: DENIED |
| Push (guarded) | bash scripts/ci/push_image.sh ghcr.io/OWNER/REPO:tag --dry-run | Requires APPROVED; otherwise denied |

Steps
1) File-based 24h window
```bash
make owner-approve-24h
bash scripts/ci/owner_approval_test.sh docker-build-push
```text
2) Expiry simulation
- Edit .github/OWNER_APPROVAL.yml and set created_at 25h in the past:
  created_at: "2025-10-19T18:00:00Z"
- Rerun:
```bash
bash scripts/ci/owner_approval_test.sh docker-build-push
```text
3) Environment variable mode (no commit)
```bash
OWNER_APPROVED_DURATION=24h bash scripts/ci/owner_approval_test.sh docker-build-push
# Alternatively (until timestamp):
OWNER_APPROVED_UNTIL="2025-10-21T19:43:52Z" bash scripts/ci/owner_approval_test.sh docker-build-push
```text
4) Push (guarded)
```bash
# Expect APPROVED within window:
bash scripts/ci/push_image.sh ghcr.io/OWNER/REPO:tag --dry-run
# After clearing approval:
make owner-approve-clear
# Expect denial:
bash scripts/ci/push_image.sh ghcr.io/OWNER/REPO:tag --dry-run || echo "Denied as expected"
```text

Notes
- The guard supports both bullet lists and inline lists for cost_workflows.
- Comments and quotes in YAML scalars are ignored by the parser.
- When enabling CI later, the disabled workflow already calls the guard at the start of build and push jobs.
- Decisions are recorded in .codex/evidence/owner_approval.jsonl for auditability.
