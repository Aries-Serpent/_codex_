"""Fixture attestations exercise validation, never production trust or activation."""

from __future__ import annotations

import copy
import json
from dataclasses import asdict, replace
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from codex.institutional import authority as a
from codex.institutional import core
from codex.institutional.__main__ import main

NOW = datetime(2026, 10, 24, 22, tzinfo=timezone.utc)
REQUEST = a.AuthorityRequest("activate", "/fixture", "a" * 64)


class FixtureProvider:
    def __init__(self, assertion):
        self.assertion = assertion

    def attest(self, request):
        return self.assertion


def fixture():
    return a.Attestation(
        a.PROVIDER_SCHEMA,
        REQUEST,
        tuple(a.Identity(role, f"fixture:{role}", (f"evidence:{role}",), True) for role in a.ROLES),
        NOW - timedelta(minutes=1),
        NOW + timedelta(minutes=1),
        False,
        NOW,
        ("fixture:approval-bound-to-candidate",),
        "fixture",
    )


def evaluate(value):
    return a.evaluate(REQUEST, FixtureProvider(value), lambda: NOW)


def test_valid_fixture_is_not_operational_authority():
    result = evaluate(fixture())
    assert result.status == "valid-mechanics"
    assert result.provider_assurance == "fixture"
    assert result.activation_allowed is False
    assert result.reasons == ("ACTIVATION_DISABLED",)
    result = evaluate(replace(fixture(), assurance="externally-verified"))
    assert result.status == "valid-mechanics"
    assert not result.activation_allowed


@pytest.mark.parametrize(
    "provider,status,reason",
    [
        (None, "unavailable", "PROVIDER_UNAVAILABLE"),
        (FixtureProvider(a.ProviderUnavailable()), "unavailable", "PROVIDER_UNAVAILABLE"),
        (
            FixtureProvider(a.ProviderUnavailable("unsupported")),
            "unsupported",
            "PROVIDER_UNSUPPORTED",
        ),
        (FixtureProvider({"approved": True}), "malformed", "MALFORMED_PROVIDER"),
        (
            FixtureProvider(replace(fixture(), schema="codex.authority-provider.v2")),
            "unsupported",
            "UNSUPPORTED_PROVIDER_SCHEMA",
        ),
    ],
)
def test_missing_unverified_and_unsupported_providers(provider, status, reason):
    result = a.evaluate(REQUEST, provider, lambda: NOW)
    assert result.status == status
    assert reason in result.reasons
    assert not result.activation_allowed


def test_provider_failure_does_not_leak_exception_details():
    class Fails:
        def attest(self, request):
            raise RuntimeError("sensitive provider detail")

    result = a.evaluate(REQUEST, Fails(), lambda: NOW)
    assert result.status == "unavailable"
    assert "PROVIDER_FAILURE" in result.reasons
    assert "sensitive" not in repr(result)


@pytest.mark.parametrize(
    "field,value,reason",
    [
        ("operation", "write", "OPERATION_MISMATCH"),
        ("target", "/other", "TARGET_MISMATCH"),
        ("artifact", "b" * 64, "ARTIFACT_MISMATCH"),
    ],
)
def test_exact_approval_binding(field, value, reason):
    result = evaluate(replace(fixture(), request=replace(REQUEST, **{field: value})))
    assert result.status == "invalid"
    assert reason in result.reasons


def test_separation_and_authenticated_identity_evidence():
    value = fixture()
    identities = list(value.identities)
    identities[3] = replace(identities[3], actor=identities[0].actor, authenticated=False)
    result = evaluate(replace(value, identities=tuple(identities)))
    assert {"ACTOR_COLLISION", "UNVERIFIED_IDENTITY"} <= set(result.reasons)
    result = evaluate(replace(value, identities=value.identities[:3]))
    assert "REQUIRED_ROLES" in result.reasons
    identities = list(value.identities)
    identities[1] = replace(identities[1], role="approver")
    assert "REQUIRED_ROLES" in evaluate(replace(value, identities=tuple(identities))).reasons


