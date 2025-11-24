from __future__ import annotations

import json
import subprocess
import time
from typing import Dict, Iterable, List, Tuple

from .log import (
    REGRESSION_CATEGORIES,
    RegressionRun,
    load_regression_log,
    record_regression,
    write_coverage_report,
)

REGRESSION_MARKERS: Dict[str, str] = {
    "R1": "regression_R1",
    "R2": "regression_R2",
    "R3": "regression_R3",
    "R4": "regression_R4",
    "R5": "regression_R5",
}


def _run_pytest(marker: str, extra_args: Iterable[str] | None = None) -> Tuple[int, str]:
    args = ["pytest", "-q", "--disable-warnings", "-m", marker]
    if extra_args:
        args.extend(extra_args)
    proc = subprocess.run(args, check=False, text=True, capture_output=True)
    output = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, output


def _parse_summary(output: str) -> Dict[str, int]:
    summary: Dict[str, int] = {"passed": 0, "failed": 0, "skipped": 0}
    for line in output.splitlines():
        line = line.strip()
        if "passed" in line or "failed" in line or "skipped" in line:
            for key in list(summary.keys()):
                match = _extract_count(line, key)
                if match is not None:
                    summary[key] = match
    summary["total"] = sum(summary.values())
    return summary


def _extract_count(line: str, token: str) -> int | None:
    for part in line.split(","):
        chunk = part.strip()
        if chunk.endswith(token) or f" {token} in" in chunk:
            bits = chunk.split()
            for bit in bits:
                if bit.isdigit():
                    return int(bit)
    return None


def run_regression(
    categories: Iterable[str] | None = None, extra_pytest_args: Iterable[str] | None = None
) -> List[Dict[str, str | int]]:
    selected = list(categories) if categories else list(REGRESSION_MARKERS)
    results: List[Dict[str, str | int]] = []
    for category in selected:
        if category not in REGRESSION_CATEGORIES:
            raise ValueError(f"Unknown regression category: {category}")
        marker = REGRESSION_MARKERS.get(category)
        if not marker:
            raise ValueError(f"Unknown regression category: {category}")
        start = time.perf_counter()
        code, output = _run_pytest(marker, extra_pytest_args)
        duration = time.perf_counter() - start
        summary = _parse_summary(output)
        if code == 0:
            status = "passed"
        elif code == 5:
            status = "skipped"
        else:
            status = "failed"
        metadata = {"marker": marker, "tests": summary.get("total", 0), "exit_code": code}
        if code == 5:
            metadata["note"] = "no tests collected"
        record_regression(
            RegressionRun(
                category=category,
                name=f"pytest::{marker}",
                status=status,
                duration_s=round(duration, 3),
                details=output.strip()[-2000:],
                metadata=metadata,
            )
        )
        results.append(
            {
                "category": category,
                "marker": marker,
                "status": status,
                "tests": summary.get("total", 0),
                "passed": summary.get("passed", 0),
                "failed": summary.get("failed", 0),
                "skipped": summary.get("skipped", 0),
            }
        )
    history = load_regression_log()
    write_coverage_report(history)
    return results


if __name__ == "__main__":
    result = run_regression()
    print(json.dumps(result, indent=2))
