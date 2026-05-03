import argparse
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Optional

from codex.analysis.duplication import DuplicationReport, analyze_duplication

ACCEPTABLE_DUP_RATIO = 0.10
WARNING_DUP_RATIO = 0.20
CRITICAL_DUP_RATIO = 0.30


class DuplicationAnalyzer:
    def __init__(
        self,
        root_path: Path | str,
        *,
        acceptable_ratio: float = ACCEPTABLE_DUP_RATIO,
        extensions: Optional[Iterable[str]] = None,
    ) -> None:
        self.root_path = Path(root_path)
        self.acceptable_ratio = acceptable_ratio
        self.extensions = extensions
        self._last_report: Optional[DuplicationReport] = None

    def analyze(self) -> dict:
        report = analyze_duplication(
            self.root_path,
            extensions=self.extensions,
            acceptable_ratio=self.acceptable_ratio,
            warning_ratio=WARNING_DUP_RATIO,
            critical_ratio=CRITICAL_DUP_RATIO,
        )
        self._last_report = report
        return {
            "stats": report.stats,
            "duplicate_groups": report.duplicate_groups,
            "content_duplicates": report.content_duplicates,
            "recommendations": report.recommendations,
        }

    def generate_report(self) -> str:
        if self._last_report is None:
            self.analyze()
        assert self._last_report is not None
        stats = self._last_report.stats
        lines = ["# Duplication Analysis Report", "", "## Summary", ""]
        lines.append(f"- Total files: {stats.get('total_files', 0)}")
        lines.append(f"- Duplicate count: {stats.get('duplicate_count', 0)}")
        lines.append(f"- Duplication ratio: {stats.get('duplication_ratio', 0):.2%}")
        lines.append(f"- Severity: {stats.get('severity', 'unknown')}")
        lines.append("")
        lines.append("## Recommendations")
        for rec in self._last_report.recommendations:
            lines.append(f"- {rec}")
        return "\n".join(lines)

    def find_refactoring_candidates(self, min_duplicates: int = 2) -> list[dict]:
        if self._last_report is None:
            self.analyze()
        assert self._last_report is not None
        return [
            group
            for group in self._last_report.duplicate_groups
            if group.get("count", 0) >= min_duplicates
        ]


def _cli(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze code duplication")
    parser.add_argument("root", type=str, help="Root directory to analyze")
    parser.add_argument(
        "--threshold", type=float, default=ACCEPTABLE_DUP_RATIO, help="Acceptable duplication ratio"
    )
    parser.add_argument("--output", type=str, default=None, help="Optional path to save report")
    parser.add_argument(
        "--extensions",
        nargs="*",
        default=None,
        help="File extensions to include (e.g., .py .md .yaml)",
    )

    args = parser.parse_args(argv)
    analyzer = DuplicationAnalyzer(
        args.root, acceptable_ratio=args.threshold, extensions=args.extensions
    )
    result = analyzer.analyze()

    if args.output:
        Path(args.output).write_text(json.dumps(result["stats"], indent=2), encoding="utf-8")

    print(json.dumps(result["stats"], indent=2))

    if result["stats"].get("duplication_ratio", 0) > args.threshold:
        return 1
    return 0


def main() -> int:
    return _cli()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
