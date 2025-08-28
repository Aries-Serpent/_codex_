# Ephemeral (Single-Job) Self-Hosted Runners — Codex Toolkit

This repository includes a toolkit so ChatGPT Codex can launch a self-hosted runner that processes **one** job and then automatically de-registers.

## Secrets

Provide a GitHub PAT via one of these secrets (highest priority first):

1. Environment secret `CODEX_ENVIRONMENT_RUNNER` in environment `Aries_Serpent_codex_`
1. Repository secret `_CODEX_BOT_RUNNER`
1. Organization secret `_CODEX_ACTION_RUNNER`

Expose the chosen value to the shell as `GH_PAT`:

```bash
export GH_PAT="${CODEX_ENVIRONMENT_RUNNER:-${_CODEX_BOT_RUNNER:-${_CODEX_ACTION_RUNNER:-}}}"
```

## Label policy

`tools/label_policy.json` defines allowed labels and required base labels. Lint workflows locally:

```bash
pre-commit run label-policy-lint -a
```

## Pre-flight minimal labels

Compute a minimal label set for queued jobs on branch `0B_base_`:

```bash
GH_PAT=... python3 tools/preflight_minimal_labels.py --branch 0B_base_
```

If no queued jobs are found, the script falls back to `linux,x64,codex`.

## One-shot runner CLI

Launch an ephemeral runner, either with auto labels or explicit labels:

```bash
# Auto labels from queued jobs
GH_PAT=... tools/ephem_runner.sh --auto-labels --branch 0B_base_

# Explicit labels
GH_PAT=... tools/ephem_runner.sh --labels linux,x64,codex
```

### Flags

- `--owner`, `--repo`, `--branch` – override defaults `Aries-Serpent`, `_codex_`, `0B_base_`
- `--labels` – comma-separated labels
- `--auto-labels` – derive labels from queued jobs
- `--runner-version` – pin runner version (default `2.328.0`)
- `--work-dir` – working directory (default `_work`)
- `--name-prefix` – runner name prefix (default `codex-ephem`)
- `--no-disable-update` – allow self-update

## Notes

No GitHub Actions workflow files are modified. Runners register with `--ephemeral`, process one job, and disappear.
