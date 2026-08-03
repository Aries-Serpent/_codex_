"""Shell Execution Safety Layer for the Cognitive Brain runtime.

Implements command-level allow/deny policy, timeout ceilings, retry limits,
working-directory constraints, and sensitive-token redaction for all shell
invocations that pass through the cognitive brain planner.

Design
------
- ``ShellPolicy`` is the single gating object.  Every shell execution
  request **must** call ``ShellPolicy.gate(command, cwd)`` before invoking
  the OS.  The returned :class:`GateDecision` carries the verdict plus the
  sanitised command string safe to log.
- Token redaction runs on both the command string **before** execution
  (logged path) and on captured output **after** execution.
- The policy is deterministic: same inputs → same verdict.  No randomness.

Usage::

    from codex.cognitive_brain.shell_policy import ShellPolicy, PolicyVerdict

    policy = ShellPolicy()
    decision = policy.gate("git status", cwd="/repo")
    if decision.verdict != PolicyVerdict.ALLOW:
        raise PermissionError(f"Shell command denied: {decision.reason}")
    # … execute command …
    safe_output = policy.redact(raw_output)
"""

from __future__ import annotations

import fnmatch
import logging
import os
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Sequence, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Default maximum wall-clock time for any single shell command (seconds).
DEFAULT_TIMEOUT_CEILING_S: float = 120.0

# Maximum automatic retries for transient errors.
DEFAULT_MAX_RETRIES: int = 3

# Token-like patterns to redact from command strings and output.
# Matches: GitHub tokens, API keys, bearer tokens, passwords in flags.
_DEFAULT_REDACT_PATTERNS: Tuple[re.Pattern[str], ...] = (
    re.compile(
        r"(github_pat_[A-Za-z0-9_]+|gh[oprsu]_[A-Za-z0-9]{20,})",
        re.ASCII,
    ),  # GitHub token variants (classic, fine-grained, app, refresh, user-to-server)
    re.compile(r"(GITHUB_TOKEN=[^\s]+)", re.IGNORECASE),
    re.compile(r"(CODEX_MASTER_KEY=[^\s]+)", re.IGNORECASE),
    re.compile(r"(--password[= ][^\s]+)", re.IGNORECASE),
    re.compile(r"(--token[= ][^\s]+)", re.IGNORECASE),
    re.compile(r"(Bearer\s+[A-Za-z0-9\-._~+/]+=*)", re.IGNORECASE),
)

_REDACTED = "[REDACTED]"

# Shell metacharacters that enable command chaining, redirection, and substitution.
# These MUST be detected and blocked BEFORE pattern matching, regardless of
# whether the base command is in the allow list.
# Examples of bypasses we prevent:
#   - "git stash; rm -rf /" matches allow pattern "git *"
#   - "echo hello && sudo" matches allow pattern "echo *"
#   - "cat file | sh" matches allow pattern "cat *"
#   - "echo $(malicious_code)" matches allow pattern "echo *"
_SHELL_METACHARACTERS: Tuple[str, ...] = (
    # Multi-character metacharacters MUST be checked first to avoid substring matching
    # (e.g., "||" before "|", "&&" before "&", "2>" before ">")
    "&&",  # Logical AND (conditional execution)
    "||",  # Logical OR (conditional execution)
    "$(",  # Command substitution
    "2>",  # Error redirection
    # Single-character metacharacters
    ";",  # Command separator
    "|",  # Pipe (stdout to stdin chaining)
    "\n",  # Newline (multi-line commands)
    "\r",  # Carriage return
    "`",  # Backtick command substitution
    "{",  # Brace grouping/expansion
    "}",  # Brace grouping/expansion
    "(",  # Subshell grouping
    ")",  # Subshell grouping
    ">",  # Output redirection
    "<",  # Input redirection
    "&",  # Background execution (when not part of &&)
)

