"""Read-only checks of local isolated-executor artifacts, not reviewer attestation.

The supplied outcome is the caller's identity anchor. Hashes detect inconsistent
or missing retained files; they cannot authenticate a coherently fabricated
local artifact collection or establish production authorization.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import stat
from dataclasses import asdict, is_dataclass
from pathlib import Path, PurePosixPath
from typing import Any, TypeGuard


def _hex(value: Any, length: int) -> TypeGuard[str]:
    return isinstance(value, str) and re.fullmatch(rf"[0-9a-f]{{{length}}}", value) is not None


def _path(value: Any) -> bool:
    return (
        isinstance(value, str)
        and bool(value)
        and not PurePosixPath(value).is_absolute()
        and "\\" not in value
        and not any(part in {"", ".", ".."} for part in value.split("/"))
    )


def _file_identity(info: os.stat_result) -> tuple[int, ...]:
    return (
        info.st_dev,
        info.st_ino,
        info.st_mode,
        info.st_nlink,
        info.st_size,
        info.st_mtime_ns,
        info.st_ctime_ns,
    )


def _read(
    root: Path,
    path: Path,
    observed: dict[Path, tuple[tuple[int, ...], bytes]] | None = None,
) -> bytes:
    if not path.is_absolute():
        path = Path.cwd() / path
    if ".." in path.parts or path != path.resolve():
        raise ValueError("aliased artifact path")
    path.relative_to(root)
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > 4 * 1024 * 1024:
        raise ValueError("artifact must be a bounded, unaliased regular file")
    with path.open("rb") as handle:
        data = handle.read(4 * 1024 * 1024 + 1)
    if len(data) > 4 * 1024 * 1024:
        raise ValueError("artifact exceeds size limit")
    identity = _file_identity(info)
    if path != path.resolve() or _file_identity(path.stat()) != identity:
        raise ValueError("artifact changed while reading")
    if observed is not None:
        if path in observed and observed[path] != (identity, data):
            raise ValueError("artifact changed between reads")
        observed[path] = (identity, data)
    return data


def _json(
    root: Path, path: Path, observed: dict[Path, tuple[tuple[int, ...], bytes]]
) -> dict[str, Any]:
    value = json.loads(_read(root, path, observed))
    if not isinstance(value, dict):
        raise ValueError("artifact object required")
    return value


def _patch_scope(patch: str) -> tuple[list[str], int]:
    """Conservatively support ordinary textual patches; other forms stay unknown."""
    paths: list[str] = []
    lines = 0
    in_hunk = False
    for line in patch.splitlines():
        if line.startswith("diff --git "):
            in_hunk = False
            match = re.fullmatch(r"diff --git a/(\S+) b/(\S+)", line)
            if not match or match[1] != match[2] or not _path(match[1]):
                raise ValueError("unsupported or noncanonical patch scope")
            paths.append(match[1])
        elif line.startswith(("rename ", "copy ", "Binary ", "GIT binary", "new mode ")):
            raise ValueError("unsupported retained patch form")
        elif line.startswith("@@ "):
            in_hunk = True
        elif in_hunk and line.startswith(("+", "-")):
            lines += 1
    if not paths or len(paths) != len(set(paths)) or not lines:
        raise ValueError("missing or duplicate patch paths")
    return paths, lines


def read_retained_execution(repo_path: str | Path, outcome: Any) -> dict[str, Any]:
    """Validate an executor outcome against its exact retained local attempt.

    Never launches a command, changes a claim, retries an attempt, or grants
    execution/review authority. Unsupported patch forms fail closed as unknown.
    """
    result: dict[str, Any] = {
        "status": "unknown",
        "proof_scope": "local-retained-execution",
        "authenticated_review": False,
        "production_proof": False,
        "execution_authorized": False,
        "authority_source": "retained-assertion-not-rederived",
        "profile_activation": "unverified",
        "profile_mapping": None,
    }
    try:
        if is_dataclass(outcome) and not isinstance(outcome, type):
            outcome = asdict(outcome)
        if not isinstance(outcome, dict):
            raise ValueError("execution outcome required")
        # A denied/cancelled outcome is never promoted, even without artifacts.
        if outcome.get("status") in {"rejected", "cancelled"}:
            return {**result, "status": outcome["status"], "reason": outcome.get("reason", "")}
        if outcome.get("status") != "verified":
            raise ValueError("no verified retained attempt")
        root = Path(repo_path).absolute()
        if root != root.resolve():
            raise ValueError("aliased repository root")
        observed: dict[Path, tuple[tuple[int, ...], bytes]] = {}
        patch_hash, base, attempt = (
            outcome.get(k) for k in ("patch_hash", "base_sha", "attempt_id")
        )
        if not (_hex(patch_hash, 64) and _hex(base, 40) and _hex(attempt, 32)):
            raise ValueError("immutable execution identity required")
        directory = root / ".codex/improvement/artifacts" / patch_hash
        if outcome.get("artifact_path") != str(directory):
            raise ValueError("artifact path does not match canonical patch identity")
        retained = _json(root, directory / f"{attempt}.json", observed)
        if retained != json.loads(json.dumps(outcome, allow_nan=False)):
            raise ValueError("retained outcome differs from requested attempt")
        identity = _json(root, directory / f"{attempt}-identity.json", observed)
        if identity.get("schema_version") != 2 or any(
            identity.get(key) != outcome.get(key)
            for key in ("event_id", "attempt_id", "patch_hash", "base_sha")
        ):
            raise ValueError("retained attempt identity mismatch")
        if not isinstance(outcome.get("event_id"), str) or not outcome["event_id"].strip():
            raise ValueError("event identity required")
        patch = _read(root, directory / "proposal.patch", observed)
        if hashlib.sha256(patch).hexdigest() != patch_hash:
            raise ValueError("retained patch hash mismatch")
        paths, lines = _patch_scope(patch.decode("utf-8"))
        inventory = _json(root, directory / "inventory.json", observed)
        declared = identity.get("declared_files")
        if (
            not isinstance(declared, list)
            or not all(_path(path) for path in declared)
            or len(set(declared)) != len(declared)
            or set(declared) != set(paths)
            or inventory.get("files") != sorted(paths)
            or inventory.get("diff_lines") != lines
            or type(identity.get("declared_lines")) is not int
            or identity["declared_lines"] < lines
        ):
            raise ValueError("retained patch scope mismatch")
        authority = outcome.get("authority")
        if not isinstance(authority, dict) or authority.get("authorized") is not True:
            raise ValueError("authorized local execution decision absent")
        if not _hex(outcome.get("artifact_hash"), 64) or not _hex(
            outcome.get("candidate_tree_hash"), 40
        ):
            raise ValueError("candidate identity absent")
        required = outcome.get("required_gates")
        gates = outcome.get("gate_logs")
        baseline = outcome.get("baseline_gate_logs")
        if (
            not isinstance(required, (list, tuple))
            or not required
            or not all(isinstance(name, str) for name in required)
            or len(set(required)) != len(required)
            or not isinstance(gates, (list, tuple))
            or not isinstance(baseline, (list, tuple))
            or any(not isinstance(log, dict) for log in (*gates, *baseline))
            or [log.get("name") for log in gates] != list(required)
            or [log.get("name") for log in baseline]
            != [name for name in required if name in {"behavior", "tests", "regression"}]
            or not baseline
        ):
            raise ValueError("complete required gate and baseline identity absent")
        for log in (*gates, *baseline):
            command = log.get("command")
            duration = log.get("duration_ms")
            if (
                not isinstance(command, (list, tuple))
                or not command
                or not all(isinstance(arg, str) and arg and "\x00" not in arg for arg in command)
                or type(log.get("returncode")) is not int
                or log.get("status") != ("passed" if log["returncode"] == 0 else "failed")
                or type(duration) not in (int, float)
                or not math.isfinite(duration)
                or duration < 0
                or not _hex(log.get("output_hash"), 64)
            ):
                raise ValueError("invalid retained gate observation")
            output = directory / f"{log['output_hash']}.log"
            if (
                log.get("output_path") != str(output)
                or hashlib.sha256(_read(root, output, observed)).hexdigest() != log["output_hash"]
            ):
                raise ValueError("retained gate output mismatch")
        by_name = {log["name"]: log for log in gates}
        if any(log["returncode"] != 0 for log in gates) or not any(
            log["returncode"] != 0 for log in baseline
        ):
            raise ValueError("before-fail/after-pass evidence absent")
        if any(log["command"] != by_name[log["name"]]["command"] for log in baseline):
            raise ValueError("baseline/candidate command mismatch")
        # These are mutable local files, not an immutable or authenticated store.
        for path in observed:
            _read(root, path, observed)
        return {
            **result,
            "status": "pass",
            "reason": "consistent retained local execution; not authenticated review",
            "event_id": outcome["event_id"],
            "attempt_id": attempt,
            "patch_hash": patch_hash,
            "base_sha": base,
            "files": paths,
            "gate_logs": list(gates),
            "baseline_gate_logs": list(baseline),
        }
    except (OSError, ValueError, TypeError, KeyError, OverflowError) as exc:
        return {**result, "reason": str(exc)}
