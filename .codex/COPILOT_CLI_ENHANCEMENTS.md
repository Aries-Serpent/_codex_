# Copilot CLI Enhancements

**Status:** Implemented bootstrap for Phase 10/11/12 campaign entry points  
**Updated:** 2026-07-02T21:45:29Z

## New `chronicle` commands

- `python -m codex.cli chronicle checkpoint`
  - Creates a compressed session checkpoint in `/home/runner/work/_codex_/_codex_/.codex/checkpoints`
- `python -m codex.cli chronicle resume-session <checkpoint_id>`
  - Restores checkpoint state and prints the recovered task summary
- `python -m codex.cli chronicle route-task "<command>"`
  - Recommends `task`, `bash`, or `general-purpose` execution based on workflow shape
- `python -m codex.cli chronicle agent-chain --focus <focus>`
  - Prints the recommended specialized-agent chain for `codeql`, `security`, `ci`, `coverage`, `docs`, or `orchestration`
- `python -m codex.cli chronicle auto-fix`
  - Runs the campaign CI diagnostics/remediation wrappers

## Campaign metric logging

Every new command appends JSONL telemetry to:

- `/home/runner/work/_codex_/_codex_/.codex/campaign_metrics.jsonl`

Tracked events:

- `checkpoint_created`
- `checkpoint_restored`
- `task_route_recommended`
- `agent_chain_requested`
- `autofix_invoked`

## Rollout intent

These CLI entry points are the user-facing bootstrap for:

- Phase 10 checkpoint/resume adoption
- Phase 11 task-agent routing and security chaining
- Phase 11/12 CI auto-fix orchestration
- Phase 12 observability through campaign metric capture
