#!/usr/bin/env python3
"""
Add accessibility titles to all Mermaid diagrams in documentation.

This script scans for Mermaid code blocks and adds descriptive accessibility
titles using the init directive format.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple

class MermaidAltTextProcessor:
    """Process Mermaid diagrams to add accessibility titles."""

    # Map diagram patterns to descriptive titles
    DIAGRAM_PATTERNS = {
        r'graph\s+(TD|LR|BT|RL)': 'Flowchart',
        r'sequenceDiagram': 'Sequence Diagram',
        r'classDiagram': 'Class Diagram',
        r'stateDiagram': 'State Diagram',
        r'erDiagram': 'Entity Relationship Diagram',
        r'pie\s+title': 'Pie Chart',
        r'%%{init:.*%%': 'Diagram Configuration',
        r'flowchart': 'Flowchart',
        r'mindmap': 'Mind Map',
        r'timeline': 'Timeline',
        r'gitGraph': 'Git Graph',
        r'journey': 'User Journey',
        r'xychart-beta': 'XY Chart',
    }

    def __init__(self, docs_dir: str = "docs"):
        self.docs_dir = Path(docs_dir)
        self.processed_files: List[str] = []
        self.diagrams_with_alt: int = 0
        self.diagrams_without_alt: int = 0
        self.samples: List[Dict] = []

    def extract_diagram_type(self, diagram_code: str) -> str:
        """Determine the type of Mermaid diagram."""
        lines = diagram_code.strip().split('\n')
        for line in lines[:5]:  # Check first 5 lines
            for pattern, diagram_type in self.DIAGRAM_PATTERNS.items():
                if re.search(pattern, line, re.IGNORECASE):
                    return diagram_type
        return 'Diagram'

    def generate_descriptive_title(self, diagram_code: str, file_path: str) -> str:
        """Generate a descriptive title based on diagram content."""
        diagram_type = self.extract_diagram_type(diagram_code)
        
        # Extract key entities/nodes
        nodes = re.findall(r'\[([^\]]+)\]', diagram_code)
        labels = re.findall(r'--+\s*([^-]+)\s*-+', diagram_code)
        
        entities = nodes[:3] if nodes else []
        entity_text = ', '.join(entities[:2]) if entities else ''
        
        if entity_text:
            return f"{diagram_type} showing {entity_text}"
        elif labels:
            action = labels[0].strip()[:30]
            return f"{diagram_type}: {action}"
        else:
            return diagram_type

    def has_accessibility_title(self, diagram_block: str) -> bool:
        """Check if diagram already has accessibility title."""
        return "'accessibility'" in diagram_block or "'title'" in diagram_block

    def add_accessibility_title(self, diagram_block: str, alt_text: str) -> str:
        """Add accessibility title to diagram block."""
        if self.has_accessibility_title(diagram_block):
            return diagram_block
        
        # Extract code block parts
        lines = diagram_block.split('\n')
        opening = lines[0]  # ```mermaid
        code_lines = lines[1:-1]  # diagram code
        closing = lines[-1]  # ```
        
        # Check for existing init directive
        init_pattern = r"%%{init:\s*\{([^}]+)\}\s*\}%%"
        has_init = False
        
        for i, line in enumerate(code_lines):
            if re.search(init_pattern, line):
                # Add to existing init
                match = re.search(init_pattern, line)
                if match:
                    existing = match.group(1)
                    new_init = "%%{init: {" + existing + ", 'accessibility': {'title': '" + alt_text + "'}}%%"
                    code_lines[i] = new_init
                    has_init = True
                    break
        
        if not has_init:
            # Add new init directive at start
            init_line = "%%{init: {'accessibility': {'title': '" + alt_text + "'}}%%"
            code_lines.insert(0, init_line)
        
        return '\n'.join([opening] + code_lines + [closing])

    def process_file(self, file_path: Path) -> Tuple[int, int]:
        """Process a single markdown file."""
        if not file_path.is_file() or file_path.suffix != '.md':
            return 0, 0
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, OSError):
            return 0, 0
        
        # Find all mermaid blocks
        pattern = r'```mermaid\n(.*?)```'
        matches = list(re.finditer(pattern, content, re.DOTALL))
        
        if not matches:
            return 0, 0
        
        with_alt = 0
        without_alt = 0
        updated_content = content
        
        for match in reversed(matches):  # Process in reverse to maintain positions
            diagram_block = match.group(0)
            diagram_code = match.group(1)
            
            if self.has_accessibility_title(diagram_block):
                with_alt += 1
            else:
                without_alt += 1
                alt_text = self.generate_descriptive_title(diagram_code, str(file_path))
                new_block = self.add_accessibility_title(diagram_block, alt_text)
                
                # Store sample for report
                if len(self.samples) < 5:
                    self.samples.append({
                        'file': str(file_path.relative_to(self.docs_dir)),
                        'original': diagram_block[:100],
                        'alt_text': alt_text,
                        'updated': new_block[:150]
                    })
                
                updated_content = updated_content[:match.start()] + new_block + updated_content[match.end():]
        
        if without_alt > 0:
            try:
                file_path.write_text(updated_content, encoding='utf-8')
                self.processed_files.append(str(file_path.relative_to(self.docs_dir)))
            except OSError:
                pass
        
        self.diagrams_with_alt += with_alt
        self.diagrams_without_alt += without_alt
        
        return with_alt, without_alt

    def process_all(self) -> Dict:
        """Process all markdown files in docs directory."""
        for file_path in self.docs_dir.rglob('*.md'):
            self.process_file(file_path)
        
        return {
            'total_diagrams': self.diagrams_with_alt + self.diagrams_without_alt,
            'with_alt_text': self.diagrams_with_alt,
            'without_alt_text': self.diagrams_without_alt,
            'files_processed': len(self.processed_files),
            'files_modified': len(self.processed_files),
            'samples': self.samples
        }

    def generate_report(self) -> str:
        """Generate accessibility report."""
        stats = self.process_all()
        
        report = f"""# Mermaid Diagram Accessibility Report

## Summary
- **Total Mermaid Diagrams:** {stats['total_diagrams']}
- **Diagrams with Alt Text:** {stats['with_alt_text']}
- **Diagrams without Alt Text (Fixed):** {stats['without_alt_text']}
- **Files Modified:** {stats['files_modified']}

## Processing Status
✅ All {stats['total_diagrams']} Mermaid diagrams have been processed
✅ Alt text added to {stats['without_alt_text']} diagrams
✅ {stats['files_modified']} files updated

## Sample Improvements
"""
        for i, sample in enumerate(stats['samples'], 1):
            report += f"\n### Example {i}: {sample['file']}\n"
            report += f"**Alt Text Added:** {sample['alt_text']}\n"
        
        return report


if __name__ == '__main__':
    import sys
    
    docs_dir = sys.argv[1] if len(sys.argv) > 1 else 'docs'
    processor = MermaidAltTextProcessor(docs_dir)
    stats = processor.process_all()
    
    print(processor.generate_report())
    print(f"\n✅ Processing complete: {stats['without_alt_text']} diagrams updated")
