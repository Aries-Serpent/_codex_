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

These are planned work packages, not completed milestones or authorization to
pack. Do not execute 003 merely because 002 has started.

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
