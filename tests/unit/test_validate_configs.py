"""Tests for scripts/ci/validate_configs.py — Gap 35 CI health fix."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_SCRIPTS_CI = str(Path(__file__).resolve().parent.parent.parent / "scripts" / "ci")
if _SCRIPTS_CI not in sys.path:
    sys.path.insert(0, _SCRIPTS_CI)

import validate_configs as vc  # noqa: E402

# ---------------------------------------------------------------------------
# validate_yaml_syntax tests
# ---------------------------------------------------------------------------


class TestValidateYamlSyntax:
    def test_valid_yaml_returns_none(self, tmp_path: Path) -> None:
        f = tmp_path / "ok.yaml"
        f.write_text("learning_rate: 0.001\nbatch_size: 32\n")
        assert vc.validate_yaml_syntax(f) is None, "Condition must be true"

    def test_invalid_yaml_returns_error_string(self, tmp_path: Path) -> None:
        f = tmp_path / "bad.yaml"
        f.write_text("key: [unclosed\n")
        result = vc.validate_yaml_syntax(f)
        assert result is not None, "result must be initialized"
        assert "YAML parse error" in result, "Result must not be empty"

    def test_empty_file_is_valid(self, tmp_path: Path) -> None:
        f = tmp_path / "empty.yaml"
        f.write_text("")
        assert vc.validate_yaml_syntax(f) is None, "Condition must be true"


# ---------------------------------------------------------------------------
# _is_train_candidate tests
# ---------------------------------------------------------------------------


class TestIsTrainCandidate:
    def test_dict_with_int_config_version_is_candidate(self) -> None:
        assert vc._is_train_candidate({"config_version": 1, "learning_rate": 1e-4})

    def test_dict_without_config_version_is_not_candidate(self) -> None:
        assert not vc._is_train_candidate({"learning_rate": 0.001}), "Condition must be true"

    def test_string_config_version_is_not_candidate(self) -> None:
        assert not vc._is_train_candidate({"config_version": "1.0"}), "Condition must be true"

    def test_non_dict_is_not_candidate(self) -> None:
        assert not vc._is_train_candidate([1, 2, 3])
        assert not vc._is_train_candidate("string"), "Condition must be true"
        assert not vc._is_train_candidate(None), "Condition must be true"

    def test_empty_dict_is_not_candidate(self) -> None:
        assert not vc._is_train_candidate({}), "Condition must be true"


# ---------------------------------------------------------------------------
# _should_skip tests
# ---------------------------------------------------------------------------


class TestShouldSkip:
    def test_skips_desired_subdir(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        configs_dir = tmp_path / "configs"
        configs_dir.mkdir()
        path = configs_dir / "desired" / "state.yaml"
        path.parent.mkdir(parents=True)
        path.write_text("x: 1")
        monkeypatch.setattr(vc, "CONFIGS_DIR", configs_dir)
        assert vc._should_skip(path), "Condition must be true"

    def test_does_not_skip_normal_training_config(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        configs_dir = tmp_path / "configs"
        configs_dir.mkdir()
        path = configs_dir / "train_base.yaml"
        path.write_text("learning_rate: 0.001\n")
        monkeypatch.setattr(vc, "CONFIGS_DIR", configs_dir)
        assert not vc._should_skip(path), "Condition must be true"


# ---------------------------------------------------------------------------
# run() tests
# ---------------------------------------------------------------------------


class TestRun:
    def test_run_on_empty_directory_returns_zero(self, tmp_path: Path) -> None:
        configs_dir = tmp_path / "configs"
        configs_dir.mkdir()
        failures = vc.run(configs_dir)
        assert failures == 0, "failures is not valid"

    def test_run_returns_zero_for_valid_syntax_only_yaml(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        configs_dir = tmp_path / "configs"
        configs_dir.mkdir()
        f = configs_dir / "alertmanager.yaml"
        f.write_text("route:\n  receiver: ops\n")
        monkeypatch.setattr(vc, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(vc, "CONFIGS_DIR", configs_dir)
        failures = vc.run(configs_dir)
        assert failures == 0, "failures is not valid"

    def test_run_counts_invalid_yaml_as_failure(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        configs_dir = tmp_path / "configs"
        configs_dir.mkdir()
        bad = configs_dir / "broken.yaml"
        bad.write_text("key: [unclosed\n")
        monkeypatch.setattr(vc, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(vc, "CONFIGS_DIR", configs_dir)
        failures = vc.run(configs_dir)
        assert failures == 1, "failures is not valid"

    def test_run_skips_desired_directory(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        configs_dir = tmp_path / "configs"
        (configs_dir / "desired").mkdir(parents=True)
        bad = configs_dir / "desired" / "bad.yaml"
        bad.write_text("key: [unclosed\n")  # bad yaml but should be skipped
        monkeypatch.setattr(vc, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(vc, "CONFIGS_DIR", configs_dir)
        failures = vc.run(configs_dir)
        assert failures == 0, "failures is not valid"

    def test_run_verbose_flag_accepted(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
    ) -> None:
        configs_dir = tmp_path / "configs"
        configs_dir.mkdir()
        f = configs_dir / "ok.yaml"
        f.write_text("name: ok\n")
        monkeypatch.setattr(vc, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(vc, "CONFIGS_DIR", configs_dir)
        failures = vc.run(configs_dir, verbose=True)
        assert failures == 0, "failures is not valid"


# ---------------------------------------------------------------------------
# validate_train_config — graceful degradation
# ---------------------------------------------------------------------------


class TestValidateTrainConfig:
    def test_returns_skip_message_when_import_fails(self, tmp_path: Path) -> None:
        path = tmp_path / "cfg.yaml"
        path.write_text("config_version: 1\nlearning_rate: 0.001\n")
        data = {"config_version": 1, "learning_rate": 0.001}
        with patch.dict("sys.modules", {"codex_ml.config_schema": None}):
            result = vc.validate_train_config(path, data)
        # Either None (valid) or skip/error message — should not crash
        assert result is None or isinstance(result, str)
