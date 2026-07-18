# PHASE 4 — VERSION PINNING STRATEGY

**Objective:** Specify exact versions for Phase 4 Custom Images to maximize compatibility

## Language Versions — Final Recommendations

### Python

**Detected versions:** 3.12.13, 6, [

```dockerfile
# Recommended: Install Python 3.12 (latest stable)
RUN apt-get update && apt-get install -y python3.12 python3.12-venv python3-pip
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1
```

### Node.js

**Detected versions:** ${{ env.NODE_VERSION }}, 22, 5

```dockerfile
# Recommended: Install Node.js 22.x (LTS)
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
RUN apt-get install -y nodejs
```

### Go

```dockerfile
# Recommended: Install Go 1.22+
ENV GO_VERSION=1.23
RUN wget -q https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz -O /tmp/go.tar.gz
RUN tar -C /usr/local -xzf /tmp/go.tar.gz
ENV PATH=/usr/local/go/bin:$PATH
```

### Rust

```dockerfile
# Recommended: Install Rust stable
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH=/root/.cargo/bin:$PATH
```

## System Packages — Required

```dockerfile
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    jq \
    make \
    openssl \
    ca-certificates \
    wget \
    zip \
    unzip \
    tar \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*
```

## Pre-install Pip Packages

```dockerfile
RUN pip install --no-cache-dir \
    --upgrade pip \
    pyte \
    -e ".[dev]" \
    detect- \
    setuptools \
    wheel
```

## Build Optimization Tips

1. **Multi-stage builds**: Use builder stage to reduce final image size
2. **Cache layers**: Order RUN commands from least-frequently-changed to most-frequently-changed
3. **Clean up**: Always remove apt cache and temporary files
4. **Slim variants**: Consider `debian:bookworm-slim` or `ubuntu:24.04-minimal` for smaller base
5. **Layer caching**: Pre-install heavy packages (Go, Rust) before light ones (pip packages)

## Version Override Strategy

Despite pre-installing specific versions, workflows can still override via `actions/setup-*`:

- `actions/setup-python` → allows any Python version (overrides base image)
- `actions/setup-node` → allows any Node version (overrides base image)
- `actions/setup-go` → allows any Go version (overrides base image)
- `actions/setup-rust` → allows any Rust version (overrides base image)

**Recommendation:** Pre-install LTS/recommended versions, but don't force them—actions override is preserved
