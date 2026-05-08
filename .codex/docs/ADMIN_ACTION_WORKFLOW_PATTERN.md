# Admin Action Workflow Pattern

> **Version:** 1.0 · **Created:** 2026-05-08 · **Author:** copilot-swe-agent S861-cont

This document describes the reusable **Admin Action Notifier** pattern used in this
repository to track, surface, and auto-close gaps that require manual admin intervention
(token rotation, scope grants, secret updates, etc.).

---

## Overview

When a CI workflow requires an admin action (e.g. a token scope change that only a
GitHub organization owner can make), the standard pattern is:

```
workflow trigger (approval)
    → admin-action-<gap-id>.yml   (caller — gap-specific)
        → admin-action-notifier.yml  (engine — reusable)
            → scripts/ci/admin_action_probe.py (optional CLI)
```

1. **Probe** a GitHub API endpoint to check if the gap is still open.
2. If **open** → create or update a GitHub issue assigned to `@mbaetiong` with exact fix steps.
3. If **closed** (admin completed the action) → auto-close the issue.

The trigger fires on `workflow_run` of the auto-approve workflows — so every time the
Copilot agent's pending runs are approved, the gap status is re-checked automatically.

---

## Files

| File | Purpose |
|------|---------|
| `.github/workflows/admin-action-notifier.yml` | **Reusable engine** — accepts gap params via `workflow_call` inputs |
| `.github/workflows/admin-action-t03.yml` | **Caller** for T-03 (`security_events` scope on `CODEX_MASTER_KEY`) |
| `scripts/ci/admin_action_probe.py` | **CLI script** — probe + issue CRUD, usable locally or in any step |
| This file | Pattern documentation and gap registry |

---

## Gap Registry

| Gap ID | Title | Status | Caller Workflow | Probe Endpoint |
|--------|-------|--------|-----------------|----------------|
| T-03 | CODEX_MASTER_KEY missing `security_events` scope | 🔴 OPEN | `admin-action-t03.yml` | `GET /repos/.../code-scanning/alerts?per_page=1` |

Add new rows here when registering new gaps.

---

## How to Add a New Admin-Action Gap

### Step 1 — Identify the probe endpoint

Find a GitHub API endpoint that returns a clear success/failure signal:
- `200` = gap closed (action completed)
- `403` / `401` = gap still open (action not yet taken)

**Example probes:**
```
# security_events scope
GET /repos/OWNER/REPO/code-scanning/alerts?per_page=1

# actions:write scope (can dispatch workflows)
POST /repos/OWNER/REPO/actions/workflows/my.yml/dispatches  → 204

# org-level variable access
GET /orgs/ORG/actions/variables → 200
```

### Step 2 — Create the caller workflow

Create `.github/workflows/admin-action-<gap-id>.yml`:

```yaml
name: Admin Action — <GAP_ID> <Short Description>
# aais-cache: none  # No pip install — stdlib only

on:
  workflow_run:
    workflows:
      - "⚡ Auto-Approve Pending Workflow Runs"
      - "Trigger validations on approval"
    types: [completed]
  workflow_dispatch:

permissions:
  contents: read
  issues: write

jobs:
  check-<gap-id-lower>:
    name: Check <GAP_ID> gap
    uses: ./.github/workflows/admin-action-notifier.yml
    secrets: inherit
    with:
      gap_id: "<GAP_ID>"
      probe_url: "https://api.github.com/repos/${{ github.repository }}/<PATH>"
      expected_ok_status: "200"
      issue_title: "[<GAP_ID>] <Human-readable title>"
      issue_body_md: |
        ## ⚠️ Admin Action Required — <GAP_ID>

        ### What is blocked
        - <Description of what CI capability is missing>

        ### Root Cause
        <Explanation of why the gap exists>

        ### ✅ Fix Steps
        1. <Step 1 — specific click-by-click>
        2. <Step 2>
        3. **Verify** by re-running `<verification-workflow>.yml`

        ### After Completion
        This workflow will automatically detect the fix and close this issue.
      issue_label: "admin-action-required"
      assignee: "mbaetiong"
```

