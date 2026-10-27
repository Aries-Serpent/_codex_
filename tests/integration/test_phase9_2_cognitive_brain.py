"""Contract checks for the *archived* Phase 9.2 design specifications.

These documents are historical design evidence, not the live runtime contract.
Validate their concrete schemas, examples and references without promoting their
sample metrics, FINAL front matter or catalog presence to current phase status.
See .codex/archive/README.md for the historical/active documentation boundary.
"""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / ".codex/archive/phase-reports/phase-1-10"
NAMES = (
    "LTM_PATTERNS",
    "PATTERN_PROMOTION_RULES",
    "SESSION_CONTEXT",
    "CHECKPOINT_PROCEDURES",
    "RECOVERY_PROCEDURES",
)


def document(name):
    assert name in NAMES
    path = ARCHIVE / f"PHASE_9_2_{name}.md"
    assert path.is_file(), f"Missing archived specification: {path}"
    content = path.read_text(encoding="utf-8")
    assert re.search(r'^version: "1\.0"$', content, re.M), path
    return content


def section(name, heading):
    """Return a design section, excluding headings inside fenced examples.

    The archive embeds Markdown examples containing inner shell fences. Track
    those nested example fences too; Python comments are not document headings.
    """
    content = document(name)
    headings = []
    fences = []
    offset = 0
    for line in content.splitlines(keepends=True):
        fence = re.match(r"^(`{3,})(.*)$", line.strip())
        if fence:
            if fence[2].strip() or not fences:
                fences.append(len(fence[1]))
            elif len(fence[1]) >= fences[-1]:
                fences.pop()
        elif not fences:
            match = re.match(r"^(#{2,4}) (.+?)\s*$", line)
            if match:
                headings.append((offset, offset + len(line), len(match[1]), match[2]))
        offset += len(line)
    matches = [entry for entry in headings if entry[3] == heading]
    assert len(matches) == 1, f"{name}: expected one heading {heading!r}"
    start, body_start, level, _ = matches[0]
    end = next(
        (pos for pos, _, depth, _ in headings if pos > start and depth <= level), len(content)
    )
    body = content[body_start:end]
    assert body.strip(), f"{name}: empty section {heading!r}"
    return body


def pattern_records():
    content = document("LTM_PATTERNS").split("## Summary Statistics")[0]
    records = {}
    for match in re.finditer(
        r"^### ((?:RP|L|C)-\d{3}): ([^\n]+)\n(.*?)(?=^### |^## |\Z)",
        content,
        re.M | re.S,
    ):
        pattern_id, title, body = match.groups()
        assert pattern_id not in records, f"Duplicate {pattern_id}"
        fields = {
            key: value.strip()
            for key, value in re.findall(r"^\*\*([^*]+):\*\*[ \t]*(.*)$", body, re.M)
        }
        records[pattern_id] = (title, fields, body)
    assert len(records) == 23, "Archive defines 12 RP + 8 L + 3 C entries, not 50"
    return records


def field_values(field):
    values = []
    for pattern_id, (_, fields, _) in pattern_records().items():
        assert field in fields, f"{pattern_id}: missing {field}"
        assert fields[field], f"{pattern_id}: empty {field}"
        values.append(fields[field])
    return values


def recovery(procedure):
    return section("RECOVERY_PROCEDURES", procedure)


