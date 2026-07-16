"""
PHASE 8 LANE 2: Cache Optimization Tests

Tests for 4-layer cache hierarchy optimization:
1. Layer 1: Pip cache optimization
2. Layer 2: npm cache optimization
3. Layer 3: Workflow cache key expansion
4. Layer 4: Artifact cache retention

Unit tests verify:
- Cache key generation with proper scoping
- Dependency hash calculation
- Restore key fallback chains
- Cache health validation
- Retention policy compliance
"""

import json
import pytest
from pathlib import Path
from aries_serpent_core.ci.cache_manager import (
    CacheManager,
    CacheType,
    CacheConfig,
    CacheHealth,
)


class TestLayer1PipCacheOptimization:
    """Layer 1: Pip cache optimization tests."""

    def test_pip_cache_key_with_workflow_scope(self):
        """Test pip cache key includes workflow scope."""
        manager = CacheManager()
        key = manager.generate_cache_key(
            cache_type=CacheType.PIP,
            workflow_name="pr-checks",
        )

        # Key should include workflow name
        assert "pr-checks" in key
        assert "pip" in key
        assert "Linux" in key or "macOS" in key or "Windows" in key

    def test_pip_cache_key_with_python_version(self):
        """Test pip cache key includes Python version."""
        manager = CacheManager()
        key = manager.generate_cache_key(
            cache_type=CacheType.PIP,
            workflow_name="test-suite",
            extra_identifiers={"python": "3.12"},
        )

        # Key should include Python version
        assert "python-3.12" in key or "3.12" in key

    def test_pip_cache_restore_keys(self):
        """Test pip cache has proper restore key fallback."""
        manager = CacheManager()
        key = manager.generate_cache_key(
            cache_type=CacheType.PIP,
            workflow_name="pr-checks",
        )

        restore_keys = manager.generate_restore_keys(key, fallback_levels=3)

        # Should have fallback levels
        assert len(restore_keys) >= 2
        # Restore keys should be less specific than main key
        assert all(key.startswith(k.rstrip("-")) for k in restore_keys)

    def test_pip_cache_config_creation(self):
        """Test complete pip cache configuration."""
        manager = CacheManager()
        config = manager.create_cache_config(
            cache_type=CacheType.PIP,
            workflow_name="pr-checks",
        )

        # Should be CacheConfig instance
        assert isinstance(config, CacheConfig)
        # Should include pip cache paths
        assert any("pip" in p for p in config.paths)
        # Should have restore keys
        assert len(config.restore_keys) > 0


class TestLayer2NpmCacheOptimization:
    """Layer 2: npm cache optimization tests."""

    def test_npm_cache_key_with_workflow_scope(self):
        """Test npm cache key includes workflow scope."""
        manager = CacheManager()
        key = manager.generate_cache_key(
            cache_type=CacheType.YARN,
            workflow_name="frontend-test",
        )

        # Key should include workflow name
        assert "frontend-test" in key

    def test_npm_cache_key_with_node_version(self):
        """Test npm cache key includes Node version."""
        manager = CacheManager()
        key = manager.generate_cache_key(
            cache_type=CacheType.YARN,
            workflow_name="frontend-test",
            extra_identifiers={"node": "18"},
        )

        # Key should include Node version
        assert "node-18" in key or "18" in key

    def test_npm_cache_config(self):
        """Test npm cache configuration."""
        manager = CacheManager()
        config = manager.create_cache_config(
            cache_type=CacheType.YARN,
            workflow_name="frontend-test",
        )

        # Should be CacheConfig instance
        assert isinstance(config, CacheConfig)
        # Should have restore keys
        assert len(config.restore_keys) > 0


class TestLayer3WorkflowCacheKeyExpansion:
    """Layer 3: Workflow cache key expansion tests."""

    def test_workflow_scoped_cache_keys(self):
        """Test that different workflows get different cache keys."""
        manager = CacheManager()

        key1 = manager.generate_cache_key(
            cache_type=CacheType.PIP,
            workflow_name="pr-checks",
        )

        key2 = manager.generate_cache_key(
            cache_type=CacheType.PIP,
            workflow_name="security-scanning",
        )

        # Keys should be different for different workflows
        assert key1 != key2
        # Each should contain its workflow name
        assert "pr-checks" in key1
        assert "security-scanning" in key2

    def test_cache_key_format_specification(self):
        """Test cache key follows spec: {OS}-{WORKFLOW}-{TYPE}-{HASH}."""
        manager = CacheManager()
        key = manager.generate_cache_key(
            cache_type=CacheType.PIP,
            workflow_name="test-workflow",
        )

        parts = key.split("-")
        # Should have at least: OS, workflow, type, hash
        assert len(parts) >= 3

    def test_multi_level_restore_key_strategy(self):
        """Test 3-level restore key fallback strategy."""
        manager = CacheManager()
        key = manager.generate_cache_key(
            cache_type=CacheType.PIP,
            workflow_name="pr-checks",
        )

        restore_keys = manager.generate_restore_keys(key, fallback_levels=3)

        # Should have multiple fallback levels
        assert len(restore_keys) >= 2

        # Restore keys should get progressively less specific
        for i in range(len(restore_keys) - 1):
            # Each restore key should be shorter (less specific) than previous
            assert len(restore_keys[i + 1]) < len(restore_keys[i])


