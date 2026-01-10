# Security False Positive Standard

## Purpose

This document establishes the codebase standard for documenting and handling false positive security alerts from automated scanning tools (CodeQL, Bandit, etc.). This ensures that AI agents and human reviewers understand why certain alerts are suppressed and prevents repeated flagging of the same issues.

## When to Use This Standard

Use this standard when:
1. A security scanner flags code as vulnerable
2. You have verified the code is safe (false positive)
3. The alert is likely to recur on subsequent scans
4. The code should remain as-is for valid reasons

## Documentation Requirements

When suppressing a false positive alert, you **MUST** include:

### 1. Inline Suppression Comment

Use the scanner-specific suppression syntax followed by a detailed explanation:

```python
# CodeQL [py/clear-text-logging-sensitive-data] False Positive
# Justification: This log statement only contains a static informational string
# with no sensitive data. The logged message does not include tokens, passwords,
# or any user-provided data that could leak secrets.
logger.info("Validating GitHub token")
```

### 2. Required Elements

Every suppression comment must include:
- **Scanner name and rule ID**: `CodeQL [py/clear-text-logging-sensitive-data]`
- **False Positive declaration**: Explicitly state "False Positive"
- **Justification**: 2-3 sentences explaining why the alert is incorrect
- **Data flow explanation**: What data flows through the code and why it's safe

### 3. Alternative Patterns

For multi-line suppressions:

```python
# CodeQL [py/sql-injection] False Positive
# Justification: The table name is validated against a hardcoded allowlist
# of safe table names before being used in the query. User input cannot
# influence the table name selection.
# Security Review: Approved by security team on 2026-01-10
query = f"SELECT * FROM {validated_table_name} WHERE id = ?"
```

## CodeQL-Specific Syntax

### Suppression Comment Format

```python
# lgtm [rule-id] or # CodeQL [rule-id]
```

### Common Rule IDs

- `py/clear-text-logging-sensitive-data` - Logging sensitive information
- `py/sql-injection` - SQL injection
- `py/path-injection` - Path traversal
- `py/command-injection` - Command injection
- `py/unsafe-deserialization` - Unsafe deserialization

### Alert Suppression File

For repository-level suppressions, use `.github/codeql/codeql-config.yml`:

```yaml
queries:
  - uses: security-and-quality

query-filters:
  - exclude:
      id: py/clear-text-logging-sensitive-data
      paths:
        - src/security/providers/github_provider.py
```

## Examples from Codebase

### Example 1: Static Log Messages

```python
# CodeQL [py/clear-text-logging-sensitive-data] False Positive
# Justification: This is a static informational message with no dynamic data.
# No secrets, tokens, or sensitive information are included in the log output.
# The actual token value is never logged.
logger.info("Validating GitHub token")
```

### Example 2: Redacted Data

```python
# CodeQL [py/clear-text-logging-sensitive-data] False Positive
# Justification: The secret_id is intentionally redacted using _redact_identifier()
# before logging. Only the first 8 characters are shown, which is insufficient
# to reconstruct the actual secret value. This is a standard security practice
# for audit logging.
logger.info(f"Token validation: {_redact_identifier(secret_id)}")
```

### Example 3: Stub/Mock Implementation

```python
# CodeQL [py/clear-text-logging-sensitive-data] False Positive
# Justification: This is stub code that doesn't handle real secrets in production.
# The method raises NotImplementedError before any actual token operations occur.
# Real implementation will use secure secret management APIs.
logger.info("Creating GitHub token")
raise NotImplementedError("Token creation not implemented")
```

## Review Process

1. **Document the suppression**: Add inline comments as specified above
2. **Verify the justification**: Ensure the code is actually safe
3. **Add to tracking**: Update this document with new patterns
4. **Security review**: For High/Critical alerts, get security team approval

## AI Agent Guidelines

When reviewing code with suppression comments:

1. **Check for complete documentation**: Verify all required elements are present
2. **Validate the justification**: Ensure the reasoning makes sense
3. **Look for patterns**: If the same alert recurs, check for existing suppressions
4. **Don't re-flag**: If properly documented, don't create duplicate reports
5. **Update if needed**: If security context changes, flag for review

## Common False Positive Patterns

### Pattern 1: Static Informational Logs
```python
# Safe: No dynamic data
logger.info("Processing authentication request")
logger.info("Token rotation completed")
```

### Pattern 2: Metadata-Only Logs
```python
# Safe: Only non-sensitive metadata
logger.info(f"HTTP Status: {http_status}")
logger.info(f"Rate Limit: {rate_limit_remaining}")
```

### Pattern 3: Stub/Placeholder Code
```python
# Safe: Not used in production, raises error
logger.warning("Using stub implementation")
raise NotImplementedError("Must implement before production")
```

### Pattern 4: Already Redacted
```python
# Safe: Data sanitized before logging
logger.debug(f"Token: {redact(token)}")
logger.info(f"User: {anonymize(user_id)}")
```

## Maintenance

This document should be updated when:
- New false positive patterns are identified
- Security scanning tools are updated
- New suppression techniques are discovered
- Security policies change

## References

- [CodeQL Documentation](https://codeql.github.com/docs/)
- [GitHub Code Scanning](https://docs.github.com/en/code-security/code-scanning)
- Repository Security Policy: `.github/SECURITY.md`

---

**Last Updated**: 2026-01-10  
**Maintained By**: Security Team & AI Agents  
**Commit SHA**: (to be added upon commit)
