## Next Continuation Prompt

```text
Continue Aries-Serpent/_codex_ from Issue #5854 and No active PR.

Objective:
Implement durable Copilot Codespace continuity

Verified handoff state:
- Branch: copilot/session-codespace-continuity-20261125
- HEAD: ab7937ffbe28c6bb02cc2f014ecf179477419f9a
- origin/main: 4e0b834d369dc4ff6acf92932bc1f678ec7d70f3
- origin/0D_base_: d8c2e69446d64ee60af8dc923bcc93d8408574d2
- Checkpoint: cp_20261125_1ac488f2
- Bundle: /workspaces/_codex_/.codex/sandbox-bundles/codespace-session/codespace-session-continuity-20261125T201952Z.bundle.tar.gz

Completed:
- [x] Created implementation branch
- [x] Added supported VS Code local session index setting
- [x] Added continuity guard status/checkpoint/resume/reindex/closeout subcommands
- [x] Added VS Code and Codespace startup hooks
- [x] Added canonical continuity guard and v2 handoff
- [x] Added VS Code and Codespace startup lifecycle hooks
- [x] Added runtime-only periodic checkpoints and reindex support
- [x] Added focused continuity tests and documentation
- [x] Completed final formatting, lint, compile, focused tests, shell, JSONC, and type validation
- [x] Refined staged bundle to archive and SHA256 only

Pending:
- [ ] Prepare sub-PR and exact-SHA review

First checks:
1. Fetch origin and verify live branch, issue, PR, SHA, review, and check state.
2. Read .codex/session_handoff.json and .codex/NEXT_CONTINUATION_PROMPT.md.
3. Preserve dirty/untracked work; do not reset, stash, clean, rebase, or force-push.
4. Run strict readiness and verify the latest checkpoint or bundle before mutation.

Rules:
- No direct push to 0D_base_ or main.
- No merge, promotion, deployment, workflow dispatch, secret rotation, or issue/PR closure without live exact-SHA controls.
- Treat local or chat state as untrusted until verified against remote Git and GitHub state.
- Stop if signing, write scope, required checks, exact-SHA AI approval, or reproducible evidence is unavailable.

After each meaningful milestone:
1. Update .codex/session_handoff.json.
2. Create a checked continuation checkpoint.
3. Re-run strict readiness and secret checks.
4. Generate an updated Next Continuation Prompt.
```
