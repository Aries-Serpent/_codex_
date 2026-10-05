"""Bounded orchestration for source-grounded research bundles."""

from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from threading import Event
from typing import Any

from codex.deep_research.contracts import (
    SCHEMA_VERSION,
    Objective,
    ResearchBrief,
    ResearchBundle,
    validate_bundle,
)
from codex.deep_research.datasets import profile_dataset
from codex.deep_research.providers import (
    HostToolProvider,
    ProviderUnavailable,
    ResearchProvider,
    canonicalize_url,
    contains_sensitive_material,
    redact_sensitive_text,
)


@dataclass(frozen=True)
class ExecutionLimits:
    max_search_calls: int = 40
    max_sources: int = 60
    max_retries: int = 3
    deadline_seconds: float = 1800.0
    max_content_chars: int = 2_000_000
    max_results_per_query: int = 20
    max_evidence_per_source_objective: int = 5
    retain_source_content: bool = False
    max_provider_cost: float | None = None

    def __post_init__(self) -> None:
        if min(self.max_search_calls, self.max_sources, self.max_retries) < 0:
            raise ValueError("Execution counts must be non-negative")
        if self.deadline_seconds <= 0 or self.max_content_chars <= 0:
            raise ValueError("Deadline and content limits must be positive")
        if self.max_evidence_per_source_objective <= 0:
            raise ValueError("Evidence limit must be positive")
        if self.max_results_per_query <= 0:
            raise ValueError("Search result limit must be positive")
        if self.max_provider_cost is not None and self.max_provider_cost < 0:
            raise ValueError("Provider cost cap must be non-negative")


