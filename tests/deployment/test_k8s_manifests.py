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
        doc = yaml.safe_load(f.read_text(encoding="utf-8"))
        assert isinstance(doc, dict | list)
        if isinstance(doc, dict):
            assert "apiVersion" in doc and "kind" in doc
