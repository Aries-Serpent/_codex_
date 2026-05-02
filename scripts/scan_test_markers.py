#!/usr/bin/env python3
"""
Test marker scanner and tracker.
Scans all test files for pytest markers (skip, skipif, xfail, xfailif) and
maintains a registry of marked tests with metadata.
"""
import ast
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class MarkerScanner:
    """Scan Python test files for pytest markers."""

    TRACKED_MARKERS = {'skip', 'skipif', 'xfail', 'xfailif'}

    def __init__(self, test_dir: Path = Path('tests')):
        self.test_dir = test_dir
        self.markers: List[Dict] = []

    def scan_file(self, filepath: Path) -> List[Dict]:
        """
        Scan a single Python file for markers.

        Returns:
            List of marker metadata dicts
        """
        try:
            content = filepath.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(filepath))
        except Exception as e:
            print(f"⚠️  Failed to parse {filepath}: {e}")
            return []

        markers_found = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if this is a test function
                if node.name.startswith('test_'):
                    test_markers = self._extract_markers(node)
                    if test_markers:
                        for marker in test_markers:
                            # Get relative path, handling both absolute and relative paths
                            try:
                                rel_path = filepath.relative_to(Path.cwd())
                            except ValueError:
                                rel_path = filepath

                            markers_found.append({
                                'file': str(rel_path),
                                'test': node.name,
                                'marker': marker['type'],
                                'reason': marker.get('reason', ''),
                                'line': node.lineno,
                                'discovered': datetime.now().isoformat(),
                            })

        return markers_found

    def _extract_markers(self, node: ast.FunctionDef) -> List[Dict]:
        """Extract pytest markers from function decorators."""
        markers = []

        for decorator in node.decorator_list:
            marker_info = self._parse_decorator(decorator)
            if marker_info:
                markers.append(marker_info)

        return markers

    def _parse_decorator(self, decorator: ast.expr) -> Dict:
        """Parse a decorator AST node to extract marker info."""
        # Handle @pytest.mark.skip
        if isinstance(decorator, ast.Attribute) and (hasattr(decorator.value, 'attr') and
            decorator.value.attr == 'mark' and
            decorator.attr in self.TRACKED_MARKERS):
            return {'type': decorator.attr}

        # Handle @pytest.mark.skip(reason="...")
        if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
            if (hasattr(decorator.func.value, 'attr') and
                decorator.func.value.attr == 'mark' and
                decorator.func.attr in self.TRACKED_MARKERS):

                reason = ''
                for keyword in decorator.keywords:
                    if keyword.arg == 'reason':
                        if isinstance(keyword.value, ast.Constant):
                            reason = keyword.value.value

                return {
                    'type': decorator.func.attr,
                    'reason': reason
                }

        return None

    def scan_all(self) -> List[Dict]:
        """Scan all test files in test directory."""
        print(f"🔍 Scanning {self.test_dir} for test markers...")

        for test_file in self.test_dir.rglob('test_*.py'):
            file_markers = self.scan_file(test_file)
            self.markers.extend(file_markers)

        print(f"   Found {len(self.markers)} marked tests")
        return self.markers

    def save_registry(self, output_path: Path = Path('.test_markers.json')):
        """Save marker registry to JSON file."""
        with open(output_path, 'w') as f:
            json.dump({
                'scan_date': datetime.now().isoformat(),
                'total_markers': len(self.markers),
                'markers': self.markers
            }, f, indent=2)

        print(f"✅ Saved marker registry to {output_path}")

    def generate_report(self) -> str:
        """Generate human-readable marker report."""
        if not self.markers:
            return "No marked tests found."

        # Group by marker type
        by_type: Dict[str, List[Dict]] = {}
        for marker in self.markers:
            marker_type = marker['marker']
            if marker_type not in by_type:
                by_type[marker_type] = []
            by_type[marker_type].append(marker)

        report = ["# Test Marker Report", ""]
        report.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Total Marked Tests**: {len(self.markers)}")
        report.append("")

        for marker_type, items in sorted(by_type.items()):
            report.append(f"## {marker_type.upper()} ({len(items)} tests)")
            report.append("")

            for item in sorted(items, key=lambda x: x['file']):
                report.append(f"- **{item['file']}::{item['test']}** (line {item['line']})")
                if item['reason']:
                    report.append(f"  - Reason: {item['reason']}")
                report.append("")

        return '\n'.join(report)


def main():
    """Main entry point."""
    scanner = MarkerScanner()
    markers = scanner.scan_all()

    # Save JSON registry
    scanner.save_registry()

    # Generate markdown report
    report = scanner.generate_report()
    report_path = Path('docs/test_markers_report.md')
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(report)
    print(f"✅ Saved marker report to {report_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("📊 Marker Summary")
    print("=" * 60)

    by_type = {}
    for marker in markers:
        by_type[marker['marker']] = by_type.get(marker['marker'], 0) + 1

    for marker_type, count in sorted(by_type.items()):
        print(f"  {marker_type}: {count}")


if __name__ == '__main__':
    main()
