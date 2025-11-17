# AWS SageMaker Deployment Guide

This document summarises the steps required to deploy Codex ML models on Amazon SageMaker.

## 1. Package the model artefacts

* Export the fine-tuned weights and tokenizer to an S3 bucket.
* Include the `artifacts/metrics.ndjson` and session evidence for audit trails.

## 2. Build the inference container

Create a SageMaker-compatible image based on the Codex runtime:

```bash
aws sagemaker create-image-version \
  --image-name codex-ml \
  --base-image-uri <account>.dkr.ecr.<region>.amazonaws.com/codex-ml:latest
```text

Ensure the container exposes `/invocations` and `/ping` endpoints. Mount the metrics exporter to `/metrics` for
Prometheus scraping via Amazon Managed Service for Prometheus (AMP).

## 3. Define the model and endpoint configuration

```bash
aws sagemaker create-model \
  --model-name codex-ml \
  --primary-container Image=<image-uri>,ModelDataUrl=s3://bucket/model.tar.gz

aws sagemaker create-endpoint-config \
  --endpoint-config-name codex-ml-config \
  --production-variants VariantName=AllTraffic,ModelName=codex-ml,InitialInstanceCount=1,InstanceType=ml.g5.2xlarge
```text

Enable data capture for compliance by setting `EnableCapture=true` on the endpoint configuration. Route captured
payloads to S3 and apply the session ID headers to correlate with Codex logs.

## 4. Launch the endpoint

```bash
aws sagemaker create-endpoint \
  --endpoint-name codex-ml \
  --endpoint-config-name codex-ml-config
```text

Monitor the endpoint using CloudWatch metrics and forward Prometheus data to AMP. When deploying to multiple
regions, share the `.codex/evidence/phase5_*.jsonl` artefacts with the operations team for traceability.