def run_research(
    brief: ResearchBrief | dict[str, Any],
    *,
    provider: ResearchProvider | None = None,
    local_sources: list[dict[str, Any]] | None = None,
    dataset_paths: list[str | Path] | None = None,
    checkpoint: dict[str, Any] | None = None,
    limits: ExecutionLimits | None = None,
    cancellation_event: Event | None = None,
) -> ResearchBundle:
    """Execute a bounded research run; absent a provider, work remains explicitly offline."""
    research_brief = brief if isinstance(brief, ResearchBrief) else ResearchBrief.from_dict(brief)
    run_limits = limits or ExecutionLimits()
    if isinstance(provider, HostToolProvider):
        provider.retries = min(provider.retries, run_limits.max_retries)
    cost_per_search = float(getattr(provider, "cost_per_search", 0.0) or 0.0)
    if cost_per_search > 0 and run_limits.max_provider_cost is None:
        raise ValueError("A nonzero-cost provider requires an explicit max_provider_cost")
    research_id = _stable_id("research", research_brief.to_dict())
    state = _resume_state(checkpoint, research_id)
    query_ledger = state.get("query_ledger", [])
    sources = state.get("sources", [])
    evidence = state.get("evidence", [])
    claims = state.get("claims", [])
    completed_query_ids = {
        entry["id"] for entry in query_ledger if entry.get("status") == "completed"
    }
    queries = _query_plan(research_brief)
    deadline = time.monotonic() + run_limits.deadline_seconds * 0.9
    cache: dict[str, dict[str, Any]] = {
        source["canonical_url"]: source
        for source in sources
        if source.get("canonical_url") and source.get("access_outcome") == "retrieved"
    }
    if not state:
        for item in local_sources or []:
            source = _local_source(item, run_limits)
            if source is not None:
                _add_source(source, sources, cache)
                _extract_evidence(
                    source,
                    research_brief.objectives,
                    evidence,
                    claims,
                    run_limits,
                )

    calls_made = sum(1 for entry in query_ledger if entry.get("attempted"))
    cost_spent = sum(float(entry.get("cost", 0.0) or 0.0) for entry in query_ledger)
    capability: dict[str, Any] = {
        "web_retrieval_available": bool(provider),
        "fresh_web_research": False,
        "retrieval_completed": False,
        "provider_binding": ("injected_callable" if provider is not None else "unavailable"),
        "budgets": {
            "max_search_calls": run_limits.max_search_calls,
            "max_sources": run_limits.max_sources,
            "max_retries": run_limits.max_retries,
            "deadline_seconds": run_limits.deadline_seconds,
            "finalization_reserve_fraction": 0.1,
            "max_provider_cost": run_limits.max_provider_cost,
            "max_results_per_query": run_limits.max_results_per_query,
        },
        "limitations": [
            "Citation-chain following is not implemented.",
            "Dataset profiling supports supplied local CSV and JSONL/NDJSON only.",
            "Structural verification does not establish semantic entailment or source authority.",
        ],
    }
    if provider is None:
        capability["limitations"].append(
            "No callable search/fetch provider was supplied; findings use only "
            "supplied or local evidence."
        )
    elif isinstance(provider, HostToolProvider) and not provider.available:
        capability["web_retrieval_available"] = False
        capability["provider_binding"] = "incomplete_callable_binding"
        capability["limitations"].append(
            "Callable search/fetch tools and verified per-redirect DNS/SSRF protections "
            "are required for fresh web retrieval."
        )

    for query in queries:
        if query["id"] in completed_query_ids:
            continue
        attempt_number = sum(1 for entry in query_ledger if entry.get("id") == query["id"]) + 1
        ledger_entry = {
            **query,
            "execution_id": _stable_id(
                "execution", {"query_id": query["id"], "attempt": attempt_number}
            ),
            "attempt_number": attempt_number,
            "status": "pending",
            "attempted": False,
            "result_count": 0,
            "source_ids": [],
            "error": None,
        }
        query_ledger.append(ledger_entry)
        if provider is None or not capability["web_retrieval_available"]:
            ledger_entry["status"] = "skipped"
            ledger_entry["error"] = "web retrieval unavailable"
            continue
        if cost_per_search and (
            cost_spent + cost_per_search > float(run_limits.max_provider_cost or 0)
        ):
            ledger_entry["status"] = "skipped"
            ledger_entry["error"] = "provider cost budget exhausted"
            continue
        if calls_made >= run_limits.max_search_calls:
            ledger_entry["status"] = "skipped"
            ledger_entry["error"] = "search call budget exhausted"
            continue
        if _is_interrupted(deadline, cancellation_event):
            ledger_entry["status"] = "skipped"
            ledger_entry["error"] = "deadline or cancellation reached"
            continue
        calls_made += 1
        ledger_entry["attempted"] = True
        ledger_entry["cost"] = cost_per_search
        cost_spent += cost_per_search
        try:
            hits = provider.search(query["query"])
            ledger_entry["result_count"] = len(hits)
            ledger_entry["screened_result_count"] = min(len(hits), run_limits.max_results_per_query)
            ledger_entry["status"] = "completed"
            if len(hits) > run_limits.max_results_per_query:
                ledger_entry["status"] = "partial"
                ledger_entry["error"] = "per-query result budget exhausted"
        except ProviderUnavailable as exc:
            capability["web_retrieval_available"] = False
            capability["limitations"].append(str(exc))
            ledger_entry["status"] = "failed"
            ledger_entry["error"] = str(exc)
            continue
        except Exception as exc:  # Provider errors are recorded, not hidden.
            ledger_entry["status"] = "failed"
            ledger_entry["error"] = f"{type(exc).__name__}: {exc}"
            continue
        if _is_interrupted(deadline, cancellation_event):
            ledger_entry["status"] = "partial"
            ledger_entry["error"] = "deadline or cancellation reached after search"
            continue
        for hit in hits[: run_limits.max_results_per_query]:
            if len(sources) >= run_limits.max_sources:
                ledger_entry["error"] = "unique source budget exhausted"
                ledger_entry["status"] = "partial"
                break
            try:
                canonical_url = canonicalize_url(hit["url"])
            except (KeyError, TypeError, ValueError) as exc:
                ledger_entry["error"] = f"rejected search result: {exc}"
                ledger_entry["status"] = "partial"
                continue
            prior = cache.get(canonical_url)
            if prior is None:
                try:
                    fetched = provider.fetch(hit["url"])
                except Exception as exc:  # Access failures remain in the source ledger.
                    source = _failed_source(hit, canonical_url, exc, query)
                    _add_source(source, sources, cache)
                    ledger_entry["source_ids"].append(source["id"])
                    ledger_entry["status"] = "partial"
                    ledger_entry["error"] = f"source fetch failed: {type(exc).__name__}"
                    continue
                source = _web_source(
                    hit,
                    fetched,
                    query,
                    run_limits,
                    live_binding_verified=bool(getattr(provider, "is_live", False)),
                )
                prior = _add_source(source, sources, cache)
                if prior is source:
                    if source["access_outcome"] == "retrieved":
                        capability["retrieval_completed"] = True
                    _extract_evidence(
                        source,
                        research_brief.objectives,
                        evidence,
                        claims,
                        run_limits,
                    )
            else:
                prior["query_ids"] = sorted(set(prior["query_ids"] + [query["id"]]))
                prior["objective_ids"] = sorted(
                    set(prior["objective_ids"] + [query["objective_id"]])
                )
            ledger_entry["source_ids"].append(prior["id"])
            if _is_interrupted(deadline, cancellation_event):
                ledger_entry["error"] = "deadline or cancellation reached during retrieval"
                break
    retrieved_sources = [
        source for source in sources if source.get("access_outcome") == "retrieved"
    ]
    capability["retrieval_completed"] = bool(retrieved_sources)
    capability["fresh_web_research"] = any(
        source.get("retrieval_provenance", {}).get("live_binding_verified", False)
        for source in retrieved_sources
    )
    if capability["retrieval_completed"] and not capability["fresh_web_research"]:
        capability["limitations"].append(
            "Retrieval used an injected provider not marked as a verified live host binding."
        )

    datasets = list(state.get("datasets", []))
    for dataset_path in dataset_paths or []:
        profile = profile_dataset(dataset_path)
        if not any(item["dataset_id"] == profile["dataset_id"] for item in datasets):
            datasets.append(profile)
    if not run_limits.retain_source_content:
        for source in sources:
            source["content"] = None
            source["content_retained"] = False
    matrix = _objective_matrix(research_brief.objectives, evidence, claims)
    contradictions = _find_contradictions(research_brief.objectives, evidence, claims)
    verification = _verify(evidence, claims, sources, matrix)
    incomplete = (
        any(item["status"] in {"unresolved", "partially_answered"} for item in matrix)
        or any(
            entry["status"] in {"pending", "skipped", "failed", "partial"} for entry in query_ledger
        )
        or _is_interrupted(deadline, cancellation_event)
        or bool(contradictions)
    )
    status = "incomplete" if incomplete else "complete"
    azimuth = _azimuth_assessment(
        research_brief,
        sources,
        evidence,
        matrix,
        verification,
        status,
    )
    checkpoint_payload = {
        "research_id": research_id,
        "parent_id": state.get("checkpoint_id"),
        "completed_query_ids": sorted(
            completed_query_ids
            | {entry["id"] for entry in query_ledger if entry.get("status") == "completed"}
        ),
        "query_ledger": query_ledger,
        "sources": sources,
        "evidence": evidence,
        "claims": claims,
        "datasets": datasets,
        "objective_matrix": matrix,
        "status": status,
    }
    checkpoint_digest = hashlib.sha256(_canonical_json(checkpoint_payload)).hexdigest()
    checkpoint_output = {
        "checkpoint_id": _stable_id("checkpoint", checkpoint_payload),
        "parent_id": checkpoint_payload["parent_id"],
        "payload_sha256": checkpoint_digest,
        **checkpoint_payload,
    }
    bundle = ResearchBundle(
        research_id=research_id,
        schema_version=SCHEMA_VERSION,
        brief=research_brief.to_dict(),
        capability=capability,
        query_ledger=query_ledger,
        sources=sources,
        evidence=evidence,
        claims=claims,
        datasets=datasets,
        contradictions=contradictions,
        objective_matrix=matrix,
        verification=verification,
        azimuth=azimuth,
        checkpoint=checkpoint_output,
        status=status,
        report=_render_report(
            research_brief,
            capability,
            matrix,
            sources,
            evidence,
            datasets,
            azimuth,
        ),
    )
    validate_bundle(bundle)
    return bundle


