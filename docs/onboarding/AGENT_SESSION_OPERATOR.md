# Agent/session operator

## Where to start

Read the [session and agent-state guide](../SESSION_STATE_GUIDE.md), then the
[repository map](../REPOSITORY_MAP.md).

## Where the code lives

- `.codex/`: operational state, policy, memory evidence, and session artifacts
- `agents/`: packaged orchestration primitives
- `src/cognitive_brain/`: cognitive contracts and memory/coordination components
- `src/aries_serpent_core/brain/`: optional OODA, checkpoint, and resume utilities
- `scripts/ci/`: session bootstrap, recovery, query, and wrap-up tools

## What this role cares about

Session continuity, evidence provenance, checkpoint boundaries, multi-lane ownership,
WEC preservation, accountability, and safe handling of generated state.

## Key technologies

JSONL, JSON, YAML, SQLite, DuckDB, OODA/PDA/AfterMath concepts, GitHub MCP, custom
agents, and repository CI helpers.

## Typical workflow

1. Load policy, repository state, recent PDA records, and the active PR state.
2. Divide independent work into named parallel lanes.
3. Keep generated observations separate from canonical source and documentation.
4. Record validation evidence and decisions.
5. Update accountability and session-close artifacts.

## Common gotchas

- `.codex/` mixes canonical policy with dated and generated evidence; file labels and
  owning scripts determine authority.
- Agent memory, checkpoints, and git history solve different continuity problems.
- Do not edit generated indexes when their header names a generator.
- Preserve maintainer-controlled WEC selections across progress updates.

