"""
Security Scan Agent CLI
Entry point for agent invocation with task execution.

#AFTERMATH_PATTERN_IDENTIFIED - Modular CLI with task-based execution
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from agent import (
    FalsePositiveFilter,
    PRAnnotator,
    SARIFParser,
    SecurityScanner,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def task_scan(workspace: Path, output_dir: Path, skip_tools: list[str]) -> dict[str, Any]:
    """
    Run security scans.
    
    Args:
        workspace: Repository workspace
        output_dir: Output directory for results
        skip_tools: List of tools to skip
        
    Returns:
        Task result dictionary
    """
    scanner = SecurityScanner(workspace, output_dir)
    
    results = scanner.run_all_scans(
        skip_bandit="bandit" in skip_tools,
        skip_semgrep="semgrep" in skip_tools,
        skip_safety="safety" in skip_tools,
    )
    
    return {
        "task": "scan",
        "status": "success",
        "results": {
            tool: {
                "findings_count": res.findings_count,
                "sarif_path": str(res.sarif_path) if res.sarif_path else None,
                "exit_code": res.exit_code,
                "errors": res.errors,
            }
            for tool, res in results.items()
        }
    }


def task_parse(sarif_file: Path, output_dir: Path) -> dict[str, Any]:
    """
    Parse SARIF results.
    
    Args:
        sarif_file: Path to SARIF file
        output_dir: Output directory
        
    Returns:
        Task result dictionary
    """
    parser = SARIFParser()
    parsed = parser.parse_file(sarif_file)
    
    # Write parsed results to JSON
    output_file = output_dir / "parsed_results.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w") as f:
        json.dump({
            "tool": parsed.tool_name,
            "version": parsed.tool_version,
            "total_findings": parsed.total_count,
            "findings": [
                {
                    "rule_id": f.rule_id,
                    "message": f.message,
                    "level": f.level,
                    "locations": [
                        {
                            "file": loc.file_path,
                            "line": loc.start_line,
                        }
                        for loc in f.locations
                    ]
                }
                for f in parsed.findings
            ]
        }, f, indent=2)
    
    return {
        "task": "parse",
        "status": "success",
        "tool": parsed.tool_name,
        "total_findings": parsed.total_count,
        "output_file": str(output_file),
    }


def task_filter(
    parsed_file: Path,
    output_dir: Path,
    apply_defaults: bool = True
) -> dict[str, Any]:
    """
    Filter false positives.
    
    Args:
        parsed_file: Path to parsed results JSON
        output_dir: Output directory
        apply_defaults: Apply default filter rules
        
    Returns:
        Task result dictionary
    """
    # Load parsed findings
    with open(parsed_file) as f:
        data = json.load(f)
    
    # Reconstruct Finding objects (simplified for CLI)
    from agent.parser import Finding, Location
    findings = [
        Finding(
            rule_id=f["rule_id"],
            message=f["message"],
            level=f["level"],
            locations=[
                Location(
                    file_path=loc["file"],
                    start_line=loc["line"],
                    end_line=loc["line"]
                )
                for loc in f.get("locations", [])
            ]
        )
        for f in data["findings"]
    ]
    
    # Apply filter
    filter_engine = FalsePositiveFilter()
    valid, filtered = filter_engine.filter_findings(findings, apply_defaults)
    
    # Write results
    output_file = output_dir / "filtered_results.json"
    with open(output_file, "w") as f:
        json.dump({
            "valid_count": len(valid),
            "filtered_count": len(filtered),
            "filter_stats": filter_engine.get_filter_stats(filtered),
        }, f, indent=2)
    
    return {
        "task": "filter",
        "status": "success",
        "valid_count": len(valid),
        "filtered_count": len(filtered),
        "output_file": str(output_file),
    }


def task_annotate(
    findings_file: Path,
    output_dir: Path,
    max_annotations: int = 50
) -> dict[str, Any]:
    """
    Generate PR annotations.
    
    Args:
        findings_file: Path to findings JSON
        output_dir: Output directory
        max_annotations: Maximum annotations
        
    Returns:
        Task result dictionary
    """
    # Load findings
    with open(findings_file) as f:
        data = json.load(f)
    
    # Reconstruct Finding objects
    from agent.parser import Finding, Location
    findings = [
        Finding(
            rule_id=f["rule_id"],
            message=f["message"],
            level=f["level"],
            tool=data.get("tool", "unknown"),
            locations=[
                Location(
                    file_path=loc["file"],
                    start_line=loc["line"],
                    end_line=loc["line"]
                )
                for loc in f.get("locations", [])
            ]
        )
        for f in data.get("findings", [])
    ]
    
    # Generate annotations
    annotator = PRAnnotator()
    annotations = annotator.generate_annotations(findings, max_annotations)
    summary = annotator.generate_summary(findings, findings, [])
    
    # Write outputs
    annotations_file = output_dir / "annotations.json"
    summary_file = output_dir / "summary.md"
    
    annotator.write_annotations_file(annotations, annotations_file)
    annotator.write_summary_file(summary, summary_file)
    
    return {
        "task": "annotate",
        "status": "success",
        "annotations_count": len(annotations),
        "annotations_file": str(annotations_file),
        "summary_file": str(summary_file),
    }


def main() -> int:
    """Main entry point for Security Scan Agent."""
    parser = argparse.ArgumentParser(
        description="Security Scan Agent - Automated security scanning and PR annotation"
    )
    parser.add_argument("--task", required=True, choices=["scan", "parse", "filter", "annotate"])
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path, default=Path(".security-scan"))
    parser.add_argument("--sarif-file", type=Path)
    parser.add_argument("--parsed-file", type=Path)
    parser.add_argument("--findings-file", type=Path)
    parser.add_argument("--skip-tools", nargs="*", default=[])
    parser.add_argument("--max-annotations", type=int, default=50)
    
    args = parser.parse_args()
    
    try:
        # Execute task
        if args.task == "scan":
            result = task_scan(args.workspace, args.output_dir, args.skip_tools)
        elif args.task == "parse":
            if not args.sarif_file:
                parser.error("--sarif-file required for parse task")
            result = task_parse(args.sarif_file, args.output_dir)
        elif args.task == "filter":
            if not args.parsed_file:
                parser.error("--parsed-file required for filter task")
            result = task_filter(args.parsed_file, args.output_dir)
        elif args.task == "annotate":
            if not args.findings_file:
                parser.error("--findings-file required for annotate task")
            result = task_annotate(args.findings_file, args.output_dir, args.max_annotations)
        else:
            return 1
        
        # Print result
        print(json.dumps(result, indent=2))
        return 0
    
    except Exception as e:
        logger.error("Task failed: %s", e, exc_info=True)
        print(json.dumps({
            "task": args.task,
            "status": "error",
            "error": str(e)
        }), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())


# #AFTERMATH_METRIC - CLI with 4 task types: scan, parse, filter, annotate
# #AFTERMATH_PATTERN_IDENTIFIED - Task-based CLI for modular execution
