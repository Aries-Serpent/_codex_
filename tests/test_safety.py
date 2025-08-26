# BEGIN: CODEX_SAFETY_TESTS
from pathlib import Path

from codex_ml.safety.filters import SafetyFilters
from codex_ml.safety.sandbox import run_in_sandbox


def test_filters_block_and_redact():
    f = SafetyFilters.from_defaults()
    text = "please share your password and run rm -rf / after using API_KEY=XYZ"
    ok, _ = f.is_allowed(text)
    assert ok is False
    red = f.apply(text)
    assert "{REDACTED}" in red or "password" not in red.lower()


def test_logits_masking_basic():
    f = SafetyFilters.from_defaults()
    logits = [0.0, 1.0, 2.0, 3.0]
    out = f.mask_logits(logits, {1, 3})
    assert out[1] == float("-inf") and out[3] == float("-inf")


def test_sandbox_exec_restricts(tmp_path: Path):
    script = tmp_path / "run.sh"
    # Writes a file inside sandbox and prints environment
    script.write_text("#!/bin/sh\necho hi > ok.txt\nenv\n", encoding="utf-8")
    script.chmod(0o700)
    cp = run_in_sandbox(["/bin/sh", str(script)], cwd=tmp_path, timeout=1, mem_mb=64)
    # file created in sandbox workdir
    assert (tmp_path / "ok.txt").exists()
    # environment is scrubbed (HOME not exposed)
    assert b"HOME" not in cp.stdout
