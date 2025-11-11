"""
Test: Token Similarity Engine (P4)

Validates:
- Disabled mode skips output
- Enabled mode produces similarity_index in range [0,1]
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ART = Path("audit_artifacts")


def setup_raw():
    if ART.exists():
        shutil.rmtree(ART)
    ART.mkdir()
    raw = {
        "capabilities": [
            {"id":"alpha","evidence_files":["a1.txt","a2.txt"]},
            {"id":"beta","evidence_files":["b1.txt"]},
        ]
    }
    (ART/"capabilities_raw.json").write_text(json.dumps(raw), encoding="utf-8")
    Path("a1.txt").write_text("foo bar baz")
    Path("a2.txt").write_text("foo bar qux")
    Path("b1.txt").write_text("solo content")


def test_similarity_enabled():
    setup_raw()
    env = os.environ.copy()
    env["TOKEN_SIMILARITY_ENABLE"]="1"
    subprocess.run([sys.executable,"scripts/metrics/token_similarity.py"],check=True,env=env)
    out = ART / "token_similarity.json"
    assert out.exists()
    data = json.loads(out.read_text())
    for cap in data["capabilities"]:
        assert 0.0 <= cap["similarity_index"] <= 1.0


def test_similarity_disabled():
    setup_raw()
    env = os.environ.copy()
    env["TOKEN_SIMILARITY_ENABLE"]="0"
    subprocess.run([sys.executable,"scripts/metrics/token_similarity.py"],check=True,env=env)
    assert not (ART/"token_similarity.json").exists()