class TestPatternIngestion:
    """Validate actual archive records rather than summary/example metrics."""

    def test_load_ltm_pattern_catalog(self):
        records = pattern_records()
        for prefix, count in (("RP", 12), ("L", 8), ("C", 3)):
            assert sum(key.startswith(prefix + "-") for key in records) == count

    def test_pattern_schema_validation(self):
        common = (
            "Category",
            "Success Rate",
            "Confidence Threshold",
            "Fix Time (minutes)",
            "Routing Agent",
            "Fallback Agent",
            "Description",
            "Complexity Level",
            "Prerequisite Patterns",
        )
        for pattern_id, (_, fields, body) in pattern_records().items():
            for field in common:
                assert field in fields, f"{pattern_id}: missing {field}"
            assert re.search(r"\*\*Description:\*\*\s+\S", body), pattern_id
            # Composite records intentionally have no Improvement Areas field.
            if not pattern_id.startswith("C-"):
                assert re.search(r"\*\*Improvement Areas:\*\*\s+- \S", body), pattern_id

    def test_pattern_confidence_range(self):
        for value in field_values("Confidence Threshold"):
            assert re.fullmatch(r"(?:0\.\d+|1\.0+)", value)
            assert 0 <= float(value) <= 1

    def test_pattern_success_rate_format(self):
        for value in field_values("Success Rate"):
            assert re.fullmatch(r"\d+%", value), value
            assert 0 <= int(value[:-1]) <= 100

    def test_pattern_routing_agent_exists(self):
        # Historical routing identifiers, not a claim about today's registry.
        for field in ("Routing Agent", "Fallback Agent"):
            for value in field_values(field):
                assert re.fullmatch(r"[a-z][a-z0-9-]+", value), value
        routes = field_values("Routing Agent")
        assert "ci-auto-healer-agent" in routes
        assert "python-312-type-fixer" in routes

    def test_pattern_prerequisite_consistency(self):
        records = pattern_records()
        for pattern_id, (_, fields, _) in records.items():
            value = fields["Prerequisite Patterns"]
            if value == "None":
                continue
            refs = re.findall(r"(?:RP|L|C)-\d{3}", value)
            assert refs, f"{pattern_id}: invalid prerequisites {value}"
            assert set(refs) <= records.keys(), f"{pattern_id}: unresolved {refs}"
            assert pattern_id not in refs

    def test_pattern_category_consistency(self):
        expected = {
            "Import & Dependency Errors",
            "Type System & Compatibility",
            "Test Assertions & Validation",
            "Linting & Code Quality",
            "Workflow & CI Configuration",
            "Documentation & Links",
            "Runtime & Execution Errors",
            "Multi-pattern composite",
            "Code Quality",  # Learned L-003/L-006 use this historical category.
        }
        assert set(field_values("Category")) == expected

    def test_phase_9_2_vs_phase_8_patterns(self):
        records = pattern_records()
        assert {key for key in records if key.startswith("RP-")} == {
            f"RP-{i:03}" for i in range(1, 13)
        }
        learned = [fields for key, (_, fields, _) in records.items() if key.startswith("L-")]
        assert len(learned) == 8
        assert all(fields["Phase Introduced"] == "8" for fields in learned)

    def test_pattern_false_positive_risk(self):
        # Only core RP entries define this field in the historical schema.
        for pattern_id, (_, fields, _) in pattern_records().items():
            if pattern_id.startswith("RP-"):
                value = fields["False Positive Risk"]
                assert re.fullmatch(r"\d+%", value), pattern_id
                assert 0 <= int(value[:-1]) <= 50


