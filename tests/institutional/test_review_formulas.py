"""Check proposed formula assets, not mathematical truth or calibrated scores."""

from __future__ import annotations

import ast
import json
import re
from importlib.resources import files
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DOCUMENT = ROOT / "docs/design/azimuthal-formal-model.rst"
RESOURCE = files("codex.institutional").joinpath("review-formulas.json")
EXPECTED_NAMES = (
    "findings critical_findings conflict_edges changed_manifest input_and_state "
    "context_advance event_append bearing_set bearing_admission review_lane dissent_lane "
    "independence_vector independence_floor optional_independence_summary "
    "bearing_visualization tension bearing_coverage critical_bearing_coverage weight_update "
    "risk_vector resource_blockers eligible_evidence lineage_memory known_uncertainty "
    "unknown_fraction stage_readiness novelty resilience_vector resilience_aggregate "
    "critical_resilience_floor initial_reconciliation propose_responses "
    "response_reconciliation disposition_routes materialize_change authorize_change "
    "apply_change nonmutating_candidate assurance_plan assurance_reconciliation "
    "authorize_disposition review_closure identity_change finding_impact active_blockers "
    "unsatisfied_requirements novelty_window continuation next_status resume "
    "sensitivity_stability deliberation_no_authority deliberation_recommendations "
    "conceptual_resilience institutional_separation graph_derivation resilience_assessment "
    "composite_transition"
).split()
DIMENSIONS = (
    "logical adversarial institutional operational historical portability epistemic "
    "ecological resource governance architectural evidentiary temporal"
).split()


def registry() -> dict[str, Any]:
    data: dict[str, Any] = json.loads(RESOURCE.read_text(encoding="utf-8"))
    return data


def formulas() -> dict[str, dict[str, Any]]:
    return {entry["name"]: entry for entry in registry()["formulas"]}


def test_registry_contract() -> None:
    data = registry()
    assert data["schema"] == "codex.institutional.review-formulas.v1"
    assert data["status"] == "proposed_notation_not_physical_law_or_measurement"
    assert data["authority"] is False
    assert data["schema_contract"]["no_runtime_evaluator"] is True
    entries = data["formulas"]
    assert len(entries) == len(EXPECTED_NAMES) == 58
    assert [entry["id"] for entry in entries] == [f"RD4-F{index:03d}" for index in range(1, 59)]
    assert [entry["name"] for entry in entries] == EXPECTED_NAMES
    assert len({entry["id"] for entry in entries}) == len(entries)
    for entry in entries:
        assert set(data["schema_contract"]["entry_required"]) <= entry.keys()
        assert entry["latex"]
        assert entry["conditions"]
        assert entry["symbols"]
        assert set(entry["symbols"]) <= data["symbols"].keys()
        metadata = data["metadata"][entry["metadata_ref"]]
        assert metadata["implementation"] == "planned"
        assert metadata["executable_mapping"] is None
        for field in (
            "computability",
            "assumptions",
            "calibration",
            "unknown",
            "empty",
            "zero_denominator",
            "tests",
            "test_scope",
            "provenance",
            "package_status",
        ):
            assert metadata[field], (entry["id"], field)
        assert metadata["tests"] == [
            "tests/institutional/test_review_formulas.py::test_registry_contract",
            "tests/institutional/test_review_formulas.py::test_exact_document_mapping",
            "tests/institutional/test_review_formulas.py"
            "::test_source_expression_preservation_is_distinct_from_normalization",
        ]
        assert "iteration-004 user-supplied formal requirements" in metadata["provenance"]
        assert (
            "parent-provided user equation transcription, 2026-10-25T00:31:12.400+00:00"
            in metadata["provenance"]
        )
    assert [entry["name"] for entry in entries if entry["metadata_ref"] == "conceptual"] == [
        "conceptual_resilience"
    ]


def test_exact_document_mapping() -> None:
    text = DOCUMENT.read_text(encoding="utf-8")
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if index and len(line) > 2 and set(line) <= {"=", "-"}:
            assert len(line) >= len(lines[index - 1])
    mapped = re.findall(
        r"^(RD4-F\d{3}) — [^\n]+\n\n\.\. math::\n\n   ([^\n]+)",
        text,
        flags=re.MULTILINE,
    )
    assert len(mapped) == 58
    assert dict(mapped) == {entry["id"]: entry["latex"] for entry in registry()["formulas"]}
    assert "no charts" in text
    assert "azimuthal-reasoning-integrity.rst" in text
    assert "not measurements" in text


