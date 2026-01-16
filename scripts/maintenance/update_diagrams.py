#! /usr/bin/env python3
"""
Update Diagrams

Purpose:
    Updates diagrams

Usage:
    python scripts/maintenance/update_diagrams.py [options]
    
    Examples:
    $ python scripts/maintenance/update_diagrams.py --help

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


"""
Automated Diagram and Visualization Update System

Systematically updates Mermaid diagrams, architecture visualizations,
and graphical representations to match current codebase state.

Usage:
    python scripts/maintenance/update_diagrams.py [--scan|--update|--validate]
    
    --scan      Scan and report all diagrams needing updates
    --update    Update diagrams with current information
    --validate  Validate diagram syntax and accuracy
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DiagramInfo:
    """Information about a diagram found in documentation."""
    file_path: Path
    diagram_type: str  # mermaid, plantuml, graphviz, etc.
    line_start: int
    line_end: int
    content: str
    last_updated: str = ""
    needs_update: bool = False
    update_reason: str = ""
    
@dataclass
class DiagramUpdateReport:
    """Report of diagram scanning and updates."""
    total_diagrams: int = 0
    diagrams_by_type: Dict[str, int] = field(default_factory=dict)
    diagrams_needing_update: List[DiagramInfo] = field(default_factory=list)
    diagrams_updated: List[DiagramInfo] = field(default_factory=list)
    validation_errors: List[Tuple[Path, str]] = field(default_factory=list)


