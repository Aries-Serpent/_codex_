# Custom Agent: Security Input Validator - Full Specification
**Version**: 1.0.0  
**Status**: Design Complete - Ready for Implementation  
**Priority**: P0 (Critical)

See README.md for quick start guide.

## Validation Patterns

### Command Injection
```python
patterns = {
    "shell_metacharacters": r'[`$|&;<>()\\]',
    "command_substitution": r'\$\([^)]*\)',
    "backtick": r'`[^`]*`',
}
```

### Path Traversal
```python
patterns = {
    "dot_dot_slash": r'\.\.[/\\]',
    "encoded": r'%2e%2e[/\\]',
}
```

### SQL Injection
```python
patterns = {
    "union_select": r'\bunion\b.*\bselect\b',
    "or_true": r'\bor\b\s+[\d\w]+\s*=\s*[\d\w]+',
}
```

## Integration

### GitHub Actions
```yaml
name: Security Validator
on: [pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/agents/security-input-validator
```

### Pre-commit
```yaml
- repo: local
  hooks:
    - id: security-input-validator
      name: Security Input Validator
      entry: python .codex/agents/security-input-validator/run.py
      language: python
```

## Rollout Plan
1. **Phase 1 (Week 1-2)**: Silent monitoring, tune patterns
2. **Phase 2 (Week 3-4)**: PR comments, no blocking
3. **Phase 3 (Week 5-6)**: Auto-fix LOW/MEDIUM
4. **Phase 4 (Week 7+)**: Full deployment, block CRITICAL

## Success Metrics
- Detection Rate: 95%+
- False Positive Rate: < 5%
- MTTF: < 1 hour

---

For full implementation details, see the cognitive brain document:
`.codex/cognitive_brain/SECURITY_FIXES_PR2782_2026_01_11.md`
