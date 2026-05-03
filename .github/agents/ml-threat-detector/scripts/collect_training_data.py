"""
Collect historical CI failure data for ML model training.
Extracts features from past vulnerabilities and successful runs.
"""

import json
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import requests


class TrainingDataCollector:
    """Collects training data from GitHub API and repository history."""

    def __init__(self, repo: str, token: str):
        self.repo = repo
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        }
        self.base_url = f"https://api.github.com/repos/{repo}"

    def collect_workflow_runs(self, days_back: int = 90) -> list[dict[str, Any]]:
        """Collect workflow runs from last N days"""
        since = (datetime.now() - timedelta(days=days_back)).isoformat()

        url = f"{self.base_url}/actions/runs"
        params = {"created": f">={since}", "per_page": 100}

        runs = []
        response = requests.get(url, headers=self.headers, params=params, timeout=30)
        data = response.json()

        for run in data.get("workflow_runs", []):
            runs.append(
                {
                    "id": run["id"],
                    "name": run["name"],
                    "status": run["status"],
                    "conclusion": run["conclusion"],
                    "created_at": run["created_at"],
                    "updated_at": run["updated_at"],
                    "duration": self._calculate_duration(run),
                }
            )

        return runs

    def collect_security_alerts(self) -> dict[str, list[Any]]:
        """Collect historical security alerts"""
        # CodeQL alerts
        codeql_alerts = []
        try:
            url = f"{self.base_url}/code-scanning/alerts"
            response = requests.get(url, headers=self.headers, timeout=30)
            if response.status_code == 200:
                codeql_alerts = response.json()
        except Exception as e:
            print(f"Warning: Could not fetch CodeQL alerts: {e}")

        # Dependabot alerts
        dependabot_alerts = []
        try:
            url = f"{self.base_url}/dependabot/alerts"
            response = requests.get(url, headers=self.headers, timeout=30)
            if response.status_code == 200:
                dependabot_alerts = response.json()
        except Exception as e:
            print(f"Warning: Could not fetch Dependabot alerts: {e}")

        return {"codeql": codeql_alerts, "dependabot": dependabot_alerts}

    def extract_features(self, file_path: str) -> dict[str, Any]:
        """Extract security-relevant features from code"""
        try:
            with open(file_path, encoding="utf-8") as f:
                code = f.read()
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
            return {}

        return {
            # Code complexity
            "lines_of_code": len(code.split("\n")),
            "complexity": self._calculate_complexity(code),
            "max_nesting_depth": self._calculate_nesting(code),
            # Security operations
            "subprocess_calls": code.count("subprocess"),
            "shell_true": code.count("shell=True"),
            "eval_exec": code.count("eval(") + code.count("exec("),
            # File operations
            "file_operations": code.count("open("),
            "file_write": code.count("'w'") + code.count('"w"'),
            # Network operations
            "network_calls": code.count("request") + code.count("urllib"),
            "api_calls": code.count("api.") + code.count("/api/"),
            # Cryptography
            "crypto_operations": code.count("hashlib") + code.count("crypt"),
            "md5_sha1_usage": code.count("md5") + code.count("sha1"),
            # Data handling
            "pickle_usage": code.count("pickle"),
            "xml_parsing": code.count("ElementTree"),
            "json_handling": code.count("json"),
            # User input
            "user_input": code.count("input(") + code.count("request."),
            "environment_vars": code.count("os.environ"),
            # Historical context
            "file_age_days": self._get_file_age(file_path),
            "commit_count": self._get_commit_count(file_path),
            "author_security_score": self._get_author_score(file_path),
        }


    def save_training_data(self, output_dir: str) -> None:
        """Save collected data for model training"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Collect all data
        workflow_data = self.collect_workflow_runs()
        security_data = self.collect_security_alerts()

        # Save to JSON
        with open(output_dir / "workflow_history.json", "w", encoding="utf-8") as f:
            json.dump(workflow_data, f, indent=2)

        with open(output_dir / "security_alerts.json", "w", encoding="utf-8") as f:
            json.dump(security_data, f, indent=2)

        print(f"✅ Training data saved to {output_dir}")
        print(f"   Workflow runs: {len(workflow_data)}")
        print(f"   CodeQL alerts: {len(security_data['codeql'])}")
        print(f"   Dependabot alerts: {len(security_data['dependabot'])}")

    def _calculate_duration(self, run: dict[str, Any]) -> float:
        """Calculate workflow run duration in seconds"""
        try:
            created = datetime.fromisoformat(run["created_at"].replace("Z", "+00:00"))
            updated = datetime.fromisoformat(run["updated_at"].replace("Z", "+00:00"))
            return (updated - created).total_seconds()
        except Exception:
            return 0.0

    def _calculate_complexity(self, code: str) -> int:
        """Calculate cyclomatic complexity (simplified)"""
        # Count control flow statements
        complexity = 1  # Base complexity
        complexity += code.count("if ")
        complexity += code.count("elif ")
        complexity += code.count("for ")
        complexity += code.count("while ")
        complexity += code.count("except ")
        complexity += code.count("and ")
        complexity += code.count("or ")
        return complexity

    def _calculate_nesting(self, code: str) -> int:
        """Calculate maximum nesting depth"""
        max_depth = 0
        current_depth = 0

        for line in code.split("\n"):
            stripped = line.lstrip()
            if not stripped or stripped.startswith("#"):
                continue

            # Calculate indentation
            indent = len(line) - len(stripped)
            current_depth = indent // 4  # Assuming 4-space indents

            max_depth = max(max_depth, current_depth)

        return max_depth

    def _get_file_age(self, file_path: str) -> int:
        """Get file age in days"""
        try:
            stat = os.stat(file_path)
            created = datetime.fromtimestamp(stat.st_ctime)
            return (datetime.now() - created).days
        except Exception:
            return 0

    def _get_commit_count(self, file_path: str) -> int:
        """Get number of commits for file"""
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "--", file_path],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            return len(result.stdout.strip().split("\n")) if result.stdout else 0
        except Exception:
            return 0

    def _get_author_score(self, file_path: str) -> float:
        """Get author security score (simplified)"""
        # Simplified: Returns 0.5 as baseline
        # In production, would analyze author's historical vulnerability rate
        return 0.5


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python collect_training_data.py <repo> <token>")
        sys.exit(1)

    collector = TrainingDataCollector(sys.argv[1], sys.argv[2])
    collector.save_training_data("training_data")
