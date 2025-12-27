# PR Template - Genesis Pre-token Setup

## Summary
This PR adds pre-token templates and workflows for the Genesis Protocol. It does NOT inject secrets or enable workflows.

## Checklist (HUMAN admin must complete)
- [ ] I confirm I (mbaetiong) will inject required secrets via GitHub UI.
- [ ] I confirm I will review all templates and remove workflow guard (if: false) only when safe.
- [ ] I confirm a plan for token rotation and audit is in place.

## Changes
- List of created files:
  - .github/workflows/genesis-bootstrap.yml (template)
  - .github/workflows/workflow-lint.yml
  - .codex/autonomous_agent.yaml
  - .codex/guardrails.md
  - .codex/change_log.md
  - scripts/autonomous_agent.py
  - scripts/AUTONOMOUS_AGENT_README.md
  - .github/PULL_REQUEST_TEMPLATE.md
  - docs/admin/GENESIS_SETUP_GUIDE.md
  - docs/agent/OPERATIONAL_GUIDELINES.md

## Reviewer(s)
- @mbaetiong
