"""Template: Secret Detector Pattern

This template shows the pattern for creating custom secret detection scripts
that can be stored as hidden scripts (Level 2 - HIGH).

Usage:
    1. Copy this template
    2. Implement custom_detection_logic()
    3. Store using HiddenScriptsManager
    4. Execute from secure context

Example:
    from scripts.ci._hidden_scripts_manager import HiddenScriptsManager
    manager = HiddenScriptsManager()
    
    with open("my_secret_detector.py") as f:
        code = f.read()
    
    manager.store_hidden_script(
        name="my_secret_detector",
        script_content=code,
        security_level=2  # HIGH
    )
"""

import json
import re
import sys
from typing import List, Dict, Any


class SecretDetector:
    """Template for custom secret detection patterns."""

    def __init__(self):
        """Initialize detector with custom patterns."""
        # Define custom detection patterns here
        # These patterns should be specific to your organization
        # and not exposed in git history
        self.patterns = {
            "api_key": r"api[_-]?key['\"]?\s*[:=]\s*['\"]?([a-zA-Z0-9]{32,})['\"]?",
            "private_token": r"private[_-]?token['\"]?\s*[:=]\s*['\"]?([a-z0-9]{40})['\"]?",
            "db_connection": r"(mysql|postgres|mongodb)://([^@]+)@([^/]+)/",
            "aws_secret": r"aws[_-]?secret[_-]?access[_-]?key['\"]?\s*[:=]",
        }

    def custom_detection_logic(self, content: str) -> List[Dict[str, Any]]:
        """Implement custom detection logic.
        
        This method should be customized for your organization's
        specific secret patterns and requirements.
        
        Args:
            content: File content to scan for secrets
            
        Returns:
            List of detected secrets with metadata
        """
        secrets = []

        for pattern_name, pattern_regex in self.patterns.items():
            matches = re.finditer(pattern_regex, content, re.IGNORECASE)
            for match in matches:
                secrets.append({
                    "pattern": pattern_name,
                    "line": content[:match.start()].count('\n') + 1,
                    "severity": "HIGH",
                    "match_length": len(match.group(0)),
                })

        return secrets

    def detect_in_file(self, filepath: str) -> Dict[str, Any]:
        """Detect secrets in a file.
        
        Args:
            filepath: Path to file to scan
            
        Returns:
            Detection results dictionary
        """
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            return {
                "filepath": filepath,
                "status": "error",
                "error": str(e),
                "secrets": []
            }

        secrets = self.custom_detection_logic(content)

        return {
            "filepath": filepath,
            "status": "success",
            "secrets_found": len(secrets),
            "secrets": secrets
        }

    def detect_in_directory(self, directory: str) -> List[Dict[str, Any]]:
        """Detect secrets in all files in directory.
        
        Args:
            directory: Directory to scan
            
        Returns:
            List of detection results
        """
        import os
        from pathlib import Path

        results = []
        exclude_dirs = {'.git', '__pycache__', 'node_modules', '.venv'}

        for root, dirs, files in os.walk(directory):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                # Skip binary files
                if file.endswith(('.pyc', '.o', '.so', '.dll', '.exe')):
                    continue

                filepath = os.path.join(root, file)
                result = self.detect_in_file(filepath)
                if result['secrets']:
                    results.append(result)

        return results


def main():
    """Main entry point - called when script is executed."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python secret_detector.py <file_or_directory>")
        sys.exit(1)

    target = sys.argv[1]
    detector = SecretDetector()

    if os.path.isfile(target):
        result = detector.detect_in_file(target)
        print(json.dumps(result, indent=2))
    elif os.path.isdir(target):
        results = detector.detect_in_directory(target)
        print(json.dumps(results, indent=2))
    else:
        print(f"Error: {target} is not a valid file or directory")
        sys.exit(1)

    # Exit with appropriate code
    total_secrets = sum(r.get('secrets_found', 0) for r in results) if isinstance(results, list) else 0
    sys.exit(1 if total_secrets > 0 else 0)


if __name__ == "__main__":
    main()