def test_source_expression_preservation_is_distinct_from_normalization() -> None:
    data = registry()
    preserved = data["source_preservation"]
    sources = preserved["source_expressions"]
    normalized = {entry["id"]: entry["latex"] for entry in data["formulas"]}
    assert set(sources) == set(normalized)
    assert len(sources) == 58
    assert all(isinstance(source, str) and source for source in sources.values())
    assert sources["RD4-F001"] == r"\mathcal F_n=Findings(\mathcal G_n)"
    assert sources["RD4-F005"] == (
        r"\mathcal I_n=(\mathcal C_n,\mathcal X_n),"
        r"\qquad\mathcal S_n=(\mathcal I_n,\mathcal G_n,\mathcal V_n)"
    )
    assert sources["RD4-F024"] == (
        r"\mathcal H_n^{known}=\frac{\sum_{j\in J_{known}}\omega_jh_j}"
        r"{\sum_{j\in J_{known}}\omega_j}"
    )
    assert sources["RD4-F031"] == (
        r"(\mathcal G_n^{r0},\mathcal Q_n,\mathcal D_n^{prop},\Theta_{n+1})"
        r"=\mathscr R_0(\mathcal S_n,\{\mathcal L_{i,n}\},\mathcal L_n^{dissent})"
    )
    assert sources["RD4-F022"] == (
        r"EligibleEvidence(e)=Status(e)=ACTIVE\land Applicable(e)"
        r"\land BindingsCurrent(e)\land\neg Disputed(e)"
    )
    assert r"Fallback_n=preserve\_prior" in sources["RD4-F019"]
    assert r"D_n^{req}" in sources["RD4-F029"]
    assert r"\mathrm{required}" not in sources["RD4-F029"]
    assert preserved["prose_source_ids"] == ["RD4-F038", "RD4-F046", "RD4-F047"]
    assert {
        identifier for identifier, source in sources.items() if source.startswith("PROSE SOURCE:")
    } == set(preserved["prose_source_ids"])
    assert preserved["composite_extracted_ids"] == ["RD4-F056", "RD4-F057"]
    assert sources["RD4-F056"] == (
        r"\mathcal G_{n+1}=DeriveGraph(\mathcal V_{n+1},EligibleEvidence_n)"
    )
    assert set(preserved["separate_source_displays"]) == {"RD4-F008", "RD4-F027"}
    for identifier, displays in preserved["separate_source_displays"].items():
        assert len(displays) == 2
        assert all(display in sources[identifier] for display in displays)
    composite = sources["RD4-F058"]
    assert composite.startswith(r"\boxed{\begin{aligned}")
    assert composite.endswith(r"\end{aligned}}")
    assert r"Next_n&\in\{" in composite
    assert r"\begin{cases}" not in composite
    assert r"\mathcal L_n^{dissent}&=" not in composite
    assert "ApplyAuthorizedRoutes" in composite
    assert "ReviewAuthorizedClosure" in composite
    assert r"\begin{cases}" in normalized["RD4-F058"]
    assert sources["RD4-F001"] != normalized["RD4-F001"]
    assert sources["RD4-F058"] != normalized["RD4-F058"]
    assert not any(r"\setminus" in source for source in sources.values())
    mapped = re.findall(
        r"^   SOURCE (RD4-F\d{3}): ([^\n]+)",
        DOCUMENT.read_text(encoding="utf-8"),
        flags=re.MULTILINE,
    )
    assert len(mapped) == 58
    assert dict(mapped) == sources
    typography = preserved["source_typography"]
    assert typography["calligraphic_families"] == [
        r"\mathcal F_n",
        r"\mathcal C_n",
        r"\mathcal G_n",
    ]
    assert typography["required_dimensions"] == "D_n^req"
    assert typography["source_latex"]["required_dimensions"] == r"D_n^{req}"
    assert typography["normalized_required_dimensions"] == r"D_n^{\mathrm{required}}"
    assert "set_difference" not in typography
    assert typography["boxed_composite"] == r"\boxed{\begin{aligned}...\end{aligned}}"
    assert preserved["upstream_exact_latex_verified"] is False
    assert preserved["parent_transcription_preserved"] is True
    assert preserved["source_kind"].startswith("parent-provided user transcription")
    assert preserved["provenance"] == (
        "Parent-provided user equation transcription, 2026-10-25T00:31:12.400+00:00"
    )
    assert preserved["no_semantic_correction_claim"] is True
    assert preserved["no_calibration_or_numerical_correctness_claim"] is True
    assert "no independent upstream bytehash" in typography["verification_limit"]
    assert "No set difference is invented" in preserved["normalization_disclosure"]
    assert "F038/F046/F047" in preserved["normalization_disclosure"]
    assert "known uncertainty" in data["symbols"]["uncertainty"]
    assert "no domain/calibration invented" in data["symbols"]["uncertainty"]
    assert "not health" in data["symbols"]["health"]
    uncertainty = formulas()["known_uncertainty"]
    assert uncertainty["id"] == "RD4-F024"
    assert uncertainty["legacy_name"] == "known_health"
    assert uncertainty["symbols"] == ["uncertainty"]


