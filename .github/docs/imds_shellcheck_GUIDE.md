# ShellCheck Guide for IMDS Tooling (Updated)
> Generated: 2025-11-14 23:06:24 UTC | Author: mbaetiong

## Purpose
Ensure ongoing code quality for `.github/scripts/imds_diagnostic.sh`.

## Common Rules to Monitor
| Code | Meaning | Mitigation |
|------|---------|-----------|
| SC2086 | Unquoted vars | Quote parameter expansions |
| SC2016 | Literal braces in echo | Use printf or escape |
| SC2034 | Unused variables | Remove or reference |
| SC2148 | Missing shebang | Ensure `#!/usr/bin/env bash` present |
| SC2155 | Declaration in command substitution | Split declaration & assignment |

## Local Lint
