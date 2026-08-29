"""
Test Context Manifest

Test module for context manifest.
"""

import json
import subprocess
import sys


def test_manifest_contains_apis(tmp_path):
    apis = tmp_path / "docs/deepresearch/apis"
    apis.mkdir(parents=True, exist_ok=True)
    (apis / "a.yaml").write_text("openapi: 3.1.0", encoding="utf-8")
    (apis / "b.json").write_text('{"openapi":"3.1.0"}', encoding="utf-8")

    code = subprocess.call(
        [
            sys.executable,
            "-c",
            "import scripts.deepresearch.generate_context_manifest as m; m.main()",
        ],
        cwd=tmp_path,
    )
    assert code == 0, "code is not valid"

    manifest = json.loads(
        (tmp_path / "deepresearch/context_manifest.json").read_text(encoding="utf-8")
    )
    assert isinstance(manifest.get("apis"), list)
    assert len(manifest["apis"]) == 2, "Collection must not be empty"
