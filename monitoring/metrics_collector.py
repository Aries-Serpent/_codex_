"""Real-time metrics collector for CI/CD and security monitoring."""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

import requests


class MetricsCollector:
    """Collects metrics from GitHub CI workflows and security scans."""

    def __init__(self, repo: str, token: str, output_dir: str = "metrics_data"):
        self.repo = repo
        self.token = token
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        }
        self.base_url = f"https://api.github.com/repos/{repo}"

    def collect_ci_metrics(self) -> Dict[str, Any]:
        """Collect CI/CD workflow metrics."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "workflow_runs_total": self._get_workflow_count(),
            "workflow_success_rate": self._get_success_rate(),
            "average_duration_seconds": self._get_avg_duration(),
            "builds_per_day": self._get_builds_per_day(),
            "cache_hit_rate": 0.85,  # Placeholder - would query cache stats
            "failed_workflows": self._get_failed_workflows(),
        }
        return metrics

    def collect_security_metrics(self) -> Dict[str, Any]:
        """Collect security scan metrics."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "vulnerabilities_total": self._get_vuln_count(),
            "vulnerabilities_by_severity": self._get_vuln_breakdown(),
            "security_score": self._calculate_security_score(),
            "dependabot_alerts": self._get_dependabot_count(),
            "codeql_alerts": self._get_codeql_count(),
            "last_security_scan": self._get_last_scan_time(),
        }
        return metrics

    def collect_agent_metrics(self) -> Dict[str, Any]:
        """Collect custom agent performance metrics."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "ml_threat_detections": 0,  # Would query ML model logs
            "ci_diagnostic_runs": self._count_diagnostic_runs(),
            "auto_fixes_applied": 0,  # Would track from cognitive brain
            "pattern_recognition_accuracy": 0.87,  # Would calculate from results
        }
        return metrics

    def save_metrics(self, metrics_type: str, metrics: Dict[str, Any]) -> None:
        """Save metrics to JSON file."""
        filename = f"{metrics_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)

        print(f"✅ Metrics saved to {filepath}")

    def collect_all(self) -> Dict[str, Any]:
        """Collect all metrics at once."""
        return {
            "ci": self.collect_ci_metrics(),
            "security": self.collect_security_metrics(),
            "agents": self.collect_agent_metrics(),
        }

    def _get_workflow_count(self) -> int:
        """Get total workflow run count."""
        try:
            url = f"{self.base_url}/actions/runs"
            response = requests.get(url, headers=self.headers, params={"per_page": 1}, timeout=10)
            if response.status_code == 200:
                return response.json().get("total_count", 0)
        except Exception as e:
            print(f"Warning: Could not fetch workflow count: {e}")
        return 0

    def _get_success_rate(self) -> float:
        """Calculate workflow success rate."""
        try:
            url = f"{self.base_url}/actions/runs"
            response = requests.get(url, headers=self.headers, params={"per_page": 100}, timeout=10)
            if response.status_code == 200:
                runs = response.json().get("workflow_runs", [])
                if not runs:
                    return 1.0

                successful = sum(1 for run in runs if run.get("conclusion") == "success")
                return successful / len(runs)
        except Exception as e:
            print(f"Warning: Could not calculate success rate: {e}")
        return 0.0

    def _get_avg_duration(self) -> float:
        """Calculate average workflow duration in seconds."""
        try:
            url = f"{self.base_url}/actions/runs"
            response = requests.get(url, headers=self.headers, params={"per_page": 100}, timeout=10)
            if response.status_code == 200:
                runs = response.json().get("workflow_runs", [])
                if not runs:
                    return 0.0

                durations = []
                for run in runs:
                    created = datetime.fromisoformat(run["created_at"].replace("Z", "+00:00"))
                    updated = datetime.fromisoformat(run["updated_at"].replace("Z", "+00:00"))
                    duration = (updated - created).total_seconds()
                    durations.append(duration)

                return sum(durations) / len(durations) if durations else 0.0
        except Exception as e:
            print(f"Warning: Could not calculate avg duration: {e}")
        return 0.0

    def _get_builds_per_day(self) -> int:
        """Calculate average builds per day."""
        try:
            url = f"{self.base_url}/actions/runs"
            yesterday = (datetime.now() - timedelta(days=1)).isoformat()
            params = {"created": f">={yesterday}", "per_page": 100}
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            if response.status_code == 200:
                return len(response.json().get("workflow_runs", []))
        except Exception as e:
            print(f"Warning: Could not get builds per day: {e}")
        return 0

    def _get_failed_workflows(self) -> List[str]:
        """Get list of recently failed workflows."""
        try:
            url = f"{self.base_url}/actions/runs"
            params = {"status": "completed", "per_page": 10}
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            if response.status_code == 200:
                runs = response.json().get("workflow_runs", [])
                return [run["name"] for run in runs if run.get("conclusion") == "failure"]
        except Exception as e:
            print(f"Warning: Could not get failed workflows: {e}")
        return []

    def _get_vuln_count(self) -> int:
        """Get total vulnerability count."""
        return self._get_codeql_count() + self._get_dependabot_count()

    def _get_vuln_breakdown(self) -> Dict[str, int]:
        """Get vulnerabilities by severity."""
        # Simplified - would aggregate from actual alerts
        return {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        }

    def _calculate_security_score(self) -> int:
        """Calculate overall security score (0-100)."""
        vuln_count = self._get_vuln_count()

        # Simple scoring: Start at 100, deduct points for vulnerabilities
        score = 100
        score -= min(vuln_count * 5, 50)  # Max 50 point deduction

        return max(0, score)

    def _get_dependabot_count(self) -> int:
        """Get Dependabot alert count."""
        try:
            url = f"{self.base_url}/dependabot/alerts"
            response = requests.get(url, headers=self.headers, params={"state": "open"}, timeout=10)
            if response.status_code == 200:
                return len(response.json())
        except Exception:
            # Silently fail if Dependabot API is unavailable or returns an error
            # This is expected for repos without Dependabot enabled
            pass
        return 0

    def _get_codeql_count(self) -> int:
        """Get CodeQL alert count."""
        try:
            url = f"{self.base_url}/code-scanning/alerts"
            response = requests.get(url, headers=self.headers, params={"state": "open"}, timeout=10)
            if response.status_code == 200:
                return len(response.json())
        except Exception:
            # Silently fail if CodeQL API is unavailable or returns an error
            # This is expected for repos without code scanning enabled
            pass
        return 0

    def _get_last_scan_time(self) -> str:
        """Get timestamp of last security scan."""
        try:
            url = f"{self.base_url}/code-scanning/alerts"
            response = requests.get(
                url,
                headers=self.headers,
                params={"per_page": 1, "sort": "created", "direction": "desc"},
                timeout=10,
            )
            if response.status_code == 200:
                alerts = response.json()
                if alerts:
                    return alerts[0].get("created_at", "")
        except Exception:
            # Silently fail if code scanning API is unavailable or returns an error
            # Return current time as fallback
            pass
        return datetime.now().isoformat()

    def _count_diagnostic_runs(self) -> int:
        """Count CI diagnostic agent runs."""
        # Would query workflow runs for ci-diagnostic-automation
        return 0


def main():
    """Main collection loop."""
    import sys

    if len(sys.argv) < 3:
        print("Usage: python metrics_collector.py <repo> <token>")
        sys.exit(1)

    collector = MetricsCollector(sys.argv[1], sys.argv[2])

    print("Starting metrics collection (30s intervals)...")

    try:
        while True:
            print(f"\n[{datetime.now()}] Collecting metrics...")

            # Collect all metrics
            all_metrics = collector.collect_all()

            # Save to files
            for metrics_type, metrics in all_metrics.items():
                collector.save_metrics(metrics_type, metrics)

            # Print summary
            print(f"CI Success Rate: {all_metrics['ci']['workflow_success_rate']:.1%}")
            print(f"Security Score: {all_metrics['security']['security_score']}/100")
            print(f"Total Vulnerabilities: {all_metrics['security']['vulnerabilities_total']}")

            # Wait 30 seconds
            time.sleep(30)

    except KeyboardInterrupt:
        print("\n✅ Metrics collection stopped")


if __name__ == "__main__":
    main()
