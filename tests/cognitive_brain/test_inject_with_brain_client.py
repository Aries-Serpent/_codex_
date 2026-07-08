"""Acceptance tests for CB-004: offline mock fixture for BrainClient integration.

Validates that :class:`~codex.cognitive.session_hook.SessionContextInjector`
correctly integrates with an injected :class:`~codex.agents.brain_client.BrainClient`
without requiring a live cognitive-app server.

All tests use a lightweight mock so the suite runs fully offline.
"""

from __future__ import annotations

from unittest.mock import MagicMock

from codex.cognitive.session_hook import SessionContextInjector, SessionContextPayload

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_brain_api(*, get_raises: bool = False):
    """Return a minimal mock AgentBrainAPI."""
    api = MagicMock()
    if get_raises:
        api.get_session_context.side_effect = RuntimeError("offline")
    else:
        api.get_session_context.return_value = MagicMock(
            patterns=[],
            memories=[],
            context={},
            agent_context=None,
        )
    api.store_memory = MagicMock()
    return api


def _mock_brain_client(*, available: bool = True, search_results: list | None = None):
    """Return a lightweight offline mock BrainClient."""
    client = MagicMock()
    client.is_available.return_value = available
    client.memory_search.return_value = {
        "results": (
            search_results
            if search_results is not None
            else [
                {"pattern_id": "P-test-001", "fact": "Test fact from memory search"},
            ]
        )
    }
    return client


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestInjectWithBrainClient:
    """CB-004: offline mock fixture tests for BrainClient integration."""

    def test_memory_search_called_during_reconstruction(self, tmp_path):
        """memory_search() is invoked when quantum reconstruction is triggered."""
        api = _mock_brain_api(get_raises=True)  # force reconstruction path
        client = _mock_brain_client(available=True)

        injector = SessionContextInjector(
            brain_api=api,
            cache_path=tmp_path / "cache.json",
            brain_client=client,
        )

        meta = {"pr_title": "fix faiss store dimension", "pr_body": "vector search improvement"}
        result = injector.inject(meta)

        assert isinstance(result, SessionContextPayload)
        # memory_search was called at least once during quantum reconstruction
        client.memory_search.assert_called()

    def test_memory_search_not_called_when_server_unavailable(self, tmp_path):
        """memory_search() is skipped when is_available() returns False."""
        api = _mock_brain_api(get_raises=True)
        client = _mock_brain_client(available=False)

        injector = SessionContextInjector(
            brain_api=api,
            cache_path=tmp_path / "cache.json",
            brain_client=client,
        )

        injector.inject({"pr_title": "some work", "pr_body": ""})

        client.is_available.assert_called()
        client.memory_search.assert_not_called()

    def test_inject_succeeds_without_brain_client(self, tmp_path):
        """Injector works normally when no BrainClient is provided (backward compat)."""
        api = _mock_brain_api(get_raises=False)

        injector = SessionContextInjector(
            brain_api=api,
            cache_path=tmp_path / "cache.json",
        )

        result = injector.inject({"pr_title": "test", "pr_body": ""})
        assert isinstance(result, SessionContextPayload)

    def test_memory_search_results_augment_payload(self, tmp_path):
        """Patterns returned by memory_search are incorporated into the reconstructed payload."""
        api = _mock_brain_api(get_raises=True)
        search_results = [
            {"pattern_id": "P-quantum-001", "fact": "Use _captured list to avoid double invoke"},
            {"pattern_id": "P-ci-017", "fact": "SHA drift in GitHub Actions merge preview"},
        ]
        client = _mock_brain_client(available=True, search_results=search_results)

        injector = SessionContextInjector(
            brain_api=api,
            cache_path=tmp_path / "cache.json",
            brain_client=client,
        )

        result = injector.inject(
            {"pr_title": "quantum fix ci sha drift", "pr_body": "sha drift fix"}
        )

        assert isinstance(result, SessionContextPayload)
        client.memory_search.assert_called()

    def test_brain_client_exception_does_not_break_inject(self, tmp_path):
        """If BrainClient.is_available() raises, inject() still returns a payload."""
        api = _mock_brain_api(get_raises=True)
        client = MagicMock()
        client.is_available.side_effect = ConnectionError("server down")

        injector = SessionContextInjector(
            brain_api=api,
            cache_path=tmp_path / "cache.json",
            brain_client=client,
        )

        # Should not raise — exception is swallowed with a debug log
        result = injector.inject({"pr_title": "any", "pr_body": ""})
        assert isinstance(result, SessionContextPayload)

    def test_brain_client_stored_on_injector(self, tmp_path):
        """The BrainClient instance is stored on the injector for later use."""
        api = _mock_brain_api()
        client = _mock_brain_client()

        injector = SessionContextInjector(
            brain_api=api,
            cache_path=tmp_path / "cache.json",
            brain_client=client,
        )

        assert injector._brain_client is client, "_brain_client is not valid"
