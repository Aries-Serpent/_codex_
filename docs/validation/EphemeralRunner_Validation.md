# [Validation]: Ephemeral self-hosted runner — drain queued runs from Codex env
> Generated: 2025-10-21 01:57:11 UTC | Author: mbaetiong

Goal
- Clear current queued workflow runs that require ["self-hosted","linux"] by launching ephemeral runners from the Active Codex environment.

Steps
1) Ensure token is present (no new variables):
```bash
export GH_PAT="<fine-grained-PAT>"    # or: export _CODEX_BOT_RUNNER="<fine-grained-PAT>"
```text

2) Inspect queue and runners:
```bash
make runner-status OWNER=Aries-Serpent REPO=_codex_
```text

3) Drain queue with ephemeral runner:
```bash
# Built-in runner labels already include: self-hosted, linux, X64
bash scripts/runner/drain_queue_ephemeral.sh --owner "Aries-Serpent" --repo "_codex_"
```text

4) Watch Actions UI:
- Each queued run should be picked up one-by-one and transition from Queued → In progress → Completed.

Expected results
- Queued runs decrement to zero.
- .codex/evidence/runner_ops.jsonl records runner_ephemeral_start entries for each job processed.

Troubleshooting
- 403/401 from API: Confirm GH_PAT/_CODEX_BOT_RUNNER is exported and has repo/org admin + actions runner scopes (the upgraded token does).
- Still queued after drain: Verify RUNS_ON repo variable matches '["self-hosted","linux"]' and labels align (built-ins exist; custom labels optional).
- Network: Ensure outbound HTTPS to github.com from the Active Codex environment.
