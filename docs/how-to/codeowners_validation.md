# [How-to]: CODEOWNERS Validation & Enforcement  
> Generated: 2025-10-09 20:13:48 UTC | Author: mbaetiong  
Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

Purpose
- Ensure CODEOWNERS exists, is syntactically valid, and covers key paths.
- Pair with branch protection to require CODEOWNER reviews.

Validation Dimensions
| Dimension | Check | Method |
|----------|------|--------|
| Placement | .github/CODEOWNERS | validate_repo_codeowners() |
| Syntax | Owners match @user or @org/team | Regex validation |
| Default rule | '*' rule present | has_default_rule() |
| Coverage | src/, tests/, docs/ mapped | heuristic_coverage() |
| Protection | require CODEOWNER reviews | Admin bootstrap (online opt-in) |

Python API
```python
from src.tools.codeowners_validate import validate_repo_codeowners
rep = validate_repo_codeowners(".")
print(rep.errors, rep.warnings, rep.coverage)
```

Acceptance
- Non-empty file; all owners valid; default '*' rule exists; coverage true for src/tests/docs.
- Optional: enforce CODEOWNER reviews via repo bootstrap script.

*End*