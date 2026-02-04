"""
Tool Trace Module

This module provides functionality for tool trace.

Usage:
    from codex_harness.tool_trace import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence

_STATUS_PASS = {"pass", "passed", "ok", "success", "green", "approved", "true", "1"}
_STATUS_FAIL = {"fail", "failed", "block", "blocked", "reject", "false", "0", "red"}
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


def x__utc_now__mutmut_orig() -> str:
    return datetime.now(timezone.utc).isoformat()


def x__utc_now__mutmut_1() -> str:
    return datetime.now(None).isoformat()

x__utc_now__mutmut_mutants : ClassVar[MutantDict] = {
'x__utc_now__mutmut_1': x__utc_now__mutmut_1
}

def _utc_now(*args, **kwargs):
    result = _mutmut_trampoline(x__utc_now__mutmut_orig, x__utc_now__mutmut_mutants, args, kwargs)
    return result 

_utc_now.__signature__ = _mutmut_signature(x__utc_now__mutmut_orig)
x__utc_now__mutmut_orig.__name__ = 'x__utc_now'


def x__normalize_status__mutmut_orig(value: Any) -> bool | None:
    if value is None:
        return None
    lowered = str(value).lower()
    if lowered in _STATUS_PASS:
        return True
    if lowered in _STATUS_FAIL:
        return False
    return None


def x__normalize_status__mutmut_1(value: Any) -> bool | None:
    if value is not None:
        return None
    lowered = str(value).lower()
    if lowered in _STATUS_PASS:
        return True
    if lowered in _STATUS_FAIL:
        return False
    return None


def x__normalize_status__mutmut_2(value: Any) -> bool | None:
    if value is None:
        return None
    lowered = None
    if lowered in _STATUS_PASS:
        return True
    if lowered in _STATUS_FAIL:
        return False
    return None


def x__normalize_status__mutmut_3(value: Any) -> bool | None:
    if value is None:
        return None
    lowered = str(value).upper()
    if lowered in _STATUS_PASS:
        return True
    if lowered in _STATUS_FAIL:
        return False
    return None


def x__normalize_status__mutmut_4(value: Any) -> bool | None:
    if value is None:
        return None
    lowered = str(None).lower()
    if lowered in _STATUS_PASS:
        return True
    if lowered in _STATUS_FAIL:
        return False
    return None


def x__normalize_status__mutmut_5(value: Any) -> bool | None:
    if value is None:
        return None
    lowered = str(value).lower()
    if lowered not in _STATUS_PASS:
        return True
    if lowered in _STATUS_FAIL:
        return False
    return None


def x__normalize_status__mutmut_6(value: Any) -> bool | None:
    if value is None:
        return None
    lowered = str(value).lower()
    if lowered in _STATUS_PASS:
        return False
    if lowered in _STATUS_FAIL:
        return False
    return None


def x__normalize_status__mutmut_7(value: Any) -> bool | None:
    if value is None:
        return None
    lowered = str(value).lower()
    if lowered in _STATUS_PASS:
        return True
    if lowered not in _STATUS_FAIL:
        return False
    return None


def x__normalize_status__mutmut_8(value: Any) -> bool | None:
    if value is None:
        return None
    lowered = str(value).lower()
    if lowered in _STATUS_PASS:
        return True
    if lowered in _STATUS_FAIL:
        return True
    return None

x__normalize_status__mutmut_mutants : ClassVar[MutantDict] = {
'x__normalize_status__mutmut_1': x__normalize_status__mutmut_1, 
    'x__normalize_status__mutmut_2': x__normalize_status__mutmut_2, 
    'x__normalize_status__mutmut_3': x__normalize_status__mutmut_3, 
    'x__normalize_status__mutmut_4': x__normalize_status__mutmut_4, 
    'x__normalize_status__mutmut_5': x__normalize_status__mutmut_5, 
    'x__normalize_status__mutmut_6': x__normalize_status__mutmut_6, 
    'x__normalize_status__mutmut_7': x__normalize_status__mutmut_7, 
    'x__normalize_status__mutmut_8': x__normalize_status__mutmut_8
}

def _normalize_status(*args, **kwargs):
    result = _mutmut_trampoline(x__normalize_status__mutmut_orig, x__normalize_status__mutmut_mutants, args, kwargs)
    return result 

_normalize_status.__signature__ = _mutmut_signature(x__normalize_status__mutmut_orig)
x__normalize_status__mutmut_orig.__name__ = 'x__normalize_status'


@dataclass
class ToolInvocation:
    tool: str
    args: list[str]
    exit_code: int
    started_at: str
    finished_at: str
    stdout: str
    stderr: str
    ra_gate_expected: bool | None = None
    ra_gate_match: bool | None = None
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if self.metadata is None:
            payload.pop("metadata", None)
        return payload


class ToolTraceLogger:
    """Capture local tool invocations to `artifacts/tool_trace.ndjson`."""

    def xǁToolTraceLoggerǁ__init____mutmut_orig(self, output_path: Path | str = Path("artifacts/tool_trace.ndjson")) -> None:
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.ra_gate_results: dict[str, bool | None] = {}

    def xǁToolTraceLoggerǁ__init____mutmut_1(self, output_path: Path | str = Path("artifacts/tool_trace.ndjson")) -> None:
        self.output_path = None
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.ra_gate_results: dict[str, bool | None] = {}

    def xǁToolTraceLoggerǁ__init____mutmut_2(self, output_path: Path | str = Path("artifacts/tool_trace.ndjson")) -> None:
        self.output_path = Path(None)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.ra_gate_results: dict[str, bool | None] = {}

    def xǁToolTraceLoggerǁ__init____mutmut_3(self, output_path: Path | str = Path("artifacts/tool_trace.ndjson")) -> None:
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=None, exist_ok=True)
        self.ra_gate_results: dict[str, bool | None] = {}

    def xǁToolTraceLoggerǁ__init____mutmut_4(self, output_path: Path | str = Path("artifacts/tool_trace.ndjson")) -> None:
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=None)
        self.ra_gate_results: dict[str, bool | None] = {}

    def xǁToolTraceLoggerǁ__init____mutmut_5(self, output_path: Path | str = Path("artifacts/tool_trace.ndjson")) -> None:
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(exist_ok=True)
        self.ra_gate_results: dict[str, bool | None] = {}

    def xǁToolTraceLoggerǁ__init____mutmut_6(self, output_path: Path | str = Path("artifacts/tool_trace.ndjson")) -> None:
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, )
        self.ra_gate_results: dict[str, bool | None] = {}

    def xǁToolTraceLoggerǁ__init____mutmut_7(self, output_path: Path | str = Path("artifacts/tool_trace.ndjson")) -> None:
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=False, exist_ok=True)
        self.ra_gate_results: dict[str, bool | None] = {}

    def xǁToolTraceLoggerǁ__init____mutmut_8(self, output_path: Path | str = Path("artifacts/tool_trace.ndjson")) -> None:
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=False)
        self.ra_gate_results: dict[str, bool | None] = {}

    def xǁToolTraceLoggerǁ__init____mutmut_9(self, output_path: Path | str = Path("artifacts/tool_trace.ndjson")) -> None:
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.ra_gate_results: dict[str, bool | None] = None
    
    xǁToolTraceLoggerǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁToolTraceLoggerǁ__init____mutmut_1': xǁToolTraceLoggerǁ__init____mutmut_1, 
        'xǁToolTraceLoggerǁ__init____mutmut_2': xǁToolTraceLoggerǁ__init____mutmut_2, 
        'xǁToolTraceLoggerǁ__init____mutmut_3': xǁToolTraceLoggerǁ__init____mutmut_3, 
        'xǁToolTraceLoggerǁ__init____mutmut_4': xǁToolTraceLoggerǁ__init____mutmut_4, 
        'xǁToolTraceLoggerǁ__init____mutmut_5': xǁToolTraceLoggerǁ__init____mutmut_5, 
        'xǁToolTraceLoggerǁ__init____mutmut_6': xǁToolTraceLoggerǁ__init____mutmut_6, 
        'xǁToolTraceLoggerǁ__init____mutmut_7': xǁToolTraceLoggerǁ__init____mutmut_7, 
        'xǁToolTraceLoggerǁ__init____mutmut_8': xǁToolTraceLoggerǁ__init____mutmut_8, 
        'xǁToolTraceLoggerǁ__init____mutmut_9': xǁToolTraceLoggerǁ__init____mutmut_9
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁToolTraceLoggerǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁToolTraceLoggerǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁToolTraceLoggerǁ__init____mutmut_orig)
    xǁToolTraceLoggerǁ__init____mutmut_orig.__name__ = 'xǁToolTraceLoggerǁ__init__'

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_orig(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_1(self, path: Path | str) -> dict[str, bool | None]:
        p = None
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_2(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(None)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_3(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_4(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = None
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_5(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(None)
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_6(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding=None))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_7(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="XXutf-8XX"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_8(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="UTF-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_9(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = None
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_10(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) or "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_11(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "XXgatesXX" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_12(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "GATES" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_13(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" not in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_14(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get(None, []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_15(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", None):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_16(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get([]):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_17(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", ):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_18(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("XXgatesXX", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_19(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("GATES", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_20(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) and "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_21(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_22(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "XXtoolXX" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_23(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "TOOL" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_24(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_25(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    break
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_26(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = None
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_27(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["XXtoolXX"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_28(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["TOOL"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_29(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") and entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_30(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get(None) or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_31(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("XXstatusXX") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_32(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("STATUS") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_33(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get(None)
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_34(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("XXresultXX")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_35(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("RESULT")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_36(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = None
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_37(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError(None)
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_38(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("XXRA gate results must be a JSON object or contain a 'gates' listXX")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_39(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("ra gate results must be a json object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_40(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA GATE RESULTS MUST BE A JSON OBJECT OR CONTAIN A 'GATES' LIST")
        self.ra_gate_results = {tool: _normalize_status(status) for tool, status in mapping.items()}
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_41(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = None
        return self.ra_gate_results

    def xǁToolTraceLoggerǁload_ra_gate_results__mutmut_42(self, path: Path | str) -> dict[str, bool | None]:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        mapping: dict[str, Any] = {}
        if isinstance(data, dict) and "gates" in data:
            for entry in data.get("gates", []):
                if not isinstance(entry, dict) or "tool" not in entry:
                    continue
                mapping[entry["tool"]] = entry.get("status") or entry.get("result")
        elif isinstance(data, dict):
            mapping = data
        else:
            raise ValueError("RA gate results must be a JSON object or contain a 'gates' list")
        self.ra_gate_results = {tool: _normalize_status(None) for tool, status in mapping.items()}
        return self.ra_gate_results
    
    xǁToolTraceLoggerǁload_ra_gate_results__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_1': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_1, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_2': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_2, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_3': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_3, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_4': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_4, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_5': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_5, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_6': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_6, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_7': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_7, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_8': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_8, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_9': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_9, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_10': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_10, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_11': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_11, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_12': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_12, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_13': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_13, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_14': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_14, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_15': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_15, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_16': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_16, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_17': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_17, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_18': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_18, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_19': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_19, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_20': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_20, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_21': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_21, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_22': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_22, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_23': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_23, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_24': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_24, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_25': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_25, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_26': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_26, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_27': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_27, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_28': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_28, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_29': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_29, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_30': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_30, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_31': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_31, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_32': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_32, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_33': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_33, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_34': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_34, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_35': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_35, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_36': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_36, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_37': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_37, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_38': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_38, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_39': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_39, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_40': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_40, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_41': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_41, 
        'xǁToolTraceLoggerǁload_ra_gate_results__mutmut_42': xǁToolTraceLoggerǁload_ra_gate_results__mutmut_42
    }
    
    def load_ra_gate_results(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁToolTraceLoggerǁload_ra_gate_results__mutmut_orig"), object.__getattribute__(self, "xǁToolTraceLoggerǁload_ra_gate_results__mutmut_mutants"), args, kwargs, self)
        return result 
    
    load_ra_gate_results.__signature__ = _mutmut_signature(xǁToolTraceLoggerǁload_ra_gate_results__mutmut_orig)
    xǁToolTraceLoggerǁload_ra_gate_results__mutmut_orig.__name__ = 'xǁToolTraceLoggerǁload_ra_gate_results'

    def xǁToolTraceLoggerǁrecord_invocation__mutmut_orig(self, invocation: ToolInvocation) -> None:
        line = json.dumps(invocation.to_dict(), sort_keys=True)
        with self.output_path.open("a", encoding="utf-8") as handle:
            handle.write(line)
            handle.write("\n")

    def xǁToolTraceLoggerǁrecord_invocation__mutmut_1(self, invocation: ToolInvocation) -> None:
        line = None
        with self.output_path.open("a", encoding="utf-8") as handle:
            handle.write(line)
            handle.write("\n")

    def xǁToolTraceLoggerǁrecord_invocation__mutmut_2(self, invocation: ToolInvocation) -> None:
        line = json.dumps(None, sort_keys=True)
        with self.output_path.open("a", encoding="utf-8") as handle:
            handle.write(line)
            handle.write("\n")

    def xǁToolTraceLoggerǁrecord_invocation__mutmut_3(self, invocation: ToolInvocation) -> None:
        line = json.dumps(invocation.to_dict(), sort_keys=None)
        with self.output_path.open("a", encoding="utf-8") as handle:
            handle.write(line)
            handle.write("\n")

    def xǁToolTraceLoggerǁrecord_invocation__mutmut_4(self, invocation: ToolInvocation) -> None:
        line = json.dumps(sort_keys=True)
        with self.output_path.open("a", encoding="utf-8") as handle:
            handle.write(line)
            handle.write("\n")

    def xǁToolTraceLoggerǁrecord_invocation__mutmut_5(self, invocation: ToolInvocation) -> None:
        line = json.dumps(invocation.to_dict(), )
        with self.output_path.open("a", encoding="utf-8") as handle:
            handle.write(line)
            handle.write("\n")

    def xǁToolTraceLoggerǁrecord_invocation__mutmut_6(self, invocation: ToolInvocation) -> None:
        line = json.dumps(invocation.to_dict(), sort_keys=False)
        with self.output_path.open("a", encoding="utf-8") as handle:
            handle.write(line)
            handle.write("\n")

    def xǁToolTraceLoggerǁrecord_invocation__mutmut_7(self, invocation: ToolInvocation) -> None:
        line = json.dumps(invocation.to_dict(), sort_keys=True)
        with self.output_path.open(None, encoding="utf-8") as handle:
            handle.write(line)
            handle.write("\n")

    def xǁToolTraceLoggerǁrecord_invocation__mutmut_8(self, invocation: ToolInvocation) -> None:
        line = json.dumps(invocation.to_dict(), sort_keys=True)
        with self.output_path.open("a", encoding=None) as handle:
            handle.write(line)
            handle.write("\n")

    def xǁToolTraceLoggerǁrecord_invocation__mutmut_9(self, invocation: ToolInvocation) -> None:
        line = json.dumps(invocation.to_dict(), sort_keys=True)
        with self.output_path.open(encoding="utf-8") as handle:
            handle.write(line)
            handle.write("\n")

    def xǁToolTraceLoggerǁrecord_invocation__mutmut_10(self, invocation: ToolInvocation) -> None:
        line = json.dumps(invocation.to_dict(), sort_keys=True)
        with self.output_path.open("a", ) as handle:
            handle.write(line)
            handle.write("\n")

    def xǁToolTraceLoggerǁrecord_invocation__mutmut_11(self, invocation: ToolInvocation) -> None:
        line = json.dumps(invocation.to_dict(), sort_keys=True)
        with self.output_path.open("XXaXX", encoding="utf-8") as handle:
            handle.write(line)
            handle.write("\n")

    def xǁToolTraceLoggerǁrecord_invocation__mutmut_12(self, invocation: ToolInvocation) -> None:
        line = json.dumps(invocation.to_dict(), sort_keys=True)
        with self.output_path.open("A", encoding="utf-8") as handle:
            handle.write(line)
            handle.write("\n")

    def xǁToolTraceLoggerǁrecord_invocation__mutmut_13(self, invocation: ToolInvocation) -> None:
        line = json.dumps(invocation.to_dict(), sort_keys=True)
        with self.output_path.open("a", encoding="XXutf-8XX") as handle:
            handle.write(line)
            handle.write("\n")

    def xǁToolTraceLoggerǁrecord_invocation__mutmut_14(self, invocation: ToolInvocation) -> None:
        line = json.dumps(invocation.to_dict(), sort_keys=True)
        with self.output_path.open("a", encoding="UTF-8") as handle:
            handle.write(line)
            handle.write("\n")

    def xǁToolTraceLoggerǁrecord_invocation__mutmut_15(self, invocation: ToolInvocation) -> None:
        line = json.dumps(invocation.to_dict(), sort_keys=True)
        with self.output_path.open("a", encoding="utf-8") as handle:
            handle.write(None)
            handle.write("\n")

    def xǁToolTraceLoggerǁrecord_invocation__mutmut_16(self, invocation: ToolInvocation) -> None:
        line = json.dumps(invocation.to_dict(), sort_keys=True)
        with self.output_path.open("a", encoding="utf-8") as handle:
            handle.write(line)
            handle.write(None)

    def xǁToolTraceLoggerǁrecord_invocation__mutmut_17(self, invocation: ToolInvocation) -> None:
        line = json.dumps(invocation.to_dict(), sort_keys=True)
        with self.output_path.open("a", encoding="utf-8") as handle:
            handle.write(line)
            handle.write("XX\nXX")
    
    xǁToolTraceLoggerǁrecord_invocation__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁToolTraceLoggerǁrecord_invocation__mutmut_1': xǁToolTraceLoggerǁrecord_invocation__mutmut_1, 
        'xǁToolTraceLoggerǁrecord_invocation__mutmut_2': xǁToolTraceLoggerǁrecord_invocation__mutmut_2, 
        'xǁToolTraceLoggerǁrecord_invocation__mutmut_3': xǁToolTraceLoggerǁrecord_invocation__mutmut_3, 
        'xǁToolTraceLoggerǁrecord_invocation__mutmut_4': xǁToolTraceLoggerǁrecord_invocation__mutmut_4, 
        'xǁToolTraceLoggerǁrecord_invocation__mutmut_5': xǁToolTraceLoggerǁrecord_invocation__mutmut_5, 
        'xǁToolTraceLoggerǁrecord_invocation__mutmut_6': xǁToolTraceLoggerǁrecord_invocation__mutmut_6, 
        'xǁToolTraceLoggerǁrecord_invocation__mutmut_7': xǁToolTraceLoggerǁrecord_invocation__mutmut_7, 
        'xǁToolTraceLoggerǁrecord_invocation__mutmut_8': xǁToolTraceLoggerǁrecord_invocation__mutmut_8, 
        'xǁToolTraceLoggerǁrecord_invocation__mutmut_9': xǁToolTraceLoggerǁrecord_invocation__mutmut_9, 
        'xǁToolTraceLoggerǁrecord_invocation__mutmut_10': xǁToolTraceLoggerǁrecord_invocation__mutmut_10, 
        'xǁToolTraceLoggerǁrecord_invocation__mutmut_11': xǁToolTraceLoggerǁrecord_invocation__mutmut_11, 
        'xǁToolTraceLoggerǁrecord_invocation__mutmut_12': xǁToolTraceLoggerǁrecord_invocation__mutmut_12, 
        'xǁToolTraceLoggerǁrecord_invocation__mutmut_13': xǁToolTraceLoggerǁrecord_invocation__mutmut_13, 
        'xǁToolTraceLoggerǁrecord_invocation__mutmut_14': xǁToolTraceLoggerǁrecord_invocation__mutmut_14, 
        'xǁToolTraceLoggerǁrecord_invocation__mutmut_15': xǁToolTraceLoggerǁrecord_invocation__mutmut_15, 
        'xǁToolTraceLoggerǁrecord_invocation__mutmut_16': xǁToolTraceLoggerǁrecord_invocation__mutmut_16, 
        'xǁToolTraceLoggerǁrecord_invocation__mutmut_17': xǁToolTraceLoggerǁrecord_invocation__mutmut_17
    }
    
    def record_invocation(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁToolTraceLoggerǁrecord_invocation__mutmut_orig"), object.__getattribute__(self, "xǁToolTraceLoggerǁrecord_invocation__mutmut_mutants"), args, kwargs, self)
        return result 
    
    record_invocation.__signature__ = _mutmut_signature(xǁToolTraceLoggerǁrecord_invocation__mutmut_orig)
    xǁToolTraceLoggerǁrecord_invocation__mutmut_orig.__name__ = 'xǁToolTraceLoggerǁrecord_invocation'

    def xǁToolTraceLoggerǁrun_tool__mutmut_orig(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_1(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = False,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_2(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = None
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_3(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(None)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_4(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(None) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_5(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = None
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_6(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = None
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_7(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(None, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_8(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=None, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_9(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=None, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_10(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=None, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_11(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=None)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_12(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_13(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_14(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_15(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_16(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, )
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_17(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=False, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_18(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=False, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_19(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = None
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_20(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = None
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_21(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(None)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_22(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = ""
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_23(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_24(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = None
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_25(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode != 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_26(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 1) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_27(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode == 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_28(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 1)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_29(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = None
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_30(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=None,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_31(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=None,
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_32(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=None,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_33(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=None,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_34(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=None,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_35(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=None,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_36(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=None,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_37(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=None,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_38(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=None,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_39(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_40(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_41(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_42(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_43(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_44(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_45(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_46(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_47(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_48(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(None),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_49(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[2:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_50(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(None)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_51(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check or completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_52(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode == 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_53(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 1:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_54(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                None, argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_55(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, None, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_56(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=None, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_57(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, stderr=None
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_58(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                argv, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_59(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, output=completed.stdout, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_60(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, stderr=completed.stderr
            )
        return invocation

    def xǁToolTraceLoggerǁrun_tool__mutmut_61(
        self,
        tool: str,
        args: Sequence[str] | None = None,
        *,
        env: dict[str, str] | None = None,
        cwd: str | Path | None = None,
        check: bool = True,
    ) -> ToolInvocation:
        argv: list[str] = [tool]
        if args:
            argv.extend(str(a) for a in args)
        started_at = _utc_now()
        completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (completed.returncode == 0) if expected else (completed.returncode != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(argv[1:]),
            exit_code=completed.returncode,
            started_at=started_at,
            finished_at=finished_at,
            stdout=completed.stdout,
            stderr=completed.stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
        )
        self.record_invocation(invocation)
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode, argv, output=completed.stdout, )
        return invocation
    
    xǁToolTraceLoggerǁrun_tool__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁToolTraceLoggerǁrun_tool__mutmut_1': xǁToolTraceLoggerǁrun_tool__mutmut_1, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_2': xǁToolTraceLoggerǁrun_tool__mutmut_2, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_3': xǁToolTraceLoggerǁrun_tool__mutmut_3, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_4': xǁToolTraceLoggerǁrun_tool__mutmut_4, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_5': xǁToolTraceLoggerǁrun_tool__mutmut_5, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_6': xǁToolTraceLoggerǁrun_tool__mutmut_6, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_7': xǁToolTraceLoggerǁrun_tool__mutmut_7, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_8': xǁToolTraceLoggerǁrun_tool__mutmut_8, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_9': xǁToolTraceLoggerǁrun_tool__mutmut_9, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_10': xǁToolTraceLoggerǁrun_tool__mutmut_10, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_11': xǁToolTraceLoggerǁrun_tool__mutmut_11, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_12': xǁToolTraceLoggerǁrun_tool__mutmut_12, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_13': xǁToolTraceLoggerǁrun_tool__mutmut_13, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_14': xǁToolTraceLoggerǁrun_tool__mutmut_14, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_15': xǁToolTraceLoggerǁrun_tool__mutmut_15, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_16': xǁToolTraceLoggerǁrun_tool__mutmut_16, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_17': xǁToolTraceLoggerǁrun_tool__mutmut_17, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_18': xǁToolTraceLoggerǁrun_tool__mutmut_18, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_19': xǁToolTraceLoggerǁrun_tool__mutmut_19, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_20': xǁToolTraceLoggerǁrun_tool__mutmut_20, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_21': xǁToolTraceLoggerǁrun_tool__mutmut_21, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_22': xǁToolTraceLoggerǁrun_tool__mutmut_22, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_23': xǁToolTraceLoggerǁrun_tool__mutmut_23, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_24': xǁToolTraceLoggerǁrun_tool__mutmut_24, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_25': xǁToolTraceLoggerǁrun_tool__mutmut_25, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_26': xǁToolTraceLoggerǁrun_tool__mutmut_26, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_27': xǁToolTraceLoggerǁrun_tool__mutmut_27, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_28': xǁToolTraceLoggerǁrun_tool__mutmut_28, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_29': xǁToolTraceLoggerǁrun_tool__mutmut_29, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_30': xǁToolTraceLoggerǁrun_tool__mutmut_30, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_31': xǁToolTraceLoggerǁrun_tool__mutmut_31, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_32': xǁToolTraceLoggerǁrun_tool__mutmut_32, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_33': xǁToolTraceLoggerǁrun_tool__mutmut_33, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_34': xǁToolTraceLoggerǁrun_tool__mutmut_34, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_35': xǁToolTraceLoggerǁrun_tool__mutmut_35, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_36': xǁToolTraceLoggerǁrun_tool__mutmut_36, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_37': xǁToolTraceLoggerǁrun_tool__mutmut_37, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_38': xǁToolTraceLoggerǁrun_tool__mutmut_38, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_39': xǁToolTraceLoggerǁrun_tool__mutmut_39, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_40': xǁToolTraceLoggerǁrun_tool__mutmut_40, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_41': xǁToolTraceLoggerǁrun_tool__mutmut_41, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_42': xǁToolTraceLoggerǁrun_tool__mutmut_42, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_43': xǁToolTraceLoggerǁrun_tool__mutmut_43, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_44': xǁToolTraceLoggerǁrun_tool__mutmut_44, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_45': xǁToolTraceLoggerǁrun_tool__mutmut_45, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_46': xǁToolTraceLoggerǁrun_tool__mutmut_46, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_47': xǁToolTraceLoggerǁrun_tool__mutmut_47, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_48': xǁToolTraceLoggerǁrun_tool__mutmut_48, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_49': xǁToolTraceLoggerǁrun_tool__mutmut_49, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_50': xǁToolTraceLoggerǁrun_tool__mutmut_50, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_51': xǁToolTraceLoggerǁrun_tool__mutmut_51, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_52': xǁToolTraceLoggerǁrun_tool__mutmut_52, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_53': xǁToolTraceLoggerǁrun_tool__mutmut_53, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_54': xǁToolTraceLoggerǁrun_tool__mutmut_54, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_55': xǁToolTraceLoggerǁrun_tool__mutmut_55, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_56': xǁToolTraceLoggerǁrun_tool__mutmut_56, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_57': xǁToolTraceLoggerǁrun_tool__mutmut_57, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_58': xǁToolTraceLoggerǁrun_tool__mutmut_58, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_59': xǁToolTraceLoggerǁrun_tool__mutmut_59, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_60': xǁToolTraceLoggerǁrun_tool__mutmut_60, 
        'xǁToolTraceLoggerǁrun_tool__mutmut_61': xǁToolTraceLoggerǁrun_tool__mutmut_61
    }
    
    def run_tool(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁToolTraceLoggerǁrun_tool__mutmut_orig"), object.__getattribute__(self, "xǁToolTraceLoggerǁrun_tool__mutmut_mutants"), args, kwargs, self)
        return result 
    
    run_tool.__signature__ = _mutmut_signature(xǁToolTraceLoggerǁrun_tool__mutmut_orig)
    xǁToolTraceLoggerǁrun_tool__mutmut_orig.__name__ = 'xǁToolTraceLoggerǁrun_tool'

    def xǁToolTraceLoggerǁlog_manual__mutmut_orig(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(args or []),
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            stdout=stdout,
            stderr=stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_1(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "XXXX",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(args or []),
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            stdout=stdout,
            stderr=stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_2(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "XXXX",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(args or []),
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            stdout=stdout,
            stderr=stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_3(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = None
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(args or []),
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            stdout=stdout,
            stderr=stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_4(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = None
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(args or []),
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            stdout=stdout,
            stderr=stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_5(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = None
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(args or []),
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            stdout=stdout,
            stderr=stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_6(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(None)
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(args or []),
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            stdout=stdout,
            stderr=stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_7(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = ""
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(args or []),
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            stdout=stdout,
            stderr=stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_8(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(args or []),
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            stdout=stdout,
            stderr=stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_9(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = None
        invocation = ToolInvocation(
            tool=tool,
            args=list(args or []),
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            stdout=stdout,
            stderr=stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_10(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code != 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(args or []),
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            stdout=stdout,
            stderr=stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_11(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code == 1) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(args or []),
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            stdout=stdout,
            stderr=stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_12(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code == 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(args or []),
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            stdout=stdout,
            stderr=stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_13(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 1)
        invocation = ToolInvocation(
            tool=tool,
            args=list(args or []),
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            stdout=stdout,
            stderr=stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_14(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = None
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_15(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=None,
            args=list(args or []),
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            stdout=stdout,
            stderr=stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_16(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=None,
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            stdout=stdout,
            stderr=stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_17(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(args or []),
            exit_code=None,
            started_at=started_at,
            finished_at=finished_at,
            stdout=stdout,
            stderr=stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_18(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(args or []),
            exit_code=exit_code,
            started_at=None,
            finished_at=finished_at,
            stdout=stdout,
            stderr=stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_19(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(args or []),
            exit_code=exit_code,
            started_at=started_at,
            finished_at=None,
            stdout=stdout,
            stderr=stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_20(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(args or []),
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            stdout=None,
            stderr=stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_21(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(args or []),
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            stdout=stdout,
            stderr=None,
            ra_gate_expected=expected,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_22(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(args or []),
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            stdout=stdout,
            stderr=stderr,
            ra_gate_expected=None,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_23(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(args or []),
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            stdout=stdout,
            stderr=stderr,
            ra_gate_expected=expected,
            ra_gate_match=None,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_24(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(args or []),
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            stdout=stdout,
            stderr=stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
            metadata=None,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_25(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            args=list(args or []),
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            stdout=stdout,
            stderr=stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_26(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=tool,
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            stdout=stdout,
            stderr=stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_27(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(args or []),
            started_at=started_at,
            finished_at=finished_at,
            stdout=stdout,
            stderr=stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_28(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(args or []),
            exit_code=exit_code,
            finished_at=finished_at,
            stdout=stdout,
            stderr=stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_29(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(args or []),
            exit_code=exit_code,
            started_at=started_at,
            stdout=stdout,
            stderr=stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_30(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(args or []),
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            stderr=stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_31(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(args or []),
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            stdout=stdout,
            ra_gate_expected=expected,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_32(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(args or []),
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            stdout=stdout,
            stderr=stderr,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_33(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(args or []),
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            stdout=stdout,
            stderr=stderr,
            ra_gate_expected=expected,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_34(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(args or []),
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            stdout=stdout,
            stderr=stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
            )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_35(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(None),
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            stdout=stdout,
            stderr=stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_36(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(args and []),
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            stdout=stdout,
            stderr=stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(invocation)
        return invocation

    def xǁToolTraceLoggerǁlog_manual__mutmut_37(
        self,
        tool: str,
        args: Iterable[str] | None,
        *,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocation:
        started_at = _utc_now()
        finished_at = _utc_now()
        expected = self.ra_gate_results.get(tool)
        match = None
        if expected is not None:
            match = (exit_code == 0) if expected else (exit_code != 0)
        invocation = ToolInvocation(
            tool=tool,
            args=list(args or []),
            exit_code=exit_code,
            started_at=started_at,
            finished_at=finished_at,
            stdout=stdout,
            stderr=stderr,
            ra_gate_expected=expected,
            ra_gate_match=match,
            metadata=metadata,
        )
        self.record_invocation(None)
        return invocation
    
    xǁToolTraceLoggerǁlog_manual__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁToolTraceLoggerǁlog_manual__mutmut_1': xǁToolTraceLoggerǁlog_manual__mutmut_1, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_2': xǁToolTraceLoggerǁlog_manual__mutmut_2, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_3': xǁToolTraceLoggerǁlog_manual__mutmut_3, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_4': xǁToolTraceLoggerǁlog_manual__mutmut_4, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_5': xǁToolTraceLoggerǁlog_manual__mutmut_5, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_6': xǁToolTraceLoggerǁlog_manual__mutmut_6, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_7': xǁToolTraceLoggerǁlog_manual__mutmut_7, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_8': xǁToolTraceLoggerǁlog_manual__mutmut_8, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_9': xǁToolTraceLoggerǁlog_manual__mutmut_9, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_10': xǁToolTraceLoggerǁlog_manual__mutmut_10, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_11': xǁToolTraceLoggerǁlog_manual__mutmut_11, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_12': xǁToolTraceLoggerǁlog_manual__mutmut_12, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_13': xǁToolTraceLoggerǁlog_manual__mutmut_13, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_14': xǁToolTraceLoggerǁlog_manual__mutmut_14, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_15': xǁToolTraceLoggerǁlog_manual__mutmut_15, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_16': xǁToolTraceLoggerǁlog_manual__mutmut_16, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_17': xǁToolTraceLoggerǁlog_manual__mutmut_17, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_18': xǁToolTraceLoggerǁlog_manual__mutmut_18, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_19': xǁToolTraceLoggerǁlog_manual__mutmut_19, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_20': xǁToolTraceLoggerǁlog_manual__mutmut_20, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_21': xǁToolTraceLoggerǁlog_manual__mutmut_21, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_22': xǁToolTraceLoggerǁlog_manual__mutmut_22, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_23': xǁToolTraceLoggerǁlog_manual__mutmut_23, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_24': xǁToolTraceLoggerǁlog_manual__mutmut_24, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_25': xǁToolTraceLoggerǁlog_manual__mutmut_25, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_26': xǁToolTraceLoggerǁlog_manual__mutmut_26, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_27': xǁToolTraceLoggerǁlog_manual__mutmut_27, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_28': xǁToolTraceLoggerǁlog_manual__mutmut_28, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_29': xǁToolTraceLoggerǁlog_manual__mutmut_29, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_30': xǁToolTraceLoggerǁlog_manual__mutmut_30, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_31': xǁToolTraceLoggerǁlog_manual__mutmut_31, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_32': xǁToolTraceLoggerǁlog_manual__mutmut_32, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_33': xǁToolTraceLoggerǁlog_manual__mutmut_33, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_34': xǁToolTraceLoggerǁlog_manual__mutmut_34, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_35': xǁToolTraceLoggerǁlog_manual__mutmut_35, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_36': xǁToolTraceLoggerǁlog_manual__mutmut_36, 
        'xǁToolTraceLoggerǁlog_manual__mutmut_37': xǁToolTraceLoggerǁlog_manual__mutmut_37
    }
    
    def log_manual(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁToolTraceLoggerǁlog_manual__mutmut_orig"), object.__getattribute__(self, "xǁToolTraceLoggerǁlog_manual__mutmut_mutants"), args, kwargs, self)
        return result 
    
    log_manual.__signature__ = _mutmut_signature(xǁToolTraceLoggerǁlog_manual__mutmut_orig)
    xǁToolTraceLoggerǁlog_manual__mutmut_orig.__name__ = 'xǁToolTraceLoggerǁlog_manual'

    def xǁToolTraceLoggerǁread_invocations__mutmut_orig(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_1(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = None
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_2(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_3(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding=None).splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_4(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="XXutf-8XX").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_5(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="UTF-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_6(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_7(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                break
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_8(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = None
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_9(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(None)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_10(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                None
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_11(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=None,
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_12(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=None,
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_13(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=None,
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_14(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=None,
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_15(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=None,
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_16(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=None,
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_17(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=None,
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_18(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=None,
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_19(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=None,
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_20(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=None,
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_21(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_22(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_23(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_24(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_25(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_26(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_27(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_28(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_29(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_30(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_31(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get(None, ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_32(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", None),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_33(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get(""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_34(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_35(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("XXtoolXX", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_36(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("TOOL", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_37(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", "XXXX"),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_38(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get(None, []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_39(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", None),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_40(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get([]),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_41(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", ),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_42(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("XXargsXX", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_43(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("ARGS", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_44(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get(None, -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_45(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", None),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_46(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get(-1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_47(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", ),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_48(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("XXexit_codeXX", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_49(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("EXIT_CODE", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_50(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", +1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_51(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -2),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_52(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get(None, ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_53(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", None),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_54(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get(""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_55(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_56(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("XXstarted_atXX", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_57(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("STARTED_AT", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_58(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", "XXXX"),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_59(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get(None, ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_60(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", None),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_61(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get(""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_62(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_63(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("XXfinished_atXX", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_64(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("FINISHED_AT", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_65(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", "XXXX"),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_66(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get(None, ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_67(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", None),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_68(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get(""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_69(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_70(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("XXstdoutXX", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_71(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("STDOUT", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_72(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", "XXXX"),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_73(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get(None, ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_74(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", None),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_75(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get(""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_76(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_77(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("XXstderrXX", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_78(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("STDERR", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_79(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", "XXXX"),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_80(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get(None),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_81(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("XXra_gate_expectedXX"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_82(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("RA_GATE_EXPECTED"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_83(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get(None),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_84(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("XXra_gate_matchXX"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_85(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("RA_GATE_MATCH"),
                    metadata=data.get("metadata"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_86(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get(None),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_87(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("XXmetadataXX"),
                )
            )
        return invocations

    def xǁToolTraceLoggerǁread_invocations__mutmut_88(self) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        if not self.output_path.exists():
            return invocations
        for line in self.output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            invocations.append(
                ToolInvocation(
                    tool=data.get("tool", ""),
                    args=data.get("args", []),
                    exit_code=data.get("exit_code", -1),
                    started_at=data.get("started_at", ""),
                    finished_at=data.get("finished_at", ""),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    ra_gate_expected=data.get("ra_gate_expected"),
                    ra_gate_match=data.get("ra_gate_match"),
                    metadata=data.get("METADATA"),
                )
            )
        return invocations
    
    xǁToolTraceLoggerǁread_invocations__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁToolTraceLoggerǁread_invocations__mutmut_1': xǁToolTraceLoggerǁread_invocations__mutmut_1, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_2': xǁToolTraceLoggerǁread_invocations__mutmut_2, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_3': xǁToolTraceLoggerǁread_invocations__mutmut_3, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_4': xǁToolTraceLoggerǁread_invocations__mutmut_4, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_5': xǁToolTraceLoggerǁread_invocations__mutmut_5, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_6': xǁToolTraceLoggerǁread_invocations__mutmut_6, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_7': xǁToolTraceLoggerǁread_invocations__mutmut_7, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_8': xǁToolTraceLoggerǁread_invocations__mutmut_8, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_9': xǁToolTraceLoggerǁread_invocations__mutmut_9, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_10': xǁToolTraceLoggerǁread_invocations__mutmut_10, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_11': xǁToolTraceLoggerǁread_invocations__mutmut_11, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_12': xǁToolTraceLoggerǁread_invocations__mutmut_12, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_13': xǁToolTraceLoggerǁread_invocations__mutmut_13, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_14': xǁToolTraceLoggerǁread_invocations__mutmut_14, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_15': xǁToolTraceLoggerǁread_invocations__mutmut_15, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_16': xǁToolTraceLoggerǁread_invocations__mutmut_16, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_17': xǁToolTraceLoggerǁread_invocations__mutmut_17, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_18': xǁToolTraceLoggerǁread_invocations__mutmut_18, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_19': xǁToolTraceLoggerǁread_invocations__mutmut_19, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_20': xǁToolTraceLoggerǁread_invocations__mutmut_20, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_21': xǁToolTraceLoggerǁread_invocations__mutmut_21, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_22': xǁToolTraceLoggerǁread_invocations__mutmut_22, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_23': xǁToolTraceLoggerǁread_invocations__mutmut_23, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_24': xǁToolTraceLoggerǁread_invocations__mutmut_24, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_25': xǁToolTraceLoggerǁread_invocations__mutmut_25, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_26': xǁToolTraceLoggerǁread_invocations__mutmut_26, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_27': xǁToolTraceLoggerǁread_invocations__mutmut_27, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_28': xǁToolTraceLoggerǁread_invocations__mutmut_28, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_29': xǁToolTraceLoggerǁread_invocations__mutmut_29, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_30': xǁToolTraceLoggerǁread_invocations__mutmut_30, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_31': xǁToolTraceLoggerǁread_invocations__mutmut_31, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_32': xǁToolTraceLoggerǁread_invocations__mutmut_32, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_33': xǁToolTraceLoggerǁread_invocations__mutmut_33, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_34': xǁToolTraceLoggerǁread_invocations__mutmut_34, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_35': xǁToolTraceLoggerǁread_invocations__mutmut_35, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_36': xǁToolTraceLoggerǁread_invocations__mutmut_36, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_37': xǁToolTraceLoggerǁread_invocations__mutmut_37, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_38': xǁToolTraceLoggerǁread_invocations__mutmut_38, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_39': xǁToolTraceLoggerǁread_invocations__mutmut_39, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_40': xǁToolTraceLoggerǁread_invocations__mutmut_40, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_41': xǁToolTraceLoggerǁread_invocations__mutmut_41, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_42': xǁToolTraceLoggerǁread_invocations__mutmut_42, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_43': xǁToolTraceLoggerǁread_invocations__mutmut_43, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_44': xǁToolTraceLoggerǁread_invocations__mutmut_44, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_45': xǁToolTraceLoggerǁread_invocations__mutmut_45, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_46': xǁToolTraceLoggerǁread_invocations__mutmut_46, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_47': xǁToolTraceLoggerǁread_invocations__mutmut_47, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_48': xǁToolTraceLoggerǁread_invocations__mutmut_48, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_49': xǁToolTraceLoggerǁread_invocations__mutmut_49, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_50': xǁToolTraceLoggerǁread_invocations__mutmut_50, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_51': xǁToolTraceLoggerǁread_invocations__mutmut_51, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_52': xǁToolTraceLoggerǁread_invocations__mutmut_52, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_53': xǁToolTraceLoggerǁread_invocations__mutmut_53, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_54': xǁToolTraceLoggerǁread_invocations__mutmut_54, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_55': xǁToolTraceLoggerǁread_invocations__mutmut_55, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_56': xǁToolTraceLoggerǁread_invocations__mutmut_56, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_57': xǁToolTraceLoggerǁread_invocations__mutmut_57, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_58': xǁToolTraceLoggerǁread_invocations__mutmut_58, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_59': xǁToolTraceLoggerǁread_invocations__mutmut_59, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_60': xǁToolTraceLoggerǁread_invocations__mutmut_60, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_61': xǁToolTraceLoggerǁread_invocations__mutmut_61, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_62': xǁToolTraceLoggerǁread_invocations__mutmut_62, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_63': xǁToolTraceLoggerǁread_invocations__mutmut_63, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_64': xǁToolTraceLoggerǁread_invocations__mutmut_64, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_65': xǁToolTraceLoggerǁread_invocations__mutmut_65, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_66': xǁToolTraceLoggerǁread_invocations__mutmut_66, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_67': xǁToolTraceLoggerǁread_invocations__mutmut_67, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_68': xǁToolTraceLoggerǁread_invocations__mutmut_68, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_69': xǁToolTraceLoggerǁread_invocations__mutmut_69, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_70': xǁToolTraceLoggerǁread_invocations__mutmut_70, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_71': xǁToolTraceLoggerǁread_invocations__mutmut_71, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_72': xǁToolTraceLoggerǁread_invocations__mutmut_72, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_73': xǁToolTraceLoggerǁread_invocations__mutmut_73, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_74': xǁToolTraceLoggerǁread_invocations__mutmut_74, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_75': xǁToolTraceLoggerǁread_invocations__mutmut_75, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_76': xǁToolTraceLoggerǁread_invocations__mutmut_76, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_77': xǁToolTraceLoggerǁread_invocations__mutmut_77, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_78': xǁToolTraceLoggerǁread_invocations__mutmut_78, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_79': xǁToolTraceLoggerǁread_invocations__mutmut_79, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_80': xǁToolTraceLoggerǁread_invocations__mutmut_80, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_81': xǁToolTraceLoggerǁread_invocations__mutmut_81, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_82': xǁToolTraceLoggerǁread_invocations__mutmut_82, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_83': xǁToolTraceLoggerǁread_invocations__mutmut_83, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_84': xǁToolTraceLoggerǁread_invocations__mutmut_84, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_85': xǁToolTraceLoggerǁread_invocations__mutmut_85, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_86': xǁToolTraceLoggerǁread_invocations__mutmut_86, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_87': xǁToolTraceLoggerǁread_invocations__mutmut_87, 
        'xǁToolTraceLoggerǁread_invocations__mutmut_88': xǁToolTraceLoggerǁread_invocations__mutmut_88
    }
    
    def read_invocations(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁToolTraceLoggerǁread_invocations__mutmut_orig"), object.__getattribute__(self, "xǁToolTraceLoggerǁread_invocations__mutmut_mutants"), args, kwargs, self)
        return result 
    
    read_invocations.__signature__ = _mutmut_signature(xǁToolTraceLoggerǁread_invocations__mutmut_orig)
    xǁToolTraceLoggerǁread_invocations__mutmut_orig.__name__ = 'xǁToolTraceLoggerǁread_invocations'


__all__ = ["ToolInvocation", "ToolTraceLogger"]
