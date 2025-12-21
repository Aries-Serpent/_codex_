"""
Validation script for agent manifest.

This script validates the agent manifest YAML structure and configuration.
"""

import sys
from pathlib import Path

import yaml


def validate_manifest(manifest_path: Path) -> bool:
    """
    Validate agent manifest structure and configuration.
    
    Args:
        manifest_path: Path to agent manifest YAML file
        
    Returns:
        True if validation passes
        
    Raises:
        SystemExit: If validation fails
    """
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = yaml.safe_load(f)
        
        # Required fields
        required_fields = ['name', 'version', 'description', 'metadata', 'triggers', 
                          'permissions', 'capabilities', 'configuration', 'runtime']
        
        for field in required_fields:
            if field not in manifest:
                print(f"❌ Missing required field: {field}", file=sys.stderr)
                return False
        
        # Validate structure
        print(f"✓ Agent: {manifest['name']} v{manifest['version']}")
        print(f"✓ Description: {manifest['description']}")
        print(f"✓ Triggers: {len(manifest['triggers'])} events")
        print(f"✓ Capabilities: {len(manifest['capabilities'])} categories")
        print(f"✓ Permissions: {len(manifest['permissions'])} scopes")
        
        # Validate configuration
        config = manifest.get('configuration', {})
        if 'criteria_weights' in config:
            weights = config['criteria_weights']
            total = sum(weights.values())
            if abs(total - 1.0) > 0.01:
                print(f"⚠️  Warning: Criteria weights sum to {total}, expected 1.0", file=sys.stderr)
        
        # Validate runtime
        runtime = manifest.get('runtime', {})
        if 'entry_point' in runtime:
            entry_point = Path(runtime['entry_point'])
            if not entry_point.exists():
                print(f"⚠️  Warning: Entry point not found: {entry_point}", file=sys.stderr)
        
        print("\n✅ Manifest validation: PASSED")
        return True
        
    except yaml.YAMLError as e:
        print(f"❌ YAML parsing error: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"❌ Validation error: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    manifest_path = Path(".github/agents/codex-reviewer.agent.yml")
    
    if not manifest_path.exists():
        print(f"❌ Manifest not found: {manifest_path}", file=sys.stderr)
        sys.exit(1)
    
    if not validate_manifest(manifest_path):
        sys.exit(1)
    
    sys.exit(0)
