#!/usr/bin/env python3
"""
Generate Verification Checklists for Post-Deployment Verification

This script generates environment-specific verification checklists
to validate successful deployment.

Usage:
    python generate_verify_checklist.py [--output-dir .codex]

Output:
    - .codex/verification-checklists/VERIFICATION_CHECKLIST_PRODUCTION.md
    - .codex/verification-checklists/VERIFICATION_CHECKLIST_STAGING.md
    - .codex/verification-checklists/VERIFICATION_CHECKLIST_DEV.md
    - .codex/VERIFICATION_CHECKLIST_GUIDE.md
"""

import sys
from pathlib import Path
from typing import Dict, List


class ChecklistItem:
    """Represents a single verification checklist item."""

    def __init__(
        self,
        name: str,
        description: str,
        verification_steps: List[str],
        expected_result: str,
        action_on_failure: str,
        estimated_time_seconds: int,
    ):
        self.name = name
        self.description = description
        self.verification_steps = verification_steps
        self.expected_result = expected_result
        self.action_on_failure = action_on_failure
        self.estimated_time_seconds = estimated_time_seconds

    def to_markdown(self) -> str:
        """Convert to markdown format."""
        md = f"### [ ] {self.name}\n\n"
        md += f"**Description:** {self.description}\n\n"
        md += "**Verification Steps:**\n"
        for step in self.verification_steps:
            md += f"- {step}\n"
        md += "\n"
        md += f"**Expected Result:** {self.expected_result}\n\n"
        md += f"**Action on Failure:** {self.action_on_failure}\n\n"
        md += f"**Estimated Time:** {self.estimated_time_seconds}s\n\n"
        return md


