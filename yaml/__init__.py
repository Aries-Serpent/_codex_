"""Shim module that prefers the real PyYAML implementation when available."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import IO, Any

__all__: list[str]

_root = Path(__file__).resolve().parent.parent
_candidates = [
    _root
    / ".venv"
    / "lib"
    / f"python{sys.version_info.major}.{sys.version_info.minor}"
    / "site-packages",
    _root
    / "venv"
    / "lib"
    / f"python{sys.version_info.major}.{sys.version_info.minor}"
    / "site-packages",
]

for site in _candidates:
    init_path = site / "yaml" / "__init__.py"
    if init_path.exists():
        spec = importlib.util.spec_from_file_location("_codex_real_yaml", init_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules.setdefault("_codex_real_yaml", module)
            spec.loader.exec_module(module)  # type: ignore[call-arg]
            __path__ = [str(init_path.parent)]
            for name, value in module.__dict__.items():
                if name == "__all__":
                    __all__ = list(value)  # type: ignore[assignment]
                elif not name.startswith("__") or name in {"__version__", "__doc__"}:
                    globals()[name] = value
            if "__all__" not in globals():
                __all__ = [
                    "YAMLError",
                    "safe_load",
                    "safe_dump",
                    "dump",
                    "load",
                    "compose",
                    "SafeLoader",
                    "Loader",
                    "CSafeLoader",
                    "SafeDumper",
                    "Dumper",
                    "CSafeDumper",
                ]
            break
else:
    import json

    __all__ = [
        "YAMLError",
        "safe_load",
        "safe_dump",
        "dump",
        "load",
        "compose",
        "SafeLoader",
        "Loader",
        "CSafeLoader",
        "SafeDumper",
        "Dumper",
        "CSafeDumper",
    ]

    class YAMLError(Exception):
        """Minimal replacement when PyYAML is not installed."""

    def _coerce_text(data: str | bytes | IO[str] | None) -> str:
        if data is None:
            return ""
        if hasattr(data, "read"):
            return str(data.read())  # type: ignore[no-any-return]
        if isinstance(data, bytes):
            return data.decode("utf-8")
        return str(data)

    def safe_load(data: str | bytes | IO[str] | None) -> Any:
        text = _coerce_text(data)
        if not text.strip():
            return None
        try:
            return json.loads(text)
        except Exception:
            try:
                from codex_ml.safety.filters import _minimal_yaml_load  # type: ignore
            except Exception as exc:  # pragma: no cover - defensive fallback
                raise YAMLError(str(exc)) from exc
            try:
                return _minimal_yaml_load(text)
            except Exception as exc:  # pragma: no cover - defensive fallback
                raise YAMLError(str(exc)) from exc

    def safe_dump(
        data: Any, stream: IO[str] | None = None, *, default_flow_style: bool | None = None
    ) -> str:
        serialized = json.dumps(data, indent=2, default=str)
        if stream is not None:
            stream.write(serialized)
            return ""
        return serialized

    def dump(data: Any, stream: IO[str] | None = None, **kwargs: Any) -> str:
        return safe_dump(data, stream=stream, **kwargs)

    load = safe_load

    class SafeLoader:  # pragma: no cover - placeholder
        pass

    class SafeDumper:  # pragma: no cover - placeholder
        pass

    Loader = SafeLoader
    CSafeLoader = SafeLoader
    Dumper = SafeDumper
    CSafeDumper = SafeDumper

    def compose(stream, Loader=None):  # type: ignore[override]
        return safe_load(stream)

    safe_loader = SafeLoader
    safe_dumper = SafeDumper

__all__ = list(dict.fromkeys(__all__))
