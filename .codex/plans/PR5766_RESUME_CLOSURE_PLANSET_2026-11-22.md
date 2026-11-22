# PR 5766 Resume and Closure Planset

Status: implementation handoff; merge blocked

## Evidence anchor

- Latest published 0D_base handoff head before the refresh: `1212dbbcf52a1a208eb0921265e4a9604575028f`
- ML evidence head: `42073ea3eeee218c3350816017fb92c5c6b2fa21`
- Live main: `f6f822dde20e221eefffdbc133b82f4868cc5659`
- PR: `5766`, open, not merged
- ML run: `44971752791`, attempt 2, aggregate failed
- Aggregate artifact: `14735719851`, `ml-slow-reports`
- Integration: 1,797 tests, 0 failures/errors, 23 skipped
- Unit: 32,258 tests, 754 failures/errors, 1,014 skipped
- Combined unit coverage: 54.99%
- Coverage floor: 54; target: 70
- Quarantine: 0 entries
- Ratchet result: no quarantine growth and no floor decrease
- Review: exact-SHA approval record remains applicable to the unchanged campaign head
- Today’s local scorecard: 85/100, NOT READY; PDA/accountability, sync, action pins, ruff, Pattern 27, download-artifact v5, and AAIS pass; repository auto-fix remains red
- Merge decision: do not merge until a fresh exact-head aggregate passes

## Resumable objective

Complete the four unit-failure repair lanes, ratchet coverage toward 70%, refresh all
campaign issue evidence, reconcile `0D_base_` and `main`, and merge PR 5766 only when
the live merge gate is green. Coverage 54.99% is retained as a successful floor result;
it is not a substitute for the unit failure gate or the target 70% milestone.

## Multi-lane execution model

Run independent evidence and issue lanes in parallel only after the exact campaign state
is frozen. Run implementation lanes sequentially by batch to prevent overlapping fixes
from changing the same test contract.

### Lane A: unit-failure remediation

Owner: CI Testing Agent plus direct execution.

Ordered batches:

1. Collection and fixture/environment debt:
   - missing files and documentation fixtures
   - subprocess/CLI JSON preambles
   - secret-policy assumptions
   - optional-dependency and import drift
   - pytest setup/fixture errors
2. API and contract debt:
   - CLI 49 failures
   - unit 37 failures
   - tokenizer 22 failures
   - interfaces 12 failures
   - tracking 12 failures
   - model-loader 11 failures
   - reporting and CI modules
   - explicit missing signatures/imports
3. Stateful behavior:
   - refactoring 31 failures
   - cognitive 30 failures
   - cognitive-brain 24 failures
   - checkpoint/circuit-breaker behavior
   - quantum/distributed/service contracts
   - interpretability 27 failures
4. ML/reporting/quality:
   - reporting CLI 19 failures
   - metrics 16 failures
   - codex-ml 12 failures
   - validation 14 failures
   - remaining module families

Per-batch stop condition:

- reproduce exact node IDs and exception classes
- make one root-cause repair per PR
- add focused regression coverage
- run the owning shard/focused suite
- run compile, Ruff, Black/isort, diff, and manifest checks as applicable
- push a signed commit to `0D_base_`
- rerun the exact aggregate before declaring the batch complete

Do not place these failures in the quarantine manifest merely to force the aggregate
green. Quarantine entries require the explicit `quarantine-approved` PR label and
strict-xfail verification.

### Lane B: coverage ratchet

Owner: Unified Coverage Agent plus direct execution.

- Preserve floor 54 and target 70.
- Preserve 54.99% as the post-run baseline.
- Rank uncovered `src/` modules by uncovered lines times impact.
- Select one batch and one regression group at a time.
- Recompute combined coverage from all four `.coverage.unit-*` artifacts.
- Raise the floor only after measured coverage rises at least 1.5 points:
  `floor = floor(measured - 0.5)`, capped at 70.
- Never lower the floor or shrink the target by relabeling debt.
- Close #5801 only at 70% or by an explicit owner-approved target policy change.

### Lane C: issue and scorecard closure

Owner: direct execution plus issue-tracker review.

Issue mappings:

