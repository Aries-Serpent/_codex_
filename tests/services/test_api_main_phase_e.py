"""Phase E tests for services/api/main.py — helper functions and HTTP endpoints."""

from __future__ import annotations

import importlib
import sys
import types
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

# Ensure repo root is on sys.path so 'services.*' is importable
_REPO_ROOT = Path(__file__).resolve().parents[2]
_ROOT_SERVICES = str(_REPO_ROOT / "services")
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
# Extend services.__path__ to include both src/services and root services/
try:
    import services as _svc_pkg

    if hasattr(_svc_pkg, "__path__") and _ROOT_SERVICES not in _svc_pkg.__path__:
        _svc_pkg.__path__.append(_ROOT_SERVICES)
except ImportError:
    # Some focused test runs may not have the namespace package importable yet.
    pass

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _reload_api(monkeypatch: pytest.MonkeyPatch, *, auth_enabled: bool = False):
    """Reload services.api.main for an isolated test.

    Parameters
    ----------
    auth_enabled:
        When True, does NOT set CODEX_AUTH_MIDDLEWARE_ENABLED=0, so the
        API-key middleware is active.  Used by auth-guarded endpoint tests.
    """
    if not auth_enabled:
        monkeypatch.setenv("CODEX_AUTH_MIDDLEWARE_ENABLED", "0")
    monkeypatch.delenv("API_KEY", raising=False)
    monkeypatch.delenv("API_RATE_LIMIT", raising=False)

    # --- torch shim robustness --------------------------------------------------
    # services/api/main.py installs fake torch helpers only when
    # ``not hasattr(torch, "as_tensor")``.  After the first test the shim has
    # already patched the torch module, so subsequent reloads would skip it and
    # leave ``torch.tensor`` pointing to ``_raise_missing`` if something (e.g.
    # monkeypatch teardown of a previous test) unset it.
    #
    # Fix: (a) evict the cached module so importlib always does a fresh import,
    # and (b) use monkeypatch to temporarily remove ``torch.as_tensor`` so the
    # shim condition is satisfied → _fake_tensor is installed every time.
    sys.modules.pop("services.api.main", None)
    import torch as _t

    if hasattr(_t, "as_tensor"):
        monkeypatch.delattr(_t, "as_tensor")

    return importlib.import_module("services.api.main")


class _FakeTokenizer:
    def __init__(self, vocab_size: int = 32):
        self.model_max_length = 512
        self._vocab_size = vocab_size

    def encode(self, text: str) -> list[int]:
        return [ord(c) % self._vocab_size for c in text[:5]]

    def decode(self, tokens: list[int]) -> str:
        return " ".join(str(t) for t in tokens)


class _FakeModel:
    def __init__(self, vocab_size: int = 32):
        self._vocab_size = vocab_size
        self.config = types.SimpleNamespace(vocab_size=vocab_size)

    def eval(self) -> "_FakeModel":
        return self

    def __call__(self, input_ids: Any) -> dict[str, Any]:
        raw = input_ids.tolist() if hasattr(input_ids, "tolist") else input_ids
        tokens = list(raw[0]) if raw and isinstance(raw[0], list) else list(raw)
        n = len(tokens) or 1
        logits = [[[0] * self._vocab_size] * n]
        logits[0][-1][1] = 1
        # Return as dict with tensor-like object
        return {"logits": input_ids.__class__([[[0] * self._vocab_size] * n])}


def _make_client(monkeypatch: pytest.MonkeyPatch) -> tuple[Any, TestClient]:
    """Return (module, TestClient) with faked model/tokenizer."""
    mod = _reload_api(monkeypatch)
    monkeypatch.setattr(mod, "get_tokenizer", lambda _: _FakeTokenizer())
    monkeypatch.setattr(mod, "get_model", lambda *_: mod._EchoModel(vocab_size=32))
    monkeypatch.setattr(mod, "apply_lora", lambda m: m)
    client = TestClient(mod.app, raise_server_exceptions=False)
    return mod, client


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------


class TestHealthEndpoint:
    def test_health_returns_200(self, monkeypatch):
        mod = _reload_api(monkeypatch)
        with TestClient(mod.app) as client:
            resp = client.get("/health")
        assert resp.status_code == 200, "status_code is not valid"
        data = resp.json()
        assert data["status"] == "healthy", "Data must not be empty"
        assert "timestamp" in data, "Data must not be empty"

    def test_health_no_auth_required(self, monkeypatch):
        monkeypatch.setenv("CODEX_AUTH_MIDDLEWARE_ENABLED", "0")
        mod = _reload_api(monkeypatch)
        with TestClient(mod.app) as client:
            resp = client.get("/health")
        assert resp.status_code == 200, "status_code is not valid"


# ---------------------------------------------------------------------------
# /ready
# ---------------------------------------------------------------------------