def validate_checkpoint(checkpoint: dict[str, Any]) -> None:
    expected = checkpoint.get("payload_sha256")
    if not isinstance(expected, str):
        raise ValueError("Checkpoint has no payload digest")
    payload = {
        key: value
        for key, value in checkpoint.items()
        if key not in {"checkpoint_id", "payload_sha256"}
    }
    actual = hashlib.sha256(_canonical_json(payload)).hexdigest()
    if actual != expected:
        raise ValueError("Checkpoint digest does not match its contents")


def _resume_state(checkpoint: dict[str, Any] | None, research_id: str) -> dict[str, Any]:
    if checkpoint is None:
        return {}
    validate_checkpoint(checkpoint)
    if checkpoint.get("research_id") != research_id:
        raise ValueError("Checkpoint belongs to a different research brief")
    return {
        key: checkpoint[key]
        for key in (
            "checkpoint_id",
            "query_ledger",
            "sources",
            "evidence",
            "claims",
            "datasets",
        )
    }


def _query_plan(brief: ResearchBrief) -> list[dict[str, Any]]:
    result = []
    for objective in brief.objectives:
        modifiers = [
            *brief.jurisdictions,
            brief.time_period or "",
            brief.scope,
        ]
        terminology_terms = []
        question_words = _keywords_text(objective.question)
        for term, meaning in brief.terminology.items():
            if question_words.intersection(_keywords_text(f"{term} {meaning}")):
                terminology_terms.append(f"{term} {meaning}")
        terms = list(dict.fromkeys([objective.question, *objective.synonyms, *terminology_terms]))
        for index, term in enumerate(terms):
            text = " ".join(part for part in (term, *modifiers) if part)
            if brief.exclusions:
                text = f"{text} excluding {'; '.join(brief.exclusions)}"
            result.append(_query_record(objective, f"support-{index + 1}", text, "supporting"))
        for index, hypothesis in enumerate(brief.hypotheses.get(objective.id, ()), start=1):
            result.append(
                _query_record(
                    objective,
                    f"hypothesis-{index}",
                    hypothesis,
                    "hypothesis",
                )
            )
            result.append(
                _query_record(
                    objective,
                    f"disconfirm-hypothesis-{index}",
                    f"evidence against: {hypothesis}",
                    "disconfirmation",
                )
            )
        result.append(
            _query_record(
                objective,
                "disconfirmation",
                f"{objective.question} contrary evidence limitations alternative explanations",
                "disconfirmation",
            )
        )
    return result