class TestPatternPromotion:
    """Validate documented promotion criteria, not execution of pseudocode."""

    def test_promotion_rules_loaded(self):
        assert "STM → LTM" in document("PATTERN_PROMOTION_RULES")

    def test_minimum_observations_requirement(self):
        body = section("PATTERN_PROMOTION_RULES", "Minimum Observations Requirement")
        assert re.search(r"\| \*\*Gold\*\* \| 5 \|", body)
        assert "pattern.observations >= 5" in section(
            "PATTERN_PROMOTION_RULES", "Final Confidence Score"
        )

    def test_success_rate_threshold(self):
        assert "pattern.success_rate >= 0.80" in section(
            "PATTERN_PROMOTION_RULES", "Final Confidence Score"
        )

    def test_confidence_scoring_algorithm(self):
        body = section("PATTERN_PROMOTION_RULES", "Final Confidence Score")
        for expression in (
            "base_conf +",
            "recency_boost +",
            "conflict_penalty",
            ") * success_mult",
            "max(0.0, min(1.0, final_confidence))",
        ):
            assert expression in body

    def test_recency_decay_schedule(self):
        body = section("PATTERN_PROMOTION_RULES", "Decay Schedule")
        for category in (
            "fresh (0-7 days)",
            "current (8-30 days)",
            "stale (31-60 days)",
            "very_stale (61-90 days)",
            "archival (91+ days)",
        ):
            assert category in body
        # The archive's table and scoring pseudocode disagree on decay magnitude.
        # Do not turn either into a live runtime constant.

    def test_confidence_boost_for_recent_patterns(self):
        body = section("PATTERN_PROMOTION_RULES", "Recency Boost")
        assert re.search(r"if days_old <= 7:\s+return \+0.10", body)

    def test_conflict_detection_categories(self):
        for heading in (
            "1. Contradictory Fix Strategies",
            "2. Overlapping Signatures",
            "3. Agent Capability Conflicts",
        ):
            assert "Resolution:" in section("PATTERN_PROMOTION_RULES", heading)
        assert (
            "prerequisite"
            in section("PATTERN_PROMOTION_RULES", "Conflict Detection Algorithm").lower()
        )

    def test_promotion_workflow_documented(self):
        body = section("PATTERN_PROMOTION_RULES", "Automated Promotion Workflow")
        headings = re.findall(r"^### Step \d: (.+)", body, re.M)
        assert headings == [
            "Detection",
            "Aggregation",
            "Confidence Scoring",
            "Promotion Decision",
            "Integration into LTM",
        ]

    def test_promotion_metrics_defined(self):
        for heading in (
            "Promotion Success Rate",
            "LTM Pattern Stability",
            "Conflict Resolution Efficiency",
        ):
            assert section("PATTERN_PROMOTION_RULES", heading).strip()

    def test_pattern_supersession_procedure(self):
        body = section("PATTERN_PROMOTION_RULES", "Pattern Supersession")
        assert "supersed" in body.lower()
        assert "historical reference" in body


