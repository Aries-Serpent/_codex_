"""Utilities to merge version-like JSON payloads into deterministic reports."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import re


# Canonical key groups extracted from the specification.
SUMMARY_KEYS = {
    "summary",
    "overview",
    "highlights",
    "recap",
    "what_changed",
    "result",
}
OPEN_KEYS = {
    "open_questions",
    "open_items",
    "unresolved",
    "decisions",
    "tradeoffs",
    "options",
}
NEXT_KEYS = {
    "next_prompt",
    "follow_up",
    "next_steps",
    "plan",
    "prompt",
}
TEST_KEYS = {"tests", "testing", "validation", "checks"}
DOC_KEYS = {
    "docs",
    "documentation",
    "runbook",
    "paths",
    "citations",
    "links",
}
AUX_KEYS = {"changelog", "notes"}

KNOWN_KEYS = SUMMARY_KEYS | OPEN_KEYS | NEXT_KEYS | TEST_KEYS | DOC_KEYS | AUX_KEYS

IGNORED_PREFIX = "@codex implement plan"


CATEGORY_KEYWORDS: List[Tuple[str, Tuple[str, ...]]] = [
    ("Tracking/Guardrails", ("guard", "mlflow", "policy", "track", "safety", "manifest")),
    ("Writers/Logging", ("writer", "logging", "log", "ndjson", "telemetry")),
    ("Rotation/Summarizer", ("rotate", "rotation", "summarizer", "summary stream")),
    ("Tests/Validation", ("test", "pytest", "validate", "check", "lint", "coverage")),
    ("Docs/Runbooks", ("doc", "readme", "guide", "runbook", "manual")),
]

CATEGORY_ORDER = [c for c, _ in CATEGORY_KEYWORDS] + ["Misc"]


QUESTION_FIELDS = ("question", "prompt", "item", "topic", "text", "title")
OPTION_FIELDS = ("options", "choices", "alternatives", "variants")
LABEL_FIELDS = ("label", "name", "title", "option")
DESC_FIELDS = ("description", "details", "text", "summary")
STATUS_FIELDS = ("status", "state", "flag", "tag")

OPTION_PRIORITY_KEYWORDS: List[Tuple[str, Tuple[str, ...]]] = [
    ("offline-safety", ("offline", "file://", "local", "no network", "airgap", "air-gapped")),
    ("determinism", ("deterministic", "seed", "idempotent", "repro", "stable")),
    ("schema-parity", ("schema", "parity", "consistent", "align", "sync")),
    ("legacy-compat", ("legacy", "compat", "fallback")),
]


@dataclass
class Option:
    label: str
    text: str
    status: Optional[str] = None

    def weight(self) -> Tuple[int, int, int, int, str]:
        label_lower = f"{self.label} {self.text}".lower()
        priority_scores: List[int] = []
        for idx, (_, keywords) in enumerate(OPTION_PRIORITY_KEYWORDS):
            priority_scores.append(1 if any(keyword in label_lower for keyword in keywords) else 0)
        return (*priority_scores, self.label.lower())

    def has_preferred_status(self) -> bool:
        if not self.status:
            return False
        status_lower = self.status.lower()
        return any(token in status_lower for token in ("ideal", "preferred", "primary"))

    def has_affirmative_marker(self) -> bool:
        joined = f"{self.label} {self.text}".lower()
        return "✅" in self.label or "✅" in self.text or "preferred" in joined


@dataclass
class OpenQuestion:
    prompt: str
    options: List[Option]


def normalize_key(key: str) -> str:
    """Normalize keys by collapsing whitespace, dashes, and underscores."""

    collapsed = re.sub(r"[\s\-_]+", "_", key.strip().lower())
    return collapsed


def _coerce_lines(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []
        # Split on newlines while keeping embedded bullet text deterministic.
        lines = [ln.strip(" -\t") for ln in stripped.replace("\r", "").splitlines()]
        cleaned = [ln for ln in lines if ln]
        return cleaned or [stripped]
    if isinstance(value, Mapping):
        lines: List[str] = []
        for v in value.values():
            lines.extend(_coerce_lines(v))
        return lines
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        lines: List[str] = []
        for item in value:
            lines.extend(_coerce_lines(item))
        return lines
    return [str(value)]


def _is_version_candidate(obj: Mapping[str, Any]) -> bool:
    normalized_keys = {
        normalize_key(key)
        for key in obj
        if isinstance(key, str)
        and not normalize_key(key).startswith(IGNORED_PREFIX.replace(" ", "_"))
    }
    return bool(normalized_keys & KNOWN_KEYS)


def _collect_versions(obj: Any) -> List[Mapping[str, Any]]:
    versions: List[Mapping[str, Any]] = []
    if isinstance(obj, Mapping):
        if _is_version_candidate(obj):
            versions.append(obj)
        for value in obj.values():
            versions.extend(_collect_versions(value))
    elif isinstance(obj, Sequence) and not isinstance(obj, (str, bytes, bytearray)):
        for item in obj:
            versions.extend(_collect_versions(item))
    return versions


def _extract_summary(version: Mapping[str, Any]) -> List[str]:
    for key, value in version.items():
        if normalize_key(key) in SUMMARY_KEYS:
            return _coerce_lines(value)
    # fallback: synthesize from imperative phrases across entries
    candidate_lines: List[str] = []
    for value in version.values():
        for line in _coerce_lines(value):
            if _looks_actionable(line):
                candidate_lines.append(line)
            if len(candidate_lines) >= 6:
                break
        if len(candidate_lines) >= 6:
            break
    return candidate_lines[:6]


def _looks_actionable(line: str) -> bool:
    verbs = (
        "add",
        "enforce",
        "emit",
        "rotate",
        "update",
        "test",
        "document",
        "guard",
        "ensure",
        "wire",
        "bootstrap",
        "harden",
        "validate",
    )
    lowered = line.lower()
    return any(lowered.startswith(verb) or f" {verb} " in lowered for verb in verbs)


def _extract_tests(version: Mapping[str, Any]) -> List[str]:
    tests: List[str] = []
    for key, value in version.items():
        if normalize_key(key) in TEST_KEYS:
            tests.extend(_coerce_lines(value))
    return tests


def _extract_docs(version: Mapping[str, Any]) -> List[str]:
    docs: List[str] = []
    for key, value in version.items():
        if normalize_key(key) in DOC_KEYS:
            docs.extend(_coerce_lines(value))
    return docs


def _extract_next(version: Mapping[str, Any]) -> List[str]:
    next_items: List[str] = []
    for key, value in version.items():
        if normalize_key(key) in NEXT_KEYS:
            next_items.extend(_coerce_lines(value))
    return next_items


def _extract_open_questions(version: Mapping[str, Any]) -> List[OpenQuestion]:
    questions: List[OpenQuestion] = []
    for key, value in version.items():
        if normalize_key(key) in OPEN_KEYS:
            questions.extend(_coerce_open_questions(value))
    return questions


def _coerce_open_questions(value: Any) -> List[OpenQuestion]:
    results: List[OpenQuestion] = []
    if value is None:
        return results
    if isinstance(value, Mapping):
        questions: List[Any] = []
        if any(normalize_key(k) in OPTION_FIELDS for k in value):
            questions.append(value)
        else:
            for v in value.values():
                results.extend(_coerce_open_questions(v))
            return results
        for entry in questions:
            question_text = _extract_question_text(entry)
            options = _extract_options(entry)
            if question_text or options:
                results.append(OpenQuestion(prompt=question_text or "", options=options))
        return results
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for item in value:
            results.extend(_coerce_open_questions(item))
        return results
    if isinstance(value, str):
        stripped = value.strip()
        if stripped:
            results.append(OpenQuestion(prompt=stripped, options=[]))
    return results


def _extract_question_text(entry: Mapping[str, Any]) -> str:
    for field in QUESTION_FIELDS:
        if field in entry and isinstance(entry[field], str):
            stripped = entry[field].strip()
            if stripped:
                return stripped
    # Attempt to derive from free-form text
    for value in entry.values():
        if isinstance(value, str) and value.strip().endswith("?"):
            return value.strip()
    return ""


def _extract_options(entry: Mapping[str, Any]) -> List[Option]:
    options: List[Option] = []
    for field in OPTION_FIELDS:
        field_key = next((k for k in entry if normalize_key(k) == normalize_key(field)), None)
        if field_key is None:
            continue
        raw_options = entry[field_key]
        if isinstance(raw_options, Sequence) and not isinstance(
            raw_options, (str, bytes, bytearray)
        ):
            for opt in raw_options:
                option = _parse_option(opt)
                if option:
                    options.append(option)
        elif isinstance(raw_options, Mapping):
            option = _parse_option(raw_options)
            if option:
                options.append(option)
    return options


def _parse_option(value: Any) -> Optional[Option]:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        return Option(label=stripped, text="")
    if isinstance(value, Mapping):
        label = ""
        for field in LABEL_FIELDS:
            if field in value and isinstance(value[field], str):
                label = value[field].strip()
                break
        description = ""
        for field in DESC_FIELDS:
            if field in value and isinstance(value[field], str):
                description = value[field].strip()
                break
        status = None
        for field in STATUS_FIELDS:
            if field in value and isinstance(value[field], str):
                status = value[field].strip()
                break
        if not label and description:
            label = description
            description = ""
        if label or description:
            return Option(label=label or "Option", text=description, status=status)
    return None


def _dedupe_preserve_order(items: Iterable[str]) -> List[str]:
    seen: Dict[str, None] = {}
    for item in items:
        normalized = item.strip()
        if not normalized:
            continue
        if normalized not in seen:
            seen[normalized] = None
    return list(seen.keys())


def _categorize_summary(summary_items: Sequence[str]) -> List[str]:
    categorized: Dict[str, List[str]] = {cat: [] for cat in CATEGORY_ORDER}
    for item in summary_items:
        lowered = item.lower()
        category = "Misc"
        for cat, keywords in CATEGORY_KEYWORDS:
            if any(keyword in lowered for keyword in keywords):
                category = cat
                break
        categorized[category].append(item)
    ordered_items: List[str] = []
    for category in CATEGORY_ORDER:
        entries = categorized[category]
        if not entries:
            continue
        entries.sort(key=_summary_sort_key)
        ordered_items.extend(entries)
    return ordered_items


PATH_REGEX = re.compile(r"([\w./-]+\.[\w\d]+(?:[#:L]\d+(?:-\d+)?)?)")


def _summary_sort_key(item: str) -> Tuple[str, str]:
    match = PATH_REGEX.search(item)
    if match:
        return match.group(1), item.lower()
    return item.lower(), item.lower()


def _decide_open_question(question: OpenQuestion) -> Tuple[List[str], str]:
    if not question.options:
        return [], "Needs Decision"
    preferred = [
        option
        for option in question.options
        if option.has_preferred_status() or option.has_affirmative_marker()
    ]
    if preferred:
        labels = [opt.label for opt in sorted(preferred, key=lambda opt: opt.label.lower())]
        return labels, "Selected options marked as preferred or ✅."
    scored = sorted(
        question.options,
        key=lambda option: option.weight(),
        reverse=True,
    )
    top_score = scored[0].weight()
    chosen = [opt for opt in scored if opt.weight() == top_score and any(opt.weight()[:-1])]
    if chosen:
        labels = [opt.label for opt in sorted(chosen, key=lambda opt: opt.label.lower())]
        rationale = _rationale_for_weight(chosen[0])
        return labels, rationale
    return [], "Needs Decision"


def _rationale_for_weight(option: Option) -> str:
    weights = option.weight()[:-1]
    for (name, _), score in zip(OPTION_PRIORITY_KEYWORDS, weights):
        if score:
            if name == "offline-safety":
                return "Prioritize offline safety guardrails."
            if name == "determinism":
                return "Favor deterministic execution path."
            if name == "schema-parity":
                return "Align on schema parity across sources."
            if name == "legacy-compat":
                return "Maintain legacy compatibility when ambiguous."
    return "Needs Decision"


def _format_open_question(question: OpenQuestion) -> Tuple[str, List[str], List[str], str]:
    options_lines: List[str] = []
    for option in sorted(question.options, key=lambda opt: opt.label.lower()):
        descriptor = option.text
        if option.status:
            descriptor = f"{descriptor} ({option.status})" if descriptor else option.status
        text = option.label
        if descriptor:
            text = f"{text} — {descriptor}"
        options_lines.append(text)
    decision_labels, rationale = _decide_open_question(question)
    return question.prompt or "", options_lines, decision_labels, rationale


def _compose_next_prompt(
    summaries: Sequence[str],
    decisions: Sequence[Tuple[str, List[str]]],
    tests: Sequence[str],
    docs: Sequence[str],
    next_steps: Sequence[str],
) -> List[str]:
    scope_focus = next_steps or summaries
    scope_text = ", ".join(scope_focus[:2]) if scope_focus else "Address outstanding summary items."
    decision_text = "; ".join(
        f"{question}: {', '.join(labels) if labels else 'Needs Decision'}"
        for question, labels in decisions
    )
    if not decision_text:
        decision_text = "No pending decisions captured."
    tests_list = tests or ["PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q"]
    docs_list = docs or ["Document updates in docs/CHANGELOG.md and related runbooks."]
    scope_line = f"**Scope** — {scope_text}"
    decisions_line = f"**Decisions** — {decision_text}"
    tests_line = "**Tests** — " + "; ".join(tests_list)
    docs_line = "**Docs** — " + "; ".join(docs_list)
    rollback_line = "**Rollback** — Revert the commit locally (e.g., `git revert HEAD`) and restore touched files."
    non_goals_line = (
        "**Non-Goals** — Avoid expanding beyond the summarized scope or unrelated refactors."
    )
    acceptance_line = "**Acceptance Criteria** — Preserve offline safety, deterministic execution, and bounded artifacts."
    return [
        scope_line,
        decisions_line,
        tests_line,
        docs_line,
        rollback_line,
        non_goals_line,
        acceptance_line,
    ]


def _collect_citations(entries: Sequence[str]) -> List[str]:
    citations = sorted({entry.strip() for entry in entries if entry.strip()})
    return citations


def generate_report(payload: Mapping[str, Any]) -> str:
    """Generate the three-section report from a JSON payload."""

    versions = _collect_versions(payload)
    if not versions:
        consolidated = ["No summary details provided."]
        open_questions: List[OpenQuestion] = []
        tests: List[str] = []
        docs: List[str] = []
        next_items: List[str] = []
    else:
        summaries: List[str] = []
        open_questions = []
        tests = []
        docs = []
        next_items = []
        for version in versions:
            summaries.extend(_extract_summary(version))
            open_questions.extend(_extract_open_questions(version))
            tests.extend(_extract_tests(version))
            docs.extend(_extract_docs(version))
            next_items.extend(_extract_next(version))
        consolidated = _categorize_summary(_dedupe_preserve_order(summaries))
        tests = _dedupe_preserve_order(tests)
        docs = _dedupe_preserve_order(docs)
        next_items = _dedupe_preserve_order(next_items)

    lines: List[str] = []
    lines.append("### 1) Consolidated Summary")
    if consolidated:
        for item in consolidated:
            lines.append(f"- {item}")
    else:
        lines.append("- No summary details provided.")

    lines.append("\n### 2) Unified Open Questions")
    if open_questions:
        for question in open_questions:
            prompt, options, decisions, rationale = _format_open_question(question)
            prompt_text = prompt or "Open question"
            lines.append(f"- {prompt_text}")
            if options:
                lines.append("  - Options:")
                for option in options:
                    lines.append(f"    - {option}")
            else:
                lines.append("  - Options: None captured")
            decision_repr = f"[{', '.join(decisions)}]" if decisions else "[]"
            lines.append(f"  - **Decision:** {decision_repr}")
            lines.append(f"  - **Rationale:** {rationale}")
    else:
        lines.append("- No open questions detected.")

    decision_pairs = [
        (
            (question.prompt or "Open question"),
            _decide_open_question(question)[0],
        )
        for question in open_questions
    ]

    lines.append("\n### 3) Next Prompt")
    for entry in _compose_next_prompt(consolidated, decision_pairs, tests, docs, next_items):
        lines.append(f"- {entry}")

    citations = _collect_citations(docs)
    if citations:
        lines.append("\nCitations")
        for citation in citations:
            lines.append(f"- {citation}")

    return "\n".join(lines)


__all__ = ["generate_report"]