# Default allow-patterns: safe read-only and build commands.
_DEFAULT_ALLOW_PATTERNS: Tuple[str, ...] = (
    "git *",
    "python *",
    "python3 *",
    "pytest *",
    "pre-commit *",
    "nox *",
    "ruff *",
    "black *",
    "isort *",
    "mypy *",
    "pip *",
    "pip3 *",
    "echo *",
    "cat *",
    "ls *",
    "find *",
    "grep *",
    "head *",
    "tail *",
    "wc *",
    "sort *",
    "uniq *",
    "diff *",
    "cp *",
    "mv *",
    "mkdir *",
    "rm *",
    "touch *",
    "true",
    "false",
)

# Default deny-patterns: potentially destructive or escalation-prone.
_DEFAULT_DENY_PATTERNS: Tuple[str, ...] = (
    "sudo *",
    "su *",
    "chmod 777 *",
    "curl * | sh",
    "wget * | sh",
    "curl * | bash",
    "wget * | bash",
    "dd *",
    "mkfs *",
    "fdisk *",
    "rm -rf /*",
    ":(){ :|:& };:",  # fork bomb
    "nc *",
    "netcat *",
    "ncat *",
)


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


class PolicyVerdict(str, Enum):
    """Outcome of a :class:`ShellPolicy` gate check."""

    ALLOW = "allow"
    DENY = "deny"
    AUDIT = "audit"  # Allowed but must be recorded; elevated risk


@dataclass
class GateDecision:
    """Result of :meth:`ShellPolicy.gate`."""

    verdict: PolicyVerdict
    command: str  # original command
    safe_command: str  # redacted command safe for logging
    cwd: Optional[str]
    reason: str
    timeout_s: float
    max_retries: int
    risk_flags: List[str] = field(default_factory=list)

    @property
    def allowed(self) -> bool:
        return self.verdict in (PolicyVerdict.ALLOW, PolicyVerdict.AUDIT)

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict.value,
            "safe_command": self.safe_command,
            "cwd": self.cwd,
            "reason": self.reason,
            "timeout_s": self.timeout_s,
            "max_retries": self.max_retries,
            "risk_flags": self.risk_flags,
        }


# ---------------------------------------------------------------------------
# ShellPolicy
# ---------------------------------------------------------------------------


