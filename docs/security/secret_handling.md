# Secret Handling (Offline)

- All scans run locally; no data leaves the machine.
- Findings are masked in `audit_artifacts/secret_scan.json`.
- If a real secret is suspected, rotate it and remove from history separately.

## Secret Scanner

The offline secret scanner uses regex patterns to detect potential secrets:

```bash
python tools/security/scan_repo.py
```

Outputs to: `audit_artifacts/secret_scan.json`

## Patterns Detected

- Generic API keys/tokens (e.g., `api_key="..."`, `token="..."`)
- AWS access keys (`AKIA...`)
- GitHub tokens (`ghp_...`, `gho_...`, `ghu_...`, `ghs_...`)

## Masking

All detected values are masked in the output:
- Values > 8 chars: show first 4 and last 4 with `…` in between
- Values ≤ 8 chars: replaced with `[REDACTED]`

## If a Real Secret is Found

1. **Rotate immediately**: Generate a new secret and update systems
2. **Remove from history**: Use `git filter-branch` or BFG Repo-Cleaner
3. **Document incident**: Record in security log (not in this repo)
4. **Update `.gitignore`**: Prevent future exposure

## Best Practices

- Never commit `.env` files
- Use environment variables for secrets
- Keep secrets in external secret managers (AWS Secrets Manager, HashiCorp Vault, etc.)
- Run secret scan in pre-commit hooks
- Review scan results regularly
