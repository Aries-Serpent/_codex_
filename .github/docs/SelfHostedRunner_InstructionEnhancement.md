# [Plan]: Self-hosted runner — Codex session quick-guide (GH_PAT/_CODEX_BOT_RUNNER) — Ephemeral queue drain
> Generated: 2025-10-21 01:57:11 UTC | Author: mbaetiong

Goal
- Let Codex immediately pick up queued jobs using an ephemeral runner launched from the Active Codex environment (no new variable names).
- Continue to support persistent runners on dedicated hosts.

Prereqs (no new variables)
- Export GH_PAT in your shell OR ensure _CODEX_BOT_RUNNER is available in env.
- Keep existing repo variable names only: RUNS_ON, OWNER_APPROVED_DURATION/UNTIL, PUSH_PLATFORMS.

Quick reference
| Task | Command |
|---|---|
| Check runner inventory | make runner-status OWNER=Aries-Serpent REPO=_codex_ |
| Drain queued runs (ephemeral) | bash scripts/runner/drain_queue_ephemeral.sh --owner "Aries-Serpent" --repo "_codex_" |
| Launch single ephemeral runner | bash scripts/runner/actions_runner_ephemeral.sh --url "https://github.com/Aries-Serpent/_codex_" |
| Persistent runner (host) | sudo -u <runner_user> bash scripts/runner/actions_runner_bootstrap.sh --url "https://github.com/Aries-Serpent/_codex_" --version "2.329.0" --svc "systemd" |

Notes
- You do NOT need to paste the registration token manually; scripts mint short-lived tokens via GitHub API using GH_PAT/_CODEX_BOT_RUNNER.
- You do NOT need to edit workflow YAML to runs-on: self-hosted; repo already uses dynamic runs-on via RUNS_ON.
- The Actions runner automatically includes labels self-hosted, linux (and architecture). Add custom labels only if needed (e.g., docker).

Evidence
- All runner ops write JSONL entries to .codex/evidence/runner_ops.jsonl:
  - Actions: runner_ephemeral_start, runner_bootstrap, runner_remove, configure_repo_vars