def _query_record(objective: Objective, suffix: str, query: str, query_kind: str) -> dict[str, Any]:
    return {
        "id": f"query-{_digest(f'{objective.id}:{suffix}:{query}')[:16]}",
        "objective_id": objective.id,
        "query": query,
        "kind": query_kind,
        "status": "planned",
    }


def _local_source(item: dict[str, Any], limits: ExecutionLimits) -> dict[str, Any] | None:
    content = item.get("content")
    if not isinstance(content, str):
        return None
    content = content[: limits.max_content_chars]
    locator = item.get("locator")
    if not isinstance(locator, str) or not locator:
        locator = "supplied-text"
    locator = _safe_locator(locator)
    return _source_record(
        source_id=_stable_id("source", {"locator": locator, "content": content}),
        locator=locator,
        url=_optional_text(item.get("url")),
        evidence_role=_source_evidence_role(item.get("evidence_role")),
        title=_optional_text(item.get("title")),
        author=_optional_text(item.get("author")),
        publisher=_optional_text(item.get("publisher")),
        published_at=_optional_text(item.get("published_at")),
        license=_optional_text(item.get("license")),
        access_constraints=_optional_text(item.get("access_constraints")),
        content=content,
        content_type=_optional_text(item.get("content_type")),
        access_outcome="supplied",
        extraction_method="supplied_text",
        query=None,
        source_type="supplied",
        retrieved_at=_optional_text(item.get("retrieved_at")),
    )


def _web_source(
    hit: dict[str, Any],
    fetched: dict[str, Any],
    query: dict[str, Any],
    limits: ExecutionLimits,
    *,
    live_binding_verified: bool,
) -> dict[str, Any]:
    canonical_url = canonicalize_url(fetched["final_url"])
    content = fetched["content"][: limits.max_content_chars]
    if "html" in (fetched.get("content_type") or "").lower() or _looks_like_html(content):
        content, extraction = _html_text(content), "html_text_extraction"
    else:
        extraction = "plain_text"
    return _source_record(
        source_id=_stable_id("source", {"url": canonical_url}),
        locator=canonical_url,
        url=canonical_url,
        evidence_role=_source_evidence_role(hit.get("evidence_role")),
        title=redact_sensitive_text(fetched.get("title") or hit.get("title") or "") or None,
        author=redact_sensitive_text(hit.get("author") or "") or None,
        publisher=redact_sensitive_text(hit.get("publisher") or "") or None,
        published_at=_optional_text(hit.get("published_at")),
        license=_optional_text(hit.get("license")),
        access_constraints=_optional_text(hit.get("access_constraints")),
        content=content,
        content_type=fetched.get("content_type"),
        access_outcome="retrieved",
        extraction_method=extraction,
        query=query,
        browser_diagnostics=fetched.get("browser_diagnostics"),
        live_binding_verified=live_binding_verified,
        requested_url=canonicalize_url(hit["url"]),
        source_type="web",
        source_content_sha256=fetched.get("content_sha256"),
    )


