"""Compatibility tests for the optional standalone telemetry package."""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]


def _run_python(source: str, *, pythonpath: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        part for part in (pythonpath, str(_ROOT / "src"), env.get("PYTHONPATH", "")) if part
    )
    return subprocess.run(
        [sys.executable, "-c", textwrap.dedent(source)],
        cwd=_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )


def test_monolith_delegates_to_installed_standalone_package(tmp_path: Path) -> None:
    (tmp_path / "codex_ml_telemetry.py").write_text(
        textwrap.dedent(
            """
            REQUEST_LATENCY = object()
            TRAIN_STEP_DURATION = object()
            EXAMPLES_PROCESSED = object()

            def render_prometheus(registry=None):
                return f"standalone-render:{registry}"
            """
        ),
        encoding="utf-8",
    )

    result = _run_python(
        """
        import codex_ml_telemetry
        from codex_ml.telemetry import metrics, server
        from codex_ml.monitoring import metrics_export

        marker = object()
        observed = []

        class Histogram:
            def observe(self, value):
                observed.append(value)

        assert metrics.REQUEST_LATENCY is codex_ml_telemetry.REQUEST_LATENCY
        assert metrics.TRAIN_STEP_DURATION is codex_ml_telemetry.TRAIN_STEP_DURATION
        assert metrics.EXAMPLES_PROCESSED is codex_ml_telemetry.EXAMPLES_PROCESSED
        metrics._HAS_PROM = True

        @metrics.track_time(Histogram())
        def operation():
            return marker

        assert operation() is marker
        assert len(observed) == 1

        calls = []
        server._HAS_PROM = True
        server.start_http_server = lambda port, addr: calls.append((port, addr))
        assert server.start_metrics_server(9123, "0.0.0.0") is True
        assert calls == [(9123, "0.0.0.0")]
        assert metrics_export.get_metrics_text("registry") == "standalone-render:registry"
        """,
        pythonpath=str(tmp_path),
    )

    assert result.returncode == 0, result.stderr


def test_monolith_falls_back_when_standalone_package_is_absent(tmp_path: Path) -> None:
    result = _run_python(
        """
        import importlib.abc
        import sys

        class BlockStandalone(importlib.abc.MetaPathFinder):
            def find_spec(self, fullname, path=None, target=None):
                if fullname == "codex_ml_telemetry" or fullname.startswith(
                    "codex_ml_telemetry."
                ):
                    raise ModuleNotFoundError(fullname)
                return None

        sys.meta_path.insert(0, BlockStandalone())

        from codex_ml.telemetry import metrics, server
        from codex_ml.monitoring import metrics_export

        class Histogram:
            observed = None

            def observe(self, value):
                self.observed = value

        histogram = Histogram()
        metrics._HAS_PROM = True

        @metrics.track_time(histogram)
        def operation():
            return "fallback"

        assert operation() == "fallback"
        assert histogram.observed is not None

        calls = []
        server._HAS_PROM = True
        server.start_http_server = lambda port, addr: calls.append((port, addr))
        assert server.start_metrics_server(9124, "127.0.0.2") is True
        assert calls == [(9124, "127.0.0.2")]

        metrics_export._HAS_PROMETHEUS = False
        assert metrics_export.get_metrics_text() == "# prometheus_client not installed\\n"
        """,
        pythonpath=str(tmp_path),
    )

    assert result.returncode == 0, result.stderr