class TestSessionContextInjection:
    """Validate the archived token budget and context format."""

    def test_session_context_spec_loaded(self):
        assert "# PHASE 9.2 Session Context Injection Specification" in document("SESSION_CONTEXT")

    def test_token_budget_defined(self):
        assert section("SESSION_CONTEXT", "Total Budget: 2000 tokens")

    def test_token_allocation_breakdown(self):
        body = section("SESSION_CONTEXT", "Total Budget: 2000 tokens")
        allocations = re.findall(r": (\d+) tokens \((\d+)%\)", body)
        assert [(int(a), int(b)) for a, b in allocations] == [
            (800, 40),
            (600, 30),
            (400, 20),
            (200, 10),
        ]
        assert sum(int(a) for a, _ in allocations) == 2000
        assert sum(int(b) for _, b in allocations) == 100

    def test_priority_scoring_function(self):
        body = section("SESSION_CONTEXT", "Scoring Function")
        weights = dict(re.findall(r"(\w+)_score \* (0\.\d+)", body))
        assert weights == {
            "recency": "0.35",
            "confidence": "0.25",
            "success": "0.20",
            "relevance": "0.20",
        }
        assert sum(map(float, weights.values())) == pytest.approx(1)

    def test_priority_tier_definitions(self):
        body = section("SESSION_CONTEXT", "Priority Tiers")
        assert len(re.findall(r"^tier_[1-5]", body, re.M)) == 5
        assert sum(map(int, re.findall(r"allocation: (\d+) tokens", body))) == 2000

    def test_recency_component_weight(self):
        assert "recency_score * 0.35" in section("SESSION_CONTEXT", "Scoring Function")

    def test_confidence_component_weight(self):
        assert "confidence_score * 0.25" in section("SESSION_CONTEXT", "Scoring Function")

    def test_fallback_degradation_strategy(self):
        body = section("SESSION_CONTEXT", "Dynamic Allocation").lower()
        for step in ("1. truncate", "2. remove", "3. collapse", "4. remove"):
            assert step in body
        assert "minimal" in section("SESSION_CONTEXT", "Budget Exceeded Scenarios").lower()

    def test_pattern_format_versions(self):
        body = section("SESSION_CONTEXT", "Pattern Format Versions")
        assert "version_1_0:" in body and "version_0_9_deprecated:" in body
        assert "migration:" in body

    def test_backward_compatibility_migration(self):
        body = section("SESSION_CONTEXT", "Migration Procedure")
        assert "def migrate_v0_9_to_v1_0" in body
        assert "return" in body

    def test_session_context_injection_format(self):
        body = section("SESSION_CONTEXT", "YAML Header")
        for field in (
            "session_context_version",
            "injected_at",
            "budget_used",
            "budget_available",
            "budget_utilization",
            "patterns_included",
        ):
            assert re.search(rf"^{field}:", body, re.M), field
        assert "```markdown" in section("SESSION_CONTEXT", "Pattern Entry Format")

    def test_compact_format_for_low_budget(self):
        body = section("SESSION_CONTEXT", "Compact Format (Low Token Budget)")
        assert "| Pattern | Confidence | Success | Routing Agent |" in body
        assert "RP-001" in body

    def test_budget_exceeded_handling(self):
        body = section("SESSION_CONTEXT", "Budget Exceeded Scenarios")
        assert "budget" in body and "return" in body

    def test_integration_points_documented(self):
        body = section("SESSION_CONTEXT", "Integration Points").lower()
        for integration in ("cli", "agent", "checkpoint", "session"):
            assert integration in body

    def test_metrics_and_monitoring_defined(self):
        body = document("SESSION_CONTEXT")
        assert "budget_utilization:" in body
        assert re.search(r"^## .*Metric", body, re.M)


class TestCheckpointProcedures:
    """Validate fields actually declared by CascadeCheckpoint."""

    def test_checkpoint_spec_loaded(self):
        assert "# PHASE 9.2 Checkpoint Procedures" in document("CHECKPOINT_PROCEDURES")

    def test_checkpoint_frequency_defined(self):
        body = section("CHECKPOINT_PROCEDURES", "Frequency")
        assert re.search(
            r"failure_count_since_last_checkpoint >= 50 or\s+time_since_last_checkpoint >= 300",
            body,
        )

    def test_checkpoint_contents_defined(self):
        body = section("CHECKPOINT_PROCEDURES", "Data Structure")
        fields = set(re.findall(r"^    (\w+):", body, re.M))
        assert {
            "session_id",
            "checkpoint_id",
            "timestamp",
            "total_failures_processed",
            "git_branch",
            "git_commit_hash",
            "git_working_dir_clean",
            "git_staged_changes",
            "validation_results",
            "checkpoint_hash",
            "checksum_validation",
        } <= fields

    def test_checkpoint_validation_checks(self):
        body = section("CHECKPOINT_PROCEDURES", "Pre-Recovery Checks")
        for check in (
            "checksum",
            "git_state",
            "pattern_catalog",
            "ltm_freshness",
            "session_context",
        ):
            assert f"'{check}': validate_" in body
        assert "all(checks.values())" in body

    def test_checkpoint_storage_strategy(self):
        body = section("CHECKPOINT_PROCEDURES", "Checkpoint Storage")
        assert "**Primary:** SQLite" in body
        assert "**Backup:** JSON" in body

    def test_checkpoint_retention_policy(self):
        body = section("CHECKPOINT_PROCEDURES", "Checkpoint Storage")
        assert "Keep last 10 checkpoints per session" in body
        assert "after 7 days" in body

    def test_recovery_scenarios_documented(self):
        body = section("CHECKPOINT_PROCEDURES", "Failure Recovery Scenarios")
        headings = re.findall(r"^### Scenario \d: (.+)", body, re.M)
        assert headings == [
            "Clean Recovery (Normal Path)",
            "Process Crash Recovery",
            "Network Failure Recovery",
            "Data Corruption Recovery",
            "Timeout During Classification",
        ]

    def test_consistency_validation_before_recovery(self):
        body = section("CHECKPOINT_PROCEDURES", "Pre-Recovery Checks")
        assert "def validate_consistency_before_recovery(checkpoint)" in body
        assert "return all_passed, checks" in body


