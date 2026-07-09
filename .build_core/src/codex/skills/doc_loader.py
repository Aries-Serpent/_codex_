"""Load AI agent Markdown docs as registered skills.

Reads YAML frontmatter from ``.github/agents/*.md`` files and converts the
``capabilities`` / ``capability_tags`` fields into :class:`SkillManifest`
objects that can be registered in the :class:`SkillRegistry`.

This bridges the gap between the human-authored agent documentation and the
programmatic skill registry, allowing Copilot agents to discover and invoke
capabilities declared in Markdown.

Usage::

    from codex.skills.doc_loader import load_agent_docs_as_skills

    skills = load_agent_docs_as_skills()
    for s in skills:
        logger.info(s.manifest.id, s.manifest.capability_tags)
"""

from __future__ import annotations

import re
from pathlib import Path
from types import ModuleType
from typing import Any, Literal

from codex.logging.structured_logger import logger

from .models import BudgetConfig, DocMeta, PolicyConfig, RegisteredSkill, SkillManifest

yaml: ModuleType | None
try:
    import yaml as _yaml_module

    yaml = _yaml_module
except (IOError, OSError):  # pragma: no cover
    yaml = None


def _repo_root() -> Path:
    """Walk up from this file to find the repo root (containing pyproject.toml)."""
    candidate = Path(__file__).resolve()
    while candidate != candidate.parent:
        if (candidate / "pyproject.toml").exists():
            return candidate
        candidate = candidate.parent
    return Path.cwd()


# Default agent docs location derived robustly from repo root
_DEFAULT_AGENTS_ROOT = _repo_root() / ".github" / "agents"

# Regex to extract YAML frontmatter block between --- delimiters
_RE_FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


def _extract_frontmatter(text: str) -> dict[str, Any]:
    """Parse YAML frontmatter from a Markdown file.  Returns {} on failure."""
    if yaml is None:  # pragma: no cover
        return {}
    match = _RE_FRONTMATTER.match(text)
    if not match:
        return {}
    try:
        data = yaml.safe_load(match.group(1)) or {}
        return data if isinstance(data, dict) else {}
    except (IOError, OSError):
        return {}


def _frontmatter_to_manifest(
    fm: dict[str, Any],
    *,
    doc_path: str,
    text: str,
) -> SkillManifest | None:
    """Convert agent frontmatter dict to a :class:`SkillManifest`.

    Parameters
    ----------
    fm:
        Parsed YAML frontmatter dict.
    doc_path:
        Relative path of the source ``.md`` file (used as doc_id).
    text:
        Full Markdown content (used to compute a lightweight hash).
    """
    name = fm.get("name") or Path(doc_path).stem.replace("-", " ").title()

    # Collect capability tags from multiple possible keys
    tags: list[str] = []
    for key in ("capability_tags", "capabilities", "capability"):
        val = fm.get(key)
        if isinstance(val, list):
            tags.extend(str(t) for t in val)
        elif isinstance(val, str):
            tags.extend(val.split(","))

    # Unique, lower-cased, stripped tags
    tags = sorted({t.strip().lower() for t in tags if t.strip()})

    skill_id = fm.get("id") or f"agent.{Path(doc_path).stem.replace('-', '_').lower()}"
    version = str(fm.get("version", "1.0.0"))
    description = fm.get("description", "")
    if isinstance(description, str):
        description = description.strip()

    # Build a lightweight hash from the text content
    import hashlib

    doc_hash = hashlib.sha256(text.encode()).hexdigest()[:16]

    # Risk tier inference from autonomy_model or enforcement_tier
    autonomy = str(fm.get("autonomy_model", "E")).upper()
    enforcement = str(fm.get("enforcement_tier", "SOFT")).upper()
    risk_tier: Literal["low", "medium", "high"]
    if autonomy == "D_CAPABLE" or enforcement == "GROUNDED":
        risk_tier = "high"
    elif enforcement == "PARTIAL":
        risk_tier = "medium"
    else:
        risk_tier = "low"

    # Entrypoint: use "integration_points" if available, else stub
    integration_points = fm.get("integration_points", [])
    if integration_points and isinstance(integration_points, list):
        # Use the first .py integration point if any
        py_points = [p for p in integration_points if str(p).endswith(".py")]
        entrypoint = (
            py_points[0].replace("/", ".").rstrip(".py") + ":run"
            if py_points
            else f"codex.skills.stubs:{skill_id.replace('.', '_')}"
        )
    else:
        entrypoint = f"codex.skills.stubs:{skill_id.replace('.', '_')}"

    return SkillManifest(
        id=skill_id,
        version=version,
        name=name,
        description=description,
        capability_tags=tags,
        entrypoint=entrypoint,
        policy=PolicyConfig(
            allowlist=["*"],
            risk_tier=risk_tier,
            budgets=BudgetConfig(calls=100, tokens=50_000, wallclock_ms=60_000),
        ),
        doc=DocMeta(
            doc_id=doc_path,
            hash=doc_hash,
            aais_score=0.0,
            token_count=len(text.split()),
        ),
    )


def load_agent_docs_as_skills(
    agents_root: Path | None = None,
) -> list[RegisteredSkill]:
    """Scan ``.github/agents/*.md`` and return :class:`RegisteredSkill` objects.

    Parameters
    ----------
    agents_root:
        Override the agents directory (default: ``<repo_root>/.github/agents``).

    Returns
    -------
    list[RegisteredSkill]
        One entry per parseable agent Markdown file.
    """
    root = agents_root or _DEFAULT_AGENTS_ROOT
    if not root.exists():
        logger.debug("DocLoader: agents root '%s' not found", root)
        return []

    skills: list[RegisteredSkill] = []
    for md_file in sorted(root.glob("*.md")):
        try:
            text = md_file.read_text(encoding="utf-8", errors="replace")
            fm = _extract_frontmatter(text)
            if not fm:
                continue
            doc_path = str(md_file.relative_to(md_file.parents[2]))
            manifest = _frontmatter_to_manifest(fm, doc_path=doc_path, text=text)
            if manifest is None:
                continue
            skills.append(RegisteredSkill(manifest=manifest, source_path=str(md_file)))
        except (IOError, OSError) as exc:
            logger.debug("DocLoader: skipping '%s': %s", md_file, exc)

    logger.info("DocLoader: loaded %d agent doc skills from '%s'", len(skills), root)
    return skills


__all__ = ["load_agent_docs_as_skills"]