class ChecklistGenerator:
    """Generates environment-specific verification checklists."""

    def __init__(self):
        self.checklists: Dict[str, List[ChecklistItem]] = {}

    def generate_common_checks(self) -> List[ChecklistItem]:
        """Generate checks common to all environments."""
        return [
            ChecklistItem(
                name="Service Startup Verification",
                description="Verify that the service started successfully",
                verification_steps=[
                    "Check service process is running",
                    "Verify logs for startup errors",
                    "Confirm port bindings are active",
                ],
                expected_result="Service running with no errors in startup logs",
                action_on_failure="Check logs, restart service, check configuration",
                estimated_time_seconds=30,
            ),
            ChecklistItem(
                name="Health Endpoint Availability",
                description="Verify health check endpoints are responding",
                verification_steps=[
                    "Call GET /health endpoint",
                    "Verify 200 HTTP status",
                    "Check response contains status field",
                    "Verify response time < 500ms",
                ],
                expected_result="200 OK with valid JSON health status",
                action_on_failure="Check adapter connectivity, restart adapters, review logs",
                estimated_time_seconds=15,
            ),
            ChecklistItem(
                name="Authentication Flow",
                description="Verify authentication endpoints work correctly",
                verification_steps=[
                    "Test OAuth code exchange flow",
                    "Verify session creation",
                    "Test session cookies are set",
                    "Test authenticated request with cookie",
                ],
                expected_result="Session created, cookies set, authenticated requests succeed",
                action_on_failure="Check GitHub OAuth config, verify session store, restart service",
                estimated_time_seconds=60,
            ),
            ChecklistItem(
                name="API Request Processing",
                description="Verify core API request handling works",
                verification_steps=[
                    "Send valid JSON-RPC request",
                    "Verify request is routed correctly",
                    "Verify response format is correct",
                    "Verify response latency is acceptable",
                ],
                expected_result="Request processed, correct response returned <3000ms",
                action_on_failure="Check adapter configuration, review logs, verify network connectivity",
                estimated_time_seconds=45,
            ),
            ChecklistItem(
                name="Error Handling Verification",
                description="Verify error handling and recovery",
                verification_steps=[
                    "Send invalid request",
                    "Verify error response format",
                    "Verify error is logged",
                    "Verify service remains operational",
                ],
                expected_result="Error handled gracefully, service continues operating",
                action_on_failure="Review error handling code, check logs for patterns",
                estimated_time_seconds=30,
            ),
            ChecklistItem(
                name="Metrics and Observability",
                description="Verify metrics are being collected",
                verification_steps=[
                    "Check metrics endpoint (if available)",
                    "Verify Prometheus metrics format",
                    "Check traces in observability system",
                    "Verify request IDs are propagated",
                ],
                expected_result="Metrics available, traces visible in observability system",
                action_on_failure="Restart observability collectors, check configuration",
                estimated_time_seconds=30,
            ),
        ]

    def generate_dev_checks(self) -> List[ChecklistItem]:
        """Generate checks specific to development environment."""
        return self.generate_common_checks() + [
            ChecklistItem(
                name="Unit Tests Pass",
                description="Verify all unit tests pass",
                verification_steps=[
                    "Run: pytest tests/unit/",
                    "Verify all tests pass",
                    "Check coverage > 70%",
                ],
                expected_result="All unit tests passing, coverage > 70%",
                action_on_failure="Fix failing tests, increase coverage, update unit tests",
                estimated_time_seconds=120,
            ),
            ChecklistItem(
                name="Linting and Type Checks",
                description="Verify code quality checks pass",
                verification_steps=[
                    "Run: ruff check .",
                    "Run: mypy src/",
                    "Fix any violations",
                ],
                expected_result="No linting or type errors",
                action_on_failure="Fix linting issues, add type hints, update code",
                estimated_time_seconds=60,
            ),
        ]

    def generate_staging_checks(self) -> List[ChecklistItem]:
        """Generate checks specific to staging environment."""
        return self.generate_common_checks() + [
            ChecklistItem(
                name="Load Testing Verification",
                description="Verify system handles expected load",
                verification_steps=[
                    "Generate load: 10 concurrent requests",
                    "Monitor response times",
                    "Check error rates < 1%",
                    "Verify memory/CPU stable",
                ],
                expected_result="Handles load with <1% errors, resources stable",
                action_on_failure="Investigate performance bottlenecks, scale infrastructure, optimize code",
                estimated_time_seconds=300,
            ),
            ChecklistItem(
                name="Data Integrity Check",
                description="Verify data persists correctly",
                verification_steps=[
                    "Write test data to backend",
                    "Query test data back",
                    "Verify data matches exactly",
                    "Check no data corruption",
                ],
                expected_result="Test data persists and retrieves correctly",
                action_on_failure="Check database consistency, run recovery procedures, check storage",
                estimated_time_seconds=120,
            ),
            ChecklistItem(
                name="Integration Tests Pass",
                description="Verify integration tests pass",
                verification_steps=[
                    "Run: pytest tests/integration/",
                    "All tests pass",
                    "No flaky tests detected",
                ],
                expected_result="All integration tests passing consistently",
                action_on_failure="Fix integration test failures, investigate flakiness, update tests",
                estimated_time_seconds=180,
            ),
        ]

    def generate_production_checks(self) -> List[ChecklistItem]:
        """Generate checks specific to production environment."""
        return self.generate_common_checks() + [
            ChecklistItem(
                name="Production Load Readiness",
                description="Verify system ready for production load",
                verification_steps=[
                    "Generate load: 100+ concurrent requests",
                    "Monitor response times (p99 < 5s)",
                    "Check error rates = 0%",
                    "Verify auto-scaling active",
                    "Check backup systems functional",
                ],
                expected_result="Handles production load, p99 < 5s, 0% errors, auto-scaling works",
                action_on_failure="Scale infrastructure, optimize performance, review capacity plan",
                estimated_time_seconds=600,
            ),
            ChecklistItem(
                name="Data Backup Verification",
                description="Verify data backups are functional",
                verification_steps=[
                    "Check backup status",
                    "Verify last backup completed successfully",
                    "Test backup restore procedure (dry-run)",
                    "Verify backup retention policy",
                ],
                expected_result="Recent backups exist, restore process verified",
                action_on_failure="Trigger backup immediately, verify backup infrastructure, check storage",
                estimated_time_seconds=300,
            ),
            ChecklistItem(
                name="Security and Compliance",
                description="Verify security requirements met",
                verification_steps=[
                    "Verify TLS certificates valid",
                    "Check no exposed credentials in logs",
                    "Verify rate limiting is active",
                    "Verify authentication enforced",
                    "Check CORS policies correct",
                ],
                expected_result="TLS valid, no credentials exposed, security controls active",
                action_on_failure="Rotate certificates, audit logs, verify security configuration",
                estimated_time_seconds=120,
            ),
            ChecklistItem(
                name="Monitoring and Alerting",
                description="Verify monitoring and alerting is active",
                verification_steps=[
                    "Check all metrics being collected",
                    "Verify alerts are triggered on thresholds",
                    "Confirm on-call team has alerts",
                    "Verify dashboards showing live data",
                ],
                expected_result="All monitoring active, alerting functional, on-call team notified",
                action_on_failure="Restart monitoring stack, reconfigure alerts, notify ops team",
                estimated_time_seconds=120,
            ),
            ChecklistItem(
                name="Rollback Plan Verification",
                description="Verify rollback procedures are ready",
                verification_steps=[
                    "Review rollback procedures",
                    "Verify previous version available",
                    "Check rollback time estimate",
                    "Confirm rollback communication plan",
                ],
                expected_result="Rollback plan ready, previous version available, team briefed",
                action_on_failure="Prepare rollback procedures, ensure backup version available",
                estimated_time_seconds=60,
            ),
        ]

    def generate_checklists(self):
        """Generate all environment-specific checklists."""
        self.checklists["dev"] = self.generate_dev_checks()
        self.checklists["staging"] = self.generate_staging_checks()
        self.checklists["production"] = self.generate_production_checks()

    def save_to_files(self, output_dir: str = ".codex"):
        """Save checklists to files."""
        checklist_dir = Path(output_dir) / "verification-checklists"
        checklist_dir.mkdir(parents=True, exist_ok=True)

        # Define environment names and file names
        environments = {
            "dev": "VERIFICATION_CHECKLIST_DEV.md",
            "staging": "VERIFICATION_CHECKLIST_STAGING.md",
            "production": "VERIFICATION_CHECKLIST_PRODUCTION.md",
        }

        for env, filename in environments.items():
            md = f"# Post-Deployment Verification Checklist - {env.upper()}\n\n"
            md += f"**Environment:** {env}\n\n"
            md += f"**Total Estimated Time:** {sum(item.estimated_time_seconds for item in self.checklists[env])}s\n\n"
            md += "**Instructions:**\n"
            md += "1. Go through each item in order\n"
            md += "2. Mark checkbox when complete\n"
            md += "3. If any verification fails, follow the 'Action on Failure' guidance\n"
            md += "4. Keep track of completion time for each step\n\n"
            md += "---\n\n"

            for item in self.checklists[env]:
                md += item.to_markdown()

            filepath = checklist_dir / filename
            filepath.write_text(md)
            print(f"✓ Created {filepath}")

        # Create usage guide
        guide_file = Path(output_dir) / "VERIFICATION_CHECKLIST_GUIDE.md"
        guide = self._create_guide()
        guide_file.write_text(guide)
        print(f"✓ Created {guide_file}")

    def _create_guide(self) -> str:
        """Create verification checklist usage guide."""
        guide = """# Verification Checklist Usage Guide

## Overview

These checklists provide systematic verification procedures for post-deployment validation.

## Checklist Types

### Development Checklist
**Target Environment:** Local development or CI/CD pipeline
**Target Audience:** Developers and CI systems
**Time Budget:** ~10 minutes
**Rigor Level:** Standard (code quality + basic functionality)

Use this checklist for:
- Local testing before pushing
- CI/CD validation on every commit
- Development deployment validation

### Staging Checklist
**Target Environment:** Staging/QA environment
**Target Audience:** QA engineers and integration teams
**Time Budget:** ~15 minutes
**Rigor Level:** High (performance + integration + data integrity)

Use this checklist for:
- Pre-release validation
- Performance regression testing
- Integration testing in production-like environment

### Production Checklist
**Target Environment:** Production environment
**Target Audience:** Ops teams and deployment engineers
**Time Budget:** ~30 minutes
**Rigor Level:** Highest (load testing + security + disaster recovery)

Use this checklist for:
- Final pre-deployment validation
- Post-deployment verification
- Disaster recovery testing

## How to Use a Checklist

### 1. Preparation
- Read through the entire checklist before starting
- Gather required credentials and access tokens
- Notify relevant teams (ops, on-call, etc.)
- Start a timer to track total verification time

### 2. Execution
- Work through items in order (don't skip)
- Follow verification steps exactly as written
- Mark checkbox when item is complete
- Note any unusual observations

### 3. Failure Handling
If any verification fails:
- **STOP** - Don't continue to next items
- **Note** - Record which item failed and why
- **Follow** - Execute the "Action on Failure" guidance
- **Investigate** - Understand root cause before retrying
- **Retry** - Once fix is applied, re-run failed item

### 4. Completion
- Verify all items are checked
- Calculate total time taken
- Confirm go/no-go decision (see below)
- Archive checklist results

## Go/No-Go Decision Guide

### GO (Approve for Production)
✅ **Conditions:**
- [ ] All checklist items pass
- [ ] No critical failures encountered
- [ ] Response times within acceptable range
- [ ] Error rates at 0% (or < 1% for staging)
- [ ] All security controls verified
- [ ] Backup/rollback procedures confirmed

### CONDITIONAL (Investigate Before GO)
⚠️ **Conditions:**
- [ ] One or more warnings recorded
- [ ] Performance slightly degraded but acceptable
- [ ] Minor security considerations
- [ ] Non-critical errors that recovered

**Action:** Investigate and document before proceeding

### NO-GO (Do Not Deploy)
❌ **Conditions:**
- [ ] Critical verification failed
- [ ] Error rates > acceptable threshold
- [ ] Security controls not verified
- [ ] Performance unacceptable
- [ ] Data integrity issues detected
- [ ] Rollback procedures not ready

**Action:** Halt deployment, investigate root cause, fix, restart verification

## Integration with Automation

These checklists are integrated into:
- `scripts/deployment/generate_verify_checklist.py` - Generate dynamic checklists
- `.github/workflows/automated-post-deployment-verification.yml` - Automated workflow
- `.codex/GO_NO_GO_DECISION_MATRIX.md` - Automated decision logic

## Examples

### Example: Successful Development Verification

```
1. Service Startup ✓ (15s)
2. Health Endpoint ✓ (5s)
3. Authentication Flow ✓ (45s)
4. API Request Processing ✓ (30s)
5. Error Handling ✓ (20s)
6. Metrics Collection ✓ (10s)
7. Unit Tests ✓ (120s)
8. Linting ✓ (45s)

Total: 290s (~5 min)
Result: ✅ GO
```

### Example: Staging Verification with Issue

```
1. Service Startup ✓ (30s)
2. Health Endpoint ✓ (15s)
3. Authentication ✓ (60s)
4. API Requests ✓ (45s)
5. Error Handling ✓ (30s)
6. Metrics ✓ (30s)
7. Load Testing ⚠️ (p99=4.5s, threshold=3s) - INVESTIGATE
   - Action: Scaling investigation → Found insufficient replicas
   - Fix: Increased replicas to 5
   - Retry: p99=1.2s ✓
8. Data Integrity ✓ (120s)
9. Integration Tests ✓ (180s)

Total: 510s (~8.5 min)
Result: ✅ GO (after investigation & fix)
```

## Troubleshooting

### "Health endpoint returning degraded status"
- Check adapter connectivity
- Verify adapter credentials
- Check network connectivity to adapter services
- Restart adapter processes

### "API requests timing out"
- Check request latency metrics
- Verify adapter is not overloaded
- Check network connectivity
- Review database performance

### "Error handling verification failing"
- Verify error handlers are active
- Check error logging is functional
- Ensure circuit breakers are configured
- Review recent error patterns

## Related Documents

- `.codex/CRITICAL_PATHS_FOR_VERIFICATION.md` - Critical business paths
- `.codex/GO_NO_GO_DECISION_MATRIX.md` - Automated decision logic
- `.codex/SUCCESS_CRITERIA_BY_ENVIRONMENT.md` - Success criteria
- `.codex/SMOKE_TEST_GUIDE.md` - Automated smoke tests

## Contact

For checklist issues or updates:
- Deployment Team: #deployments on Slack
- On-Call Engineer: Check pagerduty
- Documentation: Create issue in repository
"""
        return guide


def main():
    """Main entry point."""
    output_dir = ".codex"
    if "--output-dir" in sys.argv:
        idx = sys.argv.index("--output-dir")
        if idx + 1 < len(sys.argv):
            output_dir = sys.argv[idx + 1]

    print("Generating verification checklists...")
    generator = ChecklistGenerator()
    generator.generate_checklists()
    generator.save_to_files(output_dir)
    print(f"\n✓ Verification checklists generated to {output_dir}/")


if __name__ == "__main__":
    main()
