"""The maintained runner exposes diagnostics only as an explicit separate stage."""

from datetime import datetime, timezone

from codex.cognitive_brain import improvement_loop_runner as runner
from codex.cognitive_brain.evidence_store import EvidenceStore


def test_explicit_runner_handoff_missing_event_creates_nothing(tmp_path):
    root = tmp_path / "absent"
    store = EvidenceStore(root / "evidence.jsonl")
    result = runner.compose_post_attempt_handoff(
        store, event_id="not-recorded", now=datetime(2026, 11, 2, tzinfo=timezone.utc)
    )
    assert result["status"] in ("partial", "unavailable")
    assert result["learning_eligible"] is False
    assert result["execution_authorized"] is False
    assert result["recovery_performed"] is False
    assert not root.exists()


def test_runner_forwards_only_explicit_stage_parameters(tmp_path, monkeypatch):
    store = EvidenceStore(tmp_path / "missing.jsonl")
    seen = {}

    def diagnostic(subject, **kwargs):
        assert subject is store
        seen.update(kwargs)
        return {"human_handoff_required": True}

    monkeypatch.setattr(runner, "_compose_post_attempt_handoff", diagnostic)
    result = runner.compose_post_attempt_handoff(
        store, event_id="event", pattern_id="RP-019", patch_hash="a" * 64, attempt_id="attempt"
    )
    assert result == {"human_handoff_required": True}
    assert seen == {
        "event_id": "event",
        "pattern_id": "RP-019",
        "patch_hash": "a" * 64,
        "attempt_id": "attempt",
        "observation_context": None,
        "reader": None,
        "now": None,
    }
