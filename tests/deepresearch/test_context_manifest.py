"""
Test Context Manifest

Test module for context manifest.
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def test_manifest_contains_apis(tmp_path):
    apis = tmp_path / "docs/deepresearch/apis"
    apis.mkdir(parents=True, exist_ok=True)
    (apis / "a.yaml").write_text("openapi: 3.1.0", encoding="utf-8")
    (apis / "b.json").write_text('{"openapi":"3.1.0"}', encoding="utf-8")

    repo_root = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    py_path = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(repo_root) if not py_path else os.pathsep.join([str(repo_root), py_path])

    code = subprocess.call(
        [
            sys.executable,
            "-c",
            "import scripts.deepresearch.generate_context_manifest as m; m.main()",
        ],
        cwd=tmp_path,
        env=env,
    )
    assert code == 0, "code is not valid"

    manifest = json.loads(
        (tmp_path / "deepresearch/context_manifest.json").read_text(encoding="utf-8")
    )
    assert isinstance(manifest.get("apis"), list)
    assert len(manifest["apis"]) == 2, "Collection must not be empty"
