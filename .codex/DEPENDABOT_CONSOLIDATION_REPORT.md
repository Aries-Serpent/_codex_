# Dependabot PR Consolidation Report

## Summary
All 19 open Dependabot PRs have been successfully consolidated into PR #5368.

## Consolidated Changes

### Cargo Dependencies (4 PRs)
1. anyhow: 1.0.100 → 1.0.104
2. rayon: 1.11.0 → 1.12.0
3. serde: 1.0.228 → 1.0.229
4. tracing-subscriber: 0.3.22 → 0.3.23

### GitHub Actions (3 PRs)
1. actions/setup-node: → 7
2. actions/setup-python: → 7.0.0
3. softprops/action-gh-release: 3.0.1 → 3.0.2

### npm Dependencies (5 PRs)
1. @github/spark: 0.44.15 → 0.46.15 (cognitive_app)
2. lucide-react: 0.484.0 → 1.25.0 (cognitive_app)
3. @radix-ui/react-dialog: → 1.1.20 (cognitive_app)
4. @radix-ui/react-tooltip: → 1.2.13 (cognitive_app)
5. @tailwindcss/postcss: → 4.3.3 (cognitive_app)

### pip Dependencies (7 PRs)
1. mkdocs-macros-plugin: → ≥1.5.0
2. opentelemetry-sdk: ≥1.24 → ≥1.44.0
3. pyarrow: 16.1.0 → 25.0.0
4. pygments: ≥2.15.1 → ≥2.20.0
5. pymdown-extensions: → ≥11.0.1
6. mypy: 2.2.0 → 2.3.0
7. uvicorn: <1,>=0.50.1 → ≥0.51.0,<1

## PRs Ready to Close

All of the following Dependabot PRs can now be closed as their changes have been consolidated into PR #5368:

### Origin/Dependabot Branches:
- `origin/dependabot/cargo/anyhow-1.0.104` - deps(deps): Bump anyhow from 1.0.100 to 1.0.104
- `origin/dependabot/cargo/rayon-1.12.0` - deps(deps): Bump rayon from 1.11.0 to 1.12.0
- `origin/dependabot/cargo/serde-1.0.229` - deps(deps): Bump serde from 1.0.228 to 1.0.229
- `origin/dependabot/cargo/tracing-subscriber-0.3.23` - deps(deps): Bump tracing-subscriber from 0.3.22 to 0.3.23
- `origin/dependabot/github_actions/actions/setup-node-7` - chore(auth): write provenance session token [skip ci]
- `origin/dependabot/github_actions/actions/setup-python-7.0.0` - chore(auth): write provenance session token [skip ci]
- `origin/dependabot/github_actions/softprops/action-gh-release-3.0.2` - ci(deps): Bump softprops/action-gh-release from 3.0.1 to 3.0.2
- `origin/dependabot/npm_and_yarn/cognitive_app/github/spark-0.46.15` - deps(deps): Bump @github/spark from 0.44.15 to 0.46.15 in /cognitive_app
- `origin/dependabot/npm_and_yarn/cognitive_app/lucide-react-1.25.0` - deps(deps): Bump lucide-react from 0.484.0 to 1.25.0 in /cognitive_app
- `origin/dependabot/npm_and_yarn/cognitive_app/radix-ui/react-dialog-1.1.20` - deps(deps): Bump @radix-ui/react-dialog in /cognitive_app
- `origin/dependabot/npm_and_yarn/cognitive_app/radix-ui/react-tooltip-1.2.13` - deps(deps): Bump @radix-ui/react-tooltip in /cognitive_app
- `origin/dependabot/npm_and_yarn/cognitive_app/tailwindcss/postcss-4.3.3` - deps(deps-dev): Bump @tailwindcss/postcss in /cognitive_app
- `origin/dependabot/pip/mkdocs-macros-plugin-gte-1.5.0` - deps(deps): Update mkdocs-macros-plugin requirement
- `origin/dependabot/pip/opentelemetry-sdk-gte-1.44.0` - deps(deps): Update opentelemetry-sdk requirement from >=1.24 to >=1.44.0
- `origin/dependabot/pip/pyarrow-25.0.0` - deps(deps-dev): Bump pyarrow from 16.1.0 to 25.0.0
- `origin/dependabot/pip/pygments-gte-2.20.0` - deps(deps): Update pygments requirement from >=2.15.1 to >=2.20.0
- `origin/dependabot/pip/pymdown-extensions-gte-11.0.1` - deps(deps): Update pymdown-extensions requirement
- `origin/dependabot/pip/python-dev-6ffa451956` - deps(deps): Bump mypy from 2.2.0 to 2.3.0 in the python-dev group
- `origin/dependabot/pip/uvicorn-gte-0.51.0-and-lt-1` - deps(deps): Update uvicorn requirement from <1,>=0.50.1 to >=0.51.0,<1

## Commit History in Current Branch

All changes applied in sequence with individual commits for each dependency update.
