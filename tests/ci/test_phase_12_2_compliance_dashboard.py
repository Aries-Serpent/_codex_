from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module():
    module_path = (
        Path(__file__).resolve().parents[2]
        / "scripts"
        / "ci"
        / "phase_12_2_compliance_dashboard.py"
    )
    spec = importlib.util.spec_from_file_location("phase_12_2_compliance_dashboard", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_heuristic_secret_scan_diff_skips_allowlisted_lines(monkeypatch):
    mod = _load_module()

    def fake_git(*args: str, check: bool = False):
        return (
            0,
            '\n'.join(
                [
                    '+++ b/src/codex/auth/github_app.py',
                    (
                        '+verifier = WebhookVerifier(secret="webhook-secret")  '
                        "<!-- pragma: allowlist secret -->"
                    ),
                    '+token = "******"',
                ]
            ),
            "",
        )

    monkeypatch.setattr(mod, "_git", fake_git)

    found, details = mod._heuristic_secret_scan_diff()

    assert found is True
    assert "webhook-secret" not in details
    assert "******" not in details
    assert 'token = "******"'[:20] in details
