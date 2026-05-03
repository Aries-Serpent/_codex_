#!/usr/bin/env python3
"""
Project Architect Researcher Agent

Generates research artifacts and documentation for AI knowledge platforms like
NotebookLM, providing structured sources for research and architecture analysis.

Usage:
    python -m project_architect_researcher --source-dir ./docs --output ./artifacts
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import click
import yaml


@dataclass
class NotebookLMSource:
    """Represents a research source document."""
    title: str
    content: str
    source_type: str  # 'markdown', 'text', 'json'
    metadata: dict[str, Any]
    citations: list[str]
    created_at: str


@dataclass
class ResearchArtifact:
    """Represents a complete research artifact."""
    artifact_id: str
    title: str
    sources: list[NotebookLMSource]
    summary: str
    tags: list[str]
    created_at: str


class ProjectArchitectResearcher:
    """
    Main agent for generating research artifacts and documentation.

    Capabilities:
    - Parse documentation and code files
    - Extract structured information
    - Generate research sources
    - Create artifacts for AI platforms
    - Export in multiple formats
    """

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize researcher with optional config."""
        self.config = self._load_config(config_path)
        self.artifacts: list[ResearchArtifact] = []

    def _load_config(self, config_path: Optional[Path]) -> dict:
        """Load researcher configuration."""
        if config_path and config_path.exists():
            with open(config_path) as f:
                return yaml.safe_load(f)
        return self._default_config()

    def _default_config(self) -> dict:
        """Return default configuration."""
        return {
            'version': '1.0.0',
            'enabled': True,
            'source_types': ['markdown', 'text', 'json', 'yaml'],
            'max_source_size_kb': 1024,
            'include_metadata': True,
            'export_formats': ['json', 'markdown', 'yaml'],
        }

    def parse_file(self, filepath: Path) -> Optional[NotebookLMSource]:
        """
        Parse a file and create a research source.

        Args:
            filepath: Path to file to parse

        Returns:
            NotebookLMSource if successful, None if error
        """
        try:
            # Check file size
            file_size_kb = filepath.stat().st_size / 1024
            if file_size_kb > self.config['max_source_size_kb']:
                click.echo(f"Skipping {filepath}: too large ({file_size_kb:.1f}KB)")
                return None

            content = filepath.read_text(encoding='utf-8', errors='ignore')

            # Determine source type
            suffix = filepath.suffix.lower()
            source_type_map = {
                '.md': 'markdown',
                '.txt': 'text',
                '.json': 'json',
                '.yaml': 'yaml',
                '.yml': 'yaml',
            }
            source_type = source_type_map.get(suffix, 'text')

            # Extract metadata
            metadata = {
                'file_path': str(filepath),
                'file_size_kb': round(file_size_kb, 2),
                'file_type': source_type,
                'modified_at': datetime.fromtimestamp(
                    filepath.stat().st_mtime,
                    tz=timezone.utc
                ).isoformat(),
            }

            # Extract citations (basic implementation)
            citations = self._extract_citations(content)

            return NotebookLMSource(
                title=filepath.name,
                content=content,
                source_type=source_type,
                metadata=metadata,
                citations=citations,
                created_at=datetime.now(timezone.utc).isoformat()
            )


        except Exception as e:
            click.echo(f"Error parsing {filepath}: {e}", err=True)
            return None

    def _extract_citations(self, content: str) -> list[str]:
        """Extract citations/references from content."""
        citations = []

        # Look for markdown links
        import re
        link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        for match in re.finditer(link_pattern, content):
            citations.append(match.group(2))

        return citations[:20]  # Limit to 20 citations

    def scan_directory(
        self,
        directory: Path,
        recursive: bool = True
    ) -> list[NotebookLMSource]:
        """
        Scan a directory for documentation files.

        Args:
            directory: Directory to scan
            recursive: Whether to scan recursively

        Returns:
            List of NotebookLMSource objects
        """
        sources = []

        # Patterns to match
        patterns = ['*.md', '*.txt', '*.json', '*.yaml', '*.yml']

        for pattern in patterns:
            glob_pattern = f'**/{pattern}' if recursive else pattern
            for filepath in directory.glob(glob_pattern):
                source = self.parse_file(filepath)
                if source:
                    sources.append(source)

        return sources

    def create_artifact(
        self,
        title: str,
        sources: list[NotebookLMSource],
        tags: Optional[list[str]] = None
    ) -> ResearchArtifact:
        """
        Create a research artifact from sources.

        Args:
            title: Artifact title
            sources: List of sources
            tags: Optional tags

        Returns:
            ResearchArtifact object
        """
        # Generate summary
        total_size = sum(len(s.content) for s in sources)
        summary = f"Research artifact with {len(sources)} sources, {total_size:,} characters"

        artifact = ResearchArtifact(
            artifact_id=f"artifact_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            title=title,
            sources=sources,
            summary=summary,
            tags=tags or [],
            created_at=datetime.now(timezone.utc).isoformat()
        )

        self.artifacts.append(artifact)
        return artifact

    def export_artifact(
        self,
        artifact: ResearchArtifact,
        output_path: Path,
        format: str = 'json'
    ) -> Path:
        """
        Export artifact to file.

        Args:
            artifact: Artifact to export
            output_path: Output file path
            format: Export format ('json', 'markdown', 'yaml')

        Returns:
            Path to exported file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format == 'json':
            data = {
                'artifact_id': artifact.artifact_id,
                'title': artifact.title,
                'summary': artifact.summary,
                'tags': artifact.tags,
                'created_at': artifact.created_at,
                'sources': [asdict(s) for s in artifact.sources]
            }
            output_path.write_text(json.dumps(data, indent=2))

        elif format == 'markdown':
            md_content = f"# {artifact.title}\n\n"
            md_content += f"**Created**: {artifact.created_at}\n"
            md_content += f"**Summary**: {artifact.summary}\n"
            md_content += f"**Tags**: {', '.join(artifact.tags)}\n\n"
            md_content += "## Sources\n\n"

            for i, source in enumerate(artifact.sources, 1):
                md_content += f"### {i}. {source.title}\n\n"
                md_content += f"- **Type**: {source.source_type}\n"
                md_content += f"- **Size**: {source.metadata.get('file_size_kb', 0):.1f}KB\n"
                if source.citations:
                    md_content += f"- **Citations**: {len(source.citations)}\n"
                md_content += f"\n```\n{source.content[:500]}...\n```\n\n"

            output_path.write_text(md_content)

        elif format == 'yaml':
            data = {
                'artifact_id': artifact.artifact_id,
                'title': artifact.title,
                'summary': artifact.summary,
                'tags': artifact.tags,
                'created_at': artifact.created_at,
                'sources': [asdict(s) for s in artifact.sources]
            }
            output_path.write_text(yaml.dump(data, default_flow_style=False))

        return output_path

    def generate_report(self, artifacts: list[ResearchArtifact]) -> dict:
        """Generate summary report of artifacts."""
        total_sources = sum(len(a.sources) for a in artifacts)
        total_content = sum(
            sum(len(s.content) for s in a.sources)
            for a in artifacts
        )

        return {
            'total_artifacts': len(artifacts),
            'total_sources': total_sources,
            'total_content_chars': total_content,
            'avg_sources_per_artifact': total_sources / len(artifacts) if artifacts else 0,
            'artifacts_by_tag': self._count_by_tags(artifacts),
        }

    def _count_by_tags(self, artifacts: list[ResearchArtifact]) -> dict[str, int]:
        """Count artifacts by tag."""
        tag_counts = {}
        for artifact in artifacts:
            for tag in artifact.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        return tag_counts


@click.command()
@click.option('--source-dir', type=click.Path(exists=True), required=True, help='Source directory')
@click.option('--output', type=click.Path(), default='./artifacts', help='Output directory')
@click.option('--title', default='Research Artifact', help='Artifact title')
@click.option('--tags', default='', help='Comma-separated tags')
@click.option('--format', type=click.Choice(['json', 'markdown', 'yaml']), default='json', help='Export format')
@click.option('--recursive/--no-recursive', default=True, help='Scan recursively')
@click.option('--report', is_flag=True, help='Show summary report')
def main(source_dir, output, title, tags, format, recursive, report):
    """Project Architect Researcher CLI"""
    researcher = ProjectArchitectResearcher()

    # Scan for sources
    click.echo(f"Scanning {source_dir} for documentation...")
    sources = researcher.scan_directory(Path(source_dir), recursive=recursive)
    click.echo(f"Found {len(sources)} sources")

    if not sources:
        click.echo("No sources found.")
        return

    # Create artifact
    tag_list = [t.strip() for t in tags.split(',') if t.strip()]
    artifact = researcher.create_artifact(title, sources, tag_list)

    # Export
    output_path = Path(output) / f"{artifact.artifact_id}.{format}"
    exported = researcher.export_artifact(artifact, output_path, format)
    click.echo(f"Exported to: {exported}")

    # Show report
    if report:
        report_data = researcher.generate_report([artifact])
        click.echo("\n=== Summary Report ===")
        click.echo(f"Total artifacts: {report_data['total_artifacts']}")
        click.echo(f"Total sources: {report_data['total_sources']}")
        click.echo(f"Total content: {report_data['total_content_chars']:,} characters")


if __name__ == '__main__':
    main()
