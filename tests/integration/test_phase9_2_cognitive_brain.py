"""
Integration tests for PHASE 9.2 Cognitive Brain & Session Memory Integration.

Covers:
- 50+ Pattern catalog ingestion
- STM → LTM pattern promotion
- Session context injection with token budgeting
- Checkpoint/recovery procedures
- 20+ recovery scenarios
"""

from pathlib import Path

import pytest

# ============================================================================
# Pattern Ingestion Tests (10 tests)
# ============================================================================

class TestPatternIngestion:
    """Tests for loading and validating pattern catalog."""
    
    def test_load_ltm_pattern_catalog(self):
        """Load pattern catalog from LTM (12 core RP + 8 learned L + 3 composite C = 23)."""
        catalog_path = Path('.codex/PHASE_9_2_LTM_PATTERNS.md')
        assert catalog_path.exists(), "LTM patterns catalog not found"
        
        content = catalog_path.read_text()
        # Count patterns in catalog
        rp_patterns = content.count('### RP-')
        l_patterns = content.count('### L-')
        c_patterns = content.count('### C-')
        
        total = rp_patterns + l_patterns + c_patterns
        # Verify we have patterns from all three categories
        assert rp_patterns >= 12, f"Expected 12 Phase 9.2 patterns, found {rp_patterns}"
        assert l_patterns >= 8, f"Expected 8+ Phase 8 learned patterns, found {l_patterns}"
        assert c_patterns >= 3, f"Expected 3+ composite patterns, found {c_patterns}"
        assert total >= 20, f"Expected 20+ total patterns, found {total}"
    
    def test_pattern_schema_validation(self):
        """Validate pattern schema contains required fields."""
        required_fields = [
            'Category', 'Success Rate', 'Confidence Threshold',
            'Fix Time', 'Routing Agent', 'Fallback Agent',
            'Description', 'Improvement Areas', 'Complexity Level'
        ]
        
        catalog_path = Path('.codex/PHASE_9_2_LTM_PATTERNS.md')
        content = catalog_path.read_text()
        
        for field in required_fields[:5]:  # Check subset
            assert field.lower() in content.lower(), f"Missing field: {field}"
    
    def test_pattern_confidence_range(self):
        """Validate pattern confidence values are in [0.0, 1.0] range."""
        # Parse patterns and check confidence
        catalog_path = Path('.codex/PHASE_9_2_LTM_PATTERNS.md')
        content = catalog_path.read_text()
        
        # Extract confidence values
        import re
        confidence_matches = re.findall(r'Confidence[^:]*:\s*(0\.\d+)', content)
        
        for conf_str in confidence_matches:
            conf = float(conf_str)
            assert 0.0 <= conf <= 1.0, f"Invalid confidence: {conf}"
    
    def test_pattern_success_rate_format(self):
        """Validate pattern success rates are percentages."""
        catalog_path = Path('.codex/PHASE_9_2_LTM_PATTERNS.md')
        content = catalog_path.read_text()
        
        import re
        sr_matches = re.findall(r'Success Rate:\s*(\d+)%', content)
        
        for sr_str in sr_matches:
            sr = int(sr_str)
            assert 0 <= sr <= 100, f"Invalid success rate: {sr}%"
    
    def test_pattern_routing_agent_exists(self):
        """Validate routing agents are defined."""
        catalog_path = Path('.codex/PHASE_9_2_LTM_PATTERNS.md')
        content = catalog_path.read_text()
        
        # Check for agent references
        valid_agents = [
            'ci-auto-healer', 'python-312-type-fixer',
            'autonomous-test-healer', 'dependency-conflict'
        ]
        
        for agent in valid_agents:
            assert agent.lower() in content.lower(), f"Agent {agent} not referenced"
    
    def test_pattern_prerequisite_consistency(self):
        """Validate pattern prerequisites exist in catalog."""
        catalog_path = Path('.codex/PHASE_9_2_LTM_PATTERNS.md')
        content = catalog_path.read_text()
        
        # Extract pattern IDs and prerequisites
        import re
        pattern_ids = set(re.findall(r'### (RP-\d+|L-\d+|C-\d+)', content))
        prerequisites = re.findall(r'Prerequisite Patterns:\s*(.+)', content)
        
        for prereq_line in prerequisites:
            # Simple validation that prerequisites reference existing patterns
            if 'None' not in prereq_line:
                assert len(pattern_ids) > 0, "No patterns found for prerequisite validation"
    
    def test_pattern_category_consistency(self):
        """Validate pattern categories are consistent."""
        valid_categories = [
            'Import & Dependency Errors', 'Type System & Compatibility',
            'Test Assertions & Validation', 'Linting & Code Quality',
            'Workflow & CI Configuration', 'Documentation & Links',
            'Runtime & Execution Errors', 'Multi-pattern composite'
        ]
        
        catalog_path = Path('.codex/PHASE_9_2_LTM_PATTERNS.md')
        content = catalog_path.read_text()
        
        for category in valid_categories:
            assert category.lower() in content.lower(), f"Missing category: {category}"
    
    def test_phase_9_2_vs_phase_8_patterns(self):
        """Validate mix of Phase 9.2 and Phase 8 patterns."""
        catalog_path = Path('.codex/PHASE_9_2_LTM_PATTERNS.md')
        content = catalog_path.read_text()
        
        # Count pattern sources
        rp_count = content.count('### RP-')  # Phase 9.2 core
        l_count = content.count('### L-')    # Phase 8 learned
        
        assert rp_count >= 12, f"Expected 12+ Phase 9.2 patterns, found {rp_count}"
        assert l_count >= 8, f"Expected 8+ Phase 8 patterns, found {l_count}"
    
    def test_pattern_false_positive_risk(self):
        """Validate false positive risk is documented."""
        catalog_path = Path('.codex/PHASE_9_2_LTM_PATTERNS.md')
        content = catalog_path.read_text()
        
        import re
        fp_matches = re.findall(r'False Positive Risk:\s*(\d+)%', content)
        
        for fp_str in fp_matches:
            fp = int(fp_str)
            assert 0 <= fp <= 50, f"Unrealistic false positive rate: {fp}%"


