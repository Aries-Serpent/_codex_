"""
Phase 4 — Prompt Registry

Central record of all system, task, continuation, and domain prompts used
by autonomous surfaces.  Every write-capable prompt must be registered here
with a risk class, owner, consuming surfaces, and approved autonomy modes.

Usage::

    from codex.autonomy.prompt_registry import PromptRegistry

    reg = PromptRegistry.load()
    meta = reg.get("system-copilot-agent")
    reg.validate_for_mode(meta, current_mode)   # raises if not approved

Validation CLI::

    python -m codex.autonomy.prompt_registry --validate

Blueprint: .codex/docs/AUTONOMY_BLUEPRINT.md — Phase 4
"""

from __future__ import annotations

import logging
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from codex.logging.structured_logger import logger

from .registry import AutonomyMode, ControlClass

_DEFAULT_REGISTRY_PATH = Path(".codex/prompts/registry.yaml")
_REGISTRY_PATH_ENV = "CODEX_PROMPT_REGISTRY"


@dataclass
class PromptMetadata:
    """Typed metadata for a single registered prompt."""

    prompt_id: str
    path: str
    type: str  # system | task | continuation | domain
    risk_class: str  # ControlClass value
    consumers: list[str] = field(default_factory=list)
    owner: str = ""
    version: str = ""
    approved_for_modes: list[str] = field(default_factory=list)
    description: str = ""

    @property
    def risk(self) -> ControlClass:
        try:
            return ControlClass(self.risk_class)
        except ValueError:
            return ControlClass.ADVISORY_WRITE

    def is_approved_for(self, mode: AutonomyMode) -> bool:
        return mode.value in self.approved_for_modes


class PromptRegistryError(RuntimeError):
    """Raised when prompt governance is violated."""


class PromptRegistry:
    """
    In-memory prompt registry loaded from YAML.

    Provides lookup, mode-approval checks, and CI validation.
    """

    def __init__(self, prompts: Optional[list[PromptMetadata]] = None) -> None:
        self._prompts: dict[str, PromptMetadata] = {p.prompt_id: p for p in (prompts or [])}

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "PromptRegistry":
        """Load registry from YAML file."""
        if path is None:
            env_path = os.environ.get(_REGISTRY_PATH_ENV)
            path = Path(env_path) if env_path else _DEFAULT_REGISTRY_PATH

        try:
            import yaml  # noqa: PLC0415
        except ImportError:  # pragma: no cover
            logger.warning("PyYAML not available; returning empty prompt registry")
            return cls()

        if not path.exists():
            logger.warning("Prompt registry not found at %s", path)
            return cls()

        try:
            raw: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except (IOError, OSError) as exc:  # noqa: BLE001
            logger.error("Failed to parse prompt registry %s: %s", path, exc)
            return cls()

        prompts = [cls._parse_entry(entry) for entry in raw.get("prompts", [])]
        return cls(prompts)

    @staticmethod
    def _parse_entry(entry: dict[str, Any]) -> PromptMetadata:
        return PromptMetadata(
            prompt_id=entry.get("prompt_id", ""),
            path=entry.get("path", ""),
            type=entry.get("type", "task"),
            risk_class=entry.get("risk_class", "ADVISORY_WRITE"),
            consumers=list(entry.get("consumers", [])),
            owner=entry.get("owner", ""),
            version=entry.get("version", ""),
            approved_for_modes=list(entry.get("approved_for_modes", [])),
            description=entry.get("description", ""),
        )

    # ── Lookup ────────────────────────────────────────────────────────────────

    def get(self, prompt_id: str) -> Optional[PromptMetadata]:
        """Return prompt metadata by ID, or None if not found."""
        return self._prompts.get(prompt_id)

    def all_prompts(self) -> list[PromptMetadata]:
        return list(self._prompts.values())

    def by_surface(self, surface_id: str) -> list[PromptMetadata]:
        """Return all prompts consumed by *surface_id*."""
        return [p for p in self._prompts.values() if surface_id in p.consumers]

    def by_risk_class(self, risk_class: ControlClass) -> list[PromptMetadata]:
        return [p for p in self._prompts.values() if p.risk == risk_class]

    # ── Validation ────────────────────────────────────────────────────────────

    def validate_for_mode(
        self,
        prompt: PromptMetadata | str,
        mode: AutonomyMode,
    ) -> None:
        """
        Assert *prompt* is approved for *mode*.

        Parameters
        ----------
        prompt:
            A :class:`PromptMetadata` or a prompt_id string.
        mode:
            Current autonomy mode.
        """
        if isinstance(prompt, str):
            meta = self.get(prompt)
            if meta is None:
                raise PromptRegistryError(f"Unknown prompt_id '{prompt}'")
        else:
            meta = prompt

        if not meta.is_approved_for(mode):
            raise PromptRegistryError(
                f"Prompt '{meta.prompt_id}' (risk={meta.risk_class}) is not approved "
                f"for autonomy_mode={mode.value}. "
                f"Approved modes: {meta.approved_for_modes}"
            )

    def validate_all(self) -> list[str]:
        """
        Validate all registered prompts.

        Returns a list of error strings (empty = all valid).
        """
        errors: list[str] = []
        for p in self._prompts.values():
            if not p.prompt_id:
                errors.append("Entry missing prompt_id")
            if not p.path:
                errors.append(f"{p.prompt_id}: missing path")
            if not p.risk_class:
                errors.append(f"{p.prompt_id}: missing risk_class")
            try:
                ControlClass(p.risk_class)
            except ValueError:
                errors.append(f"{p.prompt_id}: invalid risk_class '{p.risk_class}'")
            for mode_str in p.approved_for_modes:
                try:
                    AutonomyMode(mode_str)
                except ValueError:
                    errors.append(f"{p.prompt_id}: invalid approved_for_modes entry '{mode_str}'")
        return errors


# ── CLI entry-point ───────────────────────────────────────────────────────────


def _main() -> None:
    import argparse  # noqa: PLC0415

    parser = argparse.ArgumentParser(description="Validate the prompt registry")
    parser.add_argument("--validate", action="store_true", help="Run validation checks")
    parser.add_argument("--list", action="store_true", help="List all registered prompts")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    reg = PromptRegistry.load()

    if args.list or not args.validate:
        for p in reg.all_prompts():
            logger.info(f"  {p.prompt_id:40s}  {p.risk_class:20s}  {p.type}")

    if args.validate:
        errors = reg.validate_all()
        if errors:
            for err in errors:
                logger.error(f"ERROR: {err}")
            sys.exit(1)
        logger.info(f"✅  Prompt registry valid ({len(reg.all_prompts())} prompts)")


if __name__ == "__main__":
    _main()