class DiagramUpdater:
    """Automated diagram update system."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.report = DiagramUpdateReport()
        
        # Diagram type patterns
        self.diagram_patterns = {
            'mermaid': r'```mermaid\s*(.*?)```',
            'plantuml': r'```plantuml\s*(.*?)```',
            'graphviz': r'```(?:dot|graphviz)\s*(.*?)```',
            'ascii': r'```ascii\s*(.*?)```',
        }
        
        # Files to scan (exclude node_modules, .git, etc.)
        self.exclude_dirs = {'.git', 'node_modules', '__pycache__', '.pytest_cache', 
                            '.nox', 'htmlcov', 'dist', 'build', '.hypothesis'}
    
    def scan_diagrams(self) -> DiagramUpdateReport:
        """Scan repository for all diagrams."""
        print("🔍 Scanning repository for diagrams...")
        
        markdown_files = self._find_markdown_files()
        print(f"   Found {len(markdown_files)} markdown files")
        
        for md_file in markdown_files:
            self._scan_file_for_diagrams(md_file)
        
        print(f"\n📊 Scan Complete:")
        print(f"   Total diagrams: {self.report.total_diagrams}")
        for dtype, count in self.report.diagrams_by_type.items():
            print(f"   - {dtype}: {count}")
        
        return self.report
    
    def _find_markdown_files(self) -> List[Path]:
        """Find all markdown files in repository."""
        md_files = []
        for md_file in self.repo_root.rglob("*.md"):
            # Skip excluded directories
            if any(excl in md_file.parts for excl in self.exclude_dirs):
                continue
            md_files.append(md_file)
        return sorted(md_files)
    
    def _scan_file_for_diagrams(self, file_path: Path):
        """Scan a single file for diagrams."""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            for diagram_type, pattern in self.diagram_patterns.items():
                matches = re.finditer(pattern, content, re.DOTALL | re.MULTILINE)
                
                for match in matches:
                    diagram_content = match.group(0)
                    start_line = content[:match.start()].count('\n') + 1
                    end_line = content[:match.end()].count('\n') + 1
                    
                    diagram = DiagramInfo(
                        file_path=file_path,
                        diagram_type=diagram_type,
                        line_start=start_line,
                        line_end=end_line,
                        content=diagram_content
                    )
                    
                    # Check if diagram needs update
                    self._check_diagram_currency(diagram, file_path)
                    
                    self.report.total_diagrams += 1
                    self.report.diagrams_by_type[diagram_type] = \
                        self.report.diagrams_by_type.get(diagram_type, 0) + 1
                    
                    if diagram.needs_update:
                        self.report.diagrams_needing_update.append(diagram)
                        
        except (OSError, UnicodeDecodeError) as e:
            print(f"   ⚠️  Error reading {file_path}: {e}")
    
    def _check_diagram_currency(self, diagram: DiagramInfo, file_path: Path):
        """Check if diagram needs updating based on codebase state."""
        # Check for phase references
        if 'Phase' in diagram.content:
            # Check if phase status matches current state
            if self._phase_status_outdated(diagram.content):
                diagram.needs_update = True
                diagram.update_reason = "Phase status outdated"
        
        # Check for workflow diagrams
        if 'workflow' in str(file_path).lower() or 'workflow' in diagram.content.lower():
            if self._workflow_diagram_outdated(diagram.content):
                diagram.needs_update = True
                diagram.update_reason = "Workflow structure changed"
        
        # Check for architecture diagrams
        if 'architecture' in str(file_path).lower() or any(term in diagram.content.lower() 
                                                            for term in ['component', 'module', 'system']):
            if self._architecture_diagram_outdated(diagram.content):
                diagram.needs_update = True
                diagram.update_reason = "Architecture changed"
        
        # Check for coverage diagrams
        if 'coverage' in str(file_path).lower() or 'test' in diagram.content.lower():
            if '72%' not in diagram.content and 'coverage' in diagram.content.lower():
                diagram.needs_update = True
                diagram.update_reason = "Coverage percentage outdated"
    
    def _phase_status_outdated(self, content: str) -> bool:
        """Check if phase status in diagram is outdated."""
        # Known current states from CODEBASE_DASHBOARD.md
        current_phases = {
            'Phase 6': '100%',
            'Phase 7': '100%',
            'Phase 8': '100%',
            'Phase 9': '10%',
        }
        
        for phase, status in current_phases.items():
            if phase in content and status not in content:
                return True
        return False
    
    def _workflow_diagram_outdated(self, content: str) -> bool:
        """Check if workflow diagram reflects current workflows."""
        # Check for known workflow files
        workflows_dir = self.repo_root / '.github' / 'workflows'
        if not workflows_dir.exists():
            return False
        
        workflow_files = list(workflows_dir.glob('*.yml'))
        workflow_names = [f.stem for f in workflow_files if not f.stem.startswith('.')]
        
        # If diagram mentions workflows, check if they exist
        for name in workflow_names[:5]:  # Check first 5
            if name.replace('-', ' ') in content.lower():
                return False  # At least one current workflow found
        
        # If no current workflows found, might be outdated
        if 'workflow' in content.lower() and len(workflow_files) > 0:
            return True
        
        return False
    
    def _architecture_diagram_outdated(self, content: str) -> bool:
        """Check if architecture diagram matches current structure."""
        # Check for major components existence
        components_to_check = [
            ('src/codex', 'codex'),
            ('agents', 'agents'),
            ('scripts/mcp', 'mcp'),
            ('docs/system', 'cognitive brain'),
        ]
        
        missing_components = []
        for path, name in components_to_check:
            component_path = self.repo_root / path
            if component_path.exists() and name.lower() not in content.lower():
                missing_components.append(name)
        
        return len(missing_components) > 0
    
    def update_phase_status_diagram(self) -> str:
        """Generate updated phase status Mermaid diagram."""
        return """```mermaid
graph LR
    P6[Phase 6: MCP<br/>100% ✅] --> P7[Phase 7: Cognitive Brain<br/>100% ✅]
    P7 --> P8[Phase 8: Documentation<br/>100% ✅]
    P8 --> P9[Phase 9: Coverage<br/>10% 🔄]
    
    P9 --> P91[9.1: Critical Paths<br/>72% → 85%]
    P9 --> P92[9.2: Public APIs<br/>85% → 92%]
    P9 --> P93[9.3: Error Paths<br/>92% → 97%]
    P9 --> P94[9.4: Edge Cases<br/>97% → 100%]
    
    style P6 fill:#90EE90
    style P7 fill:#90EE90
    style P8 fill:#90EE90
    style P9 fill:#FFD700
    style P91 fill:#FFE4B5
    style P92 fill:#FFE4B5
    style P93 fill:#FFE4B5
    style P94 fill:#FFE4B5
```"""
    
    def update_architecture_diagram(self) -> str:
        """Generate updated architecture Mermaid diagram."""
        return """```mermaid
graph TB
    subgraph "Cognitive Brain"
        CB_MAP[Cognitive Map<br/>Architecture]
        CB_DASH[Dashboard<br/>Status]
        CB_ROAD[Roadmap<br/>Planning]
    end
    
    subgraph "Core Systems"
        CODEX[Codex Pipeline<br/>src/codex/]
        AGENTS[Agent System<br/>agents/]
        MCP[MCP Packaging<br/>scripts/mcp/]
    end
    
    subgraph "Infrastructure"
        TESTS[Test Suite<br/>1500+ tests]
        DOCS[Documentation<br/>212+ KB]
        CI[CI/CD<br/>7 workflows]
    end
    
    CB_MAP --> CODEX
    CB_MAP --> AGENTS
    CB_MAP --> MCP
    CB_DASH --> TESTS
    CB_DASH --> CI
    CB_ROAD --> DOCS
    
    AGENTS --> CODEX
    MCP --> AGENTS
    TESTS --> CODEX
    TESTS --> AGENTS
    CI --> TESTS
    
    style CB_MAP fill:#E6F3FF
    style CB_DASH fill:#E6F3FF
    style CB_ROAD fill:#E6F3FF
    style CODEX fill:#FFE6E6
    style AGENTS fill:#FFE6E6
    style MCP fill:#FFE6E6
    style TESTS fill:#E6FFE6
    style DOCS fill:#E6FFE6
    style CI fill:#E6FFE6
```"""
    
    def update_coverage_progress_diagram(self) -> str:
        """Generate updated coverage progress Mermaid diagram."""
        return """```mermaid
graph LR
    START[Current: 72%] --> P91[Phase 9.1<br/>85%]
    P91 --> P92[Phase 9.2<br/>92%]
    P92 --> P93[Phase 9.3<br/>97%]
    P93 --> TARGET[Target: 100% ✨]
    
    P91 -.150-200 tests.-> P91
    P92 -.100-150 tests.-> P92
    P93 -.80-120 tests.-> P93
    TARGET -.50-80 tests.-> TARGET
    
    style START fill:#FFB6C1
    style P91 fill:#FFD700
    style P92 fill:#90EE90
    style P93 fill:#90EE90
    style TARGET fill:#32CD32
```"""
    
    def generate_diagram_update_report(self) -> str:
        """Generate markdown report of diagram updates needed."""
        report_lines = [
            "# Diagram Update Report",
            f"\n**Generated**: {datetime.now().isoformat()}",
            f"\n## Summary",
            f"\n- Total diagrams found: {self.report.total_diagrams}",
            f"- Diagrams needing update: {len(self.report.diagrams_needing_update)}",
            f"- Diagrams by type:",
        ]
        
        for dtype, count in sorted(self.report.diagrams_by_type.items()):
            report_lines.append(f"  - {dtype}: {count}")
        
        if self.report.diagrams_needing_update:
            report_lines.append("\n## Diagrams Needing Updates\n")
            for diagram in self.report.diagrams_needing_update:
                rel_path = diagram.file_path.relative_to(self.repo_root)
                report_lines.append(f"### {rel_path}")
                report_lines.append(f"- **Type**: {diagram.diagram_type}")
                report_lines.append(f"- **Location**: Lines {diagram.line_start}-{diagram.line_end}")
                report_lines.append(f"- **Reason**: {diagram.update_reason}")
                report_lines.append("")
        
        report_lines.append("\n## Recommended Standard Diagrams\n")
        report_lines.append("### Phase Status Diagram")
        report_lines.append(self.update_phase_status_diagram())
        report_lines.append("\n### Architecture Diagram")
        report_lines.append(self.update_architecture_diagram())
        report_lines.append("\n### Coverage Progress Diagram")
        report_lines.append(self.update_coverage_progress_diagram())
        
        return "\n".join(report_lines)
    
    def validate_mermaid_syntax(self, content: str) -> Tuple[bool, str]:
        """Validate Mermaid diagram syntax (basic check)."""
        # Basic syntax validation
        if not content.strip():
            return False, "Empty diagram"
        
        # Check for required elements
        if 'graph' not in content.lower() and 'sequenceDiagram' not in content:
            return False, "Missing graph or sequenceDiagram declaration"
        
        # Check for balanced brackets
        if content.count('[') != content.count(']'):
            return False, "Unbalanced square brackets"
        
        if content.count('(') != content.count(')'):
            return False, "Unbalanced parentheses"
        
        return True, "Valid"


def main():
    parser = argparse.ArgumentParser(description='Update repository diagrams systematically')
    parser.add_argument('--scan', action='store_true', help='Scan for diagrams')
    parser.add_argument('--update', action='store_true', help='Update diagrams')
    parser.add_argument('--validate', action='store_true', help='Validate diagram syntax')
    parser.add_argument('--output', type=str, default='docs/maintenance/DIAGRAM_UPDATE_REPORT.md',
                       help='Output file for report')
    
    args = parser.parse_args()
    
    repo_root = Path(__file__).resolve().parents[2]
    updater = DiagramUpdater(repo_root)
    
    if args.validate:
        print("✅ Validation feature coming soon")
        return 0
    
    if args.update:
        print("🔄 Automatic update feature coming soon")
        print("   For now, use the generated report to update manually")
        return 0
    
    # Default action: scan (when --scan is passed or no other flags)
    report = updater.scan_diagrams()
    
    # Generate report
    report_content = updater.generate_diagram_update_report()
    output_path = repo_root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report_content)
    
    print(f"\n📄 Report saved to: {output_path}")
    print(f"\n💡 Next steps:")
    print(f"   1. Review {output_path}")
    print(f"   2. Update diagrams manually or run with --update")
    print(f"   3. Validate with --validate")
    
    return 0 if len(report.diagrams_needing_update) == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