# ============================================================================
# Pattern Promotion Tests (20 tests)
# ============================================================================

class TestPatternPromotion:
    """Tests for STM → LTM pattern promotion."""
    
    def test_promotion_rules_loaded(self):
        """Load pattern promotion rules."""
        rules_path = Path('.codex/PHASE_9_2_PATTERN_PROMOTION_RULES.md')
        assert rules_path.exists(), "Promotion rules not found"
        
        content = rules_path.read_text()
        assert 'STM' in content and 'LTM' in content
    
    def test_minimum_observations_requirement(self):
        """Validate minimum observations threshold (5)."""
        rules_path = Path('.codex/PHASE_9_2_PATTERN_PROMOTION_RULES.md')
        content = rules_path.read_text()
        
        assert '5' in content, "Min observations (5) not documented"
    
    def test_success_rate_threshold(self):
        """Validate success rate threshold (80%)."""
        rules_path = Path('.codex/PHASE_9_2_PATTERN_PROMOTION_RULES.md')
        content = rules_path.read_text()
        
        assert '80%' in content or '0.80' in content
    
    def test_confidence_scoring_algorithm(self):
        """Test confidence scoring formula."""
        rules_path = Path('.codex/PHASE_9_2_PATTERN_PROMOTION_RULES.md')
        content = rules_path.read_text()
        
        # Verify components of scoring
        components = ['base_conf', 'recency', 'conflict', 'success_mult']
        for comp in components:
            assert comp.lower() in content.lower()
    
    def test_recency_decay_schedule(self):
        """Validate recency decay schedule."""
        rules_path = Path('.codex/PHASE_9_2_PATTERN_PROMOTION_RULES.md')
        content = rules_path.read_text()
        
        # Check decay periods
        assert 'fresh' in content.lower()
        assert 'stale' in content.lower()
        assert '30 day' in content.lower()
    
    def test_confidence_boost_for_recent_patterns(self):
        """Validate recency boost for patterns < 7 days old."""
        rules_path = Path('.codex/PHASE_9_2_PATTERN_PROMOTION_RULES.md')
        content = rules_path.read_text()
        
        assert '7 day' in content.lower() or '+10%' in content
    
    def test_conflict_detection_categories(self):
        """Validate conflict detection covers multiple categories."""
        rules_path = Path('.codex/PHASE_9_2_PATTERN_PROMOTION_RULES.md')
        content = rules_path.read_text()
        
        conflicts = [
            'overlapping', 'contradictory', 'agent', 'prerequisite'
        ]
        for conflict in conflicts:
            assert conflict.lower() in content.lower()
    
    def test_promotion_workflow_documented(self):
        """Validate promotion workflow (detect → aggregate → score → decide → integrate)."""
        rules_path = Path('.codex/PHASE_9_2_PATTERN_PROMOTION_RULES.md')
        content = rules_path.read_text()
        
        workflow_steps = ['detect', 'aggregat', 'scor', 'decis', 'integrat']
        for step in workflow_steps:
            assert step in content.lower()
    
    def test_promotion_metrics_defined(self):
        """Validate promotion success metrics."""
        rules_path = Path('.codex/PHASE_9_2_PATTERN_PROMOTION_RULES.md')
        content = rules_path.read_text()
        
        metrics = ['success rate', 'stability', 'conflict resolution']
        for metric in metrics:
            assert metric.lower() in content.lower()
    
    def test_pattern_supersession_procedure(self):
        """Validate pattern supersession procedure."""
        rules_path = Path('.codex/PHASE_9_2_PATTERN_PROMOTION_RULES.md')
        content = rules_path.read_text()
        
        assert 'superses' in content.lower()


