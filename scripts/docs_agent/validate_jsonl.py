#!/usr/bin/env python3
"""
JSONL Schema Validator for Machine-Readable Documentation

Validates JSONL files against JSON Schema definitions and performs
semantic validation, consistency checks, and link validation.

Authority: Lane 3 Unified Documentation Agent
Status: Task 3.1 Implementation
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict
import logging
from datetime import datetime
import csv

try:
    import jsonschema
    from jsonschema import validate, ValidationError
except ImportError:
    print("ERROR: jsonschema module required. Install with: pip install jsonschema")
    sys.exit(1)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of validating a single record"""
    record_id: str
    record_type: str
    line_number: int
    is_valid: bool
    errors: List[str]
    warnings: List[str]


class JSONLValidator:
    """Validates JSONL files against JSON Schema definitions"""

    def __init__(self, schemas_dir: Path):
        """Initialize validator with schemas directory
        
        Args:
            schemas_dir: Path to directory containing JSON Schema files
        """
        self.schemas_dir = schemas_dir
        self.schemas: Dict[str, Dict] = {}
        self.records_by_id: Dict[str, Dict] = {}
        self.results: List[ValidationResult] = []
        self.entity_index: Dict[str, Tuple[str, str]] = {}  # id -> (type, line_number)
        
        self._load_schemas()

    def _load_schemas(self):
        """Load all JSON Schema files from schemas directory"""
        if not self.schemas_dir.exists():
            logger.error(f"Schemas directory not found: {self.schemas_dir}")
            sys.exit(1)
        
        schema_files = list(self.schemas_dir.glob("*.json"))
        if not schema_files:
            logger.error(f"No schema files found in {self.schemas_dir}")
            sys.exit(1)
        
        for schema_file in schema_files:
            try:
                with open(schema_file, 'r') as f:
                    schema = json.load(f)
                    record_type = schema_file.stem
                    self.schemas[record_type] = schema
                    logger.debug(f"Loaded schema: {record_type}")
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in schema file {schema_file}: {e}")
                sys.exit(1)
        
        logger.info(f"Loaded {len(self.schemas)} schemas")

    def validate_file(self, jsonl_file: Path) -> Tuple[List[ValidationResult], Dict[str, Any]]:
        """Validate a JSONL file
        
        Args:
            jsonl_file: Path to JSONL file
            
        Returns:
            Tuple of (results list, statistics dict)
        """
        self.results = []
        self.records_by_id = {}
        self.entity_index = {}
        
        logger.info(f"Validating file: {jsonl_file}")
        
        # Phase 1: Line parsing and schema validation
        with open(jsonl_file, 'r') as f:
            for line_number, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                result = self._validate_line(line, line_number)
                self.results.append(result)
                
                if result.is_valid:
                    try:
                        record = json.loads(line)
                        self.records_by_id[record['id']] = record
                        self.entity_index[record['id']] = (record['type'], line_number)
                    except (json.JSONDecodeError, KeyError):
                        pass
        
        # Phase 2: Semantic validation (cross-record references)
        self._validate_semantic()
        
        # Phase 3: Consistency checks
        self._validate_consistency()
        
        stats = self._compute_statistics()
        
        return self.results, stats

    def _validate_line(self, line: str, line_number: int) -> ValidationResult:
        """Validate a single JSONL line
        
        Returns:
            ValidationResult object
        """
        errors = []
        warnings = []
        record_id = "unknown"
        record_type = "unknown"
        
        # Step 1: Parse JSON
        try:
            record = json.loads(line)
        except json.JSONDecodeError as e:
            return ValidationResult(
                record_id=record_id,
                record_type=record_type,
                line_number=line_number,
                is_valid=False,
                errors=[f"Invalid JSON: {e}"],
                warnings=[]
            )
        
        # Extract id and type
        try:
            record_id = record.get('id', 'unknown')
            record_type = record.get('type', 'unknown')
        except (AttributeError, TypeError):
            return ValidationResult(
                record_id=record_id,
                record_type=record_type,
                line_number=line_number,
                is_valid=False,
                errors=["Record is not a JSON object"],
                warnings=[]
            )
        
        # Step 2: Validate against JSON Schema
        if record_type not in self.schemas:
            errors.append(f"Unknown record type: {record_type}")
        else:
            schema = self.schemas[record_type]
            try:
                validate(instance=record, schema=schema)
            except ValidationError as e:
                errors.append(f"Schema validation failed: {e.message}")
        
        # Step 3: Required fields check
        if 'id' not in record:
            errors.append("Missing required field: id")
        if 'type' not in record:
            errors.append("Missing required field: type")
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            record_id=record_id,
            record_type=record_type,
            line_number=line_number,
            is_valid=is_valid,
            errors=errors,
            warnings=warnings
        )

    def _validate_semantic(self):
        """Validate cross-record references and referential integrity"""
        logger.info("Performing semantic validation...")
        
        for record_id, record in self.records_by_id.items():
            record_type = record.get('type')
            line_number = self.entity_index[record_id][1]
            
            # Find the result for this record
            result = next((r for r in self.results if r.record_id == record_id), None)
            if not result:
                continue
            
            # Validate record-type-specific references
            if record_type == 'section':
                # Check doc_id reference
                doc_id = record.get('doc_id')
                if doc_id and doc_id not in self.records_by_id:
                    result.errors.append(f"Referenced document not found: doc_id={doc_id}")
                
                # Check parent_id reference
                parent_id = record.get('parent_id')
                if parent_id:
                    if parent_id not in self.records_by_id:
                        result.errors.append(f"Referenced parent section not found: parent_id={parent_id}")
                    else:
                        parent = self.records_by_id[parent_id]
                        if parent.get('type') != 'section':
                            result.errors.append(f"Parent must be a section: parent_id={parent_id}")
            
            elif record_type == 'block':
                # Check section_id reference
                section_id = record.get('section_id')
                if section_id and section_id not in self.records_by_id:
                    result.errors.append(f"Referenced section not found: section_id={section_id}")
                
                # Check references array
                references = record.get('references', [])
                for ref_id in references:
                    if ref_id not in self.records_by_id:
                        result.warnings.append(f"Referenced entity not found: {ref_id}")
            
            elif record_type == 'action':
                # Check block_id reference
                block_id = record.get('block_id')
                if block_id and block_id not in self.records_by_id:
                    result.errors.append(f"Referenced block not found: block_id={block_id}")
            
            elif record_type == 'requirement':
                # Check block_id reference
                block_id = record.get('block_id')
                if block_id and block_id not in self.records_by_id:
                    result.warnings.append(f"Referenced block not found: block_id={block_id}")
                
                # Check related_requirements
                related = record.get('related_requirements', [])
                for req_id in related:
                    if req_id not in self.records_by_id:
                        result.warnings.append(f"Referenced requirement not found: {req_id}")
            
            elif record_type == 'reference':
                # Check source_id and target_id
                source_id = record.get('source_id')
                target_id = record.get('target_id')
                is_external = record.get('is_external', False)
                
                if not is_external:
                    if source_id not in self.records_by_id:
                        result.errors.append(f"Source entity not found: source_id={source_id}")
                    if target_id not in self.records_by_id:
                        result.errors.append(f"Target entity not found: target_id={target_id}")
            
            elif record_type == 'relationship':
                # Check entity references
                entity_a = record.get('entity_a_id')
                entity_b = record.get('entity_b_id')
                
                if entity_a not in self.records_by_id:
                    result.warnings.append(f"Entity A not found: entity_a_id={entity_a}")
                if entity_b not in self.records_by_id:
                    result.warnings.append(f"Entity B not found: entity_b_id={entity_b}")

    def _validate_consistency(self):
        """Validate consistency of computed and derived fields"""
        logger.info("Performing consistency checks...")
        
        for record_id, record in self.records_by_id.items():
            record_type = record.get('type')
            result = next((r for r in self.results if r.record_id == record_id), None)
            if not result:
                continue
            
            # Check word_count for sections
            if record_type == 'section':
                content = record.get('content', '')
                word_count = record.get('word_count')
                if word_count is not None:
                    actual_words = len(content.split())
                    if actual_words != word_count:
                        result.warnings.append(
                            f"word_count mismatch: expected {actual_words}, got {word_count}"
                        )
            
            # Check line_range consistency for blocks
            if record_type == 'block':
                line_range = record.get('line_range', {})
                start = line_range.get('start')
                end = line_range.get('end')
                if start and end and start > end:
                    result.errors.append("line_range.start must be ≤ line_range.end")

    def _compute_statistics(self) -> Dict[str, Any]:
        """Compute validation statistics
        
        Returns:
            Dictionary with validation statistics
        """
        total = len(self.results)
        valid = sum(1 for r in self.results if r.is_valid)
        invalid = total - valid
        
        errors_total = sum(len(r.errors) for r in self.results)
        warnings_total = sum(len(r.warnings) for r in self.results)
        
        record_types = defaultdict(int)
        for r in self.results:
            record_types[r.record_type] += 1
        
        accuracy = (valid / total * 100) if total > 0 else 0
        
        return {
            'total_records': total,
            'valid_records': valid,
            'invalid_records': invalid,
            'accuracy_percent': round(accuracy, 2),
            'total_errors': errors_total,
            'total_warnings': warnings_total,
            'records_by_type': dict(record_types),
            'validation_timestamp': datetime.now().isoformat(),
        }

    def generate_csv_report(self, output_file: Path):
        """Generate CSV validation report
        
        Args:
            output_file: Path to output CSV file
        """
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'line_number', 'record_id', 'record_type', 'is_valid',
                'error_count', 'warning_count', 'errors', 'warnings'
            ])
            writer.writeheader()
            
            for result in sorted(self.results, key=lambda r: r.line_number):
                writer.writerow({
                    'line_number': result.line_number,
                    'record_id': result.record_id,
                    'record_type': result.record_type,
                    'is_valid': 'Yes' if result.is_valid else 'No',
                    'error_count': len(result.errors),
                    'warning_count': len(result.warnings),
                    'errors': '; '.join(result.errors),
                    'warnings': '; '.join(result.warnings),
                })
        
        logger.info(f"CSV report written to: {output_file}")

    def generate_json_report(self, output_file: Path, include_details: bool = False):
        """Generate JSON validation report
        
        Args:
            output_file: Path to output JSON file
            include_details: Whether to include detailed results
        """
        report = {
            'validation_timestamp': datetime.now().isoformat(),
            'statistics': self._compute_statistics(),
            'results': []
        }
        
        if include_details:
            report['results'] = [
                {
                    'line_number': r.line_number,
                    'record_id': r.record_id,
                    'record_type': r.record_type,
                    'is_valid': r.is_valid,
                    'errors': r.errors,
                    'warnings': r.warnings,
                }
                for r in sorted(self.results, key=lambda r: r.line_number)
            ]
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"JSON report written to: {output_file}")

    def generate_html_report(self, output_file: Path):
        """Generate HTML validation report with summary statistics
        
        Args:
            output_file: Path to output HTML file
        """
        stats = self._compute_statistics()
        invalid_results = [r for r in self.results if not r.is_valid]
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>JSONL Validation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f0f0f0; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .stat {{ display: inline-block; margin-right: 30px; }}
        .stat-value {{ font-size: 24px; font-weight: bold; }}
        .stat-label {{ font-size: 14px; color: #666; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background: #f0f0f0; font-weight: bold; }}
        tr:nth-child(even) {{ background: #fafafa; }}
        .error {{ color: #d32f2f; }}
        .warning {{ color: #f57c00; }}
        .valid {{ color: #388e3c; }}
    </style>
</head>
<body>
    <h1>JSONL Validation Report</h1>
    <p>Generated: {stats['validation_timestamp']}</p>
    
    <div class="summary">
        <div class="stat">
            <div class="stat-value">{stats['total_records']}</div>
            <div class="stat-label">Total Records</div>
        </div>
        <div class="stat">
            <div class="stat-value valid">{stats['valid_records']}</div>
            <div class="stat-label">Valid</div>
        </div>
        <div class="stat">
            <div class="stat-value error">{stats['invalid_records']}</div>
            <div class="stat-label">Invalid</div>
        </div>
        <div class="stat">
            <div class="stat-value">{stats['accuracy_percent']}%</div>
            <div class="stat-label">Accuracy</div>
        </div>
        <div class="stat">
            <div class="stat-value error">{stats['total_errors']}</div>
            <div class="stat-label">Total Errors</div>
        </div>
        <div class="stat">
            <div class="stat-value warning">{stats['total_warnings']}</div>
            <div class="stat-label">Total Warnings</div>
        </div>
    </div>
    
    <h2>Records by Type</h2>
    <table>
        <tr><th>Type</th><th>Count</th></tr>
"""
        for record_type, count in sorted(stats['records_by_type'].items()):
            html += f"        <tr><td>{record_type}</td><td>{count}</td></tr>\n"
        
        html += """
    </table>
    
    <h2>Invalid Records</h2>
"""
        if invalid_results:
            html += """    <table>
        <tr><th>Line</th><th>ID</th><th>Type</th><th>Errors</th><th>Warnings</th></tr>
"""
            for result in sorted(invalid_results, key=lambda r: r.line_number):
                html += f"""        <tr>
            <td>{result.line_number}</td>
            <td>{result.record_id}</td>
            <td>{result.record_type}</td>
            <td><span class="error">{'; '.join(result.errors)}</span></td>
            <td><span class="warning">{'; '.join(result.warnings)}</span></td>
        </tr>
"""
            html += "    </table>\n"
        else:
            html += "    <p><span class=\"valid\">No invalid records found!</span></p>\n"
        
        html += """
</body>
</html>
"""
        
        with open(output_file, 'w') as f:
            f.write(html)
        
        logger.info(f"HTML report written to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Validate JSONL files against JSON Schema definitions'
    )
    parser.add_argument('jsonl_file', type=Path, help='JSONL file to validate')
    parser.add_argument(
        '--schemas-dir',
        type=Path,
        default=Path('.codex/schemas'),
        help='Directory containing JSON Schema files (default: .codex/schemas)'
    )
    parser.add_argument(
        '--csv-report',
        type=Path,
        help='Output CSV validation report'
    )
    parser.add_argument(
        '--json-report',
        type=Path,
        help='Output JSON validation report'
    )
    parser.add_argument(
        '--html-report',
        type=Path,
        help='Output HTML validation report'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate input file exists
    if not args.jsonl_file.exists():
        print(f"ERROR: JSONL file not found: {args.jsonl_file}", file=sys.stderr)
        sys.exit(1)
    
    # Initialize validator and run validation
    validator = JSONLValidator(args.schemas_dir)
    results, stats = validator.validate_file(args.jsonl_file)
    
    # Print summary
    print("\n" + "="*60)
    print("JSONL VALIDATION SUMMARY")
    print("="*60)
    print(f"Total records:    {stats['total_records']}")
    print(f"Valid records:    {stats['valid_records']}")
    print(f"Invalid records:  {stats['invalid_records']}")
    print(f"Accuracy:         {stats['accuracy_percent']}%")
    print(f"Total errors:     {stats['total_errors']}")
    print(f"Total warnings:   {stats['total_warnings']}")
    print("\nRecords by type:")
    for record_type, count in sorted(stats['records_by_type'].items()):
        print(f"  {record_type}: {count}")
    print("="*60)
    
    # Generate reports if requested
    if args.csv_report:
        validator.generate_csv_report(args.csv_report)
    
    if args.json_report:
        validator.generate_json_report(args.json_report, include_details=True)
    
    if args.html_report:
        validator.generate_html_report(args.html_report)
    
    # Exit with appropriate code
    sys.exit(0 if stats['invalid_records'] == 0 else 1)


if __name__ == '__main__':
    main()
