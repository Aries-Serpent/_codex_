# [Plan]: Self-hosted runner — Codex session quick-guide (GH_PAT/_CODEX_BOT_RUNNER) — Ephemeral + Repo variables lifecycle
> Generated: 2024-10-21 03:27:15 UTC | Author: mbaetiong

Goal
- Manage self-hosted runner routing and repository Actions variables entirely from Codex using GH_PAT/_CODEX_BOT_RUNNER.
- New: Creating new repository variables is allowed (Codex-managed), alongside updating and deleting.

Prereqs (no new secrets)
- Export GH_PAT in your shell OR ensure _CODEX_BOT_RUNNER is available in env.

Quick reference
| Task | Command |
|---|---|
| Runner inventory | make runner-status OWNER=Aries-Serpent REPO=_codex_ |
| Drain queued runs (ephemeral) | bash scripts/runner/drain_queue_ephemeral.sh --owner "Aries-Serpent" --repo "_codex_" |
| Single ephemeral runner | bash scripts/runner/actions_runner_ephemeral.sh --url "https://github.com/Aries-Serpent/_codex_" |
| Persistent runner (host) | sudo -u <runner_user> bash scripts/runner/actions_runner_bootstrap.sh --url "https://github.com/Aries-Serpent/_codex_" --version "2.329.0" --svc "systemd" |
| Repo vars — set curated | make runner-vars OWNER=Aries-Serpent REPO=_codex_ RUNS_ON='["self-hosted","linux"]' |
| Repo vars — create/update generic | make runner-vars OWNER=Aries-Serpent REPO=_codex_ SETS="FOO=bar NEW_FLAG=1" |
| Repo vars — delete | make runner-vars OWNER=Aries-Serpent REPO=_codex_ DELETE="FOO NEW_FLAG" |
| Repo vars — list | make vars-list OWNER=Aries-Serpent REPO=_codex_ [FORMAT=json] |
| Repo vars — delete (targeted) | make vars-delete OWNER=Aries-Serpent REPO=_codex_ NAMES="FOO BAR" |

Notes
- Registration tokens for runners are minted automatically via GitHub API.
- Runner label nuance: ephemeral helpers add linux (lowercase) to satisfy runs-on ["self-hosted","linux"].
- Ephemeral runners export DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1 to avoid ICU issues on minimal hosts.
- Evidence for all ops: .codex/evidence/runner_ops.jsonl

Permissions
- GH_PAT/_CODEX_BOT_RUNNER must include repo admin and actions variables scopes for create/update/delete/list.