def test_lineage_and_package_claims_are_bounded() -> None:
    data = registry()
    assert data["lineage"] == {
        "assertion": "75f7dab1dbff1521ab530dd32c5d7cf028f57669f24147676a5dbf917c9b69f6",
        "verification": "unverified",
        "is_asset_content_digest": False,
        "source": "iteration-004 user-supplied formal requirements",
    }
    discovery = data["discovery"]
    assert discovery["compatible_registry_found"] is False
    assert "references directory absent" in discovery["bounded_search"]
    assert "No exhaustive nonexistence claim" in discovery["bounded_search"]
    assert ".github/agents" in discovery["bounded_search"]
    references = discovery["references"]
    assert len(references) == 8
    for reference in references:
        assert (ROOT / reference["path"]).is_file(), reference["path"]
        assert reference["compatibility"]
    toolkit = references[0]
    assert toolkit["ids"] == {
        "Table1_TimeConstraints": [1, 49, 56],
        "Table2_ImportMonitoring": [1, 6],
        "Table3_MultiOrchestrator": [4, 15],
        "Table4_CoverageUplift": [2, 3, 6],
    }
    assert sum(map(len, toolkit["ids"].values())) == 10
    assert "wheel inclusion not demonstrated" in data["metadata"]["planned"]["package_status"]
    assert data["packaging"]["intended_explicit_resource"] == "review-formulas.json"
    assert data["packaging"]["manifest_owner"] == "parent"
    assert data["packaging"]["external_wheel_verification"] == "pending"
    assert data["packaging"]["installed_wheel_inclusion_verified"] is False
    assert data["review_sdk_mapping"]["status"] == "source-inspected bounded structural APIs"
    assert data["review_sdk_mapping"]["executable_mapping"] is None


def test_structural_sdk_mappings_resolve_without_claiming_formula_execution() -> None:
    data = registry()
    mapping = data["review_sdk_mapping"]
    source = ast.parse((ROOT / mapping["source"]).read_text(encoding="utf-8"))
    defined = {node.name for node in source.body if isinstance(node, ast.FunctionDef)}
    expected = {
        "candidate_manifest",
        "review_plan",
        "lane_output",
        "reconcile",
        "new_history",
        "fold_events",
        "append_event",
        "resume",
        "remediation_adequacy",
        "attach_continuation",
    }
    bindings = mapping["bindings"]
    assert len(bindings) == len(expected) == 10
    assert {binding["api"] for binding in bindings} == expected
    assert expected <= defined
    formula_ids = {entry["id"] for entry in data["formulas"]}
    for binding in bindings:
        assert binding["formula_ids"]
        assert set(binding["formula_ids"]) <= formula_ids
        assert binding["implemented"]
        assert binding["limits"]
    assert mapping["executable_mapping"] is None
    assert all(entry["metadata_ref"] in ("planned", "conceptual") for entry in data["formulas"])


def test_all_thirteen_dimensions_and_independence_are_explicit() -> None:
    data = registry()
    entries = formulas()
    assert data["symbols"]["dimensions"] == DIMENSIONS
    vector = entries["resilience_vector"]["latex"]
    positions = [vector.index(r"z_{\mathrm{" + dimension + "}}") for dimension in DIMENSIONS]
    assert positions == sorted(positions)
    assert r"\{\mathrm{unknown}\}" in vector
    assert "^{13}" in vector
    independence = entries["independence_vector"]["latex"]
    for dimension in (
        "actor",
        "model",
        "prompt",
        "evidence",
        "environment",
        "procedure",
        "organization",
        "custody",
    ):
        assert r"i_{\mathrm{" + dimension + "}}" in independence
    assert "not_assessed" in entries["independence_vector"]["conditions"]
    assert "unknown critical" in entries["independence_floor"]["conditions"].lower()


