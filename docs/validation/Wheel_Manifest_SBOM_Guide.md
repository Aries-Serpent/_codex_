# Wheel Manifest & Baseline Management

## Overview

The wheel manifest system provides cryptographic verification of Python dependencies to ensure reproducible builds and detect supply chain drift.

## Components

### 1. Manifest Generation Script

**Location**: `scripts/ci/generate_wheel_manifest.py`

**Purpose**: Creates a JSON manifest with SHA256 hashes for all wheels in a wheelhouse directory.

**Usage**:
```bash
python scripts/ci/generate_wheel_manifest.py \
  --wheelhouse /path/to/wheels \
  --output manifest.json \
  --platform linux/amd64 \
  --python-version 3.11
```

**Output Format**:
```json
{
  "count": 42,
  "platform": "linux/amd64",
  "python_version": "3.11",
  "wheels": [
    {
      "name": "package-1.0.0-py3-none-any.whl",
      "sha256": "abc123...",
      "size": 123456
    }
  ]
}
```

### 2. CI Integration

**Workflow**: `.github/workflows/container-build.yml`

The `build-wheels` job automatically:
1. Builds the Docker builder stage to generate wheels
2. Extracts the wheelhouse from the build
3. Generates a manifest with hashes
4. Uploads both wheels and manifest as artifacts

**Artifacts**:
- `wheelhouse-linux-amd64`: Wheels + manifest for amd64
- `wheelhouse-linux-arm64`: Wheels + manifest for arm64 (if `ALLOW_MULTIARCH=true`)

### 3. Scheduled Audit

**Workflow**: `.github/workflows/scheduled-dependency-audit.yml`

**Schedule**: Weekly on Mondays at 00:00 UTC

**Capabilities**:
- Regenerate baseline wheelhouse
- Compare manifests (drift detection)
- Generate SBOM for CPU and GPU images
- Scan for vulnerabilities with Grype
- Test Python version compatibility (3.11, 3.12, 3.13)
- Auto-create GitHub issues on drift

**Manual Trigger**:
```bash
gh workflow run scheduled-dependency-audit.yml \
  -f python_version=3.12 \
  -f enable_multiarch=true
```

## Drift Detection

### What is Drift?

Dependency drift occurs when:
- An upstream package publishes a new version
- A transitive dependency changes
- Wheel hashes change even with same version (rebuild)

### Detection Process

1. Weekly audit regenerates current baseline
2. Compare with previous baseline manifest
3. If SHA256 hashes differ: alert via GitHub issue
4. Manual review required to:
   - Verify changes are expected
   - Test compatibility
   - Update pinned versions if needed

### Manual Comparison

```bash
# Download artifacts from two workflow runs
gh run download <run-id-old> -n baseline-wheelhouse-linux-amd64 -D old/
gh run download <run-id-new> -n baseline-wheelhouse-linux-amd64 -D new/

# Compare manifests
diff old/manifest-linux-amd64.json new/manifest-linux-amd64.json
```

## SBOM Integration

### Generation

SBOMs are generated using [Syft](https://github.com/anchore/syft) from Anchore:

```bash
# From Docker image
syft codex-ml:cpu-latest -o spdx-json=sbom.json

# From directory
syft dir:./wheelhouse -o cyclonedx-json=sbom.json
```

### Scanning

Vulnerability scanning uses [Grype](https://github.com/anchore/grype):

```bash
# Scan image
grype codex-ml:cpu-latest --output sarif --file results.sarif

# Scan SBOM
grype sbom:sbom.json --fail-on critical
```

### GitHub Security Integration

- SARIF files automatically uploaded to GitHub Security tab
- Alerts appear in Security > Code scanning alerts
- Integrate with Dependabot for automated PRs

## Upgrade Workflows

### Testing New Python Version

1. Trigger scheduled audit with target version:
   ```bash
   gh workflow run scheduled-dependency-audit.yml -f python_version=3.12
   ```

2. Review upgrade-compatibility job results

3. If successful, update Dockerfiles and pin Python version

### Enabling Multi-Arch

1. Test with audit workflow:
   ```bash
   gh workflow run scheduled-dependency-audit.yml -f enable_multiarch=true
   ```

2. Verify arm64 wheelhouse artifact contains all required wheels

3. Set repository variable `ALLOW_MULTIARCH=true`

4. Future builds will include arm64

### Responding to Drift Alert

1. Review GitHub issue created by drift-detection job

2. Download current and previous manifests

3. Identify changed wheels:
   ```bash
   jq -r '.wheels[].name' old/manifest.json > old-wheels.txt
   jq -r '.wheels[].name' new/manifest.json > new-wheels.txt
   diff old-wheels.txt new-wheels.txt
   ```

4. Check for hash changes:
   ```bash
   jq '.wheels[] | "\(.name) \(.sha256)"' old/manifest.json > old-hashes.txt
   jq '.wheels[] | "\(.name) \(.sha256)"' new/manifest.json > new-hashes.txt
   diff old-hashes.txt new-hashes.txt
   ```

5. Review changelog for changed packages

6. Test locally, update pins if needed, close issue

## Best Practices

### Pinning Strategy

**requirements/docker.txt**:
```
# Pin exact versions for reproducibility
ray==2.9.3
numpy==1.24.3

# Or use hash-pinning (pip-compile style)
ray==2.9.3 \
    --hash=sha256:abc123...
```

### Baseline Storage

For production systems, consider:
- Store baseline manifests in repository (`baselines/manifest-YYYY-MM-DD.json`)
- Use Git tags to mark stable baselines
- Archive artifacts to S3/blob storage for long-term retention

### Security Scanning

- Review Grype alerts weekly
- Critical vulnerabilities → immediate action
- High vulnerabilities → scheduled update
- Medium/Low → batch with regular updates

### Testing Changes

Before merging dependency updates:
1. Local build test
2. PR triggers SBOM scan
3. Review security alerts
4. Merge if clean or exceptions documented

## Troubleshooting

### Manifest Generation Fails

**Symptom**: Script exits with error or empty manifest

**Solutions**:
- Verify wheelhouse path exists: `ls -la /path/to/wheels`
- Check wheel files present: `ls -la /path/to/wheels/*.whl`
- Ensure Python interpreter matches expected version

### Drift False Positive

**Symptom**: Drift detected but no actual package changes

**Cause**: Wheel rebuild with different timestamp/metadata

**Solution**:
- Compare wheel contents: `unzip -l old.whl > old.txt && unzip -l new.whl > new.txt`
- If only timestamps differ, update baseline and close alert

### SBOM Missing Dependencies

**Symptom**: SBOM doesn't list all expected packages

**Cause**: Syft scans runtime image, not builder stage

**Solution**:
- Generate SBOM from wheelhouse: `syft dir:./wheelhouse`
- Or scan builder stage: `syft codex-ml:builder`

## References

- [Syft Documentation](https://github.com/anchore/syft)
- [Grype Documentation](https://github.com/anchore/grype)
- [SPDX Specification](https://spdx.dev/)
- [CycloneDX Specification](https://cyclonedx.org/)
- [SARIF Format](https://sarifweb.azurewebsites.net/)
