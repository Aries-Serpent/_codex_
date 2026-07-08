"""
P6 Test: Secret Context Correlation

Validates:
- Context path detection
- Keyword proximity correlation
- Elevation levels
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ART = Path("audit_artifacts")


def setup():
    if ART.exists():
        shutil.rmtree(ART)
    ART.mkdir()

    # Create entropy report with findings
    entropy_report = {
        "threshold": 3.5,
        "count": 2,
        "findings": [
            {"file": "config/auth.py", "span": "AKIAABCDEFG", "entropy": 4.2},
            {"file": "utils/helpers.py", "span": "RANDOM123", "entropy": 3.8},
        ],
    }
    (ART / "secret_entropy_report.json").write_text(json.dumps(entropy_report), encoding="utf-8")


def test_context_correlation():
    setup()
    env = os.environ.copy()
    env["SECRET_CONTEXT_ENABLE"] = "1"
    env["SECRET_CONTEXT_ARTIFACT_DIR"] = str(ART.resolve())
    env["SECRET_CONTEXT_WORKSPACE_DIR"] = str(Path.cwd())
    subprocess.run(
        [sys.executable, "scripts/security/secret_context_correlate.py"], check=True, env=env
    )

    out = ART / "secret_context_report.json"
    assert out.exists(), "Condition must be true"
    data = json.loads(out.read_text())

    assert data["total_findings"] == 2, "Data must not be empty"
    # At least one finding should be elevated due to path context
    assert data["elevated_findings"] >= 1, "Value must be greater than zero"

    # Check elevation
    elevated = data["findings"]
    assert len(elevated) > 0, "Elevated must not be empty"
    for finding in elevated:
        assert "context_indicators" in finding, "Condition must be true"
        assert "elevation" in finding, "Condition must be true"


def test_context_disabled():
    setup()
    env = os.environ.copy()
    env["SECRET_CONTEXT_ENABLE"] = "0"
    env["SECRET_CONTEXT_ARTIFACT_DIR"] = str(ART.resolve())
    env["SECRET_CONTEXT_WORKSPACE_DIR"] = str(Path.cwd())
    subprocess.run(
        [sys.executable, "scripts/security/secret_context_correlate.py"], check=True, env=env
    )

    assert not (ART / "secret_context_report.json").exists(), "Condition must be true"


def test_keyword_proximity_uses_span_position():
    if ART.exists():
        shutil.rmtree(ART)
    ART.mkdir()

    secret_file = Path("temp/long_context.py")
    secret_file.parent.mkdir(parents=True, exist_ok=True)
    span = "N3WT0K3NSECRET987654321"

    filler = [f"# filler {i}" for i in range(30)]
    body = filler + [
        "def configure():",
        '    api_key = "unused"',
        f'    generated = "{span}"',
        "    return generated",
    ]
    secret_file.write_text("\n".join(body), encoding="utf-8")

    entropy_report = {
        "threshold": 3.5,
        "count": 1,
        "findings": [
            {"file": secret_file.as_posix(), "span": span, "entropy": 4.1},
        ],
    }
    (ART / "secret_entropy_report.json").write_text(json.dumps(entropy_report), encoding="utf-8")

    env = os.environ.copy()
    env["SECRET_CONTEXT_ENABLE"] = "1"
    env["SECRET_CONTEXT_WINDOW"] = "5"
    env["SECRET_CONTEXT_ARTIFACT_DIR"] = str(ART.resolve())
    env["SECRET_CONTEXT_WORKSPACE_DIR"] = str(Path.cwd())
    subprocess.run(
        [sys.executable, "scripts/security/secret_context_correlate.py"], check=True, env=env
    )

    out = ART / "secret_context_report.json"
    assert out.exists(), "Condition must be true"
    data = json.loads(out.read_text())

    match = next((f for f in data["findings"] if f.get("file") == secret_file.as_posix()), None)
    assert match is not None, "match must be initialized"
    assert "keyword:api_key" in match.get("context_indicators", [])