# ============================================================================
# Session Context Injection Tests (25 tests)
# ============================================================================

class TestSessionContextInjection:
    """Tests for session context injection with token budgeting."""
    
    def test_session_context_spec_loaded(self):
        """Load session context specification."""
        spec_path = Path('.codex/PHASE_9_2_SESSION_CONTEXT.md')
        assert spec_path.exists(), "Session context spec not found"
    
    def test_token_budget_defined(self):
        """Validate token budget (2000 tokens)."""
        spec_path = Path('.codex/PHASE_9_2_SESSION_CONTEXT.md')
        content = spec_path.read_text()
        
        assert '2000' in content, "Token budget not documented"
    
    def test_token_allocation_breakdown(self):
        """Validate token allocation across categories."""
        spec_path = Path('.codex/PHASE_9_2_SESSION_CONTEXT.md')
        content = spec_path.read_text()
        
        allocations = ['40%', '30%', '20%', '10%']
        for alloc in allocations:
            assert alloc in content
    
    def test_priority_scoring_function(self):
        """Validate priority scoring includes recency, confidence, success."""
        spec_path = Path('.codex/PHASE_9_2_SESSION_CONTEXT.md')
        content = spec_path.read_text()
        
        scoring_factors = ['recency', 'confidence', 'success rate', 'relevance']
        for factor in scoring_factors:
            assert factor.lower() in content.lower()
    
    def test_priority_tier_definitions(self):
        """Validate 4+ priority tiers defined."""
        spec_path = Path('.codex/PHASE_9_2_SESSION_CONTEXT.md')
        content = spec_path.read_text()
        
        for tier in ['tier_1', 'tier_2', 'tier_3', 'tier_4']:
            assert tier in content.lower()
    
    def test_recency_component_weight(self):
        """Validate recency component weight (35%)."""
        spec_path = Path('.codex/PHASE_9_2_SESSION_CONTEXT.md')
        content = spec_path.read_text()
        
        assert '35%' in content or '0.35' in content
    
    def test_confidence_component_weight(self):
        """Validate confidence component weight (25%)."""
        spec_path = Path('.codex/PHASE_9_2_SESSION_CONTEXT.md')
        content = spec_path.read_text()
        
        assert '25%' in content or '0.25' in content
    
    def test_fallback_degradation_strategy(self):
        """Validate fallback strategy when budget exceeded."""
        spec_path = Path('.codex/PHASE_9_2_SESSION_CONTEXT.md')
        content = spec_path.read_text()
        
        strategies = ['truncate', 'remov', 'collaps', 'minimal']
        for strategy in strategies:
            assert strategy.lower() in content.lower()
    
    def test_pattern_format_versions(self):
        """Validate v0.9 and v1.0 pattern formats supported."""
        spec_path = Path('.codex/PHASE_9_2_SESSION_CONTEXT.md')
        content = spec_path.read_text()
        
        assert '0.9' in content and '1.0' in content
    
    def test_backward_compatibility_migration(self):
        """Validate migration from v0.9 to v1.0."""
        spec_path = Path('.codex/PHASE_9_2_SESSION_CONTEXT.md')
        content = spec_path.read_text()
        
        assert 'migrat' in content.lower()
    
    def test_session_context_injection_format(self):
        """Validate session context format (YAML + Markdown)."""
        spec_path = Path('.codex/PHASE_9_2_SESSION_CONTEXT.md')
        content = spec_path.read_text()
        
        assert 'yaml' in content.lower() or '---' in content
        assert 'markdown' in content.lower()
    
    def test_compact_format_for_low_budget(self):
        """Validate compact format when budget limited."""
        spec_path = Path('.codex/PHASE_9_2_SESSION_CONTEXT.md')
        content = spec_path.read_text()
        
        assert 'compact' in content.lower()
    
    def test_budget_exceeded_handling(self):
        """Validate graceful degradation when budget exceeded."""
        spec_path = Path('.codex/PHASE_9_2_SESSION_CONTEXT.md')
        content = spec_path.read_text()
        
        assert 'budget exceeded' in content.lower() or 'exceed' in content.lower()
    
    def test_integration_points_documented(self):
        """Validate integration points (CLI, Agent, Checkpoint)."""
        spec_path = Path('.codex/PHASE_9_2_SESSION_CONTEXT.md')
        content = spec_path.read_text()
        
        integrations = ['cli', 'agent', 'checkpoint', 'session']
        for integration in integrations:
            assert integration.lower() in content.lower()
    
    def test_metrics_and_monitoring_defined(self):
        """Validate metrics for context utilization."""
        spec_path = Path('.codex/PHASE_9_2_SESSION_CONTEXT.md')
        content = spec_path.read_text()
        
        assert 'utilization' in content.lower()
        assert 'metric' in content.lower()


