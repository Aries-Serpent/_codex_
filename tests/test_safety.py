# BEGIN: CODEX_SAFETY_TESTS
import importlib.util
import json
import sys
from pathlib import Path

import pytest

from codex_ml.safety import SafetyFilters, SafetyViolation
from codex_ml.safety.sandbox import run_in_sandbox

_ROOT = Path(__file__).resolve().parents[1]
_TRAINING_SPEC = importlib.util.spec_from_file_location(
    "_codex_training_module", _ROOT / "src" / "codex_ml" / "training.py"
)
assert _TRAINING_SPEC and _TRAINING_SPEC.loader is not None
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
    assert "block-danger" in str(excinfo.value)

    masked = filters.apply(text, stage="output")
    assert "{REDACTED}" in masked

    log_file = tmp_path / "events.ndjson"
    records = [json.loads(line) for line in log_file.read_text().splitlines()]
    rule_ids = {rec["rule_id"] for rec in records}
    assert "block-danger" in rule_ids
    assert "redact-secret" in rule_ids


def test_filters_bypass_records_event(tmp_path: Path) -> None:
    policy_path = _write_policy(tmp_path)
    filters = SafetyFilters.from_policy_file(policy_path)
    decision = filters.evaluate("forbidden", stage="prompt", bypass=True)
    assert decision.allowed and decision.bypassed
    log_file = tmp_path / "events.ndjson"
    entries = [json.loads(line) for line in log_file.read_text().splitlines()]
    assert any(entry["action"] == "bypass" for entry in entries)


def test_logits_masking_basic() -> None:
    filters = SafetyFilters.from_defaults()
    logits = [0.0, 1.0, 2.0, 3.0]
    out = filters.mask_logits(logits, {1, 3})
    assert out[1] == float("-inf")
    assert out[3] == float("-inf")


def test_training_enforces_policy(tmp_path: Path) -> None:
    policy_path = _write_policy(tmp_path)
    data = tmp_path / "train.txt"
    data.write_text("forbidden entry\n", encoding="utf-8")
    cfg = {
        "dataset": {"train_path": str(data), "format": "text"},
        "output_dir": str(tmp_path / "runs"),
        "max_epochs": 1,
        "safety": {"policy_path": str(policy_path)},
    }

    with pytest.raises(SafetyViolation):
        run_functional_training(cfg)

    cfg["safety"]["bypass"] = True
    result = run_functional_training(cfg)
    assert result["metrics"]


def test_sandbox_exec_restricts(tmp_path: Path) -> None:
    script = tmp_path / "run.sh"
    script.write_text("#!/bin/sh\necho hi > ok.txt\nenv\n", encoding="utf-8")
    script.chmod(0o700)
    cp = run_in_sandbox(["/bin/sh", str(script)], cwd=tmp_path, timeout=1, mem_mb=64)
    assert (tmp_path / "ok.txt").exists()
    assert b"HOME" not in cp.stdout