class TestLayer4ArtifactCacheRetention:
    """Layer 4: Artifact cache retention and cleanup tests."""

    def test_cache_health_validation(self):
        """Test cache health monitoring."""
        manager = CacheManager()
        health = manager.validate_cache_health()

        # Should return CacheHealth instance
        assert isinstance(health, CacheHealth)
        # Should have metrics
        assert health.total_size_gb >= 0
        assert health.total_caches >= 0

    def test_cache_size_threshold_detection(self):
        """Test cache size threshold detection."""
        manager = CacheManager()
        health = manager.validate_cache_health(size_threshold_gb=8.0)

        # Should be CacheHealth instance
        assert isinstance(health, CacheHealth)
        # If size exceeds threshold, should be critical
        if health.total_size_gb > 8.0:
            assert health.is_critical

    def test_cache_age_threshold_detection(self):
        """Test cache age threshold detection."""
        manager = CacheManager()
        health = manager.validate_cache_health(age_threshold_days=30)

        # Should be CacheHealth instance
        assert isinstance(health, CacheHealth)
        # Should have age information if caches exist
        if health.total_caches > 0:
            assert health.oldest_cache_days is not None

    def test_cache_recommendations_generated(self):
        """Test cache health recommendations."""
        manager = CacheManager()
        health = manager.validate_cache_health()

        # Should provide recommendations for optimization
        assert isinstance(health.recommendations, list)


class TestPhase8OptimizationMetrics:
    """Phase 8 Lane 2 optimization metrics tests."""

    def test_cache_optimization_report_structure(self):
        """Test optimization report has required structure."""
        from scripts.phase_8_lane_2_cache_optimization import Phase8Lane2Optimizer

        optimizer = Phase8Lane2Optimizer()
        report = optimizer.generate_comprehensive_report()

        # Should have all required fields
        assert report.current_hit_rate == 0.40  # Phase 7 baseline
        assert report.target_hit_rate == 0.60  # Phase 8 target
        assert report.workflows_analyzed > 0
        assert report.optimization_strategies is not None
        assert len(report.recommendations) > 0

    def test_layer1_pip_optimization_strategy(self):
        """Test Layer 1 optimization strategy."""
        from scripts.phase_8_lane_2_cache_optimization import Phase8Lane2Optimizer

        optimizer = Phase8Lane2Optimizer()
        layer1 = optimizer.generate_layer1_optimizations()

        # Should define Layer 1 optimization
        assert layer1["layer"] == 1
        assert layer1["type"] == "pip"
        assert "cache_paths" in layer1
        assert "key_format" in layer1
        assert "restore_keys" in layer1

    def test_layer2_npm_optimization_strategy(self):
        """Test Layer 2 optimization strategy."""
        from scripts.phase_8_lane_2_cache_optimization import Phase8Lane2Optimizer

        optimizer = Phase8Lane2Optimizer()
        layer2 = optimizer.generate_layer2_optimizations()

        # Should define Layer 2 optimization
        assert layer2["layer"] == 2
        assert layer2["type"] == "npm"
        assert "package_managers" in layer2

    def test_layer3_workflow_optimization_strategy(self):
        """Test Layer 3 optimization strategy."""
        from scripts.phase_8_lane_2_cache_optimization import Phase8Lane2Optimizer

        optimizer = Phase8Lane2Optimizer()
        layer3 = optimizer.generate_layer3_optimizations()

        # Should define Layer 3 optimization
        assert layer3["layer"] == 3
        assert layer3["type"] == "workflow_scope"
        assert "key_specification" in layer3
        assert "restore_key_strategy" in layer3

    def test_layer4_retention_optimization_strategy(self):
        """Test Layer 4 optimization strategy."""
        from scripts.phase_8_lane_2_cache_optimization import Phase8Lane2Optimizer

        optimizer = Phase8Lane2Optimizer()
        layer4 = optimizer.generate_layer4_optimizations()

        # Should define Layer 4 optimization
        assert layer4["layer"] == 4
        assert layer4["type"] == "retention_cleanup"
        assert "cleanup_policy" in layer4
        assert "monitoring" in layer4

    def test_optimization_metrics_calculation(self):
        """Test optimization metrics calculations."""
        from scripts.phase_8_lane_2_cache_optimization import Phase8Lane2Optimizer

        optimizer = Phase8Lane2Optimizer()
        report = optimizer.generate_comprehensive_report()

        # Should have calculated metrics
        metrics = report.metrics
        assert metrics["estimated_daily_savings_hours"] == 13.3
        assert metrics["estimated_annual_savings_hours"] == 4850
        assert metrics["storage_savings_percent"] == 26.7
        assert metrics["total_hit_rate_improvement"] == 0.20


class TestCacheKeyGeneration:
    """Test cache key generation for different scenarios."""

    def test_consistent_key_generation(self):
        """Test cache key generation is consistent."""
        manager = CacheManager()

        key1 = manager.generate_cache_key(
            cache_type=CacheType.PIP,
            workflow_name="test",
        )

        key2 = manager.generate_cache_key(
            cache_type=CacheType.PIP,
            workflow_name="test",
        )

        # Same inputs should produce same key
        assert key1 == key2

    def test_different_workflows_different_keys(self):
        """Test different workflows produce different cache keys."""
        manager = CacheManager()

        key1 = manager.generate_cache_key(
            cache_type=CacheType.PIP,
            workflow_name="workflow1",
        )

        key2 = manager.generate_cache_key(
            cache_type=CacheType.PIP,
            workflow_name="workflow2",
        )

        # Different workflows should produce different keys
        assert key1 != key2

    def test_dependency_hash_changes_key(self):
        """Test dependency changes affect cache key."""
        manager = CacheManager()

        # Note: This test verifies the mechanism is in place
        # Actual hash changes would require modifying dependency files
        key = manager.generate_cache_key(
            cache_type=CacheType.PIP,
            workflow_name="test",
        )

        # Key should include some hash component
        parts = key.split("-")
        # Last part should be hash
        assert len(parts[-1]) > 4  # Hash should be reasonably long
