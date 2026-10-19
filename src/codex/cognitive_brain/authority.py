"""Authority envelope for autonomous improvement actions.

Every execution or PR-creation decision must pass through
:meth:`AuthorityEnvelope.evaluate` *before* any work is dispatched. The
envelope fails closed: any violation (path outside the allowlist,
oversized diff, secret-bearing environment, missing approval) denies
authorization and records the reason.
"""

from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from typing import Mapping, Optional, Tuple


@dataclass(frozen=True, slots=True)
class AuthorityLimits:
    """Resource and scope limits for one authorized action."""

    max_diff_lines: int = 400
    max_files: int = 25
    timeout_seconds: int = 600
    max_memory_mb: int = 2048


@dataclass(frozen=True, slots=True)
class AuthorityDecision:
    """Result of an authority evaluation."""

    authorized: bool
    reasons: Tuple[str, ...] = ()
    idempotency_key: Optional[str] = None


@dataclass(slots=True)
class AuthorityEnvelope:
    """Policy boundary ahead of execution and PR creation."""

    allowed_path_globs: Tuple[str, ...] = ("src/**", "tests/**", "docs/**")
    denied_path_globs: Tuple[str, ...] = (
        ".github/workflows/**",
        ".git/**",
        "**/.env",
        "**/secrets/**",
    )
    limits: AuthorityLimits = field(default_factory=AuthorityLimits)
    require_human_approval: bool = True
    secret_env_pattern: re.Pattern[str] = field(
        default=re.compile(r"(TOKEN|SECRET|PASSWORD|API_?KEY|PRIVATE_?KEY)", re.IGNORECASE)
    )

    def check_paths(self, paths: Tuple[str, ...]) -> Tuple[str, ...]:
        """Return reasons for any path outside the allowed scope."""

        violations = []
        for path in paths:
            if any(fnmatch.fnmatch(path, pat) for pat in self.denied_path_globs):
                violations.append(f"path denied by policy: {path}")
                continue
            if not any(fnmatch.fnmatch(path, pat) for pat in self.allowed_path_globs):
                violations.append(f"path outside allowlist: {path}")
        return tuple(violations)

    def check_diff_size(self, diff_lines: int, file_count: int) -> Tuple[str, ...]:
        """Return reasons for any size-limit breach."""

        violations = []
        if diff_lines > self.limits.max_diff_lines:
            violations.append(
                f"diff too large: {diff_lines} > {self.limits.max_diff_lines} lines"
            )
        if file_count > self.limits.max_files:
            violations.append(
                f"too many files: {file_count} > {self.limits.max_files}"
            )
        return tuple(violations)

    def check_environment(self, env: Mapping[str, str]) -> Tuple[str, ...]:
        """Return reasons for variables that would carry live credentials.

        Only variables holding actual secret *values* (non-empty) block;
        metadata about secret handling (names, counts, toggles) does not.
        """

        return tuple(
            f"secret-like environment variable must not be inherited: {name}"
            for name, value in env.items()
            if self.secret_env_pattern.search(name) and value
        )

    def make_idempotency_key(self, *identity_parts: str) -> str:
        """Derive a stable idempotency key from the action identity."""

        payload = json.dumps(list(identity_parts), sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def evaluate(
        self,
        *,
        paths: Tuple[str, ...],
        diff_lines: int,
        env: Optional[Mapping[str, str]] = None,
        human_approved: bool = False,
        idempotency_key: Optional[str] = None,
    ) -> AuthorityDecision:
        """Authorize or deny an action. Fails closed on any violation."""

        reasons: list[str] = []
        reasons.extend(self.check_paths(paths))
        reasons.extend(self.check_diff_size(diff_lines, len(paths)))
        reasons.extend(self.check_environment(env if env is not None else os.environ))
        if self.require_human_approval and not human_approved:
            reasons.append("human approval is required before execution")
        return AuthorityDecision(
            authorized=not reasons,
            reasons=tuple(reasons),
            idempotency_key=idempotency_key,
        )
