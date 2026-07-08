"""
Curriculum Orchestrator for Multi-Phase Training

Manages curriculum-based training with phase transitions, metrics-based
progression, and checkpoint-per-phase persistence.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from codex.logging.structured_logger import logger

logger = logging.getLogger(__name__)


class PhaseStatus(Enum):
    """Training phase status"""

    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class TrainingPhase:
    """Definition of a training curriculum phase"""

    id: str
    dataset: str
    steps: int
    metrics: list[str] = field(default_factory=list)
    min_metric_threshold: Optional[dict[str, float]] = None
    max_metric_threshold: Optional[dict[str, float]] = None
    learning_rate: Optional[float] = None
    batch_size: Optional[int] = None
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "dataset": self.dataset,
            "steps": self.steps,
            "metrics": self.metrics,
            "min_metric_threshold": self.min_metric_threshold,
            "max_metric_threshold": self.max_metric_threshold,
            "learning_rate": self.learning_rate,
            "batch_size": self.batch_size,
            "description": self.description,
        }


@dataclass
class PhaseResult:
    """Results from completing a training phase"""

    phase_id: str
    status: PhaseStatus
    steps_completed: int
    metrics: dict[str, float] = field(default_factory=dict)
    checkpoint_path: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    error_message: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "phase_id": self.phase_id,
            "status": self.status.value,
            "steps_completed": self.steps_completed,
            "metrics": self.metrics,
            "checkpoint_path": self.checkpoint_path,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "error_message": self.error_message,
        }


@dataclass
class CurriculumState:
    """State of curriculum training"""

    curriculum_name: str
    current_phase_index: int = 0
    phase_results: list[PhaseResult] = field(default_factory=list)
    global_step: int = 0
    is_complete: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "curriculum_name": self.curriculum_name,
            "current_phase_index": self.current_phase_index,
            "phase_results": [r.to_dict() for r in self.phase_results],
            "global_step": self.global_step,
            "is_complete": self.is_complete,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CurriculumState:
        """Create from dictionary"""
        phase_results = [
            PhaseResult(
                phase_id=r["phase_id"],
                status=PhaseStatus(r["status"]),
                steps_completed=r["steps_completed"],
                metrics=r.get("metrics", {}),
                checkpoint_path=r.get("checkpoint_path"),
                start_time=r.get("start_time"),
                end_time=r.get("end_time"),
                error_message=r.get("error_message"),
            )
            for r in data.get("phase_results", [])
        ]

        return cls(
            curriculum_name=data["curriculum_name"],
            current_phase_index=data.get("current_phase_index", 0),
            phase_results=phase_results,
            global_step=data.get("global_step", 0),
            is_complete=data.get("is_complete", False),
        )


class CurriculumScheduler:
    """
    Curriculum scheduler for multi-phase training.

    Manages phase transitions based on step counts and metric thresholds,
    saves checkpoints after each phase, and tracks curriculum state.
    """

    def __init__(
        self,
        phases: list[TrainingPhase],
        curriculum_name: str,
        checkpoint_dir: Optional[str] = None,
        state_file: Optional[str] = None,
    ):
        """Initialize curriculum scheduler

        Args:
            phases: list of training phases
            curriculum_name: Name of the curriculum
            checkpoint_dir: Directory for phase checkpoints
            state_file: Path to curriculum state file
        """
        self.phases = phases
        self.curriculum_name = curriculum_name
        self.checkpoint_dir = Path(checkpoint_dir) if checkpoint_dir else Path(".codex/curriculum")
        self.state_file = Path(state_file) if state_file else self.checkpoint_dir / "state.json"

        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.state = self._load_or_create_state()

        logger.info(f"Initialized CurriculumScheduler: {curriculum_name} with {len(phases)} phases")

    def _load_or_create_state(self) -> CurriculumState:
        """Load existing state or create new"""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    data = json.load(f)
                logger.info(f"Loaded curriculum state from {self.state_file}")
                return CurriculumState.from_dict(data)
            except (IOError, OSError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                logger.warning("Failed to load state, creating new: <ERROR_TYPE>")

        return CurriculumState(curriculum_name=self.curriculum_name)

    def save_state(self) -> None:
        """Persist curriculum state to disk"""
        try:
            with open(self.state_file, "w") as f:
                json.dump(self.state.to_dict(), f, indent=2)
            logger.info(f"Saved curriculum state to {self.state_file}")
        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.error("Failed to save state: <ERROR_TYPE>")
            raise

    def get_current_phase(self) -> Optional[TrainingPhase]:
        """Get the current active phase

        Returns:
            Current TrainingPhase or None if curriculum complete
        """
        if self.state.is_complete:
            return None

        if self.state.current_phase_index >= len(self.phases):
            self.state.is_complete = True
            self.save_state()
            return None

        return self.phases[self.state.current_phase_index]

    def can_progress_to_next_phase(
        self, current_metrics: dict[str, float]
    ) -> tuple[bool, Optional[str]]:
        """Check if ready to progress to next phase

        Args:
            current_metrics: Current training metrics

        Returns:
            tuple of (can_progress, reason)
        """
        phase = self.get_current_phase()
        if not phase:
            return False, "No active phase"

        # Check step count
        current_result = self.state.phase_results[-1] if self.state.phase_results else None
        if current_result and current_result.steps_completed < phase.steps:
            remaining = phase.steps - current_result.steps_completed
            return False, f"Need {remaining} more steps"

        # Check minimum metric thresholds
        if phase.min_metric_threshold:
            for metric, threshold in phase.min_metric_threshold.items():
                if metric not in current_metrics:
                    return False, f"Missing metric: {metric}"
                if current_metrics[metric] < threshold:
                    return (
                        False,
                        f"{metric} below threshold ({current_metrics[metric]:.4f} < {threshold})",
                    )

        # Check maximum metric thresholds (e.g., loss should be below)
        if phase.max_metric_threshold:
            for metric, threshold in phase.max_metric_threshold.items():
                if metric not in current_metrics:
                    return False, f"Missing metric: {metric}"
                if current_metrics[metric] > threshold:
                    return (
                        False,
                        f"{metric} above threshold ({current_metrics[metric]:.4f} > {threshold})",
                    )

        return True, "All criteria met"

    def start_phase(self, phase_id: str) -> PhaseResult:
        """Start a new training phase

        Args:
            phase_id: Phase identifier

        Returns:
            PhaseResult for the started phase
        """
        from datetime import datetime, timezone

        phase = self.get_current_phase()
        if not phase or phase.id != phase_id:
            raise ValueError(f"Phase {phase_id} is not the current phase")

        result = PhaseResult(
            phase_id=phase_id,
            status=PhaseStatus.ACTIVE,
            steps_completed=0,
            start_time=datetime.now(timezone.utc).isoformat(),
        )

        self.state.phase_results.append(result)
        self.save_state()

        logger.info(f"Started phase: {phase_id}")
        return result

    def complete_phase(
        self,
        phase_id: str,
        metrics: dict[str, float],
        checkpoint_path: Optional[str] = None,
    ) -> PhaseResult:
        """Mark a phase as complete

        Args:
            phase_id: Phase identifier
            metrics: Final metrics for the phase
            checkpoint_path: Path to saved checkpoint

        Returns:
            Completed PhaseResult
        """
        from datetime import datetime, timezone

        if not self.state.phase_results or self.state.phase_results[-1].phase_id != phase_id:
            raise ValueError(f"Phase {phase_id} is not active")

        result = self.state.phase_results[-1]
        result.status = PhaseStatus.COMPLETED
        result.metrics = metrics
        result.checkpoint_path = checkpoint_path
        result.end_time = datetime.now(timezone.utc).isoformat()

        # Move to next phase
        self.state.current_phase_index += 1

        # Check if curriculum is complete
        if self.state.current_phase_index >= len(self.phases):
            self.state.is_complete = True
            logger.info(f"Curriculum {self.curriculum_name} completed!")

        self.save_state()

        logger.info(f"Completed phase: {phase_id}")
        return result

    def update_phase_progress(
        self, phase_id: str, steps: int, metrics: Optional[dict[str, float]] = None
    ) -> None:
        """Update progress for current phase

        Args:
            phase_id: Phase identifier
            steps: Number of steps completed
            metrics: Optional current metrics
        """
        if not self.state.phase_results or self.state.phase_results[-1].phase_id != phase_id:
            raise ValueError(f"Phase {phase_id} is not active")

        result = self.state.phase_results[-1]
        result.steps_completed = steps

        if metrics:
            result.metrics.update(metrics)

        self.state.global_step += steps
        self.save_state()

    def fail_phase(self, phase_id: str, error_message: str) -> PhaseResult:
        """Mark phase as failed

        Args:
            phase_id: Phase identifier
            error_message: Error description

        Returns:
            Failed PhaseResult
        """
        from datetime import datetime, timezone

        if not self.state.phase_results or self.state.phase_results[-1].phase_id != phase_id:
            raise ValueError(f"Phase {phase_id} is not active")

        result = self.state.phase_results[-1]
        result.status = PhaseStatus.FAILED
        result.error_message = error_message
        result.end_time = datetime.now(timezone.utc).isoformat()

        self.save_state()

        logger.error(f"Phase {phase_id} failed: {error_message}")
        return result

    def get_phase_checkpoint_path(self, phase_id: str) -> Path:
        """Get checkpoint path for a phase

        Args:
            phase_id: Phase identifier

        Returns:
            Path for phase checkpoint
        """
        return self.checkpoint_dir / f"{self.curriculum_name}-{phase_id}.pt"

    def get_summary(self) -> dict[str, Any]:
        """Get curriculum summary

        Returns:
            Summary dictionary
        """
        completed = sum(1 for r in self.state.phase_results if r.status == PhaseStatus.COMPLETED)
        failed = sum(1 for r in self.state.phase_results if r.status == PhaseStatus.FAILED)

        return {
            "curriculum_name": self.curriculum_name,
            "total_phases": len(self.phases),
            "completed_phases": completed,
            "failed_phases": failed,
            "current_phase_index": self.state.current_phase_index,
            "current_phase": (self.get_current_phase().id if self.get_current_phase() else None),  # type: ignore[union-attr]
            "global_step": self.state.global_step,
            "is_complete": self.state.is_complete,
            "phase_results": [r.to_dict() for r in self.state.phase_results],
        }

    def reset(self) -> None:
        """Reset curriculum to initial state"""
        self.state = CurriculumState(curriculum_name=self.curriculum_name)
        self.save_state()
        logger.info(f"Reset curriculum: {self.curriculum_name}")


def load_curriculum_from_config(config_path: str) -> list[TrainingPhase]:
    """Load curriculum phases from YAML config

    Args:
        config_path: Path to curriculum config file

    Returns:
        list of TrainingPhases
    """
    try:
        import yaml
    except ImportError as e:
        type(e).__name__
        logger.debug("ImportError: <ERROR_TYPE>")
        logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
        raise RuntimeError("PyYAML not installed. Install with: pip install pyyaml") from e

    with open(config_path) as f:
        config = yaml.safe_load(f)

    phases = []
    for phase_def in config.get("phase_schedule", []):
        phase = TrainingPhase(
            id=phase_def["id"],
            dataset=phase_def["dataset"],
            steps=phase_def["steps"],
            metrics=phase_def.get("metrics", []),
            min_metric_threshold=phase_def.get("min_metric_threshold"),
            max_metric_threshold=phase_def.get("max_metric_threshold"),
            learning_rate=phase_def.get("learning_rate"),
            batch_size=phase_def.get("batch_size"),
            description=phase_def.get("description", ""),
        )
        phases.append(phase)

    return phases


if __name__ == "__main__":
    # Example usage
    phases = [
        TrainingPhase(
            id="warmup",
            dataset="datasets/reasoning/warmup.jsonl",
            steps=100,
            metrics=["accuracy"],
        ),
        TrainingPhase(
            id="main",
            dataset="datasets/reasoning/main.jsonl",
            steps=500,
            metrics=["accuracy", "f1"],
            min_metric_threshold={"accuracy": 0.7},
        ),
    ]

    scheduler = CurriculumScheduler(
        phases=phases,
        curriculum_name="example_curriculum",
    )

    logger.info(f"Summary: {scheduler.get_summary()}")
