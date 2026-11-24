#!/usr/bin/env python3
"""Safe CLI for GitHub Copilot agent tasks.

The module uses the REST endpoint:
  /agents/repos/{owner}/{repo}/tasks

It is intentionally dry of hosted mutation logic outside an explicit mutation
command.  HTTP access is injected through a small stdlib-compatible transport
so tests and callers never need to touch the live API.
"""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import os
import re
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Protocol, Sequence

try:
    from scripts.ci import session_budget_guard
except ImportError:  # pragma: no cover - direct-script compatibility
    session_budget_guard = None  # type: ignore[assignment]

API_BASE = "https://api.github.com"
GITHUB_API_BASE = API_BASE
API_VERSION = "2026-03-10"
AGENT_API_VERSION = API_VERSION
ACCEPT = "application/vnd.github+json"
TASKS_ENDPOINT_TEMPLATE = "/agents/repos/{owner}/{repo}/tasks"
LAUNCH_KEY_LENGTH = 40
LAUNCH_KEY_HEX_LENGTH = 40
DEDUP_STATE_FILE = ".codex/copilot_agent_task_dedup.json"
HANDOFF_STATE_FILE = ".codex/copilot_agent_task_handoff.json"
HANDOFF_STATE_ALIAS_FILE = ".codex/handoff_state.json"
ACTION_LOG_FILE = ".codex/action_log.ndjson"
LOCK_FILE = ".codex/copilot_agent_task.lock"
SOLE_OWNER = "mbaetiong"
DEFAULT_REPO_OWNER = "Aries-Serpent"
DEFAULT_REPO_NAME = "_codex_"

TERMINAL_STATUSES = frozenset(
    {
        "completed",
        "complete",
        "succeeded",
        "success",
        "failed",
        "failure",
        "cancelled",
        "canceled",
        "error",
        "timed_out",
        "timeout",
        "stopped",
    }
)

_GITHUB_OWNER_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")
_REPO_NAME_RE = re.compile(r"^[A-Za-z0-9_.-]{1,100}$")
_LAUNCH_KEY_RE = re.compile(r"^\S{40}$")
_BRANCH_FORBIDDEN_CHARS = re.compile(r"[ ~^:?*\\\x00-\x1f\x7f\[\]]")


class CopilotAgentTaskError(RuntimeError):
    """Base error for the agent task module."""


class PolicyViolation(CopilotAgentTaskError):
    """A mutation was denied by a local control."""

    def __init__(self, message: str, result: Mapping[str, Any] | None = None):
        super().__init__(message)
        self.result = dict(result or {})


AgentTaskPolicyError = PolicyViolation


class BranchValidationError(PolicyViolation):
    """The requested base or head branch is invalid or forbidden."""


class TokenPolicyError(PolicyViolation):
    """The credential is missing or unsafe for agent task mutations."""


class AtomicLockError(CopilotAgentTaskError):
    """The operation could not acquire its local mutation lock."""


class DedupStateError(CopilotAgentTaskError):
    """Deduplication state could not be read or written."""


class GitHubAPIError(CopilotAgentTaskError):
    """A GitHub REST call failed or returned an invalid response."""

    def __init__(
        self,
        message: str,
        status: int | None = None,
        payload: Any = None,
    ):
        super().__init__(message)
        self.status = status
        self.payload = payload


@dataclass(frozen=True, slots=True)
class HTTPResponse:
    """Normalized HTTP response passed back by all transports."""

    status: int
    payload: Any
    headers: Mapping[str, str] | None = None


@dataclass(frozen=True, slots=True)
class UrllibResult:
    """Compatibility name for an HTTP response."""

    status: int
    payload: Any
    headers: Mapping[str, str] | None = None


