#!/usr/bin/env python3
"""
Validation script for monitoring configuration.
Tests that the config structure matches what artifact_monitor.py expects.
"""

import sys
from pathlib import Path

import yaml


def validate_config():
    """Validate monitoring configuration structure."""
    config_path = Path('.codex/config/monitoring.yaml')

    print(f"Loading config from: {config_path}")

    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)

        print("✓ Config file loaded successfully\n")

        # Validate required top-level keys
        assert 'monitoring' in config, "Missing 'monitoring' key"
        print("✓ 'monitoring' section exists")

        # Validate workflows section
        assert 'workflows' in config['monitoring'], "Missing 'monitoring.workflows' key"
        workflows = config['monitoring']['workflows']
        print("✓ 'monitoring.workflows' section exists")

        assert 'include_patterns' in workflows, "Missing 'monitoring.workflows.include_patterns'"
        assert 'exclude_patterns' in workflows, "Missing 'monitoring.workflows.exclude_patterns'"
        print(f"  - include_patterns: {workflows['include_patterns']}")
        print(f"  - exclude_patterns: {workflows['exclude_patterns']}")

        # Validate failure_detection section
        assert 'failure_detection' in config['monitoring'], "Missing 'monitoring.failure_detection' key"
        failure_detection = config['monitoring']['failure_detection']
        print("✓ 'monitoring.failure_detection' section exists")

        assert 'consecutive_failures_threshold' in failure_detection, \
            "Missing 'monitoring.failure_detection.consecutive_failures_threshold'"
        assert 'rate_limit_margin' in failure_detection, \
            "Missing 'monitoring.failure_detection.rate_limit_margin'"
        print(f"  - consecutive_failures_threshold: {failure_detection['consecutive_failures_threshold']}")
        print(f"  - rate_limit_margin: {failure_detection['rate_limit_margin']}")

        # Simulate the actual access patterns from artifact_monitor.py
        print("\n--- Simulating artifact_monitor.py access patterns ---")

        # Line 152: config = self.config['monitoring']['workflows']
        workflows_config = config['monitoring']['workflows']
        print(f"✓ Access config['monitoring']['workflows']: {type(workflows_config).__name__}")

        # Line 155-156: config.get('exclude_patterns', [])
        exclude = workflows_config.get('exclude_patterns', [])
        print(f"✓ Access workflows.get('exclude_patterns', []): {exclude}")

        # Line 159: config.get('include_patterns', [])
        include = workflows_config.get('include_patterns', [])
        print(f"✓ Access workflows.get('include_patterns', []): {include}")

        # Line 168: margin = self.config['monitoring']['failure_detection']['rate_limit_margin']
        margin = config['monitoring']['failure_detection']['rate_limit_margin']
        print(f"✓ Access config['monitoring']['failure_detection']['rate_limit_margin']: {margin}")

        # Line 258: threshold = self.config['monitoring']['failure_detection']['consecutive_failures_threshold']
        threshold = config['monitoring']['failure_detection']['consecutive_failures_threshold']
        print(f"✓ Access config['monitoring']['failure_detection']['consecutive_failures_threshold']: {threshold}")

        print("\n" + "="*60)
        print("✅ Configuration validation PASSED!")
        print("="*60)
        print("\nThe monitoring config structure now matches what")
        print("artifact_monitor.py expects. The KeyError should be resolved.")

        return 0

    except AssertionError as e:
        print(f"\n❌ Validation FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(validate_config())
