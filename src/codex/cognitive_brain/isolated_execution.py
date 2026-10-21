"""Isolated execution and quality gates for improvement proposals.

Proposals are applied and verified in a *disposable* git worktree with:

- a path allowlist and diff-size ceiling enforced before application,
- a scrubbed environment (no inherited secrets, ``GIT_ASKPASS`` neutralized),
- resource/time limits on every gate command,
- content-hashed logs for audit,
- idempotency: the same event identity is never executed twice.

Any gate failure discards the environment and leaves the source tree
untouched. Nothing here merges or pushes; the output is a verified
artifact descriptor that a later stage may turn into a PR.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping, Optional, Sequence, Tuple

from codex.cognitive_brain.authority import AuthorityDecision, AuthorityEnvelope

logger = logging.getLogger(__name__)

DEFAULT_GATES: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    ("compile", ("python", "-m", "compileall", "-q", ".")),
)

_SECRET_ENV = re.compile(r"(TOKEN|SECRET|PASSWORD|API_?KEY|PRIVATE_?KEY)", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class GateLog:
    """Recorded output of a single gate run."""

    name: str
    command: Tuple[str, ...]
    returncode: int
    duration_ms: float
    output_hash: str


@dataclass(frozen=True, slots=True)
class ExecutionOutcome:
    """Result of executing a proposal in isolation."""

    event_id: str
    status: str  # verified | rejected | duplicate | error
    gate_logs: Tuple[GateLog, ...] = ()
    artifact_hash: Optional[str] = None
    authority: Optional[AuthorityDecision] = None
    reason: str = ""


class IdempotencyLedger:
    """Persistent record of executed event identities."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._seen = self._load()

    def _load(self) -> set[str]:
        if not self.path.exists():
            return set()
        return {
            json.loads(line)["event_id"]
            for line in self.path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        }

    def seen(self, event_id: str) -> bool:
        return event_id in self._seen

    def record(self, outcome: ExecutionOutcome) -> None:
        self._seen.add(outcome.event_id)
        with open(self.path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(outcome), default=str) + "\n")


def scrub_environment(env: Optional[Mapping[str, str]] = None) -> dict[str, str]:
    """Return a minimal environment with no inherited secrets."""

    base = env if env is not None else os.environ
    scrubbed = {
        key: value for key, value in base.items() if not _SECRET_ENV.search(key)
    }
    scrubbed["GIT_TERMINAL_PROMPT"] = "0"
    scrubbed["GIT_ASKPASS"] = "true"
    scrubbed.pop("SSH_ASKPASS", None)
    return scrubbed


class IsolatedExecutor:
    """Apply and verify proposals inside a disposable worktree."""

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
    ) -> ExecutionOutcome:
        """Authorize, apply, and gate a proposal. Fails closed throughout."""

        if self.ledger.seen(event_id):
            return ExecutionOutcome(
                event_id=event_id, status="duplicate", reason="event already executed"
            )

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

        work_dir = Path(
            tempfile.mkdtemp(prefix="improvement-", dir=str(self.work_root) if self.work_root else None)
        )
        try:
            return self._execute_in(work_dir, event_id, patch_content, files, decision)
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
    ) -> ExecutionOutcome:
        env = scrub_environment()
        checkout = work_dir / "tree"
        try:
            subprocess.run(
                ["git", "worktree", "add", "--detach", str(checkout), "HEAD"],
                cwd=self.repo_path,
                env=env,
                capture_output=True,
                text=True,
                timeout=120,
                check=True,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            outcome = ExecutionOutcome(
                event_id=event_id,
                status="error",
                authority=decision,
                reason=f"worktree creation failed: {e}",
            )
            self.ledger.record(outcome)
            return outcome

        try:
            patch_path = work_dir / "proposal.patch"
            patch_path.write_text(patch_content, encoding="utf-8")
            applied = subprocess.run(
                ["git", "apply", "--stat", str(patch_path)],
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
            subprocess.run(
                ["git", "apply", str(patch_path)],
                cwd=checkout,
                env=env,
                capture_output=True,
                text=True,
                timeout=60,
                check=True,
            )

            gate_logs: list[GateLog] = []
            for name, command in self.gates:
                gate_logs.append(self._run_gate(name, command, checkout, env))
            failing = [log for log in gate_logs if log.returncode != 0]
            if failing:
                outcome = ExecutionOutcome(
                    event_id=event_id,
                    status="rejected",
                    gate_logs=tuple(gate_logs),
                    authority=decision,
                    reason=f"gates failed: {', '.join(log.name for log in failing)}",
                )
                self.ledger.record(outcome)
                return outcome

            artifact_hash = self._hash_paths(checkout, files)
            outcome = ExecutionOutcome(
                event_id=event_id,
                status="verified",
                gate_logs=tuple(gate_logs),
                artifact_hash=artifact_hash,
                authority=decision,
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
        finally:
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(checkout)],
                cwd=self.repo_path,
                env=env,
                capture_output=True,
                timeout=60,
            )

    def _reject(
        self, event_id: str, decision: AuthorityDecision, reason: str
    ) -> ExecutionOutcome:
        outcome = ExecutionOutcome(
            event_id=event_id, status="rejected", authority=decision, reason=reason
        )
        self.ledger.record(outcome)
        return outcome

    def _run_gate(
        self, name: str, command: Tuple[str, ...], cwd: Path, env: Mapping[str, str]
    ) -> GateLog:
        import time

        start = time.time()
        try:
            result = subprocess.run(
                list(command),
                cwd=cwd,
                env=dict(env),
                capture_output=True,
                text=True,
                timeout=self.authority.limits.timeout_seconds,
            )
            output = result.stdout + result.stderr
            return GateLog(
                name=name,
                command=tuple(command),
                returncode=result.returncode,
                duration_ms=(time.time() - start) * 1000,
                output_hash=hashlib.sha256(output.encode("utf-8")).hexdigest(),
            )
        except subprocess.TimeoutExpired:
            return GateLog(
                name=name,
                command=tuple(command),
                returncode=124,
                duration_ms=(time.time() - start) * 1000,
                output_hash=hashlib.sha256(b"timeout").hexdigest(),
            )

    @staticmethod
    def _hash_paths(root: Path, files: Sequence[str]) -> str:
        digest = hashlib.sha256()
        for rel in sorted(files):
            target = root / rel
            if target.is_file():
                digest.update(rel.encode("utf-8"))
                digest.update(target.read_bytes())
        return digest.hexdigest()
