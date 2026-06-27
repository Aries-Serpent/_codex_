# Phase 6 Wave 1: Test Generation Implementation Guide

**Document Type**: Tactical Implementation Guide  
**Target Audience**: Test developers, automation engineers  
**Scope**: 67 TIER-1 test implementations (unit + integration + error paths)  
**Reference**: `.codex/PHASE_6_WAVE_1_COVERAGE_REMEDIATION.md`

---

## Quick Start (5-Minute Setup)

### 1. Clone Test Templates
```bash
# Copy test template directory
mkdir -p tests/phase6_wave1
cp .codex/templates/test_*.py tests/phase6_wave1/

# Initialize test fixtures
python -m pytest tests/phase6_wave1/ --collect-only 2>/dev/null | head -20
```

### 2. Install Test Dependencies
```bash
# Ensure all test libraries installed
pip install pytest>=7.4 pytest-asyncio pytest-mock PyJWT cryptography -q

# Verify installation
python -c "import pytest, pytest_asyncio, pytest_mock; print('✅ All dependencies installed')"
```

### 3. Run Baseline Coverage
```bash
# Run existing tests to establish baseline
pytest tests/ -v --cov=src --cov-report=json --cov-config=.coveragerc

# View baseline metrics
python -c "import json; cov=json.load(open('coverage.json')); print(f\"Baseline: {cov['totals']['percent_covered']:.1f}%\")"
```

---

## Test Implementation Hierarchy

### TIER-1A: Authentication & Lifecycle (CRITICAL - Start Here)

#### Test Suite 1.1: `test_mcp_authentication.py`
**Module**: `src/mcp/auth.py`  
**File Size**: ~250 lines  
**Tests**: 5  
**Execution Time**: ~2 seconds

```python
"""MCP authentication layer tests."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, Mock
from src.mcp.auth import (
    MCP_Authentication,
    TokenExpiredError,
    InvalidSignatureError,
)

class TestMCPTokenGeneration:
    """Test JWT token generation."""
    
    @pytest.fixture
    def auth(self):
        """Initialize authentication instance."""
        return MCP_Authentication(
            secret_key="test-secret-key-12345",
            algorithm="HS256"
        )
    
    def test_generate_token_valid(self, auth):
        """Test token generation with valid payload.
        
        Validates:
        - Token is string
        - Token can be decoded
        - Payload matches input
        """
        payload = {"user_id": 123, "role": "admin"}
        token = auth.generate_token(payload, expires_in=3600)
        
        assert isinstance(token, str)
        assert len(token) > 10
        
        decoded = auth.validate_token(token)
        assert decoded["user_id"] == 123
        assert decoded["role"] == "admin"
    
    def test_generate_token_with_expiry(self, auth):
        """Test token generation with custom expiry."""
        token = auth.generate_token(
            {"session_id": "sess_001"},
            expires_in=7200
        )
        
        decoded = auth.validate_token(token)
        assert "exp" in decoded
        assert decoded["exp"] > datetime.utcnow().timestamp()

class TestMCPTokenValidation:
    """Test JWT token validation."""
    
    @pytest.fixture
    def auth(self):
        return MCP_Authentication(secret_key="test-secret")
    
    def test_validate_token_expired(self, auth):
        """Test validation fails for expired token.
        
        Creates token that's already expired,
        validates exception is raised.
        """
        # Generate token that's already expired
        with patch('src.mcp.auth.datetime') as mock_datetime:
            now = datetime(2026, 1, 1, 12, 0, 0)
            mock_datetime.utcnow.return_value = now
            
            token = auth.generate_token(
                {"user": "test"},
                expires_in=1  # 1 second from mock now
            )
        
        # Move time forward past expiry
        future = datetime(2026, 1, 1, 13, 0, 0)
        with patch('src.mcp.auth.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = future
            
            with pytest.raises(TokenExpiredError):
                auth.validate_token(token)
    
    def test_validate_token_invalid_signature(self, auth):
        """Test validation fails when signature tampered."""
        token = auth.generate_token({"user": "test"})
        
        # Tamper with token
        tampered = token[:-10] + "corrupted!!"
        
        with pytest.raises(InvalidSignatureError):
            auth.validate_token(tampered)
    
    def test_validate_token_malformed_json(self, auth):
        """Test validation with malformed token structure."""
        malformed_tokens = [
            "not.a.token",
            "part1.part2",  # Missing payload
            "eyJ.invalid.structure",
        ]
        
        for token in malformed_tokens:
            with pytest.raises((InvalidSignatureError, ValueError)):
                auth.validate_token(token)

class TestMCPSessionLifecycle:
    """Test session creation and management."""
    
    @pytest.fixture
    def auth(self):
        return MCP_Authentication(secret_key="test-secret")
    
    def test_create_session(self, auth):
        """Test session creation returns valid session ID."""
        session = auth.create_session(user_id=123)
        
        assert session["session_id"]
        assert session["user_id"] == 123
        assert "created_at" in session
        assert "token" in session
    
    def test_session_token_roundtrip(self, auth):
        """Test session token can be validated."""
        session = auth.create_session(user_id=456)
        token = session["token"]
        
        # Validate token contains session data
        decoded = auth.validate_token(token)
        assert decoded["user_id"] == 456
```

