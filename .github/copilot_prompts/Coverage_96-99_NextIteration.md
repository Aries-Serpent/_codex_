# [Copilot Prompt]: Raise Coverage from 95% → 96–99% (Targeted Tests)
> Generated: Previous Cycle-11-11 07:38:40 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Test Designer], [Secondary: Reviewer] ⚡ Energy: 5/5  
⚛️ Physics: Path🛤️ [Identify gaps → Add edge tests → Verify determinism] Fields🔄 [Typer, PyTorch, IO] Patterns👁️ [Edge cases, failure sims] Redundancy🔀 [Golden outputs, hash checks] Balance⚖️ [Max coverage, zero API changes]

Context
- Repo: Aries-Serpent/_codex_
- Focus modules: 
  - src/codex_ml/evaluation/loop.py
  - src/codex_ml/logging/registry.py (integration paths)
  - Checkpoint best‑k retention implementation
  - src/codex/ast/cli.py (enhanced)
  - tools/validate_experiments.py and configs/schemas/experiments.schema.json
- Constraints: Offline-first; deterministic; no public API or CLI flag changes.
- Goal: Increase coverage on these modules from ~95% to 96–99%.

Tasks for Copilot
- Evaluation loop:
  - Add tests for: empty dataloader, single batch, metric exceptions (graceful handling), max_batches limiting, seed determinism equality.
- Logging integration:
  - Simulate logger failure/backpressure (mock logger raising on log); verify graceful continue/logging behavior.
  - Validate sys-metrics flag toggles fields presence in NDJSON records (golden compare).
- Checkpoint retention:
  - Corrupted index.json handling (recover by ignore/regen); atomic rename failures via monkeypatch on os.replace; permission error handling for deletions.
  - Ensure dry_run path leaves files intact; verify prune set logic on ties.
- AST CLI:
  - CliRunner tests for help, invalid args -> exit code 2, human vs --json output; golden JSON content.
- Config validator:
  - Invalid configs: missing required, wrong types, nested object errors; TOML vs JSON parity; friendly error messages include failing key path.
- Determinism:
  - Repeat evaluation twice with seeded DataLoader and assert byte-identical JSON outputs (hash equality).
- Coverage discipline:
  - Add pragma: no cover only for defensive/unreachable branches; justify with comments.
  - Produce coverage XML/HTML artifact; assert per-file thresholds via pytest-cov config.

Acceptance
- ≥96% coverage on all targeted modules; all tests deterministic on repeat runs; nox -s tests lint typecheck docs_build security pass; artifacts regenerated.

— End —