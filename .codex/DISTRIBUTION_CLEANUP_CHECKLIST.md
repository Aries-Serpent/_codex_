# DISTRIBUTION_CLEANUP_CHECKLIST

Date: 2026-07-07
Source: lane4-cleanup (repository-hygiene-agent)

## Packaging Cleanliness
- [ ] Version metadata aligned across release artifacts.
- [ ] Distribution include/exclude rules validated.
- [ ] Runtime dependencies minimized; dev/test isolated.
- [ ] Build outputs contain no local/editor/machine-specific files.

## Artifact Bloat Control
- [ ] Remove stale build caches and temporary outputs.
- [ ] Review largest distribution files and justify heavy entries.
- [ ] Exclude non-release notebooks/reports unless intentional.
- [ ] Apply retention tiering for artifact classes.

## Release Hygiene
- [ ] Required test/lint/security gates pass.
- [ ] Secret scan + vulnerability scan reviewed.
- [ ] SBOM/checksums generated and attached.
- [ ] Clean install smoke from produced artifact in fresh environment.

## Final Sign-Off
- [ ] All checklist sections complete or exception-documented with owner and due date.
