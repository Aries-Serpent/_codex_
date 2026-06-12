#!/usr/bin/env python3
"""
Cross-reference CI failures with workflow analysis.
"""

import json

# Load workflow analysis
with open('workflow_analysis.json', 'r') as f:
    workflow_data = json.load(f)

# Known CI failures from reports
ci_failures = {
    "Job 57809086046": {
        "failure_type": "Build Failure",
        "description": "Missing src/codex_plans package directory",
        "affected_workflows": ["pypi-publish.yml", "build-chatgpt-package.yml"],
        "severity": "CRITICAL",
        "root_cause": "Package structure mismatch in pyproject.toml",
        "remediation": "Create src/codex_plans or remove from package config"
    },
    "Job 57809086031": {
        "failure_type": "Security Scan Failure",
        "description": "Bandit SAST scan failing on nosec comments",
        "affected_workflows": ["security-scan.yml", "security-scanning-suite.yml", "security-suite.yml"],
        "severity": "CRITICAL",
        "root_cause": "Missing bandit configuration, nosec without justification",
        "remediation": "Create bandit.yaml with nosec: true, audit nosec usage"
    },
    "Job 57809086050": {
        "failure_type": "Docker Build Failure",
        "description": "Debian Buster repository obsolescence",
        "affected_workflows": ["docker-build-push.yml", "security-scan.yml"],
        "severity": "HIGH",
        "root_cause": "Base image using Debian Buster (EOL)",
        "remediation": "Update Dockerfile to use Debian Bullseye or Ubuntu 22.04"
    }
}

# Additional known issues from codebase patterns
additional_issues = {
    "test-suite.yml": {
        "failure_type": "Parse Error",
        "description": "YAML syntax error - Python code embedded incorrectly",
        "severity": "CRITICAL",
        "root_cause": "Invalid YAML structure at line 178",
        "remediation": "Fix YAML syntax or extract Python to separate script"
    },
    "Import Failures": {
        "failure_type": "Module Import Errors",
        "description": "Missing codex_plans imports across codebase",
        "affected_files": ["pyproject.toml", "various Python files"],
        "severity": "HIGH",
        "root_cause": "Package namespace mismatch",
        "remediation": "Audit all imports, ensure consistent namespace"
    }
}

# Cross-reference with workflow analysis
print("# CI Failure Cross-Reference Analysis\n")
print("## Known CI Failures with Workflow Impact\n")

for job_id, failure in ci_failures.items():
    print(f"### {job_id}: {failure['failure_type']}")
    print(f"**Severity**: {failure['severity']}")
    print(f"**Description**: {failure['description']}")
    print(f"**Root Cause**: {failure['root_cause']}")
    print(f"**Remediation**: {failure['remediation']}")
    print("\n**Affected Workflows**:")

    for wf_name in failure['affected_workflows']:
        if wf_name in workflow_data['workflows']:
            wf = workflow_data['workflows'][wf_name]
            print(f"- **{wf_name}**")
            print(f"  - Status: {'Active' if not wf['guarded'] else 'Guarded'}")
            print(f"  - Jobs: {len(wf['jobs'])}")
            print(f"  - Runners: {', '.join(wf['runners'][:2])}")
            print(f"  - Secrets: {len(wf['secrets'])}")
            print(f"  - Dependencies: Docker={wf['has_docker']}, uv={wf['has_uv']}, pytest={wf['has_pytest']}")
        else:
            print(f"- **{wf_name}** (not found in analysis)")
    print()

print("\n## Additional Known Issues\n")
for issue_name, issue in additional_issues.items():
    print(f"### {issue_name}: {issue['failure_type']}")
    print(f"**Severity**: {issue['severity']}")
    print(f"**Description**: {issue['description']}")
    print(f"**Root Cause**: {issue['root_cause']}")
    print(f"**Remediation**: {issue['remediation']}")
    print()

# Priority matrix for workflow fixes
print("\n## Workflow Fix Priority Matrix\n")
print("| Workflow | Status | Priority | Known Issues | Action Required |")
print("|----------|--------|----------|--------------|-----------------|")

priority_workflows = [
    "pr-checks.yml",
    "test-suite.yml",
    "security-scan.yml",
    "security-scanning-suite.yml",
    "docker-build-push.yml",
    "pypi-publish.yml",
    "build-chatgpt-package.yml",
    "test-comprehensive.yml",
    "rust_swarm_ci.yml",
]

for wf_name in priority_workflows:
    if wf_name in workflow_data['workflows']:
        wf = workflow_data['workflows'][wf_name]
        status = "✅ Active" if not wf['guarded'] else "🔴 Guarded"

        # Determine known issues
        issues = []
        for job_id, failure in ci_failures.items():
            if wf_name in failure['affected_workflows']:
                issues.append(f"{failure['failure_type']}")

        if wf_name in workflow_data['errors']:
            issues.append("Parse Error")

        issues_str = ", ".join(issues) if issues else "None"

        # Determine action
        if issues:
            action = "🔥 URGENT FIX"
        elif wf['guarded']:
            action = "Review Guard"
        else:
            action = "Monitor"

        print(f"| {wf_name} | {status} | 🔴 Critical | {issues_str} | {action} |")
    elif wf_name in workflow_data['errors']:
        print(f"| {wf_name} | ⚠️ Error | 🔴 Critical | Parse Error | 🔥 URGENT FIX |")

print()

# Resource summary
print("\n## Resource Requirements Summary\n")
print("### Critical Workflows - Resource Needs\n")

critical_workflows = [wf for wf, data in workflow_data['workflows'].items()
                      if 'Critical' in data.get('name', '') or
                      any(x in wf.lower() for x in ['test', 'ci', 'security', 'build'])]

runner_usage = {}
secrets_usage = {}

for wf_name in critical_workflows[:20]:  # Top 20
    if wf_name in workflow_data['workflows']:
        wf = workflow_data['workflows'][wf_name]

        for runner in wf['runners']:
            runner_usage[runner] = runner_usage.get(runner, 0) + 1

        for secret in wf['secrets']:
            secrets_usage[secret] = secrets_usage.get(secret, 0) + 1

print("**Runners**:")
for runner, count in sorted(runner_usage.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"- `{runner}`: {count} critical workflows")

print("\n**Most Common Secrets**:")
for secret, count in sorted(secrets_usage.items(), key=lambda x: x[1], reverse=True)[:5]:
    # Security: mask secret name to prevent clear-text logging — CodeQL py/clear-text-logging-sensitive-data
    _secret_fp = (str(secret)[:8] + "…") if secret else "<none>"
    # codeql[py/clear-text-logging-sensitive-data]
    print(f"- `{_secret_fp}`: {count} critical workflows")  # nosec  # pragma: allowlist secret

print()
print("\n## Recommended Action Plan\n")
print("1. **IMMEDIATE** (Fix within hours):")
print("   - Fix test-suite.yml YAML parse error")
print("   - Create bandit.yaml for security scans")
print("   - Resolve src/codex_plans package structure")
print()
print("2. **HIGH PRIORITY** (Fix within 1-2 days):")
print("   - Update Docker base images (Buster → Bullseye)")
print("   - Audit and fix all nosec comments")
print("   - Test pypi-publish and build workflows")
print()
print("3. **MEDIUM PRIORITY** (Fix within 1 week):")
print("   - Review all guarded workflows")
print("   - Consolidate duplicate security workflows")
print("   - Optimize runner usage")
print()
print("4. **LOW PRIORITY** (Fix as maintenance):")
print("   - Archive unused .disabled workflows")
print("   - Update documentation")
print("   - Optimize secrets usage")
