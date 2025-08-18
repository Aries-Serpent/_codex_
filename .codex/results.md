## Results Summary
* Inventory items: 66
* Unfinished markers: 19 across 7 files
* Ruff diagnostics: 65
* Pytest summary: 11 passed, 1 skipped in 2.20s
* Error questions: 2 entries

### Unfinished code index
- .codex/codex_repo_scout.py:156: hints = len(re.findall(r"\b(TODO|FIXME|WIP|TBD|XXX|NotImplemented)\b", txt, flags=re.IGNORECASE))
- .codex/codex_repo_scout.py:171: UNFINISHED_PAT = re.compile(r"\b(TODO|FIXME|WIP|TBD|XXX|NOT\s*IMPLEMENTED|NotImplemented)\b", re.IGNORECASE)
- .codex/codex_repo_scout.py:172: PY_NOTIMPL_PAT = re.compile(r"raise\s+NotImplementedError\b")
- .codex/codex_repo_scout.py:207: if "NotImplementedError" in line:
- .codex/codex_repo_scout.py:219: if "exit 1" in line and ("TODO" in line or "TBD" in line):
- .codex/codex_repo_scout.py:155: pass
- .codex/codex_repo_scout.py:250: pass
- .codex/run_repo_scout.py:157: r"\bTODO\b", r"\bFIXME\b", r"\bTBD\b", r"\bWIP\b", r"\bHACK\b",
- .codex/run_repo_scout.py:161: "python": [r"raise\s+NotImplementedError", r"^\s*pass\s*(#.*)?$", r"assert\s+False"],
- .codex/run_repo_scout.py:162: "javascript": [r"throw\s+new\s+Error\(['\"]TODO", r"function\s+\w+\(.*\)\s*{\s*}", r"=>\s*{\s*}"],
- .codex/run_repo_scout.py:163: "typescript": [r"throw\s+new\s+Error\(['\"]TODO", r"function\s+\w+\(.*\)\s*{\s*}", r"=>\s*{\s*}"],
- .codex/run_repo_scout.py:165: "sql": [r"--\s*TODO", r"/\*\s*TODO"],
- .codex/run_repo_scout.py:166: "html": [r"<!--\s*TODO"]
- tests/test_session_logging.py:70: if isinstance(e, (ImportError, AttributeError, NotImplementedError)):
- tools/codex_logging_workflow.py:138: pass
- tools/codex_patch_session_logging.py:137: {indent2}if isinstance(e, (ImportError, AttributeError, NotImplementedError)):
- tools/codex_patch_session_logging.py:221: "(ImportError/AttributeError/NotImplementedError) and otherwise fail."
- tools/codex_workflow_session_query.py:92: pass
- tools/git_patch_parser_complete.py:305: pass

### Error index
- ruff-run: unexpected argument '--format'
- ruff-check: ruff reported lint errors

### Prune index
- No pruning performed

### Next steps
- Address lint issues flagged by Ruff.
