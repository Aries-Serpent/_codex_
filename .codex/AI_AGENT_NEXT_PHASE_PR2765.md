# AI Agent Planset: Post-Merge Production Readiness

**Context**: PR #2765 addresses code review feedback and establishes security documentation standards. After merge, the next phase focuses on production readiness for stub implementations and Priority 4 enhancements.

**Branch**: Create new branch from `main` after #2765 merges  
**Target Audience**: AI Agents (GitHub Copilot, Custom Agents)  
**Policy Compliance**: Follows `.codex/CODEBASE_AGENCY_POLICY.md` - No calendar terms, pre-commit cycle terminology only

---

## Phase Objective

Convert stub implementations to production-ready code, implement deferred enhancements, and complete Priority 4 planset items with production deployment readiness.

## Pre-Commit Cycle Structure

### Cycle 1-2: Security Production Readiness (High Priority)

#### Pre-Commit 1: Token Scope Extraction
**File**: `src/security/decorators.py`  
**Current**: `get_token_scopes()` raises NotImplementedError  
**Required**:
- Choose implementation approach (JWT or OAuth introspection)
- Implement actual token validation and scope extraction
- Add configuration for secret keys / introspection endpoints
- Write comprehensive tests (valid tokens, expired, invalid signature)
- Document deployment requirements

**Example JWT Implementation**:
```python
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

async def get_token_scopes(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> List[str]:
    """Extract scopes from JWT token."""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload.get("scopes", [])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

**Dependencies**: PyJWT or similar library  
**Tests**: `tests/security/test_token_validation.py`  
**Documentation**: Update `.codex/SECURITY_FALSE_POSITIVE_STANDARD.md` with production pattern

**Commit Criteria**:
- [ ] JWT validation implemented and tested
- [ ] Configuration management added
- [ ] Comprehensive error handling
- [ ] Documentation updated
- [ ] Integration tests passing

#### Pre-Commit 2: GitHub Provider API Integration
**File**: `src/security/providers/github_provider.py`  
**Current**: Multiple stub methods (create_token, validate_secret, revoke_secret, list_secrets)  
**Required**:
- Wire to GitHub REST API (https://api.github.com)
- Implement OAuth token creation for fine-grained PATs
- Add actual token validation via GET /user
- Implement token revocation via DELETE /user/tokens/{id}
- Add pagination for list_secrets
- Comprehensive error handling and retry logic
- Rate limit handling (X-RateLimit-* headers)

**GitHub API Endpoints**:
- POST /user/tokens - Create fine-grained PAT
- GET /user - Validate token (returns 200 if valid)
- DELETE /user/tokens/{token_id} - Revoke token
- GET /user/tokens - List all tokens

**Dependencies**: requests library (already in use)  
**Tests**: Mock GitHub API responses, test error cases  
**Security**: Never log actual token values (follow established pattern)

**Commit Criteria**:
- [ ] All GitHub provider methods implemented
- [ ] Rate limiting handled
- [ ] Error handling comprehensive
- [ ] Security logging follows `.codex/SECURITY_FALSE_POSITIVE_STANDARD.md`
- [ ] Integration tests with mocked API

### Cycle 3: PII Audit Trail
**File**: `src/codex/knowledge/pii.py`  
**Current**: TODO comment for Luhn check logging  
**Required**:
```python
import logging
logger = logging.getLogger(__name__)

def mask_credit_card(m: re.Match) -> str:
    if not _luhn_check(m.group(0)):
        # Debug logging for security audit
        logger.debug(
            "Credit card pattern matched but Luhn check failed",
            extra={
                "position": m.start(),
                "length": len(m.group(0)),
                "pattern_type": "credit_card",
                # Never log actual number
            }
        )
        return m.group(0)
    # ... rest of function
```

**Configuration**: Ensure debug logging disabled in production by default  
**Documentation**: Update security logging guidelines

**Commit Criteria**:
- [ ] Debug logging implemented
- [ ] Configuration controls added
- [ ] Documentation updated
- [ ] Tests verify logging behavior

### Cycle 4-5: User Experience Enhancements

#### Pre-Commit 4: Ticket ID Display Formatting
**File**: Create `src/codex/zendesk/display_utils.py`  
**Purpose**: Human-friendly display of 128-bit UUID-based ticket IDs  
**Reference**: `.codex/architecture/uuid_ticket_id_strategy.md` (Option B)

**Implementation**:
```python
def format_ticket_id_for_display(ticket_id: int) -> str:
    """Format 128-bit ticket ID for display.
    
    Converts large integer to human-friendly format:
    - Shows prefix + last 8 hex digits
    - Example: TKT-A7B3C9D1
    
    Args:
        ticket_id: 128-bit integer from UUID conversion
        
    Returns:
        Formatted string for UI display
    """
    return f"TKT-{ticket_id & 0xFFFFFFFF:08X}"

