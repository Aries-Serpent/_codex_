"""Generate a pattern ID migration map for the batch triage agent."""

import argparse
import json
from datetime import datetime
from pathlib import Path

from pattern_learner import PatternLearner


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate legacy pattern IDs to SHA-256.")
    parser.add_argument(
        "--kb-path",
        default=".codex/cognitive_brain",
        help="Path to cognitive brain storage root.",
    )
    parser.add_argument(
        "--output",
        default=".codex/cognitive_brain/patterns/ci_failures/pattern_id_migration.json",
        help="Output JSON path for the migration map.",
    )
    args = parser.parse_args()

    learner = PatternLearner(kb_path=Path(args.kb_path))
    migrations = learner.migrate_existing_patterns()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "mappings": migrations,
                "total_migrated": len(migrations),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
