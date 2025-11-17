# Azure Machine Learning Deployment Guide

Use Azure Machine Learning (Azure ML) to serve Codex ML models with managed compute and monitoring.

## 1. Register model artefacts

```bash
az ml model create \
  --name codex-ml \
  --path artifacts/model \
  --type custom_model
```text

Upload `.codex/evidence/phase5_*.jsonl` alongside the model for compliance evidence.

## 2. Build an Azure Container Registry image

```bash
az acr build --registry <acr-name> --image codex-ml:latest .
```text

Ensure the image exposes `/score` for predictions and `/metrics` for Prometheus scraping.

## 3. Create an online endpoint

```bash
az ml online-endpoint create \
  --name codex-ml \
  --auth-mode aad_token

az ml online-deployment create \
  --name blue \
  --endpoint codex-ml \
  --model codex-ml:1 \
  --image <acr-name>.azurecr.io/codex-ml:latest \
  --instance-type Standard_NC6s_v3 \
  --instance-count 1
```text

## 4. Enable monitoring and logging

* Stream `/metrics` into Azure Monitor or Prometheus via Azure Managed Grafana.
* Export session logs to Azure Blob Storage for retention policies.
* Leverage Azure Key Vault for certificate and API key management to complement the in-process `SecretRedactor`.
