#!/usr/bin/env python3
"""
CI Rescue Engine — scripts/ci/ci_rescue.py

Retrieves failed CI job logs, matches against a pattern library of known
fixes, attempts auto-remediation, and — when no pattern matches — posts a
structured @copilot RCA comment on the active PR so Copilot Coding Agents
can continue the healing loop.

Usage (called by .github/workflows/ci-rescue.yml):
    python scripts/ci/ci_rescue.py \\
        --run-id  <workflow_run_id> \\
        --pr      <pr_number>       \\
        --repo    <owner/repo>      \\
        [--token  <github_token>]   \\
        [--dry-run]

Exit codes:
    0 — rescue succeeded (all auto-fixable patterns applied, or nothing needed)
    1 — partial/no auto-fix; RCA comment posted for @copilot
    2 — error (e.g. could not retrieve logs)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# How many tail lines of job logs to fetch for pattern matching
LOG_TAIL_LINES = 300

# Maximum size of RCA comment body (GitHub caps PR comments at ~65 KB)
MAX_COMMENT_CHARS = 60_000

# ---------------------------------------------------------------------------
# Workflow environment profiles
# Maps workflow-name fragments and job-name fragments to a tailored Copilot
# test environment so agents get the exact setup they need to reproduce and
# fix failures from that specific pipeline.
# ---------------------------------------------------------------------------

@dataclass
class EnvProfile:
    """Tailored environment profile for a specific workflow / job pattern."""
    name: str
    description: str
    # Pip packages to install (in addition to base tools)
    pip_packages: list[str]
    # requirements files to install (-r <file>)
    requirements_files: list[str]
    # Package extras to install editable (e.g. "dev", "rag,dev")
    editable_extras: str
    # Commands to run before tests (setup, lint, etc.)
    pre_test_commands: list[str]
    # The exact pytest / test command used by CI
    ci_test_command: str
    # Commands that verify a fix is correct
    verify_commands: list[str]
    # AfterMath categories for this profile
    aftermath_categories: list[str]


WORKFLOW_ENV_PROFILES: dict[str, EnvProfile] = {
    # ── Resilient Validation Suite — sharded quick tests ─────────────────
    "sharded quick": EnvProfile(
        name="Resilient Validation Suite — Sharded Quick Tests",
        description=(
            "4-shard split of the full quick test suite. "
            "Each shard runs ~3.5 k tests with -m 'not slow and not integration' "
            "at --timeout=60. Uses pytest-split + least_duration algorithm."
        ),
        pip_packages=[
            "pytest>=8.2.0", "pytest-timeout>=2.3", "pytest-xdist>=3.5.0",
            "pytest-split>=0.9", "pytest-rerunfailures>=14.0",
            "detect-secrets==1.4.0",
        ],
        requirements_files=["requirements/dev.txt"],
        editable_extras="dev",
        pre_test_commands=[
            "python3 scripts/ci/sync_tracked_files.py --check",
            "python3 -m ruff check src/ tests/ --select E,F,I --quiet || true",
        ],
        ci_test_command=(
            "python -m pytest tests/ "
            "-m 'not slow and not integration' "
            "--timeout=60 --tb=short --maxfail=20 "
            "-p no:rerunfailures "
            "--splits 4 --group 1 "
            "--splitting-algorithm=least_duration -q"
        ),
        verify_commands=[
            "python -m pytest {failing_tests} -xvs --timeout=60",
            "python -m pytest tests/ -m 'not slow and not integration' --timeout=60 -q --maxfail=5",
        ],
        aftermath_categories=[
            "test_fix", "import_error", "caplog_scoping",
            "environment_mismatch", "timeout", "flaky",
        ],
    ),

    # ── Resilient Validation Suite — validation (quick / slow) ───────────
    r"validation.*quick": EnvProfile(
        name="Resilient Validation Suite — Validation (Quick)",
        description=(
            "Full quick+docs validation group. Runs "
            "python -m pytest -m 'not slow and not integration' at --timeout=60."
        ),
        pip_packages=[
            "pytest>=8.2.0", "pytest-timeout>=2.3",
            "detect-secrets==1.4.0", "pre-commit>=3",
        ],
        requirements_files=["requirements/dev.txt"],
        editable_extras="dev",
        pre_test_commands=[
            "python3 scripts/ci/sync_tracked_files.py --check",
            "pre-commit run --all-files --show-diff-on-failure || true",
        ],
        ci_test_command=(
            "python -m pytest tests/ "
            "-v -m 'not slow and not integration' "
            "--timeout=60 --tb=short --maxfail=20 "
            "--cov=src --cov-report=xml -q"
        ),
        verify_commands=[
            "python -m pytest {failing_tests} -xvs",
            "python3 scripts/run_validation.sh --fast",
        ],
        aftermath_categories=[
            "test_fix", "pre_commit", "lint", "coverage", "environment_mismatch",
        ],
    ),

    r"validation.*slow": EnvProfile(
        name="Resilient Validation Suite — Validation (Slow)",
        description=(
            "Full slow test group. Runs python -m pytest -m 'slow' "
            "at --timeout=600 with sequential execution."
        ),
        pip_packages=[
            "pytest>=8.2.0", "pytest-timeout>=2.3",
            "detect-secrets==1.4.0",
        ],
        requirements_files=["requirements/dev.txt"],
        editable_extras="dev",
        pre_test_commands=[
            "python3 scripts/ci/sync_tracked_files.py --check",
        ],
        ci_test_command=(
            "python -m pytest tests/ "
            "-v -m 'slow' "
            "--timeout=600 --maxfail=5 --tb=short"
        ),
        verify_commands=[
            "python -m pytest {failing_tests} -xvs --timeout=600",
        ],
        aftermath_categories=["slow_test", "timeout", "infrastructure"],
    ),

    # ── Validation Pipeline ────────────────────────────────────────────────
    "validation pipeline": EnvProfile(
        name="Validation Pipeline — Fast Validation",
        description=(
            "Pre-commit hook suite: end-of-file-fixer, detect-secrets, "
            "sync-tracked-files, ruff. All run in fast mode."
        ),
        pip_packages=[
            "detect-secrets==1.4.0", "pre-commit>=3",
            "ruff>=0.6.2",
        ],
        requirements_files=[],
        editable_extras="",
        pre_test_commands=[],
        ci_test_command="python3 scripts/run_validation.sh --fast",
        verify_commands=[
            "python3 scripts/ci/sync_tracked_files.py --check",
            "python3 scripts/run_validation.sh --fast",
        ],
        aftermath_categories=[
            "eof_newline", "secrets_baseline", "ruff", "sync_tracked_files",
        ],
    ),

    # ── Test — RAG Pipeline ───────────────────────────────────────────────
    "test.*rag": EnvProfile(
        name="Test — RAG Pipeline",
        description="RAG coverage gate. Must reach 85% coverage of src/codex/rag/.",
        pip_packages=[
            "pytest>=8.2.0", "pytest-cov>=4.1.0", "pytest-timeout>=2.3",
            "faiss-cpu", "sentence-transformers",
        ],
        requirements_files=["requirements/dev.txt"],
        editable_extras="rag,dev",
        pre_test_commands=[
            "python3 -c \"import codex.rag; print('RAG module OK')\"",
        ],
        ci_test_command=(
            "python -m pytest tests/rag/ "
            "--cov=src/codex/rag --cov-report=term-missing "
            "--timeout=120 -v"
        ),
        verify_commands=[
            "python -m pytest tests/rag/ --cov=src/codex/rag "
            "--cov-report=term-missing --timeout=120 -q",
        ],
        aftermath_categories=["rag_coverage", "embedding", "retrieval", "index"],
    ),

    # ── Workflow Compliance Audit (actionlint) ────────────────────────────
    r"actionlint|workflow compliance": EnvProfile(
        name="Workflow Compliance Audit (actionlint)",
        description=(
            "actionlint + shellcheck linting of all .github/workflows/*.yml files. "
            "Common failures: SC2028 (echo escape sequences), duplicate YAML keys, "
            "untrusted context values in run: scripts."
        ),
        pip_packages=[],
        requirements_files=[],
        editable_extras="",
        pre_test_commands=[
            "# Install actionlint v1.7.7 (pinned)",
            "curl -fsSL https://github.com/rhysd/actionlint/releases/download/v1.7.7/actionlint_1.7.7_linux_amd64.tar.gz | tar xz actionlint",
            "sudo mv actionlint /usr/local/bin/",
        ],
        ci_test_command=(
            "actionlint "
            "-format '{{range $e := .}}::error file={{$e.Filepath}},"
            "line={{$e.Line}}::{{$e.Message}}{{end}}' "
            ".github/workflows/*.yml"
        ),
        verify_commands=[
            "actionlint .github/workflows/*.yml",
        ],
        aftermath_categories=[
            "actionlint", "shellcheck", "SC2028", "yaml_key", "workflow_lint",
        ],
    ),
}


def _resolve_env_profile(workflow_name: str, job_name: str = "") -> EnvProfile:
    """Return the best-matching EnvProfile for the given workflow/job names."""
    combined = f"{workflow_name} {job_name}".lower()
    for key, profile in WORKFLOW_ENV_PROFILES.items():
        if re.search(key, combined):
            return profile
    # Default fallback — generic dev profile
    return EnvProfile(
        name=f"{workflow_name} (generic)",
        description="Generic test environment for unrecognised workflow.",
        pip_packages=["pytest>=8.2.0", "pytest-timeout>=2.3", "detect-secrets==1.4.0"],
        requirements_files=["requirements/dev.txt"],
        editable_extras="dev",
        pre_test_commands=["python3 scripts/ci/sync_tracked_files.py --check"],
        ci_test_command=(
            "python -m pytest tests/ -m 'not slow and not integration' "
            "--timeout=60 --tb=short -q"
        ),
        verify_commands=["python -m pytest {failing_tests} -xvs"],
        aftermath_categories=["test_fix", "environment_mismatch"],
    )

# ---------------------------------------------------------------------------
# Known-pattern library
# Each entry maps a regex against the job-log text to an auto-fix command.
# The auto-fix command is run with cwd=REPO_ROOT; a non-zero exit means the
# pattern was detected but the fix could not be applied automatically.
# ---------------------------------------------------------------------------


@dataclass
class RescuePattern:
    pattern_id: str
    description: str
    log_regexes: list[str]  # any match → pattern fires
    fix_command: Optional[list[str]]  # None = manual only
    fix_description: str = ""
    references: list[str] = field(default_factory=list)


RESCUE_PATTERNS: list[RescuePattern] = [
    RescuePattern(
        pattern_id="RP-001",
        description="E501 line-length violations (pattern 12)",
        log_regexes=[
            r"E501.*[Ll]ine too long",
            r"Pattern 12.*[Ll]ine [Ll]ength.*Found",
            r"auto-fixable.*[Ll]ine [Ll]ength",
        ],
        fix_command=["python3", "scripts/ci/auto_fix_common_issues.py", "--pattern", "12"],
        fix_description="Run `auto_fix_common_issues.py --pattern 12` to auto-wrap long lines",
        references=["auto_fix_common_issues.py:fix_line_length"],
    ),
    RescuePattern(
        pattern_id="RP-002",
        description="Unused import violations (pattern 1, ruff F401)",
        log_regexes=[
            r"F401.*imported but unused",
            r"Pattern 1.*[Uu]nused [Ii]mports.*Found",
        ],
        fix_command=["python3", "scripts/ci/auto_fix_common_issues.py", "--pattern", "1"],
        fix_description="Run `auto_fix_common_issues.py --pattern 1` to remove unused imports",
        references=["auto_fix_common_issues.py:fix_unused_imports"],
    ),
    RescuePattern(
        pattern_id="RP-003",
        description="Coverage threshold inconsistency (pattern 4)",
        log_regexes=[
            r"Pattern 4.*[Cc]overage.*Found",
            r"coverage.*threshold.*inconsisten",
        ],
        fix_command=["python3", "scripts/ci/auto_fix_common_issues.py", "--pattern", "4"],
        fix_description=(
            "Run `auto_fix_common_issues.py --pattern 4` to standardise coverage thresholds"
        ),
        references=["auto_fix_common_issues.py:fix_coverage_thresholds"],
    ),
    RescuePattern(
        pattern_id="RP-004",
        description="Tracked-file sync drift (pattern 22)",
        log_regexes=[
            r"Pattern 22.*[Tt]racked.*Found",
            r"CODEX_MANIFEST.*CHANGELOG.*accountability drift",
        ],
        fix_command=["python3", "scripts/ci/sync_tracked_files.py", "--fix"],
        fix_description=(
            "Run `sync_tracked_files.py --fix` to resync CODEX_MANIFEST / "
            "CHANGELOG / accountability report"
        ),
        references=["scripts/ci/sync_tracked_files.py"],
    ),
    RescuePattern(
        pattern_id="RP-005",
        description="Trailing whitespace in docs/ files",
        log_regexes=[
            r"Trim Trailing Whitespace.*Failed",
            r"trailing whitespace.*docs/",
            r"trailing-whitespace.*Failed",
        ],
        fix_command=[
            "bash",
            "-c",
            # Strip trailing whitespace from all modified tracked files
            "git diff --name-only HEAD -- '*.md' '*.rst' '*.txt' docs/ .codex/ | xargs -r sed -i 's/[[:space:]]*$//'",
        ],
        fix_description=(
            "Strip trailing whitespace from modified docs/config files via "
            "`git diff | xargs sed -i 's/[[:space:]]*$//'`"
        ),
        references=["S196 commit 24b868e"],
    ),
    RescuePattern(
        pattern_id="RP-006",
        description="Missing EOF newline in .codex/ JSON files",
        log_regexes=[
            r"Fix End of Files.*Failed",
            r"end-of-file-fixer.*Failed",
            r"no newline at end.*\.json",
        ],
        fix_command=[
            "bash",
            "-c",
            # Use find + xargs -0 for safe handling of any filenames
            "find .codex -name '*.json' -print0 | xargs -0 -I{} sh -c 'tail -c1 \"$1\" | grep -q . && echo >> \"$1\"' _ {}",
        ],
        fix_description="Add missing EOF newline to .codex JSON files",
        references=["S196 commit 24b868e"],
    ),
    RescuePattern(
        pattern_id="RP-007",
        description="detect-secrets baseline stale (agent_context.json hash mismatch)",
        log_regexes=[
            r"detect-secrets.*Failed",
            r"Detect secrets.*Failed",
            r"Secret in baseline.*not.*detected",
            r"agent_context\.json.*hash",
        ],
        fix_command=[
            "bash",
            "-c",
            # Single-string command for detect-secrets baseline refresh
            "python3 -m detect_secrets scan --no-verify --baseline .secrets.baseline .codex/agent_context.json 2>/dev/null || true",
        ],
        fix_description=(
            "Refresh the detect-secrets baseline for agent_context.json via "
            "`detect-secrets scan --baseline .secrets.baseline`"
        ),
        references=["S196 commit 24b868e", ".secrets.baseline"],
    ),
    RescuePattern(
        pattern_id="RP-008",
        description="actionlint duplicate YAML key (two run: blocks in one step)",
        log_regexes=[
            r"actionlint.*duplicate.*key",
            r"duplicate key.*\"run\"",
            r"Workflow Compliance Audit.*Fail",
        ],
        fix_command=None,  # requires manual merge
        fix_description=(
            "Merge the two `run:` blocks in the affected step so each step "
            "has exactly one `run:` key. Place `env:` above `run:`."
        ),
        references=["YAML workflow steps memory", "codex-manifest-refresh.yml"],
    ),
    RescuePattern(
        pattern_id="RP-009",
        description="mypy anti-regression gate exceeded baseline (too many errors)",
        log_regexes=[
            r"mypy.*[Ff]ailed",
            r"mypy.*[Ee]rror count.*exceed",
            r"Anti-Regression.*[Ff]ail",
            r"mypy.*> [0-9]+ baseline",
        ],
        fix_command=None,
        fix_description=(
            "Investigate new mypy errors introduced in recent commits. "
            "Never add `type: ignore` annotations to fallback imports when "
            "`--ignore-missing-imports` is active — the flag already "
            "suppresses them, making the annotations permanently unused."
        ),
        references=["mypy ignore annotations memory", "src/codex_ml/cli/train.py"],
    ),
    RescuePattern(
        pattern_id="RP-010",
        description="Pre-flight check failures (xdist or timeout-minutes missing)",
        log_regexes=[
            r"Pre-Flight.*[Ff]ail",
            r"pre_flight_check.*error",
            r"xdist.*without.*timeout-minutes",
        ],
        fix_command=None,
        fix_description=(
            'Check pre_flight_check.py output. Use `[ "${VAR}" != "" ]` '
            'instead of `[ -n "${VAR}" ]` in workflow bash steps to avoid '
            "false xdist warnings. Ensure timeout-minutes is set on jobs "
            "that contain pytest."
        ),
        references=["pre-flight check memory"],
    ),
    RescuePattern(
        pattern_id="RP-011",
        description="Validation Pipeline failure — composite (whitespace + EOF + secrets)",
        log_regexes=[
            r"Validation Pipeline.*[Ff]ail",
            r"Fast Validation.*[Ff]ail",
        ],
        fix_command=[
            "bash",
            "-c",
            "pre-commit run trailing-whitespace end-of-file-fixer --files $(git diff --name-only HEAD) 2>/dev/null || true",
        ],
        fix_description=(
            "Run pre-commit `trailing-whitespace` and `end-of-file-fixer` "
            "on modified files. Also verify detect-secrets baseline is fresh."
        ),
        references=["validation pipeline memory"],
    ),
    RescuePattern(
        pattern_id="RP-012",
        description="Unsorted imports (ruff I001, pattern 9)",
        log_regexes=[
            r"I001.*[Ii]mport block is un-sorted",
            r"Pattern 9.*[Uu]nsorted [Ii]mports.*Found",
        ],
        fix_command=["python3", "scripts/ci/auto_fix_common_issues.py", "--pattern", "9"],
        fix_description="Run `auto_fix_common_issues.py --pattern 9` to sort imports",
        references=["auto_fix_common_issues.py:fix_unsorted_imports"],
    ),
    # ── Resilient Validation Suite — Sharded quick tests ────────────────────
    RescuePattern(
        pattern_id="RP-013",
        description="pytest-timeout on test_pattern_recorder (CI latency > 60 s)",
        log_regexes=[
            r"TestCiPatternPipeline.*Timeout.*>60",
            r"Failed: Timeout.*test_pattern_recorder",
            r"test_check_only_returns_zero.*Timeout",
            r"test_artefact_written.*Timeout",
            r"test_main_returns_int.*Timeout",
        ],
        fix_command=None,
        fix_description=(
            "tests/ci/test_pattern_recorder.py subprocess calls use timeout=60 but CI "
            "takes longer. Fix: add @pytest.mark.timeout(180) to the three slow tests and "
            "increase subprocess timeout from 60 → 120 (already applied in S209)."
        ),
        references=["tests/ci/test_pattern_recorder.py — S209 fix"],
    ),
    RescuePattern(
        pattern_id="RP-014",
        description="AttributeError: module object at codex.archive/github lacks attribute",
        log_regexes=[
            r"AttributeError: 'module' object at codex\.(archive|github).*has no attribute",
            r"codex\.(archive|github).*no attribute",
        ],
        fix_command=None,
        fix_description=(
            "Sharded xdist workers may not have submodules fully loaded. "
            "Ensure the submodule is explicitly imported in its __init__.py "
            "or add `import codex.archive.archive` / `import codex.github.github` "
            "to the relevant __init__.py so the attribute is always available."
        ),
        references=["tests/archive/test_retry.py", "src/codex/archive/__init__.py"],
    ),
    RescuePattern(
        pattern_id="RP-015",
        description="MLflow local file backend in CI (URI mismatch / FutureWarning asserts)",
        log_regexes=[
            r"test_mlflow.*AssertionError: assert False",
            r"file:///tmp.*mlruns.*==.*uri",
            r"test_bootstrap.*allow_remote.*mlruns",
            r"test_logging.*mlruns.*!=.*uri",
        ],
        fix_command=None,
        fix_description=(
            "CI uses a local-file MLflow backend; tests assert a remote URI. "
            "Fix: mock `mlflow.get_tracking_uri()` in the test fixture, or guard "
            "with `@pytest.mark.skipif(not os.environ.get('MLFLOW_TRACKING_URI'), "
            "reason='remote MLFLOW_TRACKING_URI not set')`."
        ),
        references=[
            "tests/test_tracking_mlflow_smoke.py",
            "tests/monitoring/test_logging_bootstrap_initialization.py",
            "tests/tracking/test_mlflow_guard.py",
        ],
    ),
    RescuePattern(
        pattern_id="RP-016",
        description="context_index.json / audit artifact missing 'version' field",
        log_regexes=[
            r"context_index\.json.*missing.*version",
            r"AssertionError.*missing version field",
            r"capabilities.*json.*missing version",
        ],
        fix_command=[
            "python3",
            "scripts/audit/build_integrity_chain.py",
        ],
        fix_description=(
            "Run `python3 scripts/audit/build_integrity_chain.py` to regenerate "
            "audit artifact placeholders with proper `version` fields. "
            "Root fix in S209: build_integrity_chain.py now writes structured "
            "placeholders with `{\"version\": \"1.0\", ...}` instead of `{}`."
        ),
        references=["scripts/audit/build_integrity_chain.py — S209 fix"],
    ),
    RescuePattern(
        pattern_id="RP-017",
        description="TensorBoard not installed → test_logging_bootstrap tb=None",
        log_regexes=[
            r"test_logging_bootstrap.*assert None is not None",
            r"CodexLoggers.*tb=None",
            r"assert None is not None.*tb",
        ],
        fix_command=None,
        fix_description=(
            "TensorBoard is not installed in CI so `tb=None`. "
            "Fix (applied S209): added `pytest.importorskip('tensorboard')` to "
            "`tests/monitoring/test_codex_logging_bootstrap.py::test_logging_bootstrap` "
            "so the test skips cleanly rather than failing."
        ),
        references=["tests/monitoring/test_codex_logging_bootstrap.py — S209 fix"],
    ),
    RescuePattern(
        pattern_id="RP-018",
        description="test_security_event_logged: 'security_event' not captured by caplog",
        log_regexes=[
            r"assert 'security_event' in \[\]",
            r"test_security_event_logged.*AssertionError",
        ],
        fix_command=None,
        fix_description=(
            "caplog.set_level(INFO) without a logger name misses the 'codex.security' "
            "logger when propagate=False. Fix (applied S209): "
            "use `caplog.set_level(logging.INFO, logger='codex.security')`."
        ),
        references=["tests/security/test_audit_logging.py — S209 fix"],
    ),
    RescuePattern(
        pattern_id="RP-019",
        description="test_safe_init_no_accelerate: 'cpu_only' in CI (CUDA_VISIBLE_DEVICES='')",
        log_regexes=[
            r"assert 'cpu_only' == 'no_accelerate'",
            r"TestAccelerateInitGuard.*cpu_only",
        ],
        fix_command=None,
        fix_description=(
            "CI sets CUDA_VISIBLE_DEVICES='' which triggers the cpu_only branch even "
            "when is_accelerate_available is patched False. "
            "Fix (applied S209): added `patch.dict(os.environ, {'CUDA_VISIBLE_DEVICES': 'none'})` "
            "to isolate the no_accelerate code path."
        ),
        references=["tests/distributed/test_distributed_enhanced.py — S209 fix"],
    ),
    RescuePattern(
        pattern_id="RP-020",
        description="test_safe_write_text_warns: WARNING not captured by caplog",
        log_regexes=[
            r"test_safe_write_text_warns.*assert False",
            r"any.*levelno.*WARNING.*caplog.*records.*False",
        ],
        fix_command=None,
        fix_description=(
            "`caplog.at_level(WARNING)` without logger name misses 'codex.logging.session_hooks'. "
            "Fix (applied S209): "
            "use `caplog.at_level(logging.WARNING, logger='codex.logging.session_hooks')`."
        ),
        references=["tests/test_session_hooks_warnings.py — S209 fix"],
    ),
    RescuePattern(
        pattern_id="RP-021",
        description="actionlint SC2028 — echo may not expand escape sequences (use printf)",
        log_regexes=[
            r"SC2028.*echo may not expand escape sequences",
            r"shellcheck.*SC2028.*Use printf",
            r"echo may not expand escape sequences.*Use printf",
        ],
        fix_command=None,  # requires identifying the specific workflow file and line
        fix_description=(
            "actionlint/shellcheck SC2028: `echo \"...\\n...\"` does not expand `\\n` portably. "
            "Fix: replace `echo \"...\\n...\"` with `printf '...\\n'` (or use $'...\\n...' quoting). "
            "Example — commit 481f161 PR #3798 S229-CONT-2: "
            "`agent-auth-delegation.yml:865` — `echo \"### ...\\n\\n...\"` "
            "replaced with `printf '### ...\\n\\n...'`."
        ),
        references=[
            ".github/workflows/agent-auth-delegation.yml — S229-CONT-2 commit 481f161",
        ],
    ),
    RescuePattern(
        pattern_id="RP-022",
        description=(
            "P19 pytest @patch src.-prefix mismatch — "
            "patch target has `src.` prefix but module is imported without it"
        ),
        log_regexes=[
            r"@patch.*['\"]src\.codex\.",
            r"@patch.*['\"]src\.mcp\.",
            r"@patch.*['\"]src\.services\.",
            r"Expected .* to have been called.*Called 0 times.*patch",
            r"assert_called.*0.*times.*mock.*src\.",
        ],
        fix_command=None,  # requires identifying all affected @patch decorators
        fix_description=(
            "P19 root cause: `@patch(\"src.codex.*\")` patches a different module object than "
            "the one actually executing when the module-level import is `from codex.* import ...` "
            "(without `src.` prefix). The patch target must match the key in `sys.modules` at "
            "import time. Fix: change `@patch(\"src.codex.X.Y\")` → `@patch(\"codex.X.Y\")` "
            "to match the canonical (non-src.) import path. "
            "Example — commit 481f161 PR #3798 S229-CONT-2: "
            "`tests/rag/test_gpu_utils.py` had 15 `@patch(\"src.codex.rag.gpu_utils.*\")` "
            "targets → all changed to `@patch(\"codex.rag.gpu_utils.*\")`."
        ),
        references=[
            "tests/rag/test_gpu_utils.py — S229-CONT-2 commit 481f161",
            ".codex/issues/P19_SHADOW_IMPORTS_TRACKING.md",
        ],
    ),
    RescuePattern(
        pattern_id="RP-023",
        description=(
            "test_endpoints_have_type_hints — FastAPI endpoint handlers missing return type hints"
        ),
        log_regexes=[
            r"test_endpoints_have_type_hints",
            r"Handler type hint coverage.*< \d+%",
            r"assert.*handler.*type.hint.*coverage",
            r"FAILED.*test_endpoints_have_type_hints",
        ],
        fix_command=None,  # requires adding return type annotations to endpoint functions
        fix_description=(
            "`test_endpoints_have_type_hints` fails when the fraction of FastAPI handlers "
            "with explicit return type annotations falls below the threshold (default 20%). "
            "Fix: add `-> dict` (or a specific Pydantic model) return type hint to every "
            "`@app.get` / `@app.post` handler function in the affected file. "
            "Example — commit 481f161 PR #3798 S229-CONT-2: "
            "`src/codex_ml/serving/inference_server.py` endpoints `root()`, `health()`, "
            "`readiness()`, `liveness()` given `-> dict` hints, raising coverage 10%→50%."
        ),
        references=[
            "src/codex_ml/serving/inference_server.py — S229-CONT-2 commit 481f161",
            "tests/api/test_contract_validation.py::TestRequestResponseContracts",
            "::test_endpoints_have_type_hints",
        ],
    ),
    RescuePattern(
        pattern_id="COV_001",
        description="RAG test coverage dilution — --cov=src measures all source while only RAG tests run",
        log_regexes=[
            r"test-rag.*coverage.*[0-9]+\.[0-9]+%.*below",
            r"FAIL.*Required test coverage of.*not reached.*test.rag",
            r"coverage.*below.*threshold.*test.rag",
            r"RAG.*coverage.*5\.[0-9]+%",
            r"--cov=src.*test.rag",
        ],
        fix_command=[
            "bash",
            "-c",
            # Ensure .coveragerc for RAG scope is present and test-rag.yml uses it.
            # Parenthesised to avoid ISC001 implicit-string-concatenation lint warning.
            (
                "python3 -c \""
                "import pathlib, sys; "
                "coveragerc = pathlib.Path('tests/rag/.coveragerc'); "
                "assert coveragerc.exists(), 'tests/rag/.coveragerc missing — see S237 fix'; "
                "print('COV_001: tests/rag/.coveragerc present"
                " — verify test-rag.yml uses --cov-config=tests/rag/.coveragerc'); "
                "\""
            ),
        ],
        fix_description=(
            "RAG coverage scope dilution (COV_001): set `--cov=src/codex/rag` and "
            "`--cov-config=tests/rag/.coveragerc` in `test-rag.yml`. "
            "See `tests/rag/.coveragerc` and S237 lessons learned."
        ),
        references=[
            "tests/rag/.coveragerc",
            ".github/workflows/test-rag.yml",
            ".codex/patterns/ci_failure_patterns.yaml COV_001",
        ],
    ),
    RescuePattern(
        pattern_id="COV_002",
        description=".secrets.baseline version mismatch with detect-secrets pre-commit pin",
        log_regexes=[
            r"detect-secrets.*[Vv]ersion.*mismatch",
            r"baseline.*version.*[0-9]\.[0-9].*pre-commit.*[0-9]\.[0-9]",
            r"detect.secrets.*[Uu]pgrade.*baseline",
        ],
        fix_command=[
            "bash",
            "-c",
            "python3 -c \""
            + "import json, pathlib, re; "
            + "cfg = pathlib.Path('.pre-commit-config.yaml').read_text(); "
            + "m = re.search(r'detect-secrets.*?rev:\\s*v?([0-9.]+)', cfg, re.S); "
            + "pin = m.group(1) if m else '1.4.0'; "
            + "bl = pathlib.Path('.secrets.baseline'); "
            + "data = json.loads(bl.read_text()); "
            + "data['version'] = pin; "
            + "bl.write_text(json.dumps(data, indent=2)); "
            + "print(f'COV_002: updated .secrets.baseline version to {pin}'); "
            + "\"",
        ],
        fix_description=(
            "Baseline version mismatch (COV_002): downgrade `.secrets.baseline` "
            "`version` field to match the `detect-secrets` rev pinned in "
            "`.pre-commit-config.yaml`. Run `sync_tracked_files.py --fix` after."
        ),
        references=[
            ".secrets.baseline",
            ".pre-commit-config.yaml",
            ".codex/patterns/ci_failure_patterns.yaml COV_002",
        ],
    ),
]


# ---------------------------------------------------------------------------
# Historical analysis helpers (used by --deep mode)
# ---------------------------------------------------------------------------


def get_recent_workflow_runs(
    workflow_name: str,
    branch: str,
    repo: str,
    token: str,
    limit: int = 5,
    exclude_run_id: Optional[int] = None,
) -> list[dict]:
    """Return the last N completed runs of *workflow_name* on *branch*.

    Queries the workflow runs endpoint filtered by branch and status=completed,
    then matches by run name to handle workflows with the same branch prefix.
    """
    _, data = _gh_api(
        f"/repos/{repo}/actions/runs"
        f"?branch={branch}&status=completed&per_page=30",
        token,
    )
    if not isinstance(data, dict):
        return []
    runs = [
        r
        for r in data.get("workflow_runs", [])
        if r.get("name") == workflow_name and r.get("id") != exclude_run_id
    ]
    return runs[:limit]


def extract_failed_tests(log_text: str) -> list[str]:
    """Extract ``FAILED tests/...`` entries from a job log (strips timestamps)."""
    results: list[str] = []
    for line in log_text.splitlines():
        # Strip leading GitHub Actions timestamp (2026-03-26T05:19:24.5876598Z )
        clean = re.sub(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z\s+", "", line)
        if clean.startswith("FAILED "):
            # Take only the test id (before the " - " error summary)
            test_id = clean[7:].split(" - ")[0].strip()
            if test_id:
                results.append(test_id)
    return results


def _gh_api(
    path: str,
    token: str,
    method: str = "GET",
    body: Optional[dict] = None,
) -> tuple[int, dict | list | None]:
    """Call the GitHub REST API using curl (avoids PyGitHub dependency).

    Returns (http_status_code, parsed_json_body).  Uses a unique delimiter
    ``||HTTP_STATUS||`` appended via ``-w`` so the real HTTP status is captured
    and returned instead of always returning 200 for any successful JSON parse,
    which previously masked 4xx/5xx error responses.
    """
    _STATUS_DELIMITER = "||HTTP_STATUS||"
    cmd = [
        "curl",
        "-sS",
        "-w", _STATUS_DELIMITER + "%{http_code}",  # append delimiter + real status
        "-H",
        f"Authorization: Bearer {token}",
        "-H",
        "Accept: application/vnd.github+json",
        "-H",
        "X-GitHub-Api-Version: 2022-11-28",
    ]
    if method == "POST":
        cmd += ["-X", "POST", "-H", "Content-Type: application/json"]
        if body:
            cmd += ["-d", json.dumps(body)]
    elif method == "PATCH":
        cmd += ["-X", "PATCH", "-H", "Content-Type: application/json"]
        if body:
            cmd += ["-d", json.dumps(body)]

    cmd.append(f"https://api.github.com{path}")

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        stderr_snippet = result.stderr[:300] if result.stderr else "(no stderr)"
        print(
            f"  ⚠️  GitHub API error (exit {result.returncode}): {stderr_snippet}", file=sys.stderr
        )
        return -1, None

    # Split at the delimiter appended by -w '||HTTP_STATUS||%{http_code}'
    raw = result.stdout
    if _STATUS_DELIMITER in raw:
        split_idx = raw.rfind(_STATUS_DELIMITER)
        json_body = raw[:split_idx]
        http_status_str = raw[split_idx + len(_STATUS_DELIMITER):].strip()
    else:
        json_body = raw
        http_status_str = ""
    try:
        http_status = int(http_status_str)
    except (ValueError, TypeError):
        http_status = -1

    try:
        return http_status, json.loads(json_body) if json_body.strip() else None
    except json.JSONDecodeError as exc:
        print(f"  ⚠️  GitHub API response not valid JSON: {exc}", file=sys.stderr)
        return http_status, None


def get_failed_jobs(run_id: int, repo: str, token: str) -> list[dict]:
    """Return the list of failed jobs for a workflow run."""
    _, data = _gh_api(f"/repos/{repo}/actions/runs/{run_id}/jobs", token)
    if not isinstance(data, dict):
        return []
    return [j for j in data.get("jobs", []) if j.get("conclusion") == "failure"]


def get_job_log(job_id: int, repo: str, token: str, tail: int = LOG_TAIL_LINES) -> str:
    """Return the last `tail` lines of a job log."""
    _, raw = _gh_api(f"/repos/{repo}/actions/jobs/{job_id}/logs", token)
    if isinstance(raw, str):
        return "\n".join(raw.splitlines()[-tail:])
    # Logs often redirect; try via curl following redirects
    cmd = [
        "curl",
        "-sS",
        "-L",
        "-H",
        f"Authorization: Bearer {token}",
        "-H",
        "Accept: application/vnd.github+json",
        f"https://api.github.com/repos/{repo}/actions/jobs/{job_id}/logs",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    lines = result.stdout.splitlines()
    return "\n".join(lines[-tail:])


def find_pr_for_run(run_id: int, repo: str, token: str) -> Optional[int]:
    """Return the PR number associated with a workflow run (if any).

    When multiple PRs share the same head branch (e.g. two open PRs both
    pointing at ``0D_base_``), GitHub lists all of them in the workflow run's
    ``pull_requests`` array.  Taking ``prs[0]`` would pick the *oldest* PR,
    which is often the wrong one — rescue comments end up on a stale PR instead
    of the one whose session produced the failing commit.

    Strategy (in priority order):
    1. Among the PRs in the run's ``pull_requests`` list, prefer the one whose
       ``head.sha`` exactly matches the run's ``head_sha``.  When all SHAs match
       (same branch), fall back to step 2.
    2. Return the PR with the *highest* number (most recently opened) — this is
       the best proxy for "the PR that is currently being actively worked on".
    3. Fallback: scan open PRs via the REST API and apply the same logic.
    """
    _, data = _gh_api(f"/repos/{repo}/actions/runs/{run_id}", token)
    if not isinstance(data, dict):
        return None
    prs = data.get("pull_requests", [])
    head_sha = data.get("head_sha", "")
    if prs:
        # Prefer an exact SHA match first.
        if head_sha:
            sha_matches = [
                p for p in prs
                if p.get("head", {}).get("sha") == head_sha
            ]
            if sha_matches:
                return max(p["number"] for p in sha_matches)
        # No SHA match (shouldn't normally happen) — return highest-numbered PR.
        return max(pr["number"] for pr in prs)
    # Fallback: search open PRs for head SHA
    if head_sha:
        _, pr_data = _gh_api(f"/repos/{repo}/pulls?state=open&per_page=50", token)
        if isinstance(pr_data, list):
            matches = [
                pr for pr in pr_data
                if pr.get("head", {}).get("sha") == head_sha
            ]
            if matches:
                return max(pr["number"] for pr in matches)
    return None


def _find_rescue_sha_comment(
    pr_number: int,
    repo: str,
    token: str,
    sha12: str,
) -> tuple[int | None, str]:
    """Return (comment_id, comment_body) for ``<!-- ci-rescue-sha:{pr_number}:{sha12} -->``.

    Returns ``(None, "")`` if no such comment exists.
    """
    rescue_sha_marker = f"<!-- ci-rescue-sha:{pr_number}:{sha12} -->"
    page = 1
    while True:
        status, comments = _gh_api(
            f"/repos/{repo}/issues/{pr_number}/comments?per_page=100&page={page}", token
        )
        if status != 200 or not isinstance(comments, list) or not comments:
            break
        for c in comments:
            c_body = c.get("body") or ""
            if rescue_sha_marker in c_body:
                return c["id"], c_body
        if len(comments) < 100:
            break
        page += 1
    return None, ""


def _make_rca_marker(
    pr_number: Optional[int] = None,
    commit_sha: Optional[str] = None,
    run_id: Optional[int] = None,
) -> str:
    """Return the HTML comment marker used to identify rescue comments.

    Uses the canonical ``<!-- ci-rescue-sha:{pr_number}:{sha12} -->`` marker
    so that ALL failing workflows for the SAME push share ONE comment thread —
    matching the namespace used by ``post_rescue_comment.py``.  This prevents
    ``ci_rescue.py`` and ``post_rescue_comment.py`` from creating duplicate
    comment threads for the same commit SHA.

    A new push (different commit SHA) always creates a new comment, enabling
    per-push comparison by agents.  Appending multiple failures from different
    workflow runs into the same comment is intentional — this is the PDA Loop
    AfterMath requirement (S267).

    Falls back to legacy ``ci-rescue-rca`` PR-scoped or bare markers when
    commit_sha is unavailable, for backward compatibility.
    The ``run_id`` parameter is accepted for backward compatibility but is no
    longer used to scope the marker.
    """
    sha12 = commit_sha.strip()[:12] if commit_sha and commit_sha.strip() else None
    # Primary: canonical ci-rescue-sha namespace (shared with post_rescue_comment.py)
    if pr_number and sha12:
        return f"<!-- ci-rescue-sha:{pr_number}:{sha12} -->"
    # Legacy fallbacks when SHA is unavailable
    if pr_number:
        return f"<!-- ci-rescue-rca:{pr_number} -->"
    if sha12:
        return f"<!-- ci-rescue-rca:{sha12} -->"
    return "<!-- ci-rescue-rca -->"


def post_pr_comment(
    pr_number: int,
    repo: str,
    token: str,
    body: str,
    dry_run: bool = False,
    commit_sha: Optional[str] = None,
    run_id: Optional[int] = None,
) -> bool:
    """Post or append-update a @copilot RCA comment on the PR.

    Deduplication strategy (S267 + S294 + S298 — single-thread per SHA):
    ALL failing workflows for the same commit SHA are consolidated into ONE
    comment, shared between ``ci_rescue.py`` and ``post_rescue_comment.py``.

    Priority order (highest first):
    1. Existing ``<!-- ci-rescue-sha:{pr_number}:{sha12} -->`` anchor comment
       (posted first by ``post_rescue_comment.py`` or a prior ``ci_rescue.py``
       run) — the RCA content is appended as a ``<details>`` section.
    2. Existing ``<!-- ci-rescue-rca:{pr_number}:sha-{sha12} -->`` comment
       (legacy format from older ci_rescue.py versions) — absorbed and updated.
    3. New comment created using the canonical ``ci-rescue-sha`` marker format
       so that subsequent calls from either script share the same thread.
    4. Legacy bare ``ci-rescue-rca`` marker — only used when commit_sha is
       unavailable (backward compat for callers that don't pass a SHA).

    A NEW push (different commit SHA) always creates a NEW comment so agents
    can compare failures between pushes and track resolution progress.

    This keeps the PR thread clean: one thread per push, with a full
    chronological record of every failing workflow for that commit.
    """
    import datetime as _datetime

    sha12 = commit_sha.strip()[:12] if commit_sha and commit_sha.strip() else None

    if dry_run:
        marker = _make_rca_marker(pr_number=pr_number, commit_sha=commit_sha, run_id=run_id)
        full_body = f"{marker}\n{body}"
        print(f"\n[DRY RUN] Would post/update RCA on PR #{pr_number}:\n{full_body[:500]}…")
        return True

    # --- Preferred path: append RCA to existing rescue-sha anchor ---
    if sha12:
        rescue_sha_id, rescue_sha_body = _find_rescue_sha_comment(
            pr_number, repo, token, sha12
        )
        if rescue_sha_id:
            now = _datetime.datetime.now(
                tz=_datetime.timezone.utc
            ).strftime("%Y-%m-%dT%H:%M:%SZ")
            run_url = ""
            if run_id:
                run_url = (
                    f"https://github.com/{repo}/actions/runs/{run_id}"
                )
            run_link = (
                f" · <a href=\"{run_url}\">Run #{run_id}</a>"
                if run_id and run_url
                else ""
            )
            rca_section = (
                f"\n\n---\n\n"
                f"<details><summary>📋 <code>Root Cause Analysis</code>"
                f" — {now}{run_link}</summary>\n\n"
                f"{body}\n\n"
                f"</details>"
            )
            updated = (rescue_sha_body.rstrip() + rca_section)[:MAX_COMMENT_CHARS]
            status, _ = _gh_api(
                f"/repos/{repo}/issues/comments/{rescue_sha_id}",
                token,
                method="PATCH",
                body={"body": updated},
            )
            if status in (200, 201):
                print(
                    f"✅ Appended RCA to rescue-sha comment #{rescue_sha_id} "
                    f"(commit {sha12})"
                )
                return True
            # Fall through to legacy rca path on PATCH failure.

    marker = _make_rca_marker(pr_number=pr_number, commit_sha=commit_sha, run_id=run_id)
    full_body = f"{marker}\n{body}"

    # Scan all PR comments in a single paginated pass, checking for:
    #   1. The canonical ci-rescue-sha marker (shared with post_rescue_comment.py)
    #   2. The legacy ci-rescue-rca SHA-scoped marker (older ci_rescue.py format)
    #   3. The bare legacy ci-rescue-rca marker (oldest fallback, no SHA scope)
    # Priority order: sha-anchor > rca-sha > rca-bare
    # This ensures ci_rescue.py and post_rescue_comment.py always share ONE thread.
    existing_id: Optional[int] = None
    existing_body: str = ""
    legacy_id: Optional[int] = None
    legacy_body: str = ""
    legacy_rca_sha_id: Optional[int] = None
    legacy_rca_sha_body: str = ""
    # Build legacy rca-sha marker for backward-compat search.
    # The `if pr_number and sha12` guard ensures sha12 is a non-empty string
    # (never None) before embedding it in the f-string.
    legacy_rca_sha_marker = (
        f"<!-- ci-rescue-rca:{pr_number}:sha-{sha12} -->"
        if pr_number and sha12 and isinstance(sha12, str)
        else ""
    )
    page = 1
    while True:
        _, page_comments = _gh_api(
            f"/repos/{repo}/issues/{pr_number}/comments?per_page=100&page={page}", token
        )
        if not isinstance(page_comments, list) or not page_comments:
            break
        for c in page_comments:
            c_body = c.get("body") or ""
            if marker in c_body and not existing_id:
                existing_id = c["id"]
                existing_body = c_body
            elif (
                legacy_rca_sha_marker
                and legacy_rca_sha_marker in c_body
                and not legacy_rca_sha_id
            ):
                legacy_rca_sha_id = c["id"]
                legacy_rca_sha_body = c_body
            if "<!-- ci-rescue-rca -->" in c_body and not legacy_id:
                legacy_id = c["id"]
                legacy_body = c_body
        if len(page_comments) < 100:
            break
        page += 1

    # Three-tier resolution — highest priority wins:
    #   Tier 1 (canonical): ci-rescue-sha:{pr}:{sha12}  — shared namespace with
    #           post_rescue_comment.py; this is `existing_id` when found above.
    #   Tier 2 (legacy-sha): ci-rescue-rca:{pr}:sha-{sha12}  — old ci_rescue.py
    #           format; absorbed for backward compat with pre-S298 comment threads.
    #   Tier 3 (legacy-bare): ci-rescue-rca  — oldest fallback; only used when
    #           commit_sha is not provided (no SHA scope).
    if not existing_id and legacy_rca_sha_id:
        existing_id = legacy_rca_sha_id
        existing_body = legacy_rca_sha_body
    # Tier 3: only fall back to the bare marker when commit_sha was NOT provided.
    # When commit_sha IS provided the marker is already SHA-specific and must never
    # match an old bare <!-- ci-rescue-rca --> comment from a different push.
    if not existing_id and not commit_sha and legacy_id:
        existing_id = legacy_id
        existing_body = legacy_body

    if existing_id:
        # Append the new failure section to the existing rescue comment.
        sha_label = f" (SHA: `{commit_sha.strip()[:12]}`)" if commit_sha and commit_sha.strip() else ""
        appended = (
            existing_body.rstrip()
            + "\n\n---\n\n"
            + f"### 🔄 Failure Update{sha_label}\n\n"
            + body
        )
        if len(appended) > MAX_COMMENT_CHARS:
            appended = appended[:MAX_COMMENT_CHARS] + "\n\n_(comment truncated)_"
        status, _ = _gh_api(
            f"/repos/{repo}/issues/comments/{existing_id}",
            token,
            method="PATCH",
            body={"body": appended},
        )
    else:
        status, _ = _gh_api(
            f"/repos/{repo}/issues/{pr_number}/comments",
            token,
            method="POST",
            body={"body": full_body},
        )

    return status in (200, 201)


# ---------------------------------------------------------------------------
# Core rescue logic
# ---------------------------------------------------------------------------


@dataclass
class RescueResult:
    matched_patterns: list[RescuePattern] = field(default_factory=list)
    fixed_patterns: list[RescuePattern] = field(default_factory=list)
    failed_patterns: list[RescuePattern] = field(default_factory=list)
    unmatched_logs: list[str] = field(default_factory=list)  # job names with no pattern
    job_summaries: list[dict] = field(default_factory=list)  # {name, log_snippet}


def match_patterns(log_text: str) -> list[RescuePattern]:
    """Return all RescuePattern entries whose regexes match log_text."""
    matched = []
    for pat in RESCUE_PATTERNS:
        for rx in pat.log_regexes:
            if re.search(rx, log_text, re.IGNORECASE):
                matched.append(pat)
                break
    return matched


def attempt_fix(pattern: RescuePattern, dry_run: bool) -> bool:
    """Try to apply the fix for a pattern. Returns True if successful."""
    if pattern.fix_command is None:
        return False  # manual-only

    if dry_run:
        print(f"  [DRY RUN] Would run: {' '.join(pattern.fix_command)}")
        return True

    try:
        result = subprocess.run(
            pattern.fix_command,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        success = result.returncode == 0
        if not success:
            print(
                f"  ⚠️  Fix command failed (exit {result.returncode}):\n     {result.stderr[:400]}"
            )
        return success
    except subprocess.TimeoutExpired:
        print("  ⚠️  Fix command timed out after 120s")
        return False
    except OSError as exc:
        print(f"  ⚠️  Fix command OS error: {exc}")
        return False


def run_rescue(
    run_id: int,
    repo: str,
    token: str,
    pr_number: Optional[int],
    dry_run: bool,
) -> RescueResult:
    """Full rescue cycle: fetch logs → match → fix → report."""
    result = RescueResult()

    failed_jobs = get_failed_jobs(run_id, repo, token)
    if not failed_jobs:
        print("✅ No failed jobs found — nothing to rescue.")
        return result

    all_matched: dict[str, RescuePattern] = {}

    for job in failed_jobs:
        job_name = job.get("name", "<unknown>")
        job_id = job["id"]
        print(f"\n📋 Fetching logs for failed job: {job_name} (id={job_id})")

        log_text = get_job_log(job_id, repo, token)
        snippet = "\n".join(log_text.splitlines()[-30:]) if log_text else ""

        result.job_summaries.append(
            {
                "name": job_name,
                "job_id": job_id,
                "log_snippet": snippet,
            }
        )

        matched = match_patterns(log_text)
        if matched:
            for p in matched:
                if p.pattern_id not in all_matched:
                    all_matched[p.pattern_id] = p
                    print(f"  ✓ Matched pattern {p.pattern_id}: {p.description}")
        else:
            print(f"  ⚠️  No known pattern matched for job: {job_name}")
            result.unmatched_logs.append(job_name)

    result.matched_patterns = list(all_matched.values())

    # Attempt fixes for matched patterns
    for pat in result.matched_patterns:
        print(f"\n🔧 Attempting fix for {pat.pattern_id}: {pat.description}")
        if attempt_fix(pat, dry_run):
            print(f"  ✅ Fixed: {pat.description}")
            result.fixed_patterns.append(pat)
        else:
            print(f"  ❌ Could not auto-fix: {pat.description}")
            result.failed_patterns.append(pat)

    return result


# ---------------------------------------------------------------------------
# RCA comment builder
# ---------------------------------------------------------------------------


def _format_rca_comment(
    run_id: int,
    repo: str,
    result: RescueResult,
    timestamp: str,
    commit_sha: Optional[str] = None,
    workflow_name: str = "",
    branch: str = "",
    triage_issue_url: Optional[str] = None,
) -> str:
    """Build the @copilot RCA comment body with tailored env setup."""
    run_url = f"https://github.com/{repo}/actions/runs/{run_id}"

    lines = [
        "## 🚨 CI Rescue — Root Cause Analysis",
        "",
        f"> **Run:** [{run_id}]({run_url})  ",
        f"> **Time:** {timestamp}  ",
    ]
    if commit_sha:
        lines.append(f"> **Commit:** `{commit_sha[:12]}`  ")
    lines += [
        "> **Engine:** `scripts/ci/ci_rescue.py`",
        "",
    ]

    # --- Fixed patterns ---
    if result.fixed_patterns:
        lines.append("### ✅ Auto-Fixed")
        lines.append("")
        lines.append("| Pattern | Description | Fix Applied |")
        lines.append("|---------|-------------|-------------|")
        for p in result.fixed_patterns:
            cmd = " ".join(p.fix_command) if p.fix_command else "—"
            lines.append(f"| `{p.pattern_id}` | {p.description} | `{cmd}` |")
        lines.append("")

    # --- Patterns that could not be auto-fixed ---
    if result.failed_patterns or result.unmatched_logs:
        lines.append("### ❌ Requires Manual Fix")
        lines.append("")

        if result.failed_patterns:
            lines.append("**Known patterns with no auto-fix available:**")
            lines.append("")
            for p in result.failed_patterns:
                lines.append(f"#### `{p.pattern_id}` — {p.description}")
                lines.append("")
                lines.append(f"**Fix:** {p.fix_description}")
                if p.references:
                    lines.append(f"**Refs:** {', '.join(p.references)}")
                lines.append("")

        if result.unmatched_logs:
            lines.append("**Unrecognised failures (no pattern matched):**")
            lines.append("")
            for job_name in result.unmatched_logs:
                lines.append(f"- `{job_name}`")
            lines.append("")

        # Paste log snippets for unmatched jobs so @copilot has context
        unmatched_names = set(result.unmatched_logs)
        for summary in result.job_summaries:
            if summary["name"] in unmatched_names:
                lines.append(f"<details><summary>Log snippet — {summary['name']}</summary>")
                lines.append("")
                lines.append("```")
                lines.append(summary["log_snippet"][:3000])
                lines.append("```")
                lines.append("</details>")
                lines.append("")

    # --- @copilot continuation prompt ---
    has_unresolved = bool(result.failed_patterns or result.unmatched_logs)
    if has_unresolved:
        lines += [
            "---",
            "",
            "@copilot+claude-sonnet-4.6 please investigate and fix the CI failures above.",
            "",
            "**Instructions:**",
            "1. Review each ❌ pattern and the log snippets above",
            "2. Apply fixes in the order listed (unblocking patterns first)",
            "3. Run `python3 scripts/ci/auto_fix_common_issues.py --check-only` after each fix",
            "4. Run `actionlint .github/workflows/*.yml` if any YAML changes were made",
            "5. Commit with `fix(ci): <pattern-id> <short description>` and push",
            "6. Confirm CI is green before closing this rescue loop",
            "",
            "**Rules:** Follow `.codex/CODEBASE_AGENCY_POLICY.md` — fix ALL issues, "
            + "never defer. Never add `type: ignore` to fallback imports under "
            + "`--ignore-missing-imports`.",
        ]

    body = "\n".join(lines)

    # Append tailored env setup + AfterMath section for @copilot
    if workflow_name or branch:
        profile = _resolve_env_profile(workflow_name, "")
        failing_tests: list[str] = []
        for summary in result.job_summaries:
            failing_tests.extend(extract_failed_tests(summary.get("log_snippet", "")))
        env_section = _format_env_setup_section(
            profile, repo, branch or "0D_base_", failing_tests
        )
        body = body + "\n\n" + env_section

    # Append CI Failure Report cross-link when the triage issue URL is available.
    # This gives @copilot immediate context on ALL recent failures across workflows,
    # not just the one that triggered this rescue run.
    if triage_issue_url:
        body = body.rstrip() + _format_triage_report_footer(triage_issue_url)

    if len(body) > MAX_COMMENT_CHARS:
        body = (
            body[:MAX_COMMENT_CHARS]
            + "\n\n_(comment truncated — see Actions logs for full output)_"
        )
    return body


# ---------------------------------------------------------------------------
# Tailored Copilot environment setup + AfterMath tracking section
# ---------------------------------------------------------------------------


def _format_triage_report_footer(triage_issue_url: str) -> str:
    """Return a markdown section linking to the live CI Failure Triage Report.

    Appended to both standard and deep-rescue RCA comments so @copilot has
    immediate cross-workflow failure context in every rescue thread.
    """
    return (
        "\n\n---\n\n"
        "### 📊 CI Failure Report — cross-workflow context\n\n"
        f"The live **[CI Failure Triage Report]({triage_issue_url})** "
        "shows all recent workflow failures across this repository. "
        "Review it to identify recurring patterns or co-occurring failures "
        "before applying fixes.\n\n"
        f"> **Report:** {triage_issue_url}\n"
    )


def _format_env_setup_section(
    profile: EnvProfile,
    repo: str,
    branch: str,
    failing_tests: list[str],
) -> str:
    """
    Generate a self-contained 'Copilot Test Environment Setup' section.

    Produces copy-paste-ready blocks covering:
      1. Branch sync + dependency install (exact packages used by CI)
      2. Pre-test environment validation commands
      3. Exact CI test command for this workflow/job
      4. Targeted reproduction commands for each failing test
      5. AfterMath tracking table (pre-filled; @copilot updates it)
    """
    lines: list[str] = [
        "---",
        "",
        "## 🛠️ Copilot Test Environment Setup",
        f"> **Profile:** `{profile.name}`",
        f"> **Purpose:** {profile.description}",
        "",
        "### Step 1 — Branch sync",
        "```bash",
        f"git checkout {branch} && git pull origin {branch}",
        "```",
        "",
        "### Step 2 — Install dependencies (exact CI environment)",
        "```bash",
    ]

    # Editable install
    if profile.editable_extras:
        lines.append(f'python -m pip install -e ".[{profile.editable_extras}]" --quiet')
    else:
        lines.append("python -m pip install -e . --quiet")

    # requirements files
    for req in profile.requirements_files:
        lines.append(f"pip install -r {req} --quiet")

    # extra packages
    if profile.pip_packages:
        pkg_str = " ".join(f'"{p}"' for p in profile.pip_packages)
        lines.append(f"pip install {pkg_str} --quiet")

    lines += ["```", ""]

    # Pre-test commands
    if profile.pre_test_commands:
        lines += ["### Step 3 — Pre-test validation", "```bash"]
        lines.extend(profile.pre_test_commands)
        lines += ["```", ""]
        step4 = "4"
    else:
        step4 = "3"

    # Exact CI command
    lines += [
        f"### Step {step4} — Reproduce with exact CI command",
        "```bash",
        "# Exact command used by CI for this job:",
        profile.ci_test_command,
        "```",
        "",
    ]

    # Targeted failing-test commands
    if failing_tests:
        step5 = str(int(step4) + 1)
        lines += [f"### Step {step5} — Reproduce individual failures", "```bash"]
        for t in failing_tests[:10]:
            verify = profile.verify_commands[0].format(failing_tests=t) if profile.verify_commands else f"python -m pytest {t} -xvs"
            lines.append(verify)
        if len(failing_tests) > 10:
            lines.append(f"# …and {len(failing_tests) - 10} more (see failures above)")
        lines += ["```", ""]
        step6 = str(int(step5) + 1)
    else:
        step6 = str(int(step4) + 1)

    # Full verification after fixes
    if len(profile.verify_commands) > 1:
        lines += [f"### Step {step6} — Full verification after fixes", "```bash"]
        for cmd in profile.verify_commands[1:]:
            lines.append(cmd.format(failing_tests=" ".join(failing_tests[:3])))
        lines += ["```", ""]

    # AfterMath tracking table
    categories = profile.aftermath_categories or ["fix_applied", "regression", "infrastructure"]
    lines += [
        "---",
        "",
        "## 📋 AfterMath Tracking (update after each fix attempt)",
        "",
        "| # | Test / Issue | Fix Applied | Outcome | Category | Notes |",
        "|---|-------------|-------------|---------|----------|-------|",
    ]
    for i, test in enumerate(failing_tests[:8], 1):
        short = test.split("::")[-1] if "::" in test else test
        lines.append(f"| {i} | `{short}` | _pending_ | ⏳ | _tbd_ | |")
    if not failing_tests:
        lines.append("| 1 | _tbd_ | _pending_ | ⏳ | _tbd_ | |")
    lines += [
        "",
        "**Outcome key:** ✅ Fixed · ❌ Not fixed · ⏳ In progress · "
        "🔁 Flaky (needs reruns) · 🏗️ Infrastructure (not code-fixable)",
        "",
        f"**AfterMath categories for this profile:** "
        f"`{'`, `'.join(categories)}`",
        "",
        "> After completing all fixes, update the table above and store "
        "> key lessons with `store_memory` so future agents benefit.",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Deep rescue — COPILOT_AGENT_AUTH_ENABLED historical analysis mode
# ---------------------------------------------------------------------------


def _format_deep_rca_comment(
    run_id: int,
    repo: str,
    timestamp: str,
    workflow_name: str,
    branch: str,
    current_failures: dict[str, list[str]],
    historical_runs: list[dict],
    recurring: dict[str, int],
    sporadic: dict[str, int],
    new_failures: set[str],
    matched_patterns: list[RescuePattern],
    commit_sha: Optional[str],
    triage_issue_url: Optional[str] = None,
) -> str:
    """Build the comprehensive deep-rescue @copilot escalation comment body."""
    run_url = f"https://github.com/{repo}/actions/runs/{run_id}"
    total_hist = len(historical_runs)

    lines = [
        "## 🔍 Deep CI Analysis — `COPILOT_AGENT_AUTH_ENABLED` Mode",
        "",
        f"> **Workflow:** `{workflow_name}`  ",
        f"> **Branch:** `{branch}`  ",
        f"> **Run:** [{run_id}]({run_url})  ",
        f"> **Time:** {timestamp}  ",
        f"> **Historical runs analyzed:** {total_hist}  ",
    ]
    if commit_sha:
        lines.append(f"> **Commit:** `{commit_sha[:12]}`  ")
    lines += ["", "---", ""]

    # --- Current failures summary ----------------------------------------
    total_current = sum(len(v) for v in current_failures.values())
    job_count = len(current_failures)
    lines += [
        f"### 🔴 Current Failures ({total_current} tests across {job_count} jobs)",
        "",
    ]
    for job_name, tests in sorted(current_failures.items()):
        if tests:
            lines.append(f"**{job_name}** ({len(tests)} failures):")
            for t in tests[:12]:
                short = t.split("::")[-1] if "::" in t else t
                lines.append(f"- `{short}`")
            if len(tests) > 12:
                lines.append(f"- _…and {len(tests) - 12} more_")
            lines.append("")

    # --- Historical pattern analysis -------------------------------------
    if total_hist > 0:
        lines += ["### 📊 Historical Pattern Analysis", ""]

        if recurring:
            lines += [
                f"**Recurring** (≥2 of last {total_hist} runs — systematic, need code fixes):",
                "",
                "| Test | Seen in | Priority |",
                "|------|---------|----------|",
            ]
            for test, count in sorted(recurring.items(), key=lambda x: -x[1]):
                pct = int(100 * count / max(total_hist, 1))
                priority = "🔴 High" if pct >= 60 else "🟡 Medium"
                short = test.split("::")[-1] if "::" in test else test
                lines.append(f"| `{short}` | {count}/{total_hist} ({pct}%) | {priority} |")
            lines.append("")

        if sporadic:
            lines += ["**Sporadic** (single occurrence — likely flaky/environment):", ""]
            for test in sorted(sporadic.keys()):
                short = test.split("::")[-1] if "::" in test else test
                lines.append(f"- `{short}`")
            lines.append("")

        if new_failures:
            lines += ["**New** (not seen in prior runs — check recent commits):", ""]
            for test in sorted(new_failures):
                short = test.split("::")[-1] if "::" in test else test
                lines.append(f"- `{short}`")
            lines.append("")

    # --- Matched rescue patterns -----------------------------------------
    if matched_patterns:
        lines += ["### 🔧 Matched Rescue Patterns", ""]
        for p in matched_patterns:
            auto = f"`{'  '.join(p.fix_command)}`" if p.fix_command else "manual only"
            lines += [
                f"#### `{p.pattern_id}` — {p.description}",
                "",
                f"**Fix:** {p.fix_description}  ",
                f"**Auto-fix:** {auto}",
                "",
            ]

    # --- @copilot escalation prompt --------------------------------------
    lines += [
        "---",
        "",
        "@copilot+claude-sonnet-4.6 — **deep rescue escalation (COPILOT_AGENT_AUTH_ENABLED)**",
        "",
        "The above analysis covers **current and historical** CI failures on "
        f"`{branch}`. Please:",
        "",
        "1. **Fix recurring failures first** (systematic — block every PR):",
    ]
    priority_items = [p for p in matched_patterns if p.fix_command]
    if priority_items:
        for p in priority_items:
            lines.append(f"   - [{p.pattern_id}] {p.fix_description}")
    elif recurring:
        for test in list(recurring.keys())[:5]:
            short = test.split("::")[-1] if "::" in test else test
            lines.append(f"   - `{short}`")

    lines += [
        "",
        "2. **Investigate new failures** — verify they are not caused by recent commits",
        "3. **Mark confirmed-flaky tests** with `@pytest.mark.flaky(reruns=2)` "
        "+ add to `.codex/permanent_facts.md`",
        "4. **Update `.secrets.baseline`** if `CODEX_MANIFEST.json` changed: "
        "`python3 scripts/ci/sync_tracked_files.py --fix`",
        "5. **Follow** `.codex/CODEBASE_AGENCY_POLICY.md` §0 — fix ALL issues, never defer",
        "",
        "_Posted by: ci-rescue.yml → deep-rescue step (`COPILOT_AGENT_AUTH_ENABLED` mode)_",
    ]

    # Append tailored env setup + AfterMath section
    profile = _resolve_env_profile(workflow_name, "")
    all_failing = [t for tests in current_failures.values() for t in tests]
    env_section = _format_env_setup_section(profile, repo, branch, all_failing)
    lines_with_env = "\n".join(lines) + "\n\n" + env_section

    body = lines_with_env

    # Append CI Failure Report cross-link when triage issue URL is available.
    if triage_issue_url:
        body = body.rstrip() + _format_triage_report_footer(triage_issue_url)

    if len(body) > MAX_COMMENT_CHARS:
        body = body[:MAX_COMMENT_CHARS] + "\n\n_(truncated — see Actions logs for full output)_"
    return body


def run_deep_rescue(
    current_run_id: int,
    repo: str,
    token: str,
    pr_number: Optional[int],
    workflow_name: str,
    branch: str,
    dry_run: bool,
    commit_sha: Optional[str],
    triage_issue_url: Optional[str] = None,
) -> int:
    """Historical analysis mode: analyse last N runs and build pattern frequency map.

    Posts a comprehensive @copilot escalation that distinguishes recurring
    (systematic) failures from sporadic (flaky) ones, enabling targeted fixes.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(
        f"\n🔍 Deep Rescue — historical analysis for '{workflow_name}' on '{branch}'"
        f" @ {timestamp}"
    )

    # 1. Analyse current run -------------------------------------------------
    current_failed_jobs = get_failed_jobs(current_run_id, repo, token)
    current_failures: dict[str, list[str]] = {}
    all_current_log_text = ""

    for job in current_failed_jobs:
        job_name = job.get("name", "<unknown>")
        log_text = get_job_log(job["id"], repo, token)
        all_current_log_text += "\n" + log_text
        current_failures[job_name] = extract_failed_tests(log_text)

    all_current_tests: set[str] = {t for tests in current_failures.values() for t in tests}
    print(f"  Current run: {len(current_failed_jobs)} failed job(s), "
          f"{len(all_current_tests)} failed test(s)")

    # 2. Fetch historical runs -----------------------------------------------
    historical_runs = get_recent_workflow_runs(
        workflow_name, branch, repo, token, limit=5, exclude_run_id=current_run_id
    )
    print(f"  Historical runs found: {len(historical_runs)}")

    # 3. Build failure-frequency table across historical runs ----------------
    frequency: dict[str, int] = {}
    for run in historical_runs:
        run_failed_jobs = get_failed_jobs(run["id"], repo, token)
        run_tests: set[str] = set()
        for job in run_failed_jobs:
            log_text = get_job_log(job["id"], repo, token, tail=150)
            run_tests.update(extract_failed_tests(log_text))
        for test in run_tests:
            frequency[test] = frequency.get(test, 0) + 1

    # 4. Classify failures ---------------------------------------------------
    recurring = {t: c for t, c in frequency.items() if t in all_current_tests and c >= 2}
    sporadic = {t: c for t, c in frequency.items() if t in all_current_tests and c == 1}
    new_failures = {t for t in all_current_tests if t not in frequency}

    print(f"  Recurring: {len(recurring)}, sporadic: {len(sporadic)}, "
          f"new: {len(new_failures)}")

    # 5. Match rescue patterns against current log text ----------------------
    matched_patterns = match_patterns(all_current_log_text)
    print(f"  Pattern matches: {len(matched_patterns)}")

    # 6. Post deep RCA comment -----------------------------------------------
    if pr_number:
        comment = _format_deep_rca_comment(
            current_run_id, repo, timestamp, workflow_name, branch,
            current_failures, historical_runs,
            recurring, sporadic, new_failures,
            matched_patterns, commit_sha,
            triage_issue_url=triage_issue_url,
        )
        # Append deep analysis into the SHA-scoped RCA comment so the PR
        # thread has ONE rescue thread per push, not one per workflow run.
        # post_pr_comment() implements SHA-scoped upsert: it finds the
        # existing <!-- ci-rescue-rca:{pr_number}:sha-{sha12} --> comment and appends there, or
        # creates a fresh one if this is the first failure for this commit.
        print(f"\n📝 Appending deep analysis to rescue comment on PR #{pr_number}…")
        success = post_pr_comment(
            pr_number=pr_number,
            repo=repo,
            token=token,
            body=comment,
            dry_run=dry_run,
            commit_sha=commit_sha,
            run_id=current_run_id,
        )
        if success:
            print("  ✅ Deep analysis appended to rescue comment")
        else:
            print("  ⚠️  Failed to append deep analysis", file=sys.stderr)
    else:
        print("  ⚠️  No PR resolved — deep RCA comment skipped")

    return 0


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True, type=int, help="Workflow run ID")
    parser.add_argument("--pr", type=int, default=None, help="PR number (auto-detected if omitted)")
    parser.add_argument("--repo", required=True, help="owner/repo")
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"), help="GitHub token")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without executing")
    parser.add_argument(
        "--commit-sha",
        default=None,
        help=(
            "Head commit SHA of the triggering workflow run. "
            "Used to deduplicate rescue comments: subsequent failures "
            "on the same commit are appended to the existing rescue "
            "comment rather than creating a new one."
        ),
    )
    # ── Deep mode (COPILOT_AGENT_AUTH_ENABLED) ─────────────────────────────
    parser.add_argument(
        "--deep",
        action="store_true",
        help=(
            "Enable historical analysis mode. Fetches logs from the last N runs "
            "of the same workflow on the same branch and posts a comprehensive "
            "@copilot escalation with recurring vs sporadic pattern breakdown. "
            "Activated automatically when COPILOT_AGENT_AUTH_ENABLED=true."
        ),
    )
    parser.add_argument(
        "--workflow-name",
        default=None,
        help="Name of the triggering workflow (required for --deep mode).",
    )
    parser.add_argument(
        "--branch",
        default=None,
        help="Branch name (required for --deep mode historical lookup).",
    )
    parser.add_argument(
        "--triage-issue-url",
        default=None,
        help=(
            "URL of the live CI Failure Triage Report issue (batch-ci-triage.yml). "
            "When provided, a cross-workflow context link is appended to the RCA "
            "comment so @copilot can see all recent failures in one click."
        ),
    )
    args = parser.parse_args()

    if not args.token:
        print("❌ No GitHub token provided (--token or GITHUB_TOKEN env var)", file=sys.stderr)
        return 2

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"🔬 CI Rescue Engine starting — run {args.run_id} @ {timestamp}")

    # Resolve PR number
    pr_number = args.pr
    if pr_number is None:
        pr_number = find_pr_for_run(args.run_id, args.repo, args.token)
        if pr_number:
            print(f"🔗 Resolved PR #{pr_number} for run {args.run_id}")
        else:
            print("⚠️  Could not resolve a PR for this run — RCA comment will be skipped")

    # ── Deep mode: historical analysis + @copilot escalation ───────────────
    if args.deep:
        wf_name = args.workflow_name or "unknown"
        branch = args.branch or "unknown"
        return run_deep_rescue(
            args.run_id, args.repo, args.token,
            pr_number, wf_name, branch,
            args.dry_run, args.commit_sha,
            triage_issue_url=args.triage_issue_url,
        )

    # ── Standard rescue cycle ───────────────────────────────────────────────
    result = run_rescue(args.run_id, args.repo, args.token, pr_number, args.dry_run)

    # Summarise
    print("\n" + "=" * 60)
    print(f"Matched:     {len(result.matched_patterns)} pattern(s)")
    print(f"Fixed:       {len(result.fixed_patterns)} pattern(s)")
    print(f"Unfixed:     {len(result.failed_patterns)} pattern(s)")
    print(f"Unmatched:   {len(result.unmatched_logs)} job(s)")
    print("=" * 60)

    has_unresolved = bool(result.failed_patterns or result.unmatched_logs)

    # Post RCA comment if there are unresolved issues
    if has_unresolved and pr_number:
        comment_body = _format_rca_comment(
            args.run_id, args.repo, result, timestamp, args.commit_sha,
            workflow_name=args.workflow_name or "",
            branch=args.branch or "",
            triage_issue_url=args.triage_issue_url,
        )
        print(f"\n📝 Posting RCA comment to PR #{pr_number}…")
        ok = post_pr_comment(
            pr_number,
            args.repo,
            args.token,
            comment_body,
            args.dry_run,
            args.commit_sha,
            args.run_id,
        )
        if ok:
            print("  ✅ RCA comment posted")
        else:
            print("  ⚠️  Failed to post comment", file=sys.stderr)

    # Exit code
    if has_unresolved:
        print("\n⚠️  Some failures require manual attention — exit 1")
        return 1

    if result.fixed_patterns:
        print("\n✅ All matched patterns auto-fixed — exit 0")
    else:
        print("\n✅ No actionable failures — exit 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
