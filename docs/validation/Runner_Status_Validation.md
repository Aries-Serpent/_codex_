# [Validation]: Runner status — org/repo inventory and CI routing
> Generated: 2025-10-21 01:16:59 UTC | Author: mbaetiong

Scenarios
1) List org and repo runners
```bash
# Org scope
make runner-status ORG=Aries-Serpent
# Repo scope
make runner-status OWNER=Aries-Serpent REPO=_codex_
```text
Expect:
- Table shows ID, NAME, BUSY/IDLE, ONLINE/OFFLINE, LABELS for each runner.
- Non-zero exit only on usage errors; network/API errors return raw JSON.

2) Route CI to self-hosted runner
```bash
make runner-vars OWNER=Aries-Serpent REPO=_codex_ RUNS_ON='["self-hosted","linux"]'
```text
Expect:
- RUNS_ON upserted; subsequent CI jobs route to self-hosted.
- Evidence appended to .codex/evidence/runner_ops.jsonl

3) Timeboxed approval window
```bash
make runner-vars OWNER=Aries-Serpent REPO=_codex_ APPROVAL_DURATION=24h
# or
make runner-vars OWNER=Aries-Serpent REPO=_codex_ APPROVAL_UNTIL=2025-10-21T00:00:00Z
```text
Expect:
- OWNER_APPROVED_* upserted (mutually exclusive); CI guard honors window.

4) Multi-arch enablement
```bash
# On runner host (privileged Docker)
make runner-binfmt
# In repo vars:
make runner-vars OWNER=Aries-Serpent REPO=_codex_ PUSH_PLATFORMS="linux/amd64,linux/arm64"
```text
Expect:
- Binfmt installed; subsequent CI (with PUSH_PLATFORMS set) builds multi-arch images.

Troubleshooting
- 401/403 from API: confirm GH_PAT or _CODEX_BOT_RUNNER environment is set and has repo/org admin + actions variables permissions (the upgraded token does).
- Still queued: ensure a runner with labels self-hosted,linux is online; verify RUNS_ON value.
- GHCR push denied: repo Actions → Workflow permissions must allow read/write; packages: write enabled org/repo wide.
