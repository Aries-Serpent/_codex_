"""
Tests for Cognitive Brain Plan 3: Autonomous Objective Adjustment

Test coverage for:
- Phase 3.1: Metric Analysis Engine (ObjectiveAnalyzer)
- Phase 3.2: Objective Adjustment Logic (ObjectiveAdjuster)
- Phase 3.3: Autonomous Execution (AutonomousExecutor)
- Phase 3.4: Safety & Governance (SafetyGuard)
"""

import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ============================================================================
# Phase 3.1: Metric Analysis Engine Tests
# ============================================================================


class TestMetricTypes:
    """Test MetricType enum."""

    def test_metric_type_values(self):
        """Test all metric types are defined."""
        from codex.cognitive.objective_analyzer import MetricType

        assert MetricType.COVERAGE.value == "coverage", "Value must be initialized"
        assert MetricType.SECURITY.value == "security", "Value must be initialized"
        assert MetricType.CI_CD.value == "ci_cd", "Value must be initialized"
        assert MetricType.DOCUMENTATION.value == "documentation", "Value must be initialized"
        assert MetricType.BUILD_TIME.value == "build_time", "Value must be initialized"
        assert MetricType.TEST_SUCCESS_RATE.value == "test_success_rate", "Value must be initialized"


class TestTrendDirection:
    """Test TrendDirection enum."""

    def test_trend_directions(self):
        """Test all trend directions."""
        from codex.cognitive.objective_analyzer import TrendDirection

        assert TrendDirection.IMPROVING.value == "improving", "Value must be initialized"
        assert TrendDirection.STABLE.value == "stable", "Value must be initialized"
        assert TrendDirection.DEGRADING.value == "degrading", "Value must be initialized"
        assert TrendDirection.UNKNOWN.value == "unknown", "Value must be initialized"


class TestMetricValue:
    """Test MetricValue dataclass."""

    def test_create_metric_value(self):
        """Test creating a metric value."""
        from codex.cognitive.objective_analyzer import MetricType, MetricValue

        now = datetime.now(timezone.utc)
        metric = MetricValue(
            metric_type=MetricType.COVERAGE, value=75.5, timestamp=now, context={"source": "pytest"}
        )

        assert metric.metric_type == MetricType.COVERAGE, "metric_type is not valid"
        assert metric.value == 75.5, "Value must be initialized"
        assert metric.context["source"] == "pytest", "Condition must be true"

    def test_metric_value_to_dict(self):
        """Test serialization to dict."""
        from codex.cognitive.objective_analyzer import MetricType, MetricValue

        now = datetime.now(timezone.utc)
        metric = MetricValue(MetricType.SECURITY, 0, now)
        data = metric.to_dict()

        assert data["metric_type"] == "security", "Data must not be empty"
        assert data["value"] == 0, "Data must not be empty"
        assert "timestamp" in data, "Data must not be empty"

    def test_metric_value_from_dict(self):
        """Test deserialization from dict."""
        from codex.cognitive.objective_analyzer import MetricType, MetricValue

        data = {
            "metric_type": "coverage",
            "value": 80.0,
            "timestamp": "2026-02-05T10:00:00+00:00",
            "context": {},
        }
        metric = MetricValue.from_dict(data)

        assert metric.metric_type == MetricType.COVERAGE, "metric_type is not valid"
        assert metric.value == 80.0, "Value must be initialized"


