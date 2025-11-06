"""
P6 Test: Secret Context Correlation

Validates:
- Context path detection
- Keyword proximity correlation
- Elevation levels
"""
import os, json, subprocess, sys, shutil
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
        ]
    }
    (ART / "secret_entropy_report.json").write_text(json.dumps(entropy_report), encoding="utf-8")

def test_context_correlation():
    setup()
    env = os.environ.copy()
    env["SECRET_CONTEXT_ENABLE"] = "1"
    subprocess.run([sys.executable, "scripts/security/secret_context_correlate.py"], check=True, env=env)
    
    out = ART / "secret_context_report.json"
    assert out.exists()
    data = json.loads(out.read_text())
    
    assert data["total_findings"] == 2
    # At least one finding should be elevated due to path context
    assert data["elevated_findings"] >= 1
    
    # Check elevation
    elevated = data["findings"]
    assert len(elevated) > 0
    for finding in elevated:
        assert "context_indicators" in finding
        assert "elevation" in finding

def test_context_disabled():
    setup()
    env = os.environ.copy()
    env["SECRET_CONTEXT_ENABLE"] = "0"
    subprocess.run([sys.executable, "scripts/security/secret_context_correlate.py"], check=True, env=env)
    
    assert not (ART / "secret_context_report.json").exists()
