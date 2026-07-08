"""
pytest.importorskip("mlflow")
Test Safety

Test module for safety.
"""

# BEGIN: CODEX_SAFETY_TESTS
import importlib.util
import json
import sys
from pathlib import Path

import pytest

from codex_ml.safety import SafetyFilters, SafetyViolation
from codex_ml.safety.sandbox import run_in_sandbox
from codex_ml.utils.hf_pinning import HFModelUnavailableError

_ROOT = Path(__file__).resolve().parents[1]
_TRAINING_SPEC = importlib.util.spec_from_file_location(
    "_codex_training_module", _ROOT / "src" / "codex_ml" / "training.py"
)
assert _TRAINING_SPEC and _TRAINING_SPEC.loader is not None, "loader must be initialized"
_TRAINING_MODULE = importlib.util.module_from_spec(_TRAINING_SPEC)
sys.modules["_codex_training_module"] = _TRAINING_MODULE
_TRAINING_SPEC.loader.exec_module(_TRAINING_MODULE)
run_functional_training = _TRAINING_MODULE.run_functional_training


def _write_policy(tmp_path: Path) -> Path:
    policy = tmp_path / "policy.yaml"
    log_file = tmp_path / "events.ndjson"
    policy.write_text(
        (
            "version: 1\n"
            f"log_path: {log_file}\n"
            "rules:\n"
            "  - id: block-danger\n"
            "    action: block\n"
            "    severity: high\n"
            "    match:\n"
            '      literals: ["forbidden"]\n'
            "  - id: redact-secret\n"
            "    action: redact\n"
            "    severity: high\n"
            '    replacement: "{REDACTED}"\n'
            "    match:\n"
            '      patterns: ["SECRET[0-9]+"]\n'
        ),
        encoding="utf-8",
    )
    return policy


def test_filters_block_redact_and_log(tmp_path: Path) -> None:
    policy_path = _write_policy(tmp_path)
    filters = SafetyFilters.from_policy_file(policy_path)

    text = "forbidden SECRET123"
    with pytest.raises(SafetyViolation) as excinfo:
        filters.enforce(text, stage="prompt")
    assert "block-danger" in str(excinfo.value), "Value must be initialized"

    masked = filters.apply(text, stage="output")
    assert "{REDACTED}" in masked, "Condition must be true"

    log_file = tmp_path / "events.ndjson"
    records = [json.loads(line) for line in log_file.read_text().splitlines()]
    rule_ids = {rec["rule_id"] for rec in records}
    assert "block-danger" in rule_ids, "Condition must be true"
    assert "redact-secret" in rule_ids, "Condition must be true"


def test_filters_bypass_records_event(tmp_path: Path) -> None:
    policy_path = _write_policy(tmp_path)
    filters = SafetyFilters.from_policy_file(policy_path)
    decision = filters.evaluate("forbidden", stage="prompt", bypass=True)
    assert decision.allowed and decision.bypassed, "Condition must be true"
    log_file = tmp_path / "events.ndjson"
    entries = [json.loads(line) for line in log_file.read_text().splitlines()]
    assert any(entry["action"] == "bypass" for entry in entries), "Condition must be true"


def test_logits_masking_basic() -> None:
    filters = SafetyFilters.from_defaults()
    logits = [0.0, 1.0, 2.0, 3.0]
    out = filters.mask_logits(logits, {1, 3})
    assert out[1] == float("-inf"), "Condition must be true"
    assert out[3] == float("-inf"), "Condition must be true"


def test_training_enforces_policy(tmp_path: Path, monkeypatch) -> None:
    policy_path = _write_policy(tmp_path)
    data = tmp_path / "train.txt"
    data.write_text("forbidden entry\n", encoding="utf-8")
    # Set a dummy HF revision to avoid remote model pinning errors
    monkeypatch.setenv("CODEX_HF_REVISION", "0" * 40)
    cfg = {
        "dataset": {"train_path": str(data), "format": "text"},
        "output_dir": str(tmp_path / "runs"),
        "max_epochs": 1,
        "safety": {"policy_path": str(policy_path)},
    }

    with pytest.raises(SafetyViolation):
        run_functional_training(cfg)

    cfg["safety"]["bypass"] = True
    try:
        result = run_functional_training(cfg)
        assert result["metrics"], "Result must not be empty"
    except (OSError, ImportError, ValueError, RuntimeError, HFModelUnavailableError) as exc:
        # Model download may fail in CI/offline environments
        pytest.skip(f"Model loading unavailable: {exc}")


def test_sandbox_exec_restricts(tmp_path: Path) -> None:
    script = tmp_path / "run.sh"
    script.write_text("#!/bin/sh\necho hi > ok.txt\nenv\n", encoding="utf-8")
    script.chmod(0o700)
    cp = run_in_sandbox(["/bin/sh", str(script)], cwd=tmp_path, timeout=1, mem_mb=64)
    assert (tmp_path / "ok.txt").exists(), "Condition must be true"
    assert b"HOME" not in cp.stdout, "Condition must be true"