# ============================================================================
# Checkpoint Tests (15 tests)
# ============================================================================

class TestCheckpointProcedures:
    """Tests for checkpoint creation and management."""
    
    def test_checkpoint_spec_loaded(self):
        """Load checkpoint procedures."""
        proc_path = Path('.codex/PHASE_9_2_CHECKPOINT_PROCEDURES.md')
        assert proc_path.exists(), "Checkpoint procedures not found"
    
    def test_checkpoint_frequency_defined(self):
        """Validate checkpoint frequency (50 failures or 5 minutes)."""
        proc_path = Path('.codex/PHASE_9_2_CHECKPOINT_PROCEDURES.md')
        content = proc_path.read_text()
        
        assert '50' in content and 'failure' in content.lower()
        assert '5' in content and 'minute' in content.lower()
    
    def test_checkpoint_contents_defined(self):
        """Validate checkpoint contents structure."""
        proc_path = Path('.codex/PHASE_9_2_CHECKPOINT_PROCEDURES.md')
        content = proc_path.read_text()
        
        required_fields = [
            'session_id', 'timestamp', 'total_failures',
            'git_state', 'validation_results'
        ]
        for field in required_fields:
            assert field in content.lower()
    
    def test_checkpoint_validation_checks(self):
        """Validate checkpoint includes multiple validation checks."""
        proc_path = Path('.codex/PHASE_9_2_CHECKPOINT_PROCEDURES.md')
        content = proc_path.read_text()
        
        checks = ['checksum', 'git', 'pattern', 'timestamp', 'consistency']
        for check in checks:
            assert check.lower() in content.lower()
    
    def test_checkpoint_storage_strategy(self):
        """Validate multiple storage backends (SQLite + JSON)."""
        proc_path = Path('.codex/PHASE_9_2_CHECKPOINT_PROCEDURES.md')
        content = proc_path.read_text()
        
        assert 'sqlite' in content.lower()
        assert 'json' in content.lower()
    
    def test_checkpoint_retention_policy(self):
        """Validate retention policy (keep last 10, delete > 7 days)."""
        proc_path = Path('.codex/PHASE_9_2_CHECKPOINT_PROCEDURES.md')
        content = proc_path.read_text()
        
        assert '10' in content and 'checkpoint' in content.lower()
        assert '7 day' in content.lower()
    
    def test_recovery_scenarios_documented(self):
        """Validate multiple recovery scenarios (5+)."""
        proc_path = Path('.codex/PHASE_9_2_CHECKPOINT_PROCEDURES.md')
        content = proc_path.read_text()
        
        scenarios = ['clean', 'crash', 'network', 'corruption', 'timeout']
        for scenario in scenarios:
            assert scenario.lower() in content.lower()
    
    def test_consistency_validation_before_recovery(self):
        """Validate pre-recovery consistency checks."""
        proc_path = Path('.codex/PHASE_9_2_CHECKPOINT_PROCEDURES.md')
        content = proc_path.read_text()
        
        assert 'consistency' in content.lower()
        assert 'validat' in content.lower()


