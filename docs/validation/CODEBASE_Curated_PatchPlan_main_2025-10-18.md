# [Plan]: Curated Patch Sets Roadmap — Aries-Serpent/_codex_ (main @ 3eb0094)
> Generated: 2025-10-18 05:38:58 UTC | Author: mbaetiong
Roles: [Audit Orchestrator], [Capability Cartographer] Energy: 5

Alignment: Incorporates recent P0 packaging changes (MANIFEST, build script, TOML parse guard, tests). This update enumerates the next diffs to implement and completes all remaining P1/P2 items with doc-first, low-churn changes.

## A) Deltas Landed (Reference)
| Patch | Area | Outcome |
|------|------|---------|
| PS-1g/1h | Packaging normalization + parse guard | pyproject normalizer safer; MANIFEST tightened; wheel builder script; docs/tests added |

## B) Next Diffs To Implement (Now)
| Patch Set | Priority | Contents |
|-----------|----------|----------|
| PS-2 | P1 | tests/plugins/test_list_plugins_cli_json_stdout_only.py to enforce stdout-only JSON |
| PS-3 | P1 | docs/training/Checkpointing_Surfaces.md (canonical vs legacy mapping) |
| PS-4 | P1 | tokenization/* legacy shims emit DeprecationWarning and re-export from codex_ml.tokenization.* |
| PS-5 | P1 | docs/training/Evaluation_CLI.md (contracts and examples) |
| PS-6 | P1 | docs/training/Distributed_Minimal_Hooks.md (env-gated behavior) |
| PS-7 | P1 | docs/plugins/Plugin_Registry.md and docs/developer/Plugin_Registry_CLI.md |
| PS-8 | P2 | docs/validation/{Traversal_Workflow.md,Usage_Guide.md}, templates/audit/capability_matrix.md.j2 |

## C) Validation Matrix
| PS | Command | Expected |
|----|---------|----------|
| PS-2 | python -m codex_ml.cli.list_plugins --format json | exit 0; stderr empty; valid JSON |
| PS-3 | pytest tests/checkpointing -q | No regressions (doc-only) |
| PS-4 | pytest tests/interfaces -q | No behavior change; deprecation warnings allowed |
| PS-5 | pytest tests/eval -q | Contracts aligned (doc-only) |
| PS-6 | pytest tests/distributed -q | No-op + env opt-in stable |
| PS-7 | pytest tests/plugins -q | JSON schema/flows stable |
| PS-8 | make space-audit-fast | S1,S3,S4,S6 run; template hash embedded |

## D) Risks & Mitigations
- MANIFEST src-only graft may exclude needed top-level packages. If runtime modules live outside src/, re-add targeted graft lines (training/, tokenization/, etc.) in MANIFEST.in.
- Tokenization shims: ensure optional deps are guarded in canonical modules; shims only re-export.
- CLI stderr strictness: tests guide consistency; adjust CLI only if failures observed.

## E) Follow-up
- If PS-2 test fails, patch codex_ml/cli/list_plugins.py to suppress stderr in JSON mode.
- Consider adding constraints/extra marker for tokenization extras in pyproject extras if missing.

*End of Plan*