class TestRecoveryProcedures:
    """Validate concrete retry, escalation and recovery design examples."""

    def test_recovery_procedures_loaded(self):
        assert "# PHASE 9.2 Recovery Procedures" in document("RECOVERY_PROCEDURES")

    def test_network_failure_recovery(self):
        body = recovery("Procedure 1: Network Failure Recovery")
        for term in ("backoff", "retry", "escalat"):
            assert term in body.lower()

    def test_network_failure_max_retries(self):
        assert re.search(r"max_attempts\s*=\s*5", recovery("Procedure 1: Network Failure Recovery"))

    def test_process_crash_recovery(self):
        body = recovery("Procedure 2: Process Crash Recovery")
        assert "checkpoint" in body and "heartbeat" in body

    def test_timeout_handling(self):
        body = recovery("Procedure 3: Timeout Handling & Escalation")
        assert "escalate_failure" in body
        assert "'action': 'ESCALATE'" in body
        assert "trigger='timeout_emergency'" in body

    def test_timeout_sla_threshold(self):
        body = recovery("Procedure 3: Timeout Handling & Escalation")
        assert re.search(r"(?:timeout|sla)\w*\s*=\s*5(?:\.0)?", body, re.I)

    def test_data_corruption_recovery(self):
        body = recovery("Procedure 4: Data Corruption Recovery")
        for term in ("checksum", "backup", "previous"):
            assert term in body.lower()

    def test_data_corruption_max_attempts(self):
        # This is the algorithm's retry limit, not the matrix's total-attempt count.
        body = recovery("Procedure 4: Data Corruption Recovery")
        assert "max_corruption_attempts = 2" in body
        assert "attempt_count >= max_corruption_attempts" in body

    def test_unknown_pattern_recovery(self):
        body = recovery("Procedure 5: Unknown Pattern Recovery")
        assert "stm" in body.lower()
        assert "pattern" in body and "escalate" in body

    def test_unknown_pattern_max_attempts(self):
        body = recovery("Procedure 5: Unknown Pattern Recovery")
        assert re.search(r"max_unknown_attempts\s*=\s*5", body)
        assert "attempt_count >= max_unknown_attempts" in body
        # The design also escalates at attempt_count >= 3 below this guard.
        # The declared cap is not proof that five retries actually execute.
        assert "if attempt_count >= 3:" in body

    def test_recovery_matrix_defined(self):
        body = recovery("Recovery Strategy Matrix")
        assert "| Failure Type | Detection | Strategy | Retry | Escalate | Max Attempts |" in body
        for failure in (
            "Network",
            "Process crash",
            "Timeout",
            "Data corruption",
            "Unknown pattern",
        ):
            assert f"| {failure} |" in body

    def test_compound_recovery_scenarios(self):
        body = recovery("Compound Recovery Scenarios (5)")
        ids = re.findall(r"^### (CR-\d{3}):", body, re.M)
        assert ids == [f"CR-{i:03}" for i in range(1, 6)]

    def test_escalation_criteria_defined(self):
        for index, title in enumerate(
            (
                "Network Failure Recovery",
                "Process Crash Recovery",
                "Timeout Handling & Escalation",
                "Data Corruption Recovery",
                "Unknown Pattern Recovery",
            ),
            1,
        ):
            body = recovery(f"Procedure {index}: {title}")
            assert "### Escalation Criteria" in body
            assert "escalat" in body.lower()

    def test_monitoring_and_alerting(self):
        assert "metrics:" in section("RECOVERY_PROCEDURES", "Recovery Metrics")
        assert "alerts:" in section("RECOVERY_PROCEDURES", "Alert Rules")