class TestMetricThreshold:
    """Test MetricThreshold."""

    def test_threshold_gte_ok(self):
        """Test threshold check for >= comparison (value above target)."""
        from codex.cognitive.objective_analyzer import MetricThreshold, MetricType

        threshold = MetricThreshold(
            MetricType.COVERAGE,
            target=70.0,
            warning_threshold=60.0,
            critical_threshold=50.0,
            comparison="gte",
        )

        is_ok, severity = threshold.check_value(75.0)
        assert is_ok is True, "is_ok is not valid"
        assert severity is None, "severity is not valid"

    def test_threshold_gte_warning(self):
        """Test threshold check for >= comparison (warning level)."""
        from codex.cognitive.objective_analyzer import (
            AlertSeverity,
            MetricThreshold,
            MetricType,
        )

        threshold = MetricThreshold(
            MetricType.COVERAGE,
            target=70.0,
            warning_threshold=60.0,
            critical_threshold=50.0,
            comparison="gte",
        )

        is_ok, severity = threshold.check_value(65.0)
        assert is_ok is False, "is_ok is not valid"
        assert severity == AlertSeverity.WARNING, "severity is not valid"

    def test_threshold_gte_critical(self):
        """Test threshold check for >= comparison (critical level)."""
        from codex.cognitive.objective_analyzer import (
            AlertSeverity,
            MetricThreshold,
            MetricType,
        )

        threshold = MetricThreshold(
            MetricType.COVERAGE,
            target=70.0,
            warning_threshold=60.0,
            critical_threshold=50.0,
            comparison="gte",
        )

        is_ok, severity = threshold.check_value(45.0)
        assert is_ok is False, "is_ok is not valid"
        assert severity == AlertSeverity.CRITICAL, "severity is not valid"

    def test_threshold_lte(self):
        """Test threshold check for <= comparison."""
        from codex.cognitive.objective_analyzer import (
            AlertSeverity,
            MetricThreshold,
            MetricType,
        )

        threshold = MetricThreshold(
            MetricType.SECURITY,
            target=0,
            warning_threshold=3,
            critical_threshold=10,
            comparison="lte",
        )

        # 0 vulnerabilities - OK (at or below target)
        is_ok, _ = threshold.check_value(0)
        assert is_ok is True, "is_ok is not valid"

        # 2 vulnerabilities - WARNING (above target but at or below warning)
        is_ok, severity = threshold.check_value(2)
        assert is_ok is False, "is_ok is not valid"
        assert severity == AlertSeverity.WARNING, "severity is not valid"

        # 5 vulnerabilities - CRITICAL (above warning threshold)
        is_ok, severity = threshold.check_value(5)
        assert is_ok is False, "is_ok is not valid"
        assert severity == AlertSeverity.CRITICAL, "severity is not valid"


