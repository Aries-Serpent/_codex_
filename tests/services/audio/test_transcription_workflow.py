"""Tests for transcription workflow."""

from __future__ import annotations

import json
import math
import wave
from pathlib import Path

from src.services.audio.cli.smart_cli import apply_backward_compatible_default_command
from src.services.audio.workflow.transcription_workflow import (
    AudioTranscriptionWorkflow,
    TranscriptionConfig,
    load_speaker_map,
)


def _write_test_wav(path: Path, *, seconds: float = 1.0, sample_rate: int = 16000) -> None:
    total_samples = int(seconds * sample_rate)
    audio = bytearray()
    for index in range(total_samples):
        sample = int(0.2 * math.sin(2 * math.pi * 440 * (index / sample_rate)) * 32767)
        audio.extend(sample.to_bytes(2, "little", signed=True))

    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(bytes(audio))


def test_discover_media_files_includes_mp3_and_mp4(tmp_path: Path):
    media_dir = tmp_path / "media"
    media_dir.mkdir()
    (media_dir / "a.mp3").write_bytes(b"fake")
    (media_dir / "b.mp4").write_bytes(b"fake")
    (media_dir / "c.txt").write_text("not media")

    workflow = AudioTranscriptionWorkflow()
    files = workflow._discover_media_files(str(media_dir))

    assert [f.name for f in files] == ["a.mp3", "b.mp4"]


def test_discover_media_files_handles_uppercase_extensions(tmp_path: Path):
    """Directories containing files with uppercase extensions must be discovered."""
    media_dir = tmp_path / "media"
    media_dir.mkdir()
    (media_dir / "MEETING.MP3").write_bytes(b"fake")
    (media_dir / "VIDEO.MP4").write_bytes(b"fake")
    (media_dir / "note.TXT").write_text("not media")

    workflow = AudioTranscriptionWorkflow()
    files = workflow._discover_media_files(str(media_dir))

    assert {f.name for f in files} == {"MEETING.MP3", "VIDEO.MP4"}


def test_process_file_wav_writes_txt_json_srt(tmp_path: Path):
    wav_path = tmp_path / "sample.wav"
    output_dir = tmp_path / "out"
    _write_test_wav(wav_path, seconds=1.5)

    workflow = AudioTranscriptionWorkflow(
        config=TranscriptionConfig(
            transcription_backend="mock",
            max_speakers=2,
            diarization_window_seconds=0.5,
        )
    )

    result = workflow.process_file(
        input_path=wav_path,
        output_dir=output_dir,
        speaker_map={"SPEAKER_00": "Host"},
        output_formats=["txt", "json", "srt"],
    )

    assert result.success is True
    assert result.output_files.keys() == {"txt", "json", "srt"}

    txt = Path(result.output_files["txt"]).read_text(encoding="utf-8")
    assert "Host:" in txt

    payload = json.loads(Path(result.output_files["json"]).read_text(encoding="utf-8"))
    assert isinstance(payload, list)
    assert payload
    assert payload[0]["speaker_name"]

    srt = Path(result.output_files["srt"]).read_text(encoding="utf-8")
    assert "-->" in srt


def test_process_mp4_without_ffmpeg_returns_clear_error(tmp_path: Path, monkeypatch):
    mp4_path = tmp_path / "clip.mp4"
    mp4_path.write_bytes(b"fake-video")

    monkeypatch.setattr("src.services.audio.workflow.transcription_workflow.shutil.which", lambda _: None)

    workflow = AudioTranscriptionWorkflow()
    result = workflow.process_file(input_path=mp4_path, output_dir=tmp_path)

    assert result.success is False
    assert result.error is not None
    assert "ffmpeg" in result.error.lower()


def test_load_speaker_map_and_cli_compatibility(tmp_path: Path):
    speaker_map_file = tmp_path / "speakers.json"
    speaker_map_file.write_text('{"SPEAKER_00": "Alice", "SPEAKER_01": "Bob"}', encoding="utf-8")

    speaker_map = load_speaker_map(str(speaker_map_file))
    assert speaker_map["SPEAKER_00"] == "Alice"

    argv = ["smart_cli.py", "input.mp3", "--preview"]
    converted = apply_backward_compatible_default_command(argv)
    assert converted[1] == "tune"


def test_faster_whisper_backend_reports_missing_dependency(tmp_path: Path, monkeypatch):
    wav_path = tmp_path / "sample.wav"
    _write_test_wav(wav_path, seconds=1.0)

    # Patch inside the real implementation module (src layout), not the re-export wrapper.
    monkeypatch.setattr(
        "src.services.audio.workflow.transcription_workflow.importlib.util.find_spec",
        lambda _: None,
    )

    workflow = AudioTranscriptionWorkflow(
        config=TranscriptionConfig(transcription_backend="faster-whisper")
    )
    result = workflow.process_file(input_path=wav_path, output_dir=tmp_path)

    assert result.success is False
    assert result.error is not None
    assert "faster-whisper" in result.error


def test_faster_whisper_backend_raises_when_dependency_present(tmp_path: Path, monkeypatch):
    """When faster-whisper is installed the backend raises NotImplementedError
    to prevent callers from silently receiving placeholder mock text."""
    wav_path = tmp_path / "sample.wav"
    _write_test_wav(wav_path, seconds=1.0)

    # Pretend faster-whisper is installed by returning a truthy sentinel.
    monkeypatch.setattr(
        "src.services.audio.workflow.transcription_workflow.importlib.util.find_spec",
        lambda _: "present",
    )

    workflow = AudioTranscriptionWorkflow(
        config=TranscriptionConfig(transcription_backend="faster-whisper")
    )
    result = workflow.process_file(input_path=wav_path, output_dir=tmp_path)

    assert result.success is False
    assert result.error is not None
    assert "not yet wired" in result.error or "NotImplementedError" in result.error