class HTTPTransport(Protocol):
    """Minimal transport interface: request(method, url, headers, body, timeout)."""

    def request(
        self,
        method: str,
        url: str,
        headers: Mapping[str, str],
        body: bytes | None = None,
        timeout: int = 30,
    ) -> HTTPResponse: ...


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _atomic_write_text(path: Path, text: str, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".tmp-", dir=path.parent)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.close(fd)
        except OSError:
            pass
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def atomic_write_json(path: Path | str, payload: Mapping[str, Any]) -> None:
    """Atomically replace a JSON file in a way that preserves 0600 permissions."""

    target = Path(path)
    _atomic_write_text(target, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def append_action_log(path: Path | str, record: Mapping[str, Any]) -> None:
    """Append one JSON line under an exclusive local mutation lock when possible."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, sort_keys=True, ensure_ascii=True) + "\n"
    flags = os.O_APPEND | os.O_CREAT | os.O_WRONLY
    fd = os.open(target, flags, 0o600)
    try:
        os.write(fd, line.encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)


@contextmanager
def atomic_lock(lock_path: Path | str, timeout: float = 5.0):
    """Acquire an inter-process non-blocking lock with a bounded wait."""

    target = Path(lock_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    handle = target.open("a+", encoding="utf-8")
    deadline = time.monotonic() + max(0.0, timeout)
    acquired = False

    try:
        while True:
            try:
                try:
                    import fcntl

                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except ImportError:  # pragma: no cover - only non-POSIX hosts
                    pass
                except BlockingIOError:
                    raise
                acquired = True
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise AtomicLockError(f"could not acquire local lock: {target}")
                time.sleep(0.05)
        yield
    finally:
        if acquired:
            try:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            except (ImportError, OSError):
                pass
        handle.close()


AtomicTaskLock = atomic_lock


def _clean_owner_repo(owner: str, repo: str) -> tuple[str, str]:
    owner = str(owner or "").strip()
    repo = str(repo or "").strip()
    if not _GITHUB_OWNER_RE.fullmatch(owner):
        raise ValueError(f"invalid GitHub owner: {owner!r}")
    if not _REPO_NAME_RE.fullmatch(repo):
        raise ValueError(f"invalid GitHub repository name: {repo!r}")
    return owner, repo


def validate_owner_repo(owner: str, repo: str) -> bool:
    try:
        _clean_owner_repo(owner, repo)
        return True
    except (TypeError, ValueError):
        return False


def validate_branch_name(branch: str) -> bool:
    """Return whether a branch name is syntactically valid for GitHub."""

    if not isinstance(branch, str):
        return False
    branch = branch.strip()
    if not branch or branch != branch.strip():
        return False
    if branch in {"@", "HEAD"} or branch.startswith("."):
        return False
    if branch.startswith("-") or branch.startswith("/") or branch.endswith("/"):
        return False
    if branch.endswith(".") or branch.endswith(".lock"):
        return False
    if "//" in branch or ".." in branch or "@{" in branch:
        return False
    if any(part.endswith(".lock") for part in branch.split("/")):
        return False
    if _BRANCH_FORBIDDEN_CHARS.search(branch):
        return False
    if "\r" in branch or "\n" in branch:
        return False
    return len(branch) <= 255


validate_base_branch = validate_branch_name
validate_head_branch = validate_branch_name


def validate_branch_pair(
    base_branch: str = "",
    head_branch: str = "",
    promotion: bool = False,
) -> bool:
    """Validate the optional base/head pair and the 0D_base_ launch rule."""

    if base_branch:
        if not validate_branch_name(base_branch):
            return False
    if head_branch:
        if not validate_branch_name(head_branch):
            return False

    base = str(base_branch or "").strip()
    head = str(head_branch or "").strip()

    if promotion:
        return base == "main" and head == "0D_base_"

    if base == "0D_base_":
        return head.startswith("copilot/session-") or head.startswith("copilot/sub-pr-")

    if head == "0D_base_":
        return False

    return True


def validate_branches(
    base_branch: str = "",
    head_branch: str = "",
    promotion: bool = False,
) -> None:
    if base_branch and not validate_branch_name(base_branch):
        raise BranchValidationError(f"invalid base branch: {base_branch!r}")
    if head_branch and not validate_branch_name(head_branch):
        raise BranchValidationError(f"invalid head branch: {head_branch!r}")
    if not validate_branch_pair(base_branch, head_branch, promotion):
        raise BranchValidationError(
            "direct 0D_base_ launches are prohibited; use an explicit 0D_base_ to main promotion"
        )


def validate_base_head(
    base_branch: str = "",
    head_branch: str = "",
    promotion: bool = False,
) -> dict[str, Any]:
    try:
        validate_branches(base_branch, head_branch, promotion)
        return {"passed": True, "base_branch": base_branch, "head_branch": head_branch}
    except BranchValidationError as exc:
        return {"passed": False, "reason": str(exc)}


def validate_launch_key(launch_key: str) -> bool:
    return bool(isinstance(launch_key, str) and _LAUNCH_KEY_RE.fullmatch(launch_key.strip()))


def resolve_custom_agent_slug(agent: str) -> str:
    """Normalize a custom-agent name and return the hosted slug or raise."""

    if not isinstance(agent, str) or not agent.strip():
        raise PolicyViolation("custom_agent is required")

    normalized = agent.strip().lower().replace(" ", "-").replace("_", "-")
    normalized = normalized.removesuffix(".agent.md").removesuffix(".agent")
    normalized = normalized.removesuffix(".md")

    hosted = {
        "agent-orchestrator",
        "ci-failure-resolution-agent",
        "security-alert-verification-agent",
        "unified-documentation-agent",
        "ci-failure-diagnostician",
        "ci-pattern-guardian",
        "workflow-compliance-guardian",
        "codebase-health-guardian",
        "branch-divergence-resolution-agent",
        "session-wrapup-autofix-agent",
        "security-audit-agent",
        "test-failure-analyzer-agent",
        "cdx-archive-lifecycle",
    }
    if normalized not in hosted:
        raise PolicyViolation(f"unknown or unverified custom agent: {agent}")
    return normalized


def _launch_key_payload(
    *,
    owner: str,
    repo: str,
    prompt: str,
    base_branch: str,
    head_branch: str,
    issue_number: int | None,
    assignees: Sequence[str],
) -> Mapping[str, Any]:
    payload: dict[str, Any] = {
        "owner": owner,
        "repo": repo,
        "prompt": prompt,
        "base_branch": base_branch,
        "head_branch": head_branch,
        "issue_number": issue_number,
        "assignees": list(assignees),
    }
    return payload


def generate_launch_key(
    prompt: str,
    *,
    owner: str = DEFAULT_REPO_OWNER,
    repo: str = DEFAULT_REPO_NAME,
    base_branch: str = "",
    head_branch: str = "",
    head_sha: str = "",
    workflow_file: str = "",
    failure_signature: str = "",
    custom_agent: str = "",
    objective: str = "",
    objective_hash: str = "",
    prompt_hash: str = "",
    issue_number: int | None = None,
    assignees: Sequence[str] | None = None,
) -> str:
    """Create a deterministic 40-character SHA-1 launch key."""

    if isinstance(prompt, Mapping):
        source = dict(prompt)
    else:
        source = dict(
            _launch_key_payload(
                owner=str(owner or ""),
                repo=str(repo or ""),
                prompt=str(prompt or "").strip(),
                base_branch=str(base_branch or "").strip(),
                head_branch=str(head_branch or "").strip(),
                issue_number=issue_number,
                assignees=tuple(assignees or []),
            )
        )
        for key, value in (
            ("head_sha", head_sha),
            ("workflow_file", workflow_file),
            ("failure_signature", failure_signature),
            ("custom_agent", custom_agent),
            ("objective", objective),
            ("objective_hash", objective_hash),
            ("prompt_hash", prompt_hash),
        ):
            if str(value or "").strip():
                source[key] = str(value).strip()
    canonical = json.dumps(source, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha1(canonical.encode("utf-8")).hexdigest()


make_launch_key = generate_launch_key
create_launch_key = generate_launch_key


def normalize_assignees(assignees: Iterable[str] | str | None) -> list[str]:
    if assignees is None:
        return []
    if isinstance(assignees, str):
        values: Iterable[str] = assignees.split(",")
    else:
        values = assignees
    return list(
        dict.fromkeys(
            str(value).strip().lstrip("@") for value in values if str(value).strip().lstrip("@")
        )
    )


def build_agent_assignment_payload(
    *,
    launch_key: str = "",
    prompt: str = "",
    base_branch: str = "",
    head_branch: str = "",
    issue_number: int | None = None,
    assignees: Iterable[str] | str | None = None,
    probe_agent_tasks: bool = False,
) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    if launch_key:
        payload["launch_key"] = launch_key
    if prompt:
        payload["prompt"] = prompt
    if base_branch:
        payload["base_branch"] = base_branch
    if head_branch:
        payload["head_branch"] = head_branch
    if issue_number is not None:
        payload["issue_number"] = issue_number
    normalized = normalize_assignees(assignees)
    if normalized:
        payload["assignees"] = normalized
    return payload


def build_issue_assignment_payload(
    assignees: Iterable[str] | str | None,
    agent_assignment: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    normalized = normalize_assignees(assignees)
    if not normalized:
        raise PolicyViolation("at least one assignee is required")
    payload: dict[str, Any] = {"assignees": normalized}
    if agent_assignment:
        payload["agent_assignment"] = {
            key: value for key, value in agent_assignment.items() if value not in (None, "", [], {})
        }
    return payload


def build_create_payload(
    prompt: str = "",
    *,
    problem_statement: str = "",
    base_branch: str = "",
    head_branch: str = "",
    base_ref: str = "",
    head_ref: str = "",
    launch_key: str = "",
    issue_number: int | None = None,
    assignees: Iterable[str] | str | None = None,
    agent_assignment: Mapping[str, Any] | None = None,
    custom_agent: str = "",
    model: str = "",
    custom_instructions: str = "",
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the create body while omitting every empty optional field."""

    prompt_value = str(prompt or problem_statement or "").strip()
    if not prompt_value:
        raise PolicyViolation("create prompt/problem_statement is required")

    payload: dict[str, Any] = {"prompt": prompt_value}

    base_value = str(base_ref or base_branch or "").strip()
    head_value = str(head_ref or head_branch or "").strip()
    if base_value:
        payload["base_ref"] = base_value
    if head_value:
        payload["head_ref"] = head_value

    launch_value = str(launch_key or "").strip()
    if launch_value:
        if not validate_launch_key(launch_value):
            raise PolicyViolation("launch_key must be exactly 40 hexadecimal characters")
        payload["launch_key"] = launch_value.lower()

    normalized_assignees = normalize_assignees(assignees)
    if normalized_assignees:
        payload["assignees"] = normalized_assignees
    if issue_number is not None:
        if isinstance(issue_number, bool) or int(issue_number) <= 0:
            raise PolicyViolation("issue_number must be a positive integer")
        payload["issue_number"] = int(issue_number)
    if agent_assignment:
        payload["agent_assignment"] = {
            key: value for key, value in agent_assignment.items() if value not in (None, "", [], {})
        }
    if custom_agent:
        payload["custom_agent"] = str(custom_agent).strip()
    if model:
        payload["model"] = str(model).strip()
    if custom_instructions:
        payload["custom_instructions"] = str(custom_instructions).strip()
    if extra:
        for key, value in extra.items():
            if value not in (None, "", [], {}):
                payload[str(key)] = value

    return payload


def is_placeholder_credential(token: str) -> bool:
    value = str(token or "").strip()
    if not value:
        return True
    lowered = value.lower()
    placeholder_tokens = {
        "token",
        "github_token",
        "your_token",
        "your_github_token",
        "changeme",
        "change_me",
        "replace_me",
        "dummy",
        "example",
        "test",
        "test-token",
        "test_token",
        "placeholder",
        "not-a-token",
        "<github-token>",
        "${github_token}",
    }
    if lowered in placeholder_tokens:
        return True
    if re.search(r"placeholder|dummy|example|change.?me|replace.?me|your[_ -]?token|xxx+", lowered):
        return True
    if re.fullmatch(r"(?:gh[pousr]_|github_pat_)x+", lowered):
        return True
    if re.fullmatch(r"0+", value):
        return True
    if len(value) >= 8 and len(set(value)) == 1:
        return True
    return False


def is_installation_token(token: str) -> bool:
    return str(token or "").strip().lower().startswith("ghs_")


def validate_credential(token: str) -> tuple[bool, str]:
    value = str(token or "").strip()
    if not value:
        return False, "missing GitHub credential"
    if is_installation_token(value):
        return False, "GitHub App installation token ghs_ is not accepted"
    if is_placeholder_credential(value):
        return False, "placeholder or invalid GitHub credential"
    return True, "credential accepted"


def resolve_token(
    explicit: str | None = None,
    environ: Mapping[str, str] | None = None,
) -> tuple[str, str]:
    """Resolve the first acceptable credential and return (token, source)."""

    env = os.environ if environ is None else environ
    if explicit:
        value = str(explicit).strip()
        source = "explicit"
    else:
        value = ""
        source = ""
        for name in (
            "COPILOT_AGENT_TASK_TOKEN",
            "CODEX_MASTER_KEY",
            "CODEX_BACKUP_KEY",
            "CODEX_ADMIN_KEY",
            "AGENT_GITHUB_TOKEN",
            "GITHUB_COPILOT_API_TOKEN",
            "COPILOT_GITHUB_TOKEN",
            "GH_TOKEN",
            "GITHUB_TOKEN",
        ):
            candidate = str(env.get(name, "") or "").strip()
            if candidate:
                value = candidate
                source = name
                break

    valid, reason = validate_credential(value)
    if not valid:
        raise TokenPolicyError(reason)
    return value, source


get_token = resolve_token


def _env_value(environ: Mapping[str, str] | None, name: str) -> str:
    env = os.environ if environ is None else environ
    return str(env.get(name, "") or "").strip()


def kill_switch_engaged(environ: Mapping[str, str] | None = None) -> bool:
    env = os.environ if environ is None else environ
    for name in ("AGENT_KILL_SWITCH", "COPILOT_AGENT_KILL_SWITCH", "CODEX_AGENT_KILL_SWITCH"):
        value = str(env.get(name, "") or "").strip().lower()
        if value in {"1", "true", "yes", "on", "engaged", "halt"}:
            return True
    return False


def is_autonomous_actions_enabled(
    environ: Mapping[str, str] | None = None,
    repo_root: Path | str | None = None,
) -> bool:
    env = os.environ if environ is None else environ
    for name in ("AUTONOMOUS_ACTIONS_ENABLED", "COPILOT_AUTONOMOUS_ACTIONS_ENABLED"):
        if name in env:
            value = str(env.get(name, "") or "").strip().lower()
            return value in {"1", "true", "yes", "on", "enabled"}

    root = Path(repo_root) if repo_root is not None else Path.cwd()
    config = root / ".codex" / "autonomous_agent.yaml"
    if config.is_file():
        try:
            text = config.read_text(encoding="utf-8")
            match = re.search(r"(?m)^\s*autonomous_actions_enabled:\s*(true|false|1|0)", text)
            if match:
                return match.group(1).lower() in {"true", "1"}
        except OSError:
            return False
    return False


def is_d_tier_enabled(environ: Mapping[str, str] | None = None) -> bool:
    env = os.environ if environ is None else environ
    for name in (
        "COPILOT_AGENT_MAX_AUTONOMY_LEVEL",
        "AUTONOMY_LEVEL",
        "AGENT_AUTONOMY_LEVEL",
        "COPILOT_AUTONOMY_LEVEL",
    ):
        value = str(env.get(name, "") or "").strip().upper().replace("-", "_")
        if value in {"D", "D_TIER", "D_CAPABLE", "DTIER", "DCAPABLE"}:
            return True
    return str(env.get("D_CAPABLE", "") or "").strip().lower() in {"1", "true", "yes", "on"}


def owner_auth_status(
    owner: str = DEFAULT_REPO_OWNER,
    actor: str = "",
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    env = os.environ if environ is None else environ
    resolved_actor = str(actor or "").strip()
    if not resolved_actor:
        for name in ("GITHUB_ACTOR", "GITHUB_USER", "OWNER_LOGIN", "COPILOT_OWNER_LOGIN"):
            candidate = str(env.get(name, "") or "").strip()
            if candidate:
                resolved_actor = candidate
                break

    for name in ("OWNER_AUTHORIZED", "OWNER_APPROVAL_PROTECTED", "SINGLE_OWNER_APPROVED"):
        value = str(env.get(name, "") or "").strip().lower()
        if value in {"1", "true", "yes", "on", "mbaetiong"}:
            return {
                "passed": True,
                "owner": owner,
                "actor": resolved_actor or SOLE_OWNER,
                "source": name,
            }

    passed = resolved_actor.lower().lstrip("@") == SOLE_OWNER.lower()
    return {
        "passed": passed,
        "owner": owner,
        "actor": resolved_actor,
        "source": "github_actor" if resolved_actor else "missing",
    }


def check_budget(
    tasks: Sequence[str] | str,
    *,
    repo_root: Path | str | None = None,
) -> dict[str, Any]:
    task_list = [str(tasks)] if isinstance(tasks, str) else [str(item) for item in tasks]
    if not task_list:
        task_list = ["Copilot agent task"]

    estimate: dict[str, Any]
    checkpoint: dict[str, Any]
    if session_budget_guard is not None:
        estimate = session_budget_guard.estimate_session_cost(task_list)
        checkpoint = session_budget_guard.check_checkpoint_safety()
    else:  # pragma: no cover - fallback for a stripped deployment
        estimate = {
            "total_tpu": sum(4 for _ in task_list),
            "task_count": len(task_list),
            "risk_level": "low",
        }
        checkpoint = {"safe": True, "reason": "Session budget guard unavailable; local fallback"}

    risk = str(estimate.get("risk_level", "low")).lower()
    allowed = bool(checkpoint.get("safe", True)) and risk not in {"high", "very_high"}
    reasons: list[str] = []
    if not checkpoint.get("safe", True):
        reasons.append(str(checkpoint.get("reason", "session budget checkpoint is not safe")))
    if risk in {"high", "very_high"}:
        reasons.append(f"session budget risk is {risk}")
    return {
        "passed": allowed,
        "allowed": allowed,
        "estimate": estimate,
        "checkpoint": checkpoint,
        "reasons": reasons,
    }


class DedupState:
    """Small launch-key keyed state store with atomic JSON replacement."""

    def __init__(
        self,
        state_dir: Path | str,
        path: Path | str | None = None,
    ):
        self.state_dir = Path(state_dir)
        self.path = (
            Path(path) if path is not None else self.state_dir / DEDUP_STATE_FILE.rsplit("/", 1)[-1]
        )

    def load(self) -> dict[str, Any]:
        if not self.path.is_file():
            return {"version": 1, "tasks": {}}
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("dedup state root is not an object")
            tasks = payload.get("tasks")
            if not isinstance(tasks, dict):
                payload["tasks"] = {}
            return payload
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            raise DedupStateError(f"could not read dedup state: {self.path}: {exc}") from exc

    def get(self, launch_key: str) -> dict[str, Any] | None:
        state = self.load()
        record = state["tasks"].get(str(launch_key).lower())
        return dict(record) if isinstance(record, dict) else None

    def is_recent(self, launch_key: str, ttl_seconds: float = 86400.0) -> bool:
        record = self.get(launch_key)
        if not record:
            return False
        created = str(record.get("created_at") or "")
        try:
            timestamp = datetime.strptime(created, "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=timezone.utc
            )
            age = datetime.now(timezone.utc).timestamp() - timestamp.timestamp()
            return 0 <= age < ttl_seconds
        except (TypeError, ValueError):
            return True

    lookup = get

    def put(self, launch_key: str, record: Mapping[str, Any]) -> dict[str, Any]:
        launch_key = str(launch_key).strip().lower()
        if not validate_launch_key(launch_key):
            raise DedupStateError("launch key must be exactly 40 hexadecimal characters")
        state = self.load()
        state["tasks"][launch_key] = dict(record)
        state["updated_at"] = utc_now()
        atomic_write_json(self.path, state)
        return dict(record)

    save = put


class HandoffState:
    """Atomic latest-state writer for handoff continuity."""

    def __init__(
        self,
        state_dir: Path | str,
        path: Path | str | None = None,
    ):
        self.state_dir = Path(state_dir)
        self.path = (
            Path(path)
            if path is not None
            else self.state_dir / HANDOFF_STATE_FILE.rsplit("/", 1)[-1]
        )

    def load(self) -> dict[str, Any]:
        if not self.path.is_file():
            return {"version": 1, "history": []}
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            return payload if isinstance(payload, dict) else {"version": 1, "history": []}
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            return {"version": 1, "history": []}

    def update(self, record: Mapping[str, Any]) -> dict[str, Any]:
        state = self.load()
        state.update(dict(record))
        state["version"] = state.get("version", 1)
        state["updated_at"] = utc_now()
        history = state.setdefault("history", [])
        if not isinstance(history, list):
            history = []
            state["history"] = history
        history.append(dict(record, timestamp=utc_now()))
        history[:] = history[-100:]
        atomic_write_json(self.path, state)
        return dict(state)


class UrllibTransport:
    """Stdlib urllib transport with an injectable opener."""

    def __init__(
        self,
        opener: Callable[..., Any] | None = None,
        timeout: int = 30,
        max_response_bytes: int = 1024 * 1024,
    ):
        self.opener = opener or urllib.request.urlopen
        self.timeout = timeout
        self.max_response_bytes = max_response_bytes

    def request(
        self,
        method: str,
        url: str,
        headers: Mapping[str, str],
        body: bytes | None = None,
        timeout: int | None = None,
    ) -> HTTPResponse:
        request = urllib.request.Request(
            url,
            data=body,
            headers=dict(headers),
            method=method.upper(),
        )
        try:
            opened = self.opener(request, timeout=timeout or self.timeout)
        except TypeError:
            opened = self.opener(request, timeout or self.timeout)

        try:
            raw = opened.read(self.max_response_bytes + 1)
            status = int(getattr(opened, "status", getattr(opened, "code", 200)))
            response_headers = dict(getattr(opened, "headers", {}) or {})
        finally:
            close = getattr(opened, "close", None)
            if callable(close):
                close()

        if len(raw) > self.max_response_bytes:
            raise GitHubAPIError("GitHub API response exceeds size limit")
        payload = _decode_payload(raw)
        return HTTPResponse(status=status, payload=payload, headers=response_headers)

    open = request


def _decode_payload(raw: bytes) -> Any:
    if not raw:
        return {}
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return raw.decode("utf-8", errors="replace")


def _normalize_response(response: Any) -> HTTPResponse:
    if isinstance(response, HTTPResponse):
        return response
    if isinstance(response, UrllibResult):
        return HTTPResponse(response.status, response.payload, response.headers)
    if isinstance(response, tuple):
        if len(response) == 2:
            return HTTPResponse(int(response[0]), response[1], {})
        if len(response) >= 3:
            return HTTPResponse(int(response[0]), response[1], response[2] or {})
    if isinstance(response, Mapping):
        status = int(response.get("status", response.get("status_code", 200)))
        payload = response.get("payload", response.get("data", response))
        headers = response.get("headers", {})
        return HTTPResponse(status, payload, headers if isinstance(headers, Mapping) else {})

    status = int(getattr(response, "status", getattr(response, "status_code", 200)))
    payload = getattr(response, "payload", getattr(response, "data", None))
    if payload is None:
        payload = getattr(response, "json", None)
        if callable(payload):
            try:
                payload = payload()
            except (AttributeError, TypeError, ValueError):
                payload = None
    headers = getattr(response, "headers", {})
    return HTTPResponse(status, payload if payload is not None else {}, headers)


class CopilotAgentTaskClient:
    """Typed REST client for GitHub Copilot agent tasks."""

    def __init__(
        self,
        owner: str = DEFAULT_REPO_OWNER,
        repo: str = DEFAULT_REPO_NAME,
        *,
        token: str | None = None,
        environ: Mapping[str, str] | None = None,
        transport: HTTPTransport | Callable[..., Any] | None = None,
        opener: Callable[..., Any] | None = None,
        repo_root: Path | str | None = None,
        state_dir: Path | str | None = None,
        timeout: int = 30,
        sleep: Callable[[float], None] = time.sleep,
        now: Callable[[], float] = time.monotonic,
    ):
        if "/" in str(repo):
            owner, repo = str(repo).split("/", 1)
        self.owner, self.repo = _clean_owner_repo(owner, repo)
        self.token = str(token or "").strip()
        self.environ = os.environ if environ is None else environ
        self.repo_root = Path(repo_root) if repo_root is not None else Path.cwd()
        self.state_dir = Path(state_dir) if state_dir is not None else self.repo_root / ".codex"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.lock_path = self.state_dir / LOCK_FILE.rsplit("/", 1)[-1]
        self.dedup_path = self.state_dir / DEDUP_STATE_FILE.rsplit("/", 1)[-1]
        self.handoff_path = self.state_dir / HANDOFF_STATE_FILE.rsplit("/", 1)[-1]
        self.handoff_alias_path = self.state_dir / HANDOFF_STATE_ALIAS_FILE.rsplit("/", 1)[-1]
        self.action_log_path = self.state_dir / ACTION_LOG_FILE.rsplit("/", 1)[-1]
        self.dedup = DedupState(self.state_dir, self.dedup_path)
        self.handoff = HandoffState(self.state_dir, self.handoff_path)
        self.timeout = timeout
        self.sleep = sleep
        self.now = now

        if transport is not None:
            self.transport = transport
        elif opener is not None:
            self.transport = UrllibTransport(opener=opener, timeout=timeout)
        else:
            self.transport = UrllibTransport(timeout=timeout)

    def _headers(self, token: str) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {token}",
            "Accept": ACCEPT,
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": "codex-copilot-agent-task/1.0",
        }

    def _resolve_token(self) -> tuple[str, str]:
        return resolve_token(explicit=self.token or None, environ=self.environ)

    def _call_transport(
        self,
        method: str,
        url: str,
        headers: Mapping[str, str],
        body: bytes | None,
        timeout: int,
    ) -> HTTPResponse:
        transport = self.transport
        if hasattr(transport, "request"):
            return _normalize_response(
                transport.request(method, url, headers, body, timeout)  # type: ignore[union-attr]
            )
        if hasattr(transport, "open"):
            return _normalize_response(
                transport.open(method, url, headers, body, timeout)  # type: ignore[union-attr]
            )
        if callable(transport):
            signature = inspect.signature(transport)
            parameter_names = set(signature.parameters)
            if {"method", "url"}.issubset(parameter_names):
                kwargs: dict[str, Any] = {
                    "method": method,
                    "url": url,
                    "headers": dict(headers),
                    "body": body,
                    "timeout": timeout,
                }
                accepted = {key: value for key, value in kwargs.items() if key in parameter_names}
                if any(key in parameter_names for key in ("**kwargs", "kwarg")):
                    accepted = kwargs
                return _normalize_response(transport(**accepted))
            if "request" in parameter_names:
                request = urllib.request.Request(
                    url,
                    data=body,
                    headers=dict(headers),
                    method=method,
                )
                return _normalize_response(transport(request=request, timeout=timeout))
            return _normalize_response(transport(method, url, dict(headers), body, timeout))
        raise GitHubAPIError("unsupported HTTP transport")

    def _request(
        self,
        method: str,
        path: str,
        *,
        body: Mapping[str, Any] | None = None,
        token: str | None = None,
        query: Mapping[str, Any] | None = None,
        allow_empty_response: bool = False,
    ) -> dict[str, Any]:
        resolved_token, _source = resolve_token(
            explicit=token or self.token or None, environ=self.environ
        )
        url = f"{API_BASE}{path}"
        if query:
            filtered = {
                str(key): str(value) for key, value in query.items() if value not in (None, "")
            }
            if filtered:
                url = f"{url}?{urllib.parse.urlencode(filtered)}"
        encoded = (
            json.dumps(dict(body), sort_keys=True, separators=(",", ":")).encode("utf-8")
            if body is not None
            else None
        )
        headers = self._headers(resolved_token)
        if encoded is not None:
            headers["Content-Type"] = "application/json"

        try:
            response = self._call_transport(method.upper(), url, headers, encoded, self.timeout)
        except urllib.error.HTTPError as exc:
            raw = exc.read()
            payload = _decode_payload(raw)
            raise GitHubAPIError(
                f"GitHub REST request failed with HTTP {exc.code}",
                status=int(exc.code),
                payload=payload,
            ) from exc
        except urllib.error.URLError as exc:
            raise GitHubAPIError(f"GitHub REST request failed: {exc.reason}") from exc

        status = int(response.status)
        if status >= 400:
            raise GitHubAPIError(
                f"GitHub REST request failed with HTTP {status}",
                status=status,
                payload=response.payload,
            )
        if allow_empty_response or status in {204, 205}:
            return {}
        if isinstance(response.payload, dict):
            return response.payload
        if isinstance(response.payload, list):
            return {"items": response.payload}
        if response.payload in (None, ""):
            return {}
        if isinstance(response.payload, str):
            return {"message": response.payload}
        return {"value": response.payload}

    def _tasks_path(self, task_id: str = "") -> str:
        owner = urllib.parse.quote(self.owner, safe="")
        repo = urllib.parse.quote(self.repo, safe="")
        path = TASKS_ENDPOINT_TEMPLATE.format(owner=owner, repo=repo)
        if task_id:
            path = f"{path}/{urllib.parse.quote(str(task_id), safe='')}"
        return path

    def _issue_path(self, issue_number: int) -> str:
        owner = urllib.parse.quote(self.owner, safe="")
        repo = urllib.parse.quote(self.repo, safe="")
        return f"/repos/{owner}/{repo}/issues/{int(issue_number)}"

    def preflight(
        self,
        prompt: str = "",
        *,
        base_branch: str = "",
        head_branch: str = "",
        base_ref: str = "",
        head_ref: str = "",
        promotion: bool = False,
        launch_key: str = "",
        issue_number: int | None = None,
        assignees: Iterable[str] | str | None = None,
        actor: str = "",
        skip_budget: bool = False,
        probe_agent_tasks: bool = False,
    ) -> dict[str, Any]:
        base_value = str(base_ref or base_branch or "").strip()
        head_value = str(head_ref or head_branch or "").strip()
        branch_check = validate_base_head(base_value, head_value, promotion)

        kill_check = {
            "passed": not kill_switch_engaged(self.environ),
            "engaged": kill_switch_engaged(self.environ),
        }
        autonomous_check = {
            "passed": is_autonomous_actions_enabled(self.environ, self.repo_root),
        }
        d_tier_check = {"passed": is_d_tier_enabled(self.environ)}
        owner_check = owner_auth_status(self.owner, actor=actor, environ=self.environ)

        token_check: dict[str, Any]
        try:
            _token, token_source = self._resolve_token()
            if token_source not in {"COPILOT_AGENT_TASK_TOKEN", "explicit"}:
                token_check = {
                    "passed": False,
                    "source": token_source,
                    "reason": (
                        "Agent Tasks require COPILOT_AGENT_TASK_TOKEN or an explicitly "
                        "verified live credential; CODEX_MASTER_KEY and GITHUB_TOKEN are not sufficient"
                    ),
                }
            else:
                token_check = {"passed": True, "source": token_source}
        except TokenPolicyError as exc:
            token_check = {"passed": False, "reason": str(exc)}

        probe_check: dict[str, Any] = {"passed": True, "skipped": not probe_agent_tasks}
        if probe_agent_tasks and token_check.get("passed"):
            try:
                probe_check = self.probe_agent_task_access()
            except (GitHubAPIError, PolicyViolation, TokenPolicyError) as exc:
                probe_check = {"passed": False, "reason": str(exc)}

        budget_check = (
            {"passed": True, "skipped": True}
            if skip_budget
            else check_budget(prompt or "Copilot agent task", repo_root=self.repo_root)
        )

        launch_value = str(launch_key or "").strip().lower()
        if launch_value:
            launch_valid = validate_launch_key(launch_value)
            launch_reason = (
                "launch key accepted"
                if launch_valid
                else "launch key must be exactly 40 hexadecimal characters"
            )
        else:
            launch_value = generate_launch_key(
                prompt or "Copilot agent task",
                owner=self.owner,
                repo=self.repo,
                base_branch=base_value,
                head_branch=head_value,
                issue_number=issue_number,
                assignees=normalize_assignees(assignees),
            )
            launch_valid = True
            launch_reason = "launch key generated"
        launch_check = {"passed": launch_valid, "reason": launch_reason}

        checks = {
            "branches": branch_check,
            "kill_switch": kill_check,
            "autonomous_actions_enabled": autonomous_check,
            "d_tier": d_tier_check,
            "owner_auth": owner_check,
            "token": token_check,
            "budget": budget_check,
            "launch_key": launch_check,
            "agent_task_api_probe": probe_check,
        }

        blocked_reasons: list[str] = []
        for name, check in checks.items():
            if not check.get("passed", False):
                reason = str(check.get("reason", "") or check.get("engaged", "") or name)
                blocked_reasons.append(f"{name}: {reason}" if reason else name)

        allowed = not blocked_reasons
        result: dict[str, Any] = {
            "ok": allowed,
            "allowed": allowed,
            "operation": "preflight",
            "timestamp": utc_now(),
            "api_version": API_VERSION,
            "endpoint": self._tasks_path(),
            "launch_key": launch_value,
            "checks": checks,
            "blocked_reasons": blocked_reasons,
        }
        if not allowed:
            result["error"] = "agent task preflight denied"
        return result

    def _success(
        self, operation: str, data: Mapping[str, Any] | Any, **extra: Any
    ) -> dict[str, Any]:
        result: dict[str, Any] = {
            "ok": True,
            "operation": operation,
            "timestamp": utc_now(),
            "api_version": API_VERSION,
        }
        if isinstance(data, Mapping):
            result["data"] = dict(data)
            result.update(dict(data))
        else:
            result["data"] = data
        result.update(extra)
        return result

    def probe_agent_task_access(self) -> dict[str, Any]:
        """Best-effort live read probe for the repository Agent Tasks endpoint."""

        resolved_token, token_source = self._resolve_token()
        if token_source not in {"COPILOT_AGENT_TASK_TOKEN", "explicit"}:
            raise PolicyViolation(
                "live Agent Tasks probe requires COPILOT_AGENT_TASK_TOKEN or an explicit credential"
            )
        response = self._request(
            "GET", self._tasks_path(), token=resolved_token, query={"per_page": 1}
        )
        return {
            "passed": True,
            "token_source": token_source,
            "endpoint": self._tasks_path(),
            "response": response,
        }

    def _require_preflight(self, preflight: Mapping[str, Any]) -> None:
        if not preflight.get("allowed", False):
            raise PolicyViolation(
                "agent task preflight denied: " + "; ".join(preflight.get("blocked_reasons", [])),
                dict(preflight),
            )

    def _write_state(
        self,
        *,
        operation: str,
        launch_key: str,
        task_id: str,
        status: str,
        response: Mapping[str, Any] | None = None,
        extra: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        record: dict[str, Any] = {
            "operation": operation,
            "launch_key": launch_key,
            "task_id": task_id,
            "status": status,
            "owner": self.owner,
            "repo": self.repo,
            "timestamp": utc_now(),
        }
        if response:
            record["response"] = dict(response)
        if extra:
            record.update(dict(extra))

        atomic_write_json(self.handoff_path, record)
        atomic_write_json(self.handoff_alias_path, record)

        tracking_path = self.state_dir / "handoff_tracking.json"
        try:
            tracking = (
                json.loads(tracking_path.read_text(encoding="utf-8"))
                if tracking_path.is_file()
                else {"version": 1, "handoffs": []}
            )
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            tracking = {"version": 1, "handoffs": []}
        if not isinstance(tracking, dict):
            tracking = {"version": 1, "handoffs": []}
        handoffs = tracking.setdefault("handoffs", [])
        if not isinstance(handoffs, list):
            handoffs = []
            tracking["handoffs"] = handoffs
        handoffs.append(dict(record, timestamp=utc_now()))
        handoffs[:] = handoffs[-100:]
        tracking["updated_at"] = utc_now()
        atomic_write_json(tracking_path, tracking)

        append_action_log(
            self.action_log_path,
            {
                "timestamp": utc_now(),
                "action": operation,
                "launch_key": launch_key,
                "task_id": task_id,
                "status": status,
                "path": (
                    str(self.handoff_path.relative_to(self.repo_root))
                    if self.handoff_path.is_relative_to(self.repo_root)
                    else str(self.handoff_path)
                ),
            },
        )
        return record

    def create(
        self,
        prompt: str = "",
        *,
        problem_statement: str = "",
        base_branch: str = "",
        head_branch: str = "",
        base_ref: str = "",
        head_ref: str = "",
        launch_key: str = "",
        promotion: bool = False,
        issue_number: int | None = None,
        assignees: Iterable[str] | str | None = None,
        custom_agent: str = "",
        model: str = "",
        custom_instructions: str = "",
        extra: Mapping[str, Any] | None = None,
        actor: str = "",
        skip_budget: bool = False,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        prompt_value = str(prompt or problem_statement or "").strip()
        base_value = str(base_ref or base_branch or "").strip()
        head_value = str(head_ref or head_branch or "").strip()

        with atomic_lock(self.lock_path):
            preflight = self.preflight(
                prompt_value,
                base_branch=base_value,
                head_branch=head_value,
                promotion=promotion,
                launch_key=launch_key,
                issue_number=issue_number,
                assignees=assignees,
                actor=actor,
                skip_budget=skip_budget,
            )
            self._require_preflight(preflight)

            launch_value = str(preflight["launch_key"]).lower()
            existing = self.dedup.get(launch_value)
            if existing and self.dedup.is_recent(launch_value):
                task_id = str(existing.get("task_id") or existing.get("id") or "")
                record = self._write_state(
                    operation="create_deduplicated",
                    launch_key=launch_value,
                    task_id=task_id,
                    status=str(existing.get("status") or "deduplicated"),
                    response=existing,
                    extra={"deduplicated": True},
                )
                return self._success(
                    "create",
                    existing,
                    deduplicated=True,
                    launch_key=launch_value,
                    handoff=record,
                )

            if custom_agent:
                custom_agent = resolve_custom_agent_slug(custom_agent)

            normalized_assignees = normalize_assignees(assignees)
            agent_assignment = build_agent_assignment_payload(
                launch_key=launch_value,
                prompt=prompt_value,
                base_branch=base_value,
                head_branch=head_value,
                issue_number=issue_number,
                assignees=normalized_assignees,
            )

            payload = build_create_payload(
                prompt_value,
                base_ref=base_value,
                head_ref=head_value,
                launch_key=launch_value,
                issue_number=issue_number,
                assignees=normalized_assignees,
                agent_assignment=agent_assignment,
                custom_agent=custom_agent,
                model=model,
                custom_instructions=custom_instructions,
                extra=extra,
            )

            if dry_run:
                record = self._write_state(
                    operation="create_dry_run",
                    launch_key=launch_value,
                    task_id="",
                    status="dry_run",
                    extra={"payload": payload, "dry_run": True},
                )
                return self._success(
                    "create",
                    payload,
                    deduplicated=False,
                    launch_key=launch_value,
                    dry_run=True,
                    handoff=record,
                )

            response = self._request("POST", self._tasks_path(), body=payload)
            task_id = str(
                response.get("task_id")
                or response.get("id")
                or response.get("number")
                or response.get("agent_task_id")
                or ""
            )
            dedup_record = dict(response)
            dedup_record.update(
                {
                    "launch_key": launch_value,
                    "task_id": task_id,
                    "status": str(response.get("status") or "created"),
                    "created_at": utc_now(),
                }
            )
            self.dedup.put(launch_value, dedup_record)
            handoff = self._write_state(
                operation="create",
                launch_key=launch_value,
                task_id=task_id,
                status=str(dedup_record["status"]),
                response=response,
                extra={"deduplicated": False},
            )
            return self._success(
                "create",
                response,
                deduplicated=False,
                launch_key=launch_value,
                task_id=task_id,
                handoff=handoff,
            )

    create_task = create

    def view(self, task_id: str) -> dict[str, Any]:
        if not str(task_id or "").strip():
            raise PolicyViolation("task_id is required")
        response = self._request("GET", self._tasks_path(str(task_id).strip()))
        return self._success("view", response, task_id=str(task_id).strip())

    view_task = view

    def list(
        self,
        *,
        status: str = "",
        state: str = "",
        page: int = 1,
        per_page: int = 100,
    ) -> dict[str, Any]:
        if page < 1:
            raise PolicyViolation("page must be at least 1")
        if per_page < 1 or per_page > 100:
            raise PolicyViolation("per_page must be between 1 and 100")
        query: dict[str, Any] = {
            "status": status,
            "state": state,
        }
        if page != 1:
            query["page"] = page
        if per_page != 100:
            query["per_page"] = per_page
        response = self._request("GET", self._tasks_path(), query=query)
        return self._success("list", response)

    list_tasks = list

    def continue_task(
        self,
        task_id: str,
        prompt: str = "",
        *,
        message: str = "",
        launch_key: str = "",
        actor: str = "",
        skip_budget: bool = False,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        task_id = str(task_id or "").strip()
        if not task_id:
            raise PolicyViolation("task_id is required")
        prompt_value = str(prompt or message or "").strip()

        with atomic_lock(self.lock_path):
            preflight = self.preflight(
                prompt_value,
                launch_key=launch_key,
                actor=actor,
                skip_budget=skip_budget,
            )
            self._require_preflight(preflight)
            launch_value = str(preflight["launch_key"]).lower()
            payload = {
                key: value
                for key, value in {"prompt": prompt_value, "message": message}.items()
                if value
            }

            if dry_run:
                handoff = self._write_state(
                    operation="continue_dry_run",
                    launch_key=launch_value,
                    task_id=task_id,
                    status="dry_run",
                    extra={"payload": payload, "dry_run": True},
                )
                return self._success(
                    "continue",
                    payload,
                    task_id=task_id,
                    dry_run=True,
                    launch_key=launch_value,
                    handoff=handoff,
                )

            response = self._request(
                "POST",
                f"{self._tasks_path(task_id)}/continue",
                body=payload,
            )
            handoff = self._write_state(
                operation="continue",
                launch_key=launch_value,
                task_id=task_id,
                status=str(response.get("status") or "continued"),
                response=response,
            )
            return self._success(
                "continue",
                response,
                task_id=task_id,
                launch_key=launch_value,
                handoff=handoff,
            )

    def cancel(
        self,
        task_id: str,
        *,
        launch_key: str = "",
        actor: str = "",
        skip_budget: bool = False,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        task_id = str(task_id or "").strip()
        if not task_id:
            raise PolicyViolation("task_id is required")

        with atomic_lock(self.lock_path):
            preflight = self.preflight(
                "Cancel Copilot agent task",
                launch_key=launch_key,
                actor=actor,
                skip_budget=skip_budget,
            )
            self._require_preflight(preflight)
            launch_value = str(preflight["launch_key"]).lower()

            if dry_run:
                handoff = self._write_state(
                    operation="cancel_dry_run",
                    launch_key=launch_value,
                    task_id=task_id,
                    status="dry_run",
                    extra={"dry_run": True},
                )
                return self._success(
                    "cancel",
                    {},
                    task_id=task_id,
                    dry_run=True,
                    launch_key=launch_value,
                    handoff=handoff,
                )

            response = self._request(
                "POST",
                f"{self._tasks_path(task_id)}/cancel",
                body={},
            )
            handoff = self._write_state(
                operation="cancel",
                launch_key=launch_value,
                task_id=task_id,
                status=str(response.get("status") or "cancelled"),
                response=response,
            )
            return self._success(
                "cancel",
                response,
                task_id=task_id,
                launch_key=launch_value,
                handoff=handoff,
            )

    cancel_task = cancel

    def assign(
        self,
        issue_number: int,
        assignees: Iterable[str] | str | None,
        *,
        prompt: str = "",
        base_branch: str = "",
        head_branch: str = "",
        launch_key: str = "",
        actor: str = "",
        skip_budget: bool = False,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        if isinstance(issue_number, bool):
            raise PolicyViolation("issue_number must be a positive integer")
        issue_number = int(issue_number)
        if issue_number <= 0:
            raise PolicyViolation("issue_number must be a positive integer")

        normalized_assignees = normalize_assignees(assignees)
        if not normalized_assignees:
            raise PolicyViolation("at least one assignee is required")

        with atomic_lock(self.lock_path):
            preflight = self.preflight(
                prompt or "Assign Copilot coding agent task",
                base_branch=base_branch,
                head_branch=head_branch,
                launch_key=launch_key,
                issue_number=issue_number,
                assignees=normalized_assignees,
                actor=actor,
                skip_budget=skip_budget,
            )
            self._require_preflight(preflight)
            launch_value = str(preflight["launch_key"]).lower()
            agent_assignment = build_agent_assignment_payload(
                launch_key=launch_value,
                prompt=prompt,
                base_branch=base_branch,
                head_branch=head_branch,
                issue_number=issue_number,
                assignees=normalized_assignees,
            )
            payload = build_issue_assignment_payload(normalized_assignees, agent_assignment)

            if dry_run:
                handoff = self._write_state(
                    operation="assign_dry_run",
                    launch_key=launch_value,
                    task_id=str(issue_number),
                    status="dry_run",
                    extra={"payload": payload, "issue_number": issue_number, "dry_run": True},
                )
                return self._success(
                    "assign",
                    payload,
                    issue_number=issue_number,
                    assignees=normalized_assignees,
                    dry_run=True,
                    launch_key=launch_value,
                    handoff=handoff,
                )

            response = self._request(
                "POST",
                f"{self._issue_path(issue_number)}/assignees",
                body=payload,
            )
            handoff = self._write_state(
                operation="assign",
                launch_key=launch_value,
                task_id=str(issue_number),
                status=str(response.get("state") or "assigned"),
                response=response,
                extra={"issue_number": issue_number, "assignees": normalized_assignees},
            )
            return self._success(
                "assign",
                response,
                issue_number=issue_number,
                assignees=normalized_assignees,
                launch_key=launch_value,
                handoff=handoff,
            )

    assign_issue = assign

    def poll(
        self,
        task_id: str,
        *,
        timeout: float = 300.0,
        interval: float = 5.0,
        terminal_statuses: Iterable[str] | None = None,
    ) -> dict[str, Any]:
        task_id = str(task_id or "").strip()
        if not task_id:
            raise PolicyViolation("task_id is required")

        deadline = self.now() + max(0.0, timeout)
        statuses = TERMINAL_STATUSES
        if terminal_statuses:
            statuses = frozenset(str(value).lower() for value in terminal_statuses)

        observations: list[dict[str, Any]] = []
        while True:
            result = self.view(task_id)
            payload = result.get("data", result)
            status = str(payload.get("status") or payload.get("state") or "unknown")
            observations.append({"timestamp": utc_now(), "status": status.lower()})
            if status.lower() in statuses:
                launch_key = str(payload.get("launch_key") or "")
                if launch_key:
                    self._write_state(
                        operation="poll",
                        launch_key=launch_key,
                        task_id=task_id,
                        status=status.lower(),
                        response=payload,
                    )
                result["observations"] = observations
                return result

            if self.now() >= deadline:
                raise GitHubAPIError(
                    f"poll timeout reached for task {task_id}",
                    payload={"status": status, "observations": observations},
                )
            self.sleep(max(0.0, interval))


# Compatibility aliases.
AgentTaskClient = CopilotAgentTaskClient
CopilotAgentTask = CopilotAgentTaskClient


def parse_repo(repo: str | None = None) -> tuple[str, str]:
    value = str(repo or os.environ.get("GITHUB_REPOSITORY") or "Aries-Serpent/_codex_").strip()
    if "/" not in value:
        raise ValueError("repository must use owner/repo format")
    owner, name = value.split("/", 1)
    return _clean_owner_repo(owner, name)


def preflight(
    prompt: str = "",
    *,
    owner: str = DEFAULT_REPO_OWNER,
    repo: str = DEFAULT_REPO_NAME,
    token: str | None = None,
    environ: Mapping[str, str] | None = None,
    transport: HTTPTransport | Callable[..., Any] | None = None,
    repo_root: Path | str | None = None,
    state_dir: Path | str | None = None,
    base_branch: str = "",
    head_branch: str = "",
    promotion: bool = False,
    launch_key: str = "",
    issue_number: int | None = None,
    assignees: Iterable[str] | str | None = None,
    probe_agent_tasks: bool = False,
) -> dict[str, Any]:
    client = CopilotAgentTaskClient(
        owner,
        repo,
        token=token,
        environ=environ,
        transport=transport,
        repo_root=repo_root,
        state_dir=state_dir,
    )
    return client.preflight(
        prompt,
        base_branch=base_branch,
        head_branch=head_branch,
        promotion=promotion,
        launch_key=launch_key,
        issue_number=issue_number,
        assignees=assignees,
        probe_agent_tasks=probe_agent_tasks,
    )


def create_agent_task(*args: Any, **kwargs: Any) -> dict[str, Any]:
    owner = kwargs.pop("owner", DEFAULT_REPO_OWNER)
    repo = kwargs.pop("repo", DEFAULT_REPO_NAME)
    token = kwargs.pop("token", None)
    environ = kwargs.pop("environ", None)
    transport = kwargs.pop("transport", None)
    repo_root = kwargs.pop("repo_root", None)
    state_dir = kwargs.pop("state_dir", None)
    client = CopilotAgentTaskClient(
        owner,
        repo,
        token=token,
        environ=environ,
        transport=transport,
        repo_root=repo_root,
        state_dir=state_dir,
    )
    if args:
        kwargs.setdefault("prompt", args[0])
    return client.create(**kwargs)


def get_agent_task(task_id: str, *args: Any, **kwargs: Any) -> dict[str, Any]:
    owner = kwargs.pop("owner", DEFAULT_REPO_OWNER)
    repo = kwargs.pop("repo", DEFAULT_REPO_NAME)
    token = kwargs.pop("token", None)
    environ = kwargs.pop("environ", None)
    transport = kwargs.pop("transport", None)
    repo_root = kwargs.pop("repo_root", None)
    state_dir = kwargs.pop("state_dir", None)
    client = CopilotAgentTaskClient(
        owner,
        repo,
        token=token,
        environ=environ,
        transport=transport,
        repo_root=repo_root,
        state_dir=state_dir,
    )
    return client.view(task_id)


def list_agent_tasks(*args: Any, **kwargs: Any) -> dict[str, Any]:
    owner = kwargs.pop("owner", DEFAULT_REPO_OWNER)
    repo = kwargs.pop("repo", DEFAULT_REPO_NAME)
    token = kwargs.pop("token", None)
    environ = kwargs.pop("environ", None)
    transport = kwargs.pop("transport", None)
    repo_root = kwargs.pop("repo_root", None)
    state_dir = kwargs.pop("state_dir", None)
    client = CopilotAgentTaskClient(
        owner,
        repo,
        token=token,
        environ=environ,
        transport=transport,
        repo_root=repo_root,
        state_dir=state_dir,
    )
    return client.list(**kwargs)


def continue_agent_task(task_id: str, *args: Any, **kwargs: Any) -> dict[str, Any]:
    owner = kwargs.pop("owner", DEFAULT_REPO_OWNER)
    repo = kwargs.pop("repo", DEFAULT_REPO_NAME)
    token = kwargs.pop("token", None)
    environ = kwargs.pop("environ", None)
    transport = kwargs.pop("transport", None)
    repo_root = kwargs.pop("repo_root", None)
    state_dir = kwargs.pop("state_dir", None)
    client = CopilotAgentTaskClient(
        owner,
        repo,
        token=token,
        environ=environ,
        transport=transport,
        repo_root=repo_root,
        state_dir=state_dir,
    )
    if args:
        kwargs.setdefault("prompt", args[0])
    return client.continue_task(task_id, **kwargs)


def cancel_agent_task(task_id: str, *args: Any, **kwargs: Any) -> dict[str, Any]:
    owner = kwargs.pop("owner", DEFAULT_REPO_OWNER)
    repo = kwargs.pop("repo", DEFAULT_REPO_NAME)
    token = kwargs.pop("token", None)
    environ = kwargs.pop("environ", None)
    transport = kwargs.pop("transport", None)
    repo_root = kwargs.pop("repo_root", None)
    state_dir = kwargs.pop("state_dir", None)
    client = CopilotAgentTaskClient(
        owner,
        repo,
        token=token,
        environ=environ,
        transport=transport,
        repo_root=repo_root,
        state_dir=state_dir,
    )
    return client.cancel(task_id, **kwargs)


def assign_issue_task(
    issue_number: int, assignees: Iterable[str] | str, *args: Any, **kwargs: Any
) -> dict[str, Any]:
    owner = kwargs.pop("owner", DEFAULT_REPO_OWNER)
    repo = kwargs.pop("repo", DEFAULT_REPO_NAME)
    token = kwargs.pop("token", None)
    environ = kwargs.pop("environ", None)
    transport = kwargs.pop("transport", None)
    repo_root = kwargs.pop("repo_root", None)
    state_dir = kwargs.pop("state_dir", None)
    client = CopilotAgentTaskClient(
        owner,
        repo,
        token=token,
        environ=environ,
        transport=transport,
        repo_root=repo_root,
        state_dir=state_dir,
    )
    return client.assign(issue_number, assignees, **kwargs)


def poll_agent_task(task_id: str, *args: Any, **kwargs: Any) -> dict[str, Any]:
    owner = kwargs.pop("owner", DEFAULT_REPO_OWNER)
    repo = kwargs.pop("repo", DEFAULT_REPO_NAME)
    token = kwargs.pop("token", None)
    environ = kwargs.pop("environ", None)
    transport = kwargs.pop("transport", None)
    repo_root = kwargs.pop("repo_root", None)
    state_dir = kwargs.pop("state_dir", None)
    client = CopilotAgentTaskClient(
        owner,
        repo,
        token=token,
        environ=environ,
        transport=transport,
        repo_root=repo_root,
        state_dir=state_dir,
    )
    return client.poll(task_id, **kwargs)


def _positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected an integer") from exc
    if parsed < 0:
        raise argparse.ArgumentTypeError("expected a non-negative integer")
    return parsed


def _issue_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected an integer") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("expected a positive integer")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create and manage GitHub Copilot agent tasks safely.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--repo",
        "--repository",
        default=os.environ.get("GITHUB_REPOSITORY", "Aries-Serpent/_codex_"),
    )
    parser.add_argument("--owner", default="")
    parser.add_argument("--repo-name", "--name", dest="repo_name", default="")
    parser.add_argument("--token", default="")
    parser.add_argument("--state-dir", "--state_dir", "--dedup-state", dest="state_dir", default="")
    parser.add_argument("--repo-root", "--repo_root", dest="repo_root", default="")
    parser.add_argument("--actor", default="")
    parser.add_argument("--skip-budget", "--skip_budget", "--estimate-only", action="store_true")
    parser.add_argument("--dry-run", "--dry_run", action="store_true")
    parser.add_argument("--json", "--json-output", action="store_true")

    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_mutation_options(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--actor", default=argparse.SUPPRESS)
        subparser.add_argument(
            "--skip-budget",
            "--skip_budget",
            "--estimate-only",
            action="store_true",
            default=argparse.SUPPRESS,
        )
        subparser.add_argument(
            "--dry-run", "--dry_run", action="store_true", default=argparse.SUPPRESS
        )
        subparser.add_argument("--token", default=argparse.SUPPRESS)
        subparser.add_argument(
            "--json", "--json-output", action="store_true", default=argparse.SUPPRESS
        )

    create = subparsers.add_parser("create", help="Create an agent task")
    add_mutation_options(create)
    create.add_argument("prompt", nargs="?", default="")
    create.add_argument("--prompt", dest="prompt_option", default="")
    create.add_argument(
        "--problem",
        "--problem-statement",
        "--problem_statement",
        dest="problem_statement",
        default="",
    )
    create.add_argument(
        "--base",
        "--base-branch",
        "--base_branch",
        "--base-ref",
        "--base_ref",
        dest="base_branch",
        default="",
    )
    create.add_argument(
        "--head",
        "--head-branch",
        "--head_branch",
        "--head-ref",
        "--head_ref",
        dest="head_branch",
        default="",
    )
    create.add_argument(
        "--launch-key", "--launch_key", "--dedup-key", dest="launch_key", default=""
    )
    create.add_argument(
        "--issue", "--issue-number", "--issue_number", type=_issue_int, default=None
    )
    create.add_argument("--assignee", "--assignees", action="append", default=[])
    create.add_argument("--custom-agent", "--custom_agent", default="")
    create.add_argument("--model", default="")
    create.add_argument(
        "--custom-instructions", "--custom_instructions", dest="custom_instructions", default=""
    )
    create.add_argument("--promote", "--promotion", action="store_true")

    view = subparsers.add_parser("view", help="View one agent task")
    add_mutation_options(view)
    view.add_argument("task_id", nargs="?", default="")
    view.add_argument("--task-id", "--task_id", dest="task_id_option", default="")

    listing = subparsers.add_parser("list", help="List agent tasks")
    add_mutation_options(listing)
    listing.add_argument("--status", "--state", dest="status", default="")
    listing.add_argument("--page", type=_positive_int, default=1)
    listing.add_argument(
        "--per-page", "--per_page", dest="per_page", type=_positive_int, default=100
    )

    continue_parser = subparsers.add_parser("continue", help="Continue an agent task")
    add_mutation_options(continue_parser)
    continue_parser.add_argument("task_id", nargs="?", default="")
    continue_parser.add_argument("--task-id", "--task_id", dest="task_id_option", default="")
    continue_parser.add_argument("--prompt", "--message", dest="prompt", default="")
    continue_parser.add_argument("--launch-key", "--launch_key", dest="launch_key", default="")

    cancel = subparsers.add_parser("cancel", help="Cancel an agent task")
    add_mutation_options(cancel)
    cancel.add_argument("task_id", nargs="?", default="")
    cancel.add_argument("--task-id", "--task_id", dest="task_id_option", default="")
    cancel.add_argument("--launch-key", "--launch_key", dest="launch_key", default="")

    assign = subparsers.add_parser("assign", help="Assign an issue and agent task")
    add_mutation_options(assign)
    assign.add_argument("issue_number", nargs="?", type=_issue_int)
    assign.add_argument(
        "--issue", "--issue-number", "--issue_number", dest="issue_option", type=_issue_int
    )
    assign.add_argument("--assignee", "--assignees", action="append", required=True)
    assign.add_argument("--prompt", "--message", dest="prompt", default="")
    assign.add_argument(
        "--base",
        "--base-branch",
        "--base_branch",
        "--base-ref",
        "--base_ref",
        dest="base_branch",
        default="",
    )
    assign.add_argument(
        "--head",
        "--head-branch",
        "--head_branch",
        "--head-ref",
        "--head_ref",
        dest="head_branch",
        default="",
    )
    assign.add_argument("--launch-key", "--launch_key", dest="launch_key", default="")

    preflight_parser = subparsers.add_parser("preflight", help="Run local preflight checks")
    add_mutation_options(preflight_parser)
    preflight_parser.add_argument("prompt", nargs="?", default="")
    preflight_parser.add_argument("--prompt", dest="prompt_option", default="")
    preflight_parser.add_argument(
        "--base",
        "--base-branch",
        "--base_branch",
        "--base-ref",
        "--base_ref",
        dest="base_branch",
        default="",
    )
    preflight_parser.add_argument(
        "--head",
        "--head-branch",
        "--head_branch",
        "--head-ref",
        "--head_ref",
        dest="head_branch",
        default="",
    )
    preflight_parser.add_argument("--launch-key", "--launch_key", dest="launch_key", default="")
    preflight_parser.add_argument(
        "--issue", "--issue-number", "--issue_number", type=_issue_int, default=None
    )
    preflight_parser.add_argument("--assignee", "--assignees", action="append", default=[])
    preflight_parser.add_argument("--promote", "--promotion", action="store_true")
    preflight_parser.add_argument(
        "--probe-agent-tasks",
        "--probe_agent_tasks",
        action="store_true",
        help="Opt-in live read probe of the repository Agent Tasks endpoint",
    )

    poll = subparsers.add_parser("poll", help="Poll an agent task until terminal")
    add_mutation_options(poll)
    poll.add_argument("task_id", nargs="?", default="")
    poll.add_argument("--task-id", "--task_id", dest="task_id_option", default="")
    poll.add_argument("--timeout", type=float, default=300.0)
    poll.add_argument("--interval", type=float, default=5.0)

    return parser


def _json_error(operation: str, exc: BaseException) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "ok": False,
        "operation": operation,
        "timestamp": utc_now(),
        "api_version": API_VERSION,
        "error": str(exc),
    }
    if isinstance(exc, GitHubAPIError):
        payload["status"] = exc.status
        payload["http_status"] = exc.status
        if exc.payload is not None:
            payload["payload"] = exc.payload
    if isinstance(exc, PolicyViolation):
        if exc.result:
            payload["preflight"] = exc.result
            payload["blocked_reasons"] = exc.result.get("blocked_reasons", [])
        payload["policy_error"] = True
    return payload


def main(
    argv: Sequence[str] | None = None,
    *,
    transport: HTTPTransport | Callable[..., Any] | None = None,
    environ: Mapping[str, str] | None = None,
    repo_root: Path | str | None = None,
    sleep: Callable[[float], None] | None = None,
) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.owner:
            owner = args.owner
            repo = args.repo_name or args.repo.split("/")[-1]
        else:
            owner, repo = parse_repo(args.repo)
        if args.repo_name and not args.owner:
            owner, repo = owner, args.repo_name

        root = Path(repo_root) if repo_root is not None else Path.cwd()
        state_dir = Path(args.state_dir) if args.state_dir else root / ".codex"
        client = CopilotAgentTaskClient(
            owner,
            repo,
            token=args.token or None,
            environ=os.environ if environ is None else environ,
            transport=transport,
            repo_root=root,
            state_dir=state_dir,
            timeout=30,
        )
        if sleep is not None:
            client.sleep = sleep

        if args.command == "create":
            prompt = args.prompt_option or args.prompt or args.problem_statement
            result = client.create(
                prompt,
                problem_statement=args.problem_statement,
                base_branch=args.base_branch,
                head_branch=args.head_branch,
                launch_key=args.launch_key,
                promotion=args.promote,
                issue_number=args.issue,
                assignees=args.assignee,
                custom_agent=args.custom_agent,
                model=args.model,
                custom_instructions=args.custom_instructions,
                actor=args.actor,
                skip_budget=args.skip_budget,
                dry_run=args.dry_run,
            )
        elif args.command == "view":
            task_id = args.task_id_option or args.task_id
            result = client.view(task_id)
        elif args.command == "list":
            result = client.list(status=args.status, page=args.page, per_page=args.per_page)
        elif args.command == "continue":
            task_id = args.task_id_option or args.task_id
            result = client.continue_task(
                task_id,
                prompt=args.prompt,
                launch_key=args.launch_key,
                actor=args.actor,
                skip_budget=args.skip_budget,
                dry_run=args.dry_run,
            )
        elif args.command == "cancel":
            task_id = args.task_id_option or args.task_id
            result = client.cancel(
                task_id,
                launch_key=args.launch_key,
                actor=args.actor,
                skip_budget=args.skip_budget,
                dry_run=args.dry_run,
            )
        elif args.command == "assign":
            issue_number = args.issue_option or args.issue_number
            result = client.assign(
                issue_number,
                args.assignee,
                prompt=args.prompt,
                base_branch=args.base_branch,
                head_branch=args.head_branch,
                launch_key=args.launch_key,
                actor=args.actor,
                skip_budget=args.skip_budget,
                dry_run=args.dry_run,
            )
        elif args.command == "preflight":
            prompt = args.prompt_option or args.prompt
            result = client.preflight(
                prompt,
                base_branch=args.base_branch,
                head_branch=args.head_branch,
                promotion=args.promote,
                probe_agent_tasks=getattr(args, "probe_agent_tasks", False),
                launch_key=args.launch_key,
                issue_number=args.issue,
                assignees=args.assignee,
                actor=args.actor,
                skip_budget=args.skip_budget,
            )
        elif args.command == "poll":
            task_id = args.task_id_option or args.task_id
            result = client.poll(task_id, timeout=args.timeout, interval=args.interval)
        else:
            raise PolicyViolation("unsupported command")

        print(json.dumps(result, sort_keys=True, ensure_ascii=True))
        if args.command == "preflight" and not result.get("allowed", False):
            return 2
        return 0
    except BaseException as exc:
        result = _json_error(args.command, exc)
        print(json.dumps(result, sort_keys=True, ensure_ascii=True))
        if isinstance(exc, PolicyViolation):
            return 2
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