class ShellPolicy:
    """Gate and audit all shell command invocations.

    Parameters
    ----------
    allow_patterns:
        Glob patterns for commands that are explicitly allowed.  Defaults
        to :data:`_DEFAULT_ALLOW_PATTERNS`.
    deny_patterns:
        Glob patterns for commands that are always denied.  Defaults to
        :data:`_DEFAULT_DENY_PATTERNS`.  Deny rules take precedence over
        allow rules.
    working_dir_allowlist:
        If non-empty, only commands whose *cwd* starts with one of these
        prefixes are permitted.  ``None`` means any directory is allowed.
    timeout_ceiling_s:
        Maximum wall-clock time for any command.  Callers must honour this.
    max_retries:
        Maximum automatic retry attempts for transient failures.
    redact_patterns:
        Compiled regexes applied to commands and output before logging.
    default_shell_enabled:
        If False, the policy defaults to DENY for unknown commands instead
        of ALLOW.  Set to ``True`` only in explicitly shell-enabled kernels.
    """

    def __init__(
        self,
        allow_patterns: Optional[Sequence[str]] = None,
        deny_patterns: Optional[Sequence[str]] = None,
        working_dir_allowlist: Optional[Sequence[str]] = None,
        timeout_ceiling_s: float = DEFAULT_TIMEOUT_CEILING_S,
        max_retries: int = DEFAULT_MAX_RETRIES,
        redact_patterns: Optional[Sequence[re.Pattern[str]]] = None,
        default_shell_enabled: bool = False,
    ) -> None:
        self._allow: Tuple[str, ...] = (
            tuple(allow_patterns) if allow_patterns is not None else _DEFAULT_ALLOW_PATTERNS
        )
        self._deny: Tuple[str, ...] = (
            tuple(deny_patterns) if deny_patterns is not None else _DEFAULT_DENY_PATTERNS
        )
        self._cwd_allowlist: Optional[Tuple[str, ...]] = (
            tuple(working_dir_allowlist) if working_dir_allowlist else None
        )
        self._timeout = timeout_ceiling_s
        self._max_retries = max_retries
        self._redact: Tuple[re.Pattern[str], ...] = (
            tuple(redact_patterns) if redact_patterns is not None else _DEFAULT_REDACT_PATTERNS
        )
        self._default_enabled = default_shell_enabled

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def gate(self, command: str, cwd: Optional[str] = None) -> GateDecision:
        """Evaluate *command* and return a :class:`GateDecision`.

        Parameters
        ----------
        command:
            The shell command string to evaluate.
        cwd:
            The proposed working directory.
        """
        safe_cmd = self.redact(command)
        risk_flags: List[str] = []

        # Step 0: Shell metacharacter validation (BEFORE pattern matching).
        # This prevents chained-command bypass attacks regardless of allow patterns.
        metachar_check = self._check_shell_metacharacters(command)
        if metachar_check is not None:
            logger.warning(
                "ShellPolicy DENY (shell metacharacter): %s command=%r",
                metachar_check,
                safe_cmd,
            )
            return GateDecision(
                verdict=PolicyVerdict.DENY,
                command=command,
                safe_command=safe_cmd,
                cwd=cwd,
                reason=metachar_check,
                timeout_s=0.0,
                max_retries=0,
                risk_flags=["shell_metacharacter_detected"],
            )

        # Step 1: working-directory constraint check.
        if cwd is not None and self._cwd_allowlist is not None:
            cwd_ok = any(cwd.startswith(prefix) for prefix in self._cwd_allowlist)
            if not cwd_ok:
                logger.warning(
                    "ShellPolicy DENY: cwd=%r not in allowlist command=%r", cwd, safe_cmd
                )
                return GateDecision(
                    verdict=PolicyVerdict.DENY,
                    command=command,
                    safe_command=safe_cmd,
                    cwd=cwd,
                    reason=f"Working directory '{cwd}' is not in the allowed list",
                    timeout_s=self._timeout,
                    max_retries=0,
                    risk_flags=["cwd_violation"],
                )

        # Step 2: Deny pattern check (highest precedence).
        for pattern in self._deny:
            if fnmatch.fnmatch(command, pattern) or fnmatch.fnmatch(command.lower(), pattern):
                logger.warning(
                    "ShellPolicy DENY: matched deny pattern=%r command=%r",
                    pattern,
                    safe_cmd,
                )
                return GateDecision(
                    verdict=PolicyVerdict.DENY,
                    command=command,
                    safe_command=safe_cmd,
                    cwd=cwd,
                    reason=f"Command matched deny pattern '{pattern}'",
                    timeout_s=0.0,
                    max_retries=0,
                    risk_flags=["deny_pattern_match"],
                )

        # Step 3: Allow pattern check.
        for pattern in self._allow:
            if fnmatch.fnmatch(command, pattern) or fnmatch.fnmatch(command.lower(), pattern):
                # Escalate to AUDIT if command looks risky despite being allowed.
                verdict, flags = self._risk_audit(command)
                risk_flags.extend(flags)
                logger.info(
                    "ShellPolicy %s: matched allow pattern=%r command=%r",
                    verdict.value.upper(),
                    pattern,
                    safe_cmd,
                )
                return GateDecision(
                    verdict=verdict,
                    command=command,
                    safe_command=safe_cmd,
                    cwd=cwd,
                    reason=f"Command matched allow pattern '{pattern}'",
                    timeout_s=self._timeout,
                    max_retries=self._max_retries,
                    risk_flags=risk_flags,
                )

        # Step 4: Unmatched commands — allow only if default_shell_enabled.
        if self._default_enabled:
            verdict, flags = self._risk_audit(command)
            risk_flags.extend(flags)
            logger.info("ShellPolicy %s (default enabled): command=%r", verdict.value, safe_cmd)
            return GateDecision(
                verdict=verdict,
                command=command,
                safe_command=safe_cmd,
                cwd=cwd,
                reason="No explicit allow/deny pattern matched; default_shell_enabled=True",
                timeout_s=self._timeout,
                max_retries=self._max_retries,
                risk_flags=risk_flags,
            )

        logger.warning("ShellPolicy DENY (no match): command=%r", safe_cmd)
        return GateDecision(
            verdict=PolicyVerdict.DENY,
            command=command,
            safe_command=safe_cmd,
            cwd=cwd,
            reason="No allow pattern matched and default_shell_enabled=False",
            timeout_s=0.0,
            max_retries=0,
            risk_flags=["no_allow_match"],
        )

    def redact(self, text: str) -> str:
        """Replace sensitive tokens in *text* with ``[REDACTED]``.

        Safe to call on command strings before logging and on captured
        command output.
        """
        result = text
        for pattern in self._redact:
            result = pattern.sub(_REDACTED, result)
        return result

    @property
    def timeout_ceiling_s(self) -> float:
        """Maximum allowed execution time in seconds."""
        return self._timeout

    @property
    def max_retries(self) -> int:
        """Maximum retry count for transient failures."""
        return self._max_retries

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_shell_metacharacters(self, command: str) -> Optional[str]:
        """Check if *command* contains shell metacharacters that enable chaining.

        Returns an error message if found, None if clean.

        This check happens BEFORE pattern matching to prevent bypass attacks
        like "git stash; rm -rf /" matching the allow pattern "git *".
        """
        for metachar in _SHELL_METACHARACTERS:
            if metachar in command:
                return (
                    f"Command contains shell metacharacter '{metachar}' which "
                    "enables chaining/redirection"
                )

        return None

    def _risk_audit(self, command: str) -> Tuple[PolicyVerdict, List[str]]:
        """Return (ALLOW|AUDIT, risk_flags) for a command that passed allow rules."""
        flags: List[str] = []
        cmd_lower = command.lower()

        if "rm -rf" in cmd_lower or "rm -r" in cmd_lower:
            flags.append("recursive_delete")
        # Only flag --force (full word) to avoid false positives on `-f pattern_file`
        # or other single-letter flags that are not destructive force operations.
        if "--force" in cmd_lower:
            flags.append("force_flag")
        if "|" in command and ("sh" in cmd_lower or "bash" in cmd_lower):
            flags.append("pipe_to_shell")
        if ">" in command:
            flags.append("output_redirect")
        if any(tok in cmd_lower for tok in ("token", "secret", "password", "key")):
            flags.append("sensitive_keyword")

        verdict = PolicyVerdict.AUDIT if flags else PolicyVerdict.ALLOW
        return verdict, flags


# ---------------------------------------------------------------------------
# Module-level default policy (singleton)
# ---------------------------------------------------------------------------

_default_policy: Optional[ShellPolicy] = None


def get_default_policy() -> ShellPolicy:
    """Return the process-level default :class:`ShellPolicy`.

    Builds a policy with ``default_shell_enabled=False`` (deny-by-default)
    using the environment variable ``COGNITIVE_BRAIN_ALLOW_SHELL=true`` to
    opt in to shell execution.
    """
    global _default_policy
    if _default_policy is None:
        allow_shell = os.getenv("COGNITIVE_BRAIN_ALLOW_SHELL", "false").lower() == "true"
        _default_policy = ShellPolicy(default_shell_enabled=allow_shell)
        logger.info(
            "ShellPolicy default created: allow_shell=%s timeout=%.0fs max_retries=%d",
            allow_shell,
            _default_policy.timeout_ceiling_s,
            _default_policy.max_retries,
        )
    return _default_policy


def reset_default_policy() -> None:
    """Reset the singleton (for testing only)."""
    global _default_policy
    _default_policy = None
