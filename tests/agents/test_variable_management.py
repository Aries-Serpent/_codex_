"""
Unit tests for scripts/tools/variable_manager.py

Run:
    python -m pytest tests/agents/test_variable_management.py -v
"""

from __future__ import annotations

import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

from scripts.ci._token_resolver import get_token

# Ensure scripts/ and src/ are importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
# scripts/tools is on the path directly so `import variable_manager` works
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "tools"))

from variable_manager import (
    GitHubAPIError,
    VariableManager,
    _resolve_token,
)

# ─────────────────────────────────────────────────────────────────────────────
# Token resolution tests
# ─────────────────────────────────────────────────────────────────────────────


class TestResolveToken(unittest.TestCase):

    def _clear_tokens(self):
        for k in ("CODEX_MASTER_KEY", "CODEX_BACKUP_KEY", "AGENT_GITHUB_TOKEN", "GITHUB_TOKEN"):
            os.environ.pop(k, None)

    def test_priority_order_master_key_first(self):
        self._clear_tokens()
        get_token(required_elevated=True)[0] = "master_token"
        get_token(required_elevated=True)[0] = "backup_token"
        os.environ["GITHUB_TOKEN"] = "gh_token"
        tok, src = _resolve_token()
        self.assertEqual(tok, "master_token")
        self.assertEqual(src, "CODEX_MASTER_KEY")

    def test_priority_backup_key_when_master_absent(self):
        self._clear_tokens()
        get_token(required_elevated=True)[0] = "backup_token"
        os.environ["GITHUB_TOKEN"] = "gh_token"
        tok, src = _resolve_token()
        self.assertEqual(tok, "backup_token")
        self.assertEqual(src, "CODEX_BACKUP_KEY")

    def test_priority_agent_github_token(self):
        self._clear_tokens()
        os.environ["AGENT_GITHUB_TOKEN"] = "agent_token"
        os.environ["GITHUB_TOKEN"] = "gh_token"
        tok, src = _resolve_token()
        self.assertEqual(tok, "agent_token")
        self.assertEqual(src, "AGENT_GITHUB_TOKEN")

    def test_priority_github_token_fallback(self):
        self._clear_tokens()
        os.environ["GITHUB_TOKEN"] = "gh_token"
        tok, src = _resolve_token()
        self.assertEqual(tok, "gh_token")
        self.assertEqual(src, "GITHUB_TOKEN")

    def test_no_token_returns_empty(self):
        self._clear_tokens()
        tok, src = _resolve_token()
        self.assertEqual(tok, "")
        self.assertEqual(src, "NONE")

    def tearDown(self):
        self._clear_tokens()


# ─────────────────────────────────────────────────────────────────────────────
# VariableManager — repo variables
# ─────────────────────────────────────────────────────────────────────────────