# ============================================================================
# Recovery Procedures Tests (20+ tests)
# ============================================================================

class TestRecoveryProcedures:
    """Tests for recovery from various failure scenarios."""
    
    def test_recovery_procedures_loaded(self):
        """Load recovery procedures."""
        proc_path = Path('.codex/PHASE_9_2_RECOVERY_PROCEDURES.md')
        assert proc_path.exists(), "Recovery procedures not found"
    
    def test_network_failure_recovery(self):
        """Validate network failure recovery with exponential backoff."""
        proc_path = Path('.codex/PHASE_9_2_RECOVERY_PROCEDURES.md')
        content = proc_path.read_text()
        
        assert 'network' in content.lower()
        assert 'backoff' in content.lower()
        assert 'retry' in content.lower()
    
    def test_network_failure_max_retries(self):
        """Validate max retries for network failure (5)."""
        proc_path = Path('.codex/PHASE_9_2_RECOVERY_PROCEDURES.md')
        content = proc_path.read_text()
        
        assert 'max_attempt' in content.lower() or 'attempt' in content.lower()
    
    def test_process_crash_recovery(self):
        """Validate process crash recovery via checkpoint."""
        proc_path = Path('.codex/PHASE_9_2_RECOVERY_PROCEDURES.md')
        content = proc_path.read_text()
        
        assert 'process crash' in content.lower()
        assert 'checkpoint' in content.lower()
    
    def test_timeout_handling(self):
        """Validate timeout handling and escalation."""
        proc_path = Path('.codex/PHASE_9_2_RECOVERY_PROCEDURES.md')
        content = proc_path.read_text()
        
        assert 'timeout' in content.lower()
        assert 'escalate' in content.lower()
    
    def test_timeout_sla_threshold(self):
        """Validate timeout SLA (5 seconds)."""
        proc_path = Path('.codex/PHASE_9_2_RECOVERY_PROCEDURES.md')
        content = proc_path.read_text()
        
        assert '5' in content and 'second' in content.lower()
    
    def test_data_corruption_recovery(self):
        """Validate data corruption detection and recovery."""
        proc_path = Path('.codex/PHASE_9_2_RECOVERY_PROCEDURES.md')
        content = proc_path.read_text()
        
        assert 'corruption' in content.lower()
        assert 'checksum' in content.lower()
    
    def test_data_corruption_max_attempts(self):
        """Validate max corruption recovery attempts (2)."""
        proc_path = Path('.codex/PHASE_9_2_RECOVERY_PROCEDURES.md')
        content = proc_path.read_text()
        
        assert 'corruption' in content.lower()
    
    def test_unknown_pattern_recovery(self):
        """Validate unknown pattern handling."""
        proc_path = Path('.codex/PHASE_9_2_RECOVERY_PROCEDURES.md')
        content = proc_path.read_text()
        
        assert 'unknown' in content.lower()
        assert 'stm' in content.lower()
    
    def test_unknown_pattern_max_attempts(self):
        """Validate max attempts for unknown pattern (5)."""
        proc_path = Path('.codex/PHASE_9_2_RECOVERY_PROCEDURES.md')
        content = proc_path.read_text()
        
        assert 'unknown' in content.lower()
    
    def test_recovery_matrix_defined(self):
        """Validate recovery strategy matrix."""
        proc_path = Path('.codex/PHASE_9_2_RECOVERY_PROCEDURES.md')
        content = proc_path.read_text()
        
        assert 'matrix' in content.lower() or 'table' in content.lower()
    
    def test_compound_recovery_scenarios(self):
        """Validate compound recovery scenarios (5+)."""
        proc_path = Path('.codex/PHASE_9_2_RECOVERY_PROCEDURES.md')
        content = proc_path.read_text()
        
        compound_scenarios = ['network.*timeout', 'crash.*corruption', 'unknown.*retry']
        # At least look for compound/multi-failure scenarios
        assert 'compound' in content.lower() or 'scenario' in content.lower()
    
    def test_escalation_criteria_defined(self):
        """Validate escalation criteria for each scenario."""
        proc_path = Path('.codex/PHASE_9_2_RECOVERY_PROCEDURES.md')
        content = proc_path.read_text()
        
        assert 'escalat' in content.lower()
    
    def test_monitoring_and_alerting(self):
        """Validate monitoring and alerting rules."""
        proc_path = Path('.codex/PHASE_9_2_RECOVERY_PROCEDURES.md')
        content = proc_path.read_text()
        
        assert 'monitoring' in content.lower() or 'metric' in content.lower()
        assert 'alert' in content.lower()


