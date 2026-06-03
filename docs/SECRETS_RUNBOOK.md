# Secrets Runbook

> **Last Updated**: 2026-06-03T18:02:00Z | **Maintainer**: @mbaetiong
> Full inventory: [`docs/SECRETS_AND_ENVIRONMENT_VARIABLES.md`](./SECRETS_AND_ENVIRONMENT_VARIABLES.md)

---

## Purpose

Document how to store, rotate, and audit repository secrets and environment variables. Covers all 106 tracked variables (13 env, 70 repo vars, 3 env secrets, 7 repo secrets, 13 org secrets).

---

## Core Principles

- **Never commit secrets** to the repository.
- **Token chain for all write ops**: `CODEX_MASTER_KEY` → `CODEX_BACKUP_KEY` → `github.token`
- **Use least privilege** — scope API keys to test environments where possible.
- Use `report_progress` tool (never `git push`) for all commits.
- `DISABLE_SECRET_FILTER` must **never** be set to `true` in production.

---

## 🔴 Immediate Actions Required (As of 2026-06-03)

The following org secrets are 5+ months old and past their recommended rotation window:

| Secret | Age | Action |
|--------|-----|--------|
| `CODECOV_TOKEN` | 5 months | Rotate via [Codecov dashboard](https://app.codecov.io) |
| `HF_TOKEN` | 5 months | Rotate via [HuggingFace settings](https://huggingface.co/settings/tokens) |
| `NPM_TOKEN` | 5 months | Rotate via [npmjs.com](https://www.npmjs.com/settings) |
| `PYPI_TOKEN` | 5 months | Rotate via [PyPI account](https://pypi.org/manage/account/token/) |
| `_CODEX_ACTION_RUNNER` | 5 months | Rotate via GitHub Actions runner settings |

---

## Rotation Procedures

### CODEX_MASTER_KEY / CODEX_BACKUP_KEY / CODEX_ADMIN_KEY

1. Generate new Fernet key:
   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```
2. Navigate to **GitHub → Organization Settings → Secrets and variables → Secrets**
3. Update `CODEX_MASTER_KEY` (and separately `CODEX_BACKUP_KEY`, `CODEX_ADMIN_KEY`)
4. Verify the next CI run succeeds (any workflow using write ops)
5. Record rotation in `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`

**Rotation frequency**: Every 90 days  
**Emergency rotation**: Immediately if compromised — use `AGENT_KILL_SWITCH=1` to halt all agents first

### GitHub App Keys (_GITHUB_APP_*)

1. Navigate to **GitHub → Organization Settings → GitHub Apps → `_codex_` app → Generate new private key**
2. Download the new `.pem` file
3. Update `_GITHUB_APP_PRIVATE_KEY` in org secrets with the new PEM content
4. If rotating client secret: **Edit → Rotate secret** in the GitHub App settings
5. Update `_GITHUB_APP_CLIENT_SECRET` in org secrets
6. Trigger a test `actions/create-github-app-token@v1` workflow to verify

**Rotation frequency**: Every 90 days

### OPENAI_API_KEY / RAG_OPENAI_KEY

1. Navigate to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create a new key (do not delete old key yet)
3. Update the secret in GitHub repository secrets
4. Run a test workflow (`test-rag.yml`) to verify connectivity
5. Delete the old key from OpenAI dashboard

**Rotation frequency**: Every 90 days

### Runner Token (CODEX_RUNNER_TOKEN / _CODEX_BOT_RUNNER / _CODEX_ACTION_RUNNER)

1. Navigate to **GitHub → Settings → Actions → Runners**
2. Re-register the runner with a new token
3. Update the environment secret `CODEX_RUNNER_TOKEN` and repo secret `_CODEX_BOT_RUNNER`
4. For org-level `_CODEX_ACTION_RUNNER`: update in **Organization Settings → Actions → Runners**

**Rotation frequency**: Every 90 days or on runner recycle

---

## Emergency: All-Agent Halt

To immediately halt all autonomous agent activity:

1. Set `AGENT_KILL_SWITCH` repository variable to `1`
2. All agent runners will check this flag and abort
3. After investigation, reset to `0` to re-enable

---

## Enabling Live Integration Tests

1. Add required provider secrets: `OPENAI_API_KEY`, `HF_TOKEN`
2. Set `ENABLE_LIVE_TESTS` repository variable to `true` (for authorized branches only)
3. Trigger `integration-gated.yml` workflow manually
4. Monitor for billing alerts via provider dashboards
5. Disable live tests after validation: reset `ENABLE_LIVE_TESTS` to `false`

---

## Audit & Monitoring

- **GitHub Audit Log**: Settings → Security → Audit log → filter by "secret"
- **CI Failure Rate**: Monitor `CODEX_CI_FAILURE_RATE` variable (threshold: `CODEX_CI_FAILURE_THRESHOLD = 10.0`)
- **Last Green SHA**: `CODEX_CI_LAST_GREEN_SHA` — updated automatically by CI agent
- **Accountability**: `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`
- **Usage Matrix**: `.codex/security/secrets_usage_matrix.json`

---

## Setting New Variables

### Repository Variables
**GitHub UI**: Settings → Secrets and variables → Actions → Variables → **New repository variable**

Naming conventions (from `.codex/CRITICAL_REPOSITORY_VARIABLES.md`):
- `CODEX_*` — repository-specific configuration
- `COGNITIVE_*` — cognitive brain system
- `COPILOT_*` — Copilot agent settings
- `AGENT_*` — agent runner controls

### Environment Variables (Aries_Serpent_codex_)
**GitHub UI**: Settings → Environments → `Aries_Serpent_codex_` → Variables → **Add variable**

These are injected into the Copilot sandbox. Sensitive section at `copilot-setup-steps.yml:141-147` must use `run: |` (pipe) with brace-free shell syntax.

### Agents Settings Page
**GitHub UI**: `https://github.com/Aries-Serpent/_codex_/settings/variables/agents`

Must add (currently only firewall defaults shown):
- `COPILOT_AGENT_MAX_AUTONOMY_LEVEL` = `D`
- `COPILOT_AGENT_AUTH_ENABLED` = `true`
- `COPILOT_AGENT_SESSION_RESTORE_ENABLED` = `true`
- `COPILOT_AGENT_PREFLIGHT_RULES` = _(copy from repo var)_
- `COPILOT_WEC_SELECTION_MATRIX` = _(copy from repo var)_

---

## References

- Full inventory: [`docs/SECRETS_AND_ENVIRONMENT_VARIABLES.md`](./SECRETS_AND_ENVIRONMENT_VARIABLES.md)
- Rotation schedule: `.codex/security/rotation_schedule.md`
- Agency policy: `.codex/CODEBASE_AGENCY_POLICY.md`
- PR lifecycle spec: `docs/ci/PR_LIFECYCLE.md`
