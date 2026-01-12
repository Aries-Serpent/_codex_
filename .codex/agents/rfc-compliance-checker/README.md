# RFC Compliance Checker Agent

Ensures standards compliance across HTTP, URL, and protocol implementations.

## Features

- **RFC 3986**: URI Generic Syntax (scheme case-insensitivity, hostname validation)
- **RFC 7230-7235**: HTTP/1.1 Message Syntax and Semantics
- **RFC 6265**: HTTP State Management (Cookies)
- **RFC 2616**: Detects obsolete references

## Quick Start

```bash
# Check all Python files
python run.py --all

# Check specific files
python run.py --files scripts/zendesk_docs_fetch.py

# Check only URI compliance
python run.py --all --check-uri

# Generate automatic fixes
python run.py --all --auto-fix
```

## Example Issues Detected

### Case-sensitive URI scheme
```python
# BEFORE (Non-compliant)
if parsed.scheme == "https":

# AFTER (RFC 3986 compliant)
if parsed.scheme.lower() == "https":
```

### Obsolete RFC reference
```python
# DETECTED
# This follows RFC 2616

# SUGGESTION
# Update to RFC 7230 (Message Syntax) or RFC 7231 (Semantics)
```

## Output

```
RFC Compliance Checker - Scan Results
================================================================================

Total Issues: 3
Errors: 1
Warnings: 2

By RFC Standard:
  RFC 3986: URI Generic Syntax: 1
  RFC 7231: HTTP/1.1 Semantics: 2
```

## Configuration

Default thresholds:
- **ERROR**: Non-compliant with RFC (blocks merge)
- **WARNING**: Deviation from standard (review required)
- **INFO**: Suggestions for improvement

## Integration

See `.codex/cognitive_brain/SECURITY_FIXES_PR2782_2026_01_11.md` for full integration details.
