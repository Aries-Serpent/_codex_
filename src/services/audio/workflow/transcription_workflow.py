#!/usr/bin/env python3
"""Audio transcription workflow with speaker diarization and labeling."""

from __future__ import annotations

import importlib.util
import json
import logging
import math
import shutil
import subprocess
import wave
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

logger = logging.getLogger(__name__)


SUPPORTED_INPUT_SUFFIXES = {".wav", ".mp3", ".mp4", ".m4a"}


@dataclass
class TranscriptionConfig:
    """Configuration for transcription workflow."""

    sample_rate: int = 16000
    max_speakers: int = 4
    max_duration_seconds: int = 4 * 60 * 60
    diarization_window_seconds: float = 2.0
    diarization_threshold: float = 0.18
    model_size: str = "small"
    transcription_backend: str = "mock"


@dataclass
class DiarizedSegment:
    """Segment with detected speaker."""

    start: float
    end: float
    speaker_id: str


@dataclass
class TranscriptSegment:
    """Final transcript segment."""

    start: float
    end: float
    speaker_id: str
    speaker_name: str
    text: str


@dataclass
class TranscriptionResult:
    """Result of processing one media file."""

    success: bool
    input_path: Path
    normalized_wav_path: Path | None = None
    segments: list[TranscriptSegment] = field(default_factory=list)
    detected_speakers: list[str] = field(default_factory=list)
    output_files: dict[str, str] = field(default_factory=dict)
    error: str | None = None


@dataclass
class BatchTranscriptionResult:
    """Batch workflow result."""

    success: bool
    processed_files: int
    failed_files: int
    results: list[TranscriptionResult] = field(default_factory=list)
    error: str | None = None


class MissingDependencyError(RuntimeError):
    """Raised when an optional dependency is missing."""


