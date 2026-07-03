from __future__ import annotations

import importlib
import importlib.util
import os
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import Request


class ITACoverageTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env_patch = patch.dict(
            os.environ,
            {
                "ENVIRONMENT": "development",
                "ITA_API_KEY": "ita-test-key",
                "ITA_API_KEY_PEPPER": "ita-test-pepper",
            },
        )
        self._env_patch.start()
        self.addCleanup(self._env_patch.stop)
        os.environ.pop("CORS_ORIGINS", None)
        self.main = importlib.reload(importlib.import_module("services.ita.app.main"))

    def test_get_request_context_success(self) -> None:
        request = Request({"type": "http", "headers": [], "method": "GET", "path": "/"})
        request.state.context = self.main.RequestContext(request_id="req-1", api_key_hash="hash")
        context = importlib.import_module("asyncio").run(self.main.get_request_context(request))
        self.assertEqual(context.request_id, "req-1")

    def test_repo_hygiene_bad_check_returns_400(self) -> None:
        from fastapi.testclient import TestClient

        with TestClient(self.main.app) as client:
            response = client.post(
                "/repo/hygiene",
                headers={"X-API-Key": "ita-test-key", "X-Request-Id": "req-2"},
                json={"diff": "++ b/file.py", "checks": ["unknown"]},
            )
        self.assertEqual(response.status_code, 400)

    def test_issue_api_key_script_main(self) -> None:
        script_path = Path("services/ita/scripts/issue_api_key.py")
        fake_module = types.ModuleType("app.security")

        class _Store:
            def __init__(self, path=None):
                self.path = path

            def issue_key(self) -> str:
                return "issued-key"

        fake_module.ApiKeyStore = _Store
        with patch.dict("sys.modules", {"app.security": fake_module}):
            spec = importlib.util.spec_from_file_location("ita_issue_key", script_path)
            assert spec and spec.loader
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            with patch.object(module, "parse_args", return_value=types.SimpleNamespace(path=None)):
                self.assertEqual(module.main(), 0)
