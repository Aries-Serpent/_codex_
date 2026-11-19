# Queued Plan: Transplant 31 Cognitive Brain Files into `clone-main`

**Status:** Queued. Do not implement until the current
`session/cognitive-brain-autopilot-20261118` workstream is complete, committed,
pushed, and reconciled.

## Branch and Diff Identity

- Target branch: `clone-main`
- Target branch source at creation: `origin/main` at
  `13851ac2ffd7aa8592d3e4e576b0a22b790bbee2`
- Comparison base branch: `clone-0d_base_` at
  `4c99aabc498b6086e16c91ba9d37ca9c307b0b92`
- Comparison head branch: `clone-session` at
  `6f54f98c5f0d06aac2dda5995152f1d11a7789eb`
- Three-dot merge base: `f188b8277a897db4bc1fbe844270077854acf08d`
- Expected result: exactly 31 changed files, 3,441 additions, 444 deletions.

`clone-main` was created locally and on origin from `origin/main`. No comparison
files have been applied to it yet.

## Source Commits

Apply only these commits, in order, with staged/cherry-pick preparation rather than
merge commits:

1. `1fe600a82ad8edf07b7f9e4ed478af9fe5f152c7`
   - `feat(cognitive-brain): checkpoint autonomous middleware implementation`
2. `b6b03381d68d1cb65737d74e5728455a04e6a433`
   - `docs(cognitive-brain): record published resume checkpoint`
3. `6f54f98c5f0d06aac2dda5995152f1d11a7789eb`
   - `feat(cognitive-brain): add idempotent route execution`

Together these commits produce exactly the requested 31-file set from
`origin/clone-0d_base_...origin/clone-session`.

## Scope Lock: Exactly 31 Files

### Codespace and VS Code configuration

1. `.codex/.gitignore`
2. `.devcontainer/devcontainer.json`
3. `.devcontainer/scripts/post-start.sh`
4. `.devcontainer/scripts/update-content.sh`
5. `.vscode/extensions.json`
6. `.vscode/settings.json`
7. `.vscode/tasks.json`

### Cognitive App and browser session

8. `cognitive_app/e2e/har-capture.spec.ts`
9. `cognitive_app/src/components/cli/ApiClient.tsx`
10. `cognitive_app/src/components/cli/XtermTerminal.tsx`
11. `cognitive_app/src/components/cli/index.tsx`
12. `cognitive_app/src/lib/api-mode-selector.ts`
13. `cognitive_app/src/lib/brain-session.ts`
14. `cognitive_app/src/lib/codex-api-client.ts`
15. `cognitive_app/src/lib/github-public-api.ts`
16. `cognitive_app/src/server/cli_api_server.py`

### Plans and autonomous probes

17. `docs/agent/COGNITIVE_BRAIN_MIDDLEWARE_AUTOPILOT_PLAN.md`
18. `docs/agent/COGNITIVE_BRAIN_MIDDLEWARE_RESUME_CHECKPOINT.md`
19. `scripts/autonomous/credential_probe.py`
20. `scripts/autonomous/github_permission_matrix.py`
21. `scripts/autonomous/install_gh_user.py`
22. `scripts/autonomous/maintainer_probe.py`
23. `scripts/validate_mcp.py`

### Routing, execution, and client integration

24. `src/aries_serpent_core/agents/brain_client.py`
25. `src/codex/cognitive_brain/route_execution.py`
26. `src/codex/cognitive_brain/routing.py`

### Tests

27. `tests/agents/test_brain_client.py`
28. `tests/autonomous/test_github_permission_matrix.py`
29. `tests/self_improvement/test_route_execution.py`
30. `tests/self_improvement/test_routing.py`
31. `tests/self_improvement/test_routing_api.py`

## Explicit Exclusions

Do not pull newer uncommitted or later-committed work automatically. In particular,
the following are outside the 31-file diff and require separate queued work:

- `scripts/autonomous/install_node_user.sh`
- `scripts/autonomous/install_chromium_user.sh`
- `scripts/autonomous/mcp_server.py`
- `.vscode/mcp.json`
- `cognitive_app/e2e/cognitive-brain-session.spec.ts`
- `tests/autonomous/test_mcp_server.py`
- current `127.0.0.1` frontend-default edits
- any later route, MCP, Playwright, PR, CI, or documentation commits after
  `6f54f98c5f0d06aac2dda5995152f1d11a7789eb`

## Preconditions

Do not start this plan until all are true:

1. The active task branch is fully committed and pushed.
2. PR #5834 and any follow-up PR/check evidence has been reconciled without claiming
   green CI or mergeability from local tests.
3. `git status --porcelain` is empty on the current task branch.
4. `clone-main` still has not diverged unexpectedly; if it moved, compare and stop
   rather than rebasing automatically.
