from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from codex_crm.pa_legacy import PowerAutomatePackageError, read_pa_legacy, to_template


def _create_pa_zip(tmp_path: Path) -> Path:
    manifest = {"name": "Sample", "version": "1.0"}
    flow_payload = {
        "name": "SampleFlow",
        "properties": {
            "connectionReferences": {
                "shared_outlook": {
                    "displayName": "Outlook",
                    "connectionName": "shared-outlook-123",
                    "id": "/providers/Microsoft.PowerApps/apis/shared_outlook",
                }
            }
        },
    }

    archive_path = tmp_path / "pa.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("manifest.json", json.dumps(manifest))
        archive.writestr("flows/sample.json", json.dumps(flow_payload))
    return archive_path


def test_read_pa_legacy_round_trip(tmp_path: Path) -> None:
    archive_path = _create_pa_zip(tmp_path)

    package = read_pa_legacy(archive_path)
    assert package["manifest"]["name"] == "Sample"
    assert "sample" in package["flows"]

    template = to_template(package)
    assert template["manifest"]["version"] == "1.0"
    assert "sample" in template["flows"]

    connections = template["connections"]["sample"]
    assert connections == ["shared_outlook"]
    connection_ref = template["flows"]["sample"]["properties"]["connectionReferences"][
        "shared_outlook"
    ]
    assert connection_ref["connectionName"] == "{{SHARED_OUTLOOK_CONNECTION}}"


def test_to_template_without_flows_raises() -> None:
    with pytest.raises(PowerAutomatePackageError):
        to_template({"manifest": {}, "flows": {}})
