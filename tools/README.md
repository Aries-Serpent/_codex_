# Tools Overview

This directory contains small, local-only utilities to standardize message gating and structural checks.
Also see: `docs/ops/selection_guard.md` for selection verification.

## Commands

### Validate Fences
```bash
python tools/validate_fences.py
```

Validates balanced fences, prohibits mixed fence types within a block, and reports failures with file:line hints.

### Evaluator
```bash
python tools/codex_evaluator.py --rules manifests/codex_eval_rules.v3.json --input samples/assistant_message_summary.sample.json
```

Scores messages/summaries against the rubric, returning non-zero on hard fails (e.g., CI cues).

### Selection Guard
```bash
python tools/selection_guard.py --rules manifests/selection_guard_rules.json --input summary-02.json --selected 3
```
Checks that the **chosen** candidate includes the required docs surface + guardrails files; prints a ranked table.

### CLI Wrapper

```bash
python tools/cli/codex_tools.py gate --rules manifests/codex_eval_rules.v3.json --input samples/assistant_message_summary.sample.json
```

Wraps the evaluator with helpful CLI ergonomics.
