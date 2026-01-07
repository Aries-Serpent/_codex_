# [Validation]: Self-hosted runner — GH_PAT/_CODEX_BOT_RUNNER flow
> Generated: 2024-10-21 00:50:48 UTC | Author: mbaetiong

Goal
- Validate end-to-end setup of a self-hosted runner using existing tokens (GH_PAT or _CODEX_BOT_RUNNER) without introducing new variables.

Checklist
| Step | Command | Expectation |
|---|---|---|
| Install Docker | sudo bash scripts/runner/install_docker.sh <runner_user> | docker info succeeds; user in docker group |
| Optional binfmt | sudo -u <runner_user> bash scripts/runner/install_binfmt.sh | binfmt entries visible |
| Bootstrap (repo-level) | sudo -u <runner_user> bash scripts/runner/actions_runner_bootstrap.sh --url "https://github.com/Aries-Serpent/_codex_" --labels "self-hosted,linux,docker" --version "2.329.0" --svc systemd | Runner registers and service starts |
| Diagnostics | GH UI → Actions → “Runner diagnostics — self-hosted readiness” → Run workflow | Summary shows Docker present, Buildx checked |
| CI (check-only) | Dispatch Docker CI with check_only=true and approval_duration="24h" | Approval-check passes; build/push skipped |
| CI (full run on main) | Push to main during approval window | Build → smoke → push → GHCR pull+smoke succeed |

Notes
- Token sourcing: scripts prefer GH_PAT, fallback to _CODEX_BOT_RUNNER. No other variables needed.
- Repo defaults use runs-on ["self-hosted","linux"]. You Phase 5 temporarily set RUNS_ON='["ubuntu-latest"]' only if you intend to test with hosted runners (single-arch).
- If org-level registration is desired, pass --url "https://github.com/Aries-Serpent" and ensure the PAT has sufficient org admin permission.

Troubleshooting
- PAT insufficient: Use repo-level URL; confirm the fine-grained PAT has Administration: Read and write for the repository.
- Service won’t start: journalctl -u actions-runner@<runner_user> -b --no-pager
- Docker permission denied: newgrp docker or re-login after adding user to docker group.
- Multi-arch errors: binfmt requires privileged Docker; run install_binfmt.sh and re-run diagnostics.
