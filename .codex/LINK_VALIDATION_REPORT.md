# LINK_VALIDATION_REPORT

Date: 2026-07-07
Source: lane5-link (link-validator-agent)
Scope: offline/onboarding docs and isolated deployment references

## Summary

- Internal file links in reviewed scope: no missing local file targets.
- Confirmed broken links/anchors in scope: 3.
- External DNS-unresolved links in this run: 4 (revalidation needed in full-egress CI).

## Confirmed Broken Links

| Severity | File:Line | Link | Recommended Fix |
|---|---|---|---|
| High | `docs/ONBOARDING_QUICKSTART.md:235` | `https://visualstudio.microsoft.com/cpp-build-tools/` | Use `https://visualstudio.microsoft.com/visual-cpp-build-tools/` |
| Medium | `OFFLINE_DEPLOYMENT.md:421` | `QUICKSTART_BY_PROFILE.md#-core-profile-lightweight--offline-first-8-15-mb` | Replace with `QUICKSTART_BY_PROFILE.md#core-profile-lightweight-offline-first-8-15-mb` and verify against rendered heading slug in target file. |
| Medium | `OFFLINE_DEPLOYMENT.md:422` | `QUICKSTART_BY_PROFILE.md#-runtime-profile-production-inference--apis-20-35-mb` | Replace with `QUICKSTART_BY_PROFILE.md#runtime-profile-production-inference-apis-20-35-mb` and verify against rendered heading slug in target file. |

## At-Risk (DNS unresolved in runner environment)

- `https://pytorch.org/get-started/locally/`
- `https://docs.pytest.org/en/stable/reference/reference.html`
- `https://nox.thea.codes/en/stable/usage.html`
- `https://mlflow.org/docs/latest/index.html`

## Actions

1. Fix confirmed broken targets.
2. Revalidate unresolved external links in full network CI context.
3. Add periodic offline/onboarding link checks to avoid regressions.
