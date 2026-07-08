"""Tests for codex_ml.utils.optional_dependencies."""

from __future__ import annotations

import pytest

from codex_ml.utils.optional_dependencies import (
    build_optional_dependency_error,
    format_optional_dependency_error,
    raise_optional_dependency_error,
)


class TestFormatOptionalDependencyError:
    def test_contains_package_name(self):
        msg = format_optional_dependency_error("mypackage", "feature X")
        assert "mypackage" in msg, "Condition must be true"

    def test_contains_feature_name(self):
        msg = format_optional_dependency_error("mypackage", "feature X")
        assert "feature X" in msg, "Condition must be true"

    def test_contains_pip_install_hint(self):
        msg = format_optional_dependency_error("mypackage", "feature X")
        assert "pip install mypackage" in msg, "Condition must be true"

    def test_returns_string(self):
        assert isinstance(format_optional_dependency_error("pkg", "feat"), str)


class TestBuildOptionalDependencyError:
    def test_returns_import_error(self):
        err = build_optional_dependency_error("pkg", "feat")
        assert isinstance(err, ImportError)

    def test_message_matches_format(self):
        err = build_optional_dependency_error("numpy", "array ops")
        assert "numpy" in str(err), "Condition must be true"
        assert "array ops" in str(err), "Condition must be true"


class TestRaiseOptionalDependencyError:
    def test_raises_import_error(self):
        with pytest.raises(ImportError):
            raise_optional_dependency_error("pandas", "data loading")

    def test_error_message_contains_package(self):
        with pytest.raises(ImportError, match="pandas"):
            raise_optional_dependency_error("pandas", "data loading")

    def test_error_message_contains_feature(self):
        with pytest.raises(ImportError, match="data loading"):
            raise_optional_dependency_error("pandas", "data loading")
