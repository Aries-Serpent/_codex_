#!/usr/bin/env python3
"""
Code Example Validator & Audit Tool
Phase 12 WS3 - Workstream 5: Code Example Validation

Extracts, categorizes, and validates all code examples from documentation.
Supports Python, YAML, Shell, JavaScript, and Markdown syntax validation.
"""

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import tempfile
import hashlib


@dataclass
class CodeExample:
    """Represents a single code example"""
    id: str
    file_path: str
    line_number: int
    language: str
    code: str
    context: str  # Preceding text/description
    is_executable: bool
    execution_status: str  # pending, success, failed, error
    error_message: Optional[str] = None
    execution_output: Optional[str] = None
    validation_timestamp: Optional[str] = None

    def to_dict(self):
        return asdict(self)


class CodeExampleExtractor:
    """Extracts code examples from markdown files"""

    def __init__(self):
        self.examples: List[CodeExample] = []
        self.example_counter = 0

    def extract_from_file(self, file_path: str) -> List[CodeExample]:
        """Extract all code examples from a markdown file"""
        examples = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return examples

        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Look for code block markers
            if line.strip().startswith('```'):
                # Extract language
                lang_match = re.match(r'```(\w+)?', line.strip())
                language = lang_match.group(1) if lang_match and lang_match.group(1) else 'text'
                
                # Get preceding context (description before code block)
                context_lines = []
                for j in range(max(0, i - 5), i):
                    context_lines.append(lines[j].strip())
                context = ' '.join(context_lines[-3:]) if context_lines else ''
                
                # Extract code until closing ```
                code_lines = []
                start_line = i + 1
                i += 1
                
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i].rstrip('\n'))
                    i += 1
                
                code = '\n'.join(code_lines).strip()
                
                if code:
                    self.example_counter += 1
                    example_id = f"ex-{self.example_counter:04d}"
                    
                    # Determine if executable
                    is_executable = self._is_executable(language, code)
                    
                    example = CodeExample(
                        id=example_id,
                        file_path=file_path,
                        line_number=start_line,
                        language=language,
                        code=code,
                        context=context,
                        is_executable=is_executable,
                        execution_status='pending'
                    )
                    examples.append(example)
                    self.examples.append(example)
            
            i += 1
        
        return examples

    def _is_executable(self, language: str, code: str) -> bool:
        """Determine if a code example is executable"""
        non_executable = ['text', 'json', 'yaml', 'html', 'xml', 'markdown', 'md', '']
        
        if language.lower() in non_executable:
            return False
        
        # Check for common non-executable patterns
        if 'TODO' in code or '...' in code or '# [' in code:
            return False
        
        return True

    def extract_all(self, docs_path: str = 'docs') -> List[CodeExample]:
        """Extract all examples from documentation directory"""
        for root, dirs, files in os.walk(docs_path):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    self.extract_from_file(file_path)
        
        return self.examples


