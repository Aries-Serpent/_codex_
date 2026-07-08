"""
Test Link Id Crossref

Test module for link id crossref.
"""

import json
import subprocess
import sys
from pathlib import Path


def test_crossref_ok(tmp_path):
    report = {
        "snapshot": {
            "capabilities": [{"id": "CAP-001"}],
            "findings": [
                {
                    "id": "FIND-001",
                    "links": {
                        "capability_ids": ["CAP-001"],
                        "patch_ids": ["PATCH-001"],
                    },
                }
            ],
            "repro": {"registry": [{"id": "REPRO-001"}]},
        },
        "patches": [
            {
                "id": "PATCH-001",
                "capability_ids": ["CAP-001"],
                "repro_ids": ["REPRO-001"],
                "finding_ids": ["FIND-001"],
            }
        ],
    }
    p = tmp_path / "r.json"
    p.write_text(json.dumps(report), encoding="utf-8")
    tool = Path("tools/link_id_crossref.py")
    code = subprocess.call([sys.executable, str(tool), "--report", str(p)])
    assert code == 0, "code is not valid"
