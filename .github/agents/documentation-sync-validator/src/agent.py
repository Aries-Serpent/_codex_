#!/usr/bin/env python3
"""
Documentation Sync Validator Agent

Automatically validate documentation synchronization with codebase, detect semantic
drift between code and docs, and ensure schema compliance.

Component Reuse Strategy:
- Base: doc-freshness-checker (75% reuse)
- Extension 1: semantic-search (semantic matching)
- Extension 2: config-validator (schema validation)

Usage:
    python -m documentation_sync_validator.src.agent validate --all
    python -m documentation_sync_validator.src.agent check-freshness docs/
    python -m documentation_sync_validator.src.agent semantic-check src/ docs/
"""

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml


class DriftSeverity(Enum):
    """Severity levels for documentation drift"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FreshnessStatus(Enum):
    """Documentation freshness status"""
    FRESH = "fresh"  # <30 days
    AGING = "aging"  # 30-90 days
    STALE = "stale"  # >90 days


@dataclass
class DocumentationIssue:
    """Represents a detected documentation issue"""
    file_path: Path
    issue_type: str  # 'freshness', 'semantic_drift', 'broken_link', 'schema_violation'
    severity: DriftSeverity
    description: str
    line_number: Optional[int] = None
    suggested_fix: Optional[str] = None
    confidence: float = 1.0


@dataclass
class FreshnessReport:
    """Report on documentation freshness"""
    file_path: Path
    last_modified: datetime
    age_days: int
    status: FreshnessStatus
    related_code_files: List[Path] = field(default_factory=list)


@dataclass
class SemanticDriftReport:
    """Report on semantic drift between code and documentation"""
    doc_file: Path
    code_file: Path
    similarity_score: float  # 0.0 to 1.0
    drift_severity: DriftSeverity
    mismatched_concepts: List[str] = field(default_factory=list)


class DocumentationSyncValidator:
    """Main agent class for documentation synchronization validation"""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the agent with optional configuration"""
        self.config = self._load_config(config_path)
        self.freshness_threshold_days = self.config.get('freshness_threshold_days', 90)
        self.semantic_drift_threshold = self.config.get('semantic_drift_threshold', 0.7)
        self.link_check_timeout = self.config.get('link_check_timeout', 10)
        self.issues: List[DocumentationIssue] = []

    def _load_config(self, config_path: Optional[Path]) -> Dict:
        """Load agent configuration from YAML file"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "agent_config.yaml"

        if not config_path.exists():
            return self._default_config()

        with open(config_path) as f:
            return yaml.safe_load(f)

    def _default_config(self) -> Dict:
        """Return default configuration"""
        return {
            'version': '1.0.0',
            'agent_name': 'documentation-sync-validator',
            'capabilities': [
                'check_freshness',
                'validate_links',
                'detect_semantic_drift',
                'validate_schema'
            ],
            'freshness_threshold_days': 90,
            'semantic_drift_threshold': 0.7,
            'link_check_timeout': 10,
            'settings': {
                'timeout_seconds': 300,
                'max_retries': 3,
                'log_level': 'INFO',
                'enable_caching': True
            }
        }

    def validate_all(self, root_dir: Path) -> List[DocumentationIssue]:
        """
        Perform comprehensive validation of all documentation.

        Args:
            root_dir: Root directory to search for documentation

        Returns:
            List of detected issues
        """
        self.issues = []

        # Find all documentation files
        doc_files = self._find_documentation_files(root_dir)

        # Check freshness
        for doc_file in doc_files:
            freshness_report = self.check_freshness(doc_file)
            if freshness_report.status != FreshnessStatus.FRESH:
                self.issues.append(DocumentationIssue(
                    file_path=doc_file,
                    issue_type='freshness',
                    severity=self._freshness_to_severity(freshness_report.status),
                    description=f"Documentation is {freshness_report.status.value} ({freshness_report.age_days} days old)"
                ))

        # Validate links
        for doc_file in doc_files:
            broken_links = self.validate_links(doc_file)
            for link, reason in broken_links:
                self.issues.append(DocumentationIssue(
                    file_path=doc_file,
                    issue_type='broken_link',
                    severity=DriftSeverity.MEDIUM,
                    description=f"Broken link: {link} - {reason}"
                ))

        # Check semantic drift (if code directory provided)
        code_dir = root_dir / "src"
        if code_dir.exists():
            for doc_file in doc_files:
                drift_reports = self.detect_semantic_drift(doc_file, code_dir)
                for report in drift_reports:
                    if report.drift_severity != DriftSeverity.NONE:
                        self.issues.append(DocumentationIssue(
                            file_path=doc_file,
                            issue_type='semantic_drift',
                            severity=report.drift_severity,
                            description=f"Semantic drift detected with {report.code_file} (similarity: {report.similarity_score:.2f})",
                            confidence=report.similarity_score
                        ))

        return self.issues

    def _find_documentation_files(self, root_dir: Path) -> List[Path]:
        """
        Find all documentation files in the directory tree.

        Args:
            root_dir: Root directory to search

        Returns:
            List of documentation file paths
        """
        doc_patterns = ['**/*.md', '**/*.rst', '**/*.txt']
        exclude_patterns = ['node_modules', '.git', '__pycache__', '.venv', 'venv']

        doc_files = []
        for pattern in doc_patterns:
            for file_path in root_dir.glob(pattern):
                # Exclude certain directories
                if any(exclude in str(file_path) for exclude in exclude_patterns):
                    continue
                doc_files.append(file_path)

        return doc_files

    def check_freshness(self, doc_file: Path) -> FreshnessReport:
        """
        Check documentation freshness based on last modification time.

        Args:
            doc_file: Path to documentation file

        Returns:
            FreshnessReport with status and age
        """
        if not doc_file.exists():
            raise FileNotFoundError(f"Documentation file not found: {doc_file}")

        # Get last modification time
        mtime = doc_file.stat().st_mtime
        last_modified = datetime.fromtimestamp(mtime, tz=timezone.utc)

        # Calculate age
        now = datetime.now(timezone.utc)
        age_days = (now - last_modified).days

        # Determine status
        if age_days < 30:
            status = FreshnessStatus.FRESH
        elif age_days < self.freshness_threshold_days:
            status = FreshnessStatus.AGING
        else:
            status = FreshnessStatus.STALE

        return FreshnessReport(
            file_path=doc_file,
            last_modified=last_modified,
            age_days=age_days,
            status=status
        )

    def validate_links(self, doc_file: Path) -> List[Tuple[str, str]]:
        """
        Validate all links in a documentation file.

        Args:
            doc_file: Path to documentation file

        Returns:
            List of (broken_link, reason) tuples
        """
        if not doc_file.exists():
            raise FileNotFoundError(f"Documentation file not found: {doc_file}")

        broken_links = []

        with open(doc_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract markdown links: [text](url)
        markdown_links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)

        # Extract HTML links: <a href="url">
        html_links = re.findall(r'<a[^>]+href=["\']([^"\']+)["\']', content)

        # Combine all links
        all_links = [url for _, url in markdown_links] + html_links

        for link in all_links:
            # Skip anchor links
            if link.startswith('#'):
                continue

            # Check internal links (relative paths)
            if not link.startswith(('http://', 'https://', 'ftp://')):
                # Resolve relative to doc file location
                link_path = (doc_file.parent / link).resolve()
                if not link_path.exists():
                    broken_links.append((link, "File not found"))

            # External links would require network requests (skipped for now in basic implementation)
            # In production, use requests library with timeout

        return broken_links

    def detect_semantic_drift(
        self,
        doc_file: Path,
        code_dir: Path
    ) -> List[SemanticDriftReport]:
        """
        Detect semantic drift between documentation and code.

        This is a simplified implementation. In production, this would use
        vector embeddings and semantic similarity from the semantic-search component.

        Args:
            doc_file: Path to documentation file
            code_dir: Directory containing source code

        Returns:
            List of semantic drift reports
        """
        drift_reports = []

        # Read documentation content
        with open(doc_file, 'r', encoding='utf-8') as f:
            doc_content = f.read()

        # Extract concepts from documentation (simplified: just words)
        doc_concepts = set(re.findall(r'\b[a-z_][a-z0-9_]{2,}\b', doc_content.lower()))

        # Find related code files (heuristic: similar names)
        doc_stem = doc_file.stem.lower()
        related_code_files = []

        for code_file in code_dir.rglob('*.py'):
            if doc_stem in code_file.stem.lower():
                related_code_files.append(code_file)

        # Check semantic similarity with related files
        for code_file in related_code_files:
            with open(code_file, 'r', encoding='utf-8') as f:
                code_content = f.read()

            # Extract concepts from code (simplified: identifiers)
            code_concepts = set(re.findall(r'\b[a-z_][a-z0-9_]{2,}\b', code_content.lower()))

            # Calculate Jaccard similarity
            intersection = len(doc_concepts & code_concepts)
            union = len(doc_concepts | code_concepts)
            similarity = intersection / union if union > 0 else 0.0

            # Determine drift severity
            if similarity >= self.semantic_drift_threshold:
                severity = DriftSeverity.NONE
            elif similarity >= 0.5:
                severity = DriftSeverity.LOW
            elif similarity >= 0.3:
                severity = DriftSeverity.MEDIUM
            elif similarity >= 0.1:
                severity = DriftSeverity.HIGH
            else:
                severity = DriftSeverity.CRITICAL

            # Find mismatched concepts (in code but not in docs)
            mismatched = list(code_concepts - doc_concepts)[:10]  # Top 10

            drift_reports.append(SemanticDriftReport(
                doc_file=doc_file,
                code_file=code_file,
                similarity_score=similarity,
                drift_severity=severity,
                mismatched_concepts=mismatched
            ))

        return drift_reports

    def validate_schema(self, doc_file: Path, schema: Dict) -> List[DocumentationIssue]:
        """
        Validate documentation against a schema.

        This integrates with the config-validator component for schema validation.

        Args:
            doc_file: Path to documentation file
            schema: Schema definition (YAML/JSON)

        Returns:
            List of schema validation issues
        """
        issues = []

        # Read documentation frontmatter (if present)
        with open(doc_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract YAML frontmatter (between --- markers)
        frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not frontmatter_match:
            issues.append(DocumentationIssue(
                file_path=doc_file,
                issue_type='schema_violation',
                severity=DriftSeverity.LOW,
                description="No frontmatter found"
            ))
            return issues

        try:
            frontmatter = yaml.safe_load(frontmatter_match.group(1))
        except yaml.YAMLError as e:
            issues.append(DocumentationIssue(
                file_path=doc_file,
                issue_type='schema_violation',
                severity=DriftSeverity.HIGH,
                description=f"Invalid YAML frontmatter: {e}"
            ))
            return issues

        # Validate required fields from schema
        required_fields = schema.get('required', [])
        for field_name in required_fields:
            if field_name not in frontmatter:
                issues.append(DocumentationIssue(
                    file_path=doc_file,
                    issue_type='schema_violation',
                    severity=DriftSeverity.MEDIUM,
                    description=f"Missing required field: {field_name}",
                    suggested_fix=f"Add '{field}: <value>' to frontmatter"
                ))

        return issues

    def _freshness_to_severity(self, status: FreshnessStatus) -> DriftSeverity:
        """Convert freshness status to drift severity"""
        mapping = {
            FreshnessStatus.FRESH: DriftSeverity.NONE,
            FreshnessStatus.AGING: DriftSeverity.LOW,
            FreshnessStatus.STALE: DriftSeverity.MEDIUM
        }
        return mapping.get(status, DriftSeverity.LOW)

    def generate_report(self, output_format: str = 'text') -> str:
        """
        Generate a human-readable report of all issues.

        Args:
            output_format: 'text', 'json', or 'markdown'

        Returns:
            Formatted report string
        """
        if output_format == 'json':
            import json
            return json.dumps([
                {
                    'file': str(issue.file_path),
                    'type': issue.issue_type,
                    'severity': issue.severity.value,
                    'description': issue.description,
                    'line': issue.line_number,
                    'confidence': issue.confidence
                }
                for issue in self.issues
            ], indent=2)

        if output_format == 'markdown':
            lines = ['# Documentation Validation Report\n']
            lines.append(f'**Total Issues**: {len(self.issues)}\n')

            by_severity = {}
            for issue in self.issues:
                by_severity.setdefault(issue.severity, []).append(issue)

            for severity in DriftSeverity:
                issues = by_severity.get(severity, [])
                if issues:
                    lines.append(f'\n## {severity.value.upper()} ({len(issues)})\n')
                    for issue in issues:
                        lines.append(f'- **{issue.file_path.name}**: {issue.description}')

            return '\n'.join(lines)

        # text
        lines = ['Documentation Validation Report']
        lines.append('=' * 50)
        lines.append(f'Total Issues: {len(self.issues)}\n')

        for issue in self.issues:
            lines.append(f'[{issue.severity.value.upper()}] {issue.file_path}')
            lines.append(f'  Type: {issue.issue_type}')
            lines.append(f'  {issue.description}')
            if issue.suggested_fix:
                lines.append(f'  Fix: {issue.suggested_fix}')
            lines.append('')

        return '\n'.join(lines)


def main():
    """CLI entry point"""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description='Documentation Sync Validator Agent'
    )
    parser.add_argument(
        'command',
        choices=['validate', 'check-freshness', 'validate-links', 'semantic-check'],
        help='Command to execute'
    )
    parser.add_argument(
        'path',
        type=Path,
        help='Path to documentation or root directory'
    )
    parser.add_argument(
        '--code-dir',
        type=Path,
        help='Path to code directory for semantic checking'
    )
    parser.add_argument(
        '--output-format',
        choices=['text', 'json', 'markdown'],
        default='text',
        help='Output format'
    )
    parser.add_argument(
        '--config',
        type=Path,
        help='Path to configuration file'
    )

    args = parser.parse_args()

    # Initialize agent
    agent = DocumentationSyncValidator(config_path=args.config)

    # Execute command
    if args.command == 'validate':
        issues = agent.validate_all(args.path)
        print(agent.generate_report(args.output_format))
        sys.exit(1 if issues else 0)

    elif args.command == 'check-freshness':
        report = agent.check_freshness(args.path)
        print(f'{args.path}: {report.status.value} ({report.age_days} days)')
        sys.exit(1 if report.status == FreshnessStatus.STALE else 0)

    elif args.command == 'validate-links':
        broken = agent.validate_links(args.path)
        if broken:
            print(f'Found {len(broken)} broken links:')
            for link, reason in broken:
                print(f'  - {link}: {reason}')
            sys.exit(1)
        else:
            print('All links valid')
            sys.exit(0)

    elif args.command == 'semantic-check':
        if not args.code_dir:
            print('Error: --code-dir required for semantic-check')
            sys.exit(1)
        reports = agent.detect_semantic_drift(args.path, args.code_dir)
        for report in reports:
            print(f'{report.code_file}: {report.drift_severity.value} (similarity: {report.similarity_score:.2f})')
        sys.exit(0)


if __name__ == '__main__':
    main()