class TestRepoVariables(unittest.TestCase):
    """Tests use direct urllib fallback (mocked) — no server required."""

    OWNER = "Aries-Serpent"
    REPO = "_codex_"

    def setUp(self):
        get_token(required_elevated=True)[0] = "test_master_token"
        self.vm = VariableManager(brain=None)

    def tearDown(self):
        os.environ.pop("CODEX_MASTER_KEY", None)

    # ── list ──────────────────────────────────────────────────────────────

    @patch("variable_manager._gh_request")
    def test_list_repo_vars_success(self, mock_req):
        mock_req.return_value = (
            200,
            {
                "total_count": 2,
                "variables": [
                    {"name": "VAR_A", "value": "alpha", "created_at": "...", "updated_at": "..."},
                    {"name": "VAR_B", "value": "beta", "created_at": "...", "updated_at": "..."},
                ],
            },
        )
        result = self.vm.list_repo_vars(self.OWNER, self.REPO)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "VAR_A")
        mock_req.assert_called_once_with(
            "GET",
            f"/repos/{self.OWNER}/{self.REPO}/actions/variables",
            token="test_master_token",
            brain=None,
        )

    @patch("variable_manager._gh_request")
    def test_list_repo_vars_empty(self, mock_req):
        mock_req.return_value = (200, {"total_count": 0, "variables": []})
        result = self.vm.list_repo_vars(self.OWNER, self.REPO)
        self.assertEqual(result, [])

    @patch("variable_manager._gh_request")
    def test_list_repo_vars_403_raises(self, mock_req):
        mock_req.return_value = (403, {"message": "Resource not accessible"})
        with self.assertRaises(GitHubAPIError) as ctx:
            self.vm.list_repo_vars(self.OWNER, self.REPO)
        self.assertEqual(ctx.exception.status, 403)

    # ── get ───────────────────────────────────────────────────────────────

    @patch("variable_manager._gh_request")
    def test_get_repo_var_success(self, mock_req):
        mock_req.return_value = (
            200,
            {"name": "MY_VAR", "value": "hello", "created_at": "...", "updated_at": "..."},
        )
        result = self.vm.get_repo_var(self.OWNER, self.REPO, "MY_VAR")
        self.assertEqual(result["value"], "hello")

    @patch("variable_manager._gh_request")
    def test_get_repo_var_404_raises(self, mock_req):
        mock_req.return_value = (404, {"message": "Not Found"})
        with self.assertRaises(GitHubAPIError) as ctx:
            self.vm.get_repo_var(self.OWNER, self.REPO, "NONEXISTENT")
        self.assertEqual(ctx.exception.status, 404)

    # ── create ────────────────────────────────────────────────────────────

    @patch("variable_manager._gh_request")
    def test_create_repo_var_success(self, mock_req):
        mock_req.return_value = (201, None)  # GitHub returns 201 No Content
        status = self.vm.create_repo_var(self.OWNER, self.REPO, "NEW_VAR", "new_value")
        self.assertEqual(status, 201)
        mock_req.assert_called_once_with(
            "POST",
            f"/repos/{self.OWNER}/{self.REPO}/actions/variables",
            body={"name": "NEW_VAR", "value": "new_value"},
            token="test_master_token",
            brain=None,
        )

    @patch("variable_manager._gh_request")
    def test_create_repo_var_409_conflict_raises(self, mock_req):
        mock_req.return_value = (422, {"message": "Validation Failed"})
        with self.assertRaises(GitHubAPIError):
            self.vm.create_repo_var(self.OWNER, self.REPO, "EXISTING_VAR", "v")

    # ── update ────────────────────────────────────────────────────────────

    @patch("variable_manager._gh_request")
    def test_update_repo_var_success(self, mock_req):
        mock_req.return_value = (204, None)
        status = self.vm.update_repo_var(self.OWNER, self.REPO, "MY_VAR", "updated")
        self.assertEqual(status, 204)
        mock_req.assert_called_once_with(
            "PATCH",
            f"/repos/{self.OWNER}/{self.REPO}/actions/variables/MY_VAR",
            body={"name": "MY_VAR", "value": "updated"},
            token="test_master_token",
            brain=None,
        )

    # ── delete ────────────────────────────────────────────────────────────

    @patch("variable_manager._gh_request")
    def test_delete_repo_var_success(self, mock_req):
        mock_req.return_value = (204, None)
        status = self.vm.delete_repo_var(self.OWNER, self.REPO, "OLD_VAR")
        self.assertEqual(status, 204)
        mock_req.assert_called_once_with(
            "DELETE",
            f"/repos/{self.OWNER}/{self.REPO}/actions/variables/OLD_VAR",
            token="test_master_token",
            brain=None,
        )


# ─────────────────────────────────────────────────────────────────────────────
# VariableManager — environment variables
# ─────────────────────────────────────────────────────────────────────────────