- #5798 master continuation tracker
- #5799 PDA/scorecard
- #5800 unit-failure repair batches
- #5801 coverage ratchet 54.99 -> 70
- #5802 auto-fix backlog
- #5803 CodeQL, closed
- #5804 dependency CVEs, open
- #5805 merge readiness, open
- #5806 owner/auth, closed
- #5807 frontend, open
- #5808 RAG, open
- #5809 main sync, open
- #5810 review/remediation, open
- #5811 npm advisories, closed

Update bodies at each branch publication boundary. Preserve exactly one versioned
`codex-pr5766-final-evidence-v1` block per issue. Re-read each body after mutation.

### Lane D: main and PR promotion

Owner: direct execution with explicit operation-specific authorization.

Preferred path: merge PR 5766 only after all required checks pass at one exact head.
No direct push to `main` is implicit.

If a small already-approved hotfix must reach `main` before the full unit backlog closes,
use a dedicated PR against `main`, not a forced ref update. It must contain only reviewed
operational fixes and pass workflow, security, lint, and focused source validation.

Candidate promotion surfaces:

- RAG workflow and retriever
- ML PR-base ratchet and aggregate workflow
- maintainer/rate-limit transport
- exact-SHA AI review
- owner/App auth and signing
- validation and manifest publication
- hash-table and retriever behavior
- focused tests for promoted files

No workflow patch is activated or dispatched unless explicitly authorized for that task.

### Lane E: review and merge readiness

Owner: direct execution plus review gate.

At every candidate head require:

- exact-SHA approval
- commit_id equals the candidate head
- zero unresolved review threads
- zero unanswered inline findings
- all required checks success
- unchanged WEC byte-for-byte
- clean/mergeable state
- no force or preview-merge operation

One failed required check at the exact head blocks merge even if local tests pass.

## Azimuthal adversarial review

The continuation plan was tested against these alternative explanations:

1. Component and integration jobs passed, so unit debt may be infrastructure.
   Disconfirmed: aggregate JUnit reports contain 754 concrete failures, and the
   aggregate gate failed in the validation step.
2. 54.99% coverage may satisfy the target 70%.
   Disconfirmed: target remains 70; 54.99 is above floor 54 and below target 70.
3. 754 failures may justify automatic quarantine.
   Disconfirmed: quarantine is empty and intentionally fail-closed; quarantine growth
   would require explicit approval and strict-xfail evidence.
4. The final PR can merge after bypassing the ML aggregate.
   Disconfirmed: the aggregate is required evidence and remains failed at the live head.
5. 0D_base and main are already synchronized.
   Disconfirmed: main is behind or divergent, and exact-head ancestry was not satisfied.
6. Review approval can be reused after a new head.
   Disconfirmed: a new head requires fresh exact-SHA evidence and review/current checks.

## Rubber-duck validation

A reader should be able to answer all of these without chat context:

- Why is merge blocked? The exact ML aggregate failed on 754 unit failures.
- Why is coverage not a blocker and also not complete? 54.99 passes floor 54 and leaves target 70 unmet.
- Why is quarantine not an escape hatch? The baseline is zero and quarantine changes require explicit approval.
- What is the next implementation unit? One module-family repair batch on `0D_base_`, then an exact aggregate rerun.
- What is the only merge path? Fresh exact-SHA approval and all required checks at one candidate head.
- What happens after merge? Continue coverage/unit follow-up PRs against main, not a post-merge waiver.

## Codespace closure state

Before close:

- keep a clean worktree or record unrelated dirty work explicitly
- push implementation commits only to `0D_base_`
- append the 2026-11-22 PDA entry exactly once
- refresh accountability and issue evidence
- stop active test watchers and keepalive only after publication
- leave PR 5766 open and unmerged
- preserve exact rerun commands and next issue owner
- do not stop keepalive until the explicit Codespace-close wrap-up operation is authorized

## Resume prompt

Use this prompt in the next session:

> Continue PR 5766 resume from campaign head 42073ea3eeee218c3350816017fb92c5c6b2fa21.
> Refresh origin/main and origin/0D_base_, validate issue/PDA state, start unit batch 1,
> and rerun ML run 44971752791 at the first new exact head only after that batch passes.
> Preserve coverage floor 54, target 70, quarantine 0, and WEC selections. Do not merge,
> dispatch workflows, or push to main without operation-specific authorization.
