"""Compatibility wrapper for transcription workflow."""

from src.services.audio.workflow.transcription_workflow import (
    AudioTranscriptionWorkflow,
    BatchTranscriptionResult,
    DiarizedSegment,
    MissingDependencyError,
    TranscriptionConfig,
    TranscriptionResult,
    TranscriptSegment,
    load_speaker_map,
)

__all__ = [
    "AudioTranscriptionWorkflow",
    "BatchTranscriptionResult",
    "DiarizedSegment",
    "MissingDependencyError",
    "TranscriptSegment",
    "TranscriptionConfig",
    "TranscriptionResult",
    "load_speaker_map",
]
