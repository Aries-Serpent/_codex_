"""
Tests for curriculum orchestrator
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from codex_ml.training.curriculum import (
    CurriculumScheduler,
    PhaseStatus,
    TrainingPhase,
)


def test_training_phase_creation():
    """Test creating a training phase"""
    phase = TrainingPhase(
        id="warmup",
        dataset="test.jsonl",
        steps=100,
        metrics=["accuracy"],
    )
    assert phase.id == "warmup", "id is not valid"
    assert phase.steps == 100, "steps is not valid"
    assert "accuracy" in phase.metrics, "Condition must be true"


def test_curriculum_scheduler_init():
    """Test curriculum scheduler initialization"""
    phases = [
        TrainingPhase(id="phase1", dataset="data1.jsonl", steps=100),
        TrainingPhase(id="phase2", dataset="data2.jsonl", steps=200),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        scheduler = CurriculumScheduler(
            phases=phases,
            curriculum_name="test_curriculum",
            checkpoint_dir=tmpdir,
        )

        assert len(scheduler.phases) == 2, "Collection must not be empty"
        assert scheduler.curriculum_name == "test_curriculum", "curriculum_name is not valid"
        assert scheduler.get_current_phase().id == "phase1", "id is not valid"


def test_phase_progression():
    """Test phase progression logic"""
    phases = [
        TrainingPhase(id="phase1", dataset="data1.jsonl", steps=10),
        TrainingPhase(id="phase2", dataset="data2.jsonl", steps=20),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        scheduler = CurriculumScheduler(
            phases=phases,
            curriculum_name="test",
            checkpoint_dir=tmpdir,
        )

        # Start phase 1
        scheduler.start_phase("phase1")
        assert scheduler.state.current_phase_index == 0, "current_phase_index is not valid"

        # Complete phase 1
        scheduler.complete_phase("phase1", metrics={"accuracy": 0.9})
        assert scheduler.state.current_phase_index == 1, "current_phase_index is not valid"
        assert scheduler.get_current_phase().id == "phase2", "id is not valid"


def test_metrics_based_progression():
    """Test metrics-based phase progression"""
    phases = [
        TrainingPhase(
            id="phase1",
            dataset="data.jsonl",
            steps=10,
            min_metric_threshold={"accuracy": 0.7},
        ),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        scheduler = CurriculumScheduler(
            phases=phases,
            curriculum_name="test",
            checkpoint_dir=tmpdir,
        )

        scheduler.start_phase("phase1")
        scheduler.update_phase_progress("phase1", steps=10)  # Complete steps requirement

        # Should not progress - accuracy too low
        can_progress, reason = scheduler.can_progress_to_next_phase({"accuracy": 0.5})
        assert not can_progress, "Condition must be true"
        # Check for any metric-related message
        assert any(word in reason.lower() for word in ["below", "threshold", "accuracy", "metric"])

        # Should progress - accuracy meets threshold
        can_progress, reason = scheduler.can_progress_to_next_phase({"accuracy": 0.8})
        assert can_progress, "can_progress is not valid"


def test_state_persistence():
    """Test curriculum state save/load"""
    phases = [
        TrainingPhase(id="phase1", dataset="data.jsonl", steps=100),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create and save state
        scheduler1 = CurriculumScheduler(
            phases=phases,
            curriculum_name="test",
            checkpoint_dir=tmpdir,
        )
        scheduler1.start_phase("phase1")
        scheduler1.update_phase_progress("phase1", steps=50, metrics={"acc": 0.8})
        state_file = Path(tmpdir) / "state.json"

        # Load state in new scheduler
        scheduler2 = CurriculumScheduler(
            phases=phases,
            curriculum_name="test",
            checkpoint_dir=tmpdir,
            state_file=str(state_file),
        )

        assert scheduler2.state.phase_results[0].steps_completed == 50, "Result must not be empty"
        assert scheduler2.state.phase_results[0].metrics["acc"] == 0.8, "Result must not be empty"


def test_curriculum_summary():
    """Test curriculum summary generation"""
    phases = [
        TrainingPhase(id="phase1", dataset="data1.jsonl", steps=10),
        TrainingPhase(id="phase2", dataset="data2.jsonl", steps=20),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        scheduler = CurriculumScheduler(
            phases=phases,
            curriculum_name="test",
            checkpoint_dir=tmpdir,
        )

        summary = scheduler.get_summary()

        assert summary["curriculum_name"] == "test", "Condition must be true"
        assert summary["total_phases"] == 2, "Condition must be true"
        assert summary["completed_phases"] == 0, "Condition must be true"
        assert summary["current_phase"] == "phase1", "Condition must be true"


def test_phase_failure_handling():
    """Test phase failure handling"""
    phases = [
        TrainingPhase(id="phase1", dataset="data.jsonl", steps=100),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        scheduler = CurriculumScheduler(
            phases=phases,
            curriculum_name="test",
            checkpoint_dir=tmpdir,
        )

        scheduler.start_phase("phase1")
        result = scheduler.fail_phase("phase1", "Training diverged")

        assert result.status == PhaseStatus.FAILED, "Result must not be empty"
        assert result.error_message == "Training diverged", "Result must not be empty"


def test_empty_curriculum():
    """Test handling of empty curriculum"""
    with tempfile.TemporaryDirectory() as tmpdir:
        scheduler = CurriculumScheduler(
            phases=[],
            curriculum_name="empty",
            checkpoint_dir=tmpdir,
        )

        assert scheduler.get_current_phase() is None, "Condition must be true"
        assert scheduler.state.is_complete, "Condition must be true"


if __name__ == "__main__":
    # Run tests
    test_training_phase_creation()
    print("✓ test_training_phase_creation")

    test_curriculum_scheduler_init()
    print("✓ test_curriculum_scheduler_init")

    test_phase_progression()
    print("✓ test_phase_progression")

    test_metrics_based_progression()
    print("✓ test_metrics_based_progression")

    test_state_persistence()
    print("✓ test_state_persistence")

    test_curriculum_summary()
    print("✓ test_curriculum_summary")

    test_phase_failure_handling()
    print("✓ test_phase_failure_handling")

    test_empty_curriculum()
    print("✓ test_empty_curriculum")

    print("\n✅ All curriculum tests passed!")
