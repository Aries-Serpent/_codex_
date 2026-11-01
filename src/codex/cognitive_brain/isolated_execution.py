"""Isolated execution and quality gates for improvement proposals.

Proposals are applied and verified in a disposable private Git snapshot with:

- a path allowlist and diff-size ceiling enforced before application,
- a scrubbed environment (no inherited secrets, ``GIT_ASKPASS`` neutralized),
- resource/time limits on every gate command,
- content-hashed logs for audit,
- idempotency: the same event identity is never executed twice.
- inherited Linux Landlock filesystem boundaries and denied TCP bind/connect.

Landlock ABI 4+ on supported Linux architectures is required. This is not a
full sandbox: UDP/Unix sockets, process-count and escaped-session lifecycle
containment remain unsupported. Restricted profiles are not exported.

Any gate failure discards the environment and leaves the source tree
untouched. Nothing here merges or pushes; the output is a verified
artifact descriptor that a later stage may turn into a PR.
"""

from __future__ import annotations

import ctypes
import fcntl
import hashlib
import json
import logging
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import time
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence, Tuple

from codex.cognitive_brain.authority import AuthorityDecision, AuthorityEnvelope

logger = logging.getLogger(__name__)

DEFAULT_GATES: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    (
        "compile",
        (
            sys.executable,
            "-c",
            "import ast,pathlib; "
            "[ast.parse(p.read_text()) for p in pathlib.Path('src').rglob('*.py')]",
        ),
    ),
    (
        "behavior",
        (
            sys.executable,
            "-c",
            "import unittest; s=unittest.defaultTestLoader.discover('tests'); "
            "assert s.countTestCases()>0, 'no behavioral tests'; "
            "raise SystemExit(not unittest.TextTestRunner().run(s).wasSuccessful())",
        ),
    ),
)
_GATE_NAMES = frozenset(
    {"compile", "behavior", "tests", "regression", "lint", "typecheck", "security"}
)

_SECRET_ENV = re.compile(r"(TOKEN|SECRET|PASSWORD|API_?KEY|PRIVATE_?KEY)", re.IGNORECASE)


def _restrict_process_filesystem(
    writable_roots: Sequence[Path],
    readonly_roots: Sequence[Path] = (),
) -> None:
    """Linux Landlock confinement, inherited by every descendant; fail closed."""
    if platform.machine() not in {"x86_64", "aarch64"}:
        raise OSError("unsupported filesystem confinement architecture")
    libc = ctypes.CDLL(None, use_errno=True)
    abi = libc.syscall(444, 0, 0, 1)
    if abi < 4:
        raise OSError("Landlock ABI 4 or later is required")

    class Ruleset(ctypes.Structure):
        _fields_ = [("handled_access_fs", ctypes.c_uint64), ("handled_access_net", ctypes.c_uint64)]

    class PathRule(ctypes.Structure):
        _pack_ = 1
        _fields_ = [("allowed_access", ctypes.c_uint64), ("parent_fd", ctypes.c_int)]

    read = (1 << 0) | (1 << 2) | (1 << 3)
    write = (1 << 1) | sum(1 << bit for bit in range(4, 15))
    ruleset = Ruleset(read | write, 3)  # Bind/connect TCP denied; UDP is not confined.
    fd = libc.syscall(444, ctypes.byref(ruleset), ctypes.sizeof(ruleset), 0)
    if fd < 0:
        raise OSError(ctypes.get_errno(), "filesystem ruleset unavailable")
    try:
        paths = [(root, read | write) for root in writable_roots]
        paths += [(root, read) for root in readonly_roots]
        paths += [
            (Path(path), read)
            for path in {
                "/usr",
                "/bin",
                "/lib",
                "/lib64",
                sys.prefix,
                sys.base_prefix,
            }
        ]
        paths += [
            (Path(path), 1 << 2)
            for path in {
                "/etc/ld.so.cache",
                "/etc/localtime",
                "/dev/urandom",
            }
        ]
        paths.append((Path("/dev/null"), (1 << 1) | (1 << 2)))
        for path, access in paths:
            if not path.exists():
                continue
            if not path.is_dir():
                access &= (1 << 0) | (1 << 1) | (1 << 2) | (1 << 14)
            parent_fd = os.open(path, os.O_PATH | os.O_CLOEXEC)
            try:
                rule = PathRule(access, parent_fd)
                if libc.syscall(445, fd, 1, ctypes.byref(rule), 0) != 0:
                    raise OSError(ctypes.get_errno(), "filesystem rule unavailable")
            finally:
                os.close(parent_fd)
        if libc.prctl(38, 1, 0, 0, 0) != 0 or libc.syscall(446, fd, 0) != 0:
            raise OSError(ctypes.get_errno(), "filesystem confinement unavailable")
    finally:
        os.close(fd)


