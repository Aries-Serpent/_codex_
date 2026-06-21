#!/usr/bin/env python3
"""
Generate Kubernetes ServiceMonitor resources for Prometheus scraping.
This script generates ServiceMonitor CRDs for application services,
K8s system metrics, and custom application metrics.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml


def generate_servicemonitor_crd(
    name: str,
    namespace: str,
    labels: Dict[str, str],
    selectors: Dict[str, str],
    port: str,
    interval: str = "30s",
    scrape_timeout: str = "10s",
    relabel_configs: List[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Generate a ServiceMonitor CRD."""
    if relabel_configs is None:
        relabel_configs = []

    return {
        "apiVersion": "monitoring.coreos.com/v1",
        "kind": "ServiceMonitor",
        "metadata": {"name": name, "namespace": namespace, "labels": labels},
        "spec": {
            "selector": {"matchLabels": selectors},
            "endpoints": [
                {
                    "port": port,
                    "interval": interval,
                    "scrapeTimeout": scrape_timeout,
                    "relabelings": relabel_configs,
                }
            ],
        },
    }


def generate_servicemonitors() -> List[Dict[str, Any]]:
    """Generate all ServiceMonitor resources."""
    monitors = []

    # Application services (port 8080 - HTTP metrics)
    monitors.append(
        generate_servicemonitor_crd(
            name="app-service-http",
            namespace="default",
            labels={"monitoring": "enabled"},
            selectors={"app": "backend", "metrics-port": "http"},
            port="http",
            interval="30s",
            relabel_configs=[
                {
                    "sourceLabels": ["__meta_kubernetes_namespace"],
                    "action": "replace",
                    "targetLabel": "kubernetes_namespace",
                },
                {
                    "sourceLabels": ["__meta_kubernetes_pod_name"],
                    "action": "replace",
                    "targetLabel": "kubernetes_pod_name",
                },
            ],
        )
    )

    # Application services (port 9090 - Prometheus metrics)
    monitors.append(
        generate_servicemonitor_crd(
            name="app-service-prometheus",
            namespace="default",
            labels={"monitoring": "enabled"},
            selectors={"app": "backend", "metrics-port": "prometheus"},
            port="prometheus",
            interval="30s",
            relabel_configs=[
                {
                    "sourceLabels": ["__meta_kubernetes_namespace"],
                    "action": "replace",
                    "targetLabel": "kubernetes_namespace",
                },
                {
                    "sourceLabels": ["__meta_kubernetes_pod_name"],
                    "action": "replace",
                    "targetLabel": "kubernetes_pod_name",
                },
            ],
        )
    )

    # K8s API Server
    monitors.append(
        generate_servicemonitor_crd(
            name="kubernetes-apiserver",
            namespace="kube-system",
            labels={"k8s-app": "apiserver"},
            selectors={"component": "kube-apiserver"},
            port="https",
            interval="60s",
            relabel_configs=[
                {
                    "sourceLabels": ["__meta_kubernetes_namespace"],
                    "action": "replace",
                    "targetLabel": "kubernetes_namespace",
                },
            ],
        )
    )

    # Kubelet
    monitors.append(
        generate_servicemonitor_crd(
            name="kubernetes-kubelet",
            namespace="kube-system",
            labels={"k8s-app": "kubelet"},
            selectors={"k8s-app": "kubelet"},
            port="https-metrics",
            interval="60s",
            scrape_timeout="30s",
            relabel_configs=[
                {
                    "sourceLabels": ["__meta_kubernetes_node_name"],
                    "action": "replace",
                    "targetLabel": "node",
                },
            ],
        )
    )

    # Custom application metrics (port 8081)
    monitors.append(
        generate_servicemonitor_crd(
            name="custom-app-metrics",
            namespace="default",
            labels={"app": "custom-metrics"},
            selectors={"app": "custom-metrics"},
            port="metrics",
            interval="30s",
            relabel_configs=[
                {
                    "sourceLabels": ["__meta_kubernetes_namespace"],
                    "action": "replace",
                    "targetLabel": "namespace",
                },
                {
                    "sourceLabels": ["__meta_kubernetes_pod_name"],
                    "action": "replace",
                    "targetLabel": "pod",
                },
            ],
        )
    )

    return monitors


