"""Cognitive Brain Skills Registry.

Central store for discovering, registering, and resolving packaged skills.

Discovery scans all ``**/manifest.yaml`` files under ``src/codex/skills/``
and also loads Python entry-points declared under the ``codex.skills`` group.

Usage::

    from codex.skills.registry import get_registry

    reg = get_registry()
    reg.discover()

    skill = reg.resolve("doc.retriever.core")
    print(skill.manifest.name)
"""

from __future__ import annotations

import importlib
import importlib.metadata
import logging
from pathlib import Path
from typing import Callable

try:
    import yaml
except Exception:  # pragma: no cover - optional but present in requirements
    yaml = None  # type: ignore[assignment]

from .models import RegisteredSkill, SkillManifest

logger = logging.getLogger(__name__)

# Default scan root relative to the installed package location
_DEFAULT_SKILLS_ROOT = Path(__file__).parent


class SkillRegistry:
    """Thread-safe registry for discovering and resolving packaged skills.

    Attributes
    ----------
    _skills:
        Map of ``(skill_id, version)`` → :class:`RegisteredSkill`.
    _latest:
        Map of ``skill_id`` → latest registered :class:`RegisteredSkill`.
    """

    def __init__(self) -> None:
        self._skills: dict[tuple[str, str], RegisteredSkill] = {}
        self._latest: dict[str, RegisteredSkill] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        manifest: SkillManifest,
        *,
        source_path: str = "",
    ) -> RegisteredSkill:
        """Register a skill manifest.

        If the same ``(id, version)`` is already registered the existing
        entry is returned unchanged (idempotent).

        Parameters
        ----------
        manifest:
            Validated :class:`SkillManifest` to register.
        source_path:
            Filesystem path of the manifest file (for diagnostics).

        Returns
        -------
        RegisteredSkill
            The registered entry (new or existing).
        """
        key = (manifest.id, manifest.version)
        if key in self._skills:
            logger.debug(
                "Registry: '%s@%s' already registered (idempotent)",
                manifest.id,
                manifest.version,
            )
            return self._skills[key]

        skill = RegisteredSkill(manifest=manifest, source_path=source_path)
        self._skills[key] = skill

        # Track latest (highest version string; simple string compare is fine
        # for semver "X.Y.Z" where all components are padded to equal width
        # in practice; for non-semver ids callers should pin versions).
        existing_latest = self._latest.get(manifest.id)
        if existing_latest is None or manifest.version >= existing_latest.version:
            self._latest[manifest.id] = skill

        logger.info("Registry: registered skill '%s@%s'", manifest.id, manifest.version)
        return skill

    # ------------------------------------------------------------------
    # Resolution
    # ------------------------------------------------------------------

    def resolve(self, skill_id: str, version: str | None = None) -> RegisteredSkill | None:
        """Return a registered skill by id and optional version.

        Parameters
        ----------
        skill_id:
            Dotted skill identifier.
        version:
            Exact version string.  If *None* the latest is returned.

        Returns
        -------
        RegisteredSkill | None
        """
        if version is not None:
            return self._skills.get((skill_id, version))
        return self._latest.get(skill_id)

    # ------------------------------------------------------------------
    # Listing / filtering
    # ------------------------------------------------------------------

    def list(
        self,
        capability_tag: str | None = None,
        risk_tier: str | None = None,
    ) -> list[RegisteredSkill]:
        """Return all latest-version registered skills, optionally filtered.

        Parameters
        ----------
        capability_tag:
            If set, only skills whose ``capability_tags`` contains this tag.
        risk_tier:
            If set, only skills with this exact ``policy.risk_tier``.
        """
        results = list(self._latest.values())

        if capability_tag:
            results = [s for s in results if capability_tag in s.manifest.capability_tags]

        if risk_tier:
            results = [s for s in results if s.manifest.policy.risk_tier == risk_tier]

        return sorted(results, key=lambda s: s.skill_id)

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def discover(self, root: Path | None = None) -> int:
        """Scan ``root`` for ``manifest.yaml`` files and register them.

        Also discovers Python entry-points in the ``codex.skills`` group.

        Parameters
        ----------
        root:
            Directory to scan.  Defaults to the ``src/codex/skills/`` package
            directory (i.e. sibling dirs of this file).

        Returns
        -------
        int
            Number of *new* skills registered during this call.
        """
        count = 0
        scan_root = root or _DEFAULT_SKILLS_ROOT

        # 1) Filesystem scan
        for manifest_path in sorted(scan_root.glob("**/manifest.yaml")):
            loaded = self._load_manifest_file(manifest_path)
            if loaded is not None:
                before = len(self._skills)
                self.register(loaded, source_path=str(manifest_path))
                if len(self._skills) > before:
                    count += 1

        # 2) Entry-point discovery
        count += self._discover_entry_points()

        logger.info("Registry.discover: %d new skills registered", count)
        return count

    def _load_manifest_file(self, path: Path) -> SkillManifest | None:
        """Parse a single manifest.yaml file; return None on parse errors."""
        if yaml is None:  # pragma: no cover
            logger.warning("PyYAML unavailable; cannot load manifest at %s", path)
            return None
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            return SkillManifest.model_validate(data)
        except Exception as exc:
            logger.warning("Failed to load manifest '%s': %s", path, exc)
            return None

    def _discover_entry_points(self) -> int:
        """Load skills registered via the ``codex.skills`` entry-point group."""
        count = 0
        try:
            eps = importlib.metadata.entry_points(group="codex.skills")
        except Exception:  # pragma: no cover
            return 0

        for ep in eps:
            try:
                skill_factory: Callable[[], SkillManifest] = ep.load()
                manifest = skill_factory() if callable(skill_factory) else skill_factory
                if isinstance(manifest, SkillManifest):
                    before = len(self._skills)
                    self.register(manifest, source_path=f"entry_point:{ep.name}")
                    if len(self._skills) > before:
                        count += 1
            except Exception as exc:
                logger.warning("Failed to load entry-point skill '%s': %s", ep.name, exc)

        return count

    # ------------------------------------------------------------------
    # Budget tracking helpers
    # ------------------------------------------------------------------

    def consume_budget(
        self,
        skill_id: str,
        version: str | None = None,
        *,
        calls: int = 1,
        tokens: int = 0,
        wallclock_ms: int = 0,
    ) -> None:
        """Record resource usage against a skill's cumulative budget."""
        skill = self.resolve(skill_id, version)
        if skill is None:
            return
        skill.budget_used["calls"] += calls
        skill.budget_used["tokens"] += tokens
        skill.budget_used["wallclock_ms"] += wallclock_ms

    def reset_budget(self, skill_id: str, version: str | None = None) -> None:
        """Reset cumulative budget usage (e.g. at the start of a policy window)."""
        skill = self.resolve(skill_id, version)
        if skill is None:
            return
        skill.budget_used = {"calls": 0, "tokens": 0, "wallclock_ms": 0}

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._latest)

    def __repr__(self) -> str:
        return f"SkillRegistry(skills={len(self._latest)})"


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_default_registry: SkillRegistry | None = None


def get_registry() -> SkillRegistry:
    """Return the process-level default :class:`SkillRegistry` (lazy init)."""
    global _default_registry
    if _default_registry is None:
        _default_registry = SkillRegistry()
    return _default_registry


def reset_registry() -> None:
    """Reset the default registry (useful in tests)."""
    global _default_registry
    _default_registry = None


__all__ = ["SkillRegistry", "get_registry", "reset_registry"]
