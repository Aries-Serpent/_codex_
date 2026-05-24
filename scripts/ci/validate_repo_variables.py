#!/usr/bin/env python3
"""
Repository Variables Validator
Validates that all critical variables are set and correctly configured.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@dataclass
class Variable:
    """Represents a repository variable requirement."""

    name: str
    description: str
    required: bool = False
    default: str | None = None
    validator: Callable[[str], bool] | None = None
    category: str = "general"


# ── Critical Variables ────────────────────────────────────────────────────────

CRITICAL_VARIABLES = [
    Variable(
        name="NODE_JS_VERSION",
        description="Target Node.js LTS version (Node.js 20 EOL: 2026-06-02)",
        required=True,
        default="22",
        validator=lambda v: v in ("20", "22", "23"),
        category="runtime",
    ),
    Variable(
        name="CODEX_CACHE_VERSION",
        description="Cache version key for pip/venv/torch caches",
        required=True,
        default="v3",
        validator=lambda v: v.startswith("v") and len(v) > 1,
        category="cache",
    ),
    Variable(
        name="CODEX_COVERAGE_THRESHOLD",
        description="Minimum test coverage threshold (%)",
        required=True,
        default="80",
        validator=lambda v: 0 <= int(v) <= 100,
        category="testing",
    ),
    Variable(
        name="COGNITIVE_BRAIN_INJECTION_ENABLED",
        description="Enable session context injection for reduced handoff loss",
        required=True,
        default="true",
        validator=lambda v: v.lower() in ("true", "false"),
        category="cognitive",
    ),
    Variable(
        name="SESSION_CONTEXT_AUTO_CAPTURE",
        description="Auto-capture session context at session start",
        required=True,
        default="true",
        validator=lambda v: v.lower() in ("true", "false"),
        category="cognitive",
    ),
]

HIGH_PRIORITY_VARIABLES = [
    Variable(
        name="CODEX_TEST_TIMEOUT_MINUTES",
        description="Global test execution timeout (minutes)",
        required=False,
        default="60",
        validator=lambda v: 1 <= int(v) <= 600,
        category="testing",
    ),
    Variable(
        name="CODEX_SHARD_COUNT",
        description="Number of test shards for parallel execution",
        required=False,
        default="4",
        validator=lambda v: 1 <= int(v) <= 16,
        category="testing",
    ),
    Variable(
        name="CODEX_LOG_LEVEL",
        description="Logging verbosity level",
        required=False,
        default="INFO",
        validator=lambda v: v in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
        category="logging",
    ),
    Variable(
        name="CODEX_MAX_HEALER_RUNS_PER_HOUR",
        description="Self-healing rate limit per hour",
        required=False,
        default="5",
        validator=lambda v: 1 <= int(v) <= 100,
        category="reliability",
    ),
]


def validate_variable(var: Variable) -> tuple[bool, str | None]:
    """Validate a single variable."""
    value = os.getenv(var.name, var.default)

    if var.required and not value:
        return False, f"CRITICAL: {var.name} is required but not set"

    if value and var.validator:
        try:
            if not var.validator(value):
                return False, f"INVALID: {var.name}={value} fails validation"
        except Exception as exc:
            return False, f"VALIDATION_ERROR: {var.name}={value}: {exc}"

    return True, None


def validate_all_variables() -> tuple[int, int]:
    """Validate all variables. Returns (passed, failed)."""
    passed = 0
    failed = 0

    all_vars = CRITICAL_VARIABLES + HIGH_PRIORITY_VARIABLES

    logger.info("Validating %d repository variables...", len(all_vars))

    for var in all_vars:
        is_valid, error = validate_variable(var)

        if is_valid:
            value = os.getenv(var.name, var.default)
            logger.info("✓ %s=%s (%s)", var.name, value, var.category)
            passed += 1
        else:
            logger.error("✗ %s", error)
            failed += 1

    return passed, failed


def generate_agent_context() -> dict[str, Any]:
    """Generate .codex/agent_context.json with current variable values."""
    context = {}

    for var in CRITICAL_VARIABLES + HIGH_PRIORITY_VARIABLES:
        value = os.getenv(var.name, var.default)
        if value:
            context[var.name] = value

    context["_meta"] = {
        "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "workflow": "repo-var-sync-schedule",
        "variables_count": len(context) - 1,
        "critical_count": len(CRITICAL_VARIABLES),
        "high_priority_count": len(HIGH_PRIORITY_VARIABLES),
    }

    return context


def print_missing_variables() -> None:
    """Print which variables are missing and need to be set."""
    missing_critical = []
    missing_high_priority = []

    for var in CRITICAL_VARIABLES:
        if not os.getenv(var.name):
            missing_critical.append(var)

    for var in HIGH_PRIORITY_VARIABLES:
        if not os.getenv(var.name):
            missing_high_priority.append(var)

    if missing_critical:
        print("\n🔴 CRITICAL Variables (Must Set Immediately):\n")
        for var in missing_critical:
            print(f"  {var.name}={var.default or '(NO DEFAULT)'}")
            print(f"     Description: {var.description}\n")

    if missing_high_priority:
        print("🟡 HIGH PRIORITY Variables (Should Set This Week):\n")
        for var in missing_high_priority:
            print(f"  {var.name}={var.default or '(NO DEFAULT)'}")
            print(f"     Description: {var.description}\n")


def save_agent_context(output_path: Path) -> None:
    """Save agent context to file."""
    context = generate_agent_context()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(context, indent=2))
    logger.info("✓ Agent context saved to %s", output_path)


if __name__ == "__main__":
    passed, failed = validate_all_variables()

    if failed > 0:
        print_missing_variables()

    logger.info("Validation complete: %d passed, %d failed", passed, failed)

    # Save agent context
    context_path = Path(".codex/agent_context.json")
    save_agent_context(context_path)

    sys.exit(0 if failed == 0 else 1)
