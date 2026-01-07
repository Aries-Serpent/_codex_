# ADR-2025-11-02: Archive Sigstore Keyless Signing Integration

**Date**: 2025-11-02  
**Status**: Accepted (Phase 2)  
**Author**: Archive Standardization Team  
**Stakeholders**: Architecture Team, Security Team, Operations  

## Problem Statement

The _codex_ archive system currently lacks cryptographic signatures on evidence records, preventing compliance with SLSA L3 requirements and limiting supply chain integrity verification capabilities.

## Requirements

- ✅ Achieve SLSA L3 cryptographic identity binding
- ✅ Enable tamper-evident audit trails
- ✅ Support GitHub Actions native OIDC integration
- ✅ Maintain backward compatibility with v1 records
- ✅ Minimize operational overhead (no key management)
- ✅ Support production deployment immediately

## Decision

Integrate **Sigstore keyless signing** using GitHub OIDC tokens for cryptographic identity binding of archive evidence records.

### Implementation Details

| Aspect | Choice | Rationale |
|--------|--------|-----------|
| **Technology** | Sigstore (cosign + Fulcio + Rekor) | SLSA L3 compatible, zero key management |
| **Identity Provider** | GitHub OIDC tokens | Native to GitHub Actions, no additional auth needed |
| **Storage** | Evidence record `standardizationMetadata.signature` | Immutable, versioned storage |
| **Transparency** | Rekor public transparency log | Auditable, externally verifiable |
| **Fallback** | Graceful degradation if unavailable | Signing optional to preserve continuity |

## Consequences

### Positive

✅ **SLSA L3 Compliance**: Evidence records cryptographically signed with actor identity  
✅ **Zero Key Management**: Ephemeral certificates issued by Fulcio, no long-lived secrets  
✅ **Auditability**: All signatures logged publicly in Rekor transparency log  
✅ **GitHub Native**: Works seamlessly with GitHub Actions without additional setup  
✅ **Backward Compatible**: Existing v1 records unaffected, optional for v2  
✅ **Production Ready**: Sigstore GA ensures stability and support  

### Negative

⚠️ **External Dependency**: Relies on Sigstore infrastructure (Fulcio, Rekor)  
⚠️ **Signature Performance**: ~5-10% overhead per archive operation  
⚠️ **Online Verification**: Signature verification requires Rekor access  
⚠️ **Team Learning Curve**: Training needed on Sigstore concepts  

### Mitigation

| Risk | Mitigation |
|------|-----------|
| External dependency unavailability | Graceful fallback: `CODEX_ENABLE_SIGNING=false` allows continuity |
| Performance degradation | Benchmark operations; optimize if needed; sign asynchronously if necessary |
| Verification dependency | Document offline verification limitations; consider caching Rekor data |
| Team learning curve | Provide runbooks, ADR documentation, training materials |

## Alternatives Considered

### Alternative 1: Traditional GPG Signing
- ❌ Requires key management, rotation, storage
- ❌ Not SLSA L3 compatible
- ❌ Doesn't integrate with GitHub Actions
- ✅ Familiar to team

### Alternative 2: TUF (The Update Framework)
- ✅ Supply chain security framework
- ❌ Heavier than needed for evidence signing
- ❌ Requires separate infrastructure

### Alternative 3: No Signing (Defer to Phase 3)
- ✅ Faster Phase 2 delivery
- ❌ Delays SLSA L3 achievement
- ❌ Evidence records remain unsigned, audit trail incomplete

## Decision Rationale

**Sigstore keyless signing** selected because it:
1. Achieves SLSA L3 immediately
2. Requires no operational key management
3. Integrates natively with GitHub Actions
4. Provides public transparency via Rekor
5. Maintains backward compatibility

## Implementation Plan

1. **Phase 2a**: Create `SignstoreClient` class (2 weeks)
2. **Phase 2b**: Integrate into `archive store()` (1 week)
3. **Phase 2c**: Create verification tooling (1 week)
4. **Phase 2d**: Documentation + training (1 week)
5. **Phase 2e**: Testing + deployment (1 week)

## Configuration

### Environment Variables

```bash
# Enable signing (default: false for backward compatibility)
export CODEX_ENABLE_SIGNING=true

# GitHub OIDC token (auto-provided in GitHub Actions)
export SIGSTORE_ID_TOKEN=$(gh auth token)
```text

### GitHub Actions Integration

```yaml
permissions:
  id-token: write  # ← REQUIRED for OIDC token
  contents: read

steps:
  - name: Archive with standardization
    env:
      CODEX_ENABLE_SIGNING: "true"
    run: python -m codex.cli archive store ...
```text

## Approval

- [ ] Architecture Lead
- [ ] Security Lead
- [ ] Operations Lead

## References

- [Sigstore Documentation](https://docs.sigstore.dev/)
- [SLSA Framework](https://slsa.dev/)
- [GitHub OIDC](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