@pytest.mark.parametrize(
    "change,reason",
    [
        ({"expires_at": NOW}, "EXPIRED"),
        ({"valid_from": NOW + timedelta(seconds=1)}, "NOT_YET_VALID"),
        ({"valid_from": NOW + timedelta(minutes=2)}, "INVALID_VALIDITY_INTERVAL"),
        ({"revoked": True}, "REVOKED"),
        (
            {"revocation_checked_at": NOW - timedelta(minutes=5, seconds=1)},
            "STALE_OR_FUTURE_REVOCATION",
        ),
        ({"revocation_checked_at": NOW + timedelta(seconds=1)}, "STALE_OR_FUTURE_REVOCATION"),
    ],
)
def test_injected_clock_expiry_revocation_and_freshness(change, reason):
    result = evaluate(replace(fixture(), **change))
    assert result.status == "invalid"
    assert reason in result.reasons
    assert not result.activation_allowed


def test_dst_fold_uses_elapsed_utc_time_not_wall_clock_order():
    zone = ZoneInfo("Europe/London")
    now = datetime(2026, 10, 25, 1, 30, tzinfo=zone, fold=1)
    value = replace(
        fixture(),
        valid_from=datetime(2026, 10, 25, 0, 30, tzinfo=zone),
        expires_at=datetime(2026, 10, 25, 1, 45, tzinfo=zone, fold=0),
        revocation_checked_at=datetime(2026, 10, 25, 1, 30, tzinfo=zone, fold=0),
    )
    result = a.evaluate(REQUEST, FixtureProvider(value), lambda: now)
    assert result.status == "invalid"
    assert {"EXPIRED", "STALE_OR_FUTURE_REVOCATION"} <= set(result.reasons)
    assert not result.activation_allowed


@pytest.mark.parametrize(
    "change",
    [
        {"valid_from": datetime(2026, 1, 1)},
        {"expires_at": None},
        {"revoked": "false"},
        {"revocation_checked_at": "now"},
        {"evidence_refs": ()},
        {"request": None},
        {"assurance": "self-approved"},
        {"identities": () + (a.Identity("approver", "", ("e",), True),)},
        {"identities": () + (a.Identity("approver", "a", (), True),)},
        {"identities": () + (a.Identity("approver", "a", ("e",), "true"),)},
    ],
)
def test_malformed_provider_data_rejected(change):
    assert evaluate(replace(fixture(), **change)).status == "malformed"


def test_invalid_clock_and_request():
    result = a.evaluate(REQUEST, FixtureProvider(fixture()), lambda: datetime(2026, 1, 1))
    assert result.status == "malformed"
    assert "INVALID_CLOCK" in result.reasons
    for request in (
        None,
        replace(REQUEST, artifact="invalid"),
        replace(REQUEST, target=""),
        replace(REQUEST, operation=""),
    ):
        assert a.evaluate(request).status == "malformed"


def test_authority_record_and_unsupported_version():
    result = evaluate(fixture())
    payload = {**asdict(result), "reasons": list(result.reasons), "request": asdict(REQUEST)}
    value = core.record("codex.authority-evaluation.v1", payload, lambda: NOW)
    core.validate(value)
    unknown = copy.deepcopy(value)
    unknown["schema"] = "codex.authority-evaluation.v2"
    with pytest.raises(core.Rejected, match="UNSUPPORTED_SCHEMA"):
        core.validate(unknown)
    payload["activation_allowed"] = True
    with pytest.raises(core.Rejected, match="MALFORMED_RECORD"):
        core.record("codex.authority-evaluation.v1", payload)


def test_cli_cannot_load_imported_fixture_provider(tmp_path, capsys):
    target = tmp_path / "repo"
    target.mkdir()
    value = core.candidate(target, "fixture")
    value["extensions"]["provider"] = {
        "module": "arbitrary.command",
        "assurance": "externally-verified",
        "approved": True,
    }
    value["integrity"] = core.digest({k: v for k, v in value.items() if k != "integrity"})
    path = tmp_path / "candidate.json"
    path.write_bytes(core.canonical(value))
    before = path.read_bytes()
    assert main(["authority", "--root", str(target), "--input", str(path)]) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["payload"]["status"] == "unavailable"
    assert not result["payload"]["activation_allowed"]
    assert path.read_bytes() == before
    assert main(["activate", "--root", str(target), "--input", str(path)]) == 3
    assert json.loads(capsys.readouterr().out)["reason"] == "AUTHORITY_DENIED"
