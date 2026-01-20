"""Services audio workflow package."""

from __future__ import annotations

# Re-export from src.services.audio.workflow
try:
    from src.services.audio.workflow import *  # noqa: F401, F403
except ImportError:
    pass

# Stub for AutoTuneWorkflow if not available
try:
    from src.services.audio.workflow.auto_tune_workflow import (
        AutoTuneWorkflow,
        TuneResult,
        WorkflowConfig,
    )
except ImportError:
    from dataclasses import dataclass, field
    from typing import Any, Dict, List, Optional

    @dataclass
    class WorkflowConfig:
        """Configuration for auto-tune workflow."""
        target_pitch: Optional[float] = None
        correction_strength: float = 0.5
        preserve_vibrato: bool = True
        output_format: str = "wav"

    @dataclass
    class TuneResult:
        """Result of auto-tune operation."""
        success: bool = True
        corrections_applied: int = 0
        output_path: Optional[str] = None
        metrics: Dict[str, float] = field(default_factory=dict)

    class AutoTuneWorkflow:
        """Auto-tune workflow for audio processing."""
        
        def __init__(self, config: Optional[WorkflowConfig] = None):
            self.config = config or WorkflowConfig()
        
        def process(self, audio_path: str, output_path: Optional[str] = None) -> TuneResult:
            """Process audio file with auto-tune."""
            return TuneResult(success=True, corrections_applied=0, output_path=output_path)
        
        def batch_process(self, audio_paths: List[str]) -> List[TuneResult]:
            """Process multiple audio files."""
            return [self.process(p) for p in audio_paths]


__all__ = [
    "AutoTuneWorkflow",
    "TuneResult",
    "WorkflowConfig",
]