def parse_display_ticket_id(display_id: str) -> Optional[int]:
    """Parse display ID back to full ticket ID (requires lookup).
    
    Note: Display ID is truncated, requires database lookup
    to resolve to full 128-bit ticket ID.
    """
    # Implementation depends on whether you maintain a mapping table
    pass
```

**Tests**: Test formatting, roundtrip conversion  
**Documentation**: Update API docs with ID format

**Commit Criteria**:
- [ ] Display formatting utility implemented
- [ ] Tests cover edge cases
- [ ] API documentation updated
- [ ] Usage examples provided

#### Pre-Commit 5: Optional Dependency Management
**File**: `pyproject.toml`  
**Purpose**: Add optional dependencies for performance features

**Add Extras**:
```toml
[project.optional-dependencies]
performance = [
    "xxhash>=3.0.0",  # Fast hashing for sharding
]

ml = [
    "scikit-learn>=1.0.0",  # For semantic sharding (future)
]

full = [
    "xxhash>=3.0.0",
    "scikit-learn>=1.0.0",
]
```

**Documentation**: Update README.md with installation options:
```bash
# Standard installation
pip install codex-ml

# With performance optimizations
pip install codex-ml[performance]

# With all optional features
pip install codex-ml[full]
```

**Commit Criteria**:
- [ ] Optional dependencies configured
- [ ] README updated with examples
- [ ] Installation tested in clean environment
- [ ] Documentation complete

### Cycle 6-8: Testing and Quality

#### Pre-Commit 6: Enhanced Audio Test Fixtures
**File**: Create `tests/fixtures/audio_samples.py`  
**Purpose**: Provide realistic audio test data

**Implementation**:
```python
import struct
import wave

def create_minimal_wav(filepath: Path, duration_ms: int = 100):
    """Create minimal valid WAV file for testing.
    
    Args:
        filepath: Output path
        duration_ms: Duration in milliseconds
    """
    sample_rate = 44100
    num_samples = int(sample_rate * duration_ms / 1000)
    
    with wave.open(str(filepath), 'wb') as wav:
        wav.setnchannels(1)  # Mono
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(sample_rate)
        
        # Generate sine wave test tone
        for i in range(num_samples):
            value = int(32767 * 0.5 * math.sin(2 * math.pi * 440 * i / sample_rate))
            wav.writeframes(struct.pack('<h', value))
