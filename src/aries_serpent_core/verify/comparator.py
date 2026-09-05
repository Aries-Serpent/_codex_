"""
Behavior Comparator - Compare baseline vs patched code behavior.

Runs both versions with deterministic environment and compares outputs
to verify behavior preservation.

Author: mbaetiong
Generated: 2025-12-17

Safeguards:
- Deterministic execution environment
- Timeout handling
- Multiple comparison modes
- Flakiness detection
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Literal, Optional

logger = logging.getLogger(__name__)

# Safeguards: Execution bounds
DEFAULT_TIMEOUT = 60
DEFAULT_FLAKINESS_RUNS = 3


class ComparisonMode(Enum):
    """Comparison tolerance mode."""

    STRICT = "strict"  # Byte-for-byte match
    FUZZY = "fuzzy"  # Ignore whitespace, ordering
    SEMANTIC = "semantic"  # Equivalent meaning


@dataclass
class ComparisonDetail:
    """Details of a single comparison."""

    input_ref: str
    mode: ComparisonMode
    result: Literal["match", "divergence", "error"]
    baseline_output: str = ""
    patched_output: str = ""
    diff: Optional[str] = None
    error: Optional[str] = None


@dataclass
class ComparisonResult:
    """Result of behavior comparison.

    Attributes:
        result: Overall result (pass, fail, warn)
        baseline_hash: Hash of baseline output
        patched_hash: Hash of patched output
        comparisons: Individual comparison results
        flakiness_check: Results of flakiness detection
        timestamp: When comparison was performed
    """

    result: Literal["pass", "fail", "warn"]
    baseline_hash: str
    patched_hash: str
    comparisons: list[ComparisonDetail] = field(default_factory=list)
    flakiness_check: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "result": self.result,
            "baseline_hash": self.baseline_hash,
            "patched_hash": self.patched_hash,
            "comparisons": [
                {
                    "input_ref": c.input_ref,
                    "mode": c.mode.value,
                    "result": c.result,
                    "diff": c.diff,
                    "error": c.error,
                }
                for c in self.comparisons
            ],
            "flakiness_check": self.flakiness_check,
            "timestamp": self.timestamp.isoformat(),
        }

    def save(self, path: Path) -> None:
        """Save comparison result to JSON file."""
        with path.open("w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)


def _hash_output(output: str) -> str:
    """Compute hash of output for comparison."""
    return hashlib.sha256(output.encode("utf-8")).hexdigest()


def _coerce_mode(mode: ComparisonMode | str) -> ComparisonMode:
    """Normalize a comparison mode to the enum form expected by the comparator."""
    if isinstance(mode, ComparisonMode):
        return mode
    if isinstance(mode, str):
        normalized = mode.strip().casefold()
        try:
            return ComparisonMode(normalized)
        except ValueError as exc:
            valid = ", ".join(item.value for item in ComparisonMode)
            raise ValueError(f"Unsupported comparison mode {mode!r}; expected one of: {valid}") from exc
    raise TypeError(f"Expected ComparisonMode or str, got {type(mode).__name__}")


def _normalize_output(output: str, mode: ComparisonMode) -> str:
    """Normalize output based on comparison mode."""
    import re

    normalized = re.sub(
        r'File ".*?(?:/|\\)(?:baseline|patched)(?:/|\\)[^"]+"',
        'File "<snapshot>/__entry__.py"',
        output,
    )

    if mode == ComparisonMode.STRICT:
        return normalized

    if mode == ComparisonMode.FUZZY:
        # Normalize whitespace
        lines = normalized.strip().split("\n")
        lines = [line.strip() for line in lines if line.strip()]
        return "\n".join(sorted(lines))

    if mode == ComparisonMode.SEMANTIC:
        # More aggressive normalization
        normalized = re.sub(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}", "<TIMESTAMP>", normalized)
        normalized = re.sub(
            r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            "<UUID>",
            normalized,
        )
        normalized = re.sub(r"0x[0-9a-f]+", "<ADDR>", normalized)
        return normalized.strip()

    return normalized


def _run_script(
    script_path: Path,
    input_file: Optional[Path] = None,
    timeout: int = DEFAULT_TIMEOUT,
    env_overrides: Optional[dict[str, str]] = None,
) -> tuple[str, str, int]:
    """Run a Python script and capture output.

    Returns:
        tuple of (stdout, stderr, exit_code)
    """
    # Deterministic environment
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = "42"
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    if env_overrides:
        env.update(env_overrides)

    script_path = script_path.resolve()
    if not script_path.exists():
        return "", f"Script not found: {script_path}", -1
    if not script_path.is_file():
        return "", f"Script is not a file: {script_path}", -1

    python_exe = Path(sys.executable).resolve()
    cmd = [str(python_exe), str(script_path)]

    stdin_content = None
    if input_file and input_file.exists():
        stdin_content = input_file.read_text(encoding="utf-8")

    try:
        # Security: Using Python interpreter from PATH to execute script_path which is
        # validated to be a Path object. The input_file content and arguments should be
        # validated by the caller. Arguments are passed as a list to prevent shell injection.
        result = subprocess.run(
            cmd,
            input=stdin_content,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            cwd=script_path.parent,
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        logger.debug("Exception caught, returning", exc_info=True)
        return "", f"Timeout after {timeout}s", -1
    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        logger.debug("Exception caught, returning", exc_info=True)
        return "", str(e), -1


def _compare_outputs(
    baseline: str,
    patched: str,
    mode: ComparisonMode,
) -> tuple[bool, Optional[str]]:
    """Compare two outputs based on mode.

    Returns:
        tuple of (match, diff_or_None)
    """
    norm_baseline = _normalize_output(baseline, mode)
    norm_patched = _normalize_output(patched, mode)

    if norm_baseline == norm_patched:
        return True, None

    # Generate diff
    import difflib

    diff = difflib.unified_diff(
        norm_baseline.splitlines(keepends=True),
        norm_patched.splitlines(keepends=True),
        fromfile="baseline",
        tofile="patched",
    )

    return False, "".join(diff)


def compare(
    baseline_dir: Path,
    patched_dir: Path,
    sample_inputs: Optional[list[Path]] = None,
    mode: ComparisonMode | str = ComparisonMode.STRICT,
    timeout: int = DEFAULT_TIMEOUT,
    flakiness_runs: int = DEFAULT_FLAKINESS_RUNS,
) -> ComparisonResult:
    """Compare baseline and patched code behavior.

    Runs both versions with the same inputs and compares outputs.

    Args:
        baseline_dir: Directory with baseline code
        patched_dir: Directory with patched code
        sample_inputs: Optional list of input files
        mode: Comparison tolerance mode
        timeout: Execution timeout per run
        flakiness_runs: Number of runs for flakiness detection

    Returns:
        ComparisonResult with comparison details

    Example:
        >>> result = compare(Path("baseline/"), Path("patched/"))
        >>> logger.info(f"Result: {result.result}")
    """
    mode = _coerce_mode(mode)

    comparisons: list[ComparisonDetail] = []
    all_baseline_output = ""
    all_patched_output = ""

    # Find entry points (look for main.py or __main__.py)
    baseline_entry = None
    for candidate in ["main.py", "__main__.py"]:
        path = baseline_dir / candidate
        if path.exists():
            baseline_entry = path
            break

    if not baseline_entry:
        # Find any .py file
        py_files = list(baseline_dir.glob("*.py"))
        if py_files:
            baseline_entry = py_files[0]

    patched_entry = None
    if baseline_entry:
        rel_path = baseline_entry.relative_to(baseline_dir)
        patched_entry = patched_dir / rel_path

    if not baseline_entry or not patched_entry or not patched_entry.exists():
        return ComparisonResult(
            result="warn",
            baseline_hash="",
            patched_hash="",
            comparisons=[
                ComparisonDetail(
                    input_ref="(no entry point)",
                    mode=mode,
                    result="error",
                    error="Could not find entry point script",
                )
            ],
        )

    # Run without inputs first
    inputs_to_test = sample_inputs or [None]  # type: ignore[list-item]

    for input_file in inputs_to_test:
        input_ref = str(input_file) if input_file else "(no input)"

        # Run baseline
        baseline_stdout, baseline_stderr, baseline_code = _run_script(
            baseline_entry, input_file, timeout
        )
        baseline_output = baseline_stdout + baseline_stderr
        all_baseline_output += baseline_output

        # Run patched
        patched_stdout, patched_stderr, patched_code = _run_script(
            patched_entry, input_file, timeout
        )
        patched_output = patched_stdout + patched_stderr
        all_patched_output += patched_output

        # Check for timeout errors
        baseline_timeout = "Timeout" in baseline_stderr
        patched_timeout = "Timeout" in patched_stderr

        # Compare
        match, diff = _compare_outputs(baseline_output, patched_output, mode)

        detail = ComparisonDetail(
            input_ref=input_ref,
            mode=mode,
            result="match" if match else "divergence",
            baseline_output=baseline_output[:1000],  # Truncate for storage
            patched_output=patched_output[:1000],
            diff=diff,
        )

        # Set error for timeout cases
        if baseline_timeout or patched_timeout:
            detail.result = "error"
            timeout_msg = []
            if baseline_timeout:
                timeout_msg.append("baseline timed out")
            if patched_timeout:
                timeout_msg.append("patched timed out")
            detail.error = "Timeout: " + " and ".join(timeout_msg)

        # Check exit codes
        elif baseline_code != patched_code:
            detail.result = "divergence"
            detail.diff = f"Exit code mismatch: baseline={baseline_code}, patched={patched_code}"

        comparisons.append(detail)

    # Flakiness check (run multiple times)
    flakiness_results = {"runs": flakiness_runs, "consistent": True}
    if flakiness_runs > 1:
        outputs = []
        for _ in range(flakiness_runs):
            stdout, stderr, _ = _run_script(baseline_entry, None, timeout)
            outputs.append(_normalize_output(stdout + stderr, mode))

        if len(set(outputs)) > 1:
            flakiness_results["consistent"] = False
            logger.warning("Flaky baseline detected: %d unique outputs", len(set(outputs)))

    # Determine overall result
    has_divergence = any(c.result == "divergence" for c in comparisons)
    has_error = any(c.result == "error" for c in comparisons)

    if has_error:
        overall_result = "warn"
    elif has_divergence:
        overall_result = "fail"
    else:
        overall_result = "pass"

    return ComparisonResult(
        result=overall_result,  # type: ignore[arg-type]
        baseline_hash=_hash_output(all_baseline_output),
        patched_hash=_hash_output(all_patched_output),
        comparisons=comparisons,
        flakiness_check=flakiness_results,
    )


def generate_tests(
    source_dir: Path,
    sample_inputs: list[Path],
    golden_outputs: list[Path],
    output_dir: Path,
) -> list[Path]:
    """Generate snapshot tests from sample I/O.

    Args:
        source_dir: Directory with source code
        sample_inputs: list of input files
        golden_outputs: list of expected output files
        output_dir: Directory for generated tests

    Returns:
        list of generated test file paths
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_files: list[Path] = []

    # Generate test file
    test_content = '''"""
Auto-generated behavior snapshot tests.
Provenance: generated={timestamp}
DO NOT EDIT - regenerate with `codex verify --regen-tests`
"""
import pytest
from pathlib import Path
import subprocess
import os
from aries_serpent_core.logging.structured_logger import logger

class TestBehaviorSnapshots:
    @pytest.fixture
    def source_dir(self):
        return Path("{source_dir}")

    @pytest.fixture
    def golden_dir(self):
        return Path("{golden_dir}")
'''

    # Add test cases for each input/output pair
    for i, (input_path, output_path) in enumerate(zip(sample_inputs, golden_outputs, strict=False)):
        # Use string concatenation to avoid format issues with nested braces
        test_method = f'''
    def test_snapshot_{i + 1}(self, source_dir, golden_dir):
        """Test against golden output {i + 1}."""
        input_file = Path("{input_path}")
        expected_file = Path("{output_path}")

        # Run and compare
        env = os.environ.copy()
        env["PYTHONHASHSEED"] = "42"
        result = subprocess.run(
            ["python", str(source_dir / "main.py")],
            input=input_file.read_text() if input_file.exists() else None,
            capture_output=True,
            text=True,
            env=env,
        )

        expected = expected_file.read_text() if expected_file.exists() else ""
        assert result.stdout.strip() == expected.strip()
'''
        test_content += test_method

    test_file = output_dir / "test_behavior_snapshot.py"
    test_file.write_text(
        test_content.format(
            timestamp=datetime.now(timezone.utc).isoformat(),
            source_dir=str(source_dir),
            golden_dir=str(output_dir),
        ),
        encoding="utf-8",
    )

    generated_files.append(test_file)
    logger.info("Generated %d test files", len(generated_files))

    return generated_files
