#!/usr/bin/env python3
"""
Migrate D365 Sla Csv

Purpose:
    Migration script for d365_sla_csv

Usage:
    python scripts/migrate_d365_sla_csv.py [options]

    Examples:
    $ python scripts/migrate_d365_sla_csv.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""


from __future__ import annotations

import argparse
import json
import logging

# Add src to path for imports
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root / "src"))

from codex.dynamics.model.sla import SLAPolicyRegistry

logger = logging.getLogger(__name__)


def main() -> int:
    """Migrate CSV to JSON policy registry."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--csv",
        default="configs/deployment/d365/slas.csv",
        help="Path to legacy CSV file",
    )
    parser.add_argument(
        "--output",
        default="configs/deployment/d365/sla_policies.json",
        help="Path for output JSON policy file",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    csv_path = Path(args.csv)
    output_path = Path(args.output)

    if not csv_path.exists():
        logger.error(f"CSV file not found: {csv_path}")
        return 1

    logger.info(f"Migrating {csv_path} -> {output_path}")

    # Perform migration
    try:
        registry = SLAPolicyRegistry.from_csv(str(csv_path))

        logger.info(f"Migrated {len(registry.policies)} policies")
        for policy in registry.policies:
            logger.info(
                f"  - {policy.name}: {policy.metric.value}, "
                f"{policy.target_minutes}min, "
                f"{len(policy.pause_conditions)} pause conditions"
            )

        # Write to output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(
                registry.model_dump(mode="json"),
                f,
                indent=2,
            )

        logger.info(f"Successfully wrote policies to {output_path}")

        # Create a deprecation notice
        deprecation_notice = csv_path.parent / "DEPRECATED_CSV.md"
        with deprecation_notice.open("w", encoding="utf-8") as f:
            f.write(f"""# Deprecated: slas.csv

**Status:** DEPRECATED as of migration to SLA Policy Objects

**Migration Date:** {registry.last_updated}

**Replacement:** `sla_policies.json`

## Migration Path

The legacy CSV format has been replaced with a versioned Policy Object model
that provides:

- Type safety via Pydantic validation
- Version tracking for policy changes
- Dynamic evaluation against SaaS state
- Integration with Dynamics 365 API

### Using the New Format

```python
from codex.dynamics.model.sla import SLAPolicyRegistry

# Load policies
with open("sla_policies.json") as f:
    data = json.load(f)
    registry = SLAPolicyRegistry(**data)

# Get a policy
policy = registry.get_policy("cdx_assignment_standard")
```

### Legacy CSV Columns

The CSV format supported these columns:
- `name`: Policy identifier
- `metric`: SLA metric type
- `target_minutes`: Target time in minutes
- `pause_conditions`: Semicolon-separated conditions

**Do not edit this CSV file.** Update `sla_policies.json` instead.
""")

        logger.info(f"Created deprecation notice at {deprecation_notice}")

        return 0

    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
