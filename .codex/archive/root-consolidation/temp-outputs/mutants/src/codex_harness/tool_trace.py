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
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_STATUS_PASS = {"pass", "passed", "ok", "success", "green", "approved", "true", "1"}
_STATUS_FAIL = {"fail", "failed", "block", "blocked", "reject", "false", "0", "red"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_status(value: Any) -> bool | None:
    if value is None:
        return None
    lowered = str(value).lower()
    if lowered in _STATUS_PASS:
        return True
    if lowered in _STATUS_FAIL:
        return False
    return None


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

    def __init__(self, output_path: Path | str = Path("artifacts/tool_trace.ndjson")) -> None:
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.ra_gate_results: dict[str, bool | None] = {}

    def load_ra_gate_results(self, path: Path | str) -> dict[str, bool | None]:
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

    def record_invocation(self, invocation: ToolInvocation) -> None:
        line = json.dumps(invocation.to_dict(), sort_keys=True)
        with self.output_path.open("a", encoding="utf-8") as handle:
            handle.write(line)
            handle.write("\n")

    def run_tool(
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
                completed.returncode,
                argv,
                output=completed.stdout,
                stderr=completed.stderr,
            )
        return invocation

    def log_manual(
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

    def read_invocations(self) -> list[ToolInvocation]:
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


__all__ = ["ToolInvocation", "ToolTraceLogger"]
