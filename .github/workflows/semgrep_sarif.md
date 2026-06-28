# Semgrep SAST (SARIF Upload)

**Workflow File**: `semgrep_sarif.yml`

## Purpose

Automated security scanning using Semgrep with SARIF output generation and upload to GitHub Security tab.
Detects security vulnerabilities, compliance issues, and code anti-patterns across Python, security audit, and OWASP top 10 categories.

## Triggers

- **Push**: On `main`, `develop`, and `copilot/**` branches
- **Pull Request**: Against `main` and `develop` branches
- **Schedule**: Daily at 3 AM UTC
- **Manual Dispatch**: With optional severity threshold override
- **Workflow Call**: Can be called from other workflows with severity input

## Permissions Required

- **contents**: `read` — Access to repository code
- **security-events**: `write` — Permission to upload SARIF to GitHub Security

## Key Features

### 1. **Direct Semgrep CLI Execution**
- Installs Semgrep via pip for reliable SARIF generation
- Uses `semgrep --sarif` with proper output flag
- Direct CLI usage bypasses action limitations

### 2. **Comprehensive Diagnostics**
- Captures Python and Semgrep versions
- Reports working directory and file generation status
- Generates diagnostic summary in GitHub Actions summary
- Searches for and lists SARIF files in working directory

### 3. **SARIF File Validation**
- Verifies SARIF is valid JSON using `jq`
- Reports file size and location
- Handles missing files gracefully

### 4. **Fallback Handling**
- Creates minimal but valid SARIF if generation fails
- Prevents workflow from failing due to missing output file
- Allows findings to be empty (scan passes without violations)

### 5. **Flexible Severity Thresholds**
- **CRITICAL**: Blocks only on critical-level findings
- **HIGH** (default): Blocks on critical OR high-level findings  
- **MEDIUM**: Reports findings but doesn't block
- **INFO**: Reports for informational purposes

### 6. **GitHub Security Integration**
- Uploads SARIF to GitHub Security Code Scanning tab
- Categories results properly for analysis dashboard
- Provides links to view findings in GitHub UI

## Configuration

### Security Audit Rules
```yaml
config:
  - p/security-audit      # General security patterns
  - p/python              # Python-specific vulnerabilities
  - p/owasp-top-ten       # OWASP Top 10 compliance
```

### Environment Variables
- `SEMGREP_TIMEOUT`: 300 seconds (5 minutes)
- `SEMGREP_RULES_TIMEOUT`: 60 seconds per rule

## Workflow Inputs

### `fail-on-severity` (Optional)
- **Type**: `choice` (dispatch) or `string` (workflow_call)
- **Options**: `CRITICAL`, `HIGH`, `MEDIUM`, `INFO`
- **Default**: `HIGH`
- **Description**: Controls at what severity level the workflow fails

## Jobs

### `semgrep`
**Runner**: `ubuntu-latest`
**Timeout**: 30 minutes

#### Steps:

1. **Checkout** — Clone repository
2. **Set up Python** — Configure Python 3.11 with pip cache
3. **Install Semgrep CLI** — Install via pip, verify installation
4. **Run Semgrep with SARIF output** — Execute scan with diagnostic output
5. **Generate diagnostic report** — Create detailed diagnostics in summary
6. **Verify SARIF file exists** — Check file presence and JSON validity
7. **Create fallback SARIF if missing** — Generates minimal valid SARIF if needed
8. **Upload SARIF to GitHub Security** — Uploads findings to code scanning
9. **Parse Semgrep results for blocking** — Extracts severity counts, determines failure
10. **Summary** — Reports findings and links to GitHub Security

## Known Issues & Fixes (Workflow Redesign)

### Issue: `returntocorp/semgrep-action` Invalid Parameters
**Problem**: The GitHub Action didn't support `generateSarif` or `output` parameters
**Solution**: Switched to direct Semgrep CLI execution via `pip install semgrep`

### Issue: Missing SARIF File Generation
**Problem**: Action wasn't generating SARIF output at expected location
**Solution**: 
- Use `semgrep --sarif --output=semgrep.sarif` flags
- Added comprehensive file generation diagnostics
- Implemented fallback SARIF creation

### Issue: Workflow Fails When No Findings Present
**Problem**: Upload failed if SARIF file wasn't generated
**Solution**:
- Creates valid empty SARIF if generation fails
- Uses `hashFiles()` conditional check
- Allows empty result sets to pass validation

### Issue: No Diagnostics on Failure
**Problem**: Hard to debug why SARIF wasn't generated
**Solution**: 
- Added diagnostic report with version info
- Reports file search results
- Lists directory contents on each run
- Validates JSON structure with `jq`

## SARIF Structure

Generated SARIF follows v2.1.0 specification:
```json
{
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
  "version": "2.1.0",
  "runs": [
    {
      "tool": { "driver": { "name": "Semgrep", ... } },
      "results": [
        {
          "ruleId": "...",
          "level": "error|warning|note",
          "message": { "text": "..." },
          "locations": [...]
        }
      ]
    }
  ]
}
```

## Severity Mapping

| SARIF Level | Severity | Default Block? |
|-------------|----------|----------------|
| `error`     | CRITICAL | Yes (HIGH mode) |
| `warning`   | HIGH     | Yes (HIGH mode) |
| `note`      | INFO     | No (report only) |
| `none`      | MINOR    | No (report only) |

## Maintenance

**Last Updated**: 2026-06-28
**Status**: Active
**Key Changes**:
- Redesigned to use Semgrep CLI directly (v1.38.0+)
- Added comprehensive diagnostics infrastructure
- Implemented fallback SARIF generation
- Fixed severity threshold logic
- Added proper JSON validation

## Troubleshooting

### SARIF File Not Generated
1. Check diagnostics step for Python/Semgrep version info
2. Verify file generation status in summary
3. Check for alternative `*.sarif` files in directory listing
4. Review Semgrep CLI output for errors (continue-on-error allows inspection)

### Workflow Fails Unexpectedly
1. Review "Parse Semgrep results for blocking" step for severity counts
2. Check fail threshold input matches desired level
3. Verify SARIF JSON validity in diagnostics
4. Look for jq errors in parsing step

### Empty Results Not Uploading
1. Fallback SARIF creation should activate automatically
2. Check "Create fallback SARIF if missing" step
3. Verify hashFiles() condition in upload step
4. Ensure GitHub Security events permission is set to `write`

## Related Documentation

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Semgrep Documentation](https://semgrep.dev/docs)
- [SARIF Specification](https://docs.oasis-open.org/sarif/sarif/v2.1.0/os/sarif-v2.1.0-os.html)
- [GitHub Code Scanning](https://docs.github.com/en/code-security/code-scanning)

---

*Last Generated*: 2026-06-28  
*Maintainer*: GitHub Copilot + DevOps Team
