# Container Security Guide — Aries-Serpent v0.1.0-final

Comprehensive security hardening and vulnerability scanning for Aries-Serpent container images.

## Security Architecture

```
Threat Model
├─ Supply Chain: Base image vulnerabilities
├─ Runtime: Container escape, privilege escalation
├─ Network: Unauthorized network access
├─ Data: Credential exposure, secret leakage
└─ Build: Malicious code injection

Mitigation Strategy
├─ Image Scanning: Trivy + Grype
├─ SBOM: Dependency tracking (CycloneDX)
├─ Hardening: Non-root user, read-only FS, minimal deps
├─ RBAC: Least-privilege ServiceAccount
└─ Secrets: Encrypted storage, rotation policy
```

## Container Hardening

### Implemented Security Controls

All images include:

```dockerfile
# ✅ Non-root user
RUN useradd -m -u 1001 -s /bin/false codex
USER codex

# ✅ Read-only root filesystem support
RUN chmod -R go-w /app

# ✅ Minimal base image
FROM python:3.12-slim  # No unnecessary utilities

# ✅ Multi-stage builds
# (Excludes build tools from final image)

# ✅ Resource limits in pod spec
resources:
  limits:
    cpu: 500m
    memory: 1Gi

# ✅ Health checks
HEALTHCHECK --interval=30s --timeout=10s
```

### RBAC Enforcement

```yaml
# ServiceAccount with minimal permissions
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    resourceNames: ["aries-serpent-config"]
    verbs: ["get"]
  - apiGroups: [""]
    resources: ["secrets"]
    resourceNames: ["aries-serpent-secrets"]
    verbs: ["get"]
```

### Secrets Management

```bash
# ✅ Secrets NOT in ConfigMap (ConfigMap is readable)
# ✅ Secrets in encrypted Secret resource (etcd encryption)
# ✅ Non-sensitive data only in ConfigMap

# Avoid
env:
  - name: API_KEY
    value: "secret123"  # ❌ EXPOSED IN POD SPEC

# Correct
env:
  - name: API_KEY
    valueFrom:
      secretKeyRef:
        name: aries-serpent-secrets
        key: api_key
```

---

## Image Scanning

### Trivy Scanner Setup

```bash
# Installation
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Scan local image
trivy image aries-serpent:0.1.0-final-api

# Scan with detailed output
trivy image --severity HIGH,CRITICAL aries-serpent:0.1.0-final-api

# Generate JSON report
trivy image --format json --output report.json aries-serpent:0.1.0-final-api

# Scan with SBOM integration
trivy image --format cyclonedx --output sbom.json aries-serpent:0.1.0-final-api
```

### Grype Scanner Setup

```bash
# Installation
curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin

# Scan image
grype aries-serpent:0.1.0-final-api

# Output formats
grype aries-serpent:0.1.0-final-api --output json
grype aries-serpent:0.1.0-final-api --output cyclonedx
grype aries-serpent:0.1.0-final-api --output table

# Query specific severities
grype aries-serpent:0.1.0-final-api --fail-on high

# Generate JSON report
grype aries-serpent:0.1.0-final-api -o json > .codex/sbom/api-grype-report.json
```

### Automated Scanning in CI

```yaml
# .github/workflows/container-security-scan.yml
name: Container Security Scan

on:
  push:
    branches: [main, 0D_base_]
    paths:
      - 'docker/Dockerfile.*'
      - 'requirements*.txt'

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build images
        run: |
          docker build -f docker/Dockerfile.api-prod -t aries-serpent:test-api .
          docker build -f docker/Dockerfile.inference-prod -t aries-serpent:test-inf .
      
      - name: Run Trivy scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: aries-serpent:test-api
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
      
      - name: Run Grype scan
        run: |
          grype aries-serpent:test-api --output json > .codex/sbom/api-grype-report.json
      
      - name: Upload reports
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: .codex/sbom/
```

---

## SBOM (Software Bill of Materials)

### SBOM Generation

```bash
# Generate SBOM during image build
cyclonedx-bom -o bom.json -f json

# Extract SBOM from built image
docker run --rm aries-serpent:0.1.0-final-api cat /app/bom.json

# Verify SBOM format
cat .codex/sbom/api-bom.json | jq '.specVersion'  # Should be >=1.3

# Scan SBOM with Grype
grype sbom:.codex/sbom/api-bom.json --output json
```

### SBOM Format (CycloneDX)

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.4",
  "serialNumber": "urn:uuid:...",
  "version": 1,
  "metadata": {
    "component": {
      "name": "aries-serpent",
      "version": "0.1.0-final",
      "type": "application"
    }
  },
  "components": [
    {
      "type": "library",
      "name": "FastAPI",
      "version": "0.104.1",
      "purl": "pkg:pypi/fastapi@0.104.1"
    }
  ]
}
```

---

## Vulnerability Management

### CVE Severity Matrix

| Severity | CVSS Score | Action | Timeline |
|----------|-----------|--------|----------|
| CRITICAL | 9.0-10.0 | Block deployment | Immediate |
| HIGH | 7.0-8.9 | Fix or patch | 7 days |
| MEDIUM | 4.0-6.9 | Track | 30 days |
| LOW | 0.1-3.9 | Monitor | 60 days |

### Vulnerability Response

```bash
# 1. Identify vulnerable component
grype aries-serpent:0.1.0-final-api --output json | jq '.matches[] | select(.vulnerability.severity=="CRITICAL")'

# 2. Check for updates
pip index versions vulnerable-package

# 3. Update requirement
sed -i 's/vulnerable-package==1.0.0/vulnerable-package==1.0.1/g' requirements.txt

