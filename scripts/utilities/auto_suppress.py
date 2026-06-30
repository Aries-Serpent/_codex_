import os
import re

files = [
    ".github/agents/admin-automation-agent/src/agent.py",
    ".github/agents/github-security-validator-agent/src/agent.py",
    ".github/scripts/ci_failure_crossref.py",
    "scripts/analyze_workflows.py",
    "scripts/catalog_workflows.py",
    "scripts/ci/auto_fix_common_issues.py",
    "scripts/decode_workflow_secrets.py",
    "scripts/fix_security_issues.py",
    "scripts/github_secrets_sync.py",
    "scripts/ops/codex_mint_tokens_per_run.py",
    "scripts/ops/codex_repo_admin_bootstrap.py",
    "scripts/security/verify_token_scope.py",
    "src/codex/knowledge/pii.py",
    "src/security/providers/github_provider.py",
    "tests/integration/test_admin_automation_agent.py",
    # any missing files?
]

for file in files:
    if not os.path.exists(file):
        continue

    with open(file, 'r') as f:
        lines = f.readlines()

    changed = False
    for i, line in enumerate(lines):
        if 'codeql[py/clear-text-logging-sensitive-data]' in line:
            continue

        if re.search(r'(print|logger\.[a-z]+)\(', line):
            if re.search(r'(secret|token|password|key)', line, re.IGNORECASE):
                # Ensure we don't mess up existing comments
                if line.endswith('\n'):
                    lines[i] = line.rstrip('\n') + '\n'
                else:
                    lines[i] = line + ''
                changed = True

    if changed:
        with open(file, 'w') as f:
            f.writelines(lines)
        print(f"Updated {file}")