#### Test Suite 1.2: `test_mcp_protocol_basics.py`
**Module**: `src/mcp/protocol.py`  
**Tests**: 10  
**Execution Time**: ~3 seconds

```python
"""MCP protocol message handling tests."""

import pytest
import json
from src.mcp.protocol import (
    MCP_Parser,
    MCP_Serializer,
    ParseError,
    ValidationError,
)

class TestMCPMessageParsing:
    """Test protocol message parsing."""
    
    @pytest.fixture
    def parser(self):
        return MCP_Parser()
    
    def test_parse_valid_message(self, parser):
        """Test parsing valid MCP message."""
        message = {
            "type": "request",
            "id": 1,
            "method": "get_status",
            "params": {}
        }
        
        result = parser.parse(json.dumps(message))
        
        assert result["type"] == "request"
        assert result["method"] == "get_status"
    
    def test_parse_multiple_messages(self, parser):
        """Test parsing message sequence."""
        messages = [
            {"type": "request", "id": 1, "method": "ping"},
            {"type": "response", "id": 1, "result": {"pong": True}},
        ]
        
        for msg in messages:
            result = parser.parse(json.dumps(msg))
            assert result["type"] in ["request", "response"]

class TestMCPMessageSerialization:
    """Test message serialization."""
    
    @pytest.fixture
    def serializer(self):
        return MCP_Serializer()
    
    def test_serialize_message(self, serializer):
        """Test message serialization to JSON."""
        message = {
            "type": "response",
            "id": 42,
            "result": {"status": "ok"}
        }
        
        serialized = serializer.serialize(message)
        
        assert isinstance(serialized, str)
        parsed = json.loads(serialized)
        assert parsed["id"] == 42
```

---

### TIER-1B: Service Communication (HIGH PRIORITY)

#### Test Suite 2.1: `test_service_initialization.py`
**Module**: `src/services/__init__.py`, `src/services/core.py`  
**Tests**: 8  
**Execution Time**: ~2 seconds

```python
"""Service initialization and discovery tests."""

import pytest
from unittest.mock import MagicMock, patch
from src.services import Service, ServiceRegistry

class TestServiceInitialization:
    """Test service startup and configuration."""
    
    def test_service_init_minimal(self):
        """Test service can initialize with minimal config."""
        service = Service(
            name="test_service",
            version="0.1.0",
            port=9999
        )
        
        assert service.name == "test_service"
        assert service.port == 9999
    
    def test_service_init_with_endpoints(self):
        """Test service initialization with endpoints."""
        endpoints = {
            "get_status": lambda: {"status": "ok"},
            "get_version": lambda: {"version": "0.1.0"},
        }
        
        service = Service(
            name="test_service",
            endpoints=endpoints
        )
        
        assert len(service.endpoints) == 2

class TestServiceRegistry:
    """Test service discovery and registration."""
    
    @pytest.fixture
    def registry(self):
        return ServiceRegistry()
    
    def test_register_service(self, registry):
        """Test service registration."""
        service = MagicMock(name="svc1")
        
        registry.register(service)
        
        assert registry.get("svc1") == service
    
    def test_list_services(self, registry):
        """Test listing registered services."""
        svc1 = MagicMock(name="svc1")
        svc2 = MagicMock(name="svc2")
        
        registry.register(svc1)
        registry.register(svc2)
        
        services = registry.list()
        assert len(services) == 2
```

---

### TIER-1C: Security Operations (HIGH PRIORITY)

#### Test Suite 3.1: `test_crypto_operations.py`
**Module**: `src/security/crypto.py`  
**Tests**: 4  
**Execution Time**: ~1 second

