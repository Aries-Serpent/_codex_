# Kubernetes Deployment Guide

This guide outlines the key components required to run Codex ML on Kubernetes using Helm or raw manifests.

## 1. Container image

Publish a container that bundles the Codex runtime and enables telemetry:

```bash
docker build -t ghcr.io/example/codex-ml:latest .
docker push ghcr.io/example/codex-ml:latest
```text

## 2. Helm chart skeleton

Create a chart that defines the deployment, service, and optional ingress resources:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: codex-ml
spec:
  replicas: 2
  selector:
    matchLabels:
      app: codex-ml
  template:
    metadata:
      labels:
        app: codex-ml
    spec:
      containers:
        - name: codex
          image: ghcr.io/example/codex-ml:latest
          env:
            - name: CODEX_METRICS_ENABLED
              value: "1"
          ports:
            - containerPort: 8000
```text

Expose `/metrics`, `/health`, and `/ready` through a ClusterIP or Ingress. Attach Prometheus annotations to the
pod metadata to auto-discover the metrics endpoint.

## 3. Secrets and configuration

* Mount TLS certificates via Kubernetes Secrets (`tls.key`/`tls.crt`).
* Supply API keys through Secrets or External Secrets operators; the in-process `SecretRedactor` protects logs if
  verbose debugging is required.
* Use ConfigMaps to template Hydra configs and `CODEX_SESSION_ID` defaults.

## 4. Observability

* Scrape Prometheus metrics using the ServiceMonitor CRD (Prometheus Operator) or pod annotations.
* Stream `.codex/logs` and `.codex/health` directories with a sidecar such as Fluent Bit.
* Configure alerts on the `codex_ml_active_sessions` gauge and health probe failures.