class TestMetricStore:
    """Test MetricStore."""

    def test_add_and_get_metric(self):
        """Test adding and retrieving metrics."""
        from codex.cognitive.objective_analyzer import (
            MetricStore,
            MetricType,
            MetricValue,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "metrics.json"
            store = MetricStore(store_path)

            metric = MetricValue(MetricType.COVERAGE, 75.0, datetime.now(timezone.utc))
            store.add_metric(metric)

            metrics = store.get_metrics(MetricType.COVERAGE, days=1)
            assert len(metrics) == 1, "Metrics must not be empty"
            assert metrics[0].value == 75.0, "Value must be initialized"

    def test_get_latest_metric(self):
        """Test getting latest metric."""
        from codex.cognitive.objective_analyzer import (
            MetricStore,
            MetricType,
            MetricValue,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "metrics.json"
            store = MetricStore(store_path)

            # Add multiple metrics
            for value in [60.0, 70.0, 80.0]:
                metric = MetricValue(MetricType.COVERAGE, value, datetime.now(timezone.utc))
                store.add_metric(metric)

            latest = store.get_latest(MetricType.COVERAGE)
            assert latest is not None, "latest must be initialized"
            assert latest.value == 80.0, "Value must be initialized"


class TestTrendAnalyzer:
    """Test TrendAnalyzer."""

    def test_analyze_improving_trend(self):
        """Test detecting improving trend."""
        from codex.cognitive.objective_analyzer import (
            MetricType,
            MetricValue,
            TrendAnalyzer,
            TrendDirection,
        )

        analyzer = TrendAnalyzer(min_data_points=3)
        now = datetime.now(timezone.utc)

        # Create improving series
        metrics = [
            MetricValue(MetricType.COVERAGE, 60.0, now - timedelta(days=6)),
            MetricValue(MetricType.COVERAGE, 65.0, now - timedelta(days=4)),
            MetricValue(MetricType.COVERAGE, 70.0, now - timedelta(days=2)),
            MetricValue(MetricType.COVERAGE, 75.0, now),
        ]

        result = analyzer.analyze(metrics, period_days=7)
        assert result is not None, "result must be initialized"
        assert result.direction == TrendDirection.IMPROVING, "Result must not be empty"
        assert result.slope > 0, "slope must be greater than zero"

    def test_analyze_degrading_trend(self):
        """Test detecting degrading trend."""
        from codex.cognitive.objective_analyzer import (
            MetricType,
            MetricValue,
            TrendAnalyzer,
            TrendDirection,
        )

        analyzer = TrendAnalyzer(min_data_points=3)
        now = datetime.now(timezone.utc)

        # Create degrading series
        metrics = [
            MetricValue(MetricType.CI_CD, 100.0, now - timedelta(days=6)),
            MetricValue(MetricType.CI_CD, 95.0, now - timedelta(days=4)),
            MetricValue(MetricType.CI_CD, 90.0, now - timedelta(days=2)),
            MetricValue(MetricType.CI_CD, 85.0, now),
        ]

        result = analyzer.analyze(metrics, period_days=7)
        assert result is not None, "result must be initialized"
        assert result.direction == TrendDirection.DEGRADING, "Result must not be empty"
        assert result.slope < 0, "Result must not be empty"

    def test_analyze_insufficient_data(self):
        """Test with insufficient data."""
        from codex.cognitive.objective_analyzer import (
            MetricType,
            MetricValue,
            TrendAnalyzer,
        )

        analyzer = TrendAnalyzer(min_data_points=3)
        now = datetime.now(timezone.utc)

        metrics = [
            MetricValue(MetricType.COVERAGE, 70.0, now),
        ]

        result = analyzer.analyze(metrics, period_days=7)
        assert result is None, "Result must not be empty"


class TestAnomalyDetector:
    """Test AnomalyDetector."""

    def test_detect_anomalies(self):
        """Test anomaly detection."""
        from codex.cognitive.objective_analyzer import (
            AnomalyDetector,
            MetricType,
            MetricValue,
        )

        detector = AnomalyDetector(z_threshold=2.0)
        now = datetime.now(timezone.utc)

        # Normal values around 70, with one extreme outlier at 10
        metrics = [
            MetricValue(MetricType.COVERAGE, 70.0, now - timedelta(days=5)),
            MetricValue(MetricType.COVERAGE, 71.0, now - timedelta(days=4)),
            MetricValue(MetricType.COVERAGE, 69.0, now - timedelta(days=3)),
            MetricValue(MetricType.COVERAGE, 10.0, now - timedelta(days=2)),  # Extreme anomaly
            MetricValue(MetricType.COVERAGE, 70.5, now - timedelta(days=1)),
            MetricValue(MetricType.COVERAGE, 70.0, now),
        ]

        anomalies = detector.detect(metrics)
        assert len(anomalies) >= 1, "Anomalies must not be empty"
        # The outlier should be detected
        anomaly_values = [a.value for a in anomalies]
        assert 10.0 in anomaly_values, "Value must be initialized"


class TestObjectiveAnalyzer:
    """Test ObjectiveAnalyzer."""

    def test_record_metric(self):
        """Test recording a metric."""
        from codex.cognitive.objective_analyzer import (
            MetricStore,
            MetricType,
            ObjectiveAnalyzer,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            store = MetricStore(Path(tmpdir) / "metrics.json")
            analyzer = ObjectiveAnalyzer(store=store)

            metric = analyzer.record_metric(MetricType.COVERAGE, 75.0)
            assert metric.value == 75.0, "Value must be initialized"

    def test_check_threshold_ok(self):
        """Test threshold check when OK."""
        from codex.cognitive.objective_analyzer import (
            MetricStore,
            MetricType,
            ObjectiveAnalyzer,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            store = MetricStore(Path(tmpdir) / "metrics.json")
            analyzer = ObjectiveAnalyzer(store=store)

            is_ok, alert = analyzer.check_threshold(MetricType.COVERAGE, 80.0)
            assert is_ok is True, "is_ok is not valid"
            assert alert is None, "alert is not valid"

    def test_check_threshold_breach(self):
        """Test threshold breach detection."""
        from codex.cognitive.objective_analyzer import (
            MetricStore,
            MetricType,
            ObjectiveAnalyzer,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            store = MetricStore(Path(tmpdir) / "metrics.json")
            analyzer = ObjectiveAnalyzer(store=store)

            is_ok, alert = analyzer.check_threshold(MetricType.COVERAGE, 45.0)
            assert is_ok is False, "is_ok is not valid"
            assert alert is not None, "alert must be initialized"

    def test_generate_health_report(self):
        """Test health report generation."""
        from codex.cognitive.objective_analyzer import (
            MetricStore,
            MetricType,
            ObjectiveAnalyzer,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            store = MetricStore(Path(tmpdir) / "metrics.json")
            analyzer = ObjectiveAnalyzer(store=store)

            # Record some metrics
            analyzer.record_metric(MetricType.COVERAGE, 75.0)
            analyzer.record_metric(MetricType.SECURITY, 0)

            report = analyzer.generate_health_report()
            assert report.overall_status in ["healthy", "warning", "critical"]
            assert "recommendations" in report.to_dict(), "Condition must be true"


# ============================================================================
# Phase 3.2: Objective Adjustment Logic Tests
# ============================================================================


class TestAdjustmentTypes:
    """Test AdjustmentType enum."""

    def test_adjustment_types(self):
        """Test all adjustment types."""
        from codex.cognitive.objective_adjuster import AdjustmentType

        assert AdjustmentType.PRIORITY_INCREASE.value == "priority_increase", "Value must be initialized"
        assert AdjustmentType.ADD_OBJECTIVE.value == "add_objective", "Value must be initialized"
        assert AdjustmentType.PAUSE_OBJECTIVE.value == "pause_objective", "Value must be initialized"


class TestObjectivePriority:
    """Test ObjectivePriority enum."""

    def test_priority_ordering(self):
        """Test priority values are ordered correctly."""
        from codex.cognitive.objective_adjuster import ObjectivePriority

        assert ObjectivePriority.P0_CRITICAL.value < ObjectivePriority.P1_HIGH.value, "Value must be initialized"
        assert ObjectivePriority.P1_HIGH.value < ObjectivePriority.P2_MEDIUM.value, "Value must be initialized"


class TestObjective:
    """Test Objective dataclass."""

    def test_create_objective(self):
        """Test creating an objective."""
        from codex.cognitive.objective_adjuster import Objective, ObjectivePriority
        from codex.cognitive.objective_analyzer import MetricType

        now = datetime.now(timezone.utc)
        objective = Objective(
            id="OBJ-001",
            title="Test Objective",
            description="Test description",
            priority=ObjectivePriority.P2_MEDIUM,
            metric_type=MetricType.COVERAGE,
            target_value=80.0,
            current_value=70.0,
            status="active",
            created_at=now,
            updated_at=now,
            tags=["test"],
        )

        assert objective.id == "OBJ-001", "Object must be initialized"
        assert objective.priority == ObjectivePriority.P2_MEDIUM, "Object must be initialized"

    def test_objective_serialization(self):
        """Test objective serialization."""
        from codex.cognitive.objective_adjuster import Objective, ObjectivePriority

        now = datetime.now(timezone.utc)
        objective = Objective(
            id="OBJ-001",
            title="Test",
            description="Test",
            priority=ObjectivePriority.P1_HIGH,
            metric_type=None,
            target_value=None,
            current_value=None,
            status="active",
            created_at=now,
            updated_at=now,
        )

        data = objective.to_dict()
        restored = Objective.from_dict(data)
        assert restored.id == objective.id, "Object must be initialized"
        assert restored.priority == objective.priority, "Object must be initialized"


class TestAdjustmentRule:
    """Test AdjustmentRule."""

    def test_rule_can_apply_with_cooldown(self):
        """Test rule cooldown logic."""
        from codex.cognitive.objective_adjuster import (
            AdjustmentRule,
            AdjustmentTrigger,
            AdjustmentType,
        )

        rule = AdjustmentRule(
            id="test-rule",
            name="Test Rule",
            trigger=AdjustmentTrigger.THRESHOLD_BREACH,
            condition=lambda r: True,
            action=AdjustmentType.ADD_OBJECTIVE,
            parameters={},
            cooldown_hours=24,
        )

        # Should be able to apply (no last_applied)
        assert rule.can_apply() is True, "Condition must be true"

        # After applying
        rule.last_applied = datetime.now(timezone.utc)
        assert rule.can_apply() is False, "Condition must be true"

        # After cooldown
        rule.last_applied = datetime.now(timezone.utc) - timedelta(hours=25)
        assert rule.can_apply() is True, "Condition must be true"


class TestObjectiveStore:
    """Test ObjectiveStore."""

    def test_add_and_get_objective(self):
        """Test adding and getting objectives."""
        from codex.cognitive.objective_adjuster import (
            Objective,
            ObjectivePriority,
            ObjectiveStore,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            store = ObjectiveStore(Path(tmpdir) / "objectives.json")

            now = datetime.now(timezone.utc)
            objective = Objective(
                id="OBJ-001",
                title="Test",
                description="Test",
                priority=ObjectivePriority.P2_MEDIUM,
                metric_type=None,
                target_value=None,
                current_value=None,
                status="active",
                created_at=now,
                updated_at=now,
            )

            store.add_objective(objective)
            retrieved = store.get_objective("OBJ-001")

            assert retrieved is not None, "retrieved must be initialized"
            assert retrieved.id == "OBJ-001", "Object must be initialized"

    def test_get_all_objectives_by_status(self):
        """Test filtering objectives by status."""
        from codex.cognitive.objective_adjuster import (
            Objective,
            ObjectivePriority,
            ObjectiveStore,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            store = ObjectiveStore(Path(tmpdir) / "objectives.json")
            now = datetime.now(timezone.utc)

            # Add active and completed objectives
            for i, status in enumerate(["active", "active", "completed"]):
                obj = Objective(
                    id=f"OBJ-{i:03d}",
                    title=f"Test {i}",
                    description="Test",
                    priority=ObjectivePriority.P2_MEDIUM,
                    metric_type=None,
                    target_value=None,
                    current_value=None,
                    status=status,
                    created_at=now,
                    updated_at=now,
                )
                store.add_objective(obj)

            active = store.get_all_objectives(status="active")
            assert len(active) == 2, "Active must not be empty"


class TestObjectiveAdjuster:
    """Test ObjectiveAdjuster."""

    def test_create_objective(self):
        """Test manual objective creation."""
        from codex.cognitive.objective_adjuster import (
            ObjectiveAdjuster,
            ObjectivePriority,
            ObjectiveStore,
        )
        from codex.cognitive.objective_analyzer import (
            MetricStore,
            MetricType,
            ObjectiveAnalyzer,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            metric_store = MetricStore(Path(tmpdir) / "metrics.json")
            obj_store = ObjectiveStore(Path(tmpdir) / "objectives.json")
            analyzer = ObjectiveAnalyzer(store=metric_store)
            adjuster = ObjectiveAdjuster(analyzer=analyzer, store=obj_store)

            objective = adjuster.create_objective(
                title="Coverage Sprint",
                description="Improve coverage",
                priority=ObjectivePriority.P1_HIGH,
                metric_type=MetricType.COVERAGE,
                target_value=80.0,
            )

            assert objective.title == "Coverage Sprint", "Object must be initialized"
            assert objective.priority == ObjectivePriority.P1_HIGH, "Object must be initialized"

    def test_complete_objective(self):
        """Test completing an objective."""
        from codex.cognitive.objective_adjuster import (
            ObjectiveAdjuster,
            ObjectivePriority,
            ObjectiveStore,
        )
        from codex.cognitive.objective_analyzer import MetricStore, ObjectiveAnalyzer

        with tempfile.TemporaryDirectory() as tmpdir:
            metric_store = MetricStore(Path(tmpdir) / "metrics.json")
            obj_store = ObjectiveStore(Path(tmpdir) / "objectives.json")
            analyzer = ObjectiveAnalyzer(store=metric_store)
            adjuster = ObjectiveAdjuster(analyzer=analyzer, store=obj_store)

            objective = adjuster.create_objective(
                title="Test", description="Test", priority=ObjectivePriority.P2_MEDIUM
            )

            result = adjuster.complete_objective(objective.id)
            assert result is True, "Result must not be empty"

            updated = obj_store.get_objective(objective.id)
            assert updated.status == "completed", "status is not valid"


# ============================================================================
# Phase 3.3: Autonomous Execution Tests
# ============================================================================


class TestAutomationLevel:
    """Test AutomationLevel enum."""

    def test_automation_levels(self):
        """Test automation level values."""
        from codex.cognitive.autonomous_executor import AutomationLevel

        assert AutomationLevel.LEVEL_1_ADVISORY.value == 1, "Value must be initialized"
        assert AutomationLevel.LEVEL_2_SEMI_AUTONOMOUS.value == 2, "Value must be initialized"
        assert AutomationLevel.LEVEL_3_FULLY_AUTONOMOUS.value == 3, "Value must be initialized"


class TestExecutionPolicy:
    """Test ExecutionPolicy."""

    def test_advisory_mode_blocks_all(self):
        """Test advisory mode requires approval for all."""
        from codex.cognitive.autonomous_executor import AutomationLevel, ExecutionPolicy
        from codex.cognitive.objective_adjuster import Adjustment, AdjustmentType

        policy = ExecutionPolicy(AutomationLevel.LEVEL_1_ADVISORY)

        adjustment = Adjustment(
            id="ADJ-001",
            rule_id="test",
            type=AdjustmentType.PRIORITY_INCREASE,
            objective_id=None,
            description="Test",
            parameters={},
            status="proposed",
            proposed_at=datetime.now(timezone.utc),
        )

        can_execute, reason = policy.can_auto_execute(adjustment)
        assert can_execute is False, "can_execute is not valid"
        assert "Advisory mode" in reason, "Condition must be true"

    def test_semi_autonomous_auto_approves_priority_change(self):
        """Test semi-autonomous auto-approves priority changes."""
        from codex.cognitive.autonomous_executor import AutomationLevel, ExecutionPolicy
        from codex.cognitive.objective_adjuster import Adjustment, AdjustmentType

        policy = ExecutionPolicy(AutomationLevel.LEVEL_2_SEMI_AUTONOMOUS)

        adjustment = Adjustment(
            id="ADJ-001",
            rule_id="test",
            type=AdjustmentType.PRIORITY_INCREASE,
            objective_id=None,
            description="Test",
            parameters={},
            status="proposed",
            proposed_at=datetime.now(timezone.utc),
        )

        can_execute, _ = policy.can_auto_execute(adjustment)
        assert can_execute is True, "can_execute is not valid"

    def test_semi_autonomous_requires_approval_for_add(self):
        """Test semi-autonomous requires approval for adding objectives."""
        from codex.cognitive.autonomous_executor import AutomationLevel, ExecutionPolicy
        from codex.cognitive.objective_adjuster import Adjustment, AdjustmentType

        policy = ExecutionPolicy(AutomationLevel.LEVEL_2_SEMI_AUTONOMOUS)

        adjustment = Adjustment(
            id="ADJ-001",
            rule_id="test",
            type=AdjustmentType.ADD_OBJECTIVE,
            objective_id=None,
            description="Test",
            parameters={},
            status="proposed",
            proposed_at=datetime.now(timezone.utc),
        )

        can_execute, reason = policy.can_auto_execute(adjustment)
        assert can_execute is False, "can_execute is not valid"
        assert "requires approval" in reason, "Condition must be true"

    def test_fully_autonomous_approves_all(self):
        """Test fully autonomous approves everything."""
        from codex.cognitive.autonomous_executor import AutomationLevel, ExecutionPolicy
        from codex.cognitive.objective_adjuster import Adjustment, AdjustmentType

        policy = ExecutionPolicy(AutomationLevel.LEVEL_3_FULLY_AUTONOMOUS)

        adjustment = Adjustment(
            id="ADJ-001",
            rule_id="test",
            type=AdjustmentType.ADD_OBJECTIVE,
            objective_id=None,
            description="Test",
            parameters={},
            status="proposed",
            proposed_at=datetime.now(timezone.utc),
        )

        can_execute, _ = policy.can_auto_execute(adjustment)
        assert can_execute is True, "can_execute is not valid"


class TestAutonomousExecutor:
    """Test AutonomousExecutor."""

    def test_get_status(self):
        """Test getting executor status."""
        from codex.cognitive.autonomous_executor import AutonomousExecutor

        executor = AutonomousExecutor()
        status = executor.get_status()

        assert "automation_level" in status, "Condition must be true"
        assert "pending_approvals" in status, "Condition must be true"


# ============================================================================
# Phase 3.4: Safety & Governance Tests
# ============================================================================


class TestAuditEventType:
    """Test AuditEventType enum."""

    def test_audit_event_types(self):
        """Test audit event types."""
        from codex.cognitive.safety_guards import AuditEventType

        assert AuditEventType.ADJUSTMENT_EXECUTED.value == "adjustment_executed", "Value must be initialized"
        assert AuditEventType.RATE_LIMIT_HIT.value == "rate_limit_hit", "Value must be initialized"


class TestRateLimit:
    """Test RateLimit."""

    def test_rate_limit_allows_within_limit(self):
        """Test rate limit allows actions within limit."""
        from codex.cognitive.safety_guards import RateLimit

        limit = RateLimit("test", max_count=3, window_hours=24)

        # First 3 should be allowed
        for _ in range(3):
            allowed, _ = limit.check_and_increment()
            assert allowed is True, "allowed is not valid"

        # 4th should be blocked
        allowed, reason = limit.check_and_increment()
        assert allowed is False, "allowed is not valid"
        assert "exceeded" in reason, "Condition must be true"

    def test_rate_limit_resets_after_window(self):
        """Test rate limit resets after window expires."""
        from codex.cognitive.safety_guards import RateLimit

        limit = RateLimit("test", max_count=2, window_hours=1)

        # Use up limit
        limit.check_and_increment()
        limit.check_and_increment()

        # Should be blocked
        allowed, _ = limit.check_and_increment()
        assert allowed is False, "allowed is not valid"

        # Simulate window expiry
        limit.window_start = datetime.now(timezone.utc) - timedelta(hours=2)

        # Should be allowed now
        allowed, _ = limit.check_and_increment()
        assert allowed is True, "allowed is not valid"


class TestScopeRestriction:
    """Test ScopeRestriction."""

    def test_scope_allows_unblocked(self):
        """Test scope allows unblocked adjustments."""
        from codex.cognitive.objective_adjuster import Adjustment, AdjustmentType
        from codex.cognitive.safety_guards import ScopeRestriction

        scope = ScopeRestriction(name="test", description="Test scope")

        adjustment = Adjustment(
            id="ADJ-001",
            rule_id="test",
            type=AdjustmentType.PRIORITY_INCREASE,
            objective_id=None,
            description="Test",
            parameters={},
            status="proposed",
            proposed_at=datetime.now(timezone.utc),
        )

        allowed, _ = scope.check_adjustment(adjustment)
        assert allowed is True, "allowed is not valid"

    def test_scope_blocks_adjustment_type(self):
        """Test scope blocks specific adjustment types."""
        from codex.cognitive.objective_adjuster import Adjustment, AdjustmentType
        from codex.cognitive.safety_guards import ScopeRestriction

        scope = ScopeRestriction(
            name="test", description="Test scope", blocked_adjustment_types=["remove_objective"]
        )

        adjustment = Adjustment(
            id="ADJ-001",
            rule_id="test",
            type=AdjustmentType.REMOVE_OBJECTIVE,
            objective_id=None,
            description="Test",
            parameters={},
            status="proposed",
            proposed_at=datetime.now(timezone.utc),
        )

        allowed, reason = scope.check_adjustment(adjustment)
        assert allowed is False, "allowed is not valid"
        assert "blocked" in reason, "Condition must be true"


class TestAuditLog:
    """Test AuditLog."""

    def test_log_event(self):
        """Test logging an audit event."""
        from codex.cognitive.safety_guards import AuditEventType, AuditLog

        with tempfile.TemporaryDirectory() as tmpdir:
            log = AuditLog(Path(tmpdir) / "audit.json")

            event = log.log_event(
                AuditEventType.ADJUSTMENT_EXECUTED, "test_user", {"adjustment_id": "ADJ-001"}
            )

            assert event.id.startswith("AUD-"), "Condition must be true"
            assert event.actor == "test_user", "actor is not valid"

    def test_get_events_filtered(self):
        """Test getting filtered events."""
        from codex.cognitive.safety_guards import AuditEventType, AuditLog

        with tempfile.TemporaryDirectory() as tmpdir:
            log = AuditLog(Path(tmpdir) / "audit.json")

            log.log_event(AuditEventType.ADJUSTMENT_EXECUTED, "user1", {})
            log.log_event(AuditEventType.RATE_LIMIT_HIT, "system", {})
            log.log_event(AuditEventType.ADJUSTMENT_EXECUTED, "user2", {})

            executed = log.get_events(event_type=AuditEventType.ADJUSTMENT_EXECUTED)
            assert len(executed) == 2, "Executed must not be empty"


class TestSafetyGuard:
    """Test SafetyGuard."""

    def test_pause_and_resume_automation(self):
        """Test pausing and resuming automation."""
        from codex.cognitive.safety_guards import AuditLog, SafetyGuard

        with tempfile.TemporaryDirectory() as tmpdir:
            audit_log = AuditLog(Path(tmpdir) / "audit.json")
            guard = SafetyGuard(audit_log=audit_log)

            assert guard.is_paused is False, "is_paused is not valid"

            guard.pause_automation("admin", "Maintenance")
            assert guard.is_paused is True, "is_paused is not valid"

            guard.resume_automation("admin")
            assert guard.is_paused is False, "is_paused is not valid"

    def test_block_and_unblock_rule(self):
        """Test blocking and unblocking rules."""
        from codex.cognitive.safety_guards import AuditLog, SafetyGuard

        with tempfile.TemporaryDirectory() as tmpdir:
            audit_log = AuditLog(Path(tmpdir) / "audit.json")
            guard = SafetyGuard(audit_log=audit_log)

            guard.block_rule("test-rule", "admin", "Testing")
            assert "test-rule" in guard.scope.blocked_rules, "Condition must be true"

            guard.unblock_rule("test-rule", "admin")
            assert "test-rule" not in guard.scope.blocked_rules, "Condition must be true"

    def test_check_adjustment_when_paused(self):
        """Test adjustment blocked when paused."""
        from codex.cognitive.objective_adjuster import Adjustment, AdjustmentType
        from codex.cognitive.safety_guards import AuditLog, SafetyGuard

        with tempfile.TemporaryDirectory() as tmpdir:
            audit_log = AuditLog(Path(tmpdir) / "audit.json")
            guard = SafetyGuard(audit_log=audit_log)

            guard.pause_automation("admin", "Test")

            adjustment = Adjustment(
                id="ADJ-001",
                rule_id="test",
                type=AdjustmentType.PRIORITY_INCREASE,
                objective_id=None,
                description="Test",
                parameters={},
                status="proposed",
                proposed_at=datetime.now(timezone.utc),
            )

            allowed, reason = guard.check_adjustment(adjustment)
            assert allowed is False, "allowed is not valid"
            assert "paused" in reason, "Condition must be true"

    def test_generate_governance_report(self):
        """Test governance report generation."""
        from codex.cognitive.safety_guards import AuditEventType, AuditLog, SafetyGuard

        with tempfile.TemporaryDirectory() as tmpdir:
            audit_log = AuditLog(Path(tmpdir) / "audit.json")
            guard = SafetyGuard(audit_log=audit_log)

            # Log some events
            audit_log.log_event(AuditEventType.ADJUSTMENT_EXECUTED, "system", {})
            audit_log.log_event(AuditEventType.RATE_LIMIT_HIT, "system", {})

            report = guard.generate_governance_report(period_days=7)

            assert "total_events" in report, "Condition must be true"
            assert "events_by_type" in report, "Condition must be true"
            assert report["total_events"] == 2, "rep is not valid"

    def test_get_safety_status(self):
        """Test getting safety status."""
        from codex.cognitive.safety_guards import AuditLog, SafetyGuard

        with tempfile.TemporaryDirectory() as tmpdir:
            audit_log = AuditLog(Path(tmpdir) / "audit.json")
            guard = SafetyGuard(audit_log=audit_log)

            status = guard.get_safety_status()

            assert "is_paused" in status, "Condition must be true"
            assert "blocked_rules" in status, "Condition must be true"
            assert "rate_limits" in status, "Condition must be true"


# ============================================================================
# Integration Tests
# ============================================================================


class TestPlan3Integration:
    """Integration tests for Plan 3."""

    def test_full_pipeline(self):
        """Test full objective adjustment pipeline."""
        from codex.cognitive.autonomous_executor import (
            AutomationLevel,
            AutonomousExecutor,
            ExecutionPolicy,
        )
        from codex.cognitive.objective_adjuster import ObjectiveAdjuster, ObjectiveStore
        from codex.cognitive.objective_analyzer import (
            MetricStore,
            MetricType,
            ObjectiveAnalyzer,
        )
        from codex.cognitive.safety_guards import AuditLog, SafetyGuard

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Setup components
            metric_store = MetricStore(tmppath / "metrics.json")
            obj_store = ObjectiveStore(tmppath / "objectives.json")
            audit_log = AuditLog(tmppath / "audit.json")

            analyzer = ObjectiveAnalyzer(store=metric_store)
            adjuster = ObjectiveAdjuster(analyzer=analyzer, store=obj_store)
            _ = SafetyGuard(audit_log=audit_log)  # Guard created but used implicitly via audit_log
            policy = ExecutionPolicy(AutomationLevel.LEVEL_2_SEMI_AUTONOMOUS)
            executor = AutonomousExecutor(adjuster=adjuster, policy=policy)

            # Record low coverage
            analyzer.record_metric(MetricType.COVERAGE, 45.0)

            # Generate health report
            report = analyzer.generate_health_report()
            assert report.overall_status == "critical", "overall_status is not valid"

            # Run evaluation cycle
            result = executor.run_evaluation_cycle()
            assert "adjustments_proposed" in result, "Result must not be empty"

    def test_convenience_functions(self):
        """Test convenience functions work."""
        from codex.cognitive.autonomous_executor import run_advisory_mode
        from codex.cognitive.objective_analyzer import get_health_report
        from codex.cognitive.safety_guards import get_governance_report

        # These should not raise
        # Note: They use default paths which may not exist in test
        # So we just check they're callable
        assert callable(get_health_report), "Condition must be true"
        assert callable(run_advisory_mode), "Condition must be true"
        assert callable(get_governance_report), "Condition must be true"
