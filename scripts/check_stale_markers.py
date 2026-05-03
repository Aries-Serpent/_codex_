#!/usr/bin/env python3
"""
Check for stale test markers.
Analyzes test markers to identify tests that may no longer need to be skipped.
"""
import json
import sys
from datetime import datetime
from pathlib import Path


class StaleMarkerChecker:
    """Check for stale test markers."""

    def __init__(self, registry_path: Path = Path('.test_markers.json')):
        self.registry_path = registry_path
        self.markers = []
        self.stale_markers = []

    def load_registry(self) -> bool:
        """Load marker registry from JSON file."""
        if not self.registry_path.exists():
            print(f"❌ Registry file not found: {self.registry_path}")
            print("   Run scan_test_markers.py first to generate the registry.")
            return False

        try:
            with open(self.registry_path) as f:
                data = json.load(f)
                self.markers = data.get('markers', [])
                print(f"✅ Loaded {len(self.markers)} markers from {self.registry_path}")
                return True
        except Exception as e:
            print(f"❌ Failed to load registry: {e}")
            return False

    def check_staleness(self, max_age_days: int = 90) -> list[dict]:
        """
        Check for markers that might be stale based on suspicious indicators.

        Note: Currently checks for vague/missing reasons and issue references.
        The max_age_days parameter is reserved for future time-based staleness detection.

        Args:
            max_age_days: Reserved for future use - maximum age in days before marker is stale

        Returns:
            List of potentially stale markers
        """
        print("\n🔍 Checking for stale markers...")
        # Note: max_age_days is not yet implemented - requires timestamp tracking

        stale_markers = []
        datetime.now()

        for marker in self.markers:
            # Check if marker has a vague or missing reason
            reason = marker.get('reason', '').lower()

            is_suspicious = False
            suspicious_reasons = []

            # Check 1: No reason provided
            if not reason:
                is_suspicious = True
                suspicious_reasons.append("No reason provided")

            # Check 2: Vague reasons
            vague_keywords = ['todo', 'fixme', 'later', 'temporary', 'wip', 'broken']
            if any(keyword in reason for keyword in vague_keywords):
                is_suspicious = True
                suspicious_reasons.append(f"Vague reason: '{reason}'")

            # Check 3: References to old issues or PRs (simple heuristic)
            if 'pr' in reason or 'issue' in reason or '#' in reason:
                # Could be referencing an old issue
                is_suspicious = True
                suspicious_reasons.append(f"References issue/PR: '{reason}'")

            if is_suspicious:
                stale_markers.append({
                    **marker,
                    'suspicious_reasons': suspicious_reasons
                })

        self.stale_markers = stale_markers
        print(f"   Found {len(stale_markers)} potentially stale markers")
        return stale_markers

    def generate_report(self) -> str:
        """Generate stale marker report."""
        if not self.stale_markers:
            return "# Stale Marker Report\n\nNo stale markers found. ✅"

        report = ["# Stale Marker Report", ""]
        report.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Total Stale Markers**: {len(self.stale_markers)}")
        report.append("")
        report.append("## Potentially Stale Markers")
        report.append("")

        for marker in self.stale_markers:
            report.append(f"### {marker['file']}::{marker['test']}")
            report.append("")
            report.append(f"- **Marker Type**: {marker['marker']}")
            report.append(f"- **Line**: {marker['line']}")
            report.append(f"- **Reason**: {marker.get('reason', 'None')}")
            report.append("")
            report.append("**Suspicious Indicators:**")
            for reason in marker['suspicious_reasons']:
                report.append(f"- {reason}")
            report.append("")
            report.append("**Action**: Review this test to determine if it can be re-enabled.")
            report.append("")

        return '\n'.join(report)

    def print_summary(self):
        """Print summary of stale markers."""
        print("\n" + "=" * 60)
        print("📊 Stale Marker Summary")
        print("=" * 60)

        if not self.stale_markers:
            print("  No stale markers found. ✅")
            return

        print(f"  Total stale markers: {len(self.stale_markers)}")
        print("")

        # Group by file
        by_file: dict[str, int] = {}
        for marker in self.stale_markers:
            file = marker['file']
            by_file[file] = by_file.get(file, 0) + 1

        print("  By file:")
        for file, count in sorted(by_file.items(), key=lambda x: -x[1])[:10]:
            print(f"    {file}: {count}")


def main():
    """Main entry point."""
    checker = StaleMarkerChecker()

    if not checker.load_registry():
        sys.exit(1)

    # Check for staleness
    stale_markers = checker.check_staleness(max_age_days=90)

    # Generate report
    report = checker.generate_report()
    report_path = Path('docs/stale_markers_report.md')
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(report)
    print(f"✅ Saved stale marker report to {report_path}")

    # Print summary
    checker.print_summary()

    # Exit with error if stale markers found (optional)
    if stale_markers:
        print("\n⚠️  Found stale markers. Please review and update.")
        # Don't fail the build, just warn
        sys.exit(0)
    else:
        print("\n✅ No stale markers found.")
        sys.exit(0)


if __name__ == '__main__':
    main()
