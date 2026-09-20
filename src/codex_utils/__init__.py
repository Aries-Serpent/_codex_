"""Native ``codex_utils`` package implementation.

The repository's historical root-level ``codex_utils`` package was retained only
as a temporary compatibility layer during the src-layout migration. The canonical
implementation now lives under ``src/codex_utils`` and must import via the local
package rather than the deleted repo-root copy.
"""

from __future__ import annotations

from importlib import import_module

__all__: list[str] = []

for _module_name in (
    "json_report",
    "logging_setup",
    "mlflow_offline",
    "ndjson",
    "regex_patterns",
    "repro",
    "tracking",
):
    try:
        _module = import_module(f"{__name__}.{_module_name}")
    except ModuleNotFoundError:
        continue

    for _name in getattr(_module, "__all__", []):
        if _name.startswith("_"):
            continue
        globals()[_name] = getattr(_module, _name)
        if _name not in __all__:
            __all__.append(_name)

    for _name in dir(_module):
        if _name.startswith("_") or _name in globals():
            continue
        globals()[_name] = getattr(_module, _name)
        if _name not in __all__:
            __all__.append(_name)