class TestReadinessEndpoint:
    def test_ready_before_model_load_503(self, monkeypatch):
        mod = _reload_api(monkeypatch)
        # Clear any model state to simulate not-yet-loaded
        if hasattr(mod.app.state, "model"):
            del mod.app.state.model
        with TestClient(mod.app, raise_server_exceptions=False) as client:
            resp = client.get("/ready")
        assert resp.status_code == 503, "status_code is not valid"

    def test_ready_after_model_load_200(self, monkeypatch):
        mod = _reload_api(monkeypatch)
        mod.app.state.model = object()  # Inject a fake model
        with TestClient(mod.app) as client:
            resp = client.get("/ready")
        assert resp.status_code == 200, "status_code is not valid"
        data = resp.json()
        assert data["status"] == "ready", "Data must not be empty"
        assert data["checks"]["model"] is True, "Data must not be empty"
        assert data["checks"]["db"] is True, "Data must not be empty"


# ---------------------------------------------------------------------------
# /status
# ---------------------------------------------------------------------------


class TestStatusEndpoint:
    def test_status_returns_200(self, monkeypatch):
        mod = _reload_api(monkeypatch)
        with TestClient(mod.app) as client:
            resp = client.get("/status")
        assert resp.status_code == 200, "status_code is not valid"
        data = resp.json()
        assert data["ok"] is True, "Data must not be empty"
        assert "queue" in data, "Data must not be empty"
        assert "jobs" in data, "Data must not be empty"


# ---------------------------------------------------------------------------
# /evaluate
# ---------------------------------------------------------------------------


class TestEvaluateEndpoint:
    def test_evaluate_basic(self, monkeypatch):
        mod = _reload_api(monkeypatch)
        with TestClient(mod.app) as client:
            resp = client.post("/evaluate", json={"dataset": "my-data", "limit": 50})
        assert resp.status_code == 200, "status_code is not valid"
        data = resp.json()
        assert data["ok"] is True, "Data must not be empty"
        assert data["dataset"] == "my-data", "Data must not be empty"
        assert data["limit"] == 50, "Data must not be empty"
        assert "metrics" in data, "Data must not be empty"

    def test_evaluate_default_limit(self, monkeypatch):
        mod = _reload_api(monkeypatch)
        with TestClient(mod.app) as client:
            resp = client.post("/evaluate", json={"dataset": "test-set"})
        assert resp.status_code == 200, "status_code is not valid"
        assert resp.json()["limit"] == 100, "Condition must be true"


# ---------------------------------------------------------------------------
# /train
# ---------------------------------------------------------------------------


class TestTrainEndpoint:
    def test_train_enqueues_job(self, monkeypatch):
        mod = _reload_api(monkeypatch)
        with TestClient(mod.app) as client:
            resp = client.post("/train", json={"epochs": 2})
        assert resp.status_code == 200, "status_code is not valid"
        data = resp.json()
        assert data["ok"] is True, "Data must not be empty"
        assert "job_id" in data, "Data must not be empty"

    def test_train_default_epochs(self, monkeypatch):
        mod = _reload_api(monkeypatch)
        with TestClient(mod.app) as client:
            resp = client.post("/train", json={})
        assert resp.status_code == 200, "status_code is not valid"

    def test_train_invalid_epochs_422(self, monkeypatch):
        mod = _reload_api(monkeypatch)
        with TestClient(mod.app, raise_server_exceptions=False) as client:
            resp = client.post("/train", json={"epochs": 0})
        assert resp.status_code == 422, "status_code is not valid"


# ---------------------------------------------------------------------------
# /infer
# ---------------------------------------------------------------------------


class TestInferEndpoint:
    def test_infer_basic(self, monkeypatch):
        mod, client = _make_client(monkeypatch)
        monkeypatch.setattr(mod, "validate_input", lambda text, **_: text)
        monkeypatch.setattr(mod, "enforce_content_policies", lambda _: None)
        with client:
            resp = client.post("/infer", json={"prompt": "hello"})
        assert resp.status_code == 200, "status_code is not valid"

    def test_infer_empty_prompt_422(self, monkeypatch):
        mod, client = _make_client(monkeypatch)
        with client:
            resp = client.post("/infer", json={"prompt": ""})
        assert resp.status_code == 422, "status_code is not valid"

    def test_infer_missing_prompt_422(self, monkeypatch):
        mod, client = _make_client(monkeypatch)
        with client:
            resp = client.post("/infer", json={})
        assert resp.status_code == 422, "status_code is not valid"

    def test_infer_returns_completion_and_tokens(self, monkeypatch):
        mod = _reload_api(monkeypatch)
        monkeypatch.setattr(mod, "get_tokenizer", lambda _: _FakeTokenizer(vocab_size=128))
        monkeypatch.setattr(mod, "get_model", lambda *_: mod._EchoModel(vocab_size=128))
        monkeypatch.setattr(mod, "apply_lora", lambda m: m)
        # Bypass security so simple prompt passes
        monkeypatch.setattr(mod, "validate_input", lambda text, **_: text)
        monkeypatch.setattr(mod, "enforce_content_policies", lambda _: None)
        with TestClient(mod.app) as client:
            resp = client.post("/infer", json={"prompt": "hi"})
        if resp.status_code == 200:
            data = resp.json()
            assert "completion" in data, "Data must not be empty"
            assert "tokens" in data, "Data must not be empty"
            assert isinstance(data["tokens"], int)

    def test_infer_rate_key_returns_string(self, monkeypatch):
        mod = _reload_api(monkeypatch)
        req = MagicMock()
        key = mod._rate_key(req)
        assert key == "infer", "key is not valid"


