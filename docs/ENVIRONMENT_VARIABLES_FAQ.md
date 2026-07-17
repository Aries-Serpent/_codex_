# Environment Variables FAQ
**Last Updated:** 2026-07-11
**Version:** v0.2.0

## General Questions

### Q: Do I need to set all 8 environment variables?

**A:** No! All have safe localhost defaults. Set only what you customize.

- **CODEX_REDIS_HOST** defaults to `localhost`
- **CODEX_OLLAMA_HOST** defaults to `http://localhost:11434`
- **CODEX_MASTER_ADDR** defaults to `localhost`
- **CODEX_MASTER_PORT** defaults to `5000`
- **CODEX_INFERENCE_SERVICE_HOST** defaults to `localhost`
- **CODEX_INFERENCE_SERVICE_PORT** defaults to `8000`
- **CODEX_TRUSTED_HOSTS** defaults to `localhost,127.0.0.1`
- **CODEX_LOCAL_LOOPBACK** defaults to `true` (development mode)

### Q: Can I mix environment variables and code defaults?

**A:** Yes! Each variable falls back to hardcoded default if not set. Example:

```python
# In code: defaults to localhost if env var not set
redis_host = os.getenv('CODEX_REDIS_HOST', 'localhost')
```

### Q: Are these variables secrets? Should I store them securely?

**A:** No, these are configuration (not credentials). Safe to commit/version control.

- Don't put passwords/tokens here
- These are just hostnames and port numbers
- Safe to include in git repos
- Can be public in GitHub Settings Variables

### Q: How are these deployed?

**A:** Via GitHub Settings Variables (repository-level configuration).

Steps:
1. Go to Settings Variables
2. Add each CODEX_* variable
3. GitHub Actions automatically injects them into workflows
4. Applications read them via `os.getenv('CODEX_*')`

### Q: Can these be different per branch?

**A:** Yes, via GitHub Environments:
1. Settings Environments
2. Create environment (dev, staging, production)
3. Set environment-specific variables
4. Reference in workflows: `environment: name: production`

---

## Technical Questions

### Q: I set CODEX_REDIS_HOST but it's still using localhost

**A:** Confirm variable is set: `echo $CODEX_REDIS_HOST`