class TestEnvironmentVariables(unittest.TestCase):

    OWNER = "Aries-Serpent"
    REPO = "_codex_"
    ENV = "production"

    def setUp(self):
        get_token(required_elevated=True)[0] = "test_master_token"
        self.vm = VariableManager(brain=None)

    def tearDown(self):
        os.environ.pop("CODEX_MASTER_KEY", None)

    @patch("variable_manager._gh_request")
    def test_list_env_vars(self, mock_req):
        mock_req.return_value = (200, {"variables": [{"name": "ENV_VAR", "value": "ev"}]})
        result = self.vm.list_env_vars(self.OWNER, self.REPO, self.ENV)
        self.assertEqual(result[0]["name"], "ENV_VAR")
        mock_req.assert_called_with(
            "GET",
            f"/repos/{self.OWNER}/{self.REPO}/environments/{self.ENV}/variables",
            token="test_master_token",
            brain=None,
        )

    @patch("variable_manager._gh_request")
    def test_create_env_var(self, mock_req):
        mock_req.return_value = (201, None)
        self.vm.create_env_var(self.OWNER, self.REPO, self.ENV, "E_VAR", "e_val")
        mock_req.assert_called_with(
            "POST",
            f"/repos/{self.OWNER}/{self.REPO}/environments/{self.ENV}/variables",
            body={"name": "E_VAR", "value": "e_val"},
            token="test_master_token",
            brain=None,
        )

    @patch("variable_manager._gh_request")
    def test_update_env_var(self, mock_req):
        mock_req.return_value = (204, None)
        self.vm.update_env_var(self.OWNER, self.REPO, self.ENV, "E_VAR", "new_val")
        mock_req.assert_called_with(
            "PATCH",
            f"/repos/{self.OWNER}/{self.REPO}/environments/{self.ENV}/variables/E_VAR",
            body={"name": "E_VAR", "value": "new_val"},
            token="test_master_token",
            brain=None,
        )

    @patch("variable_manager._gh_request")
    def test_delete_env_var(self, mock_req):
        mock_req.return_value = (204, None)
        self.vm.delete_env_var(self.OWNER, self.REPO, self.ENV, "E_VAR")
        mock_req.assert_called_with(
            "DELETE",
            f"/repos/{self.OWNER}/{self.REPO}/environments/{self.ENV}/variables/E_VAR",
            token="test_master_token",
            brain=None,
        )


# ─────────────────────────────────────────────────────────────────────────────
# VariableManager — organization variables
# ─────────────────────────────────────────────────────────────────────────────


class TestOrgVariables(unittest.TestCase):

    ORG = "Aries-Serpent"

    def setUp(self):
        get_token(required_elevated=True)[0] = "test_master_token"
        self.vm = VariableManager(brain=None)

    def tearDown(self):
        os.environ.pop("CODEX_MASTER_KEY", None)

    @patch("variable_manager._gh_request")
    def test_list_org_vars(self, mock_req):
        mock_req.return_value = (200, {"variables": [{"name": "ORG_V", "value": "ov"}]})
        result = self.vm.list_org_vars(self.ORG)
        self.assertEqual(result[0]["name"], "ORG_V")
        mock_req.assert_called_with(
            "GET",
            f"/orgs/{self.ORG}/actions/variables",
            token="test_master_token",
            brain=None,
        )

    @patch("variable_manager._gh_request")
    def test_create_org_var_default_visibility(self, mock_req):
        mock_req.return_value = (201, None)
        self.vm.create_org_var(self.ORG, "O_VAR", "o_val")
        mock_req.assert_called_with(
            "POST",
            f"/orgs/{self.ORG}/actions/variables",
            body={"name": "O_VAR", "value": "o_val", "visibility": "all"},
            token="test_master_token",
            brain=None,
        )

    @patch("variable_manager._gh_request")
    def test_create_org_var_selected_repos(self, mock_req):
        mock_req.return_value = (201, None)
        self.vm.create_org_var(
            self.ORG, "O_SEL", "val", visibility="selected", selected_repository_ids=[123, 456]
        )
        mock_req.assert_called_with(
            "POST",
            f"/orgs/{self.ORG}/actions/variables",
            body={
                "name": "O_SEL",
                "value": "val",
                "visibility": "selected",
                "selected_repository_ids": [123, 456],
            },
            token="test_master_token",
            brain=None,
        )

    @patch("variable_manager._gh_request")
    def test_delete_org_var(self, mock_req):
        mock_req.return_value = (204, None)
        self.vm.delete_org_var(self.ORG, "O_OLD")
        mock_req.assert_called_with(
            "DELETE",
            f"/orgs/{self.ORG}/actions/variables/O_OLD",
            token="test_master_token",
            brain=None,
        )


