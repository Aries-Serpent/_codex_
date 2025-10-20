# Enable Docker Build & Push Workflow

This repository ships with a disabled Docker workflow located under
`.github/_workflows_disabled/docker-build-push.yml`. To enable automated builds
and pushes to GitHub Container Registry (GHCR), follow the checklist below.

## Prerequisites

1. **Self-hosted runners** — Confirm the `self-hosted, linux` runners referenced
   in the workflow are available, online, and permitted to run container builds.
2. **Secrets** — Ensure `GITHUB_TOKEN` has appropriate permissions or provide an
   alternative token with `packages:write` scope if required by your policy.
3. **Registry access** — Verify that your organization is allowed to push images
   to `ghcr.io` and that any required approvals are in place.

## Enablement Steps

1. Review the workflow configuration for alignment with your security and
   compliance policies.
2. Move the workflow into `.github/workflows/` (for example, using `git mv`):
   ```bash
   git mv .github/_workflows_disabled/docker-build-push.yml .github/workflows/
   ```
3. Commit the change and open a pull request for review by the repository
   owners.
4. Monitor the first CI run to confirm the build, smoke test, and push stages
   succeed. Investigate any failures before merging.

## Optional Hardening

- Configure the workflow with branch protections or required reviewers before
  merging.
- Rotate access tokens regularly and store them in your secret manager.
- Enable image scanning on GHCR or an external registry to catch vulnerabilities
  early.

Once satisfied, merge the pull request to activate the workflow.
