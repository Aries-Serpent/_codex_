# Release Alert Policy for cognitive_brain

**Version**: 1.0  
**Effective**: 2026-07-07  
**Authority**: Packaging Validation Agent (S172)  
**Purpose**: Define alert thresholds and anomaly detection for release artifacts

---

## OVERVIEW

This policy establishes alert thresholds for monitoring release quality and detecting anomalies. The CI/CD pipeline automatically enforces these thresholds and fails releases that violate them without explicit explanation.

---

## ALERT CATEGORIES & THRESHOLDS

### 1. Wheel Size Anomalies

**Metric**: Wheel size increase compared to previous release

**Threshold**: > 10% increase without explanation

**Triggers**:
- `cognitive_brain-0.1.0-core.whl`: Expected ~45MB, Alert if > 49.5MB
- `cognitive_brain-0.1.0-runtime.whl`: Expected ~150MB, Alert if > 165MB
- `cognitive_brain-0.1.0-full.whl`: Expected ~250MB, Alert if > 275MB

**Acceptable Explanations**:
- Addition of pre-trained model weights
- New ML framework dependency
- Expanded feature set documentation
- Updated binary dependencies

**Examples**:
- ✅ Size increase from 250MB → 260MB (+4%) = NO ALERT
- ⚠️ Size increase from 250MB → 285MB (+14%) = ALERT (requires explanation)
- ⛔ Size increase from 250MB → 290MB (+16%) without explanation = RELEASE BLOCKED

### 2. Build Time Anomalies

**Metric**: Build duration compared to baseline

**Baseline**: 120 seconds (target build time)

**Threshold**: > 15% increase (138 seconds)

**Alerts**:
- 120s - 138s (+0 to +15%): ✅ OK
- 138s - 180s (+15% to +50%): ⚠️ WARNING (investigate)
- > 180s (+50%): ⛔ ALERT (requires review)

**Acceptable Explanations**:
- New compilation step (Cython, Rust extensions)
- Test suite addition
- CI infrastructure limitation (shared runners)
- First build of new profile

**Examples**:
- ✅ Build time: 100s → 110s (+10%) = OK
- ⚠️ Build time: 100s → 130s (+30%) = WARNING
- ⛔ Build time: 100s → 160s (+60%) = BLOCKED

### 3. Dependency Addition/Removal

**Metric**: New packages or removed packages in uv.lock

**Threshold**: 
- **New packages**: > 5 new major dependencies without justification
- **Removed packages**: > 3 critical dependencies without notification

**Alerts**:
- 1-2 new packages: ✅ OK (normal updates)
- 3-5 new packages: ⚠️ WARNING (review required)
- > 5 new packages: ⛔ ALERT (requires documentation)

**Acceptable Explanations**:
- Upgrading ML framework (pytorch, transformers)
- Adding optional feature support
- Replacing deprecated dependency
- Removing dead code/unused dependencies

**Examples**:
- ✅ Add: dataclasses-json, remove: typing-extensions = OK (refactoring)
- ⚠️ Add: 4 new testing frameworks = WARNING (needs review)
- ⛔ Add: 8 new dependencies without CHANGELOG update = BLOCKED

### 4. License Compliance Changes

**Metric**: New licenses or license conflicts introduced

**Threshold**: Any Tier 3 (GPL/AGPL/SSPL) introduction = IMMEDIATE BLOCK

**Alerts**:
- **Tier 3 License (GPL/AGPL/SSPL)**: ⛔ INSTANT BLOCK
- **License change on existing package**: ⚠️ WARNING
- **New proprietary license**: ⛔ BLOCK (requires exception)

**Acceptable Explanations**:
- License upgrade (MIT → Apache 2.0): OK
- License downgrade (Apache 2.0 → MIT): ⚠️ Review required
- License change with restrictions: ⛔ Requires legal review

**Examples**:
- ✅ numpy license stays BSD-3-Clause = OK
- ⚠️ transformers: Apache-2.0 → MIT = Review
- ⛔ torch: BSD → GPL = BLOCKED

### 5. SBOM & Signature Anomalies

**Metric**: SBOM generation or signature validation failures

**Threshold**: Any failure = IMMEDIATE BLOCK

**Alerts**:
- Missing SBOM files: ⛔ BLOCK
- Signature validation failure: ⛔ BLOCK (possible tampering)
- Component mismatch (XML vs JSON): ⚠️ WARNING
- Incomplete license information: ⚠️ WARNING

**Examples**:
- ✅ All 3 SBOMs generated with valid signatures = OK
- ⛔ Core profile SBOM missing = BLOCKED
- ⛔ Signature mismatch = BLOCKED (possible tampering)

---

## CI GATE IMPLEMENTATION

### Environment Variables

```bash
# Size thresholds
WHEEL_SIZE_THRESHOLD_PERCENT=10
WHEEL_CORE_SIZE_MB=45
WHEEL_RUNTIME_SIZE_MB=150
WHEEL_FULL_SIZE_MB=250

# Build time thresholds
BUILD_TIME_BASELINE_SECONDS=120
BUILD_TIME_THRESHOLD_PERCENT=15

# Dependency thresholds
NEW_DEPS_ALERT_COUNT=5
REMOVED_DEPS_ALERT_COUNT=3

# License thresholds
FORBIDDEN_LICENSES=["GPL-2.0", "GPL-3.0", "AGPL-3.0", "SSPL-1.0"]
```

