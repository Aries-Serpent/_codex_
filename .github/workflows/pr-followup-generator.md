# Generate PR Follow-Up Prompt

**Historical Workflow File**: `.github/workflows.backup.20260214_131353/pr-followup-generator.yml`

The current checkout has no `.github/workflows/pr-followup-generator.yml`.
This Markdown reference is not an executable workflow and does not establish
hosted workflow status or automatic dispatch.

## Purpose

`scripts/generate_pr_followup.py` fills the selected
`.github/copilot-prompts/templates/` template and writes
`.github/copilot-prompts/active/PR-{number}-followup.md` when explicitly invoked.
Generation does not post a comment, invoke an agent, approve work or execute
commands embedded in the output. The legacy shell smoke test invokes the CLI,
but its workflow-existence assertion is not valid for this checkout.

Same-PR task blocks and explicit continuation context are preserved; another
PR's tasks are not used as defaults. Imported commands and assertions remain
untrusted content, not authorization. Local applicable policy and actual
execution/review/security gates remain authoritative.

## Triggers

No current YAML caller was found in the bounded generator-reference search.
Historical backup triggers are not evidence of an active caller.

## Permissions Required

- **contents**: `write`
- **pull-requests**: `write`

## Environment Variables

[None specified at workflow level]

## Jobs

### generate

**Runner**: `ubuntu-latest`

**Steps**: 2

**Key Steps**:
1. actions/checkout@v4
2. Setup Python


## Secrets Used

[No secrets explicitly referenced]

## Maintenance

**Last Generated**: 2026-01-16  
**Status**: Historical reference; current hosted activation unverified
**Maintainer**: DevOps Team

## Related Documentation

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

---

*This documentation was automatically generated. For detailed configuration, refer to the workflow file.*
