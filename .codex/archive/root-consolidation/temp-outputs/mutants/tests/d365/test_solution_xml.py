"""
Test Solution Xml

Test module for solution xml.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("defusedxml", reason="defusedxml required for XML security tests")
from defusedxml import ElementTree

pytest.importorskip("codex.dynamics.solution_xml", reason="codex.dynamics not installed")
from codex.dynamics.solution_xml import (
    emit_solution_xml,
    load_solution_manifest,
)


def test_emit_solution_xml_uses_config(tmp_path: Path) -> None:
    manifest = load_solution_manifest(Path("configs/deployment/d365"))
    manifest = manifest.with_overrides(name="CodexOfflineTest", version="2.0.0.0")
    xml = emit_solution_xml(manifest)
    out = tmp_path / "Solution.xml"
    out.write_text(xml, encoding="utf-8")

    tree = ElementTree.fromstring(xml)
    unique_name = tree.findtext("SolutionManifest/UniqueName")
    version = tree.findtext("SolutionManifest/Version")
    assert unique_name == "CodexOfflineTest", "unique_name is not valid"
    assert version == "2.0.0.0", "version is not valid"

    root_components = tree.findall("SolutionManifest/RootComponents/RootComponent")
    assert any(component.get("schemaName") == "incident" for component in root_components), "Condition must be true"
    assert any(component.get("schemaName") == "account" for component in root_components), "Count must be greater than zero"
