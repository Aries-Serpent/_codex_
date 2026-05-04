"""
Phase 2 — Scoped Token Broker

Resolves the least-privilege credential for each mutation class, following
the blueprint token resolution order:

    GitHub App token  →  OIDC  →  scoped PAT  →  CODEX_MASTER_KEY (admin only)

The broker never returns a credential with more scope than is necessary for
the requested mutation class.

Usage::

    from codex.autonomy.token_broker import TokenBroker
    from codex.autonomy.registry import AutonomyRegistry, ControlClass

    reg  = AutonomyRegistry.load()
    broker = TokenBroker(registry=reg)
    resolution = broker.resolve(ControlClass.ADVISORY_WRITE)
    # resolution.token  — the actual credential string (or None in dry-run)
    # resolution.source — which tier provided it

Blueprint: .codex/docs/AUTONOMY_BLUEPRINT.md — Phase 2
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .registry import AutonomyRegistry, ControlClass

logger = logging.getLogger(__name__)


class TokenSource(str, Enum):
    """Ordered from most- to least-preferred per blueprint Phase 2."""

    GITHUB_APP = "github_app"
    OIDC = "oidc"
    SCOPED_PAT = "scoped_pat"
    CODEX_MASTER = "codex_master"
    NONE = "none"  # dry-run / no credentials available


# Maximum control class allowed per token source.
# Sources ranked *higher* in the enum (lower .value index) may be used for any
# class at or below their ceiling.
_SOURCE_CEILING: dict[TokenSource, ControlClass] = {
    TokenSource.GITHUB_APP: ControlClass.REPO_STATE_WRITE,
    TokenSource.OIDC: ControlClass.REPO_STATE_WRITE,
    TokenSource.SCOPED_PAT: ControlClass.ADVISORY_WRITE,
    TokenSource.CODEX_MASTER: ControlClass.INFRA_WRITE,
    TokenSource.NONE: ControlClass.READ_ONLY,
}

# Env-var names for each token source
_SOURCE_ENV_VAR: dict[TokenSource, str] = {
    TokenSource.GITHUB_APP: "GITHUB_APP_TOKEN",
    TokenSource.OIDC: "ACTIONS_ID_TOKEN_REQUEST_URL",  # presence signals OIDC availability
    TokenSource.SCOPED_PAT: "CODEX_SCOPED_PAT",
    TokenSource.CODEX_MASTER: "CODEX_MASTER_KEY",
}

# Control-class ordinals for ceiling comparison
_CC_ORDER = list(ControlClass)


def _cc_level(cc: ControlClass) -> int:
    return _CC_ORDER.index(cc)


@dataclass(frozen=True)
class TokenResolution:
    """Result of a token broker lookup."""

    source: TokenSource
    token: Optional[str]          # None when dry_run=True or no creds available
    control_class: ControlClass
    is_dry_run: bool = False
    denial_reason: Optional[str] = None

    @property
    def available(self) -> bool:
        return self.token is not None or self.is_dry_run


class TokenBrokerError(RuntimeError):
    """Raised when no suitable credential is available and an action requires one."""


class TokenBroker:
    """
    Resolves the least-privilege credential for a given mutation class.

    The broker respects the ``token_resolution_order`` from the autonomy
    registry and never escalates beyond what the mutation class requires.
    """

    def __init__(self, registry: Optional[AutonomyRegistry] = None) -> None:
        self._registry = registry or AutonomyRegistry.load()

    def resolve(
        self,
        control_class: ControlClass | str,
        *,
        require: bool = False,
    ) -> TokenResolution:
        """
        Return the lowest-privilege token sufficient for *control_class*.

        Parameters
        ----------
        control_class:
            The mutation class the caller needs to perform.
        require:
            When True, raise :exc:`TokenBrokerError` if no usable credential
            is found (instead of returning a ``TokenResolution`` with
            ``token=None``).
        """
        cc = ControlClass(control_class) if isinstance(control_class, str) else control_class
        cc_lvl = _cc_level(cc)

        # Dry-run mode — return a sentinel without looking up real credentials
        if self._registry.dry_run:
            return TokenResolution(
                source=TokenSource.NONE,
                token=None,
                control_class=cc,
                is_dry_run=True,
            )

        resolution_order: list[str] = self._registry.token_resolution_order
        candidates = [TokenSource(s) for s in resolution_order if s in TokenSource._value2member_map_]

        for source in candidates:
            ceiling = _SOURCE_CEILING.get(source, ControlClass.READ_ONLY)
            if _cc_level(ceiling) < cc_lvl:
                # This source's privilege ceiling is too low for the requested class
                logger.debug(
                    "TokenBroker: skipping %s — ceiling %s < required %s",
                    source.value,
                    ceiling.value,
                    cc.value,
                )
                continue

            token = self._fetch(source)
            if token:
                logger.info(
                    "TokenBroker: resolved %s via %s (ceiling=%s)",
                    cc.value,
                    source.value,
                    ceiling.value,
                )
                return TokenResolution(source=source, token=token, control_class=cc)

        # No credential found
        reason = f"No credential available for {cc.value} in resolution order {resolution_order}"
        logger.warning("TokenBroker: %s", reason)
        if require:
            raise TokenBrokerError(reason)
        return TokenResolution(
            source=TokenSource.NONE,
            token=None,
            control_class=cc,
            denial_reason=reason,
        )

    # ── Internal ──────────────────────────────────────────────────────────────

    def _fetch(self, source: TokenSource) -> Optional[str]:
        """Read the credential for *source* from the environment."""
        env_var = _SOURCE_ENV_VAR.get(source)
        if not env_var:
            return None
        value = os.environ.get(env_var, "").strip()
        return value or None