class AudioTranscriptionWorkflow:
    """Transcription workflow orchestrator."""

    def __init__(self, config: TranscriptionConfig | None = None):
        self.config = config or TranscriptionConfig()

    def process_path(
        self,
        input_path: str,
        output_dir: str | None = None,
        speaker_map: dict[str, str] | None = None,
        interactive_speakers: bool = False,
        output_formats: list[str] | None = None,
        input_func: Callable[[str], str] = input,
    ) -> BatchTranscriptionResult:
        """Process a file or directory for transcription."""
        files = self._discover_media_files(input_path)
        if not files:
            return BatchTranscriptionResult(
                success=False,
                processed_files=0,
                failed_files=0,
                error="No media files found for transcription",
            )

        result_list: list[TranscriptionResult] = []
        failures = 0
        for media_file in files:
            file_output_dir = Path(output_dir).resolve() if output_dir else media_file.parent
            file_output_dir.mkdir(parents=True, exist_ok=True)
            result = self.process_file(
                media_file,
                output_dir=file_output_dir,
                speaker_map=speaker_map,
                interactive_speakers=interactive_speakers,
                output_formats=output_formats,
                input_func=input_func,
            )
            result_list.append(result)
            if not result.success:
                failures += 1

        return BatchTranscriptionResult(
            success=failures == 0,
            processed_files=len(files) - failures,
            failed_files=failures,
            results=result_list,
        )

    def process_file(
        self,
        input_path: str | Path,
        output_dir: str | Path,
        speaker_map: dict[str, str] | None = None,
        interactive_speakers: bool = False,
        output_formats: list[str] | None = None,
        input_func: Callable[[str], str] = input,
    ) -> TranscriptionResult:
        """Process one media file for transcription."""
        media_path = Path(input_path).resolve()
        output_path = Path(output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)

        try:
            normalized_wav = self._normalize_to_wav(media_path, output_path)
            diarized = self._run_speaker_diarization(normalized_wav)
            detected_speakers = sorted({segment.speaker_id for segment in diarized})
            names = self._resolve_speaker_names(
                detected_speakers=detected_speakers,
                speaker_map=speaker_map,
                interactive=interactive_speakers,
                input_func=input_func,
            )
            transcripts = self._transcribe_segments(normalized_wav, diarized, names)
            output_files = self._write_outputs(
                transcripts,
                normalized_wav,
                output_path,
                output_formats=output_formats or ["txt", "json"],
            )
            return TranscriptionResult(
                success=True,
                input_path=media_path,
                normalized_wav_path=normalized_wav,
                segments=transcripts,
                detected_speakers=detected_speakers,
                output_files=output_files,
            )
        except Exception as exc:
            return TranscriptionResult(
                success=False,
                input_path=media_path,
                error=str(exc),
            )

    def _discover_media_files(self, input_path: str) -> list[Path]:
        """Find supported media files from file or directory input."""
        root = Path(input_path).resolve()
        if not root.exists():
            raise FileNotFoundError(f"Path does not exist: {root}")

        if root.is_file():
            if root.suffix.lower() not in SUPPORTED_INPUT_SUFFIXES:
                raise ValueError(f"Unsupported media format: {root.suffix}")
            return [root]

        files: list[Path] = []
        for path in sorted(root.rglob("*")):
            if path.is_file() and path.suffix.lower() in SUPPORTED_INPUT_SUFFIXES:
                files.append(path)
        return files

    def _normalize_to_wav(self, input_path: Path, output_dir: Path) -> Path:
        """Normalize input media into mono PCM WAV for downstream processing."""
        suffix = input_path.suffix.lower()
        if suffix not in SUPPORTED_INPUT_SUFFIXES:
            raise ValueError(f"Unsupported media format: {suffix}")

        output_wav = output_dir / f"{input_path.stem}.mono16k.wav"

        if suffix == ".wav":
            duration = self._wav_duration_seconds(input_path)
            self._validate_duration(duration)
            return input_path

        ffmpeg_path = shutil.which("ffmpeg")
        if not ffmpeg_path:
            raise MissingDependencyError(
                "ffmpeg is required to process MP3/MP4/M4A inputs. Install ffmpeg and retry."
            )

        command = [
            ffmpeg_path,
            "-y",
            "-i",
            str(input_path),
            "-ac",
            "1",
            "-ar",
            str(self.config.sample_rate),
            str(output_wav),
        ]

        completed = subprocess.run(command, check=False, capture_output=True, text=True)
        if completed.returncode != 0:
            stderr = completed.stderr.strip() or "unknown ffmpeg failure"
            raise RuntimeError(f"ffmpeg conversion failed for {input_path.name}: {stderr}")

        duration = self._wav_duration_seconds(output_wav)
        self._validate_duration(duration)
        return output_wav

    def _wav_duration_seconds(self, wav_path: Path) -> float:
        with wave.open(str(wav_path), "rb") as wav_file:
            frame_rate = wav_file.getframerate()
            if frame_rate <= 0:
                raise ValueError(f"Invalid WAV frame rate in {wav_path}")
            total_frames = wav_file.getnframes()
        return float(total_frames) / float(frame_rate)

    def _validate_duration(self, duration_seconds: float) -> None:
        if duration_seconds > self.config.max_duration_seconds:
            raise ValueError(
                f"Input duration {duration_seconds:.1f}s exceeds configured memory-safe limit "
                f"of {self.config.max_duration_seconds}s"
            )

    def _run_speaker_diarization(self, wav_path: Path) -> list[DiarizedSegment]:
        """Naive speaker diarization based on lightweight acoustic clustering.

        Reads the WAV file in diarization-window-sized chunks to avoid
        materialising the entire audio file in memory.
        """
        with wave.open(str(wav_path), "rb") as wav_file:
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            total_frames = wav_file.getnframes()

            if sample_width != 2:
                raise ValueError(
                    f"Unsupported WAV sample width ({sample_width * 8}-bit): {wav_path}"
                )

            if total_frames == 0:
                return [DiarizedSegment(start=0.0, end=0.0, speaker_id="SPEAKER_00")]

            window_frames = max(1, int(sample_rate * self.config.diarization_window_seconds))
            features: list[tuple[float, float, float]] = []
            starts: list[float] = []
            ends: list[float] = []

            offset = 0
            while offset < total_frames:
                chunk_size = min(window_frames, total_frames - offset)
                raw_chunk = wav_file.readframes(chunk_size)

                sample_count = len(raw_chunk) // sample_width
                int_samples = [
                    int.from_bytes(
                        raw_chunk[i * sample_width : (i + 1) * sample_width],
                        "little",
                        signed=True,
                    )
                    for i in range(sample_count)
                ]

                if channels > 1:
                    mono: list[int] = []
                    for i in range(0, len(int_samples), channels):
                        frame = int_samples[i : i + channels]
                        if frame:
                            mono.append(int(sum(frame) / len(frame)))
                    int_samples = mono

                chunk_float = [s / 32768.0 for s in int_samples]
                if chunk_float:
                    starts.append(offset / sample_rate)
                    ends.append(min(total_frames, offset + chunk_size) / sample_rate)
                    features.append(self._feature_vector(chunk_float, sample_rate))

                offset += chunk_size

        if not features:
            return [DiarizedSegment(start=0.0, end=0.0, speaker_id="SPEAKER_00")]

        speaker_indices = self._cluster_features(features)
        raw_segments = [
            DiarizedSegment(
                start=starts[i],
                end=ends[i],
                speaker_id=f"SPEAKER_{speaker_indices[i]:02d}",
            )
            for i in range(len(features))
        ]
        return self._merge_adjacent_segments(raw_segments)

    def _feature_vector(self, chunk: list[float], sample_rate: int) -> tuple[float, float, float]:
        if not chunk:
            return (0.0, 0.0, 0.0)

        energy = sum(sample * sample for sample in chunk) / len(chunk)
        sign_changes = sum(
            1 for prev, curr in zip(chunk, chunk[1:]) if (prev >= 0) != (curr >= 0)
        )
        zcr = sign_changes / max(1, len(chunk) - 1)

        amplitude_sum = sum(abs(sample) for sample in chunk) + 1e-8
        weighted_position = sum((index + 1) * abs(sample) for index, sample in enumerate(chunk))
        centroid = weighted_position / amplitude_sum / max(len(chunk), 1)
        centroid_hz = centroid * sample_rate
        return (energy, zcr, centroid_hz / max(sample_rate, 1))

    def _cluster_features(self, features: list[tuple[float, float, float]]) -> list[int]:
        if not features:
            return []

        centroids: list[list[float]] = [list(features[0])]
        assignments: list[int] = [0]

        for feature in features[1:]:
            distances = [math.dist(feature, centroid) for centroid in centroids]
            nearest_index = min(range(len(distances)), key=distances.__getitem__)
            nearest_distance = distances[nearest_index]

            if (
                nearest_distance > self.config.diarization_threshold
                and len(centroids) < self.config.max_speakers
            ):
                new_idx = len(centroids)
                centroids.append(list(feature))
                assignments.append(new_idx)
            else:
                assignments.append(nearest_index)
                current = centroids[nearest_index]
                centroids[nearest_index] = [
                    (current[0] + feature[0]) / 2.0,
                    (current[1] + feature[1]) / 2.0,
                    (current[2] + feature[2]) / 2.0,
                ]

        return assignments

    def _merge_adjacent_segments(self, segments: list[DiarizedSegment]) -> list[DiarizedSegment]:
        if not segments:
            return []

        merged: list[DiarizedSegment] = [segments[0]]
        for segment in segments[1:]:
            last = merged[-1]
            if segment.speaker_id == last.speaker_id:
                merged[-1] = DiarizedSegment(
                    start=last.start,
                    end=segment.end,
                    speaker_id=last.speaker_id,
                )
            else:
                merged.append(segment)
        return merged

    def _resolve_speaker_names(
        self,
        detected_speakers: list[str],
        speaker_map: dict[str, str] | None,
        interactive: bool,
        input_func: Callable[[str], str],
    ) -> dict[str, str]:
        names: dict[str, str] = {}
        provided = speaker_map or {}

        for speaker_id in detected_speakers:
            mapped = provided.get(speaker_id)
            if mapped:
                names[speaker_id] = mapped
                continue

            if interactive:
                answer = input_func(
                    f"Assign a name for {speaker_id} (leave blank to keep default): "
                ).strip()
                names[speaker_id] = answer if answer else speaker_id
            else:
                names[speaker_id] = speaker_id

        return names

    def _transcribe_segments(
        self,
        wav_path: Path,
        diarized: list[DiarizedSegment],
        speaker_names: dict[str, str],
    ) -> list[TranscriptSegment]:
        """Transcribe diarized segments using configured backend."""
        if self.config.transcription_backend == "faster-whisper":
            self._validate_faster_whisper_available()
            raise NotImplementedError(
                "faster-whisper transcription backend is not yet wired into the segment "
                "inference loop. Install the dependency and use a future version, or set "
                "transcription_backend='mock' for layout testing."
            )

        transcript_segments: list[TranscriptSegment] = []
        for segment in diarized:
            transcript_segments.append(
                TranscriptSegment(
                    start=segment.start,
                    end=segment.end,
                    speaker_id=segment.speaker_id,
                    speaker_name=speaker_names.get(segment.speaker_id, segment.speaker_id),
                    text=self._mock_segment_text(wav_path, segment.start, segment.end),
                )
            )
        return transcript_segments

    def _validate_faster_whisper_available(self) -> None:
        if importlib.util.find_spec("faster_whisper") is None:
            raise MissingDependencyError(
                "transcription_backend='faster-whisper' requires installing faster-whisper. "
                "Install optional transcription dependencies and retry."
            )

    def _mock_segment_text(self, wav_path: Path, start: float, end: float) -> str:
        return f"[{wav_path.stem}] segment {start:.2f}s-{end:.2f}s"

    def _write_outputs(
        self,
        segments: list[TranscriptSegment],
        source_wav: Path,
        output_dir: Path,
        output_formats: list[str],
    ) -> dict[str, str]:
        formats = {fmt.lower().strip() for fmt in output_formats}
        allowed = {"txt", "json", "srt", "vtt"}
        unknown = formats - allowed
        if unknown:
            raise ValueError(f"Unsupported output format(s): {sorted(unknown)}")

        output_files: dict[str, str] = {}
        base = source_wav.stem

        if "txt" in formats:
            txt_path = output_dir / f"{base}.transcript.txt"
            txt_path.write_text(self._to_text(segments), encoding="utf-8")
            output_files["txt"] = str(txt_path)

        if "json" in formats:
            json_path = output_dir / f"{base}.transcript.json"
            json_payload = [
                {
                    "start": seg.start,
                    "end": seg.end,
                    "speaker_id": seg.speaker_id,
                    "speaker_name": seg.speaker_name,
                    "text": seg.text,
                }
                for seg in segments
            ]
            json_path.write_text(json.dumps(json_payload, indent=2), encoding="utf-8")
            output_files["json"] = str(json_path)

        if "srt" in formats:
            srt_path = output_dir / f"{base}.transcript.srt"
            srt_path.write_text(self._to_srt(segments), encoding="utf-8")
            output_files["srt"] = str(srt_path)

        if "vtt" in formats:
            vtt_path = output_dir / f"{base}.transcript.vtt"
            vtt_path.write_text(self._to_vtt(segments), encoding="utf-8")
            output_files["vtt"] = str(vtt_path)

        return output_files

    def _to_text(self, segments: list[TranscriptSegment]) -> str:
        lines = []
        for segment in segments:
            lines.append(
                f"[{segment.start:07.2f}-{segment.end:07.2f}] "
                f"{segment.speaker_name}: {segment.text}"
            )
        return "\n".join(lines) + ("\n" if lines else "")

    def _to_srt(self, segments: list[TranscriptSegment]) -> str:
        rows = []
        for idx, segment in enumerate(segments, start=1):
            rows.append(str(idx))
            rows.append(
                f"{self._format_timestamp(segment.start, for_vtt=False)} --> "
                f"{self._format_timestamp(segment.end, for_vtt=False)}"
            )
            rows.append(f"{segment.speaker_name}: {segment.text}")
            rows.append("")
        return "\n".join(rows)

    def _to_vtt(self, segments: list[TranscriptSegment]) -> str:
        rows = ["WEBVTT", ""]
        for segment in segments:
            rows.append(
                f"{self._format_timestamp(segment.start, for_vtt=True)} --> "
                f"{self._format_timestamp(segment.end, for_vtt=True)}"
            )
            rows.append(f"{segment.speaker_name}: {segment.text}")
            rows.append("")
        return "\n".join(rows)

    def _format_timestamp(self, seconds: float, for_vtt: bool) -> str:
        total_ms = max(0, int(round(seconds * 1000)))
        hours = total_ms // 3_600_000
        minutes = (total_ms % 3_600_000) // 60_000
        secs = (total_ms % 60_000) // 1000
        millis = total_ms % 1000
        separator = "." if for_vtt else ","
        return f"{hours:02d}:{minutes:02d}:{secs:02d}{separator}{millis:03d}"


def load_speaker_map(path: str | None) -> dict[str, str]:
    """Load speaker map from JSON file path."""
    if not path:
        return {}

    map_path = Path(path).resolve()
    if not map_path.exists():
        raise FileNotFoundError(f"Speaker map not found: {map_path}")

    payload = json.loads(map_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Speaker map JSON must be an object of speaker IDs to names")

    normalized: dict[str, str] = {}
    for key, value in payload.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise ValueError("Speaker map keys and values must be strings")
        normalized[key] = value
    return normalized
