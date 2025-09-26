# Security

This project uses `detect-secrets` with a committed baseline (`.secrets.baseline`). Update the baseline with:

```text
detect-secrets scan --baseline .secrets.baseline
```
A license check script `scripts/check_licenses.py` verifies third-party packages only use allowed licenses (MIT, Apache-2.0, BSD, ISC).
Run the script directly or via pre-commit. It exits non-zero when disallowed licenses are found.
