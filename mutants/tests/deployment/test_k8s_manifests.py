"""
Test K8S Manifests

Test module for k8s manifests.
"""

#!/usr/bin/env python
# Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5
# Purpose: Validate Kubernetes manifests if present; offline & deterministic.

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CANDIDATE_DIRS = [REPO_ROOT / "deploy", REPO_ROOT / "k8s", REPO_ROOT / "ops"]


def _manifest_files():
    files = []
    for d in CANDIDATE_DIRS:
        if d.exists():
            files.extend(list(d.rglob("*.y*ml")))
    return sorted(files)


@pytest.mark.smoke
def test_deployment_parse_manifests_if_present():
    files = _manifest_files()
    if not files:
        pytest.skip("No deployment manifests found; skipping")
    for f in files:
        content = f.read_text(encoding="utf-8")
        # Handle multi-document YAML files (separated by ---)
        docs = list(yaml.safe_load_all(content))
        assert len(docs) > 0, f"No YAML documents found in {f}"

        for doc in docs:
            if doc is None:  # Skip empty documents
                continue
            assert isinstance(doc, dict | list)
            if isinstance(doc, dict):
                # Skip Helm Chart.yaml files - they have different structure
                is_helm_chart = f.name == "Chart.yaml" or (
                    "name" in doc and "appVersion" in doc and "description" in doc
                )
                if is_helm_chart:
                    continue
                # K8s manifests must have apiVersion and kind
                assert "apiVersion" in doc and "kind" in doc, "Condition must be true"