def _failed_source(
    hit: dict[str, Any], canonical_url: str, error: Exception, query: dict[str, Any]
) -> dict[str, Any]:
    return {
        "id": _stable_id("source", {"url": canonical_url}),
        "requested_url": canonicalize_url(hit["url"]),
        "final_url": None,
        "canonical_url": canonical_url,
        "locator": canonical_url,
        "evidence_role": _source_evidence_role(hit.get("evidence_role")),
        "title": redact_sensitive_text(hit["title"]) if hit.get("title") else None,
        "author": redact_sensitive_text(hit["author"]) if hit.get("author") else None,
        "publisher": redact_sensitive_text(hit["publisher"]) if hit.get("publisher") else None,
        "published_at": _optional_text(hit.get("published_at")),
        "license": _optional_text(hit.get("license")),
        "access_constraints": _optional_text(hit.get("access_constraints")),
        "retrieved_at": _utc_now(),
        "source_type": "web",
        "access_outcome": "failed",
        "access_error": redact_sensitive_text(f"{type(error).__name__}: {error}"),
        "content_sha256": None,
        "extraction_method": None,
        "content": None,
        "query_ids": [query["id"]],
        "objective_ids": [query["objective_id"]],
        "relationships": [],
        "independence_status": "not_assessed",
        "retrieval_provenance": {
            "binding": "injected_callable",
            "live_binding_verified": False,
        },
        "browser_diagnostics": {
            "inspected": False,
            "reason": "Content retrieval did not succeed.",
        },
        "credibility_rationale": None,
        "limitations": ["Source content could not be retrieved"],
        "content_type": None,
    }


def _source_record(
    *,
    source_id: str,
    locator: str,
    url: str | None,
    evidence_role: str,
    title: str | None,
    author: str | None,
    publisher: str | None,
    published_at: str | None,
    license: str | None,
    access_constraints: str | None,
    content: str,
    content_type: str | None,
    access_outcome: str,
    extraction_method: str,
    query: dict[str, Any] | None,
    source_type: str,
    browser_diagnostics: dict[str, Any] | None = None,
    live_binding_verified: bool = False,
    requested_url: str | None = None,
    retrieved_at: str | None = None,
    source_content_sha256: str | None = None,
) -> dict[str, Any]:
    digest = (
        source_content_sha256
        if isinstance(source_content_sha256, str)
        and re.fullmatch(r"[0-9a-f]{64}", source_content_sha256)
        else hashlib.sha256(content.encode("utf-8")).hexdigest()
    )
    try:
        canonical = canonicalize_url(url) if url else None
    except ValueError:
        canonical = None
    safe_url = _safe_locator(url) if url else None
    requested = requested_url or url
    safe_requested_url = _safe_locator(requested) if requested else None
    return {
        "id": source_id,
        "requested_url": safe_requested_url,
        "final_url": safe_url,
        "canonical_url": canonical,
        "locator": locator,
        "evidence_role": evidence_role,
        "title": title,
        "author": author,
        "publisher": publisher,
        "published_at": published_at,
        "retrieved_at": retrieved_at or (_utc_now() if source_type == "web" else None),
        "source_type": source_type,
        "access_outcome": access_outcome,
        "access_error": None,
        "content_sha256": digest,
        "content_retained": content is not None,
        "extraction_method": extraction_method,
        "content": content,
        "content_type": content_type,
        "query_ids": [query["id"]] if query else [],
        "objective_ids": [query["objective_id"]] if query else [],
        "relationships": [],
        "license": license,
        "access_constraints": access_constraints,
        "credibility_rationale": None,
        "limitations": ["Credibility was not independently assessed"],
        "retrieval_provenance": {
            "binding": "injected_callable" if url else "supplied_input",
            "live_binding_verified": live_binding_verified,
        },
        "browser_diagnostics": browser_diagnostics
        or {
            "inspected": False,
            "reason": "No browser-rendered webpage was inspected for this source.",
        },
    }


