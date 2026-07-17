# Quick-Start Guides by User Profile

**Version**: v0.2.0
**Last Updated:** 2026-07-11

## 1. Local Developer (90% use case)

**Goal:** Get up and running on laptop in <5 minutes

```bash
# Step 1: Clone repo
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_

# Step 2: Install
pip install -e .

# Step 3: Done! (defaults work)
python -m codex.cli serve
```

**What's happening:**
- All 8 env vars default to localhost
- Redis, Ollama must be running locally (or skip)
- CODEX_LOCAL_LOOPBACK=true allows localhost security bypass
- Perfect for development

**Customization (optional):**
```bash
# Use external services instead
export CODEX_REDIS_HOST=my-redis.local
export CODEX_OLLAMA_HOST=http://my-ollama:11434

# Then run:
python -m codex.cli serve
```

---

## 2. Docker/Container Developer

**Goal:** Run in Docker with local service dependencies

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install Codex
RUN pip install codex

# Set container network defaults
ENV CODEX_REDIS_HOST=redis
ENV CODEX_OLLAMA_HOST=http://ollama:11434
ENV CODEX_INFERENCE_SERVICE_HOST=0.0.0.0
ENV CODEX_LOCAL_LOOPBACK=true

CMD ["python", "-m", "codex.cli", "serve"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
 codex:
 build: .
 environment:
 CODEX_REDIS_HOST: redis
 CODEX_OLLAMA_HOST: http://ollama:11434
 ports:
 - "8000:8000"
 depends_on:
 - redis
 - ollama

 redis:
 image: redis:7-alpine
 ports:
 - "6379:6379"

 ollama:
 image: ollama/ollama
 ports:
 - "11434:11434"
```

**Troubleshooting Docker:**
- Container can't reach host services? Use `host.docker.internal` for Mac/Windows
- On Linux, use `--network host` or add services to docker-compose

---

## 3. Kubernetes/Cloud Operator

**Goal:** Deploy to production Kubernetes with security

```yaml
# codex-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
 name: codex
spec:
 template:
 spec:
 containers:
 - name: codex
 image: codex:latest
 env:
 # Use repository variables (GitHub Settings Variables)
 - name: CODEX_REDIS_HOST
 valueFrom:
 secretKeyRef:
 name: codex-config
 key: redis-host
 - name: CODEX_OLLAMA_HOST
 valueFrom:
 secretKeyRef:
 name: codex-config
 key: ollama-host
 - name: CODEX_INFERENCE_SERVICE_HOST
 value: "0.0.0.0" # Bind all interfaces
 - name: CODEX_LOCAL_LOOPBACK
 value: "false" # Production security
 - name: CODEX_TRUSTED_HOSTS
 value: "*.codex.svc.cluster.local,codex.prod"
```

**Setup Instructions:**
1. Create ConfigMap with service hostnames
2. Create Secret with any sensitive values (future-proofing)
3. Deploy using YAML above
4. Verify with `kubectl logs -l app=codex | grep "Env config"`

---

## 4. CI/CD Pipeline Operator

**Goal:** Inject env vars into GitHub Actions workflows

```yaml
# .github/workflows/deploy.yml
jobs:
 deploy:
 runs-on: ubuntu-latest
 environment:
 name: production
 steps:
 - uses: actions/checkout@v5
 
 # Env vars automatically injected from repository settings
 - name: Deploy
 run: |
 # GitHub Actions injects all CODEX_* variables
 echo "CODEX_REDIS_HOST: ${{ env.CODEX_REDIS_HOST }}"
 echo "CODEX_OLLAMA_HOST: ${{ env.CODEX_OLLAMA_HOST }}"
 python -m codex.cli serve
 env:
 # Explicit override if needed
 CODEX_LOCAL_LOOPBACK: 'false'
```

**GitHub Configuration:**
1. Go to Settings Variables (repository level)
2. Add all 8 CODEX_* variables
3. For different environments (dev/staging/prod):
 - Create GitHub Environments
 - Set environment-specific variables
 - Reference in workflows: `environment: name: production`

---

## 5. Enterprise/Compliance User

**Goal:** Air-gap deployment with offline access

```bash
# Step 1: On internet-connected machine
./scripts/prepare_offline_env.sh
tar -czf wheelhouse.tar.gz wheelhouse/

# Step 2: Transfer to air-gap environment
# (USB drive, secure file transfer, etc.)

# Step 3: On isolated machine
tar -xzf wheelhouse.tar.gz
pip install --no-index --find-links ./wheelhouse codex

# Step 4: Configure for offline
export CODEX_LOCAL_LOOPBACK=false
export ALLOW_NETWORK_CALLS=false
export CODEX_REDIS_HOST=internal-redis.local
export CODEX_OLLAMA_HOST=http://internal-ollama:11434

python -m codex.cli serve
```

**Compliance Checklist:**
- [ ] All dependencies installed from local wheelhouse
- [ ] No external network calls enabled
- [ ] All service hostnames point to internal infrastructure
- [ ] Audit logging enabled for configuration access
- [ ] Network policies enforced (no unexpected outbound)

---

## Next Steps for Your Profile

| Profile | Next Steps |
|---------|-----------|
| **Local Developer** | See `docs/LOCAL_DEV_ENV_SETUP.md` |
| **Container** | See `docs/DOCKER_SETUP.md` |
| **Kubernetes** | See `docs/KUBERNETES_DEPLOYMENT.md` |
| **CI/CD** | See `.github/workflows/` examples |
| **Enterprise** | See `docs/docs/release/OFFLINE_DEPLOYMENT.md` |

---

## Common Setup Issues by Profile

### Local Developer

**Issue:** Connection refused for Redis
```
error: Connection refused: CODEX_REDIS_HOST=localhost:6379
```
**Solution:**
```bash
# Start Redis in another terminal
redis-server
# Or skip Redis for development
export CODEX_REDIS_HOST=skip
```

**Issue:** Can I use services on my office network?
**Answer:** Yes! Set `CODEX_REDIS_HOST=192.168.1.100` (ensure network is accessible and add to CODEX_TRUSTED_HOSTS)

### Docker/Container User

**Issue:** Docker compose fails with "ollama: not found"
```
ERROR: for ollama Cannot start service ollama: driver failed...
```
**Solution:** Ensure docker-compose.yml has `ollama` service defined and service names match env vars

**Issue:** Container can't reach host services
**Solution:**
- Mac/Windows: Use `host.docker.internal` in place of `localhost`
- Linux: Use `--network host` or add services to docker-compose

### Kubernetes User

**Issue:** ConfigMap vs Secret for variables?
**Answer:** Use ConfigMap for non-sensitive (hosts/ports), Secrets for future-proofing if credentials are added later

**Issue:** Pods can't resolve custom hostnames
**Solution:** Add to CoreDNS ConfigMap or use full FQDN (*.service.svc.cluster.local)

### CI/CD Pipeline Operator

**Issue:** Variables not injected into workflow
**Solution:** Confirm variables are set in Settings Variables and job doesn't have `environment` restriction blocking them

**Issue:** Different values needed for different branches
**Answer:** Use GitHub Environments (Settings Environments) and configure branch rules

### Enterprise User

**Issue:** How do I validate air-gap compliance?
**Answer:** Run `./scripts/validate_offline_install.sh` on target machine to verify no external calls

**Issue:** What if our internal services use non-standard ports?
**Answer:** Use full URL format: `CODEX_REDIS_HOST=redis.internal:6380` or `CODEX_OLLAMA_HOST=http://ollama.internal:9999`

---

## Validation Commands

Test your setup with these commands after configuration:

```bash
# Verify environment variables are set
printenv | grep CODEX_

# Test Redis connection
python -c "import redis; r = redis.Redis(host='${CODEX_REDIS_HOST}', port=6379); r.ping()"

# Test Ollama connection
curl -s "${CODEX_OLLAMA_HOST}/api/tags" | head

# Validate configuration
python -m codex.cli config --validate

# Run health check
python -m codex.cli health
```

---

**Last Updated: 2026-07-16
**For:** All User Profiles
**Activation:** 2026-07-10T10:00Z
