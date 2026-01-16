# CI - Build, Smoke Test, and Push Docker (GHCR) — OWNER APPROVED (NO-MARKETPLACE)

**Workflow File**: `docker-build-push.yml`

## Purpose

[Automated workflow - purpose to be documented]

## Triggers

[No triggers configured]

## Permissions Required

- **contents**: `read`
- **packages**: `write`

## Environment Variables

- **OWNER_APPROVED_DURATION**: ${{ github.event_name == 'workflow_dispatch' && github.event.inputs.approval_duration != '' && github.event.inputs.approval_duration || vars.OWNER_APPROVED_DURATION }}
- **OWNER_APPROVED_UNTIL**: ${{ github.event_name == 'workflow_dispatch' && github.event.inputs.approval_until != '' && github.event.inputs.approval_until || vars.OWNER_APPROVED_UNTIL }}
- **PUSH_PLATFORMS**: ${{ github.event_name == 'workflow_dispatch' && github.event.inputs.push_platforms != '' && github.event.inputs.push_platforms || vars.PUSH_PLATFORMS }}
- **BUILDX_CACHE_DIR**: /var/tmp/codex-buildx-cache

## Jobs

### approval-check

**Runner**: `['self-hosted', 'linux']`

**Steps**: 4

**Key Steps**:
1. Raw checkout (git)
2. Show owner approval context
3. Evaluate owner approval (guard)
4. Write approval status to summary

### build-and-smoke

**Runner**: `['self-hosted', 'linux']`

**Steps**: 9

**Key Steps**:
1. Raw checkout (git)
2. Show owner approval context (no-op)
3. Show owner approval status (helper)
4. Check OWNER approval window
5. Ensure Buildx and builder
... and 4 more steps

### push

**Runner**: `['self-hosted', 'linux']`

**Steps**: 11

**Key Steps**:
1. Raw checkout (git)
2. Ensure Buildx and builder
3. Set up QEMU (optional for multi-arch)
4. Derive tags (lowercase for GHCR)
5. Check OWNER approval window (push)
... and 6 more steps


## Secrets Used

[Secrets referenced in workflow - see workflow file for details]

## Maintenance

**Last Generated**: 2026-01-16  
**Status**: Active  
**Maintainer**: DevOps Team

## Related Documentation

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

---

*This documentation was automatically generated. For detailed configuration, refer to the workflow file.*