```

**Usage**: Update audio tests to use fixtures  
**Benefits**: More realistic testing, catches format-specific issues

**Commit Criteria**:
- [ ] Fixture creation utility implemented
- [ ] Audio tests updated to use fixtures
- [ ] Documentation explains fixture usage
- [ ] Tests pass with realistic data

#### Pre-Commit 7-8: Integration Test Suite
**File**: Create `tests/integration/test_security_flow.py`  
**Purpose**: End-to-end security flow testing

**Test Scenarios**:
1. Token generation → Validation → Scope check → Rotation → Revocation
2. Multi-provider token management (GitHub + AWS)
3. Scope validator integration with FastAPI routes
4. Error handling and fallback behaviors

**Commit Criteria (Pre-Commit 7)**:
- [ ] Integration test framework setup
- [ ] Token lifecycle tests implemented
- [ ] Mock services configured
- [ ] CI integration ready

**Commit Criteria (Pre-Commit 8)**:
- [ ] Multi-provider tests complete
- [ ] Scope validation tests complete
- [ ] Error handling scenarios covered
- [ ] Documentation updated

### Cycle 9-10: Documentation and Production Readiness

#### Pre-Commit 9: API Documentation
**Files**: 
- `docs/api/security.md` - Document security provider API
- `docs/api/zendesk.md` - Document ticket ID format
- `docs/deployment/production.md` - Production readiness checklist

**Commit Criteria**:
- [ ] API documentation complete
- [ ] Deployment guide written
- [ ] Production checklist finalized
- [ ] Examples and diagrams included

#### Pre-Commit 10: Migration Guide & Review
**File**: `docs/migration/stub_to_production.md`  
**Content**:
- Checklist for converting stubs to production
- Configuration requirements
- Testing requirements
- Deployment considerations

**Final Review**:
- [ ] All stub methods converted
- [ ] Security audit complete
- [ ] Integration tests passing
- [ ] Documentation comprehensive
- [ ] Production deployment guide ready

**Commit Criteria**:
- [ ] Migration guide complete
- [ ] Final security review passed
- [ ] All tests passing
- [ ] Ready for production deployment

### Cycle 11+: Priority 4 Enhancements (Future Scope)

#### Semantic Sharding (PS-06)
**Reference**: `src/codex/retrieval/stores/pgvector_store.py` lines 32-36  
**Implementation**: KMeans clustering for intelligent shard balancing

#### Additional Provider Support
**Add Azure Key Vault and HashiCorp Vault providers**  
**Reference**: `src/security/provider_factory.py` lines 64-74

---

## Success Criteria

### Must Have (Before Production)
- ✅ All security stubs implemented with real API calls
- ✅ Token validation working with real JWTs/OAuth
- ✅ Comprehensive integration tests passing
- ✅ Security audit complete with no high/critical issues
- ✅ Production deployment guide documented

### Should Have (Before 1.0 Release)
- ✅ Ticket ID display formatting implemented
- ✅ Optional dependencies properly configured
- ✅ Realistic test fixtures for audio processing
- ✅ API documentation complete

### Nice to Have (Future Releases)
- ⭕ Semantic sharding with KMeans
- ⭕ Azure and HashiCorp provider support
- ⭕ Performance benchmarking suite
- ⭕ Load testing framework

---

## Cognitive Brain Decision Process

### Domain Intersections

This planset operates across multiple domains that intersect:

1. **Security ∩ API Integration**: Token validation requires both security best practices and GitHub API knowledge
2. **Testing ∩ Audio Processing**: Realistic fixtures require understanding audio formats and test methodology
3. **UX ∩ Data Architecture**: Display formatting intersects with database schema and API design

### Quantum-Inspired Decision Framework

When multiple implementation paths exist, evaluate using:

**Superposition State Analysis**:
- Consider all viable options simultaneously
- Don't collapse to single solution until sufficient information gathered
- Example: JWT vs OAuth introspection—both remain viable until requirements clarify

**Entanglement Detection**:
- Identify dependencies between tasks
- Changes in one domain affect others
- Example: Token validation implementation affects both security and API documentation

**Wave Function Collapse Criteria**:
- Select implementation path when:
  1. Technical constraints eliminate alternatives
  2. Performance benchmarks favor one approach
  3. Security requirements mandate specific solution
  4. Team consensus achieved

**Measurement Effects**:
- Testing an implementation provides information
- Each test narrows the solution space
- Iterate rapidly to gather measurement data

### Decision Example: Token Validation

**Initial State**: JWT and OAuth both viable  
**Measurement 1**: Performance testing shows JWT 40% faster  
**Measurement 2**: Security audit prefers JWT for offline validation  
**Measurement 3**: Team has JWT expertise  
**Wave Function Collapse**: Select JWT implementation  
**Outcome**: High confidence decision based on multiple measurements

---

## Risk Assessment

### High Risk
- **Token validation security**: Incorrect implementation could grant unauthorized access
- **Mitigation**: Security review, penetration testing, staged rollout

### Medium Risk
- **GitHub API rate limits**: Could hit limits during token operations
- **Mitigation**: Implement exponential backoff, caching, rate limit monitoring

### Low Risk
- **UUID integer size**: Some systems may not support 128-bit integers
- **Mitigation**: Already documented with migration strategies in ADR

---

## Monitoring and Observability

### Metrics to Track
1. Token validation success/failure rates
2. GitHub API response times and rate limit status
3. PII redaction counts and types
4. Shard distribution balance
5. Cache hit/miss rates

### Alerts to Configure
1. High token validation failure rate (>5%)
2. GitHub API rate limit approaching (>80%)
3. Unexpected PII patterns detected
4. Shard imbalance (>20% deviation)

---

## Quick Start for AI Agents

```bash
# After PR #2765 merges to main
git checkout main
git pull origin main
git checkout -b feature/production-security-hardening

# Start with highest priority (Pre-Commit 1)
# 1. Implement get_token_scopes() in src/security/decorators.py
# 2. Write tests in tests/security/test_token_validation.py
# 3. Update documentation

# Run tests frequently
pytest tests/security/ -v

# Commit incrementally using report_progress tool
# Review changes carefully before each commit
```

---

## References

- Security False Positive Standard: `.codex/SECURITY_FALSE_POSITIVE_STANDARD.md`
- UUID Ticket ID ADR: `.codex/architecture/uuid_ticket_id_strategy.md`
- AI Agent Policy: `.codex/CODEBASE_AGENCY_POLICY.md`
- GitHub Token API: https://docs.github.com/en/rest/users/tokens
- JWT Specification: https://jwt.io/

---

**Prepared**: 2026-01-10  
**For**: AI Agents (GitHub Copilot, Custom Agents)  
**Priority**: High (Security items), Medium (UX items), Low (Advanced features)  
**Estimated Effort**: 10-12 pre-commit cycles for Phases 1-4, ongoing for Phase 5  
**Policy Compliance**: ✅ No calendar terms, pre-commit cycle terminology only  
**Commit SHA**: (to be added upon commit)
