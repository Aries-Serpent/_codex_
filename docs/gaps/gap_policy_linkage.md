# Gap Policy Linkage

This document explains how the Gap Registry fields and task sequence steps
are intended to align with higher-level policies such as hardship maps and
pruning rules.

## Registry fields

The `codex_gap_registry.yaml` file contains, for each gap:

- `id`: Stable identifier, used for filenames and references.
- `capability`: High-level area (tokenization, training, data_handling, etc.).
- `location`: Suggested code/test locations (optional).
- `description`: Human-readable description of the gap.
- `status`: One of:
  - `missing`
  - `stubbed`
  - `partial`
  - `implemented`
- `risk_level`: Optional indicator such as `low`, `medium`, `high`.
- `yaml_phase_step`: Optional link to a specific `phase.step` id in
  `codex_task_sequence.yaml`.
- `ml_test_categories`: Optional list of categories from the ML Test Score
  mapping.
- `last_seen_in_audit`: The audit date where this gap was last observed.
- `notes`: Free-form text.

## Hardship / risk integration

A separate hardship or risk metadata file (e.g. `codex_hardship.yaml`) can
be used to annotate gaps with additional context such as:

- Rationale for high risk level.
- Operational constraints (e.g. cannot change public API).
- Dependencies on external services.

The script `tools/codex_gap_registry.py` can load this metadata and apply it
to the `risk_level` and `notes` fields.

## Pruning rationale

"Pruning" in this context means deciding that a gap is intentionally not
going to be implemented in the near term. This should only happen when:

- The gap is out of scope for the current milestone.
- The implementation would introduce unacceptable complexity or risk.
- There is no clear owner for the work, and it is not critical.

When a gap is pruned, it should:

1. Have a `status` that reflects its state (e.g. `missing` or `stubbed`).
2. Include notes explaining **why** it is not being implemented now.
3. Optionally have a `risk_level` adjusted to reflect the decision.

The task sequence Phase 4 ("Controlled Pruning") is responsible for making
these decisions explicit, not for automatically changing registry entries.

## Error questions and feedback loop

Whenever the task sequence runner encounters an error, it appends a
structured block to `codex_error_questions.md`. These blocks are intended
to be fed back into ChatGPT @codex to:

- Diagnose failures.
- Suggest implementation strategies.
- Decide whether to:
  - Fix the underlying implementation gap, or
  - Prune/defer the gap with proper rationale.

This closes the loop between:
- Automated tools (registry, YAML, runner),
- Human review and policy decisions, and
- AI-assisted implementation and design discussions.
