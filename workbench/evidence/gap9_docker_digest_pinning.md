# Gap 9: Docker Base Image Digest Pinning

**Status:** ✅ Completed  
**Priority:** P1 Medium  
**Date resolved:** 2025-07-18  
**Commit:** `build(gap9): pin Docker base images to SHA256 digests`

---

## Summary

All Docker base images across the repository have been pinned to specific
SHA256 manifest-list digests.  Pinning prevents silent image drift — where a
tag like `python:3.12-slim` resolves to a different layer set after a Docker
Hub push — and ensures fully reproducible builds.

---

## Digests resolved (via `skopeo inspect`)

| Image reference | Pinned digest |
|---|---|
| `python:3.12-slim` | `sha256:090ba77e2958f6af52a5341f788b50b032dd4ca28377d2893dcf1ecbdfdfe203` |
| `python:3.12.3-slim` | `sha256:afc139a0a640942491ec481ad8dda10f2c5b753f5c969393b12480155fe15a63` |
| `python:3.10-slim` | `sha256:70f65c721aaddfb22b20ed6ec12606c59d9592493c5fcb6639f3d0e8ba3fbc10` |
| `python:3.14-slim` | `sha256:c845af9399020c7e562969a13689e929074a10fd057acd1b1fad06a2fb068e97` |
| `nvidia/cuda:13.3.0-runtime-ubuntu22.04` | `sha256:aa89ba5b690e634093fee3bec549bf3f42a67a11616fc0541b582dbebd03a5b5` |
| `nvidia/cuda:12.2.2-cudnn8-runtime-ubuntu22.04` | `sha256:2d913b09e6be8387e1a10976933642c73c840c0b735f0bf3c28d97fc9bc422e0` |

---

## Dockerfiles updated

### `Dockerfile`

| Line | Original | Pinned |
|---|---|---|
| 6 | `FROM python:3.12-slim AS base` | `FROM python:3.12-slim@sha256:090ba77...e203 AS base` |
| 59 | `FROM nvidia/cuda:13.3.0-runtime-ubuntu22.04 AS gpu-runtime` | `FROM nvidia/cuda:13.3.0-runtime-ubuntu22.04@sha256:aa89ba5b...5b5 AS gpu-runtime` |
| 110 | `FROM python:3.12-slim AS test` | `FROM python:3.12-slim@sha256:090ba77...e203 AS test` |

Stage refs (`FROM base AS cpu-runtime`) are internal references — no pinning needed.

---

### `Dockerfile.preview`

| Line | Original | Pinned |
|---|---|---|
| 51 | `FROM python:3.12-slim AS preview-base` | `FROM python:3.12-slim@sha256:090ba77...e203 AS preview-base` |
| 100 | `FROM python:3.12-slim AS preview` | `FROM python:3.12-slim@sha256:090ba77...e203 AS preview` |

Stage ref `FROM preview AS preview-dev` unchanged.

---

### `Dockerfile.restore`

| Line | Original | Pinned |
|---|---|---|
| 2 | `FROM python:3.12-slim` | `FROM python:3.12-slim@sha256:090ba77...e203` |

---

### `.github/agents/ci-testing-agent/Dockerfile`

| Line | Original | Pinned |
|---|---|---|
| 3 | `FROM python:3.12.3-slim` | `FROM python:3.12.3-slim@sha256:afc139a0...a63` |

---

### `.github/agents/security-scan-agent/Dockerfile`

| Line | Original | Pinned |
|---|---|---|
| 2 | `FROM python:3.12-slim` | `FROM python:3.12-slim@sha256:090ba77...e203` |

---

### `docker/Dockerfile.ci`

| Line | Original | Pinned |
|---|---|---|
| 10 | `FROM python:3.14-slim as base` | `FROM python:3.14-slim@sha256:c845af93...e97 as base` |

Stage refs `FROM base as minimal`, `FROM minimal as test`, etc. unchanged.

---

### `docker/Dockerfile.cpu`

| Line | Original | Pinned |
|---|---|---|
| 2 | `FROM python:3.10-slim` | `FROM python:3.10-slim@sha256:70f65c72...c10` |

---

### `docker/Dockerfile.embedding`

| Line | Original | Pinned |
|---|---|---|
| 3 | `FROM python:3.14-slim` | `FROM python:3.14-slim@sha256:c845af93...e97` |

---

### `docker/Dockerfile.gpu`

| Line | Original | Pinned |
|---|---|---|
| 16 | `FROM python:3.14-slim AS builder` | `FROM python:3.14-slim@sha256:c845af93...e97 AS builder` |
| 50 | `FROM nvidia/cuda:12.2.2-cudnn8-runtime-ubuntu22.04 AS runtime` | `FROM nvidia/cuda:12.2.2-cudnn8-runtime-ubuntu22.04@sha256:2d913b09...e0 AS runtime` |

---

### `docker/Dockerfile.local`

| Line | Original | Pinned |
|---|---|---|
| 4 | `FROM python@sha256:<PINNED_DIGEST>` *(placeholder)* | `FROM python:3.12-slim@sha256:090ba77...e203` |

The file previously had a manual placeholder comment referencing `python:3.11-slim`.
Updated to `python:3.12-slim` to match the project's minimum Python 3.12 requirement.

---

### `docker/Dockerfile.local-codex-env`

| Line | Original | Pinned |
|---|---|---|
| 4 | `FROM python:3.14-slim` | `FROM python:3.14-slim@sha256:c845af93...e97` |

---

### `docker/Dockerfile.optimized`

| Line | Original | Pinned |
|---|---|---|
| 6 | `FROM python:3.12-slim as builder` | `FROM python:3.12-slim@sha256:090ba77...e203 as builder` |
| 34 | `FROM python:3.12-slim` | `FROM python:3.12-slim@sha256:090ba77...e203` |

---

## Re-pinning script

A maintenance script was created at **`scripts/docker/pin_digests.sh`**.

```bash
# Dry-run (prints new FROM lines without modifying files)
bash scripts/docker/pin_digests.sh --dry-run

# Actually update all Dockerfiles
bash scripts/docker/pin_digests.sh
```

The script uses `skopeo inspect` to resolve the current manifest-list digest
for each base image and applies the update in-place using Python (portable
across Linux and macOS).

---

## When to re-pin

1. **Routine security updates** — Python Docker Hub pushes security patches
   to the same tag (e.g. `python:3.12-slim`) without changing the tag name.
   Run the script periodically (e.g. monthly) or after any CVE advisory.

2. **After a deliberate version upgrade** — When intentionally bumping
   `python:3.12-slim` → `python:3.13-slim`, update the image tag in
   `scripts/docker/pin_digests.sh`'s `IMAGE_FILES` table, run the script,
   and commit.

3. **Automated re-pinning (Renovate / Dependabot)** — Add a
   `docker` datasource entry in `renovate.json` or `.github/dependabot.yml`
   to have the platform propose digest-bump PRs automatically.

---

## Approach

1. Used `skopeo inspect docker://<image>:<tag>` (available in the CI
   sandbox — version 1.13.3) to fetch the manifest-list digest without
   pulling the full image layers.
2. For each external `FROM` line, prepended a human-readable comment
   `# FROM image:tag (pinned below)` and appended `@sha256:<digest>` to the
   `FROM` line itself.
3. Internal stage references (`FROM <stage-name> AS <alias>`) were left
   unchanged — they are not registry references.
4. The `docker/Dockerfile.local` placeholder (`FROM python@sha256:<PINNED_DIGEST>`)
   was resolved to the current `python:3.12-slim` digest and the outdated
   comment referencing `python:3.11-slim` was updated.