```python
"""Cryptographic operations tests."""

import pytest
from src.security.crypto import (
    encrypt_data,
    decrypt_data,
    hash_password,
    verify_password,
)

class TestEncryption:
    """Test encryption/decryption operations."""
    
    def test_encrypt_decrypt_roundtrip(self):
        """Test encrypt -> decrypt returns original data."""
        plaintext = b"sensitive data"
        key = "test-encryption-key"
        
        ciphertext = encrypt_data(plaintext, key)
        decrypted = decrypt_data(ciphertext, key)
        
        assert decrypted == plaintext
        assert ciphertext != plaintext  # Confirm encryption occurred

class TestPasswordHashing:
    """Test password hashing and verification."""
    
    def test_hash_password(self):
        """Test password hashing produces hash."""
        password = "test-password-123"
        
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 10
    
    def test_verify_password(self):
        """Test password verification."""
        password = "test-password-123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password("wrong-password", hashed) is False
```

---

## Error Path Test Implementation

#### Test Suite 4.1: `test_mcp_error_handling.py`
**Module**: `src/mcp/*`  
**Tests**: 4  
**Execution Time**: ~2 seconds

```python
"""MCP error handling and recovery tests."""

import pytest
from src.mcp.protocol import MCP_Parser, ParseError

class TestMalformedMessages:
    """Test handling of malformed protocol messages."""
    
    @pytest.fixture
    def parser(self):
        return MCP_Parser()
    
    @pytest.mark.parametrize("malformed_msg", [
        "{invalid json",
        '{"missing": "value"',
        '"unterminated string',
        '{"invalid": null, extra}',
        "",
        None,
    ])
    def test_malformed_message_rejection(self, parser, malformed_msg):
        """Test parser rejects malformed messages.
        
        Parametrized to test multiple malformed inputs.
        """
        with pytest.raises((ParseError, TypeError, ValueError)):
            parser.parse(malformed_msg)
```

---

## Integration Test Patterns

### Async Test Pattern
```python
@pytest.mark.asyncio
async def test_async_service_communication():
    """Test asynchronous service communication."""
    svc = AsyncService()
    
    await svc.connect()
    
    result = await svc.call_remote("other_svc", "method")
    
    await svc.disconnect()
    
    assert result is not None
```

### Mock External Dependencies Pattern
```python
@patch('src.services.redis.Redis')
def test_with_mocked_redis(mock_redis):
    """Test service with mocked Redis backend."""
    mock_redis.return_value.get.return_value = b'cached_value'
    
    service = ServiceWithCache()
    result = service.get_cached("key")
    
    assert result == 'cached_value'
    mock_redis.return_value.get.assert_called_with("key")
```

---

## Test Execution Command Reference

### Run Single Test Suite
```bash
pytest tests/test_mcp_authentication.py -v
```

### Run All Wave 1 Tests
```bash
pytest tests/test_mcp_*.py tests/test_service_*.py tests/test_crypto_*.py -v --tb=short
```

### Run with Coverage Report
```bash
pytest tests/phase6_wave1/ -v --cov=src --cov-report=html --cov-config=.coveragerc
```

### Run with Xfail (Expected Failures)
```bash
pytest tests/phase6_wave1/ -v --tb=no -q
```

---

## Troubleshooting Common Issues

### Issue: "ModuleNotFoundError: No module named 'src.mcp'"

**Solution**:
```bash
# Ensure PYTHONPATH includes repo root
export PYTHONPATH="$(pwd):$PYTHONPATH"
pytest tests/test_mcp_authentication.py

# OR use pytest with --import-mode
pytest --import-mode=importlib tests/test_mcp_authentication.py
```

### Issue: "Fixture 'auth' not found"

**Solution**: Ensure fixture is defined in conftest.py or same test file:
```python
# Add to tests/conftest.py
import pytest
from src.mcp.auth import MCP_Authentication

@pytest.fixture
def auth():
    return MCP_Authentication(secret_key="test-secret")
```

### Issue: Async Test Timeout

**Solution**: Increase timeout in pytest.ini:
```ini
[pytest]
asyncio_mode = auto
asyncio_default_fixture_scope = function
timeout = 30  # Seconds
```

---

## Wave 1 Completion Checklist

- [ ] All 15 test files created
- [ ] 67 test cases implemented
- [ ] All tests passing locally
- [ ] Coverage report generated (target: +15-20%)
- [ ] Mutation testing baseline created
- [ ] Integration tests verified in CI
- [ ] No flaky tests (3/3 consecutive runs)
- [ ] TIER-2 plan documented

---

*End of Test Generation Implementation Guide*