class TestEndToEndIntegration:
    """Cross-document historical design references, not phase-completion gates."""

    def test_all_deliverables_present(self):
        for name in NAMES:
            assert document(name)

    def test_pattern_catalog_referenced_in_promotion(self):
        body = section("PATTERN_PROMOTION_RULES", "Step 5: Integration into LTM")
        assert "ltm.patterns.append(ltm_entry)" in body
        assert "stm.patterns.remove(pattern_id)" in body
        assert "PHASE_9_2_LTM_PATTERNS.md" in section("PATTERN_PROMOTION_RULES", "Reference")

    def test_pattern_promotion_referenced_in_session_context(self):
        body = document("SESSION_CONTEXT")
        assert "LTM" in body
        assert "PHASE_9_2_PATTERN_PROMOTION_RULES.md" in body

    def test_checkpoint_procedures_reference_recovery(self):
        body = section("CHECKPOINT_PROCEDURES", "Integration with Recovery Procedures")
        assert "PHASE_9_2_RECOVERY_PROCEDURES.md" in body
        assert (ARCHIVE / "PHASE_9_2_RECOVERY_PROCEDURES.md").is_file()

    def test_cross_references_valid(self):
        references = set()
        for name in NAMES:
            refs = re.findall(r"PHASE_9_2_(?:" + "|".join(NAMES) + r")\.md", document(name))
            references.update(refs)
            for ref in refs:
                assert (ARCHIVE / ref).is_file(), f"{name}: unresolved {ref}"
        assert len(references) >= 4, "Expected connected historical design references"


class TestHistoricalContractGuards:
    """Regression guards: malformed artifacts must not pass vacuously."""

    @pytest.mark.parametrize(
        "old,new,check",
        [
            (
                "**Confidence Threshold:** 0.90",
                "**Confidence Threshold:** 9.90",
                "test_pattern_confidence_range",
            ),
            (
                "**Success Rate:** 92%",
                "**Success Rate:** invalid",
                "test_pattern_success_rate_format",
            ),
            (
                "**Prerequisite Patterns:** None",
                "**Prerequisite Patterns:** RP-999",
                "test_pattern_prerequisite_consistency",
            ),
            (
                "**Fallback Agent:** code-scanning-remediation-agent",
                "**Removed Field:** code-scanning-remediation-agent",
                "test_pattern_schema_validation",
            ),
        ],
    )
    def test_invalid_record_is_rejected(self, monkeypatch, old, new, check):
        content = document("LTM_PATTERNS")
        assert old in content
        monkeypatch.setitem(
            pattern_records.__globals__, "document", lambda _: content.replace(old, new, 1)
        )
        with pytest.raises(AssertionError):
            getattr(TestPatternIngestion(), check)()

    def test_empty_catalog_is_rejected(self, monkeypatch):
        monkeypatch.setitem(pattern_records.__globals__, "document", lambda _: "# No records")
        with pytest.raises(AssertionError, match="23"):
            pattern_records()

    def test_fenced_examples_are_not_section_boundaries(self, monkeypatch):
        content = (
            "## Target\n```python\n# comment\n## Not a heading\n```\n"
            "```markdown\n### Example\n```bash\ntrue\n```\n```\n"
            "required body\n## Next\nnot part of target\n"
        )
        monkeypatch.setitem(section.__globals__, "document", lambda _: content)
        body = section("SESSION_CONTEXT", "Target")
        assert "required body" in body
        assert "not part of target" not in body
        with pytest.raises(AssertionError):
            section("SESSION_CONTEXT", "Not a heading")
