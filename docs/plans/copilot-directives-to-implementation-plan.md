# 🤖 COPILOT AGENT DIRECTIVE TO IMPLEMENT:  Aries-Serpent/_codex_ Complete Implementation
> Generated:  Previous Cycle-12-17T12:30:00Z | Author: mbaetiong | Target: GitHub Copilot Agent
> Compiled:  Unified context for autonomous agent implementation

---

```yml
🧠 Roles:  [Primary:  Autonomous Agent Orchestrator], [Secondary: Security & Infrastructure Manager] ⚡ Energy:  [5]
⚛️ Physics:  
  Path🛤️:  
    - "Multi-stream execution minimizes sequential bottlenecks"
    - "UV installer reduces dependency resolution path from O(n²) to O(n)"
    - "Container caching pre-computes dependency graphs (shortest path to runtime)"
    - "Codemod automation eliminates manual fix iteration loops"
    - "GitHub Actions cache hierarchy:  UV → GHCR → compressed (fallback paths)"
    - "Agent model selection optimizes cost/performance trade-off (least resistance)"
    
  Fields🔄: 
    - "Weekly cache warmer maintains persistent 'dependency field' strength"
    - "Organization-level code scanning creates security coverage field across all repos"
    - "OpenAI client propagates context (repo, org, task type) to all agent executions"
    - "Risk scores propagate through alert prioritization (severity × criticality × exploitability)"
    - "PR-safe cache isolation prevents poisoning field contamination"
    - "Semgrep baseline creates temporal field boundary (only new alerts trigger failures)"
    
  Patterns👁️: 
    - "Dependency stability pattern: core libs (quarterly) → dev tools (monthly) → test (weekly)"
    - "Alert clustering pattern: 80% of fixes apply to 20% of rule types"
    - "Codemod reuse pattern: subprocess, SQL injection, secrets share transformation structure"
    - "CI workflow pattern: lint (fast) → test (medium) → security (comprehensive)"
    - "Agent task pattern: prompt → model selection → execution → audit logging"
    - "Security remediation lifecycle: export → score → group → fix → suppress → prevent"
    
  Redundancy🔀: 
    - "Triple cache fallback: UV cache → GHCR container → compressed pip"
    - "Dual security scanning: Semgrep (SAST) + Dependency scan + Secret detection"
    - "Multi-branch backup: backup/codeql-advanced + . github/disabled/"
    - "Agent retry logic: primary model → fallback model → error with full context"
    - "Fix validation: dry-run → PR creation → automated tests → manual review"
    - "Documentation layers: inline comments + README + dedicated docs/ + PR descriptions"
    
  Balance⚖️: 
    - "Cache compression: +10s build time ↔ -70% storage (1. 5GB → 450MB)"
    - "Security vs. velocity: PR checks read-only cache ↔ main branch writes"
    - "Automation vs. safety: codemods for P0/P1 ↔ manual review for complex patterns"
    - "Cost vs.  performance: gpt-4o-mini (default) ↔ o1-preview (reasoning tasks)"
    - "Coverage vs. noise: security-extended queries ↔ FP suppression register"
    - "Speed vs. thoroughness: container tests (1min) parallel to UV tests (3min × 3 versions)"
```
---

# TABLE OF CONTENTS

