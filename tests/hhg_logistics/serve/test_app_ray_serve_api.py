"""Ray Serve API compatibility for hhg_logistics.serve.app without a Ray install.

Ray lazy-loads ``ray.serve`` (attribute access on ``ray`` raises AttributeError)
and Ray 2.x removed ``route_prefix`` from ``serve.deployment`` along with
``Deployment.deploy``. The strict stubs below model those constraints.
"""

from __future__ import annotations

import functools
import importlib
import sys
import types
from typing import Any

import pytest
from omegaconf import OmegaConf

pytest.importorskip("fastapi")
pytest.importorskip("charset_normalizer")

_MODULE = "hhg_logistics.serve.app"


class _StubDeployment:
    def __init__(self, cls: type, calls: list[tuple[str, Any]], **options: Any) -> None:
        self.func_or_class = cls
        self._calls = calls
        self.options_kwargs = options

    def options(self, *, num_replicas: int | None = None) -> _StubDeployment:
        self._calls.append(("options", {"num_replicas": num_replicas}))
        return self

    def bind(self, *args: Any) -> tuple[str, _StubDeployment, tuple[Any, ...]]:
        return ("bound", self, args)


def _build_stub_ray(calls: list[tuple[str, Any]]) -> tuple[types.ModuleType, types.ModuleType]:
    ray = types.ModuleType("ray")
    ray.__path__ = []  # type: ignore[attr-defined]
    ray.init = lambda **kwargs: calls.append(("ray.init", kwargs))  # type: ignore[attr-defined]
    ray.shutdown = lambda: calls.append(("ray.shutdown", None))  # type: ignore[attr-defined]

    serve = types.ModuleType("ray.serve")

    def deployment(_cls: type | None = None, *, num_replicas: int = 1):  # no route_prefix
        def wrap(cls: type) -> _StubDeployment:
            return _StubDeployment(cls, calls, num_replicas=num_replicas)

        return wrap(_cls) if _cls is not None else wrap

    def ingress(app: Any):
        def wrap(cls: type) -> type:
            return type(f"Ingress{cls.__name__}", (cls,), {"_ingress_app": app})

        return wrap

    def batch(**_kwargs: Any):
        def wrap(fn):
            @functools.wraps(fn)
            async def wrapper(*args: Any, **kwargs: Any):
                return await fn(*args, **kwargs)

            return wrapper

        return wrap

    def start(*, proxy_location: str | None = None, http_options: dict[str, Any] | None = None):
        calls.append(
            ("serve.start", {"proxy_location": proxy_location, "http_options": http_options})
        )

    def run(target: Any, *, route_prefix: str | None = "/"):
        calls.append(("serve.run", {"target": target, "route_prefix": route_prefix}))

    serve.deployment = deployment  # type: ignore[attr-defined]
    serve.ingress = ingress  # type: ignore[attr-defined]
    serve.batch = batch  # type: ignore[attr-defined]
    serve.start = start  # type: ignore[attr-defined]
    serve.run = run  # type: ignore[attr-defined]
    serve.shutdown = lambda: calls.append(("serve.shutdown", None))  # type: ignore[attr-defined]
    return ray, serve


@pytest.fixture
def app_module(monkeypatch: pytest.MonkeyPatch):
    calls: list[tuple[str, Any]] = []
    ray, serve = _build_stub_ray(calls)
    monkeypatch.setitem(sys.modules, "ray", ray)
    monkeypatch.setitem(sys.modules, "ray.serve", serve)
    monkeypatch.delitem(sys.modules, _MODULE, raising=False)
    try:
        module = importlib.import_module(_MODULE)
    except ImportError as exc:  # optional ML dependencies of the app module
        pytest.skip(f"hhg_logistics.serve.app dependencies unavailable: {exc}")
    yield module, calls
    sys.modules.pop(_MODULE, None)


def test_import_uses_explicit_serve_import_and_plain_service_class(app_module) -> None:
    module, _calls = app_module

    assert isinstance(module.LLMService, type)
    assert hasattr(module.LLMService._predict_batch, "__wrapped__")
    deployment = module.LLMServiceDeployment
    assert isinstance(deployment, _StubDeployment)
    assert issubclass(deployment.func_or_class, module.LLMService)
    assert deployment.func_or_class._ingress_app is module.api


def test_start_serve_passes_route_prefix_to_serve_run(app_module, monkeypatch) -> None:
    module, calls = app_module
    monkeypatch.setattr(module.time, "sleep", lambda _s: (_ for _ in ()).throw(KeyboardInterrupt))
    cfg = OmegaConf.create(
        {"serve": {"host": "127.0.0.1", "port": 8001, "route_prefix": "/llm", "num_replicas": 2}}
    )

    module._start_serve(cfg)

    names = [name for name, _ in calls]
    assert names == [
        "ray.init",
        "serve.start",
        "options",
        "serve.run",
        "serve.shutdown",
        "ray.shutdown",
    ]
    start = dict(calls)["serve.start"]
    assert start == {
        "proxy_location": "HeadOnly",
        "http_options": {"host": "127.0.0.1", "port": 8001},
    }
    assert dict(calls)["options"] == {"num_replicas": 2}
    run = dict(calls)["serve.run"]
    assert run["route_prefix"] == "/llm"
    kind, deployment, args = run["target"]
    assert kind == "bound" and deployment is module.LLMServiceDeployment
    assert args == (cfg,)
