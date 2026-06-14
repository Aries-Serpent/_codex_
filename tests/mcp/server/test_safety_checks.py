"""Tests for mcp.server.safety_checks."""

from __future__ import annotations

import pytest

from mcp.server.safety_checks import live_tests_enabled


def test_disabled_by_default(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("ENABLE_LIVE_TESTS", raising=False)
    assert live_tests_enabled() is False


def test_enabled_with_true(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ENABLE_LIVE_TESTS", "true")
    assert live_tests_enabled() is True


def test_enabled_with_1(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ENABLE_LIVE_TESTS", "1")
    assert live_tests_enabled() is True


def test_enabled_with_yes(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ENABLE_LIVE_TESTS", "yes")
    assert live_tests_enabled() is True


def test_disabled_with_false(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ENABLE_LIVE_TESTS", "false")
    assert live_tests_enabled() is False


def test_disabled_with_zero(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ENABLE_LIVE_TESTS", "0")
    assert live_tests_enabled() is False


def test_disabled_with_empty_string(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ENABLE_LIVE_TESTS", "")
    assert live_tests_enabled() is False


def test_disabled_with_random_value(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ENABLE_LIVE_TESTS", "maybe")
    assert live_tests_enabled() is False


def test_case_insensitive_true(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ENABLE_LIVE_TESTS", "TRUE")
    assert live_tests_enabled() is True


def test_case_insensitive_yes(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ENABLE_LIVE_TESTS", "YES")
    assert live_tests_enabled() is True
