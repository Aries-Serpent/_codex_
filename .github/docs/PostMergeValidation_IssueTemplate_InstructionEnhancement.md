# [InstructionEnhancement]: Post-merge Validation Issue Form – Reserved YAML Keywords Fix
> Generated: 2025-11-14 20:31:28 UTC | Author: mbaetiong

This note documents and resolves the GitHub Issue Form error: “Config contains reserved YAML keywords as keys.”

Root cause: The template used keys that conflict with YAML reserved scalars (e.g., `on`, `yes`, `no`, `true`, `false`, `null`, `~`) or non-Issue-Forms keys at the top level (e.g., `on:` used in GitHub Actions, not valid in Issue Forms). GitHub Issue Forms require a specific schema and disallow reserved keywords as mapping keys.

## What changed

- Replaced the template with a valid Issue Forms schema (see `.github/ISSUE_TEMPLATE/post-merge-validation-optimized.yml`).
- Ensured no mapping key uses YAML-reserved scalars.
- Kept all identifiers (`id:`) and labels lowercase, hyphenated, and non-reserved.
- Added `.github/ISSUE_TEMPLATE/config.yml` to guide authors to the correct form.

## Quick rules to avoid this error

| Rule | Do | Don’t |
|---|---|---|
| Use only Issue Forms top-level keys | `name`, `description`, `title`, `labels`, `assignees`, `body` | `on`, `jobs`, `steps`, `runs-on` (Actions-only keys) |
| Avoid reserved YAML scalars as keys | Use safe keys like `workflow_run_url`, `commit_sha` | Keys named `on`, `yes`, `no`, `true`, `false`, `null`, `~` |
| Quote only when necessary | Quote strings with special characters in values | Don’t rely on quoting reserved keys to bypass schema |
| Use valid body items | `type`: `markdown`, `input`, `textarea`, `dropdown`, `checkboxes` | Non-supported `type` values |
| Keep IDs simple | lowercase, hyphen/underscore separated | Spaces, mixed case, or reserved words |

Common YAML reserved scalars to never use as mapping keys (unquoted or quoted) in Issue Forms:

| Reserved | Also treated as |
|---|---|
| `on`, `off` | boolean-like |
| `yes`, `no`, `y`, `n` | boolean-like |
| `true`, `false` | booleans |
| `null`, `~` | null |

## Validation checklist

- The template opens at: New issue → “Post-merge validation report”.
- Submission renders all fields and validations:
  - Required: workflow run URL, merge commit SHA, failing job, failure summary.
  - Optional: logs snippet, quick actions, additional context.
- The error “Config contains reserved YAML keywords as keys” no longer appears.

## References

- GitHub Issue Forms schema (supported keys and items)
- GitHub Actions workflow is separate; do not mix `on:` or `jobs:` in issue form templates.

## Copilot integration

- Copilot Agents can auto-populate `commit_sha` and `workflow_run_url` when invoked from a workflow comment or PR action.
- Keep IDs stable to enable tooling.
