# CI Failure Tracking Log

Tracks recurring CI failure patterns, root causes, and resolutions across all sessions.

## Purpose

This log is referenced by `.github/workflows/pre-flight-validation.yml` as a quick-reference
resource when rescue-comment jobs fire. For per-session remediation history, see:

- [`docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`](../docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md)
- [`docs/ci/CI_FAILURE_ANALYSIS.md`](../docs/ci/CI_FAILURE_ANALYSIS.md)
- [`.codex/CI_FAILURE_PATTERN_ANALYSIS.md`](.codex/CI_FAILURE_PATTERN_ANALYSIS.md)

## Common Patterns

| Pattern | Root Cause | Resolution |
|---------|-----------|------------|
| `end-of-file-fixer` | Workflow YAML missing trailing newline | Add `\n` at end of file |
| `check-cross-references` | Internal link targets missing | Create file or update reference |
| `Deferral Language Gate` | PR body/comment contains deferral phrase | Add `EXEMPTION_PATTERNS` or remove phrase |
| `detect-secrets` | New hex string in docs without pragma | Add `# pragma: allowlist secret` |

## Last Updated

2026-03-27 — S230: Created to satisfy `check-cross-references` hook in `pre-flight-validation.yml`.
