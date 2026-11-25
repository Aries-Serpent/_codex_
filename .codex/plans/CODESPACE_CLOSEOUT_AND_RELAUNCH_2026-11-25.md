# Codespace Closeout and Relaunch Plan

**Status:** Implementation in progress; source commit `62f3f85eb8d3da300cc16f2d1d68a18e88957d07` created locally, remote publication pending

## Live Truth

- Repository: `Aries-Serpent/_codex_`
- Authority: `origin/0D_base_`
- Authority SHA: `496da57da8f46fec3bf52715020028be88491ca5`
- Main closeout branch: `copilot/session-codespace-closeout-20261125`
- Preservation bundle: `.codex/sandbox-bundles/codespace-closeout/codespace-closeout-main-20261125T044616Z.bundle.tar.gz`
- Bundle SHA256: `54d0fce03462d5e2b05263f9605ac0850828cb8222d21a7fb548e91605a55b68`

## Merged PR Evidence

| PR | Head | Squash merge commit |
|---|---|---|
| #5850 | `250f1ced618b663067b74697e1bbd5722a61d15b` | `877a183a83f9a1e3f600cf5da2e4b068650e67ca` |
| #5851 | `152daba257a2dafb0850445d32b09b1d50efc370` | `89e50781de26525f2f3d4c562fe880873a18b7c5` |
| #5852 | `d904b21de25ad38073521688cd33ce4650e47811` | `ade470bb7f6b6e5b135e8f9b66839f56e6d51e32` |
| #5853 | `b70c56c49b57fd60941261cc91c33cd567dc505c` | `496da57da8f46fec3bf52715020028be88491ca5` |

Use live GitHub state as authoritative. PR #5850 is historical and must not be reopened or reimplemented.

## First Relaunch Objective

Resume [issue #5800](https://github.com/Aries-Serpent/_codex_/issues/5800), unit-test failure remediation, with one exact-JUnit cluster only:

1. Refresh `origin/0D_base_` and verify the closeout branch.
2. Reproduce one cluster in an isolated worktree.
3. Add or correct source/tests for that cluster only.
4. Run focused pytest, Black, isort, Ruff, compileall, mypy when applicable, and `git diff --check`.
5. Create a separate signed `copilot/session-*` branch and PR into `0D_base_` only after exact evidence and review controls pass.

The next evidence-backed cluster can be PDA integrity, routing API, coverage-gate policy, or another actual recurring JUnit cluster. The engine-HF lane remains environment-blocked until real `transformers` is available.

## Worktree Preservation

| Worktree | Branch | State |
|---|---|---|
| `/workspaces/_codex_` | `copilot/session-codespace-closeout-20261125` | Dirty implementation and handoff work preserved |
| `/workspaces/_codex-unit-engine-hf-trainer-20261125` | `copilot/session-unit-engine-hf-trainer-20261125` | Clean at 0D head; HF dependency blocked |
| `/workspaces/_codex-unit-error-logging-20261125` | `copilot/session-closeout-unit-error-logging-20261125` | Dirty `.codex/fragile_tests.json` evidence |
| `/workspaces/_codex-unit-pda-integrity-20261125` | `copilot/session-unit-pda-integrity-20261125` | Clean |
| `/workspaces/_codex-unit-pooling-20261124` | `copilot/session-closeout-unit-pooling-20261125` | Dirty coverage/report evidence |
| `/workspaces/_codex-unit-routing-api-20261125` | `copilot/session-unit-routing-api-20261125` | Clean |
| `/workspaces/_codex-unit-telemetry-20261125` | `copilot/session-closeout-unit-telemetry-20261125` | Dirty `.codex/fragile_tests.json` evidence |

Do not delete or reset these worktrees until their remote preservation refs are verified.

## Relaunch Commands

```bash
cd /workspaces/_codex_
git fetch --no-tags origin --prune
git switch copilot/session-codespace-closeout-20261125
git status --short --branch
git worktree list --porcelain
.venv/bin/python scripts/autonomous/codespace_readiness.py --strict --worktree . --json
.venv/bin/python -m scripts.ci.startup_health --validate
```

If the closeout branch is not restored remotely, restore the verified patch archive before any source changes:

```bash
.venv/bin/python scripts/archive/git_patch_bundle.py verify --bundle .codex/sandbox-bundles/codespace-closeout/codespace-closeout-main-20261125T044616Z.bundle.tar.gz
.venv/bin/python scripts/archive/git_patch_bundle.py apply --bundle .codex/sandbox-bundles/codespace-closeout/codespace-closeout-main-20261125T044616Z.bundle.tar.gz --repo-root /workspaces/_codex_
```

## Issue Continuation

- #5798: master post-merge tracker; remains open.
- #5800: unit-failure remediation; remains open until exact aggregate/stop evidence.
- #5801: coverage floor/target lane; remains open.
- #5802: auto-fix backlog; remains open.
- #5804: dependencies/CVE lane; remains open.
- #5808: RAG lane; remains open until exact hosted evidence.
- #5810: review/failing-check remediation; remains open.

ML Components remains scheduled weekly and manually dispatchable. It is not a pull-request gate.

## Closeout Stop Rules

- Do not push directly to `0D_base_`.
- Do not merge, promote, deploy, dispatch workflows, or change repository settings.
- Do not close issues or claim success from local-only evidence.
- Do not commit plaintext secrets or PII.
- Preserve existing dirty evidence; do not reset, rebase, stash, clean, or force-push.
- Stop before mutation if signing or write scope is unavailable, staged content fails secret checks, or live 0D moves during publication.
