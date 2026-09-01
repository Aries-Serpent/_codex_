from __future__ import annotations

from pathlib import Path

import yaml

from scripts.ci.validate_dependabot_config import validate_dependabot_config

REPO_ROOT = Path(__file__).resolve().parent.parent
DEPENDABOT_PATH = REPO_ROOT / ".github" / "dependabot.yml"


def test_dependabot_config_validator_passes_for_repo_rules():
    document = yaml.safe_load(DEPENDABOT_PATH.read_text(encoding="utf-8"))
    errors = validate_dependabot_config(document)
    assert not errors, "\n".join(errors)


def test_dependabot_config_validator_rejects_null_directory_values():
    document = {
        "version": 2,
        "updates": [
            {
                "package-ecosystem": "pip",
                "directory": None,
                "schedule": {"interval": "weekly"},
                "groups": {"all-dependencies": {"patterns": ["*"]}},
                "open-pull-requests-limit": 1,
            }
        ],
    }

    errors = validate_dependabot_config(document)
    assert any("missing a valid directory" in error for error in errors)


def test_dependabot_config_validator_allows_suppressed_prs_for_ignored_updates():
    document = {
        "version": 2,
        "updates": [
            {
                "package-ecosystem": "pip",
                "directory": "/",
                "schedule": {"interval": "weekly"},
                "ignore": [{"dependency-name": "torch", "versions": [">= 2.3.0"]}],
                "groups": {"python-all": {"patterns": ["*"]}},
                "open-pull-requests-limit": 0,
            }
        ],
    }

    errors = validate_dependabot_config(document)
    assert not errors, "\n".join(errors)