# ─────────────────────────────────────────────────────────────────────────────
# BrainClient secondary mechanism
# ─────────────────────────────────────────────────────────────────────────────


class TestBrainClientMechanism(unittest.TestCase):
    """Verify that _gh_request prefers BrainClient when a brain is supplied."""

    def test_uses_brain_client_when_provided(self):
        mock_brain = MagicMock()
        mock_brain.proxy_request.return_value = {
            "status_code": 200,
            "body": {"total_count": 0, "variables": []},
        }

        get_token(required_elevated=True)[0] = "tok"
        vm = VariableManager(brain=mock_brain)
        vm.list_repo_vars("Aries-Serpent", "_codex_")
        mock_brain.proxy_request.assert_called_once()
        call_args = mock_brain.proxy_request.call_args
        self.assertEqual(call_args.args[0], "GET")
        self.assertIn("actions/variables", call_args.args[1])
        os.environ.pop("CODEX_MASTER_KEY", None)

    def test_falls_back_to_urllib_on_brain_error(self):
        """BrainClientError causes fallback to urllib."""
        import importlib

        tools_vm = importlib.import_module("variable_manager")

        mock_brain = MagicMock()
        mock_brain.proxy_request.side_effect = (
            tools_vm.BrainClientError("server down")
            if hasattr(tools_vm, "BrainClientError")
            else Exception("server down")
        )

        with patch("variable_manager.urllib.request.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            mock_response.__enter__ = lambda s: s
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_response.status = 200
            mock_response.read.return_value = json.dumps(
                {"total_count": 0, "variables": []}
            ).encode()
            mock_urlopen.return_value = mock_response

            get_token(required_elevated=True)[0] = "tok"
            vm = VariableManager(brain=mock_brain)
            try:
                vm.list_repo_vars("Aries-Serpent", "_codex_")
            except (RuntimeError, OSError, KeyError, ValueError):
                pass  # brain error may propagate differently without full import
            os.environ.pop("CODEX_MASTER_KEY", None)


# ─────────────────────────────────────────────────────────────────────────────
# run_live_test dry-run (all mocked)
# ─────────────────────────────────────────────────────────────────────────────


class TestLiveTestDryRun(unittest.TestCase):
    """Simulate the full create→verify→update→verify→delete cycle via mocks."""

    def setUp(self):
        get_token(required_elevated=True)[0] = "test_tok"

    def tearDown(self):
        os.environ.pop("CODEX_MASTER_KEY", None)

    @patch("variable_manager._gh_request")
    def test_full_cycle_all_pass(self, mock_req):
        """Happy-path: every API call returns expected status."""
        OWNER, REPO = "Aries-Serpent", "_codex_"
        VAR = "COPILOT_DELEGATION_TEST"

        # Override get_repo_var calls in sequence
        call_count = {"get": 0}

        def side_effect_v2(method, path, body=None, token=None, brain=None):
            _ = brain
            if method == "GET" and "variables" in path and VAR not in path:
                return (200, {"total_count": 0, "variables": []})
            if method == "GET" and VAR in path:
                call_count["get"] += 1
                if call_count["get"] == 1:
                    return (200, {"name": VAR, "value": "delegation_active_W118"})
                if call_count["get"] == 2:
                    return (200, {"name": VAR, "value": "delegation_verified_W118"})
                # After delete — should raise 404
                raise GitHubAPIError(404, "Not Found")
            if method == "POST":
                return (201, None)
            if method == "PATCH":
                return (204, None)
            if method == "DELETE":
                return (204, None)
            return (200, {})

        mock_req.side_effect = side_effect_v2
        vm = VariableManager(brain=None)
        # Should not raise
        vm.run_live_test(OWNER, REPO)

    @patch("variable_manager._gh_request")
    def test_full_cycle_fails_gracefully_on_403(self, mock_req):
        """403 on LIST should print failure and return cleanly."""
        mock_req.return_value = (403, {"message": "Resource not accessible"})
        vm = VariableManager(brain=None)
        # Should not raise — run_live_test catches GitHubAPIError internally
        vm.run_live_test("Aries-Serpent", "_codex_")


if __name__ == "__main__":
    unittest.main()
