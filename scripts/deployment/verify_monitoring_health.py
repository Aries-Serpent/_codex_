#!/usr/bin/env python3
"""
Verify monitoring stack health and operational status.
This script checks all monitoring components and reports on their status.
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple


def check_endpoint_health(url: str, timeout: int = 5) -> Tuple[bool, str]:
    """Check if an endpoint is healthy."""
    try:
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "-m", str(timeout), url],
            capture_output=True,
            text=True,
            timeout=timeout + 2,
        )
        status_code = result.stdout.strip()
        if status_code in ["200", "204"]:
            return True, f"OK ({status_code})"
        else:
            return False, f"HTTP {status_code}"
    except Exception as e:
        return False, str(e)


def check_prometheus_health() -> Dict[str, Any]:
    """Check Prometheus health."""
    print("🔍 Checking Prometheus...")
    
    healthy, message = check_endpoint_health("http://prometheus:9090/-/healthy")
    
    result = {
        "component": "Prometheus",
        "healthy": healthy,
        "endpoint": "http://prometheus:9090/-/healthy",
        "status": message,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    if healthy:
        # Check if metrics are being scraped
        try:
            curl_result = subprocess.run(
                ["curl", "-s", "http://prometheus:9090/api/v1/targets?state=active"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if curl_result.returncode == 0:
                data = json.loads(curl_result.stdout)
                targets = data.get("data", {}).get("activeTargets", [])
                result["active_targets"] = len(targets)
                result["details"] = f"{len(targets)} active scrape targets"
            else:
                result["details"] = "Could not retrieve targets"
        except Exception as e:
            result["details"] = f"Error querying targets: {e}"
    
    return result


def check_grafana_health() -> Dict[str, Any]:
    """Check Grafana health."""
    print("🔍 Checking Grafana...")
    
    healthy, message = check_endpoint_health("http://grafana:3000/api/health")
    
    result = {
        "component": "Grafana",
        "healthy": healthy,
        "endpoint": "http://grafana:3000/api/health",
        "status": message,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    if healthy:
        # Try to get Grafana version
        try:
            curl_result = subprocess.run(
                ["curl", "-s", "http://grafana:3000/api/health"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if curl_result.returncode == 0:
                data = json.loads(curl_result.stdout)
                result["details"] = f"Database: {data.get('database', 'unknown')}"
            else:
                result["details"] = "Could not retrieve version info"
        except Exception as e:
            result["details"] = f"Error querying health: {e}"
    
    return result


def check_alertmanager_health() -> Dict[str, Any]:
    """Check AlertManager health."""
    print("🔍 Checking AlertManager...")
    
    healthy, message = check_endpoint_health("http://alertmanager:9093/-/healthy")
    
    result = {
        "component": "AlertManager",
        "healthy": healthy,
        "endpoint": "http://alertmanager:9093/-/healthy",
        "status": message,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    if healthy:
        # Check active alerts
        try:
            curl_result = subprocess.run(
                ["curl", "-s", "http://alertmanager:9093/api/v1/alerts"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if curl_result.returncode == 0:
                data = json.loads(curl_result.stdout)
                alerts = data.get("data", [])
                active_alerts = [a for a in alerts if a.get("status", {}).get("state") == "active"]
                result["active_alerts"] = len(active_alerts)
                result["details"] = f"{len(active_alerts)} active alerts"
            else:
                result["details"] = "Could not retrieve alerts"
        except Exception as e:
            result["details"] = f"Error querying alerts: {e}"
    
    return result


def check_kubernetes_resources() -> Dict[str, Any]:
    """Check Kubernetes resources."""
    print("🔍 Checking Kubernetes resources...")
    
    result = {
        "component": "Kubernetes Resources",
        "checks": [],
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    # Check namespace
    try:
        ns_result = subprocess.run(
            ["kubectl", "get", "ns", "monitoring", "-o", "json"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if ns_result.returncode == 0:
            result["checks"].append({"resource": "monitoring namespace", "status": "exists"})
        else:
            result["checks"].append({"resource": "monitoring namespace", "status": "missing"})
    except Exception as e:
        result["checks"].append({"resource": "monitoring namespace", "status": f"error: {e}"})
    
    # Check deployments
    try:
        deploy_result = subprocess.run(
            ["kubectl", "get", "deployments", "-n", "monitoring", "-o", "json"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if deploy_result.returncode == 0:
            data = json.loads(deploy_result.stdout)
            for item in data.get("items", []):
                name = item["metadata"]["name"]
                ready = item["status"].get("readyReplicas", 0)
                desired = item["spec"]["replicas"]
                status = "ready" if ready == desired else f"{ready}/{desired} ready"
                result["checks"].append({"resource": f"deployment/{name}", "status": status})
        else:
            result["checks"].append({"resource": "deployments", "status": "error"})
    except Exception as e:
        result["checks"].append({"resource": "deployments", "status": f"error: {e}"})
    
    # Check PVCs
    try:
        pvc_result = subprocess.run(
            ["kubectl", "get", "pvc", "-n", "monitoring", "-o", "json"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if pvc_result.returncode == 0:
            data = json.loads(pvc_result.stdout)
            for item in data.get("items", []):
                name = item["metadata"]["name"]
                phase = item["status"].get("phase", "unknown")
                result["checks"].append({"resource": f"pvc/{name}", "status": phase})
        else:
            result["checks"].append({"resource": "pvcs", "status": "error"})
    except Exception as e:
        result["checks"].append({"resource": "pvcs", "status": f"error: {e}"})
    
    return result


def check_metrics_collection() -> Dict[str, Any]:
    """Check if metrics are being collected."""
    print("🔍 Checking metrics collection...")
    
    result = {
        "component": "Metrics Collection",
        "checks": [],
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    # Check if Prometheus has recent data
    try:
        curl_result = subprocess.run(
            ["curl", "-s", "http://prometheus:9090/api/v1/query?query=up"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if curl_result.returncode == 0:
            data = json.loads(curl_result.stdout)
            if data.get("status") == "success":
                result_data = data.get("data", {}).get("result", [])
                result["checks"].append({
                    "metric": "up",
                    "status": f"{len(result_data)} series found",
                })
            else:
                result["checks"].append({"metric": "up", "status": "query failed"})
        else:
            result["checks"].append({"metric": "up", "status": "connection failed"})
    except Exception as e:
        result["checks"].append({"metric": "up", "status": f"error: {e}"})
    
    # Check for application metrics
    try:
        curl_result = subprocess.run(
            ["curl", "-s", "http://prometheus:9090/api/v1/query?query=http_requests_total"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if curl_result.returncode == 0:
            data = json.loads(curl_result.stdout)
            if data.get("status") == "success":
                result_data = data.get("data", {}).get("result", [])
                result["checks"].append({
                    "metric": "http_requests_total",
                    "status": f"{len(result_data)} series found",
                })
            else:
                result["checks"].append({
                    "metric": "http_requests_total",
                    "status": "no data yet (expected on startup)",
                })
        else:
            result["checks"].append({"metric": "http_requests_total", "status": "connection failed"})
    except Exception as e:
        result["checks"].append({"metric": "http_requests_total", "status": f"error: {e}"})
    
    return result


def check_alert_rules() -> Dict[str, Any]:
    """Check if alert rules are loaded."""
    print("🔍 Checking alert rules...")
    
    result = {
        "component": "Alert Rules",
        "checks": [],
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    # Check if alert rules are loaded in Prometheus
    try:
        curl_result = subprocess.run(
            ["curl", "-s", "http://prometheus:9090/api/v1/rules?type=alert"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if curl_result.returncode == 0:
            data = json.loads(curl_result.stdout)
            if data.get("status") == "success":
                groups = data.get("data", {}).get("groups", [])
                result["checks"].append({
                    "resource": "alert rule groups",
                    "status": f"{len(groups)} groups loaded",
                })
                for group in groups:
                    rules = group.get("rules", [])
                    result["checks"].append({
                        "resource": f"group: {group['name']}",
                        "status": f"{len(rules)} rules",
                    })
            else:
                result["checks"].append({"resource": "alert rules", "status": "query failed"})
        else:
            result["checks"].append({"resource": "alert rules", "status": "connection failed"})
    except Exception as e:
        result["checks"].append({"resource": "alert rules", "status": f"error: {e}"})
    
    return result


def main():
    """Main function."""
    print("🚀 Monitoring Stack Health Verification")
    print(f"⏰ Started at {datetime.utcnow().isoformat()}\n")
    
    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "checks": [],
        "summary": {
            "total_checks": 0,
            "passed": 0,
            "failed": 0,
        },
    }
    
    # Perform all health checks
    health_checks = [
        check_prometheus_health(),
        check_grafana_health(),
        check_alertmanager_health(),
        check_kubernetes_resources(),
        check_metrics_collection(),
        check_alert_rules(),
    ]
    
    results["checks"].extend(health_checks)
    
    # Count results
    for check in health_checks:
        if "healthy" in check:
            results["summary"]["total_checks"] += 1
            if check["healthy"]:
                results["summary"]["passed"] += 1
            else:
                results["summary"]["failed"] += 1
        elif "checks" in check:
            for sub_check in check["checks"]:
                results["summary"]["total_checks"] += 1
                if "ok" in sub_check.get("status", "").lower() or "ready" in sub_check.get("status", "").lower() or "series" in sub_check.get("status", "").lower():
                    results["summary"]["passed"] += 1
                elif "error" in sub_check.get("status", "").lower():
                    results["summary"]["failed"] += 1
    
    # Print results
    print("\n📊 Health Check Results:")
    for check in health_checks:
        component = check.get("component", "Unknown")
        if "healthy" in check:
            status = "✅" if check["healthy"] else "❌"
            print(f"{status} {component}: {check['status']}")
            if "details" in check:
                print(f"   {check['details']}")
        elif "checks" in check:
            print(f"📋 {component}:")
            for sub_check in check["checks"]:
                resource = sub_check.get("resource", "unknown")
                status_msg = sub_check.get("status", "unknown")
                print(f"   - {resource}: {status_msg}")
    
    # Print summary
    print(f"\n📈 Summary:")
    print(f"   Total Checks: {results['summary']['total_checks']}")
    print(f"   Passed: {results['summary']['passed']}")
    print(f"   Failed: {results['summary']['failed']}")
    
    overall_status = "✅ HEALTHY" if results["summary"]["failed"] == 0 else "⚠️  DEGRADED"
    print(f"\n   Overall Status: {overall_status}")
    
    # Save report
    report_path = Path(".codex/MONITORING_HEALTH_VERIFICATION_REPORT.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n✅ Report saved to: {report_path}")
    
    return 0 if results["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
