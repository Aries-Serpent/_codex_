"""Services audio analysis package - re-exports from src.services.audio.analysis."""

from __future__ import annotations

# Re-export from src.services.audio.analysis
try:
    from src.services.audio.analysis import *  # noqa: F401, F403
except ImportError:
    pass

# Stub for IntelligentAudioAnalyzer if not available
try:
    from src.services.audio.analysis.intelligent_analyzer import (
        AnalysisResult,
        AudioQualityMetrics,
        IntelligentAudioAnalyzer,
    )
except ImportError:
    from dataclasses import dataclass
    from typing import Any, Dict, List, Optional

    @dataclass
    class AudioQualityMetrics:
        """Stub for audio quality metrics."""
        signal_to_noise: float = 0.0
        clarity_score: float = 0.0
        frequency_balance: float = 0.0

    @dataclass
    class AnalysisResult:
        """Stub for analysis result."""
        quality_metrics: AudioQualityMetrics = None
        recommendations: list[str] = None
        confidence: float = 0.0

        def __post_init__(self):
            if self.quality_metrics is None:
                self.quality_metrics = AudioQualityMetrics()
            if self.recommendations is None:
                self.recommendations = []

    class IntelligentAudioAnalyzer:
        """Stub for intelligent audio analyzer."""

        def __init__(self, config: Optional[dict[str, Any]] = None):
            self.config = config or {}

        def analyze(self, audio_data: Any) -> AnalysisResult:
            """Analyze audio data."""
            return AnalysisResult()

        def get_recommendations(self, result: AnalysisResult) -> list[str]:
            """Get recommendations based on analysis."""
            return result.recommendations if result else []