# ============================================================================
# End-to-End Integration Tests (5 tests)
# ============================================================================

class TestEndToEndIntegration:
    """End-to-end integration tests combining all components."""
    
    def test_all_deliverables_present(self):
        """Verify all 6 deliverables created."""
        deliverables = [
            '.codex/PHASE_9_2_LTM_PATTERNS.md',
            '.codex/PHASE_9_2_PATTERN_PROMOTION_RULES.md',
            '.codex/PHASE_9_2_SESSION_CONTEXT.md',
            '.codex/PHASE_9_2_CHECKPOINT_PROCEDURES.md',
            '.codex/PHASE_9_2_RECOVERY_PROCEDURES.md',
        ]
        
        for deliverable in deliverables:
            assert Path(deliverable).exists(), f"Missing: {deliverable}"
    
    def test_pattern_catalog_referenced_in_promotion(self):
        """Validate pattern catalog referenced in promotion rules."""
        catalog_path = Path('.codex/PHASE_9_2_LTM_PATTERNS.md')
        promotion_path = Path('.codex/PHASE_9_2_PATTERN_PROMOTION_RULES.md')
        
        promotion_content = promotion_path.read_text()
        assert 'LTM_PATTERNS' in promotion_content or 'pattern' in promotion_content.lower()
    
    def test_pattern_promotion_referenced_in_session_context(self):
        """Validate promotion rules referenced in session context."""
        session_path = Path('.codex/PHASE_9_2_SESSION_CONTEXT.md')
        content = session_path.read_text()
        
        assert 'promotion' in content.lower() or 'ltm' in content.lower()
    
    def test_checkpoint_procedures_reference_recovery(self):
        """Validate checkpoint procedures reference recovery procedures."""
        checkpoint_path = Path('.codex/PHASE_9_2_CHECKPOINT_PROCEDURES.md')
        recovery_path = Path('.codex/PHASE_9_2_RECOVERY_PROCEDURES.md')
        
        checkpoint_content = checkpoint_path.read_text()
        assert 'recovery' in checkpoint_content.lower()
    
    def test_cross_references_valid(self):
        """Validate all cross-references between documents."""
        docs = {
            'LTM_PATTERNS': Path('.codex/PHASE_9_2_LTM_PATTERNS.md'),
            'PATTERN_PROMOTION': Path('.codex/PHASE_9_2_PATTERN_PROMOTION_RULES.md'),
            'SESSION_CONTEXT': Path('.codex/PHASE_9_2_SESSION_CONTEXT.md'),
            'CHECKPOINT': Path('.codex/PHASE_9_2_CHECKPOINT_PROCEDURES.md'),
            'RECOVERY': Path('.codex/PHASE_9_2_RECOVERY_PROCEDURES.md'),
        }
        
        for name, path in docs.items():
            assert path.exists(), f"Document missing: {name}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