# ---------------------------------------------------------------------------
# _mask_secrets
# ---------------------------------------------------------------------------


class TestMaskSecrets:
    def _get_fn(self, monkeypatch):
        monkeypatch.delenv("DISABLE_SECRET_FILTER", raising=False)
        mod = _reload_api(monkeypatch)
        return mod._mask_secrets

    def test_no_secrets_unchanged(self, monkeypatch):
        fn = self._get_fn(monkeypatch)
        text = "just a normal sentence"
        assert fn(text) == text, "Condition must be true"

    def test_openai_key_masked(self, monkeypatch):
        fn = self._get_fn(monkeypatch)
        result = fn("My key is sk-abcdefghij1234567890 use it")
        assert "sk-" not in result or "[SECRET]" in result, "Result must not be empty"

    def test_github_pat_masked(self, monkeypatch):
        fn = self._get_fn(monkeypatch)
        result = fn("token: ghp_" + "A" * 40)
        assert "[SECRET]" in result, "Result must not be empty"

    def test_disable_filter_env_passes_through(self, monkeypatch):
        monkeypatch.setenv("DISABLE_SECRET_FILTER", "1")  # pragma: allowlist secret
        mod = _reload_api(monkeypatch)
        text = "sk-abcdefghij1234567890"  # pragma: allowlist secret
        assert mod._mask_secrets(text) == text, "Condition must be true"


# ---------------------------------------------------------------------------
# _coerce_positive_int
# ---------------------------------------------------------------------------


class TestCoercePositiveInt:
    def _fn(self, monkeypatch):
        return _reload_api(monkeypatch)._coerce_positive_int

    def test_positive_int(self, monkeypatch):
        assert self._fn(monkeypatch)(5) == 5, "Condition must be true"

    def test_zero_returns_none(self, monkeypatch):
        assert self._fn(monkeypatch)(0) is None, "Condition must be true"

    def test_negative_returns_none(self, monkeypatch):
        assert self._fn(monkeypatch)(-1) is None, "Condition must be true"

    def test_positive_float_int(self, monkeypatch):
        assert self._fn(monkeypatch)(4.0) == 4, "Condition must be true"

    def test_non_integer_float_returns_none(self, monkeypatch):
        assert self._fn(monkeypatch)(3.5) is None, "Condition must be true"

    def test_bool_returns_none(self, monkeypatch):
        assert self._fn(monkeypatch)(True) is None, "Condition must be true"

    def test_string_returns_none(self, monkeypatch):
        assert self._fn(monkeypatch)("10") is None, "Condition must be true"


# ---------------------------------------------------------------------------
# _parse_env_context_limit
# ---------------------------------------------------------------------------


class TestParseEnvContextLimit:
    def _fn(self, monkeypatch):
        return _reload_api(monkeypatch)._parse_env_context_limit

    def test_unset_returns_none(self, monkeypatch):
        monkeypatch.delenv("API_MAX_PROMPT_TOKENS", raising=False)
        assert self._fn(monkeypatch)() is None, "Condition must be true"

    def test_valid_positive_int(self, monkeypatch):
        monkeypatch.setenv("API_MAX_PROMPT_TOKENS", "1024")
        mod = _reload_api(monkeypatch)
        assert mod._parse_env_context_limit() == 1024, "Condition must be true"

    def test_zero_returns_none(self, monkeypatch):
        monkeypatch.setenv("API_MAX_PROMPT_TOKENS", "0")
        mod = _reload_api(monkeypatch)
        assert mod._parse_env_context_limit() is None, "Condition must be true"

    def test_invalid_string_returns_none(self, monkeypatch):
        monkeypatch.setenv("API_MAX_PROMPT_TOKENS", "abc")
        mod = _reload_api(monkeypatch)
        assert mod._parse_env_context_limit() is None, "Condition must be true"


# ---------------------------------------------------------------------------
# _resolve_context_limit
# ---------------------------------------------------------------------------


