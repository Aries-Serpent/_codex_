# Tools Overview

This directory contains small, local-only utilities to standardize message gating and structural checks.
Also see: `docs/ops/selection_guard.md` for selection verification.

## Commands

### Validate Fences
```bash
python tools/validate_fences.py
```text

Validates balanced fences, prohibits mixed fence types within a block, and reports failures with file:line hints.

### Evaluator
```bash
python tools/codex_evaluator.py --rules manifests/codex_eval_rules.v3.json --input samples/assistant_message_summary.sample.json
```text

Scores messages/summaries against the rubric, returning non-zero on hard fails (e.g., CI cues).

### Selection Guard
```bash
python tools/selection_guard.py --rules manifests/selection_guard_rules.json --input summary-02.json --selected 3
```text
Checks that the **chosen** candidate includes the required docs surface + guardrails files; prints a ranked table.

### CLI Wrapper

```bash
python tools/cli/codex_tools.py gate --rules manifests/codex_eval_rules.v3.json --input samples/assistant_message_summary.sample.json
```text

Wraps the evaluator with helpful CLI ergonomics.

### Validate Status Reports

```bash
python tools/validate_status_report.py reports/daily/_codex_status_update-Previous Cycle-11-04.md
```text

Validates status update markdown files against the template schema to ensure all required sections are present and properly formatted.

### Extract Validation Errors

```bash
python tools/extract_validation_errors.py reports/daily/_codex_status_update-Previous Cycle-11-04.md
```text

Validates a status report and automatically creates an `error-<report_name>.md` file in the same directory listing all incomplete or incorrect aspects. The error file includes:
- Detailed validation errors
- Missing required sections
- Resolution steps
- Complete checklist of required sections

Use `--force` to overwrite an existing error file.
