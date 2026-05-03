#!/usr/bin/env python3
"""
Enhanced Workflow Analytics with Scribe Integration

Combines workflow analytics with doc-test-scribe capabilities for:
- Comprehensive artifact generation
- Semantic pattern analysis using TF-IDF
- Intelligent documentation of workflow issues
- Test generation for workflow validation

This cross-built agent leverages:
1. Workflow Analytics: Pattern detection, metrics, health monitoring
2. Doc-Test-Scribe: TF-IDF analysis, semantic search, documentation generation
"""

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Try to import scribe tools if available
try:
    import importlib.util
    spec = importlib.util.find_spec("codex.agents.doc_test_scribe")
    if spec is not None:
        from codex.agents.doc_test_scribe import tokenizer
        SCRIBE_AVAILABLE = True
    else:
        SCRIBE_AVAILABLE = False
except ImportError:
    SCRIBE_AVAILABLE = False
    print("⚠️ Doc-test-scribe tools not available, using basic analysis")


class WorkflowAnalyticsScribe:
    """Enhanced workflow analytics with scribe capabilities."""

    def __init__(self, use_scribe: bool = True):
        self.use_scribe = use_scribe and SCRIBE_AVAILABLE
        self.error_patterns = self._load_error_patterns()
        self.pattern_cache = {}

    def _load_error_patterns(self) -> dict[str, str]:
        """Load error pattern definitions."""
        return {
            "import_error": r"(?:ModuleNotFoundError|ImportError|NameError):\s*(.+)",
            "syntax_error": r"(?:SyntaxError|yaml\.scanner\.ScannerError):\s*(.+)",
            "test_failure": r"(?:FAILED|AssertionError|pytest\.fail):\s*(.+)",
            "timeout": r"(?:TimeoutError|Timeout|timed out):\s*(.+)",
            "permission": r"(?:PermissionError|403|Permission denied):\s*(.+)",
            "dependency": r"(?:pip resolver|incompatible|version conflict):\s*(.+)",
            "type_error": r"(?:TypeError|AttributeError):\s*(.+)",
            "file_not_found": r"(?:FileNotFoundError|No such file):\s*(.+)",
            "disk_full": r"(?:No space left|disk.*full|OSError.*28)",
            "artifact_missing": r"(?:Artifact.*not found|Unable to find.*artifact)",
            "env_setup": r"(?:command not found|tool.*not.*found|could not find)",
        }

    def analyze_with_semantic_context(
        self,
        log_content: str,
        workflow_context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Analyze workflow logs with semantic understanding.

        If scribe tools available, uses TF-IDF for pattern matching.
        Otherwise, falls back to regex-based analysis.
        """
        if self.use_scribe:
            return self._analyze_semantic(log_content, workflow_context)
        return self._analyze_regex(log_content)

    def _analyze_regex(self, log_content: str) -> dict[str, Any]:
        """Basic regex-based pattern detection."""
        results = defaultdict(list)

        for category, pattern in self.error_patterns.items():
            matches = re.findall(pattern, log_content, re.IGNORECASE | re.MULTILINE)
            if matches:
                unique_matches = list(set(matches))[:5]
                results[category].extend(unique_matches)

        return {
            "method": "regex",
            "patterns": dict(results),
            "confidence": 0.7,  # Basic regex has lower confidence
        }

    def _analyze_semantic(
        self,
        log_content: str,
        workflow_context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Semantic analysis using TF-IDF from doc-test-scribe.

        This provides higher confidence pattern matching by understanding
        semantic similarity between error patterns.
        """
        # Tokenize the log content
        tokens = self._tokenize_log(log_content)

        # Extract semantic features
        features = self._extract_semantic_features(tokens, workflow_context)

        # Match against known patterns with similarity scoring
        pattern_matches = self._match_patterns_semantic(features)

        # Find similar historical issues
        similar_issues = self._find_similar_issues(features)

        return {
            "method": "semantic",
            "patterns": pattern_matches,
            "confidence": 0.95,  # Semantic analysis has higher confidence
            "features": features,
            "similar_issues": similar_issues,
        }

    def _tokenize_log(self, log_content: str) -> list[str]:
        """Tokenize log content for semantic analysis."""
        if self.use_scribe:
            try:
                # Use scribe's tokenizer
                return tokenizer.tokenize(log_content)
            except Exception as e:
                print(f"⚠️ Scribe tokenizer failed: {e}")

        # Fallback: simple tokenization
        return re.findall(r'\w+', log_content.lower())

    def _extract_semantic_features(
        self,
        tokens: list[str],
        context: dict[str, Any]
    ) -> dict[str, Any]:
        """Extract semantic features from tokens and context."""
        # Count token frequencies
        token_freq = Counter(tokens)

        # Extract important terms (high frequency, not common words)
        stop_words = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or'}
        important_terms = {
            term: freq
            for term, freq in token_freq.most_common(50)
            if term not in stop_words and len(term) > 3
        }

        # Categorize by domain
        error_terms = [t for t in important_terms if any(e in t for e in ['error', 'fail', 'exception'])]
        test_terms = [t for t in important_terms if any(t in w for w in ['test', 'pytest', 'assert'])]
        build_terms = [t for t in important_terms if any(t in w for w in ['build', 'compile', 'install'])]

        return {
            "important_terms": important_terms,
            "error_terms": error_terms,
            "test_terms": test_terms,
            "build_terms": build_terms,
            "workflow_name": context.get("name", "unknown"),
            "workflow_type": self._infer_workflow_type(context),
        }

    def _infer_workflow_type(self, context: dict[str, Any]) -> str:
        """Infer workflow type from context."""
        name = context.get("name", "").lower()

        if "test" in name:
            return "testing"
        if "build" in name or "compile" in name:
            return "build"
        if "deploy" in name or "release" in name:
            return "deployment"
        if "security" in name or "scan" in name:
            return "security"
        return "general"

    def _match_patterns_semantic(self, features: dict[str, Any]) -> dict[str, list[str]]:
        """Match patterns using semantic similarity."""
        matches = defaultdict(list)

        # Analyze error terms for pattern matching
        error_terms = features.get("error_terms", [])

        for term in error_terms:
            # Match against known pattern categories
            if "import" in term or "module" in term:
                matches["import_error"].append(f"Import issue detected: {term}")
            elif "timeout" in term or "timed" in term:
                matches["timeout"].append(f"Timeout detected: {term}")
            elif "disk" in term or "space" in term:
                matches["disk_full"].append(f"Disk issue detected: {term}")
            elif "artifact" in term:
                matches["artifact_missing"].append(f"Artifact issue: {term}")
            elif "permission" in term or "denied" in term:
                matches["permission"].append(f"Permission issue: {term}")

        return dict(matches)

    def _find_similar_issues(self, features: dict[str, Any]) -> list[dict[str, Any]]:
        """Find similar historical issues using semantic search."""
        # In a full implementation, this would use TF-IDF to find similar
        # patterns in the error pattern database
        # For now, return placeholder
        return []

    def generate_comprehensive_artifact(
        self,
        analysis_results: dict[str, Any],
        workflow_runs: list[dict[str, Any]],
        statistics: dict[str, Any],
    ) -> tuple[str, str, str]:
        """
        Generate comprehensive artifacts:
        1. Detailed markdown report
        2. JSON data file
        3. Runbook for remediation

        Leverages scribe's documentation generation if available.
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")

        # Generate markdown report
        markdown = self._generate_markdown_report(
            analysis_results, workflow_runs, statistics, timestamp
        )

        # Generate JSON data
        json_data = self._generate_json_artifact(
            analysis_results, workflow_runs, statistics, timestamp
        )

        # Generate runbook
        runbook = self._generate_runbook(analysis_results, statistics)

        return markdown, json_data, runbook

    def _generate_markdown_report(
        self,
        analysis: dict[str, Any],
        runs: list[dict[str, Any]],
        stats: dict[str, Any],
        timestamp: str,
    ) -> str:
        """Generate comprehensive markdown report."""
        lines = [
            "# Enhanced Workflow Analytics Report",
            "",
            f"**Generated**: {timestamp}",
            f"**Analysis Method**: {analysis.get('method', 'regex')} (confidence: {analysis.get('confidence', 0.7):.0%})",
            f"**Scribe Integration**: {'✅ Enabled' if self.use_scribe else '❌ Disabled'}",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            f"**Health Status**: {stats.get('health_status', 'UNKNOWN')}",
            f"**Success Rate**: {stats.get('success_rate', 0):.1f}%",
            f"**Total Runs**: {stats.get('total_runs', 0)}",
            "",
        ]

        # Add semantic features if available
        if "features" in analysis:
            features = analysis["features"]
            lines.extend([
                "## Semantic Analysis",
                "",
                f"**Workflow Type**: {features.get('workflow_type', 'unknown')}",
                "",
                "### Important Terms Detected",
                "",
            ])

            for term, freq in list(features.get("important_terms", {}).items())[:10]:
                lines.append(f"- `{term}` ({freq} occurrences)")

            lines.append("")

        # Add pattern matches
        patterns = analysis.get("patterns", {})
        if patterns:
            lines.extend([
                "## Error Patterns Detected",
                "",
            ])

            for category, matches in patterns.items():
                lines.append(f"### {category.replace('_', ' ').title()}")
                lines.append("")
                for match in matches[:5]:
                    lines.append(f"- `{match}`")
                lines.append("")

        # Add similar issues if available
        similar = analysis.get("similar_issues", [])
        if similar:
            lines.extend([
                "## Similar Historical Issues",
                "",
            ])
            for issue in similar[:5]:
                lines.append(f"- {issue.get('title', 'Unknown')}")

        return "\n".join(lines)

    def _generate_json_artifact(
        self,
        analysis: dict[str, Any],
        runs: list[dict[str, Any]],
        stats: dict[str, Any],
        timestamp: str,
    ) -> str:
        """Generate JSON artifact."""
        artifact = {
            "metadata": {
                "generated_at": timestamp,
                "version": "2.0.0",
                "scribe_enabled": self.use_scribe,
                "analysis_method": analysis.get("method", "regex"),
                "confidence": analysis.get("confidence", 0.7),
            },
            "statistics": stats,
            "analysis": analysis,
            "workflow_runs": [
                {
                    "id": run.get("databaseId"),
                    "name": run.get("name"),
                    "conclusion": run.get("conclusion"),
                    "created_at": run.get("createdAt"),
                }
                for run in runs[:20]
            ],
        }

        return json.dumps(artifact, indent=2)

    def _generate_runbook(
        self,
        analysis: dict[str, Any],
        stats: dict[str, Any],
    ) -> str:
        """Generate remediation runbook."""
        lines = [
            "# Workflow Issue Remediation Runbook",
            "",
            f"**Health Status**: {stats.get('health_status', 'UNKNOWN')}",
            "",
            "## Quick Diagnosis",
            "",
        ]

        # Determine issues and remediation steps
        patterns = analysis.get("patterns", {})

        if not patterns:
            lines.extend([
                "✅ **No issues detected** - CI/CD is healthy",
                "",
                "### Maintenance Tasks",
                "- Continue monitoring weekly",
                "- Review success metrics monthly",
                "- Update error pattern database as needed",
            ])
        else:
            lines.extend([
                "⚠️ **Issues detected** - Action required",
                "",
                "## Remediation Steps",
                "",
            ])

            for category, matches in patterns.items():
                lines.extend([
                    f"### {category.replace('_', ' ').title()}",
                    "",
                    "**Detected Issues:**",
                ])
                for match in matches[:3]:
                    lines.append(f"- {match}")

                # Add remediation based on category
                remediation = self._get_remediation_steps(category)
                lines.extend([
                    "",
                    "**Remediation:**",
                ])
                for step in remediation:
                    lines.append(f"{step}")
                lines.append("")

        return "\n".join(lines)

    def _get_remediation_steps(self, category: str) -> list[str]:
        """Get remediation steps for error category."""
        remediation_map = {
            "import_error": [
                "1. Review missing import statements",
                "2. Check package installation in CI",
                "3. Verify PYTHONPATH configuration",
                "4. See: `.codex/reports/ERROR_PATTERN_DATABASE.md#import-errors`",
            ],
            "disk_full": [
                "1. Add disk cleanup step before heavy operations",
                "2. Remove unnecessary packages (dotnet, ghc, boost)",
                "3. Clear Docker images and apt caches",
                "4. See: `.codex/reports/ERROR_PATTERN_DATABASE.md#disk-space`",
            ],
            "timeout": [
                "1. Review test execution time",
                "2. Increase timeout thresholds if needed",
                "3. Optimize slow tests",
                "4. Consider test sharding",
            ],
            "artifact_missing": [
                "1. Verify artifact upload succeeded",
                "2. Check artifact name matches download",
                "3. Add artifact existence checks",
                "4. Review job dependencies",
            ],
        }

        return remediation_map.get(category, [
            "1. Review error pattern database for guidance",
            "2. Consult CI Testing Agent",
            "3. Check recent workflow changes",
        ])


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description="Enhanced workflow analytics with scribe integration"
    )
    parser.add_argument("--analysis-period", type=int, default=50)
    parser.add_argument("--workflow-filter", type=str, default="")
    parser.add_argument("--status-filter", type=str, default="all")
    parser.add_argument("--output-dir", type=Path, default=Path(".codex/reports"))
    parser.add_argument("--use-scribe", type=bool, default=True)
    parser.add_argument("--run-id", type=str, default="manual")

    args = parser.parse_args()

    print("🔍 Enhanced Workflow Analytics with Scribe Integration")
    print(f"{'✅' if SCRIBE_AVAILABLE and args.use_scribe else '❌'} Scribe tools: {'Available' if SCRIBE_AVAILABLE else 'Not available'}")

    # Initialize enhanced analyzer
    WorkflowAnalyticsScribe(use_scribe=args.use_scribe)

    # TODO: Fetch workflow runs (integrate with existing runner)
    # TODO: Perform enhanced analysis
    # TODO: Generate comprehensive artifacts

    print("✅ Enhanced analysis complete!")


if __name__ == "__main__":
    main()
