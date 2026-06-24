"""Load skill manifests from Markdown docs with YAML frontmatter."""

from __future__ import annotations

import logging
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import yaml

from .manifest import SkillManifest

LOGGER = logging.getLogger(__name__)

_FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)


def _split_frontmatter(raw: str) -> tuple[dict[str, Any], str]:
    """Extract YAML frontmatter and body from a Markdown document."""
    match = _FRONTMATTER_PATTERN.match(raw)
    if not match:
        return {}, raw
    frontmatter, body = match.groups()
    try:
        data = yaml.safe_load(frontmatter) or {}
        if not isinstance(data, dict):
            LOGGER.warning("Frontmatter is not a mapping; defaulting to empty dict")
            data = {}
    except yaml.YAMLError as exc:
        LOGGER.warning("Failed to parse frontmatter: %s", exc)
        data = {}
    return data, body


class SkillDocLoader:
    """Utility for reading skill manifests from Markdown doc files.

    Loads lightweight :class:`~codex.skills.manifest.SkillManifest` dataclasses
    from Markdown files with YAML frontmatter.  For full Pydantic-model registry
    integration use :func:`codex.skills.doc_loader.load_agent_docs_as_skills`.
    """

    def load_manifest(self, path: str | Path) -> SkillManifest:
        """Load a single manifest from a Markdown file."""
        resolved = Path(path)
        raw = resolved.read_text(encoding="utf-8")
        frontmatter, _ = _split_frontmatter(raw)
        capability_tags = (
            frontmatter.get("capabilities") or frontmatter.get("capability_tags") or []
        )
        return SkillManifest(
            name=frontmatter.get("name") or frontmatter.get("title") or resolved.stem,
            description=frontmatter.get("description", ""),
            capability_tags=capability_tags,
            integration_points=frontmatter.get("integration_points", []),
            enforcement_tier=frontmatter.get("enforcement_tier", "UNSPECIFIED"),
            budget_tokens=frontmatter.get("budget_tokens"),
            timeout_ms=frontmatter.get("timeout_ms"),
            doc_path=str(resolved),
            metadata={
                key: value
                for key, value in frontmatter.items()
                if key
                not in {
                    "name",
                    "title",
                    "description",
                    "capabilities",
                    "capability_tags",
                    "integration_points",
                    "enforcement_tier",
                    "budget_tokens",
                    "timeout_ms",
                }
            },
        )

    def load_many(self, paths: Iterable[str | Path]) -> list[SkillManifest]:
        """Load multiple manifests and optionally register them."""
        manifests: list[SkillManifest] = []
        for path in paths:
            try:
                manifests.append(self.load_manifest(path))
            except FileNotFoundError:
                LOGGER.warning("Skill doc not found: %s", path)
            except (IOError, OSError) as exc:
                LOGGER.warning("Failed to load skill doc %s: %s", path, exc)
        return manifests
