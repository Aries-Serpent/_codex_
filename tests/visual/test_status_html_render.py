"""
Test Status Html Render

Test module for status html render.
"""

import json
import subprocess
import sys

import pytest


@pytest.mark.skipif(
    subprocess.call(
        [sys.executable, "-c", "import importlib; importlib.import_module('playwright')"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    != 0,
    reason="playwright not installed",
)
def test_render_and_screenshot(tmp_path):
    # minimal report JSON
    rep = {
        "metadata": {
            "title": "Test Status",
            "timestamp_utc": "2025-11-02T00:00:00Z",
            "template_version": "v1.2",
            "git_context": {"branch": "test", "commit_sha_short": "deadbeef"},
            "environment": {"python_version": "3.10", "os": "linux"},
        },
        "snapshot": {
            "capabilities": [],
            "findings": [],
            "tests_gates": {
                "coverage_percent": 42.0,
                "coverage_threshold": 35,
                "tests_summary": {
                    "total": 1,
                    "passed": 1,
                    "failed": 0,
                    "skipped": 0,
                    "duration_seconds": 0,
                },
            },
        },
        "patches": [],
        "delta": {
            "tests_coverage_delta": {
                "delta_percent": 2.0,
                "previous_percent": 40.0,
                "current_percent": 42.0,
            }
        },
        "automation": {},
        "security": {},
        "questions": [],
        "decisions": [],
    }
    j = tmp_path / "r.json"
    html = tmp_path / "r.html"
    png = tmp_path / "shot.png"
    j.write_text(json.dumps(rep), encoding="utf-8")
    code = subprocess.call(
        [
            sys.executable,
            "scripts/status/render_html_report.py",
            "--json",
            str(j),
            "--out",
            str(html),
            "--template",
            "docs/templates/status/report_template_themed.html",
        ]
    )
    assert code == 0, "code is not valid"
    assert html.exists(), "Condition must be true"
    code = subprocess.call(
        [
            sys.executable,
            "scripts/status/screenshot_html.py",
            "--html",
            str(html),
            "--out",
            str(png),
        ]
    )
    assert code == 0, "code is not valid"
    assert png.exists(), "Condition must be true"
    assert png.stat().st_size > 0, "st_size must be greater than zero"
