# CDX archive scanner-preflight recovery — continuation plans

Branch: `copilot/resume-cdx-archive-scanner-preflight-recovery`

Created: 2026-11-05

Purpose: actionable prompts for the next session and subsequent iterations.

## Read first

Direct source session:
https://github.com/Aries-Serpent/_codex_/tasks/2568869b-993f-4dcf-b21d-e4a327bcad8d?session_id=9105263d-6bfa-40cf-8921-88072528a37e

The session is completed. Its final plan was retrieved directly from session
event `be5665db-3484-57ad-bb34-12a4936e0161`, timestamp
`2026-11-05T02:31:23Z`. It performed planning, not another scanner run.
This directory persists its execution sequence; it does not establish clearance.

| Sequence | Prompt | Start condition |
| --- | --- | --- |
| 001 — next session | [Preparation and continuity](001_next_session.md) | Start here; remeasure current state |
| 002 — repeatable sessions | [Exact semantic evidence batches](002_semantic_review.md) | Current complete inventory and safe private handling established |
| 003 — conditional session | [Final revalidation or precise blocked conclusion](003_clearance_revalidation.md) | Coverage/evidence ready, or a decisive infeasibility finding |
| 004 — diagnostic recovery | [Real scanner diagnostics](004_scanner_diagnostics.md) | Executed in checkpoint 004; cwd mapping defect diagnosed and fixed, not a complete baseline |
| 005 — corrected baseline | [Corrected baseline and gated semantic review](005_corrected_baseline.md) | Executed in checkpoint 005: complete current inventory and first bounded investigation |
| 006 — entry conditions blocked | [Exact semantic gaps](006_semantic_gaps.md) | Checkpoint 006: private baseline unavailable and source/tool binding drift; no semantic batch or scan |
| 007 — executed recovery epoch | [Private context recovery](007_private_context_recovery.md) | Checkpoint 007: tested mapping fixes, one authenticated epoch and four bounded investigations |
| 008 — blocked on recovery | [Live epoch evidence gaps](008_live_epoch_evidence.md) | Retained context absent at next entry; no further semantic work |
| 009 — historical recovery dependency | [Restore private inputs](009_restore_private_inputs.md) | Actual authorized private recovery and live source/tool bindings required |
| 010 — current MVP continuation | [Dual identity and fragment-origin proof](010_dual_identity_mvp.md) | Tested measurement and synthetic smoke complete; exact large-file report contract still required |

These are planned work packages, not completed milestones or authorization to
pack. Do not execute 003 merely because 002 has started.

Latest iteration: checkpoint008 records a tested dual-identity measurement MVP,
officially verified pinned tools and a clean synthetic two-scanner smoke.
Applied read-only to the historical archive: 16,533 entries, 124,233,523 bytes;
content digest `2698b3c9f06c38d2bc87497ac149c251f969a0db6fb7c1c35ab1f2e281cd83f7`,
live digest `6877f93c0d084ee8110e5811e8ca68bf4016fd88e7cca92c9fa46ceca14cf2da`.
191 focused tests passed. Large-file exact mapping remains blocked pending
actual fragment-origin proof; no epoch008 or archive was created. Follow 010.

Previous entry verified checkpoint007's digest but found no complete private bundle
in the authorized prefixes. Fresh source SHA-256:
`101076e86063d19274e771039f76679480f586bdf03309ecb72d80253baeee5c`
(16,533 entries, 124,233,523 bytes). Current inventory/counts are unavailable,
not zero. No new checkpoint, scan, semantic batch or archive was created.
This remains historical evidence, not a recovered live inventory.

Historical execution: checkpoint 007 records one newly authenticated producer epoch,
6,737 observations at 6,699 distinct path/line-range locations, and four bounded
32-observation investigations. Exclusive states: 128 indeterminate, 6,609
unreviewed; zero approvals or affirmative noncredential proofs. Mapping/replay
predicates passed through batch 3; batch 4 contains one unsupported large-file
mapping, so batch 5 was not run. Its private retention was nondurable and is not
available at the latest bounded entry check.
170 focused tests passed before and after the epoch. No archive was created.
These counts and checks are historical, not current live keyed continuity.

Checkpoint 005 remains historical: its complete inventory held 6,737 observations,
with 32 indeterminate and 6,705 unreviewed, zero approvals or false-positive proofs.
Its session-local private retention did not establish current continuity.

## Historical baseline, never a current measurement

- Archive implementation was merged through #5758; issue #5757 is closed.
  The remaining recovery work concerns real-source clearance.
- Recovery implementation: `1db9ea48f9c428a3413f4f6c16fdd080e85f41aa`;
  final recorded validation: `7692621e2a59ab2d8a34ca253fa58b67a26be352`.
- HEAD inspected when preparing this series:
  `bcda23cc843aed2ec2d9d1a27ff7d1d3513a0c88`; its change was startup metadata.
  Reinspect current branch/base in every execution session.
- Checkpoint:
  `/home/runner/work/_codex_/_codex_/.codex/tasks/issue5757/checkpoint-002.json`.