### Gate Script

```bash
#!/bin/bash
# scripts/ci/check_release_thresholds.sh

set -e

CURRENT_WHEEL_SIZE=$(stat -c%s dist/cognitive_brain-0.1.0-full.whl)
EXPECTED_WHEEL_SIZE=$((250 * 1024 * 1024))  # 250MB
THRESHOLD=$((EXPECTED_WHEEL_SIZE * 110 / 100))  # 10% increase

if [ "${CURRENT_WHEEL_SIZE}" -gt "${THRESHOLD}" ]; then
    echo "❌ Wheel size anomaly detected!"
    echo "   Current: $((CURRENT_WHEEL_SIZE / 1024 / 1024))MB"
    echo "   Threshold: $((THRESHOLD / 1024 / 1024))MB"
    echo "   Increase: $(((CURRENT_WHEEL_SIZE - EXPECTED_WHEEL_SIZE) * 100 / EXPECTED_WHEEL_SIZE))%"
    exit 1
fi

echo "✓ Wheel size check passed"
```

---

## ALERT RESOLUTION PROCESS

### 1. Alert Triggered
```
CI gate detects anomaly (e.g., wheel size +15%)
↓
PR check shows FAILED
↓
Error message specifies threshold and current value
```

### 2. Investigation Required
Submitter must:
1. Identify root cause
2. Document explanation in PR
3. Get approval from maintainer
4. Add explanation to CHANGELOG.md

### 3. Documented Exception
```markdown
## v0.1.0 Release Notes

### Known Changes
- **Wheel size increase (+14%)**
  - Reason: Added pytorch binary wheels for GPU support
  - Size impact: core +0%, runtime +8%, full +14%
  - Approved by: @maintainer (2026-07-07)
```

### 4. Re-run CI
Once explanation is documented, re-run CI with:
```bash
git commit --amend -m "Release notes updated with threshold explanations"
git push -f
```

---

## DASHBOARD & MONITORING

### Release Metrics Tracking

**Location**: `.codex/metrics/release-*.json`

**Automatic Tracking**:
- Wheel sizes (all 3 profiles)
- Build duration
- Package count delta
- License changes
- SBOM validation result

### Historical Baseline

**File**: `.codex/RELEASE_BASELINE.json`

```json
{
  "v0.0.1": {
    "date": "2026-01-01",
    "build_duration_seconds": 120,
    "wheel_core_size_mb": 45,
    "wheel_runtime_size_mb": 148,
    "wheel_full_size_mb": 248,
    "package_count": 347,
    "licenses": {
      "MIT": 210,
      "Apache-2.0": 85,
      "BSD": 52
    }
  },
  "v0.1.0": {
    "date": "2026-07-07",
    "build_duration_seconds": 115,
    "wheel_core_size_mb": 45,
    "wheel_runtime_size_mb": 150,
    "wheel_full_size_mb": 250,
    "package_count": 349,
    "licenses": {
      "MIT": 212,
      "Apache-2.0": 85,
      "BSD": 52
    }
  }
}
```

---

## EXCEPTION APPROVAL

For threshold violations requiring exception:

1. **PR Comment**: 
   ```
   @release-gates override=true reason="Adding pytorch GPU support"
   ```

2. **Approval**: Requires sign-off from:
   - Release manager (@maintainer)
   - Technical lead (@tech-lead)

3. **Audit Log**: Exception recorded in:
   - `RELEASE_EXCEPTIONS.md`
   - Metrics JSON (`approved_by`, `reason`)

---

## AUTOMATION & ENFORCEMENT

### On Every PR with Changes to uv.lock
```yaml
jobs:
  check-thresholds:
    runs-on: ubuntu-latest
    steps:
      - run: python scripts/ci/check_release_thresholds.sh
        if: |
          contains(github.event.pull_request.changed_files, 'uv.lock') ||
          contains(github.event.pull_request.changed_files, 'pyproject.toml')
```

### On Release Tag Push
```yaml
jobs:
  validate-release:
    runs-on: ubuntu-latest
    steps:
      - run: |
          python scripts/ci/check_release_thresholds.sh
          python scripts/ci/validate_sbom.sh
          python scripts/ci/validate_licenses.sh
```

---

## EXCEPTIONS REGISTER

| Version | Threshold | Value | Reason | Approved By | Date |
|---------|-----------|-------|--------|------------|------|
| v0.1.0 | None | N/A | No exceptions approved | N/A | N/A |

---

## POLICY REVIEW

**Last Updated**: 2026-07-07  
**Next Review**: 2026-08-07  
**Review Frequency**: Quarterly  
**Owner**: Packaging Validation Agent (S172)

---

## APPENDIX: THRESHOLD CALCULATION

### Wheel Size Formula
```
Current Size = 250 MB
Alert Threshold = Current Size × (1 + 10/100) = 275 MB
```

### Build Time Formula
```
Baseline = 120 seconds
Alert Threshold = Baseline × (1 + 15/100) = 138 seconds
```

### Dependency Delta
```
New Packages Alert = > 5
Removed Packages Alert = > 3
```

