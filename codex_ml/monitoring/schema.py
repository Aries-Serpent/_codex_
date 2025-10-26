"""Typed representations of monitoring payloads."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

__all__ = ["LogRecord"]


@dataclass
class LogRecord:
    message: str
    payload: Mapping[str, object]
