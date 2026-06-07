# Gap 26 Evidence — Container Scanning with Trivy

## Status: ✅ Implemented

## Workflow Created
- **File**: `.github/workflows/container-scan.yml`

## Scanner
- **Tool**: Trivy via `aquasecurity/trivy-action@0.20.0`

## Scan Scope
- Severity: `CRITICAL,HIGH` CVEs
- Output: SARIF → uploaded to GitHub Security tab via `github/codeql-action/upload-sarif@v3`
- Artifacts retained for 30 days

## Matrix
- `Dockerfile`
- `docker/Dockerfile.cpu`
- `docker/Dockerfile.gpu`

## Triggers
- Push/PR on `Dockerfile*` or `docker/**` changes
- Weekly schedule: Monday 05:00 UTC (`0 5 * * 1`)
- Manual `workflow_dispatch`

## Permissions
- `contents: read`
- `security-events: write`
