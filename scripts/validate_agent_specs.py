#!/usr/bin/env python3
"""
Agent Specification Validator

Validates agent specifications against the canonical JSON schema.
Generates a migration report for non-compliant agents.

Usage:
    python scripts/validate_agent_specs.py [--fix] [--report]
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any

# Optional: jsonschema for validation
try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

# Optional: yaml for parsing
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent
AGENTS_DIR = REPO_ROOT / ".github" / "agents"
SCHEMA_PATH = REPO_ROOT / "configs" / "schemas" / "agent_spec.schema.json"
OUTPUT_REPORT = REPO_ROOT / ".codex" / "qa_walkthrough" / "agent_validation_report.json"


def load_schema() -> dict[str, Any]:
    """Load the agent specification schema."""
    if not SCHEMA_PATH.exists():
        logger.error(f"Schema not found: {SCHEMA_PATH}")
        return {}

    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_agent_specs() -> list[Path]:
    """Find all agent specification files."""
    specs = []

    if not AGENTS_DIR.exists():
        logger.warning(f"Agents directory not found: {AGENTS_DIR}")
        return specs

    # Find YAML files
    for ext in ['*.yaml', '*.yml']:
        specs.extend(AGENTS_DIR.glob(ext))

    # Find agent.md files in subdirectories
    for subdir in AGENTS_DIR.iterdir():
        if subdir.is_dir():
            for md_file in subdir.glob('*.md'):
                if 'agent' in md_file.name.lower():
                    specs.append(md_file)

    return specs


def parse_agent_spec(path: Path) -> dict[str, Any] | None:
    """Parse an agent specification file."""
    try:
        if path.suffix in ['.yaml', '.yml']:
            if not HAS_YAML:
                logger.warning(f"PyYAML not installed, skipping: {path}")
                return None
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        elif path.suffix == '.json':
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        elif path.suffix == '.md':
            # Extract YAML frontmatter from markdown
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3 and HAS_YAML:
                    return yaml.safe_load(parts[1]) or {}
            return None
    except Exception as e:
        logger.error(f"Failed to parse {path}: {e}")
        return None

    # Explicit return for unhandled file extensions
    return None


def validate_spec(spec: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    """Validate a specification against the schema."""
    errors = []

    if not HAS_JSONSCHEMA:
        # Basic validation without jsonschema
        required = schema.get('required', [])
        for field in required:
            if field not in spec:
                errors.append(f"Missing required field: {field}")

        # Check field types
        props = schema.get('properties', {})
        for key, value in spec.items():
            if key in props:
                expected_type = props[key].get('type')
                if expected_type == 'string' and not isinstance(value, str):
                    errors.append(f"Field '{key}' should be string, got {type(value).__name__}")
                elif expected_type == 'array' and not isinstance(value, list):
                    errors.append(f"Field '{key}' should be array, got {type(value).__name__}")
                elif expected_type == 'boolean' and not isinstance(value, bool):
                    errors.append(f"Field '{key}' should be boolean, got {type(value).__name__}")
        return errors

    # Full validation with jsonschema
    validator = jsonschema.Draft7Validator(schema)
    for error in validator.iter_errors(spec):
        errors.append(f"{error.json_path}: {error.message}")

    return errors


def generate_report(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate validation report."""
    compliant = [r for r in results if r['valid']]
    non_compliant = [r for r in results if not r['valid']]

    return {
        "metadata": {
            "generated_at": __import__('datetime').datetime.now().isoformat(),
            "schema_path": str(SCHEMA_PATH),
            "total_agents": len(results)
        },
        "summary": {
            "compliant": len(compliant),
            "non_compliant": len(non_compliant),
            "compliance_rate": f"{len(compliant) / max(len(results), 1) * 100:.1f}%"
        },
        "compliant_agents": [r['path'] for r in compliant],
        "non_compliant_agents": [
            {
                "path": r['path'],
                "errors": r['errors']
            }
            for r in non_compliant
        ]
    }



def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Validate agent specifications')
    parser.add_argument('--fix', action='store_true', help='Attempt to fix issues')
    parser.add_argument('--report', action='store_true', help='Generate JSON report')
    parser.add_argument('--strict', action='store_true', help='Exit with error if non-compliant')
    args = parser.parse_args()

    logger.info("Loading agent specification schema...")
    schema = load_schema()
    if not schema:
        logger.error("Failed to load schema")
        return 1

    logger.info("Finding agent specifications...")
    specs = find_agent_specs()
    logger.info(f"Found {len(specs)} agent specifications")

    results = []
    for spec_path in specs:
        spec = parse_agent_spec(spec_path)
        if spec is None:
            continue

        errors = validate_spec(spec, schema)
        results.append({
            'path': str(spec_path.relative_to(REPO_ROOT)),
            'valid': len(errors) == 0,
            'errors': errors
        })

    # Print summary
    compliant = sum(1 for r in results if r['valid'])
    non_compliant = sum(1 for r in results if not r['valid'])

    logger.info("\nValidation Results:")
    logger.info(f"  Compliant: {compliant}")
    logger.info(f"  Non-compliant: {non_compliant}")
    logger.info(f"  Compliance Rate: {compliant / max(len(results), 1) * 100:.1f}%")

    # Print errors for non-compliant
    for r in results:
        if not r['valid']:
            logger.warning(f"\n{r['path']}:")
            for error in r['errors'][:5]:  # Limit to 5 errors per file
                logger.warning(f"  - {error}")

    # Generate report
    if args.report:
        report = generate_report(results)
        OUTPUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        logger.info(f"\nReport saved to: {OUTPUT_REPORT}")

    if args.strict and non_compliant > 0:
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