### Step 3 — Register in the gap registry

Add a row to the **Gap Registry** table above.

### Step 4 — Document in `ELEVATED_PRIVILEGES_TOKEN_REVIEW.md`

Add the gap to `docs/reference/ELEVATED_PRIVILEGES_TOKEN_REVIEW.md` with:
- Gap ID and description
- Token/scope affected
- Probe endpoint
- Fix steps

### Step 5 — Test the workflow

```bash
# Trigger manually
gh workflow run admin-action-<gap-id>.yml --repo Aries-Serpent/_codex_

# Or use the CLI script
GH_TOKEN=$CODEX_MASTER_KEY python3 scripts/ci/admin_action_probe.py \
  --gap-id <GAP_ID> \
  --probe-url "https://api.github.com/repos/Aries-Serpent/_codex_/<PATH>" \
  --repo Aries-Serpent/_codex_ \
  --probe-only
```

---

## Using the CLI Script Locally

```bash
# Probe only (exit 0=ok, 1=gap open, 2=inconclusive, 3=error)
GH_TOKEN=$CODEX_MASTER_KEY python3 scripts/ci/admin_action_probe.py \
  --gap-id T-03 \
  --probe-url "https://api.github.com/repos/Aries-Serpent/_codex_/code-scanning/alerts?per_page=1" \
  --probe-only

# Full run: probe + create/update issue
GH_TOKEN=$CODEX_MASTER_KEY python3 scripts/ci/admin_action_probe.py \
  --gap-id T-03 \
  --probe-url "https://api.github.com/repos/Aries-Serpent/_codex_/code-scanning/alerts?per_page=1" \
  --issue-title "[T-03] CODEX_MASTER_KEY missing security_events scope" \
  --fix-steps "Rotate CODEX_MASTER_KEY — add security_events scope. See docs/reference/ELEVATED_PRIVILEGES_TOKEN_REVIEW.md" \
  --repo Aries-Serpent/_codex_ \
  --close-if-ok

# Dry run (print actions without making API calls)
GH_TOKEN=$CODEX_MASTER_KEY python3 scripts/ci/admin_action_probe.py \
  --gap-id T-03 \
  --probe-url "..." \
  --issue-title "..." \
  --repo Aries-Serpent/_codex_ \
  --dry-run
```

---

## Trigger Matrix

The caller workflows fire in these situations ("when PR workflows are approved"):

| Trigger Workflow | When it fires | Why relevant |
|-----------------|---------------|--------------|
| `auto-approve-workflows.yml` completed | Every 5 min + on push + after Copilot session | All pending `action_required` runs just got unblocked |
| `trigger-on-approval.yml` completed | When a PR review is submitted with state=approved | Human explicitly approved — good time to re-probe gaps |
| `workflow_dispatch` | Manual on-demand | Agent or admin triggers directly for immediate check |

---

## Reusable Workflow Inputs Reference

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `gap_id` | string | ✅ | — | Short identifier e.g. `T-03` |
| `probe_url` | string | ✅ | — | Full GitHub API URL to GET-probe |
| `expected_ok_status` | string | ❌ | `200` | HTTP status meaning gap is CLOSED |
| `issue_title` | string | ✅ | — | GitHub issue title (must be unique per gap) |
| `issue_body_md` | string | ✅ | — | Markdown body for the issue |
| `issue_label` | string | ❌ | `admin-action-required` | Label to apply |
| `assignee` | string | ❌ | `mbaetiong` | GitHub login to assign |

**Outputs:**
| Output | Description |
|--------|-------------|
| `scope_ok` | `true` / `false` / `unknown` |
| `issue_number` | GitHub issue number created/updated (empty if none) |

---

## Exit Codes (CLI script)

| Code | Meaning |
|------|---------|
| `0` | Gap closed — probe returned expected status |
| `1` | Gap open — probe returned 401/403 |
| `2` | Inconclusive — unexpected HTTP status |
| `3` | Script error (missing args, auth failure, etc.) |
