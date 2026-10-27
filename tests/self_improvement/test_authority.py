"""Tests for the authority envelope: fail-closed policy ahead of execution."""

from __future__ import annotations

from codex.cognitive_brain.authority import AuthorityEnvelope, AuthorityLimits


def _envelope() -> AuthorityEnvelope:
    return AuthorityEnvelope(limits=AuthorityLimits(max_diff_lines=100, max_files=3))


def test_clean_action_is_authorized() -> None:
    decision = _envelope().evaluate(
        paths=("src/codex/x.py",),
        diff_lines=10,
        env={"PATH": "/usr/bin"},
        human_approved=True,
    )
    assert decision.authorized, decision.reasons


def test_denied_path_blocks() -> None:
    decision = _envelope().evaluate(
        paths=(".github/workflows/ci.yml",),
        diff_lines=5,
        env={},
        human_approved=True,
    )
    assert not decision.authorized
    assert any("denied" in r for r in decision.reasons)


def test_path_outside_allowlist_blocks() -> None:
    decision = _envelope().evaluate(
        paths=("/etc/passwd",), diff_lines=1, env={}, human_approved=True
    )
    assert not decision.authorized


def test_oversized_diff_blocks() -> None:
    decision = _envelope().evaluate(
        paths=("src/a.py",), diff_lines=101, env={}, human_approved=True
    )
    assert not decision.authorized
    assert any("diff too large" in r for r in decision.reasons)


def test_too_many_files_blocks() -> None:
    decision = _envelope().evaluate(
        paths=("src/a.py", "src/b.py", "src/c.py", "src/d.py"),
        diff_lines=4,
        env={},
        human_approved=True,
    )
    assert not decision.authorized
    assert any("too many files" in r for r in decision.reasons)


def test_secret_environment_blocks() -> None:
    decision = _envelope().evaluate(
        paths=("src/a.py",),
        diff_lines=1,
        env={"GITHUB_TOKEN": "x", "PATH": "/usr/bin"},
        human_approved=True,
    )
    assert not decision.authorized
    assert any("GITHUB_TOKEN" in r for r in decision.reasons)


def test_missing_human_approval_blocks() -> None:
    decision = _envelope().evaluate(paths=("src/a.py",), diff_lines=1, env={})
    assert not decision.authorized
    assert any("human approval" in r for r in decision.reasons)


def test_idempotency_key_is_stable() -> None:
    env = _envelope()
    assert env.make_idempotency_key("a", "b") == env.make_idempotency_key("a", "b")
    assert env.make_idempotency_key("a", "b") != env.make_idempotency_key("a", "c")