@dataclass(frozen=True, slots=True)
class GateLog:
    """Recorded output of a single gate run."""

    name: str
    command: Tuple[str, ...]
    returncode: int
    duration_ms: float
    output_hash: str
    status: str = "passed"
    output_path: Optional[str] = None


@dataclass(frozen=True, slots=True)
class ExecutionOutcome:
    """Result of executing a proposal in isolation."""

    event_id: str
    status: str  # verified | rejected | duplicate | error
    gate_logs: Tuple[GateLog, ...] = ()
    artifact_hash: Optional[str] = None
    authority: Optional[AuthorityDecision] = None
    reason: str = ""
    patch_hash: Optional[str] = None
    base_sha: Optional[str] = None
    attempt_id: Optional[str] = None
    artifact_path: Optional[str] = None
    baseline_gate_logs: tuple[GateLog, ...] = ()
    required_gates: tuple[str, ...] = ()
    candidate_tree_hash: Optional[str] = None


class IdempotencyLedger:
    """Persistent record of executed event identities."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._locked():
            self._load()

    @contextmanager
    def _locked(self):
        with self.path.open("a+", encoding="utf-8") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield handle
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    def _load(self) -> set[str]:
        if not self.path.exists():
            return set()
        identities = set()
        with self.path.open(encoding="utf-8") as handle:
            for number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                try:
                    if len(line) > 1024 * 1024 or not line.endswith("\n"):
                        raise ValueError("oversized or interrupted record")
                    record = json.loads(line)
                    self._validate_record(record)
                except (ValueError, TypeError, KeyError) as exc:
                    raise ValueError(f"invalid execution ledger record at line {number}") from exc
                identities.add(record["event_id"])
        return identities

    @staticmethod
    def _validate_record(record: Any) -> None:
        if (
            not isinstance(record, dict)
            or not isinstance(record.get("event_id"), str)
            or not 0 < len(record["event_id"]) <= 256
            or not record["event_id"].strip()
            or record.get("status") not in {"claimed", "verified", "rejected", "error", "duplicate"}
        ):
            raise ValueError("invalid execution identity or state")
        if record["status"] == "claimed":
            if (
                record.get("schema_version") != 2
                or re.fullmatch(r"[0-9a-f]{32}", str(record.get("attempt_id"))) is None
                or re.fullmatch(r"[0-9a-f]{64}", str(record.get("patch_hash"))) is None
                or re.fullmatch(r"[0-9a-f]{40}", str(record.get("base_sha"))) is None
            ):
                raise ValueError("invalid claim identity")

    def seen(self, event_id: str) -> bool:
        with self._locked():
            return event_id in self._load()

    def claim(self, event_id: str, patch_hash: str, base_sha: str) -> Optional[str]:
        """An unresolved claim remains blocked after crash; recovery is never automatic."""
        attempt_id = uuid.uuid4().hex
        record = {
            "schema_version": 2,
            "event_id": event_id,
            "attempt_id": attempt_id,
            "status": "claimed",
            "patch_hash": patch_hash,
            "base_sha": base_sha,
        }
        self._validate_record(record)
        with self._locked() as handle:
            if event_id in self._load():
                return None
            handle.write(json.dumps(record, allow_nan=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
            return attempt_id

    def record(self, outcome: ExecutionOutcome) -> None:
        record = {**asdict(outcome), "schema_version": 2}
        self._validate_record(record)
        with self._locked() as handle:
            self._load()
            handle.write(json.dumps(record, allow_nan=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())


def scrub_environment(env: Optional[Mapping[str, str]] = None) -> dict[str, str]:
    """Return a minimal environment with no inherited secrets."""

    base = env if env is not None else {}
    scrubbed = {
        "PATH": base.get("PATH", str(Path(sys.executable).parent) + os.pathsep + os.defpath),
        "LANG": "C.UTF-8",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    scrubbed["GIT_TERMINAL_PROMPT"] = "0"
    scrubbed["GIT_ASKPASS"] = "true"
    scrubbed.pop("SSH_ASKPASS", None)
    return scrubbed


class IsolatedExecutor:
    """Apply and verify proposals inside a confined disposable Git snapshot."""

    def __init__(
        self,
        repo_path: Path,
        *,
        authority: Optional[AuthorityEnvelope] = None,
        ledger: Optional[IdempotencyLedger] = None,
        gates: Sequence[Tuple[str, Tuple[str, ...]]] = DEFAULT_GATES,
        work_root: Optional[Path] = None,
    ) -> None:
        self.repo_path = Path(repo_path)
        self.authority = authority or AuthorityEnvelope()
        self.ledger = ledger or IdempotencyLedger(
            self.repo_path / ".codex" / "improvement" / "executions.jsonl"
        )
        self.gates = tuple(gates)
        self.work_root = work_root

    def execute(
        self,
        *,
        event_id: str,
        patch_content: str,
        files: Sequence[str],
        diff_lines: int,
        human_approved: bool = False,
        base_sha: Optional[str] = None,
        patch_hash: Optional[str] = None,
    ) -> ExecutionOutcome:
        """Authorize, apply, and gate a proposal. Fails closed throughout."""

        if not isinstance(event_id, str) or not event_id.strip():
            raise ValueError("event identity is required")
        if (
            not isinstance(patch_content, str)
            or not patch_content
            or len(patch_content.encode("utf-8")) > 1024 * 1024
        ):
            raise ValueError("patch must contain at most one MiB of text")
        if (
            type(self.authority.limits.timeout_seconds) is not int
            or self.authority.limits.timeout_seconds <= 0
            or type(self.authority.limits.max_memory_mb) is not int
            or self.authority.limits.max_memory_mb <= 0
        ):
            raise ValueError("execution time and memory bounds must be positive integers")
        if self.ledger.seen(event_id):
            return ExecutionOutcome(
                event_id=event_id, status="duplicate", reason="event already executed"
            )

        actual_hash = hashlib.sha256(patch_content.encode("utf-8")).hexdigest()
        if patch_hash is not None and patch_hash != actual_hash:
            artifact_dir = self.repo_path / ".codex" / "improvement" / "artifacts" / actual_hash
            artifact_dir.mkdir(parents=True, exist_ok=True)
            (artifact_dir / "proposal.patch").write_text(patch_content, encoding="utf-8")
            (artifact_dir / f"{uuid.uuid4().hex}-identity-error.json").write_text(
                json.dumps(
                    {
                        "event_id": event_id,
                        "actual_patch_hash": actual_hash,
                        "declared_patch_hash": patch_hash,
                        "error": "patch hash mismatch",
                    }
                ),
                encoding="utf-8",
            )
            return ExecutionOutcome(
                event_id,
                "rejected",
                reason="patch hash mismatch",
                patch_hash=actual_hash,
                artifact_path=str(artifact_dir),
            )
        if base_sha:
            resolved_base = self._resolve_base_sha(base_sha)
            if resolved_base is None:
                return ExecutionOutcome(
                    event_id=event_id,
                    status="rejected",
                    reason=f"base commit {base_sha!r} is unavailable in repository",
                )
        else:
            resolved_base = subprocess.run(
                ["git", "rev-parse", "--verify", "HEAD^{commit}"],
                cwd=self.repo_path,
                env=scrub_environment(),
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            ).stdout.strip()

        decision = self.authority.evaluate(
            paths=tuple(files),
            diff_lines=diff_lines,
            env=scrub_environment(),
            human_approved=human_approved,
            idempotency_key=event_id,
        )
        if not decision.authorized:
            outcome = ExecutionOutcome(
                event_id=event_id,
                status="rejected",
                authority=decision,
                reason="; ".join(decision.reasons),
            )
            self.ledger.record(outcome)
            return outcome

        if (
            not self.gates
            or any(
                not isinstance(gate, (tuple, list))
                or len(gate) != 2
                or not isinstance(gate[0], str)
                or gate[0] not in _GATE_NAMES
                or not isinstance(gate[1], (tuple, list))
                or not gate[1]
                or any(not isinstance(arg, str) or not arg or "\x00" in arg for arg in gate[1])
                for gate in self.gates
            )
            or len({gate[0] for gate in self.gates}) != len(self.gates)
            or not any(gate[0] in {"behavior", "tests", "regression"} for gate in self.gates)
        ):
            return self._reject(event_id, decision, "required behavioral gates absent or malformed")
        attempt_id = self.ledger.claim(event_id, actual_hash, resolved_base)
        if attempt_id is None:
            return ExecutionOutcome(
                event_id, "duplicate", reason="event claimed; recovery required if interrupted"
            )

        work_dir = Path(
            tempfile.mkdtemp(
                prefix="improvement-", dir=str(self.work_root) if self.work_root else None
            )
        )
        try:
            return self._execute_in(
                work_dir,
                event_id,
                patch_content,
                files,
                decision,
                resolved_base,
                diff_lines,
                actual_hash,
                attempt_id,
            )
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _execute_in(
        self,
        work_dir: Path,
        event_id: str,
        patch_content: str,
        files: Sequence[str],
        decision: AuthorityDecision,
        base_sha: str,
        declared_lines: int,
        patch_hash: str,
        attempt_id: str,
    ) -> ExecutionOutcome:
        env = scrub_environment()
        deadline = time.monotonic() + self.authority.limits.timeout_seconds

        def run(command: Sequence[str], **kwargs: Any) -> subprocess.CompletedProcess:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise subprocess.TimeoutExpired(command, self.authority.limits.timeout_seconds)
            kwargs["timeout"] = min(kwargs.get("timeout", 30), remaining)
            if checkout.exists():
                kwargs["preexec_fn"] = lambda: _restrict_process_filesystem((work_dir,))
            return subprocess.run(command, **kwargs)

        home = work_dir / "home"
        home.mkdir()
        env["HOME"] = str(home)
        env["TMPDIR"] = str(home)
        artifact_dir = self.repo_path / ".codex" / "improvement" / "artifacts" / patch_hash
        artifact_dir.mkdir(parents=True, exist_ok=True)
        (artifact_dir / "proposal.patch").write_text(patch_content, encoding="utf-8")
        (artifact_dir / f"{attempt_id}-identity.json").write_text(
            json.dumps(
                {
                    "schema_version": 2,
                    "event_id": event_id,
                    "attempt_id": attempt_id,
                    "patch_hash": patch_hash,
                    "base_sha": base_sha,
                    "declared_files": list(files),
                    "declared_lines": declared_lines,
                    "network_isolation": "TCP denied; UDP and Unix sockets unsupported",
                    "filesystem_isolation": "Landlock private checkout/home and read-only runtime",
                    "sandbox": False,
                }
            ),
            encoding="utf-8",
        )
        checkout = work_dir / "tree"
        try:
            run(
                [
                    "git",
                    "archive",
                    "--format=tar",
                    f"--output={work_dir / 'base.tar'}",
                    base_sha,
                    "--",
                    ".",
                    ":(exclude).github/agents",
                ],
                cwd=self.repo_path,
                env=env,
                capture_output=True,
                text=True,
                timeout=120,
                check=True,
            )
            checkout.mkdir()
            with tarfile.open(work_dir / "base.tar") as archive:
                archive.extractall(checkout, filter="data")
            run(["git", "init", "--quiet"], cwd=checkout, env=env, check=True)
            run(["git", "add", "--all"], cwd=checkout, env=env, check=True)
            run(
                [
                    "git",
                    "-c",
                    "user.name=isolated-validator",
                    "-c",
                    "user.email=validator@example.test",
                    "-c",
                    "core.hooksPath=/dev/null",
                    "commit",
                    "--quiet",
                    "--allow-empty",
                    "-m",
                    "Authorized base snapshot",
                ],
                cwd=checkout,
                env=env,
                check=True,
            )
        except (
            subprocess.CalledProcessError,
            subprocess.TimeoutExpired,
            subprocess.SubprocessError,
            OSError,
            tarfile.TarError,
            ValueError,
        ) as e:
            outcome = ExecutionOutcome(
                event_id=event_id,
                status="error",
                authority=decision,
                reason=f"private snapshot creation failed: {e}",
            )
            self.ledger.record(outcome)
            return outcome

        try:
            patch_path = work_dir / "proposal.patch"
            python_paths = [checkout / "src"]
            python_paths.extend((checkout / "packages").glob("*/src"))
            env["PYTHONPATH"] = os.pathsep.join(str(path) for path in python_paths if path.is_dir())
            patch_path.write_text(patch_content, encoding="utf-8")
            applied = run(
                ["git", "apply", "--numstat", "-z", str(patch_path)],
                cwd=checkout,
                env=env,
                capture_output=True,
                text=True,
                timeout=60,
            )
            if applied.returncode != 0:
                return self._reject(
                    event_id, decision, f"patch does not apply: {applied.stderr.strip()}"
                )
            try:
                actual_files, actual_lines = self._patch_inventory(applied.stdout)
            except ValueError as exc:
                return self._reject(event_id, decision, str(exc))
            (artifact_dir / "inventory.json").write_text(
                json.dumps({"files": actual_files, "diff_lines": actual_lines}), encoding="utf-8"
            )
            reasons = self.authority.check_paths(tuple(actual_files))
            reasons += self.authority.check_diff_size(actual_lines, len(actual_files))
            if set(actual_files) != set(files):
                reasons += ("actual patch paths differ from authorized declaration",)
            if actual_lines > declared_lines:
                reasons += ("actual patch exceeds declared diff size",)
            if not actual_files or actual_lines == 0:
                reasons += ("no-op or mode-only patch is not an executable repair",)
            if reasons:
                return self._reject(event_id, decision, "; ".join(reasons))
            for rel in actual_files:
                target = checkout / rel
                if any(part.is_symlink() for part in (target, *target.parents)):
                    return self._reject(event_id, decision, "symlink patch target is unsupported")
            if re.search(
                r"^(?:new file mode|new mode) (?!100644$|100755$)\d+", patch_content, re.M
            ):
                return self._reject(event_id, decision, "unsupported patch file mode")
            run(
                ["git", "apply", "--check", str(patch_path)],
                cwd=checkout,
                env=env,
                capture_output=True,
                timeout=30,
                check=True,
            )
            baseline_logs = tuple(
                self._run_gate(
                    name, command, checkout, env, deadline=deadline, log_dir=artifact_dir
                )
                for name, command in self.gates
                if name in {"behavior", "tests", "regression"}
            )
            run(
                ["git", "add", "--all"],
                cwd=checkout,
                env=env,
                capture_output=True,
                check=True,
            )
            changed = run(
                ["git", "diff", "--cached", "--quiet"],
                cwd=checkout,
                env=env,
                capture_output=True,
            )
            if changed.returncode != 0 or not any(
                log.returncode != 0 and log.status == "failed" for log in baseline_logs
            ):
                outcome = ExecutionOutcome(
                    event_id=event_id,
                    status="rejected",
                    reason=(
                        "baseline gate changed candidate"
                        if changed.returncode != 0
                        else "no demonstrated failing baseline behavior"
                    ),
                    baseline_gate_logs=baseline_logs,
                    gate_logs=(
                        baseline_logs
                        if any(log.status != "passed" for log in baseline_logs)
                        else ()
                    ),
                    patch_hash=patch_hash,
                    base_sha=base_sha,
                    attempt_id=attempt_id,
                    artifact_path=str(artifact_dir),
                )
                self.ledger.record(outcome)
                return outcome
            run(
                ["git", "apply", str(patch_path)],
                cwd=checkout,
                env=env,
                capture_output=True,
                text=True,
                timeout=60,
                check=True,
            )

            run(
                ["git", "add", "--all"],
                cwd=checkout,
                env=env,
                capture_output=True,
                timeout=30,
                check=True,
            )
            candidate_tree = run(
                ["git", "write-tree"],
                cwd=checkout,
                env=env,
                capture_output=True,
                text=True,
                timeout=30,
                check=True,
            ).stdout.strip()
            staged = run(
                ["git", "diff", "--cached", "--numstat", "-z"],
                cwd=checkout,
                env=env,
                capture_output=True,
                text=True,
                timeout=30,
                check=True,
            )
            staged_files, staged_lines = self._patch_inventory(staged.stdout)
            if staged_files != actual_files or staged_lines != actual_lines:
                return self._reject(event_id, decision, "applied patch inventory mismatch")
            candidate_filesystem = self._filesystem_inventory(checkout, deadline)
            gate_logs: list[GateLog] = []
            for name, command in self.gates:
                gate_logs.append(
                    self._run_gate(
                        name, command, checkout, env, deadline=deadline, log_dir=artifact_dir
                    )
                )
                if gate_logs[-1].returncode != 0:
                    break
            failing = [log for log in gate_logs if log.returncode != 0]
            if failing:
                outcome = ExecutionOutcome(
                    event_id=event_id,
                    status="rejected",
                    gate_logs=tuple(gate_logs),
                    authority=decision,
                    reason=f"gates failed: {', '.join(log.name for log in failing)}",
                    baseline_gate_logs=baseline_logs,
                    patch_hash=patch_hash,
                    base_sha=base_sha,
                    attempt_id=attempt_id,
                    artifact_path=str(artifact_dir),
                )
                self.ledger.record(outcome)
                return outcome

            if self._filesystem_inventory(checkout, deadline) != candidate_filesystem:
                return self._reject(event_id, decision, "gate changed the authorized candidate")
            artifact_hash = self._hash_paths(checkout, files)
            outcome = ExecutionOutcome(
                event_id=event_id,
                status="verified",
                gate_logs=tuple(gate_logs),
                artifact_hash=artifact_hash,
                authority=decision,
                reason=f"base={base_sha}; local process verification, not a network sandbox",
                patch_hash=patch_hash,
                base_sha=base_sha,
                attempt_id=attempt_id,
                artifact_path=str(artifact_dir),
                baseline_gate_logs=baseline_logs,
                required_gates=tuple(name for name, _ in self.gates),
                candidate_tree_hash=candidate_tree,
            )
            (artifact_dir / f"{attempt_id}.json").write_text(
                json.dumps(asdict(outcome)), encoding="utf-8"
            )
            self.ledger.record(outcome)
            return outcome
        except subprocess.TimeoutExpired:
            outcome = ExecutionOutcome(
                event_id=event_id,
                status="rejected",
                authority=decision,
                reason="execution timed out",
            )
            self.ledger.record(outcome)
            return outcome
        except subprocess.CalledProcessError as e:
            outcome = ExecutionOutcome(
                event_id=event_id,
                status="error",
                authority=decision,
                reason=f"execution error: {e}",
            )
            self.ledger.record(outcome)
            return outcome

    def _reject(self, event_id: str, decision: AuthorityDecision, reason: str) -> ExecutionOutcome:
        outcome = ExecutionOutcome(
            event_id=event_id, status="rejected", authority=decision, reason=reason
        )
        self.ledger.record(outcome)
        return outcome

    def _run_gate(
        self,
        name: str,
        command: Tuple[str, ...],
        cwd: Path,
        env: Mapping[str, str],
        *,
        deadline: Optional[float] = None,
        log_dir: Optional[Path] = None,
    ) -> GateLog:
        start = time.monotonic()
        command = tuple(command)
        if command[0] in {"python", "python3"}:
            command = (sys.executable, *command[1:])
        deadline = deadline or start + self.authority.limits.timeout_seconds
        try:
            with tempfile.TemporaryFile() as output:

                def limits():
                    import resource

                    memory = self.authority.limits.max_memory_mb * 1024 * 1024
                    resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
                    resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024, 1024 * 1024))
                    roots = []
                    if env.get("HOME"):
                        roots.append(Path(env["HOME"]))
                    _restrict_process_filesystem(roots, (cwd,))

                proc = subprocess.Popen(
                    list(command),
                    cwd=cwd,
                    env=dict(env),
                    stdout=output,
                    stderr=output,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True,
                    preexec_fn=limits,
                )
                status = "passed"
                try:
                    proc.wait(timeout=max(0, deadline - time.monotonic()))
                    code = proc.returncode
                    if code:
                        status = "failed"
                except subprocess.TimeoutExpired:
                    code, status = 124, "timeout"
                finally:
                    try:
                        os.killpg(proc.pid, 9)
                    except ProcessLookupError:
                        pass
                    proc.wait(timeout=2)
                output.seek(0)
                data = output.read(1024 * 1024 + 1)
                if len(data) > 1024 * 1024:
                    code, status = 125, "output_limit"
                output_hash = hashlib.sha256(data).hexdigest()
                output_path = None
                if log_dir is not None:
                    output_file = log_dir / f"{output_hash}.log"
                    output_file.write_bytes(data)
                    output_path = str(output_file)
                return GateLog(
                    name,
                    command,
                    code,
                    (time.monotonic() - start) * 1000,
                    output_hash,
                    status,
                    output_path,
                )
        except (OSError, ValueError, subprocess.SubprocessError):
            return GateLog(
                name=name,
                command=tuple(command),
                returncode=127,
                duration_ms=(time.monotonic() - start) * 1000,
                output_hash=hashlib.sha256(b"launch_error").hexdigest(),
                status="launch_error",
            )

    def _resolve_base_sha(self, base_sha: str) -> Optional[str]:
        if not re.fullmatch(r"[0-9a-f]{40}", base_sha):
            return None
        resolved = subprocess.run(
            ["git", "rev-parse", "--verify", base_sha + "^{commit}"],
            cwd=self.repo_path,
            env=scrub_environment(),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if resolved.returncode != 0:
            return None
        return resolved.stdout.strip() or None

    @staticmethod
    def _filesystem_inventory(root: Path, deadline: float) -> dict[str, tuple[int, str]]:
        """Observe bytes/types directly, never trust a gate-controlled Git index."""
        inventory = {}
        for directory, subdirs, files in os.walk(root, followlinks=False):
            if Path(directory) == root:
                subdirs[:] = [name for name in subdirs if name != ".git"]
                files = [name for name in files if name != ".git"]
            for name in (*subdirs, *files):
                if time.monotonic() >= deadline:
                    raise subprocess.TimeoutExpired("filesystem verification", 0)
                path = Path(directory) / name
                metadata = path.lstat()
                digest = hashlib.sha256()
                if stat.S_ISREG(metadata.st_mode):
                    with path.open("rb") as stream:
                        while chunk := stream.read(65536):
                            if time.monotonic() >= deadline:
                                raise subprocess.TimeoutExpired("filesystem verification", 0)
                            digest.update(chunk)
                elif stat.S_ISLNK(metadata.st_mode):
                    digest.update(os.fsencode(os.readlink(path)))
                inventory[path.relative_to(root).as_posix()] = (
                    metadata.st_mode,
                    digest.hexdigest(),
                )
        return inventory

    @staticmethod
    def _patch_inventory(output: str) -> tuple[list[str], int]:
        paths = []
        lines = 0
        for row in output.split("\x00"):
            if not row:
                continue
            fields = row.split("\t", 2)
            if len(fields) != 3 or not fields[0].isdigit() or not fields[1].isdigit():
                raise ValueError("binary or ambiguous patch inventory is unsupported")
            additions, deletions, path = fields
            if not path:
                raise ValueError("rename inventory is unsupported")
            paths.append(path)
            lines += int(additions) + int(deletions)
        return sorted(paths), lines

    @staticmethod
    def _hash_paths(root: Path, files: Sequence[str]) -> str:
        digest = hashlib.sha256()
        for rel in sorted(files):
            target = root / rel
            digest.update(rel.encode("utf-8") + b"\x00")
            if target.is_file():
                digest.update(str(target.stat().st_mode).encode("ascii") + b"\x00")
                digest.update(target.read_bytes())
            else:
                digest.update(b"deleted\x00")
        return digest.hexdigest()
