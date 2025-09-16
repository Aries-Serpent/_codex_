from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from codex_ml.config import ConfigError, load_app_config


def _write(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "config.yaml"
    path.write_text(textwrap.dedent(content), encoding="utf-8")
    return path


def test_training_validation_errors_include_path(tmp_path: Path) -> None:
    cfg_path = _write(
        tmp_path,
        """
        training:
          batch_size: 0
        """,
    )
    with pytest.raises(ConfigError) as exc:
        load_app_config(cfg_path)
    assert "training.batch_size" in str(exc.value)


def test_defaults_are_applied(tmp_path: Path) -> None:
    cfg_path = _write(
        tmp_path,
        """
        training:
          output_dir: runs/test
        """,
    )
    cfg, raw = load_app_config(cfg_path)
    assert cfg.training.batch_size == 32
    assert raw.training.batch_size == 32
    assert cfg.training.output_dir == "runs/test"


def test_override_precedence(tmp_path: Path) -> None:
    cfg_path = _write(
        tmp_path,
        """
        training:
          learning_rate: 0.001
        """,
    )
    cfg, _ = load_app_config(cfg_path, overrides=("training.learning_rate=0.123",))
    assert cfg.training.learning_rate == pytest.approx(0.123)


def test_tokenization_required_fields(tmp_path: Path) -> None:
    cfg_path = _write(
        tmp_path,
        """
        tokenization:
          corpus_glob: ""
        """,
    )
    with pytest.raises(ConfigError) as exc:
        load_app_config(cfg_path)
    assert "tokenization.corpus_glob" in str(exc.value)


def test_split_ratio_validation(tmp_path: Path) -> None:
    cfg_path = _write(
        tmp_path,
        """
        data:
          split_ratios:
            train: 0.5
            validation: 0.4
        """,
    )
    with pytest.raises(ConfigError) as exc:
        load_app_config(cfg_path)
    assert "data.split_ratios" in str(exc.value)