def test_edge_condition_metadata_is_not_vacuous_success() -> None:
    entries = formulas()
    required_phrases = {
        "tension": ("not_applicable", "Zero denominator", "not zero"),
        "bearing_coverage": ("Positive", "unknown", "not_assessed"),
        "critical_bearing_coverage": ("Nonempty", "unknown critical", "positive"),
        "weight_update": ("k_n>0", "changed membership", "explicit redistribution"),
        "risk_vector": ("vector/ordinal", "calibrated ratio"),
        "lineage_memory": ("lineage grouping", "ledger authoritative", "no aggregate"),
        "known_uncertainty": ("No known positive weight", "unknown", "not a health score"),
        "unknown_fraction": ("Empty/zero", "not 0"),
        "stage_readiness": ("Empty", "does not grant approval", "authorization separate"),
        "resilience_aggregate": (
            "all required values known",
            "positive required total",
            "nonempty",
            "no inferred zero",
        ),
        "critical_resilience_floor": ("nonempty", "unknown critical", "never close"),
        "unsatisfied_requirements": ("unknown satisfaction", "not silently omitted"),
        "novelty_window": ("positive integer", "history", "unknown"),
        "continuation": ("unknown", "cannot imply convergence", "missing-evidence/calibration"),
        "next_status": ("not approved", "known predicates", "scopes blocked"),
        "resume": (
            "pending_requirement",
            "blocked_from_state",
            "authorized service",
            "no background monitor",
        ),
        "sensitivity_stability": (
            "Finite enumeration",
            "interval proof",
            "symbolic analysis",
            "bounded sampling",
            "not continuous proof",
            "empty assessment not stable",
            "self-referential",
        ),
        "deliberation_recommendations": ("authorized service", "not direct mutation"),
        "composite_transition": ("separately authorized", "Unknown required", "no scheduler"),
    }
    for name, phrases in required_phrases.items():
        conditions = entries[name]["conditions"].lower()
        for phrase in phrases:
            assert phrase.lower() in conditions, (name, phrase)


def test_complete_routes_authority_and_composite_notation() -> None:
    entries = formulas()
    route = entries["disposition_routes"]["latex"]
    for disposition in (
        "FIXED",
        "ACCEPTED_RISK",
        "NOT_APPLICABLE",
        "REJECTED_WITH_EVIDENCE",
        "SUPERSEDED",
        "DEFERRED",
        "OUT_OF_SCOPE_TRANSFER",
    ):
        assert disposition.replace("_", r"\_") in route
    prohibited = entries["deliberation_no_authority"]["latex"]
    for role in ("Authority", "Mutation", "Execution", "Reproduction", "Audit", "Approval"):
        assert rf"\operatorname{{{role}}}(RD)" in prohibited
    assert prohibited.endswith("=0")
    recommendations = entries["deliberation_recommendations"]["latex"]
    for role in (
        "Reconcile",
        "RecommendBearing",
        "ReopenFinding",
        "PreserveUncertainty",
        "RecommendContinuation",
    ):
        assert rf"\operatorname{{{role}}}(RD)" in recommendations
    assert recommendations.endswith("=1")
    composite = entries["composite_transition"]["latex"]
    assert composite.startswith(r"\boxed{\begin{aligned}")
    for operator in (
        "Review",
        "DissentReview",
        "ProposeResponses",
        "ApplyAuthorizedRoutes",
        "PlanAssurance",
        "ReviewAuthorizedClosure",
        "AdvanceContext",
        "AppendEvents",
        "DeriveGraph",
        "AssessResilience",
    ):
        assert rf"\operatorname{{{operator}}}" in composite
    for stage in range(3):
        assert rf"\mathcal R_{stage}" in composite
    for status in (
        "STOP_SAFELY",
        "ROTATE_AND_CONTINUE",
        "CONVERGED_FOR_AUTHORIZED_DECISION",
    ):
        assert status.replace("_", r"\_") in composite
    assert r"Q_n" in composite
    assert r"X_{n+1}" in composite
    assert r"V_{n+1}" in composite
    assert r"\mathbf z_{n+1}" in composite