5. `origin/clone-0d_base_` and `origin/clone-session` still resolve to the SHAs above.
6. A fresh worktree is available so the current session work is not disturbed.

## Implementation Sequence

### Phase 0: Isolated Worktree

Use a separate worktree for `clone-main`; do not switch the active dirty workspace.

```bash
git fetch origin
git worktree add /workspaces/clone-main-worktree clone-main
cd /workspaces/clone-main-worktree
git status --short
git rev-parse HEAD
git rev-parse origin/main
git diff --name-only HEAD..origin/main
```

Expected: worktree clean, no divergence, `HEAD == origin/main`.

### Phase 1: Dry-Run Commit Applicability

Record the exact source commit file lists and run conflict checks without committing:

```bash
git show --stat --oneline 1fe600a82ad8edf07b7f9e4ed478af9fe5f152c7
git show --stat --oneline b6b03381d68d1cb65737d74e5728455a04e6a433
git show --stat --oneline 6f54f98c5f0d06aac2dda5995152f1d11a7789eb
git cherry-pick -n 1fe600a82ad8edf07b7f9e4ed478af9fe5f152c7
```

If conflicts occur, do not commit. Resolve only inside the 31-file allowlist and
remove staging for any unrelated generated file. Then repeat for the second and
third commits in order.

### Phase 2: Staged Path Audit

After all no-commit cherry-picks are staged, assert exact scope:

```bash
git diff --cached --name-only | sort > /tmp/actual-31.txt
git diff --name-only origin/clone-0d_base_...origin/clone-session | sort > /tmp/expected-31.txt
diff -u /tmp/expected-31.txt /tmp/actual-31.txt
```

Acceptance: 31 lines and no diff. If this fails, unstage/remove only out-of-scope
files from the index and resolve the missing in-scope file before continuing.

### Phase 3: Dependency-Ordered Validation

1. Validate JSON, JSONC, shell syntax, Python compile, Ruff, Black, and `git diff --check`.
2. Run route tests:
   `tests/self_improvement/test_routing.py`,
   `test_route_execution.py`, and `test_routing_api.py`.
3. Run azimuth tests and existing BrainClient compatibility tests.
4. Run MCP HTTP smoke only if the exact 31-file set retains the current validator path fix.
5. Run frontend diagnostics/Vitest/build only after `cognitive_app/node_modules` exists.
6. Do not require the excluded newer Node/Chromium/MCP files as part of this gate.

### Phase 4: Security and Conflict Review

Review these highest-conflict files first:

- `cognitive_app/src/server/cli_api_server.py`
- `src/aries_serpent_core/agents/brain_client.py`
- `.devcontainer/devcontainer.json`
- `.devcontainer/scripts/post-start.sh`
- `.devcontainer/scripts/update-content.sh`
- `.vscode/tasks.json`

For each, verify no `main`-specific security fix is lost while resolving conflicts.
Reapply the source change around current `main` logic; do not copy a stale entire
file if `main` has newer safeguards.

Adversarial checks:

- unauthenticated CLI/proxy/history/WebSocket requests are denied;
- raw GitHub token endpoint remains 410;
- caller mutation flags cannot authorize writes;
- denied plans have no preferred executable adapter;
- unchanged idempotency key plus changed request conflicts;
- repeated completed execution replays without a second side effect;
- stale PID cannot terminate unrelated processes;
- Codespace name is runtime evidence only;
- Git remote output and browser assets contain no credentials.

### Phase 5: Commit and Publish

Commit the exact staged set on `clone-main` only after all focused checks pass.
Suggested commit:

```text
feat(cognitive-brain): transplant 31-file maintainer middleware checkpoint
```

Push `clone-main` normally, never force:

```bash
git push origin clone-main
```

Do not create a PR from `clone-main` in this queued plan unless a separate task is
approved. The output is a clean transplanted branch with exact scope and evidence.

## Acceptance Matrix

| Dimension | Acceptance |
|---|---|
| Scope | `git diff --name-only` and staged file list exactly equal the 31-file matrix |
| Base | `clone-main` remains based on the verified `origin/main` tip at task start |
| Security | All negative auth/routing/SSRF/token/PID tests pass |
| Python | Focused compile, Ruff, Black, pytest, and diff check pass |
| Codespace | JSON/JSONC and shell syntax pass; startup uses dynamic workspace identity |
| Frontend | No new TypeScript diagnostics in in-scope frontend files; available Vitest/build checks pass |
| GitHub | No live write is attempted during transplant solely to prove scope |
| Recovery | Commit SHA, conflict resolutions, exact tests, and any skipped checks are recorded |

## Completion Evidence

Record:

- `clone-main` base SHA and final SHA;
- merge base and source commit SHAs;
- exact 31-file `diff` assertion;
- conflict-resolution files and rationale;
- test commands/results;
- lint/type/build skips with technical reason;
- hosted or external prerequisites that remained outside the branch transplant;
- remote push result.
