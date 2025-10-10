#!/usr/bin/env python
# Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5
# Purpose: Validate local CI tooling presence (pre-commit); avoid enabling GH Actions.

from __future__ import annotations

from pathlib import Path

import pytest

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
PRE_COMMIT = REPO_ROOT / ".pre-commit-config.yaml"


@pytest.mark.smoke
def test_ci_precommit_config_present_and_valid_yaml():
    if not PRE_COMMIT.exists():
        pytest.skip(".pre-commit-config.yaml not present")
    data = yaml.safe_load(PRE_COMMIT.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    repos = data.get("repos", [])
    assert isinstance(repos, list)
