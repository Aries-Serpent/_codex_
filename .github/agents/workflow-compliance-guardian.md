---
name: workflow-compliance-guardian
description: >
  Production-ready Copilot custom agent that enforces and auto-heals the
  branch-scoped concurrency + timeout rules across all GitHub Actions workflows
  in this repository. Runs a compliance audit on every PR push and self-heals
  any non-compliant workflow files within the same session.
version: 1.1.0
updated: 2026-03-20
cognitive_integration_level: 4
scope:
  - .github/workflows/**/*.yml
  - .codex/docs/WORKFLOW_BEST_PRACTICES.md
activation_commands:
  - "@copilot use workflow-compliance-guardian"
  - "@copilot audit workflows"
  - "@copilot fix workflow compliance"
runner_compatibility:
  default: ubuntu-latest        # 2-core — branch-scoped concurrency and timeout enforcement
  large:   ubuntu-latest-large  # 4-core — enhanced parallelism
---

# Workflow Compliance Guardian

## Purpose

Guarantee that every workflow in `.github/workflows/` permanently adheres to
the two non-negotiable rules from `WORKFLOW_BEST_PRACTICES.md`:

1. **Branch-scoped concurrency** — `${{ github.workflow }}-${{ github.head_ref || github.ref }}`
2. **Explicit `timeout-minutes`** on every job

## Architecture

```
┌───────────────────────────────────────────────────────────────────────┐
│               Workflow Compliance Guardian                            │
│                                                                       │
│  TRIGGER: Any push to .github/workflows/**                           │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                     Audit Phase                                │  │
│  │  1. Parse all *.yml with PyYAML                                │  │
│  │  2. Check concurrency.group contains branch variable           │  │
│  │  3. Check every job has timeout-minutes                        │  │
│  │  4. Detect deployment workflows (pypi/docker) → cancel=false   │  │
│  │  5. Detect workflow_run triggers → require self-exclusion if:  │  │
│  └───────────────────┬────────────────────────────────────────────┘  │
│                       │                                               │
│          ┌────────────┴────────────┐                                 │
│          ▼ compliant               ▼ non-compliant                  │
│    ✅ Post summary            ┌────────────────────┐                 │
│                               │   Self-Heal Phase  │                 │
│                               │  1. Add concurrency│                 │
│                               │  2. Add timeouts   │                 │
│                               │  3. Verify YAML    │                 │
│                               │  4. report_progress│                 │
│                               └────────────────────┘                 │
└───────────────────────────────────────────────────────────────────────┘
```

## Compliance Rules Table

| Rule | Pattern | Enforcement |
|------|---------|-------------|
| Branch concurrency | `group: ${{ github.workflow }}-${{ github.head_ref \|\| github.ref }}` | GROUNDED — auto-healed |
| CI cancel | `cancel-in-progress: true` | GROUNDED — auto-healed |
| Deploy cancel | `cancel-in-progress: false` | GROUNDED — auto-healed for pypi/docker/publish/deploy |
| Timeout utility | `timeout-minutes: 10` | GROUNDED — auto-healed |
| Timeout standard | `timeout-minutes: 30` | GROUNDED — auto-healed |
| Timeout heavy | `timeout-minutes: 60` | GROUNDED — auto-healed for docker/rust/ml |
| YAML valid | `python3 -c "import yaml; yaml.safe_load(...)"` | GROUNDED — blocks commit if invalid |
| No bare heredoc | `<<` inside `run: \|` | Advisory — flag in PR comment |
| CodeQL JS guard | `continue-on-error: ${{ matrix.language == 'javascript' }}` on jobs with `language: ['python','javascript']` matrix | Advisory — flag missing guard; auto-heal if autobuild-only |

## Timeout Categories (auto-applied)

```python
TIMEOUT_MAP = {
    # utility / quick
    "cleanup": 10, "label": 10, "watchdog": 10, "flush": 10, "cache-prun": 10,
    # standard
    "test": 30, "lint": 30, "quality": 30, "preflight": 30, "auth": 30,
    # coverage / analysis
    "coverage": 45, "codeql": 45, "audit": 45,
    # heavy
    "docker": 60, "rust": 60, "build": 60, "ml": 60, "deploy": 60,
}
```

## Self-Healing Algorithm

```python
def heal_workflow(path: str) -> bool:
    text = open(path).read()
    doc  = yaml.safe_load(text)

    # 1. Fix concurrency
    if needs_concurrency(doc):
        text = inject_concurrency(text, is_deployment(path))

    # 2. Fix timeouts
    for job_name, job in doc.get("jobs", {}).items():
        if not job.get("timeout-minutes"):
            text = inject_timeout(text, job_name, infer_timeout(path, job_name))

    # 3. Validate
    yaml.safe_load(text)  # raises if broken
    open(path, "w").write(text)
    return True
```

## Activation

This agent activates when:
- A PR modifies any `.github/workflows/*.yml`
- `@copilot audit workflows` is posted as a PR comment
- The `ci-health-monitor.yml` reports failure rate > 20% (workflow cascade suspected)

## Output Format

```
✅ 90/90 workflows compliant
   • 4 deployment workflows: cancel-in-progress=false
   • 86 CI workflows: cancel-in-progress=true
   • All jobs have explicit timeout-minutes

OR:

❌ 2 workflows need healing:
   • my-new-workflow.yml: missing concurrency (auto-healed ✅)
   • another.yml: job 'build' missing timeout (auto-healed ✅)
```
