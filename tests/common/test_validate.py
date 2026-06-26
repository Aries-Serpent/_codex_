"""Smoke tests for :mod:`common.validate` with a stubbed GE backend."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

# Skip tests if great_expectations is not available
pytest.importorskip("great_expectations", reason="great_expectations not installed")


class _StubValidator:
    def __init__(self) -> None:
        self.expectations: list[str] = []
        self.expectation_suite = SimpleNamespace(expectations=self.expectations)

    def expect_column_values_to_not_be_null(
        self, column: str
    ) -> None:  # pragma: no cover - simple stub
        self.expectations.append(f"not_null:{column}")

    def expect_column_values_to_be_unique(self, column: str) -> None:
        self.expectations.append(f"unique:{column}")

    def expect_column_values_to_be_between(
        self, column: str, min_value: Any, max_value: Any
    ) -> None:
        self.expectations.append(f"between:{column}:{min_value}:{max_value}")

    def save_expectation_suite(self, discard_failed_expectations: bool = False) -> None:
        return None

    def get_expectation_suite(self, discard_failed_expectations: bool = False):
        return self.expectation_suite


class _StubContext:
    def __init__(self) -> None:
        self.sources = SimpleNamespace(pandas_default=self)
        self._suite = None

    def get_context(self):  # pragma: no cover - compatibility
        return self

    def get_expectation_suite(self, name: str):
        if self._suite is None:
            raise Exception("missing")
        return self._suite

    def add_or_update_expectation_suite(self, name: str):
        self._suite = SimpleNamespace(expectations=[])
        return self._suite

    def read_csv(self, path: str) -> _StubValidator:  # pandas_default.read_csv
        return _StubValidator()

    def add_or_update_checkpoint(self, name: str, validator: _StubValidator):
        class _Checkpoint:
            def run(self):
                return SimpleNamespace(success=True)

        return _Checkpoint()

    def build_data_docs(self) -> None:
        return None


@pytest.fixture(autouse=True)
def stub_great_expectations(monkeypatch: pytest.MonkeyPatch) -> None:
    context = _StubContext()
    stub_module = SimpleNamespace(get_context=context.get_context)
    monkeypatch.setitem(sys.modules, "great_expectations", stub_module)
    # Ensure fresh import of common.validate to use stub
    sys.modules.pop("common.validate", None)


def test_run_clean_checkpoint(tmp_path: Path) -> None:
    from common import validate

    csv_file = tmp_path / "data.csv"
    csv_file.write_text("id,value\n1,1\n2,2\n")

    success, docs_out = validate.run_clean_checkpoint(csv_file)

    assert success is True, "success is not valid"
    assert docs_out.exists(), "Condition must be true"
