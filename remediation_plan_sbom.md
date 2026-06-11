# remediation_plan_sbom.md

- Generated: 2026-06-05T05:16:00Z
- Source artifacts: `security-suite-sbom/sbom.json`, `security-suite-sbom/sbom-metadata.json`

## Executive Summary

- SBOM format/spec: **CycloneDX 1.6**
- Components enumerated: **338**
- Repository/commit: `Aries-Serpent/_codex_` @ `4086f9afdb98d9fd58ed123220f337a4caae94f0`

## Supply Chain Risk Assessment

- High-risk dependency indicators from scanner artifacts:
  - `diskcache==5.6.3` (CVE-2025-69872, no patched release)
  - `sqlitedict==2.1.0` (CVE-2024-35515, no patched release)
- Action: keep these dependencies isolated from untrusted writable paths and monitor upstream releases.
- Action: enforce periodic re-scan cadence (daily CI + release gates) with SBOM diffing per commit.

## License Snapshot (Top 20)

| License | Components |
|---|---:|
| `MIT` | 132 |
| `Apache-2.0` | 45 |
| `License :: OSI Approved :: BSD License` | 42 |
| `License :: OSI Approved :: Apache Software License` | 42 |
| `BSD-3-Clause` | 37 |
| `UNKNOWN` | 13 |
| `License :: Other/Proprietary License` | 9 |
| `LicenseRef-NVIDIA-Proprietary` | 5 |
| `BSD-2-Clause` | 4 |
| `Python-2.0` | 4 |
| `PSF-2.0` | 3 |
| `MPL-2.0` | 3 |
| `License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)` | 3 |
| `ISC` | 2 |
| `LGPL-2.1-or-later` | 1 |
| `License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)` | 1 |
| `LicenseRef-NVIDIA-SOFTWARE-LICENSE` | 1 |
| `GPL-2.0-only` | 1 |
| `MIT-CMU` | 1 |
| `GPL-2.0-or-later` | 1 |

## Remediation Actions

1. Add a recurring CVE triage workflow for components with no available upstream fixes.
2. Add policy checks that flag newly introduced packages lacking license metadata.
3. Add SBOM drift check in PR gate (`base` vs `head` component delta) for dependency-change PRs.
