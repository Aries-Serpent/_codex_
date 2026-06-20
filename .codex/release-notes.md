# Release 0.1.0

**Date:** 2026-06-20

## Executive Summary

This release is based on the Phase 7D campaign completion:
- ✅ Phase Status: SUBSTANTIALLY COMPLETE
- 📦 Docker Builds: 5/8 successful
- 📋 SBOM Files: 5 generated and included

## 📦 Assets

This release includes the following assets:
- `sbom-*.json` - Software Bill of Materials in CycloneDX format
- `sbom-*.txt` - SBOM in text format
- `attestations.json` - Build attestations
- `provenance.json` - Software provenance record
- `release-audit.json` - Release audit trail

## ✅ Verification

To verify the integrity of this release:

```bash
# Verify SBOM
python scripts/deployment/validate_sbom_completeness.py sbom-*.json

# Verify attestations
python scripts/deployment/verify_release_audit.py release-audit.json
```

## 📥 Installation

### Python Package
```bash
pip install -U codex-ml
```

### Docker
```bash
docker pull ghcr.io/aries-serpent/_codex_:0.1.0
```

## 🔄 Upgrade Guide

For upgrading from previous versions, see [UPGRADE.md](UPGRADE.md) for detailed instructions.

## 📝 Known Issues

- Docker GPU variant requires CUDA 12.x compatibility
- See GitHub Issues for complete list of known issues

---

**Thank you** to all contributors and testers who made this release possible!
