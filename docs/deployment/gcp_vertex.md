# Google Cloud Vertex AI Deployment Guide

Deploy Codex ML models to Vertex AI for managed training and online prediction.

## 1. Upload model artefacts

```bash
gsutil cp -r artifacts/model gs://<bucket>/codex/model
```text

Include telemetry logs and evidence files to satisfy internal audit requirements.

## 2. Build a custom prediction container

Create a Container Registry image that wraps the Codex inference server:

```bash
gcloud builds submit --tag gcr.io/<project>/codex-ml:latest .
```text

Expose `/predict`, `/health`, and `/metrics` endpoints inside the container. Ensure `CODEX_METRICS_ENABLED=1`
so the Prometheus exporter is live when the model is deployed.

## 3. Create the model resource

```bash
gcloud ai models upload \
  --region=<region> \
  --display-name=codex-ml \
  --container-image-uri=gcr.io/<project>/codex-ml:latest \
  --artifact-uri=gs://<bucket>/codex/model
```text

## 4. Deploy an endpoint

```bash
gcloud ai endpoints create --region=<region> --display-name=codex-ml

gcloud ai endpoints deploy-model <endpoint-id> \
  --region=<region> \
  --display-name=codex-ml \
  --model=<model-id> \
  --machine-type=n1-standard-16 \
  --min-replica-count=1 \
  --max-replica-count=3
```text

Attach a Cloud Armor policy or Identity-Aware Proxy (IAP) for access control and use Cloud Monitoring dashboards to
watch the `codex_ml_active_sessions` gauge.
