"""Stage 2 acceptance: deterministic signal -> pattern -> proposal slice."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from aries_serpent_core.cognitive.brain_interface import AgentBrainInterface
from codex.cognitive_brain.authority import AuthorityEnvelope
from codex.cognitive_brain.improvement_pipeline import (
    ImprovementPipeline,
    load_pda_signals,
    signal_from_pda_record,
)

PATTERN_STORE = {
    "patterns": {
        "ci_timeout": {
            "id": "RP-019",
            "category": "ci_cd",
            "symptoms": [
                "ci job failure timeout",
                "workflow timeout minutes",
                "job timed out",
                "pytest",
            ],
            "solutions": ["jobs:\n  test:\n    timeout-minutes: 30"],
            "success_rate": 0.9,
            "times_applied": 3,
        }
    }
}


def _brain(tmp_path: Path) -> AgentBrainInterface:
    store_dir = tmp_path / ".codex" / "cognitive_brain"
    store_dir.mkdir(parents=True, exist_ok=True)
    (store_dir / "pattern_learning_store.json").write_text(json.dumps(PATTERN_STORE))
    return AgentBrainInterface(agent_id="test-agent", repo_root=tmp_path, auto_register=False)


def _pipeline(tmp_path: Path) -> ImprovementPipeline:
    return ImprovementPipeline(
        repo="Aries-Serpent/_codex_",
        ref="refs/heads/main",
        sha="cd47831318fe",  # pragma: allowlist secret
        brain_interface=_brain(tmp_path),
        authority=AuthorityEnvelope(require_human_approval=False),
    )


@pytest.mark.parametrize("directory", [".", "src", "src/nested", "docs"])
@pytest.mark.parametrize("nested_temp", [False, True])
def test_actual_patch_inventory_is_independent_of_cwd(
    tmp_path, monkeypatch, directory, nested_temp
):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "src/nested").mkdir(parents=True)
    (tmp_path / "docs").mkdir()
    if nested_temp:
        monkeypatch.setattr(tempfile, "tempdir", str(tmp_path / "src"))
    pipeline = ImprovementPipeline(
        repo="fixture/repo", ref="main", sha="a" * 40, brain_interface=None
    )
    patch = b"""diff --git a/src/value.py b/src/value.py
--- a/src/value.py
+++ b/src/value.py
@@ -1 +1 @@
-value = 1
+value = 2
diff --git a/docs/value.txt b/docs/value.txt
--- a/docs/value.txt
+++ b/docs/value.txt
@@ -1 +1 @@
-before
+after
"""
    digest = hashlib.sha256(patch).hexdigest()
    monkeypatch.chdir(tmp_path / directory)
    proposal = pipeline.proposal_from_patch(
        patch_bytes=patch, patch_hash=digest, base_sha=pipeline.sha
    )
    assert proposal.files == ("docs/value.txt", "src/value.py")
    assert proposal.diff_lines == 4
    assert proposal.patch_hash == digest


def _failure_record() -> dict:
    return {
        "type": "failure",
        "timestamp": "2026-10-19T00:00:00+00:00",
        "pattern_id": "RP-019",
        "workflow": "ci",
        "error_text": "job timed out after 360 minutes",
        "root_cause": "ci job failure timeout on workflow timeout minutes",
        "fix_template": "jobs:\n  test:\n    timeout-minutes: 30",
        "files": ["src/codex/ci_config.py"],
        "verification_cmd": "nox -s tests",
    }


def test_template_pipeline_without_posix_dependencies(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            """
import sys
from types import SimpleNamespace
sys.modules["fcntl"] = None
from codex.cognitive_brain.authority import AuthorityEnvelope
from codex.cognitive_brain.improvement_pipeline import ImprovementPipeline, signal_from_pda_record
import os
os.environ.clear()
signal = signal_from_pda_record({
    "type": "failure", "timestamp": "2026-11-01T00:00:00Z",
    "fix_template": "repair", "files": ["src/fixture.py"],
})
match = SimpleNamespace(pattern_id="fixture", times_applied=1, success_rate=0.9, solutions=[])
pipeline = ImprovementPipeline(
    repo="fixture/repo", ref="main", sha="a" * 40,
    brain_interface=SimpleNamespace(query_patterns=lambda _: [match]),
    authority=AuthorityEnvelope(require_human_approval=False),
)
assert pipeline.process_signal(signal).actionable
assert "codex.cognitive_brain.isolated_execution" not in sys.modules
""",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_signal_to_pattern_to_proposal(tmp_path: Path, monkeypatch) -> None:
    # Strip ambient CI secret metadata so the authority check measures the
    # action, not the surrounding automation environment.
    monkeypatch.setattr("os.environ", {})
    signal = signal_from_pda_record(_failure_record())
    decision = _pipeline(tmp_path).process_signal(signal)
    assert decision.actionable, decision.reason
    event = decision.event
    event.validate()
    assert event.pattern is not None and event.pattern.pattern_id == "RP-019"
    assert event.proposal is not None
    assert event.proposal.files == ("src/codex/ci_config.py",)


class _FixedDatetime:
    """Deterministic stand-in for datetime used in replay testing."""

    @staticmethod
    def now(tz=None):
        from datetime import datetime, timezone

        return datetime(2026, 10, 19, tzinfo=timezone.utc)


def test_replay_is_deterministic(tmp_path: Path, monkeypatch) -> None:
    signal = signal_from_pda_record(_failure_record())
    monkeypatch.setattr(
        "codex.cognitive_brain.improvement_pipeline.datetime",
        _FixedDatetime,
    )
    first = _pipeline(tmp_path).process_signal(signal)
    second = _pipeline(tmp_path).process_signal(signal)
    assert first.event == second.event
    assert first == second


def test_no_match_case(tmp_path: Path) -> None:
    record = _failure_record()
    record["root_cause"] = "zzzqxx unmatched failure domain"
    record["error_text"] = "zzzqxx"
    record["fix_template"] = ""
    decision = _pipeline(tmp_path).process_signal(signal_from_pda_record(record))
    assert not decision.actionable
    assert "no pattern matched" in decision.reason
    assert decision.event.proposal is None


def test_non_actionable_signal(tmp_path: Path) -> None:
    signal = signal_from_pda_record(_failure_record())
    heartbeat = type(signal)(
        source=signal.source,
        kind="heartbeat",
        measured_at=signal.measured_at,
        availability=signal.availability,
        summary="routine heartbeat",
    )
    decision = _pipeline(tmp_path).process_signal(heartbeat)
    assert not decision.actionable
    assert "non-actionable" in decision.reason


def test_malformed_pda_record_fails_closed() -> None:
    with pytest.raises(ValueError):
        signal_from_pda_record({"type": "session", "timestamp": "2026-10-19T00:00:00Z"})
    with pytest.raises(ValueError):
        signal_from_pda_record({"type": "failure"})


def test_load_pda_signals_filters_non_failures(tmp_path: Path) -> None:
    log = tmp_path / "pda.jsonl"
    log.write_text(
        json.dumps(_failure_record())
        + "\n"
        + json.dumps({"type": "session", "timestamp": "t"})
        + "\n"
    )
    signals = load_pda_signals(log)
    assert len(signals) == 1
    assert signals[0].kind == "ci_job_failure"
