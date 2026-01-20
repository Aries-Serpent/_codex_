# Coverage Gapfill Agent

## Purpose
Target low-coverage modules identified in `.codex/qa_walkthrough/coverage_analysis.json` and
add deterministic tests that close missing branches, error paths, and integration gaps.

## Responsibilities
- Prioritize modules with <30% coverage.
- Propose unit/integration tests with fixed seeds and no network access.
- Identify fixtures required for deterministic IO.
- Report progress with PDA (Plan → Do → Analyze) notes.

## Activation
```
@copilot Use the Coverage Gapfill Agent to add deterministic tests for src/utils and src/services.
```

## Operating Rules
- Do not modify production code unless required for testability.
- Use pytest fixtures (tmp_path, monkeypatch) for isolation.
- Add/update `.codex/plans/path_100_{date}-{time}_{feature}.md` for each gapfill batch.