Also check:
- Are you in the right shell? (Variables don't transfer between shell sessions)
- Is the application actually reading this var? (Check logs/debug output)
- Did you restart the application after setting the variable?

```bash
# Verify it's actually set
printenv | grep CODEX_REDIS_HOST

# Set and verify in same line
export CODEX_REDIS_HOST=my-redis && echo $CODEX_REDIS_HOST
```

### Q: What does CODEX_LOCAL_LOOPBACK do?

**A:** Controls localhost allowlist in security policies.

| Value | Mode | Use Case |
|-------|------|----------|
| `true` | Development | Allow localhost without validation (default) |
| `false` | Production | Require real hostnames, block localhost |

**Examples:**
```bash
# Development (allow localhost)
export CODEX_LOCAL_LOOPBACK=true
python -m codex serve  #  localhost:6379 allowed

# Production (enforce hostnames)
export CODEX_LOCAL_LOOPBACK=false
export CODEX_REDIS_HOST=redis.prod.internal
python -m codex serve  #  redis.prod.internal allowed,  localhost blocked
```

### Q: Can I override variables per environment?

**A:** Yes! Three approaches:

**Approach 1: Shell export (for testing)**
```bash
export CODEX_REDIS_HOST=test-redis
python -m pytest  # Uses test-redis
```

**Approach 2: GitHub Environments (for workflows)**
```yaml
jobs:
  deploy:
    environment: production  # Auto-injects prod variables
    runs-on: ubuntu-latest
```

**Approach 3: Docker/compose overrides**
```yaml
services:
  codex-prod:
    environment:
      CODEX_REDIS_HOST: redis.prod
  codex-dev:
    environment:
      CODEX_REDIS_HOST: localhost
```

### Q: What format should the URLs be in?

**A:** Depends on the variable:

```bash
# Hostname only (no protocol)
export CODEX_REDIS_HOST=redis.local
export CODEX_MASTER_ADDR=master.local

# Full URL with protocol
export CODEX_OLLAMA_HOST=http://ollama:11434

# Hostname with port
export CODEX_INFERENCE_SERVICE_HOST=0.0.0.0
export CODEX_INFERENCE_SERVICE_PORT=8000

# Comma-separated list
export CODEX_TRUSTED_HOSTS=localhost,127.0.0.1,myhost.local
```

---

## Deployment Questions

### Q: When should I set CODEX_LOCAL_LOOPBACK=false?

**A:** Only in production. Development should always use `true` (the default).

| Environment | CODEX_LOCAL_LOOPBACK | Reason |
|-------------|----------------------|--------|
| Local dev | `true` | Localhost is fastest for development |
| Docker | `true` | Container localhost is fine for local testing |
| Staging | `false` | Should test production-like security |
| Production | `false` | Required for security validation |

### Q: What if CODEX_TRUSTED_HOSTS blocks my request?

**A:** Add your hostname to comma-separated list:

```bash
# Before (blocks your request)
export CODEX_TRUSTED_HOSTS=localhost,127.0.0.1

# After (allows your-host)
export CODEX_TRUSTED_HOSTS=localhost,127.0.0.1,your-host.local
```

Also check:
- Fully qualified domain name (FQDN) vs short hostname
- Kubernetes services use `servicename.namespace.svc.cluster.local`

### Q: How do I test with custom variables locally?

**A:** Set variables, then run:

```bash
# Set variables inline
export CODEX_REDIS_HOST=custom-host && python -m codex serve

# Or set in .env file and source
# .env:
# CODEX_REDIS_HOST=custom-host
# CODEX_OLLAMA_HOST=http://custom-ollama:11434

source .env
python -m codex serve
```

### Q: Can I use DNS names or do they need to be IPs?

**A:** DNS names work great! Recommended actually:

```bash
#  Good (DNS resolves at runtime)
export CODEX_REDIS_HOST=redis.internal

#  Also good (IP works)
export CODEX_REDIS_HOST=192.168.1.100

#  Great for Kubernetes
export CODEX_REDIS_HOST=redis.default.svc.cluster.local
```

---

## Troubleshooting

### Q: Tests fail with "localhost not resolvable"

**A:** Likely `CODEX_LOCAL_LOOPBACK=false` in test environment. Solution:

```bash
# Option 1: Set to true for testing
export CODEX_LOCAL_LOOPBACK=true
pytest

# Option 2: Add localhost to allowlist
export CODEX_TRUSTED_HOSTS=localhost,127.0.0.1
pytest
```

### Q: Docker container can't reach services on host

**A:** Docker networking issue. Solutions:

**Mac/Windows:**
```bash
# Use special hostname
export CODEX_REDIS_HOST=host.docker.internal
```

**Linux:**
```bash
# Option 1: Use --network host
docker run --network host codex

# Option 2: Get host IP
HOST_IP=$(hostname -I | awk '{print $1}')
docker run -e CODEX_REDIS_HOST=$HOST_IP codex
```

**Docker Compose:**
```yaml
services:
  codex:
    environment:
      CODEX_REDIS_HOST: redis  # Service name works in compose
    depends_on:
      - redis
  redis:
    image: redis:7-alpine
```

### Q: Kubernetes pods can't resolve custom hostnames

**A:** Kubernetes DNS issue. Solutions:

```bash
# Option 1: Use full FQDN
export CODEX_REDIS_HOST=redis.default.svc.cluster.local

# Option 2: If short name, ensure pod in same namespace
export CODEX_REDIS_HOST=redis  # Same namespace only

# Option 3: Update CoreDNS ConfigMap for custom domains
kubectl edit configmap coredns -n kube-system
# Add custom domain resolution
```

### Q: Application starts but can't connect to services

**A:** Verify connectivity:

```bash
# Test Redis
python -c "import redis; redis.Redis('${CODEX_REDIS_HOST}').ping()"

# Test Ollama
curl -s "${CODEX_OLLAMA_HOST}/api/tags"

# Test Master
python -c "socket.create_connection(('${CODEX_MASTER_ADDR}', ${CODEX_MASTER_PORT}))"

# Check logs
tail -f logs/codex.log | grep -i "redis\|ollama\|master"
```

### Q: Variables work locally but not in CI/CD

**A:** GitHub Actions requires explicit configuration:

```yaml
#  Won't work - variables not injected
- name: Deploy
  run: echo $CODEX_REDIS_HOST

#  Works - explicit reference
- name: Deploy
  run: echo ${{ env.CODEX_REDIS_HOST }}

#  Also works - variable in env
- name: Deploy
  run: echo $CODEX_REDIS_HOST
  env:
    CODEX_REDIS_HOST: ${{ env.CODEX_REDIS_HOST }}
```

---

## Security Questions

### Q: Are these variables safe for version control?

**A:** Yes! They're configuration endpoints, not credentials.

- Safe to commit to git
- Safe to include in public repos
- No sensitive data should be here
- Never put passwords/tokens here

```bash
# Good - just hostnames
CODEX_REDIS_HOST=redis.prod.internal
CODEX_OLLAMA_HOST=http://ollama.prod.internal:11434

# Bad - never put tokens here
CODEX_AUTH_TOKEN=sk_prod_abc123  #  Don't do this!
```

### Q: Should CODEX_LOCAL_LOOPBACK ever be true in production?

**A:** Never! Production must always set `CODEX_LOCAL_LOOPBACK=false`.

```bash
# Development OK
export CODEX_LOCAL_LOOPBACK=true  #  Development

# Production REQUIRED
export CODEX_LOCAL_LOOPBACK=false  #  Production (required)
```

**Why?** Localhost bypass disables security validations that are critical in production.

### Q: How do I audit which variables are set?

**A:** Use `printenv` with grep:

```bash
# List all Codex variables
printenv | grep CODEX_

# Check specific variable
echo $CODEX_REDIS_HOST

# In logs, verify which were loaded
python -m codex --show-config  # Shows actual loaded config
```

### Q: What if variables contain sensitive data (future)?

**A:** Use Secrets instead:

```yaml
# GitHub Actions
- name: Deploy
  env:
    # For future credential variables
    CODEX_API_KEY: ${{ secrets.CODEX_API_KEY }}
    # For config variables
    CODEX_REDIS_HOST: ${{ env.CODEX_REDIS_HOST }}
```

---

## Migration Questions

### Q: I'm moving from hardcoded values to env vars

**A:** No change needed! Env vars override hardcoded defaults:

```python
# Code automatically respects env vars
redis = Redis(host=os.getenv('CODEX_REDIS_HOST', 'localhost'))
```

Just set the env vars and restart the application.

### Q: Can I use env vars for different service versions?

**A:** Yes, via different hostnames:

```bash
# Version A: Old Ollama API
export CODEX_OLLAMA_HOST=http://ollama-v0.1:11434

# Version B: New Ollama API
export CODEX_OLLAMA_HOST=http://ollama-v0.2:11434

# Switch by changing variable
```

### Q: How do I deprecate an old env var?

**A:** Keep it working but document the new one:

```bash
# Still works (backward compatible)
export CODEX_REDIS_HOST=redis

# Preferred (new name)
export CODEX_REDIS_CONNECTION_HOST=redis

# Code supports both, prefers new
redis_host = os.getenv('CODEX_REDIS_CONNECTION_HOST') or os.getenv('CODEX_REDIS_HOST')
```

---

## Where to Get Help

- **Configuration Issues:** See `docs/docs/quickstart/QUICKSTART_BY_PROFILE.md`
- **Deployment Questions:** See `docs/KUBERNETES_DEPLOYMENT.md` or `docs/DOCKER_SETUP.md`
- **Metrics/Adoption:** See `docs/ONBOARDING_METRICS_DASHBOARD.md`
- **Community:** GitHub Discussions `Environment Configuration`
- **Bugs:** GitHub Issues tag `env-var-config`

---

**Last Updated: 2026-07-08
**Total Variables:** 8 (all documented)
**Success Target:** 80%+ adoption, 95%+ success rate, 4.5/5 clarity
