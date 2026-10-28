"""Typed authority evidence boundary; even valid evidence cannot activate anything."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Literal, Protocol

from .core import Clock, utc

ROLES = ("proposer", "implementer", "verifier", "approver")
PROVIDER_SCHEMA = "codex.authority-provider.v1"


@dataclass(frozen=True)
class AuthorityRequest:
    """An exact operation, target and artifact, not a grant of authority."""

    operation: str
    target: str
    artifact: str


@dataclass(frozen=True)
class Identity:
    role: str
    actor: str
    evidence_refs: tuple[str, ...]
    authenticated: bool


@dataclass(frozen=True)
class Attestation:
    """Provider assertion; trust establishment belongs to the external provider."""

    schema: str
    request: AuthorityRequest
    identities: tuple[Identity, ...]
    valid_from: datetime
    expires_at: datetime
    revoked: bool
    revocation_checked_at: datetime
    evidence_refs: tuple[str, ...]
    assurance: Literal["fixture", "externally-verified"]


@dataclass(frozen=True)
class ProviderUnavailable:
    reason: Literal["unavailable", "unsupported"] = "unavailable"


class AuthorityProvider(Protocol):
    """Injected by trusted application code, never discovered in imported records."""

    def attest(self, request: AuthorityRequest) -> Attestation | ProviderUnavailable: ...


@dataclass(frozen=True)
class Evaluation:
    status: Literal["valid-mechanics", "invalid", "unavailable", "unsupported", "malformed"]
    reasons: tuple[str, ...]
    provider_assurance: str
    activation_allowed: Literal[False] = False


def _aware(value: object) -> bool:
    return (
        isinstance(value, datetime) and value.tzinfo is not None and value.utcoffset() is not None
    )


def _refs(value: object) -> bool:
    return (
        isinstance(value, tuple)
        and bool(value)
        and all(isinstance(ref, str) and bool(ref.strip()) for ref in value)
    )


def evaluate(
    request: AuthorityRequest, provider: AuthorityProvider | None = None, clock: Clock = utc
) -> Evaluation:
    """Validate deterministic mechanics only, preserving all applicable failures."""
    denied = ("ACTIVATION_DISABLED",)
    if (
        not isinstance(request, AuthorityRequest)
        or not isinstance(request.operation, str)
        or not request.operation.strip()
        or not isinstance(request.target, str)
        or not request.target.strip()
        or not isinstance(request.artifact, str)
        or re.fullmatch(r"[a-f0-9]{64}", request.artifact) is None
    ):
        return Evaluation("malformed", denied + ("MALFORMED_REQUEST",), "unknown")
    if provider is None:
        return Evaluation("unavailable", denied + ("PROVIDER_UNAVAILABLE",), "unknown")
    try:
        assertion = provider.attest(request)
    except Exception:
        return Evaluation("unavailable", denied + ("PROVIDER_FAILURE",), "unknown")
    if isinstance(assertion, ProviderUnavailable):
        if assertion.reason not in ("unsupported", "unavailable"):
            return Evaluation("malformed", denied + ("MALFORMED_PROVIDER",), "unknown")
        reason = (
            "PROVIDER_UNSUPPORTED" if assertion.reason == "unsupported" else "PROVIDER_UNAVAILABLE"
        )
        return Evaluation(assertion.reason, denied + (reason,), "unknown")
    if not isinstance(assertion, Attestation):
        return Evaluation("malformed", denied + ("MALFORMED_PROVIDER",), "unknown")
    if assertion.schema != PROVIDER_SCHEMA:
        return Evaluation("unsupported", denied + ("UNSUPPORTED_PROVIDER_SCHEMA",), "unknown")
    if (
        not isinstance(assertion.request, AuthorityRequest)
        or not isinstance(assertion.identities, tuple)
        or not all(
            isinstance(i, Identity)
            and isinstance(i.role, str)
            and isinstance(i.actor, str)
            and bool(i.actor.strip())
            and type(i.authenticated) is bool
            and _refs(i.evidence_refs)
            for i in assertion.identities
        )
        or not all(
            _aware(t)
            for t in (assertion.valid_from, assertion.expires_at, assertion.revocation_checked_at)
        )
        or type(assertion.revoked) is not bool
        or not _refs(assertion.evidence_refs)
        or assertion.assurance not in ("fixture", "externally-verified")
    ):
        return Evaluation("malformed", denied + ("MALFORMED_PROVIDER",), "unknown")
    now = clock()
    if not _aware(now):
        return Evaluation("malformed", denied + ("INVALID_CLOCK",), "unknown")
    now = now.astimezone(timezone.utc)
    valid_from = assertion.valid_from.astimezone(timezone.utc)
    expires_at = assertion.expires_at.astimezone(timezone.utc)
    revocation_checked_at = assertion.revocation_checked_at.astimezone(timezone.utc)
    reasons = []
    for field, code in (
        ("operation", "OPERATION_MISMATCH"),
        ("target", "TARGET_MISMATCH"),
        ("artifact", "ARTIFACT_MISMATCH"),
    ):
        if getattr(assertion.request, field) != getattr(request, field):
            reasons.append(code)
    if sorted(i.role for i in assertion.identities) != sorted(ROLES):
        reasons.append("REQUIRED_ROLES")
    actors = [i.actor for i in assertion.identities]
    if len(set(actors)) != len(actors):
        reasons.append("ACTOR_COLLISION")
    if any(not i.authenticated for i in assertion.identities):
        reasons.append("UNVERIFIED_IDENTITY")
    if valid_from >= expires_at:
        reasons.append("INVALID_VALIDITY_INTERVAL")
    if now < valid_from:
        reasons.append("NOT_YET_VALID")
    if now >= expires_at:
        reasons.append("EXPIRED")
    if assertion.revoked:
        reasons.append("REVOKED")
    if not (now - timedelta(minutes=5) <= revocation_checked_at <= now):
        reasons.append("STALE_OR_FUTURE_REVOCATION")
    return Evaluation(
        "invalid" if reasons else "valid-mechanics",
        denied + tuple(sorted(reasons)),
        assertion.assurance,
    )
