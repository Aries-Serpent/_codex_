#!/usr/bin/env markdown
# Security Findings API - Quick Reference

## Installation & Basic Usage

```bash
# No installation needed - uses stdlib only

# Make it executable
chmod +x scripts/ci/security_findings_api.py

# Run tests
python scripts/ci/test_security_findings_api.py
```

## Quick Start Examples

### 1. Find CWE-79 (XSS) Vulnerabilities

```bash
python scripts/ci/security_findings_api.py query \
  --query-type cwe --value CWE-79
```

Output: JSON with all findings matching CWE-79

### 2. Find Django Package Issues

```bash
python scripts/ci/security_findings_api.py query \
  --query-type package --value django --format csv \
  --output django-issues.csv
```

Output: CSV file with all Django-related findings

### 3. Find Critical Issues

```bash
python scripts/ci/security_findings_api.py query \
  --query-type severity --value CRITICAL --format markdown
```

Output: Markdown report with all CRITICAL findings

### 4. Find Issues in Authentication Code

```bash
python scripts/ci/security_findings_api.py query \
  --query-type file --value src/auth/
```

Output: JSON with findings in auth code

## Python API Examples

```python
from scripts.ci.security_findings_api import query_findings, format_output

# Query findings
result = query_findings('severity', 'HIGH')

# Access results
print(f"Total findings: {result['results']['total_findings']}")
print(f"Matched: {result['results']['total_matched']}")

# Format for export
findings = result['findings']
csv_output = format_output(findings, 'csv')
print(csv_output)
```

## Command-Line Options

### Required Arguments
- `--query-type` (cwe | package | file | severity)
- `--value` (search value)

### Optional Arguments
- `--findings-file` (path to findings JSON)
- `--cache-dir` (path to cache directory)
- `--format` (json | csv | markdown, default: json)
- `--output` (output file path)

## Output Formats

### JSON (Default)
- Includes query metadata
- Includes total_matched and total_findings
- Full finding objects

### CSV
- Headers for all fields
- One finding per row
- Easy to import to spreadsheets

### Markdown
- Findings grouped by severity
- Formatted for GitHub/Confluence
- Clickable to rules

## Performance

All queries complete in **< 50ms**:
- CWE queries: ~40ms
- Package queries: ~45ms
- File queries: ~50ms
- Severity queries: ~40ms

## Severity Levels

```
CRITICAL  → Only critical findings
HIGH      → Critical + High
MEDIUM    → Critical + High + Medium
LOW       → Critical + High + Medium + Low
INFO      → All findings
```

## Exit Codes

- **0** = Success (findings found)
- **1** = Error (validation, file I/O)
- **2** = Success (no findings matched)

## Environment Variables

```bash
# Override default findings file
export SECURITY_FINDINGS_JSON=/path/to/findings.json

# Override cache directory
export SECURITY_FINDINGS_CACHE=/path/to/cache
```

## Common Issues

### "No findings source found"

Solution: Ensure one of these exists:
- `.codex/security-cache/` with recent runs
- `.codex/security-findings-comprehensive.json`

Or use `--findings-file` to specify path

### "Invalid query type"

Solution: Use one of: cwe, package, file, severity

### "Invalid format"

Solution: Use one of: json, csv, markdown

## Integration Examples

### In GitHub Actions

```yaml
- name: Query Security Findings
  run: |
    python scripts/ci/security_findings_api.py query \
      --query-type severity --value CRITICAL \
      --format json > critical-findings.json
    
    # Post to PR if critical findings exist
    if [ -s critical-findings.json ]; then
      echo "⚠️ Critical findings detected"
    fi
```

### In Python Scripts

```python
import subprocess
import json

result = subprocess.run([
    'python', 'scripts/ci/security_findings_api.py', 'query',
    '--query-type', 'cwe', '--value', 'CWE-79',
    '--format', 'json'
], capture_output=True, text=True)

if result.returncode == 0:
    findings = json.loads(result.stdout)
    for finding in findings['findings']:
        print(f"- {finding['title']} in {finding.get('file', 'N/A')}")
```

## Testing

Run the test suite:

```bash
python scripts/ci/test_security_findings_api.py
```

Expected output:
```
✓ PASS: CWE Query
✓ PASS: Package Query
✓ PASS: File Query
✓ PASS: Severity Query
✓ PASS: Output Formats
✓ PASS: Performance
✓ PASS: Input Validation

Total: 7/7 test suites passed
```

## Help & Documentation

```bash
# Show help
python scripts/ci/security_findings_api.py --help

# Show module docstring
python scripts/ci/security_findings_api.py -h

# View source
less scripts/ci/security_findings_api.py
```

## Next Steps

After using the API:

1. **Phase 5C**: Workflow integration
2. **Phase 6**: PR enhancement automation
3. **Phase 7**: Conversational @copilot interface
4. **Phase 8**: Agent-specific formatting

## See Also

- `.codex/PHASE_5B_SECURITY_API_IMPLEMENTATION.md` - Full documentation
- `scripts/ci/security_cache_manager.py` - Phase 4A cache operations
- `scripts/ci/aggregate_security_findings.py` - Phase 1-3 aggregation
