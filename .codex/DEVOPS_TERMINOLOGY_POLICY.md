# DevOps Terminology Policy

**Version**: 1.1.0  
**Status**: Active  
**Effective Date**: 2026-01-05  
**See also**: [CODEBASE_AGENCY_POLICY.md](CODEBASE_AGENCY_POLICY.md)

This document defines terminology conventions for DevOps and agent operations in this
repository. Consistent terminology ensures unambiguous communication between human
maintainers and AI agents across sessions.

---

## Mandatory Terminology Table

All agents and contributors MUST use the terms in the **Use** column. Using terms
in the **Avoid** column is a policy violation.

| Concept | ✅ Use | ❌ Avoid | Notes |
|---------|-------|---------|-------|
| Work before a commit is finalized | **pre-commit** | "before the week", "before Friday" | Time-based language is prohibited |
| Work after a commit is recorded | **post-commit** | "after the deployment" | Refer to commit, not calendar |
| A logical unit of agent work | **session** | "sprint", "iteration cycle" | One PR may have multiple sessions |
| A recorded version control snapshot | **commit** | "check-in", "save" | Use git terminology |
| The set of changes in a PR | **patch** | "diff set", "change bundle" | When referring to the unit of review |
| The default branch | **main** | "master", "trunk" | Repository uses `main` |
| An automated workflow run | **CI run** or **workflow run** | "build", "pipeline run" | Matches GitHub Actions terminology |
| A workflow that passed | **green** | "successful", "passing build" | Consistent with GitHub status indicators |
| A workflow that failed | **red** or **failed** | "broken", "busted" | Avoid informal language |
| A workflow awaiting approval | **action_required** | "blocked", "stuck" | Matches GitHub API `conclusion` field |
| Automated code quality checks | **linting** | "style checks", "code review bots" | Covers ruff, black, mypy |
| A non-blocking finding | **warning** | "soft error", "advisory" | Validator uses `warnings` vs `errors` |
| A blocking finding | **error** | "failure", "hard error" | Use consistently with tool output |
| Documentation broken link | **broken link** | "dead link", "404" | Use with validate-links.py output |
| An agent's work unit in a session | **task** | "ticket", "story", "card" | No project management overhead |
| Planned but not yet created | **stub** | "placeholder", "skeleton file" | Stubs must have meaningful content |
| Planned but deferred | **DRQ** (Deep Research Question) | "TODO", "FIXME" | Follow DRQ process in Agency Policy |
| A policy deviation with justification | **documented exception** | "workaround", "hack" | Must be logged in Agency Policy format |

---

## Time-Based Language (PROHIBITED)

The following time-based terms are **PROHIBITED** in commit messages, PR comments,
code comments, and documentation because they become misleading after the moment passes:

| ❌ Prohibited | ✅ Replacement |
|---|---|
| "will be fixed next week" | "tracked in DRQ-XXX" |
| "temporary fix until Friday" | "stub pending DRQ-XXX" |
| "coming soon" | "planned in Phase N" |
| "after the deployment" | "post-commit N" |
| "before the release" | "pre-commit to release branch" |
| "eventually" | provide a DRQ or remove |
| "later" | provide a DRQ or remove |
| "TODO" (without ticket) | `# DRQ-XXX: interim fix pending research` |

---

## Branch and Commit Naming

| Artifact | Convention | Example |
|----------|-----------|---------|
| Feature branch | `copilot/<short-description>` | `copilot/fix-link-validation` |
| Hotfix branch | `hotfix/<issue-number>-<description>` | `hotfix/3365-broken-links` |
| Commit message | `<type>: <what> [<scope>]` | `fix: resolve 14 broken doc links [docs/ci]` |
| PR title | `<type>(<scope>): <imperative description>` | `fix(docs): resolve broken links in ci/` |

**Commit types**: `fix`, `feat`, `docs`, `chore`, `refactor`, `test`, `ci`, `style`

---

## Agent Operational Terms

| Term | Definition |
|------|-----------|
| **session** | A single continuous agent invocation against a PR (one `@copilot` trigger) |
| **phase** | A named group of related tasks within a session or across sessions |
| **self-review iteration** | One complete pass through the assess checklist |
| **cognitive brain** | The persistent knowledge and status system in `.codex/cognitive_brain/` |
| **memory fact** | A stored fact in the agent memory system (via `store_memory`) |
| **DRQ** | Deep Research Question — a deferred investigation with formal documentation |
| **pattern** | A recurring code or process issue catalogued with ID (e.g., P-034) |
| **learning** | A new insight catalogued with ID (e.g., L021) from a session |
| **stub** | A minimal file created to resolve a broken link, with intent to expand |
| **pre-flight** | Automated checks run before CI to catch common issues early |

---

## CI/CD Specific Terms

| Term | Definition | Source |
|------|-----------|--------|
| `action_required` | Workflow needs approval to proceed (not a failure) | GitHub API `conclusion` |
| `exit 0` | Successful script completion | Shell convention |
| `exit 1` | Script found errors that block merging | Shell convention |
| `STRICT_MODE` | Env var that forces `--fail-on-errors` for validate-links.py | workflow-link-validation.yml |
| `fail_on_errors` | CLI flag for validate-links.py to exit 1 on broken links | .github/scripts/validate-links.py |
| `link-validation-report.json` | JSON artifact produced by link validation workflow | workflow-link-validation.yml |
| `errors_count` | Number of broken links found (must be 0 to merge) | link-validation-report.json |
| `warnings_count` | Number of non-blocking issues (informational) | link-validation-report.json |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-05 | Initial creation |
| 1.1.0 | 2026-02-25 | Full terminology table, time-based language prohibition, CI/CD terms |
