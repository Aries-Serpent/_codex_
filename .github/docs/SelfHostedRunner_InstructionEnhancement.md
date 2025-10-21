# [Plan]: Self-hosted runner — Codex session quick-guide (GH_PAT/_CODEX_BOT_RUNNER)
> Generated: 2025-10-21 01:16:59 UTC | Author: mbaetiong

Goal
- Provide “muscle memory” commands Codex can run during active sessions to manage the self-hosted runner and CI toggles without introducing new variable names.

Prereqs (no new variables)
- Export GH_PAT in your shell OR ensure _CODEX_BOT_RUNNER is available in env.
- Keep existing repo variable names only: RUNS_ON, OWNER_APPROVED_DURATION/UNTIL, PUSH_PLATFORMS.

Cheat sheet
- Status (org + repo):
```bash
make runner-status ORG=Aries-Serpent
make runner-status OWNER=Aries-Serpent REPO=_codex_
```

- Configure variables (no new names):
```bash
# Dynamic runner target and approval window
make runner-vars OWNER=Aries-Serpent REPO=_codex_ RUNS_ON='["self-hosted","linux"]' APPROVAL_DURATION=24h
# OR absolute deadline
make runner-vars OWNER=Aries-Serpent REPO=_codex_ APPROVAL_UNTIL=2025-10-21T00:00:00Z
# Optional multi-arch
make runner-vars OWNER=Aries-Serpent REPO=_codex_ PUSH_PLATFORMS="linux/amd64,linux/arm64"
```

- Bootstrap/remove runner (service mode):
```bash
# On the runner host
sudo bash scripts/runner/install_docker.sh <runner_user>
sudo -u <runner_user> make runner-bootstrap URL=https://github.com/Aries-Serpent/_codex_ LABELS="self-hosted,linux,docker" SVC=systemd
# Deregister and clean
sudo -u <runner_user> make runner-remove URL=https://github.com/Aries-Serpent/_codex_
```

- Diagnostics workflow (GitHub UI)
  - Run “Runner diagnostics — self-hosted readiness” via Actions → Run workflow.
  - Confirms Docker/buildx/binfmt (best-effort) and displays the current RUNS_ON routing.

Evidence
- All runner ops using scripts write JSONL entries to .codex/evidence/runner_ops.jsonl:
  - Actions: runner_bootstrap, runner_remove, configure_repo_vars
  - Include URLs, labels, versions, and changed variable names.
