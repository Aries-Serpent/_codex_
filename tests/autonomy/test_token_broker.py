"""
Tests for Phase 2 — Token Broker
(src/codex/autonomy/token_broker.py)
"""

from __future__ import annotations

import pytest

from codex.autonomy.registry import AutonomyMode, AutonomyRegistry, ControlClass
from codex.autonomy.token_broker import (
    _SOURCE_CEILING,
    TokenBroker,
    TokenBrokerError,
    TokenResolution,
    TokenSource,
    _cc_level,
)


def _reg(**kwargs) -> AutonomyRegistry:
    defaults = dict(
        autonomy_mode=AutonomyMode.SAFE_AUTO,
        kill_switch=False,
        dry_run=False,
        token_resolution_order=["github_app", "oidc", "scoped_pat", "codex_master"],
    )
    defaults.update(kwargs)
    return AutonomyRegistry(**defaults)


class TestTokenSource:
    def test_all_sources_have_ceiling(self):
        for src in TokenSource:
            if src != TokenSource.NONE:
                assert src in _SOURCE_CEILING, f"Missing ceiling for {src}"

    def test_codex_master_has_highest_ceiling(self):
        master_lvl = _cc_level(_SOURCE_CEILING[TokenSource.CODEX_MASTER])
        for src, ceiling in _SOURCE_CEILING.items():
            if src == TokenSource.NONE:
                continue
            assert master_lvl >= _cc_level(ceiling), f"{src} ceiling exceeds CODEX_MASTER"


class TestTokenBroker:
    def test_dry_run_returns_none_token(self):
        reg = _reg(dry_run=True)
        broker = TokenBroker(registry=reg)
        result = broker.resolve(ControlClass.REPO_STATE_WRITE)
        assert result.is_dry_run, "Result must not be empty"
        assert result.token is None, "Result must not be empty"
        assert result.available, "Result must not be empty"

    def test_no_env_vars_returns_none_token(self, monkeypatch):
        for var in (
            "GITHUB_APP_TOKEN",
            "CODEX_SCOPED_PAT",
            "CODEX_MASTER_KEY",
            "ACTIONS_ID_TOKEN_REQUEST_URL",
        ):
            monkeypatch.delenv(var, raising=False)
        broker = TokenBroker(registry=_reg())
        result = broker.resolve(ControlClass.READ_ONLY)
        assert result.token is None, "Result must not be empty"
        assert not result.available, "Result must not be empty"

    def test_resolves_github_app_token(self, monkeypatch):
        monkeypatch.setenv("GITHUB_APP_TOKEN", "ghs_test_app_token")
        broker = TokenBroker(registry=_reg())
        result = broker.resolve(ControlClass.ADVISORY_WRITE)
        assert result.source == TokenSource.GITHUB_APP, "Result must not be empty"
        assert result.token == "ghs_test_app_token", "Result must not be empty"

    def test_skips_too_low_source(self, monkeypatch):
        # SCOPED_PAT ceiling is ADVISORY_WRITE — cannot service INFRA_WRITE
        monkeypatch.delenv("GITHUB_APP_TOKEN", raising=False)
        monkeypatch.delenv("ACTIONS_ID_TOKEN_REQUEST_URL", raising=False)
        monkeypatch.setenv("CODEX_SCOPED_PAT", "scoped_pat_token")
        monkeypatch.setenv("CODEX_MASTER_KEY", "master_key_token")
        reg = _reg(token_resolution_order=["scoped_pat", "codex_master"])
        broker = TokenBroker(registry=reg)
        result = broker.resolve(ControlClass.INFRA_WRITE)
        assert result.source == TokenSource.CODEX_MASTER, "Result must not be empty"
        assert result.token == "master_key_token", "Result must not be empty"

    def test_require_raises_when_no_token(self, monkeypatch):
        for var in (
            "GITHUB_APP_TOKEN",
            "CODEX_SCOPED_PAT",
            "CODEX_MASTER_KEY",
            "ACTIONS_ID_TOKEN_REQUEST_URL",
        ):
            monkeypatch.delenv(var, raising=False)
        broker = TokenBroker(registry=_reg())
        with pytest.raises(TokenBrokerError):
            broker.resolve(ControlClass.ADVISORY_WRITE, require=True)

    def test_string_control_class_accepted(self, monkeypatch):
        monkeypatch.setenv("GITHUB_APP_TOKEN", "tok")
        broker = TokenBroker(registry=_reg())
        result = broker.resolve("ADVISORY_WRITE")
        assert result.control_class == ControlClass.ADVISORY_WRITE, "Result must not be empty"


class TestTokenResolution:
    def test_available_false_when_no_token_and_not_dry_run(self):
        r = TokenResolution(
            source=TokenSource.NONE,
            token=None,
            control_class=ControlClass.READ_ONLY,
        )
        assert not r.available, "Condition must be true"

    def test_available_true_when_token_present(self):
        r = TokenResolution(
            source=TokenSource.GITHUB_APP,
            token="abc",
            control_class=ControlClass.READ_ONLY,
        )
        assert r.available, "Condition must be true"