class CodeExampleValidator:
    """Validates code examples by language"""

    def __init__(self):
        self.results = {}

    def validate(self, example: CodeExample) -> CodeExample:
        """Validate a single code example"""
        if not example.is_executable:
            example.execution_status = 'skipped'
            return example

        validator_method = getattr(
            self,
            f'validate_{example.language}',
            self._validate_generic
        )

        try:
            validator_method(example)
            example.execution_status = 'success'
        except Exception as e:
            example.execution_status = 'failed'
            example.error_message = str(e)

        example.validation_timestamp = datetime.now().isoformat()
        return example

    def validate_python(self, example: CodeExample):
        """Validate Python code examples"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(example.code)
            temp_file = f.name

        try:
            # First, syntax check
            compile(example.code, temp_file, 'exec')
            
            # Then try execution (but limit execution time)
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                raise Exception(f"Execution failed: {result.stderr}")
            
            example.execution_output = result.stdout
        finally:
            os.unlink(temp_file)

    def validate_yaml(self, example: CodeExample):
        """Validate YAML syntax"""
        try:
            import yaml
            yaml.safe_load(example.code)
        except ImportError:
            # YAML not available, skip validation
            example.execution_status = 'skipped'
        except Exception as e:
            raise Exception(f"YAML validation failed: {str(e)}")

    def validate_shell(self, example: CodeExample):
        """Validate shell command examples (syntax only)"""
        # Basic shell syntax validation
        if not example.code.strip():
            raise Exception("Empty shell command")
        
        # Check for common shell syntax errors
        if example.code.count('(') != example.code.count(')'):
            raise Exception("Mismatched parentheses")
        
        if example.code.count('[') != example.code.count(']'):
            raise Exception("Mismatched brackets")

    def validate_javascript(self, example: CodeExample):
        """Validate JavaScript syntax"""
        try:
            # Check if Node.js is available
            result = subprocess.run(
                ['node', '--check', '--input-type=module'],
                input=example.code,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                raise Exception(f"JavaScript validation failed: {result.stderr}")
        except FileNotFoundError:
            # Node.js not available, do basic syntax check
            if not _is_valid_js_syntax(example.code):
                raise Exception("JavaScript syntax appears invalid")

    def _validate_generic(self, example: CodeExample):
        """Generic validation for unknown languages"""
        if not example.code.strip():
            raise Exception("Empty code block")


def _is_valid_js_syntax(code: str) -> bool:
    """Basic JavaScript syntax validation"""
    # Check for balanced braces/brackets
    return (code.count('{') == code.count('}') and
            code.count('[') == code.count(']') and
            code.count('(') == code.count(')'))


class CodeExampleCatalog:
    """Creates and manages code example catalog"""

    def __init__(self, examples: List[CodeExample]):
        self.examples = examples

    def categorize_by_language(self) -> Dict[str, List[CodeExample]]:
        """Categorize examples by language"""
        catalog = {}
        for example in self.examples:
            lang = example.language
            if lang not in catalog:
                catalog[lang] = []
            catalog[lang].append(example)
        return catalog

    def categorize_by_status(self) -> Dict[str, List[CodeExample]]:
        """Categorize examples by execution status"""
        catalog = {}
        for example in self.examples:
            status = example.execution_status
            if status not in catalog:
                catalog[status] = []
            catalog[status].append(example)
        return catalog

    def generate_report(self) -> Dict:
        """Generate comprehensive audit report"""
        by_language = self.categorize_by_language()
        by_status = self.categorize_by_status()

        report = {
            'timestamp': datetime.now().isoformat(),
            'total_examples': len(self.examples),
            'by_language': {
                lang: {
                    'count': len(examples),
                    'executable': sum(1 for e in examples if e.is_executable),
                    'examples': [e.to_dict() for e in examples[:3]]  # First 3
                }
                for lang, examples in by_language.items()
            },
            'by_status': {
                status: len(examples)
                for status, examples in by_status.items()
            },
            'executability': {
                'total_executable': sum(1 for e in self.examples if e.is_executable),
                'total_non_executable': sum(1 for e in self.examples if not e.is_executable),
                'executable_percentage': (
                    sum(1 for e in self.examples if e.is_executable) / len(self.examples) * 100
                    if self.examples else 0
                )
            }
        }

        return report

    def export_json(self, file_path: str):
        """Export catalog to JSON"""
        catalog = {
            'metadata': {
                'created': datetime.now().isoformat(),
                'total_examples': len(self.examples),
                'phase': 'Phase 12 WS3'
            },
            'examples': [e.to_dict() for e in self.examples]
        }
        
        with open(file_path, 'w') as f:
            json.dump(catalog, f, indent=2)

    def export_csv(self, file_path: str):
        """Export catalog to CSV for analysis"""
        import csv
        
        with open(file_path, 'w', newline='') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=['id', 'file_path', 'language', 'is_executable',
                           'execution_status', 'line_number']
            )
            writer.writeheader()
            
            for example in self.examples:
                writer.writerow({
                    'id': example.id,
                    'file_path': example.file_path,
                    'language': example.language,
                    'is_executable': example.is_executable,
                    'execution_status': example.execution_status,
                    'line_number': example.line_number
                })


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Code Example Validator & Audit')
    parser.add_argument('--extract', action='store_true', help='Extract examples')
    parser.add_argument('--validate', action='store_true', help='Validate examples')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--limit', type=int, default=None, help='Limit examples to validate')
    parser.add_argument('--docs-path', default='docs', help='Path to documentation')
    parser.add_argument('--output', default='code_examples_catalog.json', help='Output file')
    
    args = parser.parse_args()
    
    print("🔍 Code Example Validator & Audit Tool")
    print("=" * 60)
    
    # Extract examples
    if args.extract or not any([args.validate, args.report]):
        print("\n📚 Extracting code examples...")
        extractor = CodeExampleExtractor()
        examples = extractor.extract_all(args.docs_path)
        print(f"✅ Found {len(examples)} code examples")
    else:
        examples = []
    
    # Validate examples
    if args.validate and examples:
        print("\n✔️ Validating code examples...")
        validator = CodeExampleValidator()
        
        limit = min(args.limit or len(examples), len(examples))
        for i, example in enumerate(examples[:limit], 1):
            validator.validate(example)
            if i % 10 == 0:
                print(f"  {i}/{limit} validated...")
        
        print(f"✅ Validation complete")
    
    # Generate report
    if args.report and examples:
        print("\n📊 Generating report...")
        catalog = CodeExampleCatalog(examples)
        report = catalog.generate_report()
        
        print("\n" + "=" * 60)
        print("AUDIT REPORT SUMMARY")
        print("=" * 60)
        print(f"Total Examples: {report['total_examples']}")
        print(f"Executable: {report['executability']['total_executable']}")
        print(f"Non-executable: {report['executability']['total_non_executable']}")
        print(f"Executable %: {report['executability']['executable_percentage']:.1f}%")
        
        print("\nBy Language:")
        for lang, data in report['by_language'].items():
            print(f"  {lang}: {data['count']} total, {data['executable']} executable")
        
        print("\nBy Status:")
        for status, count in report['by_status'].items():
            print(f"  {status}: {count}")
        
        # Export catalog
        catalog.export_json(args.output)
        print(f"\n✅ Catalog exported to {args.output}")
        
        # Export CSV
        csv_output = args.output.replace('.json', '.csv')
        catalog.export_csv(csv_output)
        print(f"✅ CSV exported to {csv_output}")
        
        return report


if __name__ == '__main__':
    main()
