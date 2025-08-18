# .codex/results.md

## Implemented Artifacts
- inventory.json
- mapping_table.md
- smoke_checks.json
- errors.ndjson

## Unfinished Code Index
- Files with unfinished markers: **1**
- Total unfinished signals: **4**

| File | Line | Kind | Snippet |
|---|---:|---|---|
| .codex/codex_repo_scout.py | 156 | marker | `hints = len(re.findall(r"\b(TODO\|FIXME\|WIP\|TBD\|XXX\|NotImplemented)\b", txt, flags=re.IGNORECASE))` |
| .codex/codex_repo_scout.py | 171 | marker | `UNFINISHED_PAT = re.compile(r"\b(TODO\|FIXME\|WIP\|TBD\|XXX\|NOT\s*IMPLEMENTED\|NotImplemented)\b", re.IGNORECASE)` |
| .codex/codex_repo_scout.py | 214 | marker | `if "throw new Error" in line and "Not Implemented" in line:` |
| .codex/codex_repo_scout.py | 219 | marker | `if "exit 1" in line and ("TODO" in line or "TBD" in line):` |

## Errors Captured as Research Questions
- Total: **10**

## Pruning Decisions
- None (detection rules retained)

## Next Steps
- Review unfinished index; prioritize high-signal files
- Address compile/test failures recorded in smoke_checks.json
- Update README references only after fixes are in-place (no CI activation)

**Constraint:** DO NOT ACTIVATE ANY GitHub Actions files.
