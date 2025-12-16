from __future__ import annotations

from pathlib import Path
import subprocess

import nox

from codex_harness.golden_harness_status import compute_golden_harness_status
from codex_harness.honesty import HonestyRecorder
from codex_harness.tool_trace import ToolTraceLogger


@nox.session
def audit(session: nox.Session) -> None:
    """
    Local, offline gate:
      1) install base & dev deps
      2) run quick unit tests (including atomic diffs)
      3) run fast audit path via space.mk

    Captures honesty metadata, tool traces, and computes the golden harness
    status so downstream workflows can reason about local readiness.
    """
    artifacts_dir = Path("artifacts")
    honesty_path = artifacts_dir / "honesty_metadata.json"
    tool_trace_path = artifacts_dir / "tool_trace.ndjson"
    ra_gate_results = Path("artifacts/gates/ra_gate_results.json")

    recorder = HonestyRecorder(workflow="nox.audit", output_path=honesty_path)
    tracer = ToolTraceLogger(output_path=tool_trace_path)
    if ra_gate_results.exists():
        tracer.load_ra_gate_results(ra_gate_results)

    recorder.record_statement(
        "Starting offline audit workflow (install base & dev deps, pytest atomic_diffs, pytest, space audit).",
        category="AUDIT",
        verified=True,
    )

    success = True
    try:
        # Install base and dev requirements
        session.install("-r", "requirements/base.txt")
        session.install("-r", "requirements/dev.txt")
        recorder.record_statement(
            "Base and development dependencies installed for audit run.",
            category="ASSERTED",
            verified=True,
        )

        # Run atomic diffs test suite with environment restrictions
        atomic_diffs_invocation = tracer.run_tool(
            "pytest",
            ["-q", "tests/atomic_diffs"],
            check=True,
            env={
                "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
                "CODEX_ALLOW_REMOTE": "0",
            },
        )
        session.log(atomic_diffs_invocation.stdout)

        # Standard test suite
        pytest_invocation = tracer.run_tool("pytest", ["-q"], check=True)
        session.log(pytest_invocation.stdout)

        # Run fast audit shell target
        space_invocation = tracer.run_tool(
            "make", ["-f", "space.mk", "space-audit-fast"], check=True
        )
        if space_invocation.stdout:
            session.log(space_invocation.stdout)

    except subprocess.CalledProcessError as exc:  # pragma: no cover
        success = False
        session.log(f"[audit] tool invocation failed: {exc}")
    finally:
        recorder.record_statement(
            "Audit workflow completed",
            category="SUMMARY",
            verified=success,
        )
        recorder.flush()
        compute_golden_harness_status(
            honesty_path=honesty_path,
            tool_trace_path=tool_trace_path,
            ra_gate_path=ra_gate_results,
        )
    if not success:
        session.error("Audit workflow failed; see tool_trace.ndjson for details.")