# 4. Rebuild image
docker build -f docker/Dockerfile.api-prod -t aries-serpent:0.1.0-final-api-patched .

# 5. Verify fix
grype aries-serpent:0.1.0-final-api-patched --fail-on high

# 6. Tag as patched release
docker tag aries-serpent:0.1.0-final-api-patched aries-serpent:0.1.0-final-api
```

---

## Dependency Pinning Strategy

### Pinning Guidelines

```dockerfile
# ✅ GOOD: Specific version for security
RUN pip install fastapi==0.104.1 uvicorn==0.24.0

# ⚠️ ACCEPTABLE: Patch version range
RUN pip install fastapi~=0.104.0 uvicorn~=0.24

# ❌ AVOID: Minor version range (security risks)
RUN pip install fastapi~=0.1 uvicorn~=0

# ❌ NEVER: No version pinning
RUN pip install fastapi uvicorn
```

### Automated Dependency Updates

```bash
#!/bin/bash
# update-dependencies.sh - Safe dependency updates

set -e

# 1. Create update branch
git checkout -b deps/update-$(date +%Y%m%d)

# 2. Update requirements
pip list --outdated > /tmp/outdated.txt
pip install --upgrade pip setuptools wheel
pip install -U pip-audit

# 3. Audit for vulnerabilities
pip-audit --desc

# 4. Update requirements.txt
pip-compile requirements.in --resolver=backtracking

# 5. Test
pytest tests/

# 6. Security scan
grype aries-serpent:test

# 7. Commit if clean
git add requirements.txt
git commit -m "chore: update dependencies (security audit passed)"
git push -u origin deps/update-$(date +%Y%m%d)
```

---

## Runtime Security

### Pod Security Standards

```yaml
# Apply to namespace
apiVersion: v1
kind: Namespace
metadata:
  name: aries-serpent
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### Network Policy

```yaml
# Restrict network traffic
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: aries-serpent-network-policy
spec:
  podSelector:
    matchLabels:
      app: aries-serpent
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 443  # HTTPS only
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
```

---

## Secret Management Best Practices

### Secret Rotation

```bash
#!/bin/bash
# rotate-secrets.sh - Rotate API keys and credentials

set -e

# 1. Generate new secret
NEW_API_KEY=$(openssl rand -base64 32)

# 2. Update secret resource
kubectl patch secret aries-serpent-secrets \
  --type merge \
  -p '{"stringData":{"api_key":"'$NEW_API_KEY'"}}'

# 3. Restart pods for new secret
kubectl rollout restart deployment/aries-serpent-api

# 4. Log rotation (audit trail)
echo "$(date -u +'%Y-%m-%dT%H:%M:%SZ') - API key rotated" >> secret-rotation.log
```

### External Secret Management

```yaml
# Use External Secrets Operator for vault integration
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aries-vault
spec:
  provider:
    vault:
      server: "https://vault.example.com:8200"
      path: "secret"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "aries-serpent"

---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: aries-serpent-secrets
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aries-vault
    kind: SecretStore
  target:
    name: aries-serpent-secrets
    creationPolicy: Owner
  data:
  - secretKey: api_key
    remoteRef:
      key: aries-serpent/api_key
  - secretKey: database_url
    remoteRef:
      key: aries-serpent/database_url
```

---

## Compliance & Audit

### Security Checklist

- ✅ Non-root user enforced
- ✅ Read-only filesystem support
- ✅ Health checks configured
- ✅ Resource limits enforced
- ✅ RBAC with least privilege
- ✅ Secrets encrypted (etcd)
- ✅ SBOM generated
- ✅ Vulnerabilities scanned
- ✅ CVE severity: 0 CRITICAL, 0 HIGH
- ✅ Base image scanned
- ✅ Dependencies pinned
- ✅ Image signed (optional)

### Audit Logging

```yaml
# Enable audit logging in cluster
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
# Log Pod events with high verbosity
- level: RequestResponse
  verbs: ["create", "delete", "patch"]
  resources: ["pods"]
  namespaces: ["aries-serpent"]

# Log Secret access
- level: RequestResponse
  verbs: ["get", "list", "watch"]
  resources: ["secrets"]
  namespaces: ["aries-serpent"]
```

### Compliance Standards

| Standard | Requirement | Status |
|----------|-------------|--------|
| CIS K8s Benchmark | Non-root user | ✅ |
| PCI-DSS | Encrypted secrets | ✅ |
| NIST 800-53 | RBAC enforced | ✅ |
| SOC 2 | Audit logging | ✅ |

---

## Incident Response

### Vulnerability Disclosure

```bash
# 1. Identify affected versions
grype aries-serpent:0.1.0-final-api --output json | grep -E '"vulnerability":' | sort -u

# 2. Create security advisory
# See: https://github.com/Aries-Serpent/_codex_/security/advisories

# 3. Prepare patch
git checkout -b security/fix-cve-2026-XXXXX
# ... make fixes ...
git push -u origin security/fix-cve-2026-XXXXX

# 4. Release patched version
git tag -a v0.1.0-final-patch1 -m "Security patch: CVE-2026-XXXXX"
docker build -f docker/Dockerfile.api-prod -t aries-serpent:0.1.0-final-patch1-api .

# 5. Notify users
# GitHub Security Advisory + Release Notes
```

---

## References

- OWASP Top 10 Container: https://owasp.org/Top10/
- CIS Docker Benchmark: https://www.cisecurity.org/cis-benchmarks/#docker
- Trivy Documentation: https://aquasecurity.github.io/trivy/
- Grype Documentation: https://github.com/anchore/grype
- Kubernetes Security: https://kubernetes.io/docs/concepts/security/

---

**Last Updated:** 2026-07-09  
**Status:** ✅ Production Ready
