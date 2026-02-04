"""Structured logging helpers used by archive commands."""

from __future__ import annotations

import json
import logging
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, UTC
from typing import Any

from .config import LoggingConfig, PerformanceConfig
from .perf import TimingMetrics
from .util import append_evidence, redact_text_credentials

ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
_STANDARD_FIELDS = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
}
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


@dataclass(slots=True)
class StructuredLogRecord:
    """Structured representation of a log record."""

    level: str
    message: str
    timestamp: str
    component: str
    extra: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "level": self.level,
            "message": self.message,
            "timestamp": self.timestamp,
            "component": self.component,
        }
        payload.update(self.extra)
        return payload

    def to_json(self) -> str:
        payload = {
            "level": self.level,
            "message": self.message,
            "timestamp": self.timestamp,
            "component": self.component,
            "extra": self.extra,
        }
        return json.dumps(payload, sort_keys=True)

    def to_text(self) -> str:
        extras = " ".join(f"{key}={value}" for key, value in sorted(self.extra.items()))
        if extras:
            return f"[{self.level}] {self.message} -- {extras}"
        return f"[{self.level}] {self.message}"


class StructuredFormatter(logging.Formatter):
    """Formatter that produces JSON or text payloads."""

    def xǁStructuredFormatterǁ__init____mutmut_orig(self, *, fmt: str = "json", component: str = "archive") -> None:
        super().__init__()
        self.format_mode = fmt
        self.component = component

    def xǁStructuredFormatterǁ__init____mutmut_1(self, *, fmt: str = "XXjsonXX", component: str = "archive") -> None:
        super().__init__()
        self.format_mode = fmt
        self.component = component

    def xǁStructuredFormatterǁ__init____mutmut_2(self, *, fmt: str = "JSON", component: str = "archive") -> None:
        super().__init__()
        self.format_mode = fmt
        self.component = component

    def xǁStructuredFormatterǁ__init____mutmut_3(self, *, fmt: str = "json", component: str = "XXarchiveXX") -> None:
        super().__init__()
        self.format_mode = fmt
        self.component = component

    def xǁStructuredFormatterǁ__init____mutmut_4(self, *, fmt: str = "json", component: str = "ARCHIVE") -> None:
        super().__init__()
        self.format_mode = fmt
        self.component = component

    def xǁStructuredFormatterǁ__init____mutmut_5(self, *, fmt: str = "json", component: str = "archive") -> None:
        super().__init__()
        self.format_mode = None
        self.component = component

    def xǁStructuredFormatterǁ__init____mutmut_6(self, *, fmt: str = "json", component: str = "archive") -> None:
        super().__init__()
        self.format_mode = fmt
        self.component = None
    
    xǁStructuredFormatterǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStructuredFormatterǁ__init____mutmut_1': xǁStructuredFormatterǁ__init____mutmut_1, 
        'xǁStructuredFormatterǁ__init____mutmut_2': xǁStructuredFormatterǁ__init____mutmut_2, 
        'xǁStructuredFormatterǁ__init____mutmut_3': xǁStructuredFormatterǁ__init____mutmut_3, 
        'xǁStructuredFormatterǁ__init____mutmut_4': xǁStructuredFormatterǁ__init____mutmut_4, 
        'xǁStructuredFormatterǁ__init____mutmut_5': xǁStructuredFormatterǁ__init____mutmut_5, 
        'xǁStructuredFormatterǁ__init____mutmut_6': xǁStructuredFormatterǁ__init____mutmut_6
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStructuredFormatterǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁStructuredFormatterǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁStructuredFormatterǁ__init____mutmut_orig)
    xǁStructuredFormatterǁ__init____mutmut_orig.__name__ = 'xǁStructuredFormatterǁ__init__'

    def xǁStructuredFormatterǁformat__mutmut_orig(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(record.created).strftime(ISO_FORMAT)
        extra_fields = {k: getattr(record, k) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = dict(extra_fields)
        extra_payload = flattened_extra.pop("extra_fields", None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            level=record.levelname,
            message=message,
            timestamp=timestamp,
            component=self.component,
            extra=flattened_extra,
        )
        if self.format_mode == "json":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_1(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = None
        timestamp = datetime.utcfromtimestamp(record.created).strftime(ISO_FORMAT)
        extra_fields = {k: getattr(record, k) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = dict(extra_fields)
        extra_payload = flattened_extra.pop("extra_fields", None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            level=record.levelname,
            message=message,
            timestamp=timestamp,
            component=self.component,
            extra=flattened_extra,
        )
        if self.format_mode == "json":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_2(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = None
        extra_fields = {k: getattr(record, k) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = dict(extra_fields)
        extra_payload = flattened_extra.pop("extra_fields", None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            level=record.levelname,
            message=message,
            timestamp=timestamp,
            component=self.component,
            extra=flattened_extra,
        )
        if self.format_mode == "json":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_3(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(record.created).strftime(None)
        extra_fields = {k: getattr(record, k) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = dict(extra_fields)
        extra_payload = flattened_extra.pop("extra_fields", None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            level=record.levelname,
            message=message,
            timestamp=timestamp,
            component=self.component,
            extra=flattened_extra,
        )
        if self.format_mode == "json":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_4(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(None).strftime(ISO_FORMAT)
        extra_fields = {k: getattr(record, k) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = dict(extra_fields)
        extra_payload = flattened_extra.pop("extra_fields", None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            level=record.levelname,
            message=message,
            timestamp=timestamp,
            component=self.component,
            extra=flattened_extra,
        )
        if self.format_mode == "json":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_5(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(record.created).strftime(ISO_FORMAT)
        extra_fields = None
        flattened_extra = dict(extra_fields)
        extra_payload = flattened_extra.pop("extra_fields", None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            level=record.levelname,
            message=message,
            timestamp=timestamp,
            component=self.component,
            extra=flattened_extra,
        )
        if self.format_mode == "json":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_6(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(record.created).strftime(ISO_FORMAT)
        extra_fields = {k: getattr(None, k) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = dict(extra_fields)
        extra_payload = flattened_extra.pop("extra_fields", None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            level=record.levelname,
            message=message,
            timestamp=timestamp,
            component=self.component,
            extra=flattened_extra,
        )
        if self.format_mode == "json":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_7(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(record.created).strftime(ISO_FORMAT)
        extra_fields = {k: getattr(record, None) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = dict(extra_fields)
        extra_payload = flattened_extra.pop("extra_fields", None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            level=record.levelname,
            message=message,
            timestamp=timestamp,
            component=self.component,
            extra=flattened_extra,
        )
        if self.format_mode == "json":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_8(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(record.created).strftime(ISO_FORMAT)
        extra_fields = {k: getattr(k) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = dict(extra_fields)
        extra_payload = flattened_extra.pop("extra_fields", None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            level=record.levelname,
            message=message,
            timestamp=timestamp,
            component=self.component,
            extra=flattened_extra,
        )
        if self.format_mode == "json":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_9(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(record.created).strftime(ISO_FORMAT)
        extra_fields = {k: getattr(record, ) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = dict(extra_fields)
        extra_payload = flattened_extra.pop("extra_fields", None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            level=record.levelname,
            message=message,
            timestamp=timestamp,
            component=self.component,
            extra=flattened_extra,
        )
        if self.format_mode == "json":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_10(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(record.created).strftime(ISO_FORMAT)
        extra_fields = {k: getattr(record, k) for k in record.__dict__ if k in _STANDARD_FIELDS}
        flattened_extra = dict(extra_fields)
        extra_payload = flattened_extra.pop("extra_fields", None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            level=record.levelname,
            message=message,
            timestamp=timestamp,
            component=self.component,
            extra=flattened_extra,
        )
        if self.format_mode == "json":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_11(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(record.created).strftime(ISO_FORMAT)
        extra_fields = {k: getattr(record, k) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = None
        extra_payload = flattened_extra.pop("extra_fields", None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            level=record.levelname,
            message=message,
            timestamp=timestamp,
            component=self.component,
            extra=flattened_extra,
        )
        if self.format_mode == "json":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_12(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(record.created).strftime(ISO_FORMAT)
        extra_fields = {k: getattr(record, k) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = dict(None)
        extra_payload = flattened_extra.pop("extra_fields", None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            level=record.levelname,
            message=message,
            timestamp=timestamp,
            component=self.component,
            extra=flattened_extra,
        )
        if self.format_mode == "json":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_13(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(record.created).strftime(ISO_FORMAT)
        extra_fields = {k: getattr(record, k) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = dict(extra_fields)
        extra_payload = None
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            level=record.levelname,
            message=message,
            timestamp=timestamp,
            component=self.component,
            extra=flattened_extra,
        )
        if self.format_mode == "json":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_14(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(record.created).strftime(ISO_FORMAT)
        extra_fields = {k: getattr(record, k) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = dict(extra_fields)
        extra_payload = flattened_extra.pop(None, None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            level=record.levelname,
            message=message,
            timestamp=timestamp,
            component=self.component,
            extra=flattened_extra,
        )
        if self.format_mode == "json":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_15(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(record.created).strftime(ISO_FORMAT)
        extra_fields = {k: getattr(record, k) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = dict(extra_fields)
        extra_payload = flattened_extra.pop(None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            level=record.levelname,
            message=message,
            timestamp=timestamp,
            component=self.component,
            extra=flattened_extra,
        )
        if self.format_mode == "json":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_16(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(record.created).strftime(ISO_FORMAT)
        extra_fields = {k: getattr(record, k) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = dict(extra_fields)
        extra_payload = flattened_extra.pop("extra_fields", )
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            level=record.levelname,
            message=message,
            timestamp=timestamp,
            component=self.component,
            extra=flattened_extra,
        )
        if self.format_mode == "json":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_17(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(record.created).strftime(ISO_FORMAT)
        extra_fields = {k: getattr(record, k) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = dict(extra_fields)
        extra_payload = flattened_extra.pop("XXextra_fieldsXX", None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            level=record.levelname,
            message=message,
            timestamp=timestamp,
            component=self.component,
            extra=flattened_extra,
        )
        if self.format_mode == "json":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_18(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(record.created).strftime(ISO_FORMAT)
        extra_fields = {k: getattr(record, k) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = dict(extra_fields)
        extra_payload = flattened_extra.pop("EXTRA_FIELDS", None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            level=record.levelname,
            message=message,
            timestamp=timestamp,
            component=self.component,
            extra=flattened_extra,
        )
        if self.format_mode == "json":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_19(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(record.created).strftime(ISO_FORMAT)
        extra_fields = {k: getattr(record, k) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = dict(extra_fields)
        extra_payload = flattened_extra.pop("extra_fields", None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(None)

        payload = StructuredLogRecord(
            level=record.levelname,
            message=message,
            timestamp=timestamp,
            component=self.component,
            extra=flattened_extra,
        )
        if self.format_mode == "json":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_20(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(record.created).strftime(ISO_FORMAT)
        extra_fields = {k: getattr(record, k) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = dict(extra_fields)
        extra_payload = flattened_extra.pop("extra_fields", None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = None
        if self.format_mode == "json":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_21(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(record.created).strftime(ISO_FORMAT)
        extra_fields = {k: getattr(record, k) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = dict(extra_fields)
        extra_payload = flattened_extra.pop("extra_fields", None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            level=None,
            message=message,
            timestamp=timestamp,
            component=self.component,
            extra=flattened_extra,
        )
        if self.format_mode == "json":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_22(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(record.created).strftime(ISO_FORMAT)
        extra_fields = {k: getattr(record, k) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = dict(extra_fields)
        extra_payload = flattened_extra.pop("extra_fields", None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            level=record.levelname,
            message=None,
            timestamp=timestamp,
            component=self.component,
            extra=flattened_extra,
        )
        if self.format_mode == "json":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_23(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(record.created).strftime(ISO_FORMAT)
        extra_fields = {k: getattr(record, k) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = dict(extra_fields)
        extra_payload = flattened_extra.pop("extra_fields", None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            level=record.levelname,
            message=message,
            timestamp=None,
            component=self.component,
            extra=flattened_extra,
        )
        if self.format_mode == "json":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_24(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(record.created).strftime(ISO_FORMAT)
        extra_fields = {k: getattr(record, k) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = dict(extra_fields)
        extra_payload = flattened_extra.pop("extra_fields", None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            level=record.levelname,
            message=message,
            timestamp=timestamp,
            component=None,
            extra=flattened_extra,
        )
        if self.format_mode == "json":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_25(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(record.created).strftime(ISO_FORMAT)
        extra_fields = {k: getattr(record, k) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = dict(extra_fields)
        extra_payload = flattened_extra.pop("extra_fields", None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            level=record.levelname,
            message=message,
            timestamp=timestamp,
            component=self.component,
            extra=None,
        )
        if self.format_mode == "json":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_26(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(record.created).strftime(ISO_FORMAT)
        extra_fields = {k: getattr(record, k) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = dict(extra_fields)
        extra_payload = flattened_extra.pop("extra_fields", None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            message=message,
            timestamp=timestamp,
            component=self.component,
            extra=flattened_extra,
        )
        if self.format_mode == "json":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_27(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(record.created).strftime(ISO_FORMAT)
        extra_fields = {k: getattr(record, k) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = dict(extra_fields)
        extra_payload = flattened_extra.pop("extra_fields", None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            level=record.levelname,
            timestamp=timestamp,
            component=self.component,
            extra=flattened_extra,
        )
        if self.format_mode == "json":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_28(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(record.created).strftime(ISO_FORMAT)
        extra_fields = {k: getattr(record, k) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = dict(extra_fields)
        extra_payload = flattened_extra.pop("extra_fields", None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            level=record.levelname,
            message=message,
            component=self.component,
            extra=flattened_extra,
        )
        if self.format_mode == "json":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_29(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(record.created).strftime(ISO_FORMAT)
        extra_fields = {k: getattr(record, k) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = dict(extra_fields)
        extra_payload = flattened_extra.pop("extra_fields", None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            level=record.levelname,
            message=message,
            timestamp=timestamp,
            extra=flattened_extra,
        )
        if self.format_mode == "json":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_30(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(record.created).strftime(ISO_FORMAT)
        extra_fields = {k: getattr(record, k) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = dict(extra_fields)
        extra_payload = flattened_extra.pop("extra_fields", None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            level=record.levelname,
            message=message,
            timestamp=timestamp,
            component=self.component,
            )
        if self.format_mode == "json":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_31(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(record.created).strftime(ISO_FORMAT)
        extra_fields = {k: getattr(record, k) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = dict(extra_fields)
        extra_payload = flattened_extra.pop("extra_fields", None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            level=record.levelname,
            message=message,
            timestamp=timestamp,
            component=self.component,
            extra=flattened_extra,
        )
        if self.format_mode != "json":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_32(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(record.created).strftime(ISO_FORMAT)
        extra_fields = {k: getattr(record, k) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = dict(extra_fields)
        extra_payload = flattened_extra.pop("extra_fields", None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            level=record.levelname,
            message=message,
            timestamp=timestamp,
            component=self.component,
            extra=flattened_extra,
        )
        if self.format_mode == "XXjsonXX":
            return payload.to_json()
        return payload.to_text()

    def xǁStructuredFormatterǁformat__mutmut_33(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        message = record.getMessage()
        timestamp = datetime.utcfromtimestamp(record.created).strftime(ISO_FORMAT)
        extra_fields = {k: getattr(record, k) for k in record.__dict__ if k not in _STANDARD_FIELDS}
        flattened_extra = dict(extra_fields)
        extra_payload = flattened_extra.pop("extra_fields", None)
        if isinstance(extra_payload, dict):
            flattened_extra.update(extra_payload)

        payload = StructuredLogRecord(
            level=record.levelname,
            message=message,
            timestamp=timestamp,
            component=self.component,
            extra=flattened_extra,
        )
        if self.format_mode == "JSON":
            return payload.to_json()
        return payload.to_text()
    
    xǁStructuredFormatterǁformat__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStructuredFormatterǁformat__mutmut_1': xǁStructuredFormatterǁformat__mutmut_1, 
        'xǁStructuredFormatterǁformat__mutmut_2': xǁStructuredFormatterǁformat__mutmut_2, 
        'xǁStructuredFormatterǁformat__mutmut_3': xǁStructuredFormatterǁformat__mutmut_3, 
        'xǁStructuredFormatterǁformat__mutmut_4': xǁStructuredFormatterǁformat__mutmut_4, 
        'xǁStructuredFormatterǁformat__mutmut_5': xǁStructuredFormatterǁformat__mutmut_5, 
        'xǁStructuredFormatterǁformat__mutmut_6': xǁStructuredFormatterǁformat__mutmut_6, 
        'xǁStructuredFormatterǁformat__mutmut_7': xǁStructuredFormatterǁformat__mutmut_7, 
        'xǁStructuredFormatterǁformat__mutmut_8': xǁStructuredFormatterǁformat__mutmut_8, 
        'xǁStructuredFormatterǁformat__mutmut_9': xǁStructuredFormatterǁformat__mutmut_9, 
        'xǁStructuredFormatterǁformat__mutmut_10': xǁStructuredFormatterǁformat__mutmut_10, 
        'xǁStructuredFormatterǁformat__mutmut_11': xǁStructuredFormatterǁformat__mutmut_11, 
        'xǁStructuredFormatterǁformat__mutmut_12': xǁStructuredFormatterǁformat__mutmut_12, 
        'xǁStructuredFormatterǁformat__mutmut_13': xǁStructuredFormatterǁformat__mutmut_13, 
        'xǁStructuredFormatterǁformat__mutmut_14': xǁStructuredFormatterǁformat__mutmut_14, 
        'xǁStructuredFormatterǁformat__mutmut_15': xǁStructuredFormatterǁformat__mutmut_15, 
        'xǁStructuredFormatterǁformat__mutmut_16': xǁStructuredFormatterǁformat__mutmut_16, 
        'xǁStructuredFormatterǁformat__mutmut_17': xǁStructuredFormatterǁformat__mutmut_17, 
        'xǁStructuredFormatterǁformat__mutmut_18': xǁStructuredFormatterǁformat__mutmut_18, 
        'xǁStructuredFormatterǁformat__mutmut_19': xǁStructuredFormatterǁformat__mutmut_19, 
        'xǁStructuredFormatterǁformat__mutmut_20': xǁStructuredFormatterǁformat__mutmut_20, 
        'xǁStructuredFormatterǁformat__mutmut_21': xǁStructuredFormatterǁformat__mutmut_21, 
        'xǁStructuredFormatterǁformat__mutmut_22': xǁStructuredFormatterǁformat__mutmut_22, 
        'xǁStructuredFormatterǁformat__mutmut_23': xǁStructuredFormatterǁformat__mutmut_23, 
        'xǁStructuredFormatterǁformat__mutmut_24': xǁStructuredFormatterǁformat__mutmut_24, 
        'xǁStructuredFormatterǁformat__mutmut_25': xǁStructuredFormatterǁformat__mutmut_25, 
        'xǁStructuredFormatterǁformat__mutmut_26': xǁStructuredFormatterǁformat__mutmut_26, 
        'xǁStructuredFormatterǁformat__mutmut_27': xǁStructuredFormatterǁformat__mutmut_27, 
        'xǁStructuredFormatterǁformat__mutmut_28': xǁStructuredFormatterǁformat__mutmut_28, 
        'xǁStructuredFormatterǁformat__mutmut_29': xǁStructuredFormatterǁformat__mutmut_29, 
        'xǁStructuredFormatterǁformat__mutmut_30': xǁStructuredFormatterǁformat__mutmut_30, 
        'xǁStructuredFormatterǁformat__mutmut_31': xǁStructuredFormatterǁformat__mutmut_31, 
        'xǁStructuredFormatterǁformat__mutmut_32': xǁStructuredFormatterǁformat__mutmut_32, 
        'xǁStructuredFormatterǁformat__mutmut_33': xǁStructuredFormatterǁformat__mutmut_33
    }
    
    def format(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStructuredFormatterǁformat__mutmut_orig"), object.__getattribute__(self, "xǁStructuredFormatterǁformat__mutmut_mutants"), args, kwargs, self)
        return result 
    
    format.__signature__ = _mutmut_signature(xǁStructuredFormatterǁformat__mutmut_orig)
    xǁStructuredFormatterǁformat__mutmut_orig.__name__ = 'xǁStructuredFormatterǁformat'


def x_setup_logging__mutmut_orig(
    config: LoggingConfig,
    *,
    logger_name: str = "codex.archive",
    stream: Any | None = None,
) -> logging.Logger:
    """Initialise a structured logger according to *config*."""

    logger = logging.getLogger(logger_name)
    level = getattr(logging, config.level.upper(), logging.INFO)
    logger.setLevel(level)
    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(StructuredFormatter(fmt=config.format, component=logger_name))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def x_setup_logging__mutmut_1(
    config: LoggingConfig,
    *,
    logger_name: str = "XXcodex.archiveXX",
    stream: Any | None = None,
) -> logging.Logger:
    """Initialise a structured logger according to *config*."""

    logger = logging.getLogger(logger_name)
    level = getattr(logging, config.level.upper(), logging.INFO)
    logger.setLevel(level)
    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(StructuredFormatter(fmt=config.format, component=logger_name))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def x_setup_logging__mutmut_2(
    config: LoggingConfig,
    *,
    logger_name: str = "CODEX.ARCHIVE",
    stream: Any | None = None,
) -> logging.Logger:
    """Initialise a structured logger according to *config*."""

    logger = logging.getLogger(logger_name)
    level = getattr(logging, config.level.upper(), logging.INFO)
    logger.setLevel(level)
    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(StructuredFormatter(fmt=config.format, component=logger_name))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def x_setup_logging__mutmut_3(
    config: LoggingConfig,
    *,
    logger_name: str = "codex.archive",
    stream: Any | None = None,
) -> logging.Logger:
    """Initialise a structured logger according to *config*."""

    logger = None
    level = getattr(logging, config.level.upper(), logging.INFO)
    logger.setLevel(level)
    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(StructuredFormatter(fmt=config.format, component=logger_name))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def x_setup_logging__mutmut_4(
    config: LoggingConfig,
    *,
    logger_name: str = "codex.archive",
    stream: Any | None = None,
) -> logging.Logger:
    """Initialise a structured logger according to *config*."""

    logger = logging.getLogger(None)
    level = getattr(logging, config.level.upper(), logging.INFO)
    logger.setLevel(level)
    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(StructuredFormatter(fmt=config.format, component=logger_name))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def x_setup_logging__mutmut_5(
    config: LoggingConfig,
    *,
    logger_name: str = "codex.archive",
    stream: Any | None = None,
) -> logging.Logger:
    """Initialise a structured logger according to *config*."""

    logger = logging.getLogger(logger_name)
    level = None
    logger.setLevel(level)
    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(StructuredFormatter(fmt=config.format, component=logger_name))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def x_setup_logging__mutmut_6(
    config: LoggingConfig,
    *,
    logger_name: str = "codex.archive",
    stream: Any | None = None,
) -> logging.Logger:
    """Initialise a structured logger according to *config*."""

    logger = logging.getLogger(logger_name)
    level = getattr(None, config.level.upper(), logging.INFO)
    logger.setLevel(level)
    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(StructuredFormatter(fmt=config.format, component=logger_name))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def x_setup_logging__mutmut_7(
    config: LoggingConfig,
    *,
    logger_name: str = "codex.archive",
    stream: Any | None = None,
) -> logging.Logger:
    """Initialise a structured logger according to *config*."""

    logger = logging.getLogger(logger_name)
    level = getattr(logging, None, logging.INFO)
    logger.setLevel(level)
    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(StructuredFormatter(fmt=config.format, component=logger_name))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def x_setup_logging__mutmut_8(
    config: LoggingConfig,
    *,
    logger_name: str = "codex.archive",
    stream: Any | None = None,
) -> logging.Logger:
    """Initialise a structured logger according to *config*."""

    logger = logging.getLogger(logger_name)
    level = getattr(logging, config.level.upper(), None)
    logger.setLevel(level)
    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(StructuredFormatter(fmt=config.format, component=logger_name))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def x_setup_logging__mutmut_9(
    config: LoggingConfig,
    *,
    logger_name: str = "codex.archive",
    stream: Any | None = None,
) -> logging.Logger:
    """Initialise a structured logger according to *config*."""

    logger = logging.getLogger(logger_name)
    level = getattr(config.level.upper(), logging.INFO)
    logger.setLevel(level)
    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(StructuredFormatter(fmt=config.format, component=logger_name))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def x_setup_logging__mutmut_10(
    config: LoggingConfig,
    *,
    logger_name: str = "codex.archive",
    stream: Any | None = None,
) -> logging.Logger:
    """Initialise a structured logger according to *config*."""

    logger = logging.getLogger(logger_name)
    level = getattr(logging, logging.INFO)
    logger.setLevel(level)
    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(StructuredFormatter(fmt=config.format, component=logger_name))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def x_setup_logging__mutmut_11(
    config: LoggingConfig,
    *,
    logger_name: str = "codex.archive",
    stream: Any | None = None,
) -> logging.Logger:
    """Initialise a structured logger according to *config*."""

    logger = logging.getLogger(logger_name)
    level = getattr(logging, config.level.upper(), )
    logger.setLevel(level)
    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(StructuredFormatter(fmt=config.format, component=logger_name))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def x_setup_logging__mutmut_12(
    config: LoggingConfig,
    *,
    logger_name: str = "codex.archive",
    stream: Any | None = None,
) -> logging.Logger:
    """Initialise a structured logger according to *config*."""

    logger = logging.getLogger(logger_name)
    level = getattr(logging, config.level.lower(), logging.INFO)
    logger.setLevel(level)
    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(StructuredFormatter(fmt=config.format, component=logger_name))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def x_setup_logging__mutmut_13(
    config: LoggingConfig,
    *,
    logger_name: str = "codex.archive",
    stream: Any | None = None,
) -> logging.Logger:
    """Initialise a structured logger according to *config*."""

    logger = logging.getLogger(logger_name)
    level = getattr(logging, config.level.upper(), logging.INFO)
    logger.setLevel(None)
    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(StructuredFormatter(fmt=config.format, component=logger_name))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def x_setup_logging__mutmut_14(
    config: LoggingConfig,
    *,
    logger_name: str = "codex.archive",
    stream: Any | None = None,
) -> logging.Logger:
    """Initialise a structured logger according to *config*."""

    logger = logging.getLogger(logger_name)
    level = getattr(logging, config.level.upper(), logging.INFO)
    logger.setLevel(level)
    handler = None
    handler.setFormatter(StructuredFormatter(fmt=config.format, component=logger_name))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def x_setup_logging__mutmut_15(
    config: LoggingConfig,
    *,
    logger_name: str = "codex.archive",
    stream: Any | None = None,
) -> logging.Logger:
    """Initialise a structured logger according to *config*."""

    logger = logging.getLogger(logger_name)
    level = getattr(logging, config.level.upper(), logging.INFO)
    logger.setLevel(level)
    handler = logging.StreamHandler(None)
    handler.setFormatter(StructuredFormatter(fmt=config.format, component=logger_name))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def x_setup_logging__mutmut_16(
    config: LoggingConfig,
    *,
    logger_name: str = "codex.archive",
    stream: Any | None = None,
) -> logging.Logger:
    """Initialise a structured logger according to *config*."""

    logger = logging.getLogger(logger_name)
    level = getattr(logging, config.level.upper(), logging.INFO)
    logger.setLevel(level)
    handler = logging.StreamHandler(stream and sys.stderr)
    handler.setFormatter(StructuredFormatter(fmt=config.format, component=logger_name))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def x_setup_logging__mutmut_17(
    config: LoggingConfig,
    *,
    logger_name: str = "codex.archive",
    stream: Any | None = None,
) -> logging.Logger:
    """Initialise a structured logger according to *config*."""

    logger = logging.getLogger(logger_name)
    level = getattr(logging, config.level.upper(), logging.INFO)
    logger.setLevel(level)
    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(None)
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def x_setup_logging__mutmut_18(
    config: LoggingConfig,
    *,
    logger_name: str = "codex.archive",
    stream: Any | None = None,
) -> logging.Logger:
    """Initialise a structured logger according to *config*."""

    logger = logging.getLogger(logger_name)
    level = getattr(logging, config.level.upper(), logging.INFO)
    logger.setLevel(level)
    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(StructuredFormatter(fmt=None, component=logger_name))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def x_setup_logging__mutmut_19(
    config: LoggingConfig,
    *,
    logger_name: str = "codex.archive",
    stream: Any | None = None,
) -> logging.Logger:
    """Initialise a structured logger according to *config*."""

    logger = logging.getLogger(logger_name)
    level = getattr(logging, config.level.upper(), logging.INFO)
    logger.setLevel(level)
    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(StructuredFormatter(fmt=config.format, component=None))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def x_setup_logging__mutmut_20(
    config: LoggingConfig,
    *,
    logger_name: str = "codex.archive",
    stream: Any | None = None,
) -> logging.Logger:
    """Initialise a structured logger according to *config*."""

    logger = logging.getLogger(logger_name)
    level = getattr(logging, config.level.upper(), logging.INFO)
    logger.setLevel(level)
    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(StructuredFormatter(component=logger_name))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def x_setup_logging__mutmut_21(
    config: LoggingConfig,
    *,
    logger_name: str = "codex.archive",
    stream: Any | None = None,
) -> logging.Logger:
    """Initialise a structured logger according to *config*."""

    logger = logging.getLogger(logger_name)
    level = getattr(logging, config.level.upper(), logging.INFO)
    logger.setLevel(level)
    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(StructuredFormatter(fmt=config.format, ))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def x_setup_logging__mutmut_22(
    config: LoggingConfig,
    *,
    logger_name: str = "codex.archive",
    stream: Any | None = None,
) -> logging.Logger:
    """Initialise a structured logger according to *config*."""

    logger = logging.getLogger(logger_name)
    level = getattr(logging, config.level.upper(), logging.INFO)
    logger.setLevel(level)
    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(StructuredFormatter(fmt=config.format, component=logger_name))
    logger.handlers.clear()
    logger.addHandler(None)
    logger.propagate = False
    return logger


def x_setup_logging__mutmut_23(
    config: LoggingConfig,
    *,
    logger_name: str = "codex.archive",
    stream: Any | None = None,
) -> logging.Logger:
    """Initialise a structured logger according to *config*."""

    logger = logging.getLogger(logger_name)
    level = getattr(logging, config.level.upper(), logging.INFO)
    logger.setLevel(level)
    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(StructuredFormatter(fmt=config.format, component=logger_name))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = None
    return logger


def x_setup_logging__mutmut_24(
    config: LoggingConfig,
    *,
    logger_name: str = "codex.archive",
    stream: Any | None = None,
) -> logging.Logger:
    """Initialise a structured logger according to *config*."""

    logger = logging.getLogger(logger_name)
    level = getattr(logging, config.level.upper(), logging.INFO)
    logger.setLevel(level)
    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(StructuredFormatter(fmt=config.format, component=logger_name))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = True
    return logger

x_setup_logging__mutmut_mutants : ClassVar[MutantDict] = {
'x_setup_logging__mutmut_1': x_setup_logging__mutmut_1, 
    'x_setup_logging__mutmut_2': x_setup_logging__mutmut_2, 
    'x_setup_logging__mutmut_3': x_setup_logging__mutmut_3, 
    'x_setup_logging__mutmut_4': x_setup_logging__mutmut_4, 
    'x_setup_logging__mutmut_5': x_setup_logging__mutmut_5, 
    'x_setup_logging__mutmut_6': x_setup_logging__mutmut_6, 
    'x_setup_logging__mutmut_7': x_setup_logging__mutmut_7, 
    'x_setup_logging__mutmut_8': x_setup_logging__mutmut_8, 
    'x_setup_logging__mutmut_9': x_setup_logging__mutmut_9, 
    'x_setup_logging__mutmut_10': x_setup_logging__mutmut_10, 
    'x_setup_logging__mutmut_11': x_setup_logging__mutmut_11, 
    'x_setup_logging__mutmut_12': x_setup_logging__mutmut_12, 
    'x_setup_logging__mutmut_13': x_setup_logging__mutmut_13, 
    'x_setup_logging__mutmut_14': x_setup_logging__mutmut_14, 
    'x_setup_logging__mutmut_15': x_setup_logging__mutmut_15, 
    'x_setup_logging__mutmut_16': x_setup_logging__mutmut_16, 
    'x_setup_logging__mutmut_17': x_setup_logging__mutmut_17, 
    'x_setup_logging__mutmut_18': x_setup_logging__mutmut_18, 
    'x_setup_logging__mutmut_19': x_setup_logging__mutmut_19, 
    'x_setup_logging__mutmut_20': x_setup_logging__mutmut_20, 
    'x_setup_logging__mutmut_21': x_setup_logging__mutmut_21, 
    'x_setup_logging__mutmut_22': x_setup_logging__mutmut_22, 
    'x_setup_logging__mutmut_23': x_setup_logging__mutmut_23, 
    'x_setup_logging__mutmut_24': x_setup_logging__mutmut_24
}

def setup_logging(*args, **kwargs):
    result = _mutmut_trampoline(x_setup_logging__mutmut_orig, x_setup_logging__mutmut_mutants, args, kwargs)
    return result 

setup_logging.__signature__ = _mutmut_signature(x_setup_logging__mutmut_orig)
x_setup_logging__mutmut_orig.__name__ = 'x_setup_logging'


def x_log_restore__mutmut_orig(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_1(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = None
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_2(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(None)
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_3(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail and "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_4(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "XXXX")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_5(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = None
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_6(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "XXactorXX": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_7(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "ACTOR": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_8(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "XXtombstoneXX": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_9(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "TOMBSTONE": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_10(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "XXstatusXX": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_11(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "STATUS": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_12(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = None
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_13(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["XXduration_msXX"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_14(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["DURATION_MS"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_15(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(None, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_16(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, None)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_17(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_18(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, )
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_19(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 4)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_20(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) or "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_21(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "XXduration_msXX" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_22(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "DURATION_MS" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_23(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" not in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_24(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = None
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_25(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["XXduration_msXX"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_26(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["DURATION_MS"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_27(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["XXduration_msXX"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_28(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["DURATION_MS"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_29(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = None

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_30(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["XXdetailXX"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_31(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["DETAIL"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_32(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = None

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_33(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level=None,
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_34(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=None,
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_35(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=None,
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_36(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=None,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_37(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=None,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_38(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_39(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_40(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_41(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_42(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_43(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="XXINFOXX",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_44(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="info",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_45(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.upper()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_46(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(None),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_47(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(None).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_48(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        None,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_49(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra=None,
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_50(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_51(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_52(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"XXextra_fieldsXX": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_53(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"EXTRA_FIELDS": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_54(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = None
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_55(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "XXactionXX": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_56(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "ACTION": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_57(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "XXRESTORE_BATCHXX",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_58(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "restore_batch",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_59(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "XXactorXX": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_60(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "ACTOR": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_61(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "XXtombstoneXX": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_62(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "TOMBSTONE": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_63(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "XXstatusXX": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_64(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "STATUS": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_65(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = None
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_66(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["XXdetailXX"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_67(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["DETAIL"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_68(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = None
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_69(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["XXmetricsXX"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_70(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["METRICS"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_71(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = None
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_72(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["XXmetricsXX"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_73(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["METRICS"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_74(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config or logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_75(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = None

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_76(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["XXlog_pathXX"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_77(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["LOG_PATH"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_78(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(None)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_79(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None and performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_80(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is not None or performance_config.emit_to_evidence:
        append_evidence(evidence_payload)


def x_log_restore__mutmut_81(
    logger: logging.Logger,
    *,
    actor: str,
    tombstone: str,
    status: str,
    detail: str | None = None,
    metrics: TimingMetrics | dict[str, Any] | None = None,
    logging_config: LoggingConfig | None = None,
    performance_config: PerformanceConfig | None = None,
) -> None:
    """Emit structured restore logging and append evidence."""

    sanitized = redact_text_credentials(detail or "")
    extra: dict[str, Any] = {
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if isinstance(metrics, TimingMetrics):
        extra["duration_ms"] = round(metrics.duration_ms, 3)
    elif isinstance(metrics, dict) and "duration_ms" in metrics:
        extra["duration_ms"] = metrics["duration_ms"]
    if sanitized:
        extra["detail"] = sanitized

    record = StructuredLogRecord(
        level="INFO",
        message=f"restore {status.lower()}",
        timestamp=datetime.now(UTC).strftime(ISO_FORMAT),
        component=logger.name,
        extra=extra,
    )

    logger.info(
        record.message,
        extra={"extra_fields": record.to_dict(), **record.extra},
    )

    evidence_payload: dict[str, Any] = {
        "action": "RESTORE_BATCH",
        "actor": actor,
        "tombstone": tombstone,
        "status": status,
    }
    if sanitized:
        evidence_payload["detail"] = sanitized
    if isinstance(metrics, TimingMetrics):
        evidence_payload["metrics"] = metrics.to_dict()
    elif isinstance(metrics, dict):
        evidence_payload["metrics"] = metrics
    if logging_config and logging_config.evidence_file:
        evidence_payload["log_path"] = str(logging_config.evidence_file)

    if performance_config is None or performance_config.emit_to_evidence:
        append_evidence(None)

x_log_restore__mutmut_mutants : ClassVar[MutantDict] = {
'x_log_restore__mutmut_1': x_log_restore__mutmut_1, 
    'x_log_restore__mutmut_2': x_log_restore__mutmut_2, 
    'x_log_restore__mutmut_3': x_log_restore__mutmut_3, 
    'x_log_restore__mutmut_4': x_log_restore__mutmut_4, 
    'x_log_restore__mutmut_5': x_log_restore__mutmut_5, 
    'x_log_restore__mutmut_6': x_log_restore__mutmut_6, 
    'x_log_restore__mutmut_7': x_log_restore__mutmut_7, 
    'x_log_restore__mutmut_8': x_log_restore__mutmut_8, 
    'x_log_restore__mutmut_9': x_log_restore__mutmut_9, 
    'x_log_restore__mutmut_10': x_log_restore__mutmut_10, 
    'x_log_restore__mutmut_11': x_log_restore__mutmut_11, 
    'x_log_restore__mutmut_12': x_log_restore__mutmut_12, 
    'x_log_restore__mutmut_13': x_log_restore__mutmut_13, 
    'x_log_restore__mutmut_14': x_log_restore__mutmut_14, 
    'x_log_restore__mutmut_15': x_log_restore__mutmut_15, 
    'x_log_restore__mutmut_16': x_log_restore__mutmut_16, 
    'x_log_restore__mutmut_17': x_log_restore__mutmut_17, 
    'x_log_restore__mutmut_18': x_log_restore__mutmut_18, 
    'x_log_restore__mutmut_19': x_log_restore__mutmut_19, 
    'x_log_restore__mutmut_20': x_log_restore__mutmut_20, 
    'x_log_restore__mutmut_21': x_log_restore__mutmut_21, 
    'x_log_restore__mutmut_22': x_log_restore__mutmut_22, 
    'x_log_restore__mutmut_23': x_log_restore__mutmut_23, 
    'x_log_restore__mutmut_24': x_log_restore__mutmut_24, 
    'x_log_restore__mutmut_25': x_log_restore__mutmut_25, 
    'x_log_restore__mutmut_26': x_log_restore__mutmut_26, 
    'x_log_restore__mutmut_27': x_log_restore__mutmut_27, 
    'x_log_restore__mutmut_28': x_log_restore__mutmut_28, 
    'x_log_restore__mutmut_29': x_log_restore__mutmut_29, 
    'x_log_restore__mutmut_30': x_log_restore__mutmut_30, 
    'x_log_restore__mutmut_31': x_log_restore__mutmut_31, 
    'x_log_restore__mutmut_32': x_log_restore__mutmut_32, 
    'x_log_restore__mutmut_33': x_log_restore__mutmut_33, 
    'x_log_restore__mutmut_34': x_log_restore__mutmut_34, 
    'x_log_restore__mutmut_35': x_log_restore__mutmut_35, 
    'x_log_restore__mutmut_36': x_log_restore__mutmut_36, 
    'x_log_restore__mutmut_37': x_log_restore__mutmut_37, 
    'x_log_restore__mutmut_38': x_log_restore__mutmut_38, 
    'x_log_restore__mutmut_39': x_log_restore__mutmut_39, 
    'x_log_restore__mutmut_40': x_log_restore__mutmut_40, 
    'x_log_restore__mutmut_41': x_log_restore__mutmut_41, 
    'x_log_restore__mutmut_42': x_log_restore__mutmut_42, 
    'x_log_restore__mutmut_43': x_log_restore__mutmut_43, 
    'x_log_restore__mutmut_44': x_log_restore__mutmut_44, 
    'x_log_restore__mutmut_45': x_log_restore__mutmut_45, 
    'x_log_restore__mutmut_46': x_log_restore__mutmut_46, 
    'x_log_restore__mutmut_47': x_log_restore__mutmut_47, 
    'x_log_restore__mutmut_48': x_log_restore__mutmut_48, 
    'x_log_restore__mutmut_49': x_log_restore__mutmut_49, 
    'x_log_restore__mutmut_50': x_log_restore__mutmut_50, 
    'x_log_restore__mutmut_51': x_log_restore__mutmut_51, 
    'x_log_restore__mutmut_52': x_log_restore__mutmut_52, 
    'x_log_restore__mutmut_53': x_log_restore__mutmut_53, 
    'x_log_restore__mutmut_54': x_log_restore__mutmut_54, 
    'x_log_restore__mutmut_55': x_log_restore__mutmut_55, 
    'x_log_restore__mutmut_56': x_log_restore__mutmut_56, 
    'x_log_restore__mutmut_57': x_log_restore__mutmut_57, 
    'x_log_restore__mutmut_58': x_log_restore__mutmut_58, 
    'x_log_restore__mutmut_59': x_log_restore__mutmut_59, 
    'x_log_restore__mutmut_60': x_log_restore__mutmut_60, 
    'x_log_restore__mutmut_61': x_log_restore__mutmut_61, 
    'x_log_restore__mutmut_62': x_log_restore__mutmut_62, 
    'x_log_restore__mutmut_63': x_log_restore__mutmut_63, 
    'x_log_restore__mutmut_64': x_log_restore__mutmut_64, 
    'x_log_restore__mutmut_65': x_log_restore__mutmut_65, 
    'x_log_restore__mutmut_66': x_log_restore__mutmut_66, 
    'x_log_restore__mutmut_67': x_log_restore__mutmut_67, 
    'x_log_restore__mutmut_68': x_log_restore__mutmut_68, 
    'x_log_restore__mutmut_69': x_log_restore__mutmut_69, 
    'x_log_restore__mutmut_70': x_log_restore__mutmut_70, 
    'x_log_restore__mutmut_71': x_log_restore__mutmut_71, 
    'x_log_restore__mutmut_72': x_log_restore__mutmut_72, 
    'x_log_restore__mutmut_73': x_log_restore__mutmut_73, 
    'x_log_restore__mutmut_74': x_log_restore__mutmut_74, 
    'x_log_restore__mutmut_75': x_log_restore__mutmut_75, 
    'x_log_restore__mutmut_76': x_log_restore__mutmut_76, 
    'x_log_restore__mutmut_77': x_log_restore__mutmut_77, 
    'x_log_restore__mutmut_78': x_log_restore__mutmut_78, 
    'x_log_restore__mutmut_79': x_log_restore__mutmut_79, 
    'x_log_restore__mutmut_80': x_log_restore__mutmut_80, 
    'x_log_restore__mutmut_81': x_log_restore__mutmut_81
}

def log_restore(*args, **kwargs):
    result = _mutmut_trampoline(x_log_restore__mutmut_orig, x_log_restore__mutmut_mutants, args, kwargs)
    return result 

log_restore.__signature__ = _mutmut_signature(x_log_restore__mutmut_orig)
x_log_restore__mutmut_orig.__name__ = 'x_log_restore'


def x_export_configuration__mutmut_orig(config: LoggingConfig) -> dict[str, Any]:
    """Return a JSON serialisable representation of *config*."""

    payload = asdict(config)
    if config.evidence_file is not None:
        payload["evidence_file"] = str(config.evidence_file)
    return payload


def x_export_configuration__mutmut_1(config: LoggingConfig) -> dict[str, Any]:
    """Return a JSON serialisable representation of *config*."""

    payload = None
    if config.evidence_file is not None:
        payload["evidence_file"] = str(config.evidence_file)
    return payload


def x_export_configuration__mutmut_2(config: LoggingConfig) -> dict[str, Any]:
    """Return a JSON serialisable representation of *config*."""

    payload = asdict(None)
    if config.evidence_file is not None:
        payload["evidence_file"] = str(config.evidence_file)
    return payload


def x_export_configuration__mutmut_3(config: LoggingConfig) -> dict[str, Any]:
    """Return a JSON serialisable representation of *config*."""

    payload = asdict(config)
    if config.evidence_file is None:
        payload["evidence_file"] = str(config.evidence_file)
    return payload


def x_export_configuration__mutmut_4(config: LoggingConfig) -> dict[str, Any]:
    """Return a JSON serialisable representation of *config*."""

    payload = asdict(config)
    if config.evidence_file is not None:
        payload["evidence_file"] = None
    return payload


def x_export_configuration__mutmut_5(config: LoggingConfig) -> dict[str, Any]:
    """Return a JSON serialisable representation of *config*."""

    payload = asdict(config)
    if config.evidence_file is not None:
        payload["XXevidence_fileXX"] = str(config.evidence_file)
    return payload


def x_export_configuration__mutmut_6(config: LoggingConfig) -> dict[str, Any]:
    """Return a JSON serialisable representation of *config*."""

    payload = asdict(config)
    if config.evidence_file is not None:
        payload["EVIDENCE_FILE"] = str(config.evidence_file)
    return payload


def x_export_configuration__mutmut_7(config: LoggingConfig) -> dict[str, Any]:
    """Return a JSON serialisable representation of *config*."""

    payload = asdict(config)
    if config.evidence_file is not None:
        payload["evidence_file"] = str(None)
    return payload

x_export_configuration__mutmut_mutants : ClassVar[MutantDict] = {
'x_export_configuration__mutmut_1': x_export_configuration__mutmut_1, 
    'x_export_configuration__mutmut_2': x_export_configuration__mutmut_2, 
    'x_export_configuration__mutmut_3': x_export_configuration__mutmut_3, 
    'x_export_configuration__mutmut_4': x_export_configuration__mutmut_4, 
    'x_export_configuration__mutmut_5': x_export_configuration__mutmut_5, 
    'x_export_configuration__mutmut_6': x_export_configuration__mutmut_6, 
    'x_export_configuration__mutmut_7': x_export_configuration__mutmut_7
}

def export_configuration(*args, **kwargs):
    result = _mutmut_trampoline(x_export_configuration__mutmut_orig, x_export_configuration__mutmut_mutants, args, kwargs)
    return result 

export_configuration.__signature__ = _mutmut_signature(x_export_configuration__mutmut_orig)
x_export_configuration__mutmut_orig.__name__ = 'x_export_configuration'
