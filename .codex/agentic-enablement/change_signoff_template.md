# Change Sign-Off Template — Agentic Enablement
> Template version: 1.0.0 | Repo: Aries-Serpent/_codex_
> Purpose: Human approval gate for any mutating action arising from the agentic-enablement investigation.
> Policy: Per `.codex/CODEBASE_AGENCY_POLICY.md` — no autonomous mutation without explicit signed approval.

---

## Instructions

1. Copy this template for each proposed change batch.
2. Fill in all fields. Leave no field blank — write "N/A" if not applicable.
3. Sign with your GitHub username and a UTC timestamp.
4. Commit the signed copy to `.codex/agentic-enablement/signoffs/YYYY-MM-DD-<slug>.md`.
5. Reference the signoff file in the PR description before Copilot is instructed to implement.

---

## Signoff Record

| Field | Value |
|---|---|
| **Signoff ID** | `SIGNOFF-YYYY-MM-DD-NNN` |
| **Signer GitHub username** | `@` |
| **Signed at (UTC)** | `YYYY-MM-DDTHH:MM:SSZ` |
| **PR / Issue reference** | `#` |
| **Commit SHA authorizing this** | *(leave blank if pre-implementation)* |

---

## Proposed Change

| Field | Value |
|---|---|
| **Title** | |
| **Affected files** | *(list each file path)* |
| **Risk level** | Critical / High / Medium / Low |
| **Remediation type** | FIX / MIGRATE / REMOVE |
| **References top_risks.md item(s)** | Risk N, Risk M, … |

---

## Change Description

*(2–5 sentences explaining what will change, why, and what the expected outcome is.)*

---

## Verification Steps

*(Exact commands the implementer must run and expected output to confirm the fix is correct.)*

```bash
# Example:
git ls-files .codex/agent_auth_session.json   # must return empty
grep autonomous_actions_enabled .codex/autonomous_agent.yaml  # must show: false
```

---

## Rollback Plan

*(How to undo this change if it causes problems. Include exact git commands or variable resets.)*

```bash
# Example rollback:
git revert <commit-sha>
# Re-set repo variable:
gh variable set COPILOT_AGENT_AUTH_BYPASS_TOOLS --body "" --repo Aries-Serpent/_codex_
```

---

## Approval Checklist

- [ ] I have read `top_risks.md` entry for all referenced risks.
- [ ] I confirm this change does NOT expose new secrets or tokens.
- [ ] I confirm this change does NOT increase the attack surface.
- [ ] I confirm rollback is feasible and documented above.
- [ ] I confirm CI checks (`validate.yml`, `codeql-analysis.yml`) must pass before merge.
- [ ] I authorize Copilot to implement this change as described.

---

## Signer Declaration

> By committing this file, **@{SIGNER}** at **{TIMESTAMP}** explicitly authorizes the changes described above in the Aries-Serpent/_codex_ repository. This constitutes the human approval required by `.codex/CODEBASE_AGENCY_POLICY.md` for autonomous agent mutations.

---

## Stage Gate

| Stage | Signoff Required? | Notes |
|---|---|---|
| Stage 0 (read-only) | No | Discovery only |
| Stage 1 (critical hardening) | **Yes — this template** | Required before any code change |
| Stage 2 (simulation) | **Yes — this template** | Required before enabling sandbox workflow |
| Stage 3 (canary) | **Yes — this template** | Required before enabling `agent-canary` environment |
| Stage 4 (controlled autonomy) | **Yes — this template + external audit** | |
| Stage 5 (operational autonomy) | **Yes — this template + pentest report** | |
