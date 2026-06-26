"""Tests for scripts/ci/check_workflow_yaml.py — Gap 35 CI health fix."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_SCRIPTS_CI = str(Path(__file__).resolve().parent.parent.parent / "scripts" / "ci")
if _SCRIPTS_CI not in sys.path:
    sys.path.insert(0, _SCRIPTS_CI)

import check_workflow_yaml as cwv  # noqa: E402

# ---------------------------------------------------------------------------
# validate_syntax tests
# ---------------------------------------------------------------------------


class TestValidateSyntax:
    def test_valid_yaml_returns_no_errors(self, tmp_path: Path) -> None:
        f = tmp_path / "ok.yml"
        f.write_text("name: CI\non: [push]\njobs:\n  test:\n    runs-on: ubuntu-latest\n")
        errors = cwv.validate_syntax([str(f)])
        assert errors == [], "Error should be raised or set"

    def test_invalid_yaml_returns_error(self, tmp_path: Path) -> None:
        f = tmp_path / "bad.yml"
        f.write_text("key: [unclosed\n")
        errors = cwv.validate_syntax([str(f)])
        assert len(errors) == 1, "Errors must not be empty"
        assert "bad.yml" in errors[0], "Error should be raised or set"
        assert "YAML syntax error" in errors[0], "Error should be raised or set"

    def test_missing_file_returns_error(self, tmp_path: Path) -> None:
        errors = cwv.validate_syntax([str(tmp_path / "nonexistent.yml")])
        assert len(errors) == 1, "Errors must not be empty"
        assert "cannot open file" in errors[0], "Error should be raised or set"

    def test_multiple_files_some_valid(self, tmp_path: Path) -> None:
        good = tmp_path / "good.yml"
        good.write_text("name: ok\n")
        bad = tmp_path / "bad.yml"
        bad.write_text("key: [unclosed\n")
        errors = cwv.validate_syntax([str(good), str(bad)])
        assert len(errors) == 1, "Errors must not be empty"
        assert "bad.yml" in errors[0], "Error should be raised or set"

    def test_empty_file_is_valid_yaml(self, tmp_path: Path) -> None:
        f = tmp_path / "empty.yml"
        f.write_text("")
        errors = cwv.validate_syntax([str(f)])
        assert errors == [], "Error should be raised or set"

    def test_no_paths_returns_empty(self) -> None:
        errors = cwv.validate_syntax([])
        assert errors == [], "Error should be raised or set"


# ---------------------------------------------------------------------------
# validate_schema tests
# ---------------------------------------------------------------------------


class TestValidateSchema:
    def test_check_jsonschema_available_returns_bool(self) -> None:
        result = cwv._check_jsonschema_available()
        assert isinstance(result, bool)

    def test_validate_schema_calls_subprocess(self, tmp_path: Path) -> None:
        f = tmp_path / "wf.yml"
        f.write_text("name: CI\n")
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        with patch("check_workflow_yaml.subprocess.run", return_value=mock_result) as mock_run:
            errors = cwv.validate_schema([str(f)])
        assert errors == [], "Error should be raised or set"
        mock_run.assert_called_once()

    def test_validate_schema_returns_error_on_failure(self, tmp_path: Path) -> None:
        f = tmp_path / "wf.yml"
        f.write_text("name: CI\n")
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "Schema validation failed"
        mock_result.stderr = ""
        with patch("check_workflow_yaml.subprocess.run", return_value=mock_result):
            errors = cwv.validate_schema([str(f)])
        assert len(errors) == 1, "Errors must not be empty"
        assert "Schema validation failed" in errors[0], "Error should be raised or set"


# ---------------------------------------------------------------------------
# main() tests
# ---------------------------------------------------------------------------


class TestMain:
    def test_main_exits_zero_when_no_paths(self) -> None:
        with patch.object(sys, "argv", ["check_workflow_yaml.py"]):
            with pytest.raises(SystemExit) as exc_info:
                cwv.main()
        assert exc_info.value.code == 0, "Value must be initialized"

    def test_main_exits_one_on_syntax_error(self, tmp_path: Path) -> None:
        f = tmp_path / "bad.yml"
        f.write_text("key: [unclosed\n")
        with patch.object(sys, "argv", ["check_workflow_yaml.py", str(f)]):
            with pytest.raises(SystemExit) as exc_info:
                cwv.main()
        assert exc_info.value.code == 1, "Value must be initialized"

    def test_main_exits_zero_on_valid_yaml_without_jsonschema(self, tmp_path: Path) -> None:
        f = tmp_path / "ok.yml"
        f.write_text("name: CI\non: [push]\njobs:\n  build:\n    runs-on: ubuntu-latest\n")
        with patch.object(sys, "argv", ["check_workflow_yaml.py", str(f)]):
            with patch("check_workflow_yaml._check_jsonschema_available", return_value=False):
                with pytest.raises(SystemExit) as exc_info:
                    cwv.main()
        assert exc_info.value.code == 0, "Value must be initialized"
