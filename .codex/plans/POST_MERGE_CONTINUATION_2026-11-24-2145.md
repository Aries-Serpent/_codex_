# Post-Merge Continuation Plan - 2026-11-24T21:45Z

## Objective

Continue PR #5850 (`Fix Auto-Approve closed and unapproved PR handling`) through exact-SHA review, terminal checks, and merge into `0D_base_`.

## Live Truth

- Repository: `Aries-Serpent/_codex_`
- Canonical branch: `0D_base_`
- Origin 0D_base SHA: `3202ed81943ac4f7dfd722186b4fa0f9b3e867dd`
- Origin main SHA: `4e0b834d369dc4ff6acf92932bc1f678ec7d70f3`
- PR: `#5850`, open, non-draft, mergeable=true, mergeable_state=unstable
- PR base: `0D_base_`
- PR head: `56fc1e9fa267efc307c96b4060acfac3ada0e5ec`
- Signed follow-up commits: `492f14fcccf9f5ecb66469a93cbb5d1440b6a6a1`, `56fc1e9fa267efc307c96b4060acfac3ada0e5ec`
- Rebase hard-stop marker: absent
- Existing dirty/untracked work: preserved

## Open Review Threads

1. Malformed PR state code fix: implemented with exact `open`/`closed` state validation in both target paths; resolved after exact-SHA verification.
2. WEC lookup conflation fix: implemented with authorized/missing-or-expired/label-inspection-error dispositions; resolved after exact-SHA verification.

## Current CI Evidence

- Historical Auto-Approve run `45493088673`: missing-WEC branch on PR head, exit code 1. Labeled rerun `45499276143` later completed success at head `492f14fccc`.
- Cognitive Pre-flight run `45493087810`: session-plan/accountability prerequisites were incomplete at that SHA. Cache save conflicts were infrastructure-only in the log.
- Exact-SHA merge gate at `56fc1e9fa267efc307c96b4060acfac3ada0e5ec` now ignores observation-only ML/cancelled Copilot evidence and evaluates real rollup checks. ML Components is being moved to weekly scheduled/manual evidence execution, removing PR-triggered gate pressure.
- Historical ML workflow `45501188838` was terminal and unit debt was routed to PR #5851; its current 307-failure aggregate is a scheduled remediation lane, not a PR merge gate.

## Execution Plan

1. Add two narrow regression groups:
   - malformed/missing PR state is denied in PR-only and SHA-plus-PR modes;
   - WEC lookup/status/history failures are denied and never return success.
2. Implement strict state classification and a tri-state WEC label result.
3. Run focused pytest, compileall, Black, isort, Ruff, mypy, and `git diff --check`. Completed locally for the approval slice.
4. Update the accountability report and changelog for the bounded fix. Completed.
5. Commit and push only the session branch. Completed at `492f14fccc` and `56fc1e9fa267efc307c96b4060acfac3ada0e5ec`.
6. Refresh PR reviews and all exact-SHA checks. Exact-SHA AI review is APPROVE; 4 coverage shards remain pending.
7. Resolve only review threads with matching landed code and exact verification. Both threads are resolved.
8. Merge PR #5850 into `0D_base_` only through the repository merge gate after:
   - no unresolved review threads;
   - exact-SHA AI review is approved;
   - required checks are terminal and green;
   - branch, WEC, owner, and environment controls remain intact.

## Queue After PR #5850

- #5810: review/failing-check remediation remains active.
- #5798: master tracker remains active until all post-merge lanes have exact dispositions.
- #5800/#5801/#5802/#5804/#5808: use existing evidence stop conditions and separate bounded sub-PRs.
- Codespaces and additional lanes remain evidence-gated; no closure claim until terminal artifacts prove disposition.

## Residual Risks

- The trusted approval helper is checked out from workflow SHA/default branch controls, so a PR-only source fix is not proof until a new exact-SHA rerun executes the repaired helper.
- The merge gate now deduplicates required checks by newest timestamp/ID to prevent historical failures from overriding later successes.
- Existing unrelated dirty/untracked files remain outside this lane.
