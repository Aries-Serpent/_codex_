#! /usr/bin/env python3
"""
AfterMath Session Parser

Extracts structured aftermath blocks from GitHub logs and PR comments,
generating durable lessons learned artifacts.

Usage:
    python scripts/aftermath/parse_session.py --source=file.md --output=.codex/lessons_learned/
"""

import argparse
import re
import sys
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class AftermathParser:
    """Parser for aftermath blocks in Copilot session logs."""
    
    def __init__(self):
        self.fenced_pattern = re.compile(
            r'```aftermath\n(.*?)\n```',
            re.DOTALL | re.MULTILINE
        )
        self.inline_pattern = re.compile(
            r'<!--AFTERMATH:(.*?)-->',
            re.MULTILINE
        )
    
    def parse_fenced_block(self, content: str) -> Optional[Dict]:
        """Extract YAML from fenced aftermath block."""
        match = self.fenced_pattern.search(content)
        if not match:
            return None
        
        try:
            data = yaml.safe_load(match.group(1))
            return data
        except yaml.YAMLError as e:
            print(f"YAML parse error: {e}", file=sys.stderr)
            return None
    
    def parse_inline_tags(self, content: str) -> Optional[Dict]:
        """Extract data from inline aftermath tags."""
        matches = self.inline_pattern.findall(content)
        if not matches:
            return None
        
        data = {
            'meta': {},
            'lessons': [],
            'decisions': [],
            'metrics': {},
            'quality': {},
            'blockers': [],
            'next_steps': [],
            'future_research': []
        }
        
        for match in matches:
            if '=' in match:
                key, value = match.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"')
                
                if key == 'SESSION_ID':
                    data['meta']['session_id'] = value
                elif key.startswith('LESSON_'):
                    data['lessons'].append({'title': value})
                elif key.startswith('DECISION_'):
                    data['decisions'].append({'what': value})
                elif key.startswith('FUTURE_RESEARCH_') and not key.endswith('_COUNT'):
                    data['future_research'].append({'topic': value})
                elif key.startswith('METRICS:'):
                    metric_name = key.split(':', 1)[1].lower()
                    data['metrics'][metric_name] = value
                elif key.startswith('QUALITY:'):
                    quality_name = key.split(':', 1)[1].lower()
                    data['quality'][quality_name] = value
                elif key == 'STATUS':
                    data['status'] = value
        
        return data if data['meta'] else None
    
    def parse_file(self, file_path: Path) -> Optional[Dict]:
        """Parse aftermath data from a file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Try fenced block first
            data = self.parse_fenced_block(content)
            if data:
                return data
            
            # Fallback to inline tags
            data = self.parse_inline_tags(content)
            if data:
                return data
            
            print(f"No aftermath data found in {file_path}", file=sys.stderr)
            return None
            
        except (OSError, UnicodeDecodeError) as e:
            print(f"Error reading {file_path}: {e}", file=sys.stderr)
            return None
    
    def validate_schema(self, data: Dict) -> List[str]:
        """Validate aftermath data schema."""
        errors = []
        
        # Required top-level keys (future_research is optional)
        required_keys = ['meta', 'lessons', 'decisions', 'metrics', 'quality', 'next_steps']
        for key in required_keys:
            if key not in data:
                errors.append(f"Missing required key: {key}")
        
        # Validate meta
        if 'meta' in data:
            meta_required = ['session_id', 'started_at', 'finished_at', 'context']
            for key in meta_required:
                if key not in data['meta']:
                    errors.append(f"Missing meta.{key}")
        
        return errors
    
    def save_lessons_learned(self, data: Dict, output_dir: Path):
        """Save lessons learned to cumulative file."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        session_id = data.get('meta', {}).get('session_id', 'unknown')
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        
        # Save individual session file
        session_file = output_dir / f"session_{timestamp}_{session_id}.yaml"
        with open(session_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        print(f"Saved session data: {session_file}")
        
        # Append to cumulative lessons
        cumulative_file = output_dir / "lessons_learned_cumulative.md"
        with open(cumulative_file, 'a', encoding='utf-8') as f:
            f.write(f"\n## Session: {session_id}\n")
            f.write(f"**Date**: {data.get('meta', {}).get('started_at', 'N/A')}\n")
            f.write(f"**Context**: {data.get('meta', {}).get('context', 'N/A')}\n\n")
            
            if data.get('lessons'):
                f.write("### Lessons Learned\n\n")
                for lesson in data['lessons']:
                    f.write(f"- **{lesson.get('title', 'Untitled')}**: ")
                    f.write(f"{lesson.get('outcome', 'N/A')}\n")
            
            if data.get('decisions'):
                f.write("\n### Key Decisions\n\n")
                for decision in data['decisions']:
                    f.write(f"- **{decision.get('what', 'Unknown')}**: ")
                    f.write(f"{decision.get('why', 'N/A')}\n")
            
            if data.get('future_research'):
                f.write("\n### Future Research Topics\n\n")
                for research in data['future_research']:
                    f.write(f"- **{research.get('topic', 'Unknown')}** ")
                    f.write(f"({research.get('estimated_complexity', 'unknown')} complexity): ")
                    f.write(f"{research.get('rationale', 'N/A')}\n")
            
            f.write("\n---\n")
        
        print(f"Updated cumulative lessons: {cumulative_file}")
    
    def generate_checkpoint(self, data: Dict, output_dir: Path):
        """Generate checkpoint file for session resume."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        session_id = data.get('meta', {}).get('session_id', 'unknown')
        checkpoint_file = output_dir / f"checkpoint_{session_id}.yaml"
        
        checkpoint = {
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat(),
            'status': data.get('status', 'unknown'),
            'phases_complete': data.get('phases_complete', []),
            'phases_active': data.get('phases_active', []),
            'next_steps': data.get('next_steps', []),
            'metrics': data.get('metrics', {}),
            'blockers': [b for b in data.get('blockers', []) if b.get('status') != 'resolved']
        }
        
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            yaml.dump(checkpoint, f, default_flow_style=False, sort_keys=False)
        
        print(f"Generated checkpoint: {checkpoint_file}")


def main():
    parser = argparse.ArgumentParser(description='Parse AfterMath session blocks')
    parser.add_argument('--source', required=True, help='Source file to parse')
    parser.add_argument('--output', required=True, help='Output directory for artifacts')
    parser.add_argument('--validate', action='store_true', help='Validate schema only')
    args = parser.parse_args()
    
    source_path = Path(args.source)
    output_path = Path(args.output)
    
    if not source_path.exists():
        print(f"Error: Source file not found: {source_path}", file=sys.stderr)
        return 1
    
    aftermath = AftermathParser()
    data = aftermath.parse_file(source_path)
    
    if not data:
        print("No aftermath data found", file=sys.stderr)
        return 1
    
    # Validate
    errors = aftermath.validate_schema(data)
    if errors:
        print("Schema validation errors:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        if args.validate:
            return 1
    
    if args.validate:
        print("Schema validation passed")
        return 0
    
    # Generate artifacts
    aftermath.save_lessons_learned(data, output_path)
    aftermath.generate_checkpoint(data, output_path / '../checkpoints')
    
    print(f"\nAfterMath processing complete:")
    print(f"  - Lessons learned: {output_path}/lessons_learned_cumulative.md")
    print(f"  - Checkpoint: {output_path}/../checkpoints/checkpoint_{data['meta']['session_id']}.yaml")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
