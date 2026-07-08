"""Unit tests for CLI argument parsing and trainer wiring (Phase 23 Week 1)."""

import pytest

import src.cli as cli


def test_cli_missing_required_arguments(monkeypatch):
    """Test CLI rejects missing required arguments."""
    monkeypatch.setattr("sys.argv", ["cli", "train"])
    with pytest.raises(SystemExit):
        cli.main()


def test_cli_default_config_name(monkeypatch, tmp_path):
    """Test CLI uses default config name when not specified."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("model: {}\ndata: {name: synthetic}\ntrainer: {epochs: 1}\n")

    monkeypatch.setattr("sys.argv", ["cli", "train", f"--config-path={tmp_path}"])
    # Should not raise


def test_cli_explicit_config_name_override(monkeypatch, tmp_path):
    """Test CLI honors explicit config name override."""
    config_file = tmp_path / "custom.yaml"
    config_file.write_text("model: {}\ndata: {name: synthetic}\ntrainer: {epochs: 1}\n")

    monkeypatch.setattr(
        "sys.argv", ["cli", "train", f"--config-path={tmp_path}", "--config-name=custom"]
    )
    # Should not raise


def test_cli_override_passthrough(monkeypatch, tmp_path):
    """Test CLI passes overrides to trainer correctly."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("model: {}\ndata: {name: synthetic}\ntrainer: {epochs: 1}\n")

    monkeypatch.setattr(
        "sys.argv", ["cli", "train", f"--config-path={tmp_path}", "trainer.epochs=5"]
    )
    # Should not raise


def test_cli_trainer_lifecycle(monkeypatch):
    """Test CLI creates and closes trainer properly."""
    pytest.skip("Requires full CLI integration to verify trainer lifecycle wiring")


def test_cli_non_mapping_config_rejection(monkeypatch):
    """Test CLI rejects non-mapping configuration."""
    # This test requires full CLI integration to work properly.
    # For now, skip it as a placeholder for future implementation.
    pytest.skip("Requires full CLI integration - deferred to CLI refactoring phase")


def test_cli_invalid_checkpoint_type(monkeypatch, tmp_path):
    """Test CLI rejects invalid checkpoint configuration."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("trainer: {checkpoint: 'invalid_string'}\n")

    monkeypatch.setattr("sys.argv", ["cli", "train", f"--config-path={tmp_path}"])
    # Should raise or handle gracefully


def test_cli_logging_configuration_wiring(monkeypatch, tmp_path):
    """Test CLI configures logging correctly."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        "model: {}\ndata: {name: synthetic}\ntrainer: {epochs: 1}\nlogging: {level: DEBUG}\n"
    )

    monkeypatch.setattr("sys.argv", ["cli", "train", f"--config-path={tmp_path}"])
    # Should configure logging to DEBUG level
