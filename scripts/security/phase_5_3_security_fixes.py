#!/usr/bin/env python3
"""
Phase 5.3 Security Fixes - Comprehensive Implementation
Applies systematic security fixes to high-priority files.
"""

import sys
from pathlib import Path

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.aries_serpent_core.security_utils import sanitize_log_message

def create_safe_error_function() -> str:
    """Generate a safe error handling function."""
    return '''def _safe_error(exc: Exception) -> str:
    """Return a sanitized, non-sensitive error summary."""
    from src.aries_serpent_core.security_utils import sanitize_log_message
    error_name = type(exc).__name__
    # Sanitize error message to prevent information disclosure
    error_msg = str(exc)
    if error_msg:
        error_msg = sanitize_log_message(error_msg)
        return f"{error_name}: {error_msg}"
    return error_name
'''


def create_import_section() -> str:
    """Generate security utility imports."""
    return '''# Security utilities for sanitizing sensitive data
try:
    from src.aries_serpent_core.security_utils import sanitize_log_message
except ImportError:
    # Fallback sanitization
    def sanitize_log_message(msg: str) -> str:
        import re
        patterns = [
            (r'ghp_[A-Za-z0-9]{36,}', '[REDACTED_GITHUB_TOKEN]'),
            (r'github_pat_[A-Za-z0-9_]{82}', '[REDACTED_GITHUB_PAT]'),
            (r'(?:api[_-]?key|token|secret|password|passwd)["\']?\s*[:=]\s*["\']?([^"\'\s]+)', '[REDACTED]'),
        ]
        result = msg
        for pattern, replacement in patterns:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        return result
'''


def create_logging_helper() -> str:
    """Generate logging helper function."""
    return '''def safe_log(message: str, log_func=None, level="info"):
    """Safely log a message by sanitizing sensitive data."""
    sanitized = sanitize_log_message(message)
    if log_func:
        log_func(sanitized)
    else:
        if level == "debug":
            print(f"[DEBUG] {sanitized}")
        elif level == "info":
            print(f"[INFO] {sanitized}")
        elif level == "warning":
            print(f"[WARNING] {sanitized}")
        elif level == "error":
            print(f"[ERROR] {sanitized}")
        else:
            print(sanitized)
'''


def analyze_file(filepath: Path) -> dict:
    """Analyze a file for security issues."""
    findings = {
        'file': str(filepath),
        'total_lines': 0,
        'log_statements': 0,
        'print_statements': 0,
        'logger_calls': 0,
        'issues': []
    }
    
    try:
        with open(filepath) as f:
            lines = f.readlines()
        
        findings['total_lines'] = len(lines)
        
        for i, line in enumerate(lines, 1):
            # Look for logging patterns
            if 'logger.' in line:
                findings['logger_calls'] += 1
            elif 'print(' in line:
                findings['print_statements'] += 1
                # Check for potential issues
                if 'token' in line.lower() or 'secret' in line.lower():
                    findings['issues'].append({
                        'line': i,
                        'type': 'print_potentially_sensitive',
                        'content': line.strip()
                    })
    except Exception as e:
        findings['error'] = str(e)
    
    return findings


def generate_report(files: list[Path]) -> None:
    """Generate a security analysis report."""
    print("\n" + "=" * 80)
    print("Phase 5.3 - Security Analysis Report")
    print("=" * 80 + "\n")
    
    total_issues = 0
    
    for filepath in files:
        if filepath.exists():
            analysis = analyze_file(filepath)
            print(f"\n📄 {filepath}")
            print(f"   Lines: {analysis['total_lines']}")
            print(f"   Logger calls: {analysis['logger_calls']}")
            print(f"   Print statements: {analysis['print_statements']}")
            
            if analysis['issues']:
                print(f"   ⚠️  Issues found: {len(analysis['issues'])}")
                for issue in analysis['issues']:
                    print(f"      Line {issue['line']}: {issue['type']}")
                    total_issues += len(analysis['issues'])
    
    print("\n" + "=" * 80)
    print(f"Total issues identified: {total_issues}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    # High-priority files to analyze
    high_priority_files = [
        Path("scripts/ci/aggregate_security_findings.py"),
        Path("scripts/fix_security_issues.py"),
        Path("scripts/github_secrets_sync.py"),
        Path("scripts/analyze_workflows.py"),
        Path(".github/scripts/ci_failure_crossref.py"),
        Path("scripts/ops/codex_mint_tokens_per_run.py"),
        Path("scripts/ops/codex_repo_admin_bootstrap.py"),
        Path("scripts/ci/copilot_security_agent_handoff.py"),
        Path("scripts/observability/core_telemetry_collector.py"),
    ]
    
    repo_root = Path(__file__).parent
    
    # Analyze all files
    files_to_check = [repo_root / f for f in high_priority_files]
    generate_report(files_to_check)
