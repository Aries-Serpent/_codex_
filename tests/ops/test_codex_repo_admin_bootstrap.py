from __future__ import annotations

import json
from importlib import import_module


def _m():
    return import_module("scripts.ops.codex_repo_admin_bootstrap")


def test_dry_run_plan_shape(capsys):
    m = _m()
    rc = m.main(["--owner", "o", "--repo", "r"])  # dry-run
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["dry_run"] is True
    plan = out["plan"]
    assert plan["target"] == {"owner": "o", "repo": "r", "branch": "main"}
    assert isinstance(plan["repo_settings"], dict)
    assert isinstance(plan["branch_protection"], dict)
    assert isinstance(plan["labels"], list)