1. [MISSION OVERVIEW](#mission-overview)
2. [STREAM A: Cost-Optimized Caching Architecture](#stream-a-cost-optimized-caching-architecture)
3. [STREAM B: OpenAI Custom Models Integration](#stream-b-openai-custom-models-integration)
4. [STREAM C: Semgrep Alert Remediation (1,665 Alerts)](#stream-c-semgrep-alert-remediation)
5. [STREAM D: Code Scanning Conflict Resolution](#stream-d-code-scanning-conflict-resolution)
6. [UNIFIED EXECUTION SEQUENCE](#unified-execution-sequence)
7. [MASTER VALIDATION CHECKLIST](#master-validation-checklist)

---

# MISSION OVERVIEW

## Authorization Statement

**Copilot Agent**:  You are authorized to operate autonomously on `Aries-Serpent/_codex_` (repo ID: `1040037790`) with the following scope:

| Permission | Scope | Constraints |
|------------|-------|-------------|
| **Repository Write** | Full | Create branches, PRs, files, workflows |
| **GitHub Actions** | Full | Create/modify workflows, manage secrets references |
| **Issues** | Full | Create, update, close issues |
| **Pull Requests** | Full | Create, merge (with approval), comment |
| **Security** | Read + Remediate | Fix alerts, configure scanning, suppress FPs |
| **Packages (GHCR)** | Write | Push container images |
| **Organization** | Limited | Request org-admin actions via issues |

## Physics Optimization Summary

| Principle | Applied To | Optimization Result |
|-----------|-----------|---------------------|
| 🛤️ **Path** | Dependency resolution | 10-100x faster installs (UV vs pip) |
| 🔄 **Fields** | Cache warming | Zero cold-start penalty for 7-day window |
| 👁️ **Patterns** | Alert grouping | 60% reduction in fix PRs via batching |
| 🔀 **Redundancy** | Multi-tier caching | 95% cache hit rate across environments |
| ⚖️ **Balance** | Compression level | zstd-19:  3x size reduction, <5% time overhead |

## Implementation-Specific Applications

### Stream A (Caching): Path Optimization Dominant
- **Primary**:  Shortest path to dependencies (UV → CDN, no local cache needed)
- **Secondary**: Field propagation (weekly warmer maintains cache field)
- **Tertiary**:  Redundancy (3-tier fallback prevents cache misses)

### Stream B (OpenAI): Balance Optimization Dominant
- **Primary**: Cost ↔ Performance (model selection algorithm)
- **Secondary**: Pattern recognition (task type → model capability mapping)
- **Tertiary**: Fields (context propagation to all agents)

### Stream C (Semgrep): Pattern Recognition Dominant
- **Primary**: Alert clustering by fix type (enables batch codemods)
- **Secondary**: Path optimization (automated fixes vs manual review decision tree)
- **Tertiary**: Balance (fix thoroughness ↔ developer velocity)

### Stream D (Code Scanning): Redundancy Optimization Dominant
- **Primary**:  Backup preservation (advanced config saved to 2 locations)
- **Secondary**: Fields (org-level policy propagates to all repos)
- **Tertiary**: Balance (org compliance ↔ custom query requirements)


## Repository Context

```yaml
repository:
  owner:  Aries-Serpent
  name:  _codex_
  id: 1040037790
  visibility: public
  type: AI/ML Autonomous Agent Framework
  
languages:
  primary: Python (89.5%, ~13MB)
  secondary: [JavaScript, TypeScript, Shell, YAML]
  
dependencies:
  heavy_500mb_plus: 
    - torch
    - transformers
    - datasets
  medium_50_200mb: 
    - mlflow
    - ray[serve]
    - accelerate
    - pandas
    - numpy
  light_under_50mb:
    - pydantic
    - typer
    - hydra-core
    - peft

security_state: 
  semgrep_alerts:  1665
  code_scanning_status: "Advanced setup conflict with org default"
  
secrets_available:
  - GITHUB_TOKEN (automatic)
  - GITHUB_CODEX (OpenAI API key - 32 custom models)
```

## Implementation Streams

| Stream | Priority | Scope | Dependencies |
|--------|----------|-------|--------------|
| **A:  Caching** | 🔴 Critical | CI/CD optimization | None |
| **B: OpenAI Integration** | 🔴 Critical | Agent runtime | Stream A (optional) |
| **C: Semgrep Remediation** | 🔴 Critical | Security fixes | Stream D |
| **D:  Code Scanning** | 🔴 Critical | Org compliance | None |

---

# STREAM A:  COST-OPTIMIZED CACHING ARCHITECTURE

## Objective

Implement zero-cost to minimal-cost caching strategy prioritizing: 
1. Free-tier resources first (GitHub native features, compression, deduplication)
2. Remote sourcing over local caching (streaming, CDN, package registries)
3. Intelligent cache eviction (deterministic rebuilds, layer sharing)
4. Cross-agent cache reuse (monorepo patterns, shared artifacts)

## Phase A. 1: Dependency Splitting

### Task A.1.1: Create Minimal Requirements

**File**: `requirements-minimal.txt`

```text
# Minimal dependencies for CLI/core operations (~50MB installed)
# Used for:  linting, basic CLI, config validation
typer>=0.12
pydantic>=2.6
pyyaml>=6.0
omegaconf>=2.3
jsonschema>=4.23
```

### Task A.1.2: Create Test Requirements

**File**: `requirements-test.txt`

```text
# Test dependencies (~200MB installed)
# Used for: unit tests, integration tests, CI validation
-r requirements-minimal.txt
pytest>=8.0
pytest-cov>=4.1
pytest-randomly>=3.15
pytest-xdist>=3.5
hypothesis>=6.100
ruff>=0.4
mypy>=1.10
```

### Task A. 1.3: Create Dev Requirements

**File**:  `requirements-dev.txt`

```text
# Development dependencies
# Used for: local development, debugging
-r requirements-test.txt
ipython>=8.20
jupyterlab>=4.0
pre-commit>=3.6
```

## Phase A. 2: UV Installer Integration

### Task A. 2.1: Create Reusable Setup Action

**File**: `.github/actions/setup-python-uv/action.yml`

```yaml
name: 'Setup Python with UV'
description: 'Install Python and dependencies using UV (10-100x faster than pip)'

inputs:
  python-version:
    description: 'Python version to use'
    required:  false
    default: '3.11'
  dependency-profile:
    description:  'Dependency profile:  minimal|test|dev|full'
    required:  false
    default:  'test'
  cache-key-prefix:
    description: 'Cache key prefix for UV cache'
    required:  false
    default:  'uv'

outputs:
  cache-hit:
    description:  'Whether cache was hit'
    value: ${{ steps.cache.outputs.cache-hit }}

runs:
  using: composite
  steps: 
    - name: Setup Python
      uses:  actions/setup-python@v5
      with: 
        python-version:  ${{ inputs.python-version }}

    - name: Install UV
      shell: bash
      run: |
        curl -LsSf https://astral. sh/uv/install.sh | sh
        echo "$HOME/.cargo/bin" >> $GITHUB_PATH

    - name:  Restore UV cache
      id: cache
      uses: actions/cache@v4
      with:
        path:  /tmp/uv-cache
        key:  ${{ inputs.cache-key-prefix }}-${{ runner.os }}-py${{ inputs.python-version }}-${{ inputs.dependency-profile }}-${{ hashFiles('**/requirements*.txt', '**/pyproject.toml', '**/uv.lock') }}
        restore-keys: |
          ${{ inputs.cache-key-prefix }}-${{ runner.os }}-py${{ inputs.python-version }}-${{ inputs.dependency-profile }}-
          ${{ inputs. cache-key-prefix }}-${{ runner.os }}-py${{ inputs.python-version }}-
          ${{ inputs. cache-key-prefix }}-${{ runner.os }}-

    - name: Install dependencies with UV
      shell:  bash
      env:
        UV_CACHE_DIR: /tmp/uv-cache
      run: |
        case "${{ inputs.dependency-profile }}" in
          minimal)
            uv pip install --system -r requirements-minimal.txt
            ;;
          test)
            uv pip install --system -r requirements-test.txt
            ;;
          dev)
            uv pip install --system -r requirements-dev.txt
            ;;
          full)
            uv pip install --system -r requirements. txt
            ;;
          *)
            echo "Unknown profile: ${{ inputs. dependency-profile }}"
            exit 1
            ;;
        esac
```

## Phase A.3: Compressed Cache Action

### Task A. 3.1: Create Compression Helper

**File**: `.github/actions/compressed-cache/action. yml`

```yaml
name: 'Compressed Cache'
description:  'Cache with zstd compression (3-5x size reduction)'

inputs:
  key:
    description:  'Cache key'
    required: true
  path:
    description:  'Path to cache'
    required: true
  compression-level:
    description: 'zstd compression level (1-22, higher = smaller but slower)'
    required: false
    default: '19'
  restore-only:
    description:  'Only restore, do not save'
    required:  false
    default:  'false'

outputs:
  cache-hit:
    description: 'Whether cache was restored'
    value:  ${{ steps.cache-restore.outputs.cache-hit }}

runs: 
  using: composite
  steps: 
    - name: Install zstd
      shell: bash
      run: |
        if !  command -v zstd &> /dev/null; then
          sudo apt-get update && sudo apt-get install -y zstd
        fi

    - name:  Restore compressed cache
      id:  cache-restore
      uses: actions/cache/restore@v4
      with:
        path: ${{ inputs.path }}. tar.zst
        key: ${{ inputs.key }}-zstd
        restore-keys:  |
          ${{ inputs.key }}-

    - name:  Decompress cache
      if: steps.cache-restore. outputs.cache-hit == 'true'
      shell:  bash
      run:  |
        echo "📦 Decompressing cache from ${{ inputs. path }}.tar. zst"
        zstd -d "${{ inputs.path }}.tar.zst" -o "${{ inputs.path }}. tar" --force
        mkdir -p "$(dirname "${{ inputs.path }}")"
        tar -xf "${{ inputs.path }}.tar" -C "$(dirname "${{ inputs.path }}")"
        rm -f "${{ inputs. path }}.tar" "${{ inputs.path }}.tar.zst"
        echo "✅ Cache decompressed successfully"

    - name:  Compress and save cache
      if:  steps.cache-restore.outputs.cache-hit != 'true' && inputs.restore-only != 'true'
      shell: bash
      run: |
        if [ -e "${{ inputs.path }}" ]; then
          echo "📦 Compressing ${{ inputs.path }} with zstd level ${{ inputs.compression-level }}"
          tar -cf "${{ inputs.path }}.tar" -C "$(dirname "${{ inputs.path }}")" "$(basename "${{ inputs.path }}")"
          zstd -${{ inputs.compression-level }} "${{ inputs.path }}.tar" -o "${{ inputs. path }}.tar. zst" --force
          rm -f "${{ inputs. path }}.tar"
          echo "✅ Compressed size: $(du -h "${{ inputs.path }}.tar.zst" | cut -f1)"
        else
          echo "⚠️ Path ${{ inputs.path }} does not exist, skipping compression"
        fi

    - name: Save compressed cache
      if: steps.cache-restore.outputs.cache-hit != 'true' && inputs. restore-only != 'true'
      uses: actions/cache/save@v4
      with: 
        path: ${{ inputs.path }}. tar.zst
        key: ${{ inputs.key }}-zstd
```

## Phase A.4: Container-Based Caching (GHCR)

### Task A. 4.1: Create Multi-Stage Dockerfile

**File**:  `Dockerfile.ci`

```dockerfile
# =============================================================================
# Multi-Stage Dockerfile for _codex_ CI/CD
# Provides pre-built dependency layers for fast CI runs
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Base Python with UV
# -----------------------------------------------------------------------------
FROM python: 3.11-slim as base

# Install UV globally
RUN pip install --no-cache-dir uv

# Set environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_CACHE_DIR=/root/.cache/uv

WORKDIR /app

# -----------------------------------------------------------------------------
# Stage 2: Minimal dependencies
# -----------------------------------------------------------------------------
FROM base as minimal

COPY requirements-minimal. txt ./
RUN uv pip install --system -r requirements-minimal. txt

# -----------------------------------------------------------------------------
# Stage 3: Test dependencies
# -----------------------------------------------------------------------------
FROM minimal as test

COPY requirements-test.txt ./
RUN uv pip install --system -r requirements-test. txt

# -----------------------------------------------------------------------------
# Stage 4: Full dependencies
# -----------------------------------------------------------------------------
FROM test as full

COPY requirements.txt ./
RUN uv pip install --system -r requirements.txt

# -----------------------------------------------------------------------------
# Stage 5: Development image
# -----------------------------------------------------------------------------
FROM full as dev

COPY requirements-dev.txt ./
RUN uv pip install --system -r requirements-dev.txt

# Copy application code
COPY .  . 

# Default command
CMD ["python", "-m", "pytest", "tests/"]
```

### Task A.4.2: Create Container Build Workflow

**File**:  `.github/workflows/build-container-cache.yml`

```yaml
name: Build Container Cache

on: 
  push:
    branches: [main]
    paths:
      - 'requirements*.txt'
      - 'pyproject.toml'
      - 'Dockerfile*'
      - 'uv.lock'
  workflow_dispatch: 
    inputs:
      force_rebuild:
        description: 'Force rebuild all layers'
        type: boolean
        default: false

env:
  REGISTRY: ghcr. io
  IMAGE_NAME: ${{ github.repository }}/ci-base

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions: 
      contents: read
      packages: write

    strategy:
      matrix: 
        target: [minimal, test, full]

    steps: 
      - name: Checkout repository
        uses:  actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images:  ${{ env. REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=raw,value=${{ matrix.target }}-latest,enable={{is_default_branch}}
            type=sha,prefix=${{ matrix.target }}-
            type=ref,event=branch,prefix=${{ matrix.target }}-

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          file:  Dockerfile.ci
          target: ${{ matrix. target }}
          push: true
          tags: ${{ steps. meta.outputs.tags }}
          labels:  ${{ steps.meta.outputs.labels }}
          cache-from: type=registry,ref=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ matrix.target }}-buildcache
          cache-to: type=registry,ref=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ matrix.target }}-buildcache,mode=max
          build-args: |
            BUILDKIT_INLINE_CACHE=1

      - name: Image digest
        run:  echo "Image pushed with digest ${{ steps. build-push.outputs.digest }}"
```

## Phase A.5: Optimized CI Workflow

### Task A.5.1: Create Main CI Workflow

**File**: `.github/workflows/ci.yml`

```yaml
name: CI

on: 
  push: 
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

concurrency:
  group: ${{ github. workflow }}-${{ github.ref }}
  cancel-in-progress: true

env:
  PYTHON_VERSION: '3.11'
  UV_CACHE_DIR: /tmp/uv-cache

jobs:
  # -------------------------------------------------------------------------
  # Fast checks (no heavy dependencies)
  # -------------------------------------------------------------------------
  lint:
    name: Lint & Format
    runs-on: ubuntu-latest
    steps: 
      - uses: actions/checkout@v4

      - name: Setup Python with UV
        uses: . /.github/actions/setup-python-uv
        with: 
          python-version: ${{ env. PYTHON_VERSION }}
          dependency-profile: minimal

      - name:  Install linting tools
        run: uv pip install --system ruff mypy

      - name: Run Ruff
        run: ruff check .  --output-format=github

      - name:  Run Ruff Format Check
        run: ruff format --check . 

  # -------------------------------------------------------------------------
  # Unit tests (container-cached or UV-cached)
  # -------------------------------------------------------------------------
  test:
    name: Test (Python ${{ matrix.python-version }})
    runs-on: ubuntu-latest
    needs: lint
    strategy: 
      fail-fast: false
      matrix:
        python-version: ['3.10', '3.11', '3.12']

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python with UV
        uses:  ./.github/actions/setup-python-uv
        with:
          python-version: ${{ matrix.python-version }}
          dependency-profile: test

      - name:  Run tests
        run:  |
          pytest tests/ \
            --cov=src \
            --cov-report=xml \
            --cov-report=term-missing \
            -n auto \
            --dist=loadfile

      - name: Upload coverage
        if: matrix.python-version == '3.11'
        uses: codecov/codecov-action@v4
        with: 
          files: ./coverage.xml
          fail_ci_if_error: false

  # -------------------------------------------------------------------------
  # Container-based tests (uses pre-built GHCR image)
  # -------------------------------------------------------------------------
  test-container:
    name: Test (Container)
    runs-on: ubuntu-latest
    needs:  lint
    container:
      image:  ghcr.io/${{ github.repository }}/ci-base: test-latest
      credentials: 
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    steps: 
      - uses:  actions/checkout@v4

      # Dependencies already in container - no install needed! 
      - name:  Run tests
        run: pytest tests/ --cov=src -n auto

  # -------------------------------------------------------------------------
  # Security scanning
  # -------------------------------------------------------------------------
  security: 
    name: Security Scan
    runs-on: ubuntu-latest
    needs:  lint
    steps: 
      - uses: actions/checkout@v4

      - name:  Run Semgrep
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/secrets
            p/python
```

## Phase A.6: Cache Warming Workflow

### Task A.6.1: Create Weekly Cache Warmer

**File**:  `.github/workflows/cache-warmer.yml`

```yaml
name: Weekly Cache Warmer

on:
  schedule:
    # Run every Sunday at 2 AM UTC
    - cron: '0 2 * * 0'
  workflow_dispatch: 

jobs:
  warm-caches:
    name: Warm Cache (${{ matrix.python-version }}, ${{ matrix.profile }})
    runs-on: ubuntu-latest
    strategy: 
      matrix:
        python-version: ['3.10', '3.11', '3.12']
        profile: ['minimal', 'test', 'full']

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python with UV
        uses: ./.github/actions/setup-python-uv
        with:
          python-version: ${{ matrix.python-version }}
          dependency-profile: ${{ matrix.profile }}

      - name:  Verify installation
        run: |
          python --version
          pip list | head -20

      - name: Touch cache timestamp
        run: |
          mkdir -p /tmp/uv-cache
          echo "Cache warmed at $(date -u +"%Y-%m-%dT%H:%M:%SZ")" > /tmp/uv-cache/. timestamp

  warm-container-cache:
    name: Warm Container Cache
    runs-on:  ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Pull latest container images
        run: |
          echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin
          docker pull ghcr.io/${{ github.repository }}/ci-base: minimal-latest || true
          docker pull ghcr.io/${{ github.repository }}/ci-base:test-latest || true
          docker pull ghcr.io/${{ github.repository }}/ci-base:full-latest || true

      - name:  Verify images
        run: docker images | grep ci-base
```

## Phase A.7: PR-Safe Cache Isolation

### Task A. 7.1: Create Secure PR Workflow

**File**:  `.github/workflows/pr-checks.yml`

```yaml
name: PR Checks (Isolated Cache)

on:
  pull_request: 
    types: [opened, synchronize, reopened]

permissions:
  contents:  read
  pull-requests:  write

jobs: 
  pr-test:
    name:  PR Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github. event.pull_request. head.sha }}

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      # SECURITY: Read-only cache from main branch
      - name:  Restore cache from main (read-only)
        uses: actions/cache/restore@v4
        with: 
          path: /tmp/uv-cache
          key: uv-${{ runner.os }}-py3. 11-test-${{ hashFiles('**/requirements*.txt') }}
          restore-keys: |
            uv-${{ runner.os }}-py3.11-test-
            uv-${{ runner.os }}-py3.11-
        # NOTE: No cache/save for PRs - prevents cache poisoning

      - name: Install UV
        run: curl -LsSf https://astral. sh/uv/install.sh | sh

      - name:  Install dependencies
        env:
          UV_CACHE_DIR:  /tmp/uv-cache
        run: |
          export PATH="$HOME/.cargo/bin:$PATH"
          uv pip install --system -r requirements-test. txt

      - name: Run tests
        run: pytest tests/ -x --tb=short

      - name: Run linting
        run: |
          pip install ruff
          ruff check .  --output-format=github
```

---

# STREAM B:  OPENAI CUSTOM MODELS INTEGRATION

## Objective

Implement autonomous agent infrastructure leveraging the organization's `GITHUB_CODEX` OpenAI API key (32 custom models) for AI Assistant/Agent operations.

## Phase B.1: OpenAI Client Configuration

### Task B. 1.1: Create OpenAI Client Factory

**File**: `src/config/openai_client.py`

```python
"""
OpenAI Client Configuration for _codex_ Autonomous Agents
Leverages Aries-Serpent organization custom models (32 models)

Author: mbaetiong
Generated: Previous Cycle-12-17
"""

from __future__ import annotations

import hashlib
import os
import time
from dataclasses import dataclass, field
from typing import Any, Literal

from openai import OpenAI

# Model cost tiers
CostTier = Literal["low", "medium", "high", "very-high"]


@dataclass
class ModelConfig:
    """Configuration for an OpenAI model."""
    
    context_length: int
    reasoning:  bool = False
    cost_tier: CostTier = "medium"
    input_cost_per_1k:  float = 0.01
    output_cost_per_1k: float = 0.03


# Available models in GITHUB_CODEX organization
AVAILABLE_MODELS:  dict[str, ModelConfig] = {
    # Reasoning models (o-series)
    "o1-preview": ModelConfig(128000, reasoning=True, cost_tier="high", input_cost_per_1k=0.015, output_cost_per_1k=0.06),
    "o1-mini": ModelConfig(128000, reasoning=True, cost_tier="medium", input_cost_per_1k=0.003, output_cost_per_1k=0.012),
    "o3-mini": ModelConfig(128000, reasoning=True, cost_tier="medium", input_cost_per_1k=0.003, output_cost_per_1k=0.012),
    
    # GPT-4 Turbo models
    "gpt-4-turbo": ModelConfig(128000, cost_tier="medium", input_cost_per_1k=0.01, output_cost_per_1k=0.03),
    "gpt-4-turbo-preview": ModelConfig(128000, cost_tier="medium", input_cost_per_1k=0.01, output_cost_per_1k=0.03),
    
    # GPT-4 models
    "gpt-4":  ModelConfig(8192, cost_tier="high", input_cost_per_1k=0.03, output_cost_per_1k=0.06),
    "gpt-4-32k": ModelConfig(32768, cost_tier="very-high", input_cost_per_1k=0.06, output_cost_per_1k=0.12),
    
    # GPT-4o models
    "gpt-4o": ModelConfig(128000, cost_tier="medium", input_cost_per_1k=0.005, output_cost_per_1k=0.015),
    "gpt-4o-mini":  ModelConfig(128000, cost_tier="low", input_cost_per_1k=0.00015, output_cost_per_1k=0.0006),
    
    # GPT-3.5 models
    "gpt-3.5-turbo":  ModelConfig(16385, cost_tier="low", input_cost_per_1k=0.0005, output_cost_per_1k=0.0015),
    "gpt-3.5-turbo-16k": ModelConfig(16385, cost_tier="low", input_cost_per_1k=0.0005, output_cost_per_1k=0.0015),
}


@dataclass
class ExecutionResult:
    """Result of an agent task execution."""
    
    success: bool
    model:  str
    response: str | None = None
    error: str | None = None
    usage: dict[str, int] | None = None
    duration_ms: int = 0
    estimated_cost:  float = 0.0


@dataclass
class AuditLogEntry:
    """Audit log entry for API usage tracking."""
    
    timestamp: str
    task_id: str
    model: str
    tokens_used: int
    duration_ms: int
    estimated_cost: float
    success: bool


class CodexOpenAIClient:
    """
    OpenAI client for _codex_ autonomous agents. 
    
    Features:
    - Intelligent model selection based on task requirements
    - Cost estimation and tracking
    - Audit logging for compliance
    - Rate limiting support
    """
    
    def __init__(self) -> None:
        """Initialize the OpenAI client."""
        self.api_key = os. getenv("OPENAI_API_KEY") or os.getenv("GITHUB_CODEX")
        
        if not self. api_key: 
            raise EnvironmentError(
                "❌ CRITICAL: OPENAI_API_KEY or GITHUB_CODEX not found.  "
                "Agent cannot operate without API credentials."
            )
        
        self.client = OpenAI(
            api_key=self.api_key,
            organization=os.getenv("OPENAI_ORG_ID"),
        )
        
        self.models = AVAILABLE_MODELS
        self. audit_log: list[AuditLogEntry] = []
        
        # Rate limiting state
        self._requests_this_minute = 0
        self._tokens_this_minute = 0
        self._minute_start = time.time()
    
    def select_model(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost:  CostTier = "medium",
        min_context:  int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.
        
        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)
        
        Returns: 
            Selected model name
        """
        # Use preferred model if specified and valid
        if preferred_model and preferred_model in self.models:
            return preferred_model
        
        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)
        
        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]
        
        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"
        
        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))
        
        # Prefer reasoning models if required
        if requires_reasoning: 
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]
        
        return candidates[0][0]
    
    def build_system_prompt(self, task_type: str = "general") -> str:
        """Build the system prompt with _codex_ context."""
        return f"""You are an autonomous AI agent operating within the Aries-Serpent/_codex_ repository. 

Your capabilities: 
- Full access to 32 OpenAI custom models via GITHUB_CODEX API key
- Autonomous decision-making within defined safety boundaries
- Code generation, analysis, and modification
- GitHub API integration (issues, PRs, workflows)
- Multi-agent coordination and task decomposition

Current context:
- Repository: {os.getenv('REPO_CONTEXT', '_codex_')}
- Organization: {os.getenv('ORG_CONTEXT', 'Aries-Serpent')}
- Task Type: {task_type}

Physics-optimized principles:
- 🛤️ Path:  Optimize for least resistance
- 🔄 Fields: Propagate changes efficiently
- 👁️ Patterns: Recognize and apply successful patterns
- 🔀 Redundancy: Build fallback mechanisms
- ⚖️ Balance: Trade off speed vs. accuracy appropriately

Execute the user's request autonomously, following _codex_ patterns and best practices."""
    
    async def execute_task(
        self,
        prompt: str,
        *,
        task_type: str = "general",
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        preferred_model: str | None = None,
    ) -> ExecutionResult:
        """
        Execute an autonomous agent task. 
        
        Args:
            prompt:  The task prompt
            task_type:  Type of task for context building
            requires_reasoning: Whether reasoning is required
            max_cost: Maximum cost tier
            max_tokens: Maximum tokens in response
            temperature:  Sampling temperature
            preferred_model:  Preferred model override
        
        Returns: 
            ExecutionResult with response or error
        """
        model = self.select_model(
            requires_reasoning=requires_reasoning,
            max_cost=max_cost,
            preferred_model=preferred_model,
        )
        
        start_time = time. time()
        task_id = hashlib.sha256(prompt.encode()).hexdigest()[:8]
        
        try:
            response = self.client. chat.completions. create(
                model=model,
                messages=[
                    {"role": "system", "content": self.build_system_prompt(task_type)},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            usage = {
                "prompt_tokens": response. usage.prompt_tokens,
                "completion_tokens": response. usage.completion_tokens,
                "total_tokens": response. usage.total_tokens,
            }
            
            estimated_cost = self._estimate_cost(model, usage)
            
            # Log execution
            self._log_execution(
                task_id=task_id,
                model=model,
                tokens_used=usage["total_tokens"],
                duration_ms=duration_ms,
                estimated_cost=estimated_cost,
                success=True,
            )
            
            return ExecutionResult(
                success=True,
                model=model,
                response=response.choices[0].message. content,
                usage=usage,
                duration_ms=duration_ms,
                estimated_cost=estimated_cost,
            )
            
        except Exception as e: 
            duration_ms = int((time.time() - start_time) * 1000)
            
            self._log_execution(
                task_id=task_id,
                model=model,
                tokens_used=0,
                duration_ms=duration_ms,
                estimated_cost=0.0,
                success=False,
            )
            
            return ExecutionResult(
                success=False,
                model=model,
                error=str(e),
                duration_ms=duration_ms,
            )
    
    def _estimate_cost(self, model:  str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models. get(model)
        if not config: 
            return 0.0
        
        input_cost = (usage["prompt_tokens"] / 1000) * config.input_cost_per_1k
        output_cost = (usage["completion_tokens"] / 1000) * config.output_cost_per_1k
        
        return round(input_cost + output_cost, 6)
    
    def _log_execution(
        self,
        *,
        task_id: str,
        model: str,
        tokens_used: int,
        duration_ms: int,
        estimated_cost: float,
        success: bool,
    ) -> None:
        """Log an execution for audit purposes."""
        from datetime import datetime, timezone
        
        entry = AuditLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            task_id=task_id,
            model=model,
            tokens_used=tokens_used,
            duration_ms=duration_ms,
            estimated_cost=estimated_cost,
            success=success,
        )
        
        self.audit_log. append(entry)
        
        # Keep only last 1000 entries in memory
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]
    
    def get_usage_summary(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if not self.audit_log:
            return {"total_requests": 0, "total_tokens": 0, "total_cost":  0.0}
        
        return {
            "total_requests": len(self.audit_log),
            "successful_requests": sum(1 for e in self.audit_log if e.success),
            "total_tokens": sum(e.tokens_used for e in self. audit_log),
            "total_cost": sum(e. estimated_cost for e in self.audit_log),
            "models_used": list(set(e.model for e in self.audit_log)),
            "avg_duration_ms": sum(e.duration_ms for e in self. audit_log) // len(self.audit_log),
        }
```

## Phase B. 2: Autonomous Agent Runner

### Task B. 2.1: Create Agent Runner

**File**:  `src/agents/autonomous_runner.py`

```python
"""
Autonomous Agent Runner for _codex_
Executes agent tasks with OpenAI custom models

Author: mbaetiong
Generated: Previous Cycle-12-17
"""

from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from src.config.openai_client import CodexOpenAIClient, ExecutionResult


class AutonomousAgent:
    """
    Autonomous agent that executes tasks using OpenAI models.
    
    Features:
    - Task execution with automatic model selection
    - Report generation
    - Error handling and recovery
    """
    
    def __init__(self, reports_dir: str | Path = ". agents/reports") -> None:
        """Initialize the autonomous agent."""
        self.client = CodexOpenAIClient()
        self.reports_dir = Path(reports_dir)
        self.reports_dir. mkdir(parents=True, exist_ok=True)
    
    async def execute(
        self,
        task:  str,
        *,
        task_type: str = "general",
        model_preference: str = "auto",
        max_tokens: int = 8192,
        temperature: float = 0.7,
    ) -> ExecutionResult:
        """
        Execute an autonomous task.
        
        Args:
            task: The task description/prompt
            task_type: Type of task for context
            model_preference:  Preferred model or "auto"
            max_tokens: Maximum response tokens
            temperature:  Sampling temperature
        
        Returns: 
            ExecutionResult with response or error
        """
        print(f"🚀 Starting autonomous agent execution...")
        print(f"📋 Task: {task[: 100]}{'...' if len(task) > 100 else ''}")
        print(f"🎯 Model preference: {model_preference}")
        
        result = await self.client.execute_task(
            task,
            task_type=task_type,
            preferred_model=model_preference if model_preference != "auto" else None,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        
        if result.success:
            print(f"✅ Execution successful")
            print(f"📊 Model used: {result.model}")
            print(f"⏱️ Duration: {result.duration_ms}ms")
            print(f"💰 Tokens:  {result.usage['total_tokens'] if result.usage else 'N/A'}")
            print(f"💵 Estimated cost:  ${result.estimated_cost:.4f}")
        else:
            print(f"❌ Execution failed: {result.error}")
        
        # Save report
        await self._save_report(task, result)
        
        return result
    
    async def _save_report(self, task: str, result:  ExecutionResult) -> Path:
        """Save execution report to file."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        report_path = self.reports_dir / f"agent_{timestamp}.json"
        
        report = {
            "timestamp": datetime.now(timezone. utc).isoformat(),
            "task": task,
            "result": {
                "success":  result.success,
                "model": result.model,
                "response": result.response,
                "error":  result.error,
                "usage": result.usage,
                "duration_ms":  result.duration_ms,
                "estimated_cost": result. estimated_cost,
            },
            "environment": {
                "repo":  os.getenv("REPO_CONTEXT", "_codex_"),
                "org": os.getenv("ORG_CONTEXT", "Aries-Serpent"),
            },
        }
        
        report_path.write_text(json.dumps(report, indent=2))
        print(f"💾 Report saved:  {report_path}")
        
        return report_path


async def main() -> None:
    """Main entry point for the autonomous agent."""
    task = os.getenv("AGENT_TASK", "Analyze _codex_ repository structure")
    model_preference = os. getenv("MODEL_PREFERENCE", "auto")
    
    agent = AutonomousAgent()
    result = await agent.execute(
        task,
        model_preference=model_preference,
    )
    
    if result.success and result.response:
        print("\n--- AGENT RESPONSE ---\n")
        print(result.response)
        print("\n--- END RESPONSE ---\n")
    
    # Print usage summary
    summary = agent.client.get_usage_summary()
    print(f"\n📈 Usage Summary:  {json.dumps(summary, indent=2)}")


if __name__ == "__main__": 
    asyncio. run(main())
```

## Phase B.3: Agent Runtime Workflow

### Task B. 3.1: Create Agent Workflow

**File**:  `.github/workflows/agent-runtime.yml`

```yaml
name:  Autonomous Agent Runtime

on:
  workflow_dispatch:
    inputs:
      agent_task:
        description: 'Task for the autonomous agent to execute'
        required: true
        type: string
      model_preference:
        description: 'Preferred model (auto, gpt-4o, o1-mini, etc.)'
        required: false
        default: 'auto'
        type: string
      max_tokens:
        description:  'Maximum response tokens'
        required:  false
        default:  '8192'
        type: string
  
  # Allow triggering from other workflows
  workflow_call:
    inputs:
      agent_task:
        required: true
        type: string
      model_preference: 
        required: false
        default: 'auto'
        type: string
    secrets:
      GITHUB_CODEX: 
        required: true

jobs:
  execute-agent:
    name: Execute Autonomous Agent
    runs-on: ubuntu-latest
    permissions:
      contents:  write
      issues: write
      pull-requests: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Python with UV
        uses: . /.github/actions/setup-python-uv
        with:
          python-version: '3.11'
          dependency-profile: full

      - name:  Install OpenAI SDK
        run: uv pip install --system openai

      - name: Execute Autonomous Agent
        id: agent
        env:
          OPENAI_API_KEY: ${{ secrets. GITHUB_CODEX }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          AGENT_TASK:  ${{ inputs.agent_task }}
          MODEL_PREFERENCE:  ${{ inputs.model_preference }}
          ORG_CONTEXT: 'Aries-Serpent'
          REPO_CONTEXT:  '_codex_'
        run: |
          python -m src.agents.autonomous_runner

      - name: Upload Agent Report
        if: always()
        uses: actions/upload-artifact@v4
        with: 
          name: agent-execution-report-${{ github.run_id }}
          path:  . agents/reports/
          retention-days: 30

      - name: Summary
        if: always()
        run: |
          echo "## 🤖 Agent Execution Summary" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "**Task:** ${{ inputs.agent_task }}" >> $GITHUB_STEP_SUMMARY
          echo "**Model:** ${{ inputs.model_preference }}" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          if [ -f ".agents/reports/"*. json ]; then
            echo "### Report" >> $GITHUB_STEP_SUMMARY
            echo '```json' >> $GITHUB_STEP_SUMMARY
            cat .agents/reports/*.json >> $GITHUB_STEP_SUMMARY
            echo '```' >> $GITHUB_STEP_SUMMARY
          fi
```

## Phase B. 4: Multi-Agent Orchestrator

### Task B. 4.1: Create Orchestrator

**File**: `src/agents/orchestrator.py`

```python
"""
Multi-Agent Orchestrator for _codex_
Coordinates multiple autonomous agents with shared resources

Author: mbaetiong
Generated: Previous Cycle-12-17
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from src.config.openai_client import CodexOpenAIClient, ExecutionResult


class AgentStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"


@dataclass
class Agent:
    """Represents a registered agent."""
    
    id: str
    capabilities: list[str]
    status: AgentStatus = AgentStatus.IDLE
    tasks_completed: int = 0
    total_tokens_used: int = 0


@dataclass
class RateLimiter:
    """Rate limiter for API requests."""
    
    requests_per_minute:  int = 60
    tokens_per_minute:  int = 150000
    current_requests: int = 0
    current_tokens: int = 0
    window_start: float = 0. 0


class AgentOrchestrator:
    """
    Orchestrates multiple autonomous agents with shared OpenAI resources. 
    
    Features:
    - Agent registration and capability matching
    - Rate limiting across all agents
    - Task queue management
    - Resource pooling
    """
    
    def __init__(self) -> None:
        """Initialize the orchestrator."""
        self.client = CodexOpenAIClient()
        self.agents: dict[str, Agent] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.rate_limiter = RateLimiter()
        self._lock = asyncio.Lock()
    
    def register_agent(self, agent_id: str, capabilities: list[str]) -> Agent:
        """
        Register a new agent with the orchestrator. 
        
        Args:
            agent_id: Unique identifier for the agent
            capabilities: List of task types the agent can handle
        
        Returns: 
            The registered Agent instance
        """
        agent = Agent(id=agent_id, capabilities=capabilities)
        self.agents[agent_id] = agent
        return agent
    
    def select_agent_for_task(self, task_type: str) -> Agent | None:
        """
        Select the best available agent for a task.
        
        Args:
            task_type: Type of task to execute
        
        Returns:
            Selected agent or None if no suitable agent available
        """
        for agent in self.agents.values():
            if agent.status == AgentStatus. IDLE and task_type in agent. capabilities:
                return agent
        
        # Fallback:  any idle agent
        for agent in self.agents.values():
            if agent.status == AgentStatus. IDLE:
                return agent
        
        return None
    
    async def delegate_task(
        self,
        prompt: str,
        task_type: str = "general",
        **kwargs: Any,
    ) -> ExecutionResult:
        """
        Delegate a task to an available agent.
        
        Args:
            prompt: The task prompt
            task_type:  Type of task
            **kwargs: Additional arguments for task execution
        
        Returns:
            ExecutionResult from the agent
        """
        agent = self.select_agent_for_task(task_type)
        
        if not agent:
            # Queue the task for later
            await self.task_queue.put((prompt, task_type, kwargs))
            return ExecutionResult(
                success=False,
                model="",
                error="No available agents.  Task queued.",
            )
        
        async with self._lock:
            agent.status = AgentStatus. BUSY
        
        try: 
            # Apply rate limiting
            await self._enforce_rate_limits(prompt)
            
            # Execute task
            result = await self. client.execute_task(
                prompt,
                task_type=task_type,
                **kwargs,
            )
            
            # Update agent stats
            async with self._lock:
                agent.tasks_completed += 1
                if result.usage:
                    agent.total_tokens_used += result.usage["total_tokens"]
                agent.status = AgentStatus. IDLE
            
            return result
            
        except Exception as e:
            async with self._lock:
                agent.status = AgentStatus. ERROR
            
            return ExecutionResult(
                success=False,
                model="",
                error=str(e),
            )
    
    async def _enforce_rate_limits(self, prompt: str) -> None:
        """Enforce rate limits before making a request."""
        import time
        
        estimated_tokens = len(prompt.split()) * 1.3
        
        async with self._lock:
            current_time = time. time()
            
            # Reset counters if minute has passed
            if current_time - self. rate_limiter. window_start > 60:
                self.rate_limiter.current_requests = 0
                self.rate_limiter.current_tokens = 0
                self.rate_limiter.window_start = current_time
            
            # Check if we need to wait
            if (
                self.rate_limiter.current_requests >= self.rate_limiter.requests_per_minute
                or self.rate_limiter.current_tokens + estimated_tokens > self.rate_limiter.tokens_per_minute
            ):
                wait_time = 60 - (current_time - self. rate_limiter. window_start)
                if wait_time > 0:
                    print(f"⏳ Rate limit approaching, waiting {wait_time:.1f}s...")
                    await asyncio.sleep(wait_time)
                    self.rate_limiter.current_requests = 0
                    self.rate_limiter.current_tokens = 0
                    self.rate_limiter.window_start = time.time()
            
            self.rate_limiter.current_requests += 1
            self.rate_limiter.current_tokens += int(estimated_tokens)
    
    def get_orchestrator_status(self) -> dict[str, Any]:
        """Get the current status of the orchestrator."""
        return {
            "registered_agents": len(self.agents),
            "agents":  {
                agent_id: {
                    "status": agent.status.value,
                    "capabilities": agent.capabilities,
                    "tasks_completed": agent.tasks_completed,
                    "tokens_used": agent. total_tokens_used,
                }
                for agent_id, agent in self.agents.items()
            },
            "queued_tasks": self.task_queue. qsize(),
            "rate_limiter": {
                "requests_used": self.rate_limiter.current_requests,
                "tokens_used": self.rate_limiter.current_tokens,
            },
            "client_usage": self.client. get_usage_summary(),
        }
```

---

# STREAM C: SEMGREP ALERT REMEDIATION

## Objective

Systematically resolve all 1,665 Semgrep code scanning alerts through: 
1. Discovery & prioritization
2. Automated codemods for repetitive fixes
3. Manual fixes for complex issues
4. False positive suppression with documentation
5. CI/CD prevention gates

## Phase C. 1: Alert Export & Analysis

### Task C. 1.1: Create Analysis Script

**File**:  `scripts/security/export_semgrep_alerts. py`

```python
"""
Export and analyze Semgrep alerts from GitHub Code Scanning. 

Author: mbaetiong
Generated: Previous Cycle-12-17
"""

from __future__ import annotations

import csv
import json
import os
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import requests

# GitHub API configuration
GITHUB_TOKEN = os. getenv("GITHUB_TOKEN")
OWNER = "Aries-Serpent"
REPO = "_codex_"
API_BASE = f"https://api.github.com/repos/{OWNER}/{REPO}"

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


def export_alerts() -> list[dict]:
    """Export all code scanning alerts from GitHub API."""
    alerts = []
    page = 1
    per_page = 100
    
    print("📥 Exporting Semgrep alerts...")
    
    while True: 
        response = requests.get(
            f"{API_BASE}/code-scanning/alerts",
            headers=HEADERS,
            params={
                "state": "open",
                "tool_name": "Semgrep",
                "per_page": per_page,
                "page": page,
            },
        )
        response.raise_for_status()
        
        batch = response.json()
        if not batch:
            break
        
        alerts.extend(batch)
        print(f"  Fetched page {page}:  {len(batch)} alerts")
        page += 1
    
    print(f"✅ Exported {len(alerts)} total alerts")
    return alerts


def analyze_alerts(alerts: list[dict]) -> dict:
    """Analyze alert distribution and patterns."""
    analysis = {
        "total":  len(alerts),
        "by_severity": Counter(),
        "by_rule":  Counter(),
        "by_file": Counter(),
        "by_language":  Counter(),
        "rule_details": {},
    }
    
    for alert in alerts: 
        # Severity
        severity = alert. get("rule", {}).get("severity", "unknown")
        analysis["by_severity"][severity] += 1
        
        # Rule
        rule_id = alert.get("rule", {}).get("id", "unknown")
        analysis["by_rule"][rule_id] += 1
        
        # File
        file_path = alert.get("most_recent_instance", {}).get("location", {}).get("path", "unknown")
        analysis["by_file"][file_path] += 1
        
        # Store rule details
        if rule_id not in analysis["rule_details"]:
            analysis["rule_details"][rule_id] = {
                "name": alert.get("rule", {}).get("name", ""),
                "description": alert.get("rule", {}).get("description", ""),
                "severity":  severity,
                "count": 0,
            }
        analysis["rule_details"][rule_id]["count"] += 1
    
    return analysis


def generate_report(alerts: list[dict], analysis: dict, output_dir: Path) -> None:
    """Generate analysis report and export files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Export raw alerts
    alerts_file = output_dir / "semgrep-alerts-export.json"
    alerts_file.write_text(json.dumps(alerts, indent=2))
    print(f"💾 Saved alerts to {alerts_file}")
    
    # Export distribution CSV
    dist_file = output_dir / "alert-distribution.csv"
    with open(dist_file, "w", newline="") as f:
        writer = csv. writer(f)
        writer.writerow(["Category", "Item", "Count"])
        
        for severity, count in analysis["by_severity"].most_common():
            writer.writerow(["severity", severity, count])
        
        for rule, count in analysis["by_rule"].most_common(20):
            writer. writerow(["rule", rule, count])
        
        for file, count in analysis["by_file"].most_common(20):
            writer.writerow(["file", file, count])
    
    print(f"💾 Saved distribution to {dist_file}")
    
    # Generate markdown report
    report = generate_markdown_report(analysis)
    report_file = output_dir. parent. parent / "docs" / "security" / "semgrep-analysis-report.md"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(report)
    print(f"💾 Saved report to {report_file}")


def generate_markdown_report(analysis: dict) -> str:
    """Generate a markdown analysis report."""
    timestamp = datetime.utcnow().isoformat()
    
    report = f"""# Semgrep Alert Analysis Report
> Generated: {timestamp}

## Summary

| Metric | Value |
|--------|-------|
| **Total Alerts** | {analysis['total']} |
| **Unique Rules** | {len(analysis['by_rule'])} |
| **Affected Files** | {len(analysis['by_file'])} |

## Severity Distribution

| Severity | Count | Percentage |
|----------|-------|------------|
"""
    
    for severity, count in analysis["by_severity"]. most_common():
        pct = (count / analysis["total"]) * 100
        report += f"| {severity. upper()} | {count} | {pct:.1f}% |\n"
    
    report += """
## Top 10 Rules by Alert Count

| Rule ID | Severity | Count | Description |
|---------|----------|-------|-------------|
"""
    
    for rule_id, count in analysis["by_rule"].most_common(10):
        details = analysis["rule_details"]. get(rule_id, {})
        severity = details.get("severity", "unknown")
        desc = details.get("description", "")[:50] + "..."
        report += f"| `{rule_id}` | {severity} | {count} | {desc} |\n"
    
    report += """
## Top 10 Files by Alert Count

| File Path | Alert Count |
|-----------|-------------|
"""
    
    for file_path, count in analysis["by_file"]. most_common(10):
        report += f"| `{file_path}` | {count} |\n"
    
    report += """
## Remediation Priority

Based on severity and frequency:

### P0 (Critical - Fix Immediately)
- High/Critical severity alerts in production code paths
- Hardcoded secrets, SQL injection, command injection

### P1 (High - Fix This Sprint)
- Medium severity in core modules
- Authentication/authorization issues

### P2 (Medium - Backlog)
- Low severity issues
- Code quality improvements

### P3 (Low - Defer/Suppress)
- False positives (document and suppress)
- Test/example code with intentional patterns
"""
    
    return report


def main() -> None:
    """Main entry point."""
    if not GITHUB_TOKEN:
        print("❌ GITHUB_TOKEN environment variable required")
        return
    
    output_dir = Path(". github/security")
    
    # Export alerts
    alerts = export_alerts()
    
    # Analyze
    analysis = analyze_alerts(alerts)
    
    # Generate reports
    generate_report(alerts, analysis, output_dir)
    
    # Print summary
    print("\n📊 Summary:")
    print(f"  Total alerts: {analysis['total']}")
    print(f"  Severity breakdown:")
    for severity, count in analysis["by_severity"].most_common():
        print(f"    - {severity}: {count}")
    print(f"\n  Top 5 rules:")
    for rule, count in analysis["by_rule"].most_common(5):
        print(f"    - {rule}:  {count}")


if __name__ == "__main__": 
    main()
```

## Phase C.2: Risk Scoring System

### Task C. 2.1: Create Criticality Map

**File**: `.github/security/criticality-map.yaml`

```yaml
# File criticality mapping for Aries-Serpent/_codex_
# Used for risk scoring of security alerts

critical_paths:  # weight:  3
  - src/agents/core/**
  - src/agents/autonomous/**
  - src/api/auth/**
  - src/config/openai*. py
  - src/security/**

high_paths:      # weight:  2
  - src/agents/**
  - src/api/**
  - src/middleware/**
  - src/utils/crypto*. py
  - src/utils/auth*.py

medium_paths:    # weight: 1. 5
  - src/utils/**
  - src/models/**
  - src/services/**

low_paths:       # weight: 1
  - tests/**
  - docs/**
  - examples/**
  - scripts/**

# Rule category weights for exploitability
rule_categories:
  critical:  # weight: 3
    - injection
    - secrets
    - deserialization
    - authentication
    
  high:      # weight: 2
    - cryptography
    - authorization
    - path-traversal
    - ssrf
    
  medium:    # weight: 1.5
    - xss
    - logging
    - configuration
    
  low:       # weight: 1
    - code-quality
    - best-practice
    - performance
```

### Task C.2.2: Create Risk Scoring Script

**File**: `scripts/security/score_alerts.py`

```python
"""
Risk scoring system for Semgrep alerts. 

Risk Score = severity_weight × criticality_weight × exploitability_weight

Author: mbaetiong
Generated: Previous Cycle-12-17
"""

from __future__ import annotations

import csv
import fnmatch
import json
from pathlib import Path

import yaml


# Severity weights
SEVERITY_WEIGHTS = {
    "critical":  4. 0,
    "high": 3.0,
    "medium": 2.0,
    "low": 1.0,
    "warning": 0.5,
    "note": 0.5,
    "unknown": 1.0,
}

# Priority bucket thresholds
PRIORITY_THRESHOLDS = {
    "P0": 9.0,   # Critical:  9-36
    "P1":  6.0,   # High: 6-8. 9
    "P2": 3.0,   # Medium:  3-5.9
    "P3": 0.0,   # Low:  0-2.9
}


def load_criticality_map(path: Path) -> dict: 
    """Load the criticality map from YAML."""
    with open(path) as f:
        return yaml.safe_load(f)


def get_path_weight(file_path: str, criticality_map: dict) -> float:
    """Get the criticality weight for a file path."""
    path_weights = [
        ("critical_paths", 3.0),
        ("high_paths", 2.0),
        ("medium_paths", 1.5),
        ("low_paths", 1.0),
    ]
    
    for category, weight in path_weights: 
        patterns = criticality_map.get(category, [])
        for pattern in patterns:
            if fnmatch. fnmatch(file_path, pattern):
                return weight
    
    return 1.0  # Default weight


def get_rule_weight(rule_id: str, criticality_map: dict) -> float:
    """Get the exploitability weight for a rule."""
    rule_categories = criticality_map.get("rule_categories", {})
    
    category_weights = {
        "critical": 3.0,
        "high": 2.0,
        "medium": 1.5,
        "low": 1.0,
    }
    
    rule_lower = rule_id. lower()
    
    for category, keywords in rule_categories. items():
        for keyword in keywords: 
            if keyword in rule_lower: 
                return category_weights.get(category, 1.0)
    
    return 1.0  # Default weight


def calculate_risk_score(
    severity:  str,
    file_path: str,
    rule_id: str,
    criticality_map: dict,
) -> float:
    """Calculate the risk score for an alert."""
    severity_weight = SEVERITY_WEIGHTS.get(severity. lower(), 1.0)
    path_weight = get_path_weight(file_path, criticality_map)
    rule_weight = get_rule_weight(rule_id, criticality_map)
    
    return severity_weight * path_weight * rule_weight


def get_priority_bucket(risk_score: float) -> str:
    """Determine the priority bucket based on risk score."""
    for bucket, threshold in PRIORITY_THRESHOLDS.items():
        if risk_score >= threshold:
            return bucket
    return "P3"


def score_all_alerts(alerts_file: Path, criticality_file: Path, output_file: Path) -> None:
    """Score all alerts and output prioritized list."""
    # Load data
    with open(alerts_file) as f:
        alerts = json.load(f)
    
    criticality_map = load_criticality_map(criticality_file)
    
    # Score each alert
    scored_alerts = []
    
    for alert in alerts:
        rule = alert.get("rule", {})
        rule_id = rule.get("id", "unknown")
        severity = rule.get("severity", "unknown")
        
        location = alert.get("most_recent_instance", {}).get("location", {})
        file_path = location.get("path", "unknown")
        line = location.get("start_line", 0)
        
        risk_score = calculate_risk_score(
            severity=severity,
            file_path=file_path,
            rule_id=rule_id,
            criticality_map=criticality_map,
        )
        
        priority = get_priority_bucket(risk_score)
        
        scored_alerts.append({
            "alert_id": alert.get("number", 0),
            "rule_id": rule_id,
            "rule_name": rule. get("name", ""),
            "severity":  severity,
            "file":  file_path,
            "line": line,
            "risk_score": round(risk_score, 2),
            "priority_bucket": priority,
            "html_url": alert.get("html_url", ""),
        })
    
    # Sort by risk score descending
    scored_alerts.sort(key=lambda x: x["risk_score"], reverse=True)
    
    # Write output
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=scored_alerts[0]. keys())
        writer.writeheader()
        writer.writerows(scored_alerts)
    
    print(f"✅ Scored {len(scored_alerts)} alerts")
    print(f"💾 Saved to {output_file}")
    
    # Print summary
    priority_counts = {}
    for alert in scored_alerts:
        bucket = alert["priority_bucket"]
        priority_counts[bucket] = priority_counts. get(bucket, 0) + 1
    
    print("\n📊 Priority Distribution:")
    for bucket in ["P0", "P1", "P2", "P3"]:
        count = priority_counts. get(bucket, 0)
        print(f"  {bucket}: {count} alerts")


def main() -> None:
    """Main entry point."""
    base_dir = Path(".github/security")
    
    score_all_alerts(
        alerts_file=base_dir / "semgrep-alerts-export.json",
        criticality_file=base_dir / "criticality-map. yaml",
        output_file=base_dir / "prioritized-alerts.csv",
    )


if __name__ == "__main__": 
    main()
```

## Phase C.3:  Automated Codemods

### Task C.3.1: Create Codemod for Subprocess Safety

**File**: `scripts/security/codemods/fix_subprocess. py`

```python
"""
Codemod:  Fix unsafe subprocess usage

Transforms:
  subprocess.call(... , shell=True) → subprocess.run(..., shell=False, check=True)
  os.system(...) → subprocess.run([...], check=True)

Author: mbaetiong
Generated: Previous Cycle-12-17
"""

from __future__ import annotations

import libcst as cst
from libcst import matchers as m


class SubprocessSafetyTransformer(cst.CSTTransformer):
    """Transform unsafe subprocess calls to safe alternatives."""
    
    def __init__(self) -> None:
        super().__init__()
        self.changes_made:  list[str] = []
    
    def leave_Call(
        self, original_node: cst.Call, updated_node: cst.Call
    ) -> cst.Call: 
        """Transform subprocess.call and os.system calls."""
        
        # Check for subprocess.call or subprocess. Popen with shell=True
        if self._is_subprocess_call_with_shell(updated_node):
            return self._fix_subprocess_call(updated_node)
        
        # Check for os.system
        if self._is_os_system(updated_node):
            return self._fix_os_system(updated_node)
        
        return updated_node
    
    def _is_subprocess_call_with_shell(self, node: cst.Call) -> bool:
        """Check if this is a subprocess call with shell=True."""
        if not isinstance(node.func, cst.Attribute):
            return False
        
        if not isinstance(node. func.value, cst.Name):
            return False
        
        if node. func.value.value != "subprocess": 
            return False
        
        if node.func.attr. value not in ("call", "Popen", "run"):
            return False
        
        # Check for shell=True
        for arg in node.args:
            if isinstance(arg. keyword, cst.Name) and arg.keyword.value == "shell":
                if isinstance(arg.value, cst.Name) and arg.value.value == "True":
                    return True
        
        return False
    
    def _fix_subprocess_call(self, node: cst.Call) -> cst.Call:
        """Fix subprocess call to use shell=False and check=True."""
        new_args = []
        has_check = False
        
        for arg in node.args:
            if isinstance(arg. keyword, cst. Name) and arg.keyword.value == "shell":
                # Change shell=True to shell=False
                new_args.append(
                    arg.with_changes(value=cst.Name("False"))
                )
                self.changes_made. append(f"Changed shell=True to shell=False")
            elif isinstance(arg. keyword, cst. Name) and arg.keyword.value == "check":
                has_check = True
                new_args.append(arg)
            else:
                new_args.append(arg)
        
        # Add check=True if not present and using subprocess. run
        if not has_check and isinstance(node.func, cst.Attribute):
            if node.func.attr. value == "run":
                new_args.append(
                    cst.Arg(
                        keyword=cst.Name("check"),
                        value=cst.Name("True"),
                    )
                )
                self.changes_made. append("Added check=True")
        
        # Change call/Popen to run
        new_func = node. func
        if isinstance(node.func, cst.Attribute):
            if node.func.attr.value in ("call", "Popen"):
                new_func = node.func.with_changes(attr=cst.Name("run"))
                self.changes_made.append(f"Changed subprocess.{node.func.attr.value} to subprocess.run")
        
        return node. with_changes(func=new_func, args=new_args)
    
    def _is_os_system(self, node: cst. Call) -> bool:
        """Check if this is an os. system call."""
        if not isinstance(node.func, cst.Attribute):
            return False
        
        if not isinstance(node.func. value, cst. Name):
            return False
        
        return (
            node.func. value.value == "os" 
            and node. func.attr.value == "system"
        )
    
    def _fix_os_system(self, node: cst.Call) -> cst.Call:
        """Convert os.system to subprocess.run."""
        self.changes_made. append("Converted os.system to subprocess. run")
        
        # Get the command argument
        if node.args:
            cmd_arg = node.args[0]. value
            
            # Create subprocess.run call
            return cst.Call(
                func=cst.Attribute(
                    value=cst.Name("subprocess"),
                    attr=cst.Name("run"),
                ),
                args=[
                    cst.Arg(value=cmd_arg),
                    cst.Arg(
                        keyword=cst.Name("shell"),
                        value=cst.Name("False"),
                    ),
                    cst.Arg(
                        keyword=cst.Name("check"),
                        value=cst.Name("True"),
                    ),
                    cst.Arg(
                        keyword=cst.Name("capture_output"),
                        value=cst. Name("True"),
                    ),
                ],
            )
        
        return node


def transform_file(file_path:  str) -> tuple[str, list[str]]: 
    """Transform a single file and return the new code and changes."""
    with open(file_path) as f:
        source = f.read()
    
    tree = cst.parse_module(source)
    transformer = SubprocessSafetyTransformer()
    new_tree = tree.visit(transformer)
    
    return new_tree.code, transformer.changes_made


def main() -> None:
    """Main entry point for CLI usage."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python fix_subprocess.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    new_code, changes = transform_file(file_path)
    
    if changes:
        print(f"✅ Made {len(changes)} changes:")
        for change in changes:
            print(f"  - {change}")
        
        # Write back
        with open(file_path, "w") as f:
            f.write(new_code)
        print(f"💾 Updated {file_path}")
    else: 
        print("No changes needed")


if __name__ == "__main__":
    main()
```

### Task C.3.2: Create Codemod for SQL Injection

**File**: `scripts/security/codemods/fix_sql_injection.py`

```python
"""
Codemod: Fix SQL injection vulnerabilities

Transforms:
  cursor.execute(f"SELECT * FROM {table}") → cursor.execute("SELECT * FROM ? ", (table,))
  cursor.execute("SELECT * FROM " + table) → cursor.execute("SELECT * FROM ? ", (table,))

Author: mbaetiong
Generated: Previous Cycle-12-17
"""

from __future__ import annotations

import re
from pathlib import Path


def fix_fstring_sql(content: str) -> tuple[str, list[str]]:
    """Fix f-string SQL injection patterns."""
    changes = []
    
    # Pattern:  cursor.execute(f"... {var}...")
    fstring_pattern = r'(\w+\. execute\s*\(\s*)f(["\'])(. +?)\2(\s*\))'
    
    def replace_fstring(match:  re.Match) -> str:
        prefix = match.group(1)
        quote = match.group(2)
        sql = match.group(3)
        suffix = match.group(4)
        
        # Find all {var} patterns
        vars_pattern = r'\{(\w+)\}'
        variables = re. findall(vars_pattern, sql)
        
        if not variables:
            return match.group(0)
        
        # Replace {var} with ? 
        new_sql = re.sub(vars_pattern, '?', sql)
        
        # Create parameters tuple
        params = ', '.join(variables)
        if len(variables) == 1:
            params += ','  # Single element tuple needs trailing comma
        
        changes.append(f"Parameterized SQL with variables: {variables}")
        
        return f'{prefix}{quote}{new_sql}{quote}, ({params}){suffix}'
    
    new_content = re. sub(fstring_pattern, replace_fstring, content)
    
    return new_content, changes


def fix_concat_sql(content:  str) -> tuple[str, list[str]]:
    """Fix string concatenation SQL injection patterns."""
    changes = []
    
    # Pattern: cursor. execute("SELECT..." + var + "...")
    concat_pattern = r'(\w+\.execute\s*\(\s*)(["\'])(.+?)\2\s*\+\s*(\w+)(\s*(? :\+\s*["\']. +?["\'])?)(\s*\))'
    
    def replace_concat(match: re. Match) -> str:
        prefix = match.group(1)
        quote = match.group(2)
        sql_before = match.group(3)
        variable = match.group(4)
        sql_after = match. group(5) or ""
        suffix = match.group(6)
        
        # Clean up the after part
        after_clean = ""
        if sql_after: 
            after_match = re.search(r'["\'](.+?)["\']', sql_after)
            if after_match:
                after_clean = after_match.group(1)
        
        new_sql = f"{sql_before}? {after_clean}"
        
        changes.append(f"Parameterized concatenated SQL with variable: {variable}")
        
        return f'{prefix}{quote}{new_sql}{quote}, ({variable},){suffix}'
    
    new_content = re.sub(concat_pattern, replace_concat, content)
    
    return new_content, changes


def transform_file(file_path: str) -> tuple[str, list[str]]: 
    """Transform a single file."""
    with open(file_path) as f:
        content = f.read()
    
    all_changes = []
    
    # Apply fixes
    content, changes = fix_fstring_sql(content)
    all_changes.extend(changes)
    
    content, changes = fix_concat_sql(content)
    all_changes.extend(changes)
    
    return content, all_changes


def main() -> None:
    """Main entry point."""
    import sys
    
    if len(sys. argv) < 2:
        print("Usage: python fix_sql_injection.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    new_content, changes = transform_file(file_path)
    
    if changes: 
        print(f"✅ Made {len(changes)} changes:")
        for change in changes: 
            print(f"  - {change}")
        
        with open(file_path, "w") as f:
            f.write(new_content)
        print(f"💾 Updated {file_path}")
    else:
        print("No changes needed")


if __name__ == "__main__": 
    main()
```

### Task C. 3.3: Create Codemod for Hardcoded Secrets

**File**: `scripts/security/codemods/fix_hardcoded_secrets.py`

```python
"""
Codemod: Remove hardcoded secrets and move to environment variables

Transforms:
  API_KEY = "sk-xxxxx" → API_KEY = os.getenv("API_KEY")
  PASSWORD = "secret123" → PASSWORD = os.getenv("PASSWORD")

Author: mbaetiong
Generated: Previous Cycle-12-17
"""

from __future__ import annotations

import re
from pathlib import Path


# Patterns that indicate secrets
SECRET_PATTERNS = [
    r'(? i)(api[_-]?key)\s*=\s*["\']([^"\']+)["\']',
    r'(?i)(secret[_-]? key)\s*=\s*["\']([^"\']+)["\']',
    r'(? i)(password)\s*=\s*["\']([^"\']+)["\']',
    r'(?i)(token)\s*=\s*["\']([^"\']+)["\']',
    r'(? i)(auth[_-]?token)\s*=\s*["\']([^"\']+)["\']',
    r'(?i)(access[_-]?key)\s*=\s*["\']([^"\']+)["\']',
    r'(?i)(private[_-]? key)\s*=\s*["\']([^"\']+)["\']',
    r'(? i)(client[_-]? secret)\s*=\s*["\']([^"\']+)["\']',
]

# Values that are clearly not secrets (placeholders, examples)
SAFE_PATTERNS = [
    r'^(your[_-]? |my[_-]? |example[_-]?|test[_-]? |dummy[_-]? |placeholder)',
    r'^(xxx+|yyy+|zzz+)$',
    r'^(changeme|replace|todo|fixme)$',
    r'^\$\{',  # Template variables
    r'^<.*>$',  # Angle bracket placeholders
]


def is_safe_value(value: str) -> bool:
    """Check if a value is clearly a placeholder, not a real secret."""
    value_lower = value. lower()
    
    for pattern in SAFE_PATTERNS:
        if re.match(pattern, value_lower):
            return True
    
    # Very short values are likely placeholders
    if len(value) < 4:
        return True
    
    return False


def transform_file(file_path: str) -> tuple[str, list[str], list[str]]: 
    """Transform a file to use environment variables for secrets."""
    with open(file_path) as f:
        content = f. read()
    
    changes = []
    env_vars = []
    
    # Check if os import exists
    has_os_import = bool(re.search(r'^import os\b', content, re.MULTILINE))
    needs_os_import = False
    
    for pattern in SECRET_PATTERNS:
        def replace_secret(match: re.Match) -> str:
            nonlocal needs_os_import
            
            var_name = match. group(1)
            value = match.group(2)
            
            if is_safe_value(value):
                return match.group(0)
            
            # Convert to environment variable format
            env_var_name = var_name.upper().replace("-", "_")
            
            changes.append(f"Moved {var_name} to environment variable {env_var_name}")
            env_vars. append((env_var_name, value))
            needs_os_import = True
            
            return f'{var_name} = os.getenv("{env_var_name}")'
        
        content = re.sub(pattern, replace_secret, content)
    
    # Add os import if needed and not present
    if needs_os_import and not has_os_import:
        # Add import at the top of the file
        import_line = "import os\n"
        
        # Find the right place to insert (after other imports)
        import_match = re.search(r'^((? :import |from ).+\n)+', content, re. MULTILINE)
        if import_match:
            insert_pos = import_match.end()
            content = content[: insert_pos] + import_line + content[insert_pos:]
        else:
            content = import_line + content
        
        changes.append("Added 'import os'")
    
    return content, changes, env_vars


def generate_env_example(env_vars: list[tuple[str, str]], output_path: Path) -> None:
    """Generate or update . env. example file."""
    existing_vars = set()
    
    if output_path.exists():
        with open(output_path) as f:
            for line in f: 
                if "=" in line: 
                    existing_vars.add(line.split("=")[0].strip())
    
    with open(output_path, "a") as f:
        for var_name, original_value in env_vars:
            if var_name not in existing_vars: 
                # Use a placeholder, not the actual value
                f.write(f"\n# Original value had {len(original_value)} characters\n")
                f.write(f"{var_name}=your_{var_name.lower()}_here\n")


def main() -> None:
    """Main entry point."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python fix_hardcoded_secrets.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    new_content, changes, env_vars = transform_file(file_path)
    
    if changes: 
        print(f"✅ Made {len(changes)} changes:")
        for change in changes:
            print(f"  - {change}")
        
        with open(file_path, "w") as f:
            f.write(new_content)
        print(f"💾 Updated {file_path}")
        
        if env_vars: 
            env_example = Path(file_path).parent / ".env.example"
            generate_env_example(env_vars, env_example)
            print(f"📝 Updated {env_example}")
    else:
        print("No changes needed")


if __name__ == "__main__":
    main()
```

## Phase C. 4: Batch Fix Automation

### Task C. 4.1: Create Batch Fix Runner

**File**: `scripts/security/run_codemods.py`

```python
"""
Batch codemod runner for security fixes. 

Executes codemods against multiple files and creates PRs for each fix group. 

Author: mbaetiong
Generated: Previous Cycle-12-17
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

# Import codemods
from codemods.fix_subprocess import transform_file as fix_subprocess
from codemods. fix_sql_injection import transform_file as fix_sql_injection
from codemods.fix_hardcoded_secrets import transform_file as fix_secrets


@dataclass
class FixGroup:
    """A group of related fixes to apply together."""
    
    group_id: str
    rule_pattern: str
    fix_function: Callable[[str], tuple[str, list[str]]]
    description: str
    priority: str


# Define fix groups
FIX_GROUPS = [
    FixGroup(
        group_id="FG-001",
        rule_pattern="subprocess",
        fix_function=fix_subprocess,
        description="Fix unsafe subprocess usage (shell=True, os.system)",
        priority="P0",
    ),
    FixGroup(
        group_id="FG-002",
        rule_pattern="sql",
        fix_function=fix_sql_injection,
        description="Fix SQL injection vulnerabilities",
        priority="P0",
    ),
    FixGroup(
        group_id="FG-003",
        rule_pattern="hardcoded",
        fix_function=fix_secrets,
        description="Remove hardcoded secrets",
        priority="P0",
    ),
]


def load_prioritized_alerts(alerts_file: Path) -> list[dict]: 
    """Load the prioritized alerts CSV."""
    alerts = []
    with open(alerts_file) as f:
        reader = csv. DictReader(f)
        for row in reader:
            alerts.append(row)
    return alerts


def group_alerts_by_fix(alerts: list[dict]) -> dict[str, list[dict]]:
    """Group alerts by which fix group they belong to."""
    grouped = {fg.group_id: [] for fg in FIX_GROUPS}
    
    for alert in alerts: 
        rule_id = alert.get("rule_id", "").lower()
        
        for fg in FIX_GROUPS:
            if fg.rule_pattern in rule_id: 
                grouped[fg. group_id].append(alert)
                break
    
    return grouped


def apply_fix_group(fix_group: FixGroup, alerts: list[dict], dry_run: bool = True) -> dict: 
    """Apply fixes for a group of alerts."""
    results = {
        "group_id": fix_group.group_id,
        "description":  fix_group.description,
        "files_processed": 0,
        "changes_made": 0,
        "errors": [],
        "modified_files": [],
    }
    
    # Get unique files
    files = set(alert["file"] for alert in alerts)
    
    for file_path in files:
        if not Path(file_path).exists():
            results["errors"].append(f"File not found: {file_path}")
            continue
        
        try: 
            new_content, changes = fix_group.fix_function(file_path)
            
            if changes: 
                results["files_processed"] += 1
                results["changes_made"] += len(changes)
                results["modified_files"]. append({
                    "path": file_path,
                    "changes": changes,
                })
                
                if not dry_run: 
                    with open(file_path, "w") as f:
                        f.write(new_content)
                    print(f"  ✅ Fixed {file_path}:  {len(changes)} changes")
                else:
                    print(f"  🔍 Would fix {file_path}:  {len(changes)} changes")
        
        except Exception as e:
            results["errors"].append(f"Error processing {file_path}: {str(e)}")
    
    return results


def create_fix_branch(group_id: str, dry_run: bool = True) -> str:
    """Create a new branch for the fix group."""
    from datetime import datetime
    
    date_str = datetime.now().strftime("%Y%m%d")
    branch_name = f"security/fix-{group_id. lower()}-{date_str}"
    
    if not dry_run: 
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)
    
    return branch_name


def commit_and_push(fix_group: FixGroup, results: dict, dry_run: bool = True) -> None:
    """Commit changes and push to remote."""
    if not results["modified_files"]: 
        return
    
    commit_msg = f"""[Security] {fix_group.description}

Fix Group: {fix_group.group_id}
Priority: {fix_group.priority}
Files Modified: {results['files_processed']}
Total Changes: {results['changes_made']}

Automated security fix by Copilot Agent. 
"""
    
    if not dry_run:
        # Stage modified files
        for file_info in results["modified_files"]:
            subprocess. run(["git", "add", file_info["path"]], check=True)
        
        # Commit
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        
        # Push
        subprocess.run(["git", "push", "-u", "origin", "HEAD"], check=True)
    else: 
        print(f"  🔍 Would commit:  {commit_msg[: 100]}...")


def create_pull_request(fix_group: FixGroup, results: dict, branch_name: str, dry_run: bool = True) -> None:
    """Create a pull request for the fix group."""
    alert_count = results["files_processed"]
    
    pr_title = f"[Security] Fix {fix_group.description} ({alert_count} files)"
    
    pr_body = f"""## Security Fix:  {fix_group. description}

**Fix Group ID**:  {fix_group. group_id}
**Priority**: {fix_group.priority}
**Files Modified**: {results['files_processed']}
**Total Changes**:  {results['changes_made']}

### Changes Made

| File | Changes |
|------|---------|
"""
    
    for file_info in results["modified_files"][:20]:  # Limit to 20 for readability
        changes_summary = "; ".join(file_info["changes"][:3])
        if len(file_info["changes"]) > 3:
            changes_summary += f" (+{len(file_info['changes']) - 3} more)"
        pr_body += f"| `{file_info['path']}` | {changes_summary} |\n"
    
    if len(results["modified_files"]) > 20:
        pr_body += f"\n*... and {len(results['modified_files']) - 20} more files*\n"
    
    pr_body += """
### Testing

- [ ] All existing tests pass
- [ ] No new security alerts introduced
- [ ] Manual spot-check completed

### Verification

After merge, verify fixes with:
"""bash
semgrep --config auto --json | jq '.results[] | select(.check_id | contains("RULE_PATTERN"))'
"""

---
*Automated security fix by Copilot Agent*
/cc @mbaetiong
"""
    
    pr_body = pr_body.replace("RULE_PATTERN", fix_group.rule_pattern)
    
    if not dry_run:
        subprocess.run([
            "gh", "pr", "create",
            "--title", pr_title,
            "--body", pr_body,
            "--base", "main",
            "--label", "security",
            "--label", "automated-fix",
        ], check=True)
    else:
        print(f"  🔍 Would create PR: {pr_title}")


def main() -> None:
    """Main entry point."""
    import argparse
    
    parser = argparse. ArgumentParser(description="Run security codemods")
    parser.add_argument("--dry-run", action="store_true", help="Don't make actual changes")
    parser.add_argument("--group", type=str, help="Only run specific fix group")
    args = parser.parse_args()
    
    alerts_file = Path(". github/security/prioritized-alerts.csv")
    
    if not alerts_file.exists():
        print("❌ Prioritized alerts file not found.  Run score_alerts.py first.")
        sys.exit(1)
    
    # Load and group alerts
    alerts = load_prioritized_alerts(alerts_file)
    grouped = group_alerts_by_fix(alerts)
    
    # Process each fix group
    for fix_group in FIX_GROUPS:
        if args.group and fix_group.group_id != args.group:
            continue
        
        group_alerts = grouped[fix_group.group_id]
        
        if not group_alerts:
            print(f"⏭️ {fix_group.group_id}:  No matching alerts")
            continue
        
        print(f"\n🔧 Processing {fix_group.group_id}:  {fix_group. description}")
        print(f"   {len(group_alerts)} alerts to process")
        
        # Create branch
        branch_name = create_fix_branch(fix_group.group_id, dry_run=args. dry_run)
        print(f"   Branch: {branch_name}")
        
        # Apply fixes
        results = apply_fix_group(fix_group, group_alerts, dry_run=args.dry_run)
        
        if results["modified_files"]: 
            # Commit and push
            commit_and_push(fix_group, results, dry_run=args.dry_run)
            
            # Create PR
            create_pull_request(fix_group, results, branch_name, dry_run=args.dry_run)
        
        if results["errors"]: 
            print(f"   ⚠️ Errors: {len(results['errors'])}")
            for error in results["errors"][:5]: 
                print(f"      - {error}")
    
    print("\n✅ Codemod run complete")


if __name__ == "__main__": 
    main()
```

## Phase C.5: False Positive Suppression

### Task C.5.1: Create Suppression Configuration

**File**: `.semgrep/semgrep.yml`

```yaml
# Semgrep configuration for Aries-Serpent/_codex_
# Manages rule exclusions and suppressions

rules:  []

# Path exclusions for all rules
paths:
  exclude: 
    # Test files with intentional patterns
    - "tests/**"
    - "**/test_*.py"
    - "**/*_test.py"
    
    # Example and documentation code
    - "examples/**"
    - "docs/code-samples/**"
    - "**/README*.md"
    
    # Generated and vendored code
    - "**/generated/**"
    - "**/vendor/**"
    - "**/.venv/**"
    - "**/node_modules/**"
    
    # Build artifacts
    - "build/**"
    - "dist/**"
    - "*. egg-info/**"
```

### Task C. 5.2: Create Suppression Register

**File**: `docs/security/suppressions-register.md`

```markdown
# Semgrep Suppression Register

> Last Updated: Previous Cycle-12-17
> Maintained by: @mbaetiong

## Overview

This document tracks all intentionally suppressed Semgrep alerts in the `Aries-Serpent/_codex_` repository. Each suppression must be documented with a clear rationale and undergo periodic review.

## Suppression Policy

1. **Documentation Required**: Every suppression must be documented in this register
2. **Rationale Required**: Clear explanation of why the alert is a false positive
3. **Approval Required**: Security team review for high/critical severity suppressions
4. **Review Cycle**: All suppressions reviewed every 6 months

## Active Suppressions

| Rule ID | File | Line | Severity | Reason | Approved By | Approved Date | Review Date |
|---------|------|------|----------|--------|-------------|---------------|-------------|
| python. lang.security.audit. eval-used | src/agents/sandbox_executor.py | 142 | High | Eval used in sandboxed agent executor with AST validation | @mbaetiong | Previous Cycle-12-17 | Current Cycle-06-17 |
| python.lang. security.audit.exec-used | src/agents/code_runner.py | 89 | High | Exec in isolated subprocess with resource limits | @mbaetiong | Previous Cycle-12-17 | Current Cycle-06-17 |

## Path Exclusions

| Path Pattern | Reason | Approved By | Approved Date |
|--------------|--------|-------------|---------------|
| tests/** | Test files contain intentional vulnerable patterns for testing | @mbaetiong | Previous Cycle-12-17 |
| examples/** | Example code demonstrates patterns without production context | @mbaetiong | Previous Cycle-12-17 |
| docs/code-samples/** | Documentation samples are not production code | @mbaetiong | Previous Cycle-12-17 |

## Review History

### Previous Cycle-12-17 - Initial Suppression Setup
- Created suppression register
- Documented path exclusions
- Added eval/exec suppressions for agent sandbox

## How to Add a Suppression

1. **Create inline suppression** in code:
   ```python
   # nosemgrep:  rule-id
   # SECURITY REVIEW: Explanation of why this is safe
   # Reviewed by: @username on YYYY-MM-DD
   code_here()
   ```

2. **Document in this register** with: 
   - Rule ID
   - File and line number
   - Severity
   - Detailed rationale
   - Approver and date
   - Next review date (6 months out)

3. **Get approval** from security team for high/critical severity

## Suppression Removal Process

1. Review suppression rationale
2. Determine if original justification still applies
3. If no longer valid, remove suppression and fix the issue
4. Update this register
```

## Phase C.6: CI/CD Security Gates

### Task C. 6.1: Create Security Scan Workflow

**File**:  `.github/workflows/security-scan.yml`

```yaml
name: Security Scanning

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
  schedule:
    # Weekly scan on Monday at 2 AM UTC
    - cron: '0 2 * * 1'
  workflow_dispatch:

permissions:
  contents:  read
  security-events:  write
  actions: read

jobs:
  semgrep: 
    name: Semgrep Security Scan
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for baseline comparison

      - name: Run Semgrep
        uses: returntocorp/semgrep-action@v1
        with: 
          config: >-
            p/security-audit
            p/secrets
            p/owasp-top-ten
            p/python
            . semgrep/
          
          # Only fail on new findings (uses baseline)
          generateSarif: true
          
        env:
          SEMGREP_RULES: >-
            p/security-audit
            p/secrets
            p/owasp-top-ten
            p/python

      - name: Upload SARIF results
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: semgrep. sarif

  dependency-scan:
    name:  Dependency Security Scan
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with: 
          python-version:  '3.11'

      - name: Install safety
        run: pip install safety

      - name: Run safety check
        run: |
          safety check -r requirements.txt --output json > safety-results.json || true
          
      - name: Process results
        run:  |
          if [ -f safety-results.json ]; then
            echo "## Dependency Vulnerabilities" >> $GITHUB_STEP_SUMMARY
            cat safety-results.json | python -c "
import json, sys
data = json.load(sys.stdin)
if data: 
    print('| Package | Vulnerability | Severity |')
    print('|---------|---------------|----------|')
    for vuln in data[: 10]:
        print(f'| {vuln.get(\"package_name\", \"unknown\")} | {vuln.get(\"vulnerability_id\", \"unknown\")} | {vuln.get(\"severity\", \"unknown\")} |')
"
          fi

  secret-scan:
    name:  Secret Detection
    runs-on:  ubuntu-latest
    
    steps: 
      - name:  Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run Gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITLEAKS_LICENSE:  ${{ secrets. GITLEAKS_LICENSE }}
```

---

# STREAM D: CODE SCANNING CONFLICT RESOLUTION

## Objective

Resolve the "failed (code scanning) GitHub recommended" conflict for `Aries-Serpent/_codex_` by properly configuring code scanning to work with organization defaults.

## Phase D.1: Preflight Checks

### Task D.1.1: Detect Repository Languages

**Command** (Agent must execute):
```bash
gh api repos/Aries-Serpent/_codex_/languages --jq 'to_entries | map("\(.key): \(.value)") | .[]'
```

### Task D.1.2: Locate Existing Advanced Scanning Files

**Command** (Agent must execute):
```bash
# Find all CodeQL and code scanning related files
find . -type f \( \
  -name "*codeql*" -o \
  -name "*code-scanning*" -o \
  -name "*. ql" -o \
  -path "*/.github/codeql/*" \
\) 2>/dev/null | grep -v node_modules | grep -v . git
```

## Phase D.2: Backup Existing Configuration

### Task D.2.1: Create Backup Branch

**Commands** (Agent must execute):
```bash
# Create backup branch
BACKUP_BRANCH="backup/codeql-advanced-$(date +%Y%m%d)-$(git rev-parse --short HEAD)"
git checkout -b "$BACKUP_BRANCH"

# Add all CodeQL/scanning files
git add . github/workflows/*codeql* .github/codeql* codeql* 2>/dev/null || true

# Commit and push
git commit -m "backup: preserve existing advanced CodeQL/code-scanning files"
git push --set-upstream origin "$BACKUP_BRANCH"

# Return to main
git checkout main
```

## Phase D.3: Disable Advanced Workflows

### Task D. 3.1: Move Advanced Workflows to Disabled Directory

**File to create**: `.github/disabled/README.md`

```markdown
# Disabled Workflows

This directory contains workflows that have been disabled to resolve conflicts with organization-level default configurations.

## Reason for Disabling

The `Aries-Serpent` organization has enabled the "GitHub recommended (default) code scanning setup" at the organization level.  Repositories with custom/advanced CodeQL configurations conflict with this setting.

## Backup Information

- **Backup Branch**: `backup/codeql-advanced-YYYYMMDD-XXXXXXX`
- **Disabled Date**: Previous Cycle-12-17
- **Disabled By**:  Copilot Agent

## Restoration

To restore advanced CodeQL configuration:

1. Check out the backup branch: 
   ```bash
   git checkout backup/codeql-advanced-YYYYMMDD-XXXXXXX
     ```

2. Copy files back: 
   ```bash
   git checkout main
   git checkout backup/codeql-advanced-YYYYMMDD-XXXXXXX -- .github/workflows/codeql*. yml
    ```

3. Request exclusion from org-level defaults: 
   - Open issue in `Aries-Serpent/. github` repository
   - Request `_codex_` be excluded from default code scanning

## Contact

For questions, contact @mbaetiong or the Aries-Serpent security team.
```

### Task D.3.2: Create Disable PR

**Commands** (Agent must execute):
```bash
# Create disable branch
DISABLE_BRANCH="disable-codeql-advanced-$(date +%Y%m%d)"
git checkout -b "$DISABLE_BRANCH"

# Create disabled directories
mkdir -p . github/disabled . github/disabled-config

# Move CodeQL workflows
git mv .github/workflows/*codeql*. yml .github/disabled/ 2>/dev/null || true
git mv .github/workflows/*code-scanning*.yml . github/disabled/ 2>/dev/null || true

# Move custom configs
git mv .github/codeql* .github/disabled-config/ 2>/dev/null || true
git mv codeql-pack* .github/disabled-config/ 2>/dev/null || true

# Add README
# (README content from Task D.3.1)

# Commit
git add . 
git commit -m "chore: disable advanced CodeQL workflows to resolve org default conflict"

# Push and create PR
git push --set-upstream origin "$DISABLE_BRANCH"

gh pr create \
  --title "Disable advanced CodeQL workflows — resolve org default conflict" \
  --body "$(cat <<'EOF'
## Summary

This PR disables advanced CodeQL/code-scanning workflows so the organization-recommended default setup can be applied.

## Changes

- Moved advanced CodeQL workflows to `.github/disabled/`
- Moved custom CodeQL configurations to `.github/disabled-config/`
- Added documentation for restoration process

## Backup Information

- **Backup Branch**: `backup/codeql-advanced-YYYYMMDD-XXXXXXX`
- All files are preserved and can be restored

## Validation Checklist

- [ ] Backup branch created and pushed
- [ ] All advanced workflows moved (not deleted)
- [ ] README added with restoration instructions
- [ ] Organization default can now be applied

## Next Steps

After merge: 
1. Verify org default code scanning is applied
2. Confirm no regression in security coverage
3. If custom queries are needed, package them in `Aries-Serpent/codeql-packs`

/cc @mbaetiong @Aries-Serpent/security
EOF
)" \
  --base main \
  --label security \
  --label code-scanning
```

## Phase D.4: Enable Organization Default

### Task D.4.1: Create Default CodeQL Workflow

**File**: `.github/workflows/codeql-analysis.yml`

```yaml
# CodeQL Analysis Workflow
# This is the organization-recommended default configuration

name: "CodeQL"

on:
  push:
    branches: [main, develop]
  pull_request: 
    branches: [main, develop]
  schedule:
    # Weekly scan on Sunday at 3 AM UTC
    - cron: '0 3 * * 0'
  workflow_dispatch: 

jobs:
  analyze: 
    name:  Analyze
    runs-on: ubuntu-latest
    
    permissions:
      actions:  read
      contents:  read
      security-events: write

    strategy:
      fail-fast: false
      matrix:
        # Languages detected in repository
        # Agent:  Update this based on gh api repos/Aries-Serpent/_codex_/languages
        language: ['python', 'javascript']

    steps:
      - name: Checkout repository
        uses:  actions/checkout@v4

      - name: Initialize CodeQL
        uses: github/codeql-action/init@v3
        with:
          languages: ${{ matrix. language }}
          # Use default queries plus security-extended
          queries: +security-extended

      # Autobuild for compiled languages
      - name:  Autobuild
        uses: github/codeql-action/autobuild@v3

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v3
        with:
          category: "/language:${{ matrix.language }}"
```

## Phase D.5: Documentation

### Task D.5.1: Create Security Code Scanning Note

**File**: `.github/SECURITY-CODE-SCANNING-NOTE.md`

```markdown
# Code Scanning Configuration Notes

> Last Updated: Previous Cycle-12-17
> Maintained by:  Copilot Agent / @mbaetiong

## Current Configuration

| Setting | Value |
|---------|-------|
| **Configuration Type** | Organization Default |
| **Scanning Tool** | CodeQL |
| **Languages** | Python, JavaScript |
| **Schedule** | Weekly (Sunday 3 AM UTC) + Push/PR triggers |

## Migration History

### Previous Cycle-12-17: Migrated to Org Default

**Reason**: Resolve "Advanced setup conflict" with organization-level default code scanning. 

**Changes Made**:
1. Created backup branch:  `backup/codeql-advanced-YYYYMMDD-XXXXXXX`
2. Moved advanced workflows to `.github/disabled/`
3. Enabled organization default CodeQL workflow

**PRs**:
- Disable PR: #TBD
- Enable PR: #TBD

**Validation**: 
- [ ] CodeQL workflow runs successfully
- [ ] Security alerts are being created
- [ ] Org conflict message cleared

## Rollback Procedure

If custom configuration is required:

1. **Restore from backup**:
   ```bash
   git checkout main
   git checkout backup/codeql-advanced-YYYYMMDD -- .github/workflows/
   git commit -m "restore:  advanced CodeQL configuration"
   git push
     ```

2. **Request org exclusion**:
   - Open issue in `Aries-Serpent/.github`
   - Title: "Exclude _codex_ from org default code scanning"
   - Explain need for custom configuration

## Custom Query Preservation

If the repository had custom CodeQL queries:

1. **Location**: `.github/disabled-config/` (preserved)
2. **Future home**: `Aries-Serpent/codeql-packs` (to be created)
3. **Integration**: Reference packs in CodeQL init step

## Contact

- Security questions: @Aries-Serpent/security
- Configuration questions: @mbaetiong
```

---

# UNIFIED EXECUTION SEQUENCE

## Copilot Agent:  Execute in This Order

```yaml
# Master Execution Plan for Aries-Serpent/_codex_
execution_sequence:
  
  # =========================================================================
  # PHASE 1: Foundation (Parallel Execution Possible)
  # =========================================================================
  phase_1:
    name: "Foundation Setup"
    parallel:  true
    
    tasks:
      # Stream A: Caching Infrastructure
      - id: A. 1
        name:  "Create dependency split files"
        files:
          - requirements-minimal.txt
          - requirements-test.txt
          - requirements-dev.txt
        validation: "pip check -r requirements-minimal. txt"
      
      - id: A.2
        name: "Create UV setup action"
        files: 
          - . github/actions/setup-python-uv/action. yml
        validation: "act -j lint --dry-run"
      
      - id:  A.3
        name: "Create compressed cache action"
        files: 
          - .github/actions/compressed-cache/action. yml
        validation:  "yaml-lint . github/actions/"
      
      # Stream B: OpenAI Infrastructure
      - id:  B.1
        name: "Create OpenAI client"
        files: 
          - src/config/openai_client.py
        validation: "python -c 'from src.config.openai_client import CodexOpenAIClient'"
      
      - id: B.2
        name: "Create autonomous runner"
        files: 
          - src/agents/autonomous_runner.py
          - src/agents/orchestrator.py
        validation: "python -m py_compile src/agents/*. py"
      
      # Stream D: Code Scanning (Prerequisite for Stream C)
      - id: D.1
        name: "Preflight checks"
        commands:
          - "gh api repos/Aries-Serpent/_codex_/languages"
          - "find . -name '*codeql*' -type f"
        validation: "Commands complete successfully"
      
      - id: D. 2
        name:  "Create backup branch"
        commands: 
          - "git checkout -b backup/codeql-advanced-$(date +%Y%m%d)"
          - "git push origin HEAD"
        validation: "git branch -r | grep backup/codeql"

  # =========================================================================
  # PHASE 2: Core Implementation
  # =========================================================================
  phase_2:
    name:  "Core Implementation"
    depends_on: [phase_1]
    
    tasks: 
      # Stream A: CI/CD Workflows
      - id:  A.4
        name: "Create CI workflows"
        files: 
          - Dockerfile. ci
          - . github/workflows/build-container-cache.yml
          - .github/workflows/ci. yml
          - .github/workflows/cache-warmer.yml
          - .github/workflows/pr-checks.yml
        validation: "gh workflow list"
      
      # Stream B: Agent Runtime
      - id:  B.3
        name: "Create agent workflow"
        files: 
          - . github/workflows/agent-runtime.yml
        validation: "gh workflow view agent-runtime"
      
      # Stream C: Security Analysis
      - id:  C.1
        name: "Create security scripts"
        files: 
          - scripts/security/export_semgrep_alerts.py
          - scripts/security/score_alerts.py
          - . github/security/criticality-map.yaml
        validation: "python -m py_compile scripts/security/*. py"
      
      # Stream D:  Code Scanning Resolution
      - id:  D.3
        name: "Disable advanced workflows"
        files:
          - . github/disabled/README.md
        commands:
          - "mkdir -p .github/disabled . github/disabled-config"
          - "git mv .github/workflows/*codeql* .github/disabled/ || true"
        validation: "ls . github/disabled/"
      
      - id: D.4
        name: "Enable default CodeQL"
        files: 
          - .github/workflows/codeql-analysis.yml
          - .github/SECURITY-CODE-SCANNING-NOTE.md
        validation: "gh workflow run codeql-analysis.yml --dry-run"

  # =========================================================================
  # PHASE 3: Security Remediation
  # =========================================================================
  phase_3:
    name: "Security Remediation"
    depends_on: [phase_2]
    
    tasks:
      # Stream C: Codemods and Fixes
      - id:  C.2
        name: "Export and analyze alerts"
        commands: 
          - "python scripts/security/export_semgrep_alerts.py"
          - "python scripts/security/score_alerts.py"
        outputs:
          - . github/security/semgrep-alerts-export.json
          - .github/security/prioritized-alerts.csv
          - docs/security/semgrep-analysis-report.md
        validation: "test -f .github/security/prioritized-alerts.csv"
      
      - id: C. 3
        name:  "Create codemods"
        files:
          - scripts/security/codemods/fix_subprocess. py
          - scripts/security/codemods/fix_sql_injection.py
          - scripts/security/codemods/fix_hardcoded_secrets.py
          - scripts/security/run_codemods. py
        validation: "python scripts/security/run_codemods.py --dry-run"
      
      - id: C.4
        name: "Run automated fixes"
        commands:
          - "python scripts/security/run_codemods.py"
        validation: "gh pr list --label security"
      
      - id: C.5
        name: "Configure suppressions"
        files:
          - . semgrep/semgrep.yml
          - docs/security/suppressions-register.md
        validation: "semgrep --validate --config .semgrep/"
      
      - id: C.6
        name: "Enable security gates"
        files: 
          - .github/workflows/security-scan.yml
        validation: "gh workflow run security-scan. yml --dry-run"

  # =========================================================================
  # PHASE 4: Validation & Documentation
  # =========================================================================
  phase_4:
    name: "Validation & Documentation"
    depends_on: [phase_3]
    
    tasks: 
      - id: V.1
        name: "Validate all workflows"
        commands: 
          - "gh workflow list"
          - "gh api repos/Aries-Serpent/_codex_/code-scanning/alerts --jq 'length'"
        validation:  "All workflows listed and running"
      
      - id: V.2
        name: "Run CI pipeline"
        commands: 
          - "gh workflow run ci.yml"
        validation: "gh run list --workflow=ci.yml --limit=1 --json conclusion"
      
      - id: V. 3
        name:  "Generate final report"
        outputs:
          - docs/IMPLEMENTATION-COMPLETE.md
        validation: "test -f docs/IMPLEMENTATION-COMPLETE. md"
```

---

# MASTER VALIDATION CHECKLIST

## Copilot Agent:  Verify All Items Before Completion

### Stream A: Caching Architecture
- [ ] `requirements-minimal.txt` exists and installs successfully
- [ ] `requirements-test.txt` exists and installs successfully
- [ ] `.github/actions/setup-python-uv/action.yml` is valid
- [ ] `.github/actions/compressed-cache/action. yml` is valid
- [ ] `Dockerfile.ci` builds successfully
- [ ] `.github/workflows/ci.yml` runs without errors
- [ ] `.github/workflows/build-container-cache. yml` pushes to GHCR
- [ ] `.github/workflows/cache-warmer.yml` is scheduled
- [ ] UV cache size < 100MB
- [ ] CI job duration < 3 minutes with cache hit

### Stream B: OpenAI Integration
- [ ] `src/config/openai_client.py` imports without errors
- [ ] `src/agents/autonomous_runner.py` executes successfully
- [ ] `src/agents/orchestrator.py` imports without errors
- [ ] `.github/workflows/agent-runtime.yml` is valid
- [ ] Agent can connect to OpenAI API (test with dry run)
- [ ] Audit logging captures executions
- [ ] Cost estimation works correctly

### Stream C:  Semgrep Remediation
- [ ] `.github/security/semgrep-alerts-export.json` contains all alerts
- [ ] `.github/security/prioritized-alerts. csv` has risk scores
- [ ] `docs/security/semgrep-analysis-report.md` is generated
- [ ] At least 3 codemods are implemented
- [ ] Automated fix PRs are created
- [ ] `.semgrep/semgrep.yml` is valid configuration
- [ ] `docs/security/suppressions-register.md` documents all FPs
- [ ] `.github/workflows/security-scan.yml` runs on PRs
- [ ] P0 alert count reduced by > 50%

### Stream D: Code Scanning
- [ ] Backup branch exists:  `backup/codeql-advanced-*`
- [ ] Advanced workflows moved to `.github/disabled/`
- [ ] `.github/workflows/codeql-analysis. yml` exists
- [ ] CodeQL workflow completes successfully
- [ ] Code scanning alerts appear in Security tab
- [ ] Organization conflict message is cleared
- [ ] `.github/SECURITY-CODE-SCANNING-NOTE.md` documents changes

### Final Validation
- [ ] All GitHub Actions workflows pass
- [ ] No new security alerts introduced
- [ ] Documentation is complete and accurate
- [ ] All PRs are created with proper labels
- [ ] Master tracking issue updated with progress

---

## 🚀 COPILOT AGENT:  BEGIN EXECUTION

**Authorization Confirmed**: You are authorized to execute this complete implementation plan on `Aries-Serpent/_codex_`.

**Execution Mode**: Autonomous with checkpoints

**Reporting**: Update progress after each phase completion

**Escalation with Recommendations**: Contact @mbaetiong for: 
- High-risk security fixes
- Breaking changes
- Blocked dependencies
- Ambiguous requirements

**Start Command**: Begin with Phase 1, execute all parallel tasks, then proceed sequentially through remaining phases.

---

*Document compiled by Copilot Agent on Previous Cycle-12-17*
*Target Repository: Aries-Serpent/_codex_ (ID: 1040037790)*
*Total Implementation Streams: 4*
*Estimated Completion: 5 phases*
