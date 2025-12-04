# _codex_ Secret Scan Stub Report

- Total findings: **52**

## Findings

| File | Line | Pattern | Snippet |
| ---- | ---- | ------- | ------- |
| `/workspace/_codex_/codex_secret_scan_report.json` | 7 | `BEGIN\s+PRIVATE\s+KEY` | `"snippet": "- Private keys (e.g., `-----BEGIN PRIVATE KEY-----`)"` |
| `/workspace/_codex_/codex_secret_scan_report.json` | 13 | `BEGIN\s+PRIVATE\s+KEY` | `"snippet": "- \"BEGIN PRIVATE KEY\""` |
| `/workspace/_codex_/codex_secret_scan_report.json` | 18 | `AWS_ACCESS_KEY_ID` | `"pattern": "AWS_ACCESS_KEY_ID",` |
| `/workspace/_codex_/codex_secret_scan_report.json` | 19 | `AWS_ACCESS_KEY_ID` | `"snippet": "- \"AWS_ACCESS_KEY_ID\" / \"AWS_SECRET_ACCESS_KEY\""` |
| `/workspace/_codex_/codex_secret_scan_report.json` | 19 | `AWS_SECRET_ACCESS_KEY` | `"snippet": "- \"AWS_ACCESS_KEY_ID\" / \"AWS_SECRET_ACCESS_KEY\""` |
| `/workspace/_codex_/codex_secret_scan_report.json` | 24 | `AWS_SECRET_ACCESS_KEY` | `"pattern": "AWS_SECRET_ACCESS_KEY",` |
| `/workspace/_codex_/codex_secret_scan_report.json` | 25 | `AWS_ACCESS_KEY_ID` | `"snippet": "- \"AWS_ACCESS_KEY_ID\" / \"AWS_SECRET_ACCESS_KEY\""` |
| `/workspace/_codex_/codex_secret_scan_report.json` | 25 | `AWS_SECRET_ACCESS_KEY` | `"snippet": "- \"AWS_ACCESS_KEY_ID\" / \"AWS_SECRET_ACCESS_KEY\""` |
| `/workspace/_codex_/codex_secret_scan_report.json` | 30 | `AWS_ACCESS_KEY_ID` | `"pattern": "AWS_ACCESS_KEY_ID",` |
| `/workspace/_codex_/codex_secret_scan_report.json` | 31 | `AWS_ACCESS_KEY_ID` | `"snippet": "re.compile(r\"AWS_ACCESS_KEY_ID\", re.IGNORECASE),"` |
| `/workspace/_codex_/codex_secret_scan_report.json` | 36 | `AWS_SECRET_ACCESS_KEY` | `"pattern": "AWS_SECRET_ACCESS_KEY",` |
| `/workspace/_codex_/codex_secret_scan_report.json` | 37 | `AWS_SECRET_ACCESS_KEY` | `"snippet": "re.compile(r\"AWS_SECRET_ACCESS_KEY\", re.IGNORECASE),"` |
| `/workspace/_codex_/codex_secret_scan_report.json` | 42 | `AWS_SECRET_ACCESS_KEY` | `"pattern": "AWS_SECRET_ACCESS_KEY",` |
| `/workspace/_codex_/codex_secret_scan_report.json` | 43 | `AWS_SECRET_ACCESS_KEY` | `"snippet": "\"api_key = 'AWS_SECRET_ACCESS_KEY=abc123'\\n\" \"print('hello')\\n\","` |
| `/workspace/_codex_/codex_secret_scan_report.json` | 48 | `AWS_SECRET_ACCESS_KEY` | `"pattern": "AWS_SECRET_ACCESS_KEY",` |
| `/workspace/_codex_/codex_secret_scan_report.json` | 49 | `AWS_SECRET_ACCESS_KEY` | `"snippet": "assert \"AWS_SECRET_ACCESS_KEY\" in first[\"snippet\"]"` |
| `/workspace/_codex_/codex_secret_scan_report.json` | 54 | `AWS_SECRET_ACCESS_KEY` | `"pattern": "AWS_SECRET_ACCESS_KEY",` |
| `/workspace/_codex_/codex_secret_scan_report.json` | 55 | `AWS_SECRET_ACCESS_KEY` | `"snippet": "re.compile(r\"aws_secret_access_key\", re.IGNORECASE),"` |
| `/workspace/_codex_/codex_secret_scan_report.json` | 60 | `AWS_SECRET_ACCESS_KEY` | `"pattern": "AWS_SECRET_ACCESS_KEY",` |
| `/workspace/_codex_/codex_secret_scan_report.json` | 61 | `AWS_SECRET_ACCESS_KEY` | `"snippet": "re.compile(r\"(?i)(aws_secret_access_key\\s*=\\s*[A-Za-z0-9/+=]{40})\"),"` |
| `/workspace/_codex_/codex_secret_scan_report.json` | 66 | `AWS_SECRET_ACCESS_KEY` | `"pattern": "AWS_SECRET_ACCESS_KEY",` |
| `/workspace/_codex_/codex_secret_scan_report.json` | 67 | `AWS_SECRET_ACCESS_KEY` | `"snippet": "re.compile(r\"(?i)(aws_secret_access_key\\s*=\\s*[A-Za-z0-9/+=]{40})\"),"` |
| `/workspace/_codex_/codex_secret_scan_report.json` | 73 | `BEGIN\s+PRIVATE\s+KEY` | `"snippet": "- Private key markers (`BEGIN PRIVATE KEY`)"` |
| `/workspace/_codex_/codex_secret_scan_report.json` | 79 | `BEGIN\s+PRIVATE\s+KEY` | `"snippet": "export GITHUB_APP_PRIVATE_KEY_PEM=\"-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\"  # pr...` |
| `/workspace/_codex_/codex_secret_scan_report.md` | 9 | `BEGIN\s+PRIVATE\s+KEY` | `| `/workspace/_codex_/validation.md` | 48 | `BEGIN\s+PRIVATE\s+KEY` | `- Private keys (e.g., `-----BEGIN PRIVATE KEY-...` |
| `/workspace/_codex_/codex_secret_scan_report.md` | 10 | `BEGIN\s+PRIVATE\s+KEY` | `| `/workspace/_codex_/tools/codex_secret_scan_stub.py` | 7 | `BEGIN\s+PRIVATE\s+KEY` | `- "BEGIN PRIVATE KEY"` |` |
| `/workspace/_codex_/codex_secret_scan_report.md` | 11 | `AWS_ACCESS_KEY_ID` | `| `/workspace/_codex_/tools/codex_secret_scan_stub.py` | 8 | `AWS_ACCESS_KEY_ID` | `- "AWS_ACCESS_KEY_ID" / "AWS_SECR...` |
| `/workspace/_codex_/codex_secret_scan_report.md` | 11 | `AWS_SECRET_ACCESS_KEY` | `| `/workspace/_codex_/tools/codex_secret_scan_stub.py` | 8 | `AWS_ACCESS_KEY_ID` | `- "AWS_ACCESS_KEY_ID" / "AWS_SECR...` |
| `/workspace/_codex_/codex_secret_scan_report.md` | 12 | `AWS_ACCESS_KEY_ID` | `| `/workspace/_codex_/tools/codex_secret_scan_stub.py` | 8 | `AWS_SECRET_ACCESS_KEY` | `- "AWS_ACCESS_KEY_ID" / "AWS_...` |
| `/workspace/_codex_/codex_secret_scan_report.md` | 12 | `AWS_SECRET_ACCESS_KEY` | `| `/workspace/_codex_/tools/codex_secret_scan_stub.py` | 8 | `AWS_SECRET_ACCESS_KEY` | `- "AWS_ACCESS_KEY_ID" / "AWS_...` |
| `/workspace/_codex_/codex_secret_scan_report.md` | 13 | `AWS_ACCESS_KEY_ID` | `| `/workspace/_codex_/tools/codex_secret_scan_stub.py` | 27 | `AWS_ACCESS_KEY_ID` | `re.compile(r"AWS_ACCESS_KEY_ID",...` |
| `/workspace/_codex_/codex_secret_scan_report.md` | 14 | `AWS_SECRET_ACCESS_KEY` | `| `/workspace/_codex_/tools/codex_secret_scan_stub.py` | 28 | `AWS_SECRET_ACCESS_KEY` | `re.compile(r"AWS_SECRET_ACCE...` |
| `/workspace/_codex_/codex_secret_scan_report.md` | 15 | `AWS_SECRET_ACCESS_KEY` | `| `/workspace/_codex_/tests/tools/test_codex_secret_scan_stub.py` | 10 | `AWS_SECRET_ACCESS_KEY` | `"api_key = 'AWS_S...` |
| `/workspace/_codex_/codex_secret_scan_report.md` | 16 | `AWS_SECRET_ACCESS_KEY` | `| `/workspace/_codex_/tests/tools/test_codex_secret_scan_stub.py` | 34 | `AWS_SECRET_ACCESS_KEY` | `assert "AWS_SECRE...` |
| `/workspace/_codex_/codex_secret_scan_report.md` | 17 | `AWS_SECRET_ACCESS_KEY` | `| `/workspace/_codex_/tests/security/test_no_hardcoded_secrets.py` | 8 | `AWS_SECRET_ACCESS_KEY` | `re.compile(r"aws_...` |
| `/workspace/_codex_/codex_secret_scan_report.md` | 18 | `AWS_SECRET_ACCESS_KEY` | `| `/workspace/_codex_/services/api/main.py` | 140 | `AWS_SECRET_ACCESS_KEY` | `re.compile(r"(?i)(aws_secret_access_ke...` |
| `/workspace/_codex_/codex_secret_scan_report.md` | 19 | `AWS_SECRET_ACCESS_KEY` | `| `/workspace/_codex_/src/codex_ml/monitoring/codex_logging.py` | 193 | `AWS_SECRET_ACCESS_KEY` | `re.compile(r"(?i)(...` |
| `/workspace/_codex_/codex_secret_scan_report.md` | 20 | `BEGIN\s+PRIVATE\s+KEY` | `| `/workspace/_codex_/docs/security/codex_security_safety_baseline.md` | 34 | `BEGIN\s+PRIVATE\s+KEY` | `- Private ke...` |
| `/workspace/_codex_/codex_secret_scan_report.md` | 21 | `BEGIN\s+PRIVATE\s+KEY` | `| `/workspace/_codex_/docs/examples/mint_tokens_per_run.md` | 17 | `BEGIN\s+PRIVATE\s+KEY` | `export GITHUB_APP_PRIVA...` |
| `/workspace/_codex_/validation.md` | 48 | `BEGIN\s+PRIVATE\s+KEY` | `- Private keys (e.g., `-----BEGIN PRIVATE KEY-----`)` |
| `/workspace/_codex_/tools/codex_secret_scan_stub.py` | 7 | `BEGIN\s+PRIVATE\s+KEY` | `- "BEGIN PRIVATE KEY"` |
| `/workspace/_codex_/tools/codex_secret_scan_stub.py` | 8 | `AWS_ACCESS_KEY_ID` | `- "AWS_ACCESS_KEY_ID" / "AWS_SECRET_ACCESS_KEY"` |
| `/workspace/_codex_/tools/codex_secret_scan_stub.py` | 8 | `AWS_SECRET_ACCESS_KEY` | `- "AWS_ACCESS_KEY_ID" / "AWS_SECRET_ACCESS_KEY"` |
| `/workspace/_codex_/tools/codex_secret_scan_stub.py` | 27 | `AWS_ACCESS_KEY_ID` | `re.compile(r"AWS_ACCESS_KEY_ID", re.IGNORECASE),` |
| `/workspace/_codex_/tools/codex_secret_scan_stub.py` | 28 | `AWS_SECRET_ACCESS_KEY` | `re.compile(r"AWS_SECRET_ACCESS_KEY", re.IGNORECASE),` |
| `/workspace/_codex_/tests/tools/test_codex_secret_scan_stub.py` | 10 | `AWS_SECRET_ACCESS_KEY` | `"api_key = 'AWS_SECRET_ACCESS_KEY=abc123'\n" "print('hello')\n",` |
| `/workspace/_codex_/tests/tools/test_codex_secret_scan_stub.py` | 34 | `AWS_SECRET_ACCESS_KEY` | `assert "AWS_SECRET_ACCESS_KEY" in first["snippet"]` |
| `/workspace/_codex_/tests/security/test_no_hardcoded_secrets.py` | 8 | `AWS_SECRET_ACCESS_KEY` | `re.compile(r"aws_secret_access_key", re.IGNORECASE),` |
| `/workspace/_codex_/services/api/main.py` | 140 | `AWS_SECRET_ACCESS_KEY` | `re.compile(r"(?i)(aws_secret_access_key\s*=\s*[A-Za-z0-9/+=]{40})"),` |
| `/workspace/_codex_/src/codex_ml/monitoring/codex_logging.py` | 193 | `AWS_SECRET_ACCESS_KEY` | `re.compile(r"(?i)(aws_secret_access_key\s*=\s*[A-Za-z0-9/+=]{40})"),` |
| `/workspace/_codex_/docs/security/codex_security_safety_baseline.md` | 34 | `BEGIN\s+PRIVATE\s+KEY` | `- Private key markers (`BEGIN PRIVATE KEY`)` |
| `/workspace/_codex_/docs/examples/mint_tokens_per_run.md` | 17 | `BEGIN\s+PRIVATE\s+KEY` | `export GITHUB_APP_PRIVATE_KEY_PEM="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"  # pragma: allowlist ...` |
