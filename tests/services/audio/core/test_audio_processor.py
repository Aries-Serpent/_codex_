from pathlib import Path

from services.audio.core.audio_processor import (
    AudioConfig,
    AudioProcessor,
    ProcessingProfile,
    ProcessingResult,
)


def test_audio_config():
    config = AudioConfig()
    assert config.sample_rate == 44100


def test_processing_profile():
    profile = ProcessingProfile(name="test", parameters={"key": "val"})
    assert profile.name == "test"
    assert profile.parameters == {"key": "val"}


def test_processing_result():
    res = ProcessingResult(
        success=True,
        output_path=Path("out.wav"),
        quality_score=9.0,
        processing_time=1.5,
    )
    assert res.success is True
    assert res.output_path == Path("out.wav")
    assert res.quality_score == 9.0
    assert res.processing_time == 1.5
    assert res.error is None


def test_audio_processor_process_file(tmp_path):
    config = AudioConfig()
    processor = AudioProcessor(config)
    profile = ProcessingProfile(name="basic", parameters={})

    in_path = tmp_path / "in.wav"
    out_path = tmp_path / "out.wav"

    result = processor.process_file(in_path, out_path, profile)

    assert result.success is True
    assert result.output_path == out_path
    assert result.quality_score == 8.5
    assert result.error is None
    assert result.processing_time >= 0
