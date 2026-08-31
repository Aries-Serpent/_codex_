from __future__ import annotations

from pathlib import Path

import yaml

from scripts.ci.validate_dependabot_config import validate_dependabot_config

REPO_ROOT = Path(__file__).resolve().parent.parent
DEPENDABOT_PATH = REPO_ROOT / ".github" / "dependabot.yml"


def test_dependabot_config_has_no_overlap_and_secret_tokens():
    document = yaml.safe_load(DEPENDABOT_PATH.read_text(encoding="utf-8"))
    errors = validate_dependabot_config(document)
    assert not errors, "\n".join(errors)
