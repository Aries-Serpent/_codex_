# TLS and Mutual TLS Configuration

This guide outlines common deployment patterns for securing Codex ML APIs with TLS and mutual TLS (mTLS).

## Self-signed certificates (development)

```bash
openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem \
  -keyout key.pem \
  -days 365 \
  -subj "/CN=localhost"

uvicorn codex_ml.main:app \
  --host 0.0.0.0 \
  --port 8443 \
  --ssl-keyfile key.pem \
  --ssl-certfile cert.pem
```text

## Let's Encrypt / ACME (production)

Use a reverse proxy such as Traefik or Nginx to terminate TLS and automatically renew certificates.

```yaml
services:
  codex:
    image: ghcr.io/example/codex-ml:latest
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.codex.rule=Host(`api.example.com`)"
      - "traefik.http.routers.codex.entrypoints=websecure"
      - "traefik.http.routers.codex.tls.certresolver=letsencrypt"
```text

## Mutual TLS between services

Generate client certificates signed by the same CA and require them at the ingress layer:

```bash
curl https://api.internal:8000/health \
  --cert client-cert.pem \
  --key client-key.pem \
  --cacert ca.pem
```text

Configure the reverse proxy (e.g. Nginx) to validate client certificates:

```nginx
ssl_client_certificate /etc/nginx/certs/ca.pem;
ssl_verify_client on;
```text

## Hardening checklist

* Store private keys in a secrets manager (AWS Secrets Manager, HashiCorp Vault, etc.).
* Rotate certificates regularly and monitor expiry with Prometheus alerts.
* Enforce TLS 1.2+ and disable legacy ciphers.
* Combine mTLS with structured session logging to trace request provenance.