def generate_prometheus_scrape_config() -> Dict[str, Any]:
    """Generate Prometheus scrape configuration."""
    return {
        "global": {
            "scrape_interval": "30s",
            "evaluation_interval": "30s",
            "external_labels": {"cluster": "kubernetes", "environment": "production"},
        },
        "scrape_configs": [
            {
                "job_name": "prometheus",
                "static_configs": [{"targets": ["localhost:9090"]}],
            },
            {
                "job_name": "kubernetes-apiservers",
                "kubernetes_sd_configs": [{"role": "endpoints"}],
                "scheme": "https",
                "tls_config": {"ca_file": "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"},
                "bearer_token_file": "/var/run/secrets/kubernetes.io/serviceaccount/token",
                "relabel_configs": [
                    {
                        "source_labels": [
                            "__meta_kubernetes_namespace",
                            "__meta_kubernetes_service_name",
                            "__meta_kubernetes_endpoint_port_name",
                        ],
                        "action": "keep",
                        "regex": "default;kubernetes;https",
                    }
                ],
            },
            {
                "job_name": "kubernetes-nodes",
                "scheme": "https",
                "tls_config": {"ca_file": "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"},
                "bearer_token_file": "/var/run/secrets/kubernetes.io/serviceaccount/token",
                "kubernetes_sd_configs": [{"role": "node"}],
                "relabel_configs": [
                    {"action": "labelmap", "regex": "__meta_kubernetes_node_label_(.+)"},
                    {
                        "target_label": "__address__",
                        "replacement": "kubernetes.default.svc:443",
                    },
                    {
                        "source_labels": ["__meta_kubernetes_node_name"],
                        "regex": "(.+)",
                        "target_label": "__metrics_path__",
                        "replacement": "/api/v1/nodes/${1}/proxy/metrics",
                    },
                ],
            },
            {
                "job_name": "kubernetes-pods",
                "kubernetes_sd_configs": [{"role": "pod"}],
                "relabel_configs": [
                    {
                        "source_labels": ["__meta_kubernetes_pod_annotation_prometheus_io_scrape"],
                        "action": "keep",
                        "regex": "true",
                    },
                    {
                        "source_labels": ["__meta_kubernetes_pod_annotation_prometheus_io_path"],
                        "action": "replace",
                        "target_label": "__metrics_path__",
                        "regex": "(.+)",
                    },
                    {
                        "source_labels": ["__address__", "__meta_kubernetes_pod_annotation_prometheus_io_port"],
                        "action": "replace",
                        "regex": "([^:]+)(?::\\d+)?;(\\d+)",
                        "replacement": "$1:$2",
                        "target_label": "__address__",
                    },
                    {"action": "labelmap", "regex": "__meta_kubernetes_pod_label_(.+)"},
                    {
                        "source_labels": ["__meta_kubernetes_namespace"],
                        "action": "replace",
                        "target_label": "kubernetes_namespace",
                    },
                    {
                        "source_labels": ["__meta_kubernetes_pod_name"],
                        "action": "replace",
                        "target_label": "kubernetes_pod_name",
                    },
                ],
            },
        ],
    }


def main():
    """Main function."""
    # Create output directory
    output_dir = Path(__file__).parent.parent.parent / "manifests" / "monitoring" / "prometheus" / "servicemonitors"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate ServiceMonitor resources
    monitors = generate_servicemonitors()

    for monitor in monitors:
        filename = output_dir / f"{monitor['metadata']['name']}.yaml"
        with open(filename, "w") as f:
            yaml.dump([monitor], f, default_flow_style=False)
        print(f"✅ Generated: {filename.relative_to(Path.cwd())}")

    # Generate Prometheus scrape config
    scrape_config = generate_prometheus_scrape_config()
    scrape_config_file = output_dir.parent / "scrape-config.yaml"
    with open(scrape_config_file, "w") as f:
        yaml.dump(scrape_config, f, default_flow_style=False)
    print(f"✅ Generated: {scrape_config_file.relative_to(Path.cwd())}")

    # Generate summary
    summary = {
        "servicemonitors_generated": len(monitors),
        "servicemonitors": [m["metadata"]["name"] for m in monitors],
        "scrape_targets": [sc["job_name"] for sc in scrape_config["scrape_configs"]],
        "output_directory": str(output_dir),
    }

    summary_file = output_dir.parent / "servicemonitor-summary.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"✅ Generated summary: {summary_file.relative_to(Path.cwd())}")

    print("\n📊 Summary:")
    print(f"  - ServiceMonitors: {summary['servicemonitors_generated']}")
    print(f"  - Scrape targets: {len(summary['scrape_targets'])}")
    print(f"  - Output directory: {summary['output_directory']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