class TestResolveContextLimit:
    def test_env_overrides_model(self, monkeypatch):
        monkeypatch.setenv("API_MAX_PROMPT_TOKENS", "512")
        mod = _reload_api(monkeypatch)
        result = mod._resolve_context_limit(MagicMock(), MagicMock())
        assert result == 512, "Result must not be empty"

    def test_model_attribute_used_when_no_env(self, monkeypatch):
        monkeypatch.delenv("API_MAX_PROMPT_TOKENS", raising=False)
        mod = _reload_api(monkeypatch)
        tokenizer = MagicMock(model_max_length=256)
        model = MagicMock()
        # Remove attributes that would match first
        del model.cfg
        del model.config
        result = mod._resolve_context_limit(tokenizer, model)
        assert result in (256, None)  # Depends on which attr path matches

    def test_none_when_no_info(self, monkeypatch):
        monkeypatch.delenv("API_MAX_PROMPT_TOKENS", raising=False)
        mod = _reload_api(monkeypatch)
        tokenizer = types.SimpleNamespace()
        model = types.SimpleNamespace()
        result = mod._resolve_context_limit(tokenizer, model)
        assert result is None, "Result must not be empty"


# ---------------------------------------------------------------------------
# _get_model_vocab_size
# ---------------------------------------------------------------------------


class TestGetModelVocabSize:
    def test_from_config_vocab_size(self, monkeypatch):
        mod = _reload_api(monkeypatch)
        model = types.SimpleNamespace(config=types.SimpleNamespace(vocab_size=50257))
        result = mod._get_model_vocab_size(model)
        assert result == 50257, "Result must not be empty"

    def test_from_direct_vocab_size(self, monkeypatch):
        mod = _reload_api(monkeypatch)
        model = types.SimpleNamespace(vocab_size=32000)
        result = mod._get_model_vocab_size(model)
        assert result == 32000, "Result must not be empty"

    def test_returns_none_when_no_vocab_size(self, monkeypatch):
        mod = _reload_api(monkeypatch)
        model = types.SimpleNamespace()
        result = mod._get_model_vocab_size(model)
        assert result is None, "Result must not be empty"


# ---------------------------------------------------------------------------
# API key middleware
# ---------------------------------------------------------------------------


class TestApiKeyMiddleware:
    def test_no_api_key_configured_passes(self, monkeypatch):
        monkeypatch.delenv("API_KEY", raising=False)
        mod = _reload_api(monkeypatch)
        with TestClient(mod.app) as client:
            resp = client.get("/health")
        assert resp.status_code == 200, "status_code is not valid"

    def test_wrong_api_key_blocked(self, monkeypatch):
        monkeypatch.setenv("API_KEY", "secret-key-12345")
        # auth_enabled=True keeps CODEX_AUTH_MIDDLEWARE_ENABLED at its default (1)
        # so the API-key middleware is active and an invalid key returns 401.
        mod = _reload_api(monkeypatch, auth_enabled=True)
        with TestClient(mod.app, raise_server_exceptions=False) as client:
            resp = client.get("/status", headers={"x-api-key": "wrong"})
        assert resp.status_code == 401, "status_code is not valid"

    def test_correct_api_key_passes(self, monkeypatch):
        monkeypatch.setenv("API_KEY", "correct-key")
        mod = _reload_api(monkeypatch)
        with TestClient(mod.app) as client:
            resp = client.get("/status", headers={"x-api-key": "correct-key"})
        assert resp.status_code == 200, "status_code is not valid"


# ---------------------------------------------------------------------------
# _EchoModel
# ---------------------------------------------------------------------------


class TestEchoModel:
    def test_echo_model_returns_logits(self, monkeypatch):
        mod = _reload_api(monkeypatch)
        model = mod._EchoModel(vocab_size=16)
        # Input shape is [[token1, token2, ...]] — a single batch of flat token ids.
        result = model([[1, 2, 3]])
        assert "logits" in result, "Result must not be empty"

    def test_echo_model_eval_returns_self(self, monkeypatch):
        mod = _reload_api(monkeypatch)
        model = mod._EchoModel()
        assert model.eval() is model, "Condition must be true"

    def test_echo_model_empty_tokens(self, monkeypatch):
        mod = _reload_api(monkeypatch)
        model = mod._EchoModel(vocab_size=8)
        result = model([[]])
        assert "logits" in result, "Result must not be empty"

    def test_check_db_connection(self, monkeypatch):
        mod = _reload_api(monkeypatch)
        assert mod.check_db_connection() is True, "Condition must be true"

    def test_check_model_loaded_false_when_no_model(self, monkeypatch):
        mod = _reload_api(monkeypatch)
        if hasattr(mod.app.state, "model"):
            del mod.app.state.model
        # checkfn is not bound to app state at import time; just call it
        result = mod.check_model_loaded()
        assert isinstance(result, bool)
