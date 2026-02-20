# Commit Message Guidelines for CI Fixes

## Template

```
<type>(<scope>): <subject>

<body>

<footer>
```

## Types for CI fixes:
- `fix(ci)`: Fixes to CI workflows
- `fix(tests)`: Test-related fixes
- `fix(docs)`: Documentation fixes
- `chore(ci)`: CI maintenance/automation

## Examples:

### Emergency test timeout fix:
```
fix(ci): emergency - resolve chronic test timeout (6+ iteration execution)

CRITICAL CHANGES:
- Add slow test markers in conftest.py (auto-detect patterns)
- Update workflows to skip slow tests (-m "not slow")
- Increase workflow timeouts (90 mins Coverage, 60 mins Validation)
- Add per-test timeout decorator (300s max)
- Ensure artifact upload on failure (if: always())

Impact:
- Estimated execution time: 2 iterations → 30 minutes
- Prevents runner shutdown/timeout
- Enables post-validation to succeed

Resolves: Jobs 63600697256, 63606638531, 63600697265
PR: #3248
```

### Documentation fixes:
```
fix(docs): auto-resolve 39 dead links in PR #3248

- Replace RAG_META_TENSOR_FIX_SUMMARY.md references
- Create missing docs/api/README.md placeholder
- Update OpenAI API link URLs (403 → valid)
- Remove invalid anchor links
- Fix security scanning URL

Script: scripts/fix_pr3248_dead_links.sh
Verification: 0 dead links reported
PR: #3248
```

### Code quality fixes:
```
chore(ci): remove unused imports flagged by CodeQL

- scripts/empty_toc_resolver.py: remove Tuple
- scripts/phase3_stage1_processor.py: remove Dict, Set  
- scripts/phase3_categorization.py: remove re, List, Tuple

Resolves: Bot comments (4 unused import warnings)
PR: #3248
```