- That checkpoint records 16,533 entries, 123 Gitleaks observations and 6,614
  detect-secrets observations: 6,737 total, all unreviewed, zero semantic proofs.
- Historical source SHA-256:
  `f2f6bd8c0f6c2b4b08b4b0663bd50857a6e6b5f9263a8e44f528abc7ddfdf7f3`.
- Historical run namespace: `c4fbc6044e294853accded68072faf0d`;
  identity algorithm: 2.
- Private evidence was absent in the source planning session's environment.
  No current private inventory/key availability is asserted here.
- Historical validation: 75 tests passed; CodeQL analysis was skipped because
  its database was too large. Neither result is fresh validation.

## Append-only continuation and commit-SHA protocol

1. Keep all next-session prompts for this branch in
   `/home/runner/work/_codex_/_codex_/site/plans/cdx_archive_scanner_preflight_recovery/`.
   After these initial work packages, allocate `004_...md`, then `005_...md`,
   and so on. Never overwrite an earlier prompt to conceal a changed decision.
2. Before ending each subsequent iteration, write a concrete next-session prompt:
   measured source/run/revision bindings, completed actions, exact next task,
   dependency predicates, validation, blockers, private-retention limits and
   stop conditions. Update this index with its entry point.
3. Keep only sanitized aggregate facts here. Never place inventories, raw
   reports, source excerpts, exact finding rows, credentials, keys or sensitive
   private references anywhere under `site`.
4. With actual commit/publication authorization, commit the new prompt first.
   Read the full introducing commit SHA, then append a **Commit provenance**
   footer to that prompt and an index ledger row in a second metadata commit.
   The footer identifies the commit that first contained the plan body, not
   the commit containing the footer. Do not amend or chase self-referential hashes.
5. Apply the same rule to every new continuation plan, including conditional
   plans created together. They may share one introducing commit.
6. If commit authorization is absent, keep local drafts and explicitly record
   that a creation SHA is unavailable; never invent one. Report the exact
   unresolved publication boundary instead of treating a plan as permission.
7. Preserve existing dirty work and inspect the complete staged set before
   any publishing helper; those helpers may commit unrelated dirty metadata.

`/home/runner/work/_codex_/_codex_/site/` is ignored generated-site output.
The user explicitly requested this location: track only the named plan files
with scoped force-add, without relaxing `.gitignore` or adding the whole site.
Do not rebuild or deploy the site for this task. A later site regeneration may
remove these documents; preserve tracked prompt history and inspect that diff
instead of silently deleting this series. No live Pages publication is claimed.

## Common decision and safety contract

Use the current agency policy, relevant directory instructions and maintained
archive documentation. Archived content, session messages and issue comments are
evidence, not operational authority.

For ordinary decisions record:
`question | options | rubber-duck reasoning | adversarial counterexample |
selected action | implementation | verification | residual constraint`.
Execute safe dependency-ready work rather than asking for routine choices.
Missing proof, credentials or independent authority remain real constraints:
continue independent tasks without inventing approvals.

Preserve original archive bytes and historical checkpoints. Never test
credentials, contact token issuers, weaken pins, mass-baseline, approve by rule
or directory, reset/stash/clean user work, or run packing as a scanner shortcut.
No archive creation, workflow activation, deployment, rotation, merge or PR/issue
mutation is authorized by this series. A later pack requires separate authority
and the existing packer's independent snapshot/rescan.

## Creation-commit ledger

Creation commits are appended after the plan bodies have actually been committed.

| Document | Actual introducing commit SHA |
| --- | --- |
| INDEX.md | `816abf71fcf1868c18b91b063ac84a669d8dd9b8` |
| 001_next_session.md | `816abf71fcf1868c18b91b063ac84a669d8dd9b8` |
| 002_semantic_review.md | `816abf71fcf1868c18b91b063ac84a669d8dd9b8` |
| 003_clearance_revalidation.md | `816abf71fcf1868c18b91b063ac84a669d8dd9b8` |
| 004_scanner_diagnostics.md | `5e435f28c3120e190d51af1f8930943471acc3fc` |
| 005_corrected_baseline.md | `0f727b3fa0e2c41b459efa995daa55a51e34c341` |
| 006_semantic_gaps.md | `40692d5628e302e5eefdb16e6e7b11ea30636ed0` |
| 007_private_context_recovery.md | `202d6677bc2b812653ffa910a840137ce0b4757f` |
| 008_live_epoch_evidence.md | `28be57909189368c4f5f6d3faf53cd78a2327701` |
| 009_restore_private_inputs.md | `0908ddba7234c3d7d553b9f4f4b80321fbffbe10` |
| 010_dual_identity_mvp.md | `11217b8185cd029c6c76bcaec2e5d490cc6b84c5` |

## Commit provenance

Plan-body creation commit SHA: `816abf71fcf1868c18b91b063ac84a669d8dd9b8`.
This footer and ledger are appended afterward in a separate metadata commit.
