"""Versioned, JSON-serializable contracts for evidence-grounded research."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any

SCHEMA_VERSION = "1.0"
OBJECTIVE_STATUSES = {
    "answered",
    "partially_answered",
    "unresolved",
    "not_applicable",
}


@dataclass(frozen=True)
class Objective:
    id: str
    question: str
    acceptance_criteria: tuple[str, ...] = ()
    synonyms: tuple[str, ...] = ()
    applicable: bool = True
    parent_id: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Objective:
        applicable = data.get("applicable", True)
        if not isinstance(applicable, bool):
            raise ValueError("objective applicable must be a boolean")
        return cls(
            id=_required_text(data, "id"),
            question=_required_text(data, "question"),
            acceptance_criteria=tuple(_text_list(data.get("acceptance_criteria", []))),
            synonyms=tuple(_text_list(data.get("synonyms", []))),
            applicable=applicable,
            parent_id=_optional_text(data.get("parent_id")),
        )


@dataclass(frozen=True)
class ResearchBrief:
    title: str
    objectives: tuple[Objective, ...]
    scope: str = ""
    exclusions: tuple[str, ...] = ()
    jurisdictions: tuple[str, ...] = ()
    time_period: str | None = None
    terminology: dict[str, str] = field(default_factory=dict)
    hypotheses: dict[str, tuple[str, ...]] = field(default_factory=dict)
    execution_lanes: tuple[dict[str, Any], ...] = ()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ResearchBrief:
        if not isinstance(data, dict):
            raise ValueError("A research brief must be an object")
        if _contains_credential_pattern(data):
            raise ValueError("Research brief contains secret-like credential syntax")
        objectives = tuple(
            Objective.from_dict(item) for item in _dict_list(data.get("objectives"), "objectives")
        )
        if not objectives:
            raise ValueError("A research brief must contain at least one objective")
        ids = [objective.id for objective in objectives]
        if len(ids) != len(set(ids)):
            raise ValueError("Objective IDs must be unique")
        known_ids = set(ids)
        parent_map = {item.id: item.parent_id for item in objectives}
        for objective in objectives:
            if objective.parent_id and objective.parent_id not in known_ids:
                raise ValueError(f"Unknown parent objective: {objective.parent_id}")
            visited_objectives = {objective.id}
            parent = objective.parent_id
            while parent:
                if parent in visited_objectives:
                    raise ValueError("Objective hierarchy contains a cycle")
                visited_objectives.add(parent)
                parent = parent_map[parent]
        hypotheses = data.get("hypotheses", {})
        if not isinstance(hypotheses, dict):
            raise ValueError("hypotheses must be an object keyed by objective ID")
        if not set(hypotheses).issubset(known_ids):
            raise ValueError("Hypotheses reference an unknown objective")
        terminology = data.get("terminology", {})
        if not isinstance(terminology, dict) or any(
            not isinstance(key, str) or not isinstance(value, str)
            for key, value in terminology.items()
        ):
            raise ValueError("terminology must map strings to strings")
        scope = data.get("scope", "")
        if not isinstance(scope, str):
            raise ValueError("scope must be a string")
        lanes = data.get("execution_lanes", [])
        if not isinstance(lanes, list) or any(not isinstance(item, dict) for item in lanes):
            raise ValueError("execution_lanes must be a list of objects")
        required_lane_fields = {
            "id",
            "owner",
            "mode",
            "depends_on",
            "scope",
            "evidence_contract",
            "completion_gate",
        }
        normalized_lanes: list[dict[str, Any]] = []
        for lane in lanes:
            if not required_lane_fields.issubset(lane):
                raise ValueError(
                    "Each execution lane requires id, owner, mode, depends_on, scope, "
                    "evidence_contract, and completion_gate"
                )
            if any(
                field_name != "depends_on"
                and (not isinstance(lane[field_name], str) or not lane[field_name].strip())
                for field_name in required_lane_fields
            ):
                raise ValueError("Execution lane fields must be non-empty strings")
            dependencies = lane["depends_on"]
            if not isinstance(dependencies, list) or any(
                not isinstance(dependency, str) or not dependency.strip()
                for dependency in dependencies
            ):
                raise ValueError("Execution lane depends_on must be a list of lane IDs")
            if lane["mode"] not in {"parallel", "dependent", "aggregator"}:
                raise ValueError("Execution lane mode must be parallel, dependent, or aggregator")
            normalized_lanes.append(
                {
                    **{
                        field_name: lane[field_name].strip()
                        for field_name in required_lane_fields
                        if field_name != "depends_on"
                    },
                    "depends_on": [dependency.strip() for dependency in dependencies],
                }
            )
        lane_ids = [lane["id"] for lane in normalized_lanes]
        if len(lane_ids) != len(set(lane_ids)):
            raise ValueError("Execution lane IDs must be unique")
        lane_id_set = set(lane_ids)
        dependencies_by_lane = {lane["id"]: lane["depends_on"] for lane in normalized_lanes}
        for lane in normalized_lanes:
            if lane["id"] in lane["depends_on"] or not set(lane["depends_on"]).issubset(
                lane_id_set
            ):
                raise ValueError("Execution lane dependencies must reference other known lanes")
            if lane["mode"] == "parallel" and lane["depends_on"]:
                raise ValueError("Parallel execution lanes cannot depend on another lane")
        for lane_id in lane_ids:
            visited: set[str] = set()
            pending = list(dependencies_by_lane[lane_id])
            while pending:
                dependency = pending.pop()
                if dependency == lane_id or dependency in visited:
                    if dependency == lane_id:
                        raise ValueError("Execution lane dependencies contain a cycle")
                    continue
                visited.add(dependency)
                pending.extend(dependencies_by_lane[dependency])
        return cls(
            title=_required_text(data, "title"),
            objectives=objectives,
            scope=scope,
            exclusions=tuple(_text_list(data.get("exclusions", []))),
            jurisdictions=tuple(_text_list(data.get("jurisdictions", []))),
            time_period=_optional_text(data.get("time_period")),
            terminology=terminology,
            hypotheses={str(key): tuple(_text_list(value)) for key, value in hypotheses.items()},
            execution_lanes=tuple(normalized_lanes),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "objectives": [
                {
                    "id": objective.id,
                    "question": objective.question,
                    "acceptance_criteria": list(objective.acceptance_criteria),
                    "synonyms": list(objective.synonyms),
                    "applicable": objective.applicable,
                    "parent_id": objective.parent_id,
                }
                for objective in self.objectives
            ],
            "scope": self.scope,
            "exclusions": list(self.exclusions),
            "jurisdictions": list(self.jurisdictions),
            "time_period": self.time_period,
            "terminology": dict(self.terminology),
            "hypotheses": {key: list(value) for key, value in self.hypotheses.items()},
            "execution_lanes": [dict(lane) for lane in self.execution_lanes],
        }


@dataclass
class ResearchBundle:
    research_id: str
    schema_version: str
    brief: dict[str, Any]
    capability: dict[str, Any]
    query_ledger: list[dict[str, Any]]
    sources: list[dict[str, Any]]
    evidence: list[dict[str, Any]]
    claims: list[dict[str, Any]]
    datasets: list[dict[str, Any]]
    contradictions: list[dict[str, Any]]
    objective_matrix: list[dict[str, Any]]
    verification: dict[str, Any]
    azimuth: dict[str, Any]
    checkpoint: dict[str, Any]
    status: str
    report: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ResearchBundle:
        required = {
            "research_id",
            "schema_version",
            "brief",
            "capability",
            "query_ledger",
            "sources",
            "evidence",
            "claims",
            "datasets",
            "contradictions",
            "objective_matrix",
            "verification",
            "azimuth",
            "checkpoint",
            "status",
            "report",
        }
        missing = required.difference(data)
        if missing:
            raise ValueError(f"Research bundle is missing fields: {sorted(missing)}")
        if data["schema_version"] != SCHEMA_VERSION:
            raise ValueError(f"Unsupported research schema: {data['schema_version']}")
        bundle = cls(**{key: data[key] for key in required})
        validate_bundle(bundle)
        return bundle


def validate_bundle(bundle: ResearchBundle) -> None:
    if bundle.schema_version != SCHEMA_VERSION:
        raise ValueError(f"Unsupported research schema: {bundle.schema_version}")
    if not isinstance(bundle.azimuth, dict):
        raise ValueError("Research bundle AZIMUTH assessment must be an object")
    sequence = ["A", "Z", "I", "M", "U", "T", "H"]
    if bundle.azimuth.get("model") != "AZIMUTH" or bundle.azimuth.get("sequence") != sequence:
        raise ValueError("Research bundle must include the ordered AZIMUTH assessment")
    if bundle.azimuth.get("repo_mutations_performed") is not False:
        raise ValueError("Research analysis must not imply repository mutations")
    phases = bundle.azimuth.get("phases")
    if not isinstance(phases, list) or any(not isinstance(phase, dict) for phase in phases):
        raise ValueError("AZIMUTH assessment phases must be a list of objects")
    phase_ids = [phase.get("id") for phase in phases]
    if phase_ids != sequence:
        raise ValueError("AZIMUTH assessment phases are incomplete or out of order")
    valid_phase_statuses = {"completed", "partial", "incomplete", "not_assessed"}
    if any(phase.get("status") not in valid_phase_statuses for phase in phases):
        raise ValueError("AZIMUTH phase has an invalid status")
    expected_azimuth_status = (
        "completed" if all(phase["status"] == "completed" for phase in phases) else "partial"
    )
    if bundle.azimuth.get("status") != expected_azimuth_status:
        raise ValueError("AZIMUTH overall status does not match its phase assessments")
    if any(
        source.get("evidence_role") not in {"current", "historical", "archive", "unknown"}
        for source in bundle.sources
    ):
        raise ValueError("Source has an invalid evidence role")
    source_ids = {item["id"] for item in bundle.sources}
    evidence_ids = {item["id"] for item in bundle.evidence}
    claim_ids = {item["id"] for item in bundle.claims}
    objective_ids = {item["id"] for item in bundle.brief.get("objectives", [])}
    matrix_ids = [item["id"] for item in bundle.objective_matrix]
    if len(matrix_ids) != len(set(matrix_ids)) or set(matrix_ids) != objective_ids:
        raise ValueError("Each brief objective must have exactly one objective-matrix entry")
    for item in bundle.evidence:
        if item["objective_id"] not in objective_ids:
            raise ValueError(f"Evidence {item['id']} references an unknown objective")
        if not set(item["source_ids"]).issubset(source_ids):
            raise ValueError(f"Evidence {item['id']} references an unknown source")
        if item.get("locator") in (None, ""):
            raise ValueError(f"Evidence {item['id']} has no source locator")
        if item.get("claim_id") not in claim_ids:
            raise ValueError(f"Evidence {item['id']} references an unknown claim")
    for item in bundle.claims:
        if item["objective_id"] not in objective_ids:
            raise ValueError(f"Claim {item['id']} references an unknown objective")
        if not set(item["evidence_ids"]).issubset(evidence_ids):
            raise ValueError(f"Claim {item['id']} references unknown evidence")
    for item in bundle.contradictions:
        if not set(item["claim_ids"]).issubset(claim_ids):
            raise ValueError(f"Contradiction {item['id']} references unknown claims")
        if not set(item["evidence_ids"]).issubset(evidence_ids):
            raise ValueError(f"Contradiction {item['id']} references unknown evidence")
    for item in bundle.objective_matrix:
        if item["status"] not in OBJECTIVE_STATUSES:
            raise ValueError(f"Invalid objective status: {item['status']}")
        if not set(item["evidence_ids"]).issubset(evidence_ids):
            raise ValueError(f"Objective {item['id']} references unknown evidence")
        if not set(item["claim_ids"]).issubset(claim_ids):
            raise ValueError(f"Objective {item['id']} references unknown claims")
    for finding in bundle.verification.get("findings", []):
        if not set(finding.get("evidence_ids", [])).issubset(evidence_ids):
            raise ValueError("Verification finding references unknown evidence")


def _required_text(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value.strip()


def _optional_text(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _text_list(value: Any) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError("Expected a list of strings")
    return [item.strip() for item in value if item.strip()]


def _dict_list(value: Any, field_name: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise ValueError(f"{field_name} must be a list of objects")
    return value


def _contains_credential_pattern(value: Any) -> bool:
    if isinstance(value, str):
        patterns = (
            r"(?i)(authorization|token|secret|api[_-]?key|password)\s*[:=]\s*\S+",
            r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+",
            r"\bAKIA[0-9A-Z]{16}\b",
            r"\bsk-[A-Za-z0-9_-]{16,}\b",
        )
        return any(re.search(pattern, value) for pattern in patterns)
    if isinstance(value, dict):
        return any(
            _contains_credential_pattern(key) or _contains_credential_pattern(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_contains_credential_pattern(item) for item in value)
    return False
