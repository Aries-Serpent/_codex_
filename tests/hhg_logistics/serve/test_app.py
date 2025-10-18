"""Unit tests for hhg_logistics.serve.app helpers."""

from __future__ import annotations

import asyncio
import builtins
import os
import sys
import types
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Lightweight stubs for optional ray.serve dependency used during import.
# ---------------------------------------------------------------------------
serve_module = types.ModuleType("ray.serve")


def _deployment_decorator(*_args: Any, **_kwargs: Any):
    def _decorator(obj):
        return obj

    return _decorator


def _ingress_decorator(_app: Any):
    def _decorator(obj):
        return obj

    return _decorator


def _batch_decorator(*_args: Any, **_kwargs: Any):
    def _decorator(func):
        async def _wrapper(*args: Any, **kwargs: Any):
            return await func(*args, **kwargs)

        _wrapper.__wrapped__ = func
        return _wrapper

    return _decorator


serve_module.batch = _batch_decorator
serve_module.deployment = _deployment_decorator
serve_module.ingress = _ingress_decorator
serve_module.start = lambda *_args, **_kwargs: None
serve_module.shutdown = lambda *_args, **_kwargs: None

ray_module = types.ModuleType("ray")
ray_module.init = lambda *_args, **_kwargs: None
ray_module.shutdown = lambda *_args, **_kwargs: None
ray_module.serve = serve_module

sys.modules.setdefault("ray", ray_module)
sys.modules.setdefault("ray.serve", serve_module)


# ---------------------------------------------------------------------------
# Minimal hydra stub to bypass optional dependency requirements.
# ---------------------------------------------------------------------------
os.environ.setdefault("CODEX_ALLOW_MISSING_HYDRA_EXTRA", "1")

hydra_module = types.ModuleType("hydra")


def _hydra_main(*_args: Any, **_kwargs: Any):
    def _decorator(func):
        return func

    return _decorator


hydra_module.main = _hydra_main
sys.modules.setdefault("hydra", hydra_module)


# ---------------------------------------------------------------------------
# Minimal fastapi stubs (we only need decorators and response containers).
# ---------------------------------------------------------------------------
fastapi_module = types.ModuleType("fastapi")


class _FakeFastAPI:
    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover - trivial
        self.routes: list[tuple[str, str]] = []

    def get(self, path: str):  # pragma: no cover - decorator passthrough
        def _decorator(func):
            self.routes.append(("GET", path))
            return func

        return _decorator

    def post(self, path: str):  # pragma: no cover - decorator passthrough
        def _decorator(func):
            self.routes.append(("POST", path))
            return func

        return _decorator


class _FakeRequest:  # pragma: no cover - helper placeholder
    async def json(self) -> dict[str, Any]:
        return {}


fastapi_module.FastAPI = _FakeFastAPI
fastapi_module.Request = _FakeRequest

responses_module = types.ModuleType("fastapi.responses")


class _JSONResponse(dict):
    def __init__(self, content: Any | None = None, status_code: int = 200) -> None:
        super().__init__(content or {})
        self.status_code = status_code


class _PlainTextResponse(str):
    def __new__(cls, content: str, status_code: int = 200):
        instance = str.__new__(cls, content)
        instance.status_code = status_code
        return instance


responses_module.JSONResponse = _JSONResponse
responses_module.PlainTextResponse = _PlainTextResponse

sys.modules.setdefault("fastapi", fastapi_module)
sys.modules.setdefault("fastapi.responses", responses_module)


from hhg_logistics.serve.app import (  # noqa: E402  (import after stubbing)
    GenConfig,
    LLMService,
    _freeze_override_value,
    _make_override_key,
    _TorchInferenceContext,
)


def test_freeze_override_value_handles_nested_iterables() -> None:
    nested = {
        "beta": [3, {"zeta": {2, 1}}],
        "alpha": ("x", b"bytes", None),
    }

    frozen = _freeze_override_value(nested)

    assert frozen == (
        ("alpha", ("x", "bytes", None)),
        ("beta", (3, (("zeta", (1, 2)),))),
    )


def test_make_override_key_is_order_invariant() -> None:
    overrides_a = {
        "temperature": 0.6,
        "generate": {"top_p": 0.9, "top_k": None},
        "tags": ["x", "y"],
    }
    overrides_b = {
        "tags": ["x", "y"],
        "generate": {"top_k": None, "top_p": 0.9},
        "temperature": 0.6,
    }

    assert _make_override_key(overrides_a) == _make_override_key(overrides_b)


def test_collect_generate_kwargs_filters_unknown_keys() -> None:
    service = types.SimpleNamespace(
        gen_cfg=GenConfig(
            max_new_tokens=10,
            do_sample=False,
            temperature=0.2,
            top_p=0.8,
            top_k=4,
        )
    )

    collected = LLMService._collect_generate_kwargs(
        service,
        {
            "max_new_tokens": 5,
            "temperature": None,
            "top_k": 0,
            "unexpected": "ignored",
        },
    )

    assert collected["max_new_tokens"] == 5
    assert collected["top_k"] == 0
    assert collected["temperature"] == 0.2
    assert "unexpected" not in collected


def test_predict_batch_groups_by_override_key() -> None:
    service = types.SimpleNamespace(batch_size=8, batch_timeout_s=0.02)

    def fake_generate(prompts: list[str], overrides: dict[str, Any]):
        label = overrides.get("tag", "default")
        return [f"{label}::{prompt}" for prompt in prompts]

    service._generate = fake_generate

    payloads = [
        {"prompts": ["alpha"], "overrides": {"tag": "A"}},
        {"prompts": ["beta1", "beta2"], "overrides": {"tag": "A"}},
        {"prompts": ["gamma"], "overrides": {"tag": "B"}},
        {"prompts": [], "overrides": {"tag": "empty"}},
    ]

    result = asyncio.run(LLMService._predict_batch.__wrapped__(service, payloads))

    assert result[0]["outputs"] == ["A::alpha"]
    assert result[1]["outputs"] == ["A::beta1", "A::beta2"]
    assert result[2]["outputs"] == ["B::gamma"]
    assert result[3]["outputs"] == []


def test_torch_inference_context_without_torch(monkeypatch: pytest.MonkeyPatch) -> None:
    original_import = builtins.__import__

    def fake_import(
        name: str, globals: Any = None, locals: Any = None, fromlist: Any = (), level: int = 0
    ):
        if name == "torch":
            raise ImportError("torch missing")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    ctx = _TorchInferenceContext()

    assert ctx._torch is None  # type: ignore[attr-defined]
    assert ctx._inference is None  # type: ignore[attr-defined]
    assert ctx._autocast is None  # type: ignore[attr-defined]

    with ctx:
        pass