def _add_source(
    source: dict[str, Any],
    sources: list[dict[str, Any]],
    cache: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    canonical = source.get("canonical_url")
    if canonical and canonical in cache:
        cache[canonical]["query_ids"] = sorted(
            set(cache[canonical]["query_ids"] + source["query_ids"])
        )
        cache[canonical]["objective_ids"] = sorted(
            set(cache[canonical]["objective_ids"] + source["objective_ids"])
        )
        return cache[canonical]
    digest = source.get("content_sha256")
    if digest:
        duplicate = next((item for item in sources if item.get("content_sha256") == digest), None)
        if duplicate:
            source["relationships"].append(
                {"type": "derivative_or_duplicate_content", "source_id": duplicate["id"]}
            )
            source["independence_status"] = "duplicate_content_not_independent"
    sources.append(source)
    if canonical:
        if source.get("access_outcome") == "retrieved":
            cache[canonical] = source
    return source


def _extract_evidence(
    source: dict[str, Any],
    objectives: tuple[Objective, ...],
    evidence: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    limits: ExecutionLimits,
) -> None:
    content = source.get("content")
    if not isinstance(content, str):
        return
    lines = content.splitlines()
    for objective in objectives:
        terms = _keywords(objective)
        selected = 0
        for line_number, line in enumerate(lines, start=1):
            quote = line.strip()
            if not quote or not terms.intersection(_keywords_text(quote)):
                continue
            if contains_sensitive_material(quote):
                source["limitations"].append("Potentially sensitive line excluded from evidence.")
                continue
            quote = quote[:1000]
            evidence_id = _stable_id(
                "evidence",
                {"source_id": source["id"], "objective_id": objective.id, "line": line_number},
            )
            if any(item["id"] == evidence_id for item in evidence):
                continue
            evidence_item = {
                "id": evidence_id,
                "objective_id": objective.id,
                "claim_id": None,
                "source_ids": [source["id"]],
                "locator": {
                    "kind": "extracted_text_line",
                    "line": line_number,
                    "label": source["locator"],
                },
                "quote": quote,
                "kind": "observation",
                "value": None,
                "unit": None,
                "denominator": None,
                "population": None,
                "geography": None,
                "timeframe": None,
                "extraction_method": source["extraction_method"],
                "notes": "Verbatim extracted text; interpretation is not asserted.",
            }
            claim_id = _stable_id("claim", {"evidence_id": evidence_id, "quote": quote})
            evidence_item["claim_id"] = claim_id
            evidence.append(evidence_item)
            claims.append(
                {
                    "id": claim_id,
                    "objective_id": objective.id,
                    "text": quote,
                    "kind": "source_observation",
                    "evidence_ids": [evidence_id],
                    "status": "source_grounded",
                }
            )
            selected += 1
            if selected >= limits.max_evidence_per_source_objective:
                break


def _objective_matrix(
    objectives: tuple[Objective, ...],
    evidence: list[dict[str, Any]],
    claims: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    matrix = []
    for objective in objectives:
        linked = [item for item in evidence if item["objective_id"] == objective.id]
        linked_claims = [item for item in claims if item["objective_id"] == objective.id]
        if not objective.applicable:
            status = "not_applicable"
            rationale = "Objective was explicitly marked not applicable in the brief."
        elif not linked:
            status = "unresolved"
            rationale = "No source-grounded evidence was retrieved for this objective."
        else:
            matched = [
                criterion
                for criterion in objective.acceptance_criteria
                if any(criterion.casefold() in item["quote"].casefold() for item in linked)
            ]
            if not objective.acceptance_criteria:
                status = "partially_answered"
                rationale = (
                    "Relevant evidence exists, but the brief specifies no acceptance "
                    "criteria for a completed answer."
                )
            elif len(matched) == len(objective.acceptance_criteria):
                status = "answered"
                rationale = "Evidence was found for all specified acceptance criteria."
            elif matched:
                status = "partially_answered"
                rationale = "Evidence covers only some specified acceptance criteria."
            else:
                status = "partially_answered"
                rationale = (
                    "Relevant evidence exists, but acceptance criteria were not fully matched."
                )
        matrix.append(
            {
                "id": objective.id,
                "question": objective.question,
                "status": status,
                "rationale": rationale,
                "acceptance_criteria": list(objective.acceptance_criteria),
                "matched_criteria": [
                    criterion
                    for criterion in objective.acceptance_criteria
                    if any(criterion.casefold() in item["quote"].casefold() for item in linked)
                ],
                "evidence_ids": [item["id"] for item in linked],
                "claim_ids": [item["id"] for item in linked_claims],
            }
        )
    return matrix


def _find_contradictions(
    objectives: tuple[Objective, ...],
    evidence: list[dict[str, Any]],
    claims: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    contradictions = []
    by_objective: dict[str, list[dict[str, Any]]] = {}
    for item in evidence:
        by_objective.setdefault(item["objective_id"], []).append(item)
    claim_by_evidence = {
        evidence_id: claim["id"] for claim in claims for evidence_id in claim["evidence_ids"]
    }
    for objective in objectives:
        items = by_objective.get(objective.id, [])
        for index, left in enumerate(items):
            for right in items[index + 1 :]:
                left_terms = _keywords_text(left["quote"])
                right_terms = _keywords_text(right["quote"])
                if not left_terms.intersection(right_terms):
                    continue
                if _polarity(left["quote"]) * _polarity(right["quote"]) != -1:
                    continue
                contradictions.append(
                    {
                        "id": _stable_id("contradiction", [left["id"], right["id"]]),
                        "objective_id": objective.id,
                        "claim_ids": [
                            claim_by_evidence[left["id"]],
                            claim_by_evidence[right["id"]],
                        ],
                        "evidence_ids": [left["id"], right["id"]],
                        "status": "unresolved",
                        "detection_method": "lexical_polarity_heuristic",
                        "resolution_evidence_ids": [],
                    }
                )
    return contradictions


def _verify(
    evidence: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    sources: list[dict[str, Any]],
    matrix: list[dict[str, Any]],
) -> dict[str, Any]:
    evidence_by_id = {item["id"]: item for item in evidence}
    source_ids = {item["id"] for item in sources}
    findings = []
    for claim in claims:
        linked = [evidence_by_id[item] for item in claim["evidence_ids"] if item in evidence_by_id]
        if not linked or any(not set(item["source_ids"]).issubset(source_ids) for item in linked):
            findings.append(
                {
                    "type": "unsupported_claim",
                    "claim_id": claim["id"],
                    "evidence_ids": claim["evidence_ids"],
                    "message": "Claim has no resolvable supporting source evidence.",
                }
            )
        if any(claim["text"] != item["quote"] for item in linked):
            findings.append(
                {
                    "type": "claim_evidence_mismatch",
                    "claim_id": claim["id"],
                    "evidence_ids": claim["evidence_ids"],
                    "message": "Claim text differs from its verbatim evidence.",
                }
            )
    return {
        "mode": "independent_read_only_structural_verification",
        "findings": findings,
        "claims_checked": len(claims),
        "citations_resolved": sum(
            1
            for item in evidence
            if item.get("locator") and set(item.get("source_ids", [])).issubset(source_ids)
        ),
        "objectives_checked": len(matrix),
        "limitations": [
            "Semantic entailment, source authority, retractions, and citation-chain "
            "depth require expert or dedicated-provider review."
        ],
    }


def _azimuth_assessment(
    brief: ResearchBrief,
    sources: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
    matrix: list[dict[str, Any]],
    verification: dict[str, Any],
    bundle_status: str,
) -> dict[str, Any]:
    source_ids = [source["id"] for source in sources]
    evidence_ids = [item["id"] for item in evidence]
    roles_known = bool(sources) and all(
        source.get("evidence_role") != "unknown" for source in sources
    )
    archived_ids = [
        source["id"]
        for source in sources
        if source.get("evidence_role") in {"historical", "archive"}
    ]
    references_resolved = verification["citations_resolved"] == len(evidence)
    phases = [
        {
            "id": "A",
            "name": "Align to current truth",
            "status": "completed" if sources else "not_assessed",
            "evidence_ids": evidence_ids,
            "notes": (
                "Only recorded source observations are treated as evidence; evidence "
                "role and retrieval limits remain explicit."
            ),
        },
        {
            "id": "Z",
            "name": "Separate stale state from active evidence",
            "status": "completed" if roles_known else "partial",
            "evidence_ids": source_ids,
            "notes": (
                f"Explicitly tagged historical/archive sources: {len(archived_ids)}. "
                "No source records were deleted or rewritten."
            ),
        },
        {
            "id": "I",
            "name": "Integrate evidence and provenance",
            "status": "completed" if references_resolved else "incomplete",
            "evidence_ids": evidence_ids,
            "notes": f"{len(evidence)} evidence items link to source locators.",
        },
        {
            "id": "M",
            "name": "Map lanes and owners",
            "status": "completed" if brief.execution_lanes else "not_assessed",
            "evidence_ids": [],
            "notes": (
                f"{len(brief.execution_lanes)} declared lanes; declaration is not proof "
                "that parallel agents were run."
            ),
            "lanes": [dict(lane) for lane in brief.execution_lanes],
        },
        {
            "id": "U",
            "name": "Publish canonical research status",
            "status": "completed" if matrix else "incomplete",
            "evidence_ids": evidence_ids,
            "notes": (
                "Canonical status is recorded in this bundle only; repository, package "
                "metadata, and public documentation were not modified."
            ),
        },
        {
            "id": "T",
            "name": "Test and validate evidence",
            "status": (
                "completed"
                if verification.get("mode") == "independent_read_only_structural_verification"
                and not verification["findings"]
                else "incomplete"
            ),
            "evidence_ids": evidence_ids,
            "notes": (
                "Structural claim/citation validation ran; it does not establish "
                "semantic entailment or release readiness."
            ),
        },
        {
            "id": "H",
            "name": "Harmonize archive and active truth",
            "status": "completed" if roles_known else "partial",
            "evidence_ids": archived_ids,
            "notes": (
                "Historical/archive evidence remains preserved and separately tagged; "
                "no archival migration was performed."
            ),
        },
    ]
    completed = sum(phase["status"] == "completed" for phase in phases)
    return {
        "model": "AZIMUTH",
        "sequence": ["A", "Z", "I", "M", "U", "T", "H"],
        "status": "completed" if completed == len(phases) else "partial",
        "phases": phases,
        "canonical_truth_statement": (
            f"This research bundle is {bundle_status} based only on its recorded evidence; "
            "it is not a repository release-readiness certification."
        ),
        "repo_mutations_performed": False,
        "archived_source_ids": archived_ids,
    }


def _render_report(
    brief: ResearchBrief,
    capability: dict[str, Any],
    matrix: list[dict[str, Any]],
    sources: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
    datasets: list[dict[str, Any]],
    azimuth: dict[str, Any],
) -> str:
    lines = [
        f"# {brief.title}",
        "",
        "## Capability and method",
        (
            "- Fresh web retrieval: "
            f"{'available' if capability['fresh_web_research'] else 'not verified'}"
        ),
        f"- Sources recorded: {len(sources)}; evidence items: {len(evidence)}.",
        "- Extracted quotations are observations, not independently established conclusions.",
    ]
    lines.extend(f"- Limitation: {item}" for item in capability["limitations"])
    lines.extend(["", "## Objective matrix"])
    for item in matrix:
        lines.append(f"- **{item['id']} — {item['status']}**: {item['rationale']}")
        for evidence_id in item["evidence_ids"]:
            lines.append(f"  - Evidence: `{evidence_id}`")
    lines.extend(["", "## AZIMUTH assessment"])
    lines.append(f"- Sequence completion: **{azimuth['status']}**.")
    lines.append(f"- {azimuth['canonical_truth_statement']}")
    for phase in azimuth["phases"]:
        lines.append(f"- **{phase['id']} — {phase['name']}: {phase['status']}**. {phase['notes']}")
    lines.extend(["", "## Evidence"])
    for item in evidence:
        lines.append(
            f"- `{item['id']}` — {item['quote']} "
            f"(source `{item['source_ids'][0]}`, {item['locator']['label']}, "
            f"{item['locator']['kind']} {item['locator']['line']})"
        )
    lines.extend(["", "## Dataset profiles"])
    if datasets:
        for dataset in datasets:
            lines.append(
                f"- `{dataset['dataset_id']}`: {dataset['observed']['record_count']} "
                f"parsed records; SHA-256 `{dataset['sha256']}`."
            )
    else:
        lines.append("- No dataset was supplied or profiled.")
    lines.extend(
        [
            "",
            "## Interpretation and recommendations",
            "No additional causal or normative interpretation is asserted by the deterministic pipeline.",
            "",
        ]
    )
    return "\n".join(lines)


class _VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._hidden_depth = 0
        self._hidden_tags = {"script", "style", "noscript", "template"}
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in self._hidden_tags:
            self._hidden_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in self._hidden_tags and self._hidden_depth:
            self._hidden_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._hidden_depth and data.strip():
            self.parts.append(data.strip())


def _html_text(content: str) -> str:
    parser = _VisibleText()
    parser.feed(content)
    return "\n".join(parser.parts)


def _looks_like_html(content: str) -> bool:
    return bool(re.search(r"<\s*(?:html|body|main|article|p|div)\b", content[:1000], re.I))


def _keywords(objective: Objective) -> set[str]:
    return _keywords_text(" ".join((objective.question, *objective.acceptance_criteria)))


def _keywords_text(text: str) -> set[str]:
    return {
        token.casefold()
        for token in re.findall(r"[A-Za-z0-9][A-Za-z0-9_-]{2,}", text)
        if token.casefold() not in {"what", "which", "does", "have", "with", "from", "that", "this"}
    }


def _polarity(text: str) -> int:
    words = _keywords_text(text)
    negative = {
        "not",
        "never",
        "no",
        "absent",
        "failed",
        "decrease",
        "ineffective",
        "false",
        "blocked",
        "unresolved",
        "mismatched",
    }
    positive = {
        "yes",
        "present",
        "increase",
        "effective",
        "supports",
        "true",
        "succeed",
        "ready",
        "verified",
    }
    has_negative = bool(words & negative)
    has_positive = bool(words & positive)
    if has_negative and has_positive and "not" in words:
        return -1
    if has_negative == has_positive:
        return 0
    return -1 if has_negative else 1


def _is_interrupted(deadline: float, cancellation_event: Event | None) -> bool:
    return time.monotonic() >= deadline or bool(cancellation_event and cancellation_event.is_set())


def _optional_text(value: Any) -> str | None:
    return (
        redact_sensitive_text(value.strip()) if isinstance(value, str) and value.strip() else None
    )


def _source_evidence_role(value: Any) -> str:
    allowed = {"current", "historical", "archive", "unknown"}
    return value if isinstance(value, str) and value in allowed else "unknown"


def _safe_locator(value: str) -> str:
    try:
        return canonicalize_url(value)
    except ValueError:
        return redact_sensitive_text(value)


def _stable_id(prefix: str, value: Any) -> str:
    return f"{prefix}-{_digest(value)[:20]}"


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str
    ).encode("utf-8")


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
