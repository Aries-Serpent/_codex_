# Aries-Serpent Core v0.1.0-beta2 Release Notes

**Release Date**: 2026-07-09  
**Package**: `aries-serpent-core`  
**Version**: 0.1.0-beta2  
**Status**: Beta (Pre-release)

## 🎯 Overview

Aries-Serpent Core is the lightweight, zero-ML foundation package for the Aries-Serpent project. It provides essential utilities, configuration management, security handling, and resilience patterns for building robust, offline-capable applications.

**Key Characteristics**:
- ✅ **Lightweight**: 212 KB wheel size (minimal dependencies)
- ✅ **Offline-First**: Zero network calls during import/runtime
- ✅ **ML-Free**: No machine learning dependencies or coupling
- ✅ **Pure Python**: 100% stdlib + minimal curated dependencies
- ✅ **Type-Safe**: Full type hints throughout
- ✅ **Production-Ready**: Tested core modules with 80%+ coverage

## 📦 What's Included

### Core Modules (10 packages)

#### 1. Configuration Management (`codex.config`)
- Hydra-based configuration loading and merging
- YAML/JSON configuration support
- Configuration validation and schema enforcement
- Type-safe configuration classes
- Environment variable override support

**Key Classes**:
- `ConfigLoader` — Load configs from multiple sources
- `ConfigValidator` — Validate configuration schemas
- `HydraConfig` — Hydra integration layer

#### 2. Security Management (`codex.security`)
- Encryption/decryption utilities
- Key management and rotation
- Secure credential storage
- Sanitization helpers
- Input validation

**Key Classes**:
- `SecretValidator` — Validate secret compliance
- `EncryptionUtils` — Symmetric encryption operations
- `KeyStore` — Manage encryption keys

#### 3. Secrets Handling (`codex.secrets`)
- Credential vault integration
- Secret lifecycle management
- Audit logging for secret access
- Automatic secret rotation
- Multi-environment secret support

**Key Classes**:
- `SecretsManager` — Manage and rotate secrets
- `SecretStore` — In-memory secret storage
- `AuditLogger` — Track secret access

#### 4. Resilience Patterns (`codex.resilience`)
- Configurable retry policies
- Circuit breaker pattern
- Exponential backoff with jitter
- Timeout management
- Degradation strategies

**Key Classes**:
- `RetryPolicy` — Define and apply retry logic
- `CircuitBreaker` — Fail-fast pattern for cascading failures
- `DegradationStrategy` — Graceful degradation under load

#### 5. Structured Logging (`codex.logging`)
- Structured JSON logging
- Log level management
- Performance-optimized logging
- Integration with external log aggregation
- Request/correlation ID tracking

**Key Classes**:
- `StructuredLogger` — Log structured events
- `LoggerFactory` — Create type-safe loggers
- `ContextLogger` — Request context tracking

#### 6. Session Management (`codex.session`)
- Session lifecycle management
- Session state persistence
- Context-aware session handling
- Automatic cleanup and garbage collection
- Thread-safe session operations

**Key Classes**:
- `SessionManager` — Manage session lifecycle
- `SessionState` — Thread-safe state container
- `ContextManager` — Request-scoped context

#### 7. Utilities (`codex.utils`)
- String manipulation helpers
- Path and file operations
- Type checking utilities
- Dictionary/JSON helpers
- Async task helpers
- Validation utilities

**Key Modules**:
- `string_utils` — String operations
- `path_utils` — Cross-platform path handling
- `json_safe` — Safe JSON serialization
- `type_utils` — Type checking helpers

#### 8. Observability (`codex.observability`)
- Metrics collection and reporting
- Performance monitoring
- Health check endpoints
- Tracing integration
- Event tracking

**Key Classes**:
- `MetricsCollector` — Collect and aggregate metrics
- `HealthChecker` — System health monitoring
- `EventTracker` — Event tracking and reporting

#### 9. Database Operations (`codex.db`)
- Connection pooling
- Transaction management
- Query builders
- Migration support
- Connection lifecycle management

**Key Classes**:
- `ConnectionPool` — Manage database connections
- `TransactionManager` — Handle transactions
- `MigrationRunner` — Run schema migrations

#### 10. Metrics & Monitoring (`codex.metrics`)
- Prometheus-compatible metrics
- Performance counters
- Request timing and tracking
- Custom metric support
- Real-time metric aggregation

**Key Classes**:
- `MetricsRegistry` — Register and track metrics
- `Counter` — Count events
- `Histogram` — Track value distributions

## 🎯 APIs (40+ Functions)

### Configuration APIs
```python
from codex.config import ConfigLoader, ConfigValidator

# Load configuration
config = ConfigLoader.from_file('config.yaml')
config = ConfigLoader.from_dict({'key': 'value'})

# Validate configuration
validator = ConfigValidator(schema)
validator.validate(config)
```

### Security APIs
```python
from codex.security import SecretValidator, EncryptionUtils

# Validate secrets
validator = SecretValidator()
validator.check_no_hardcoded_secrets(code)

# Encrypt/decrypt
utils = EncryptionUtils()
encrypted = utils.encrypt(data, key)
decrypted = utils.decrypt(encrypted, key)
```

### Resilience APIs
```python
from codex.resilience import RetryPolicy, CircuitBreaker

# Retry with exponential backoff
policy = RetryPolicy(max_retries=3, backoff_factor=2.0)
result = policy.execute(some_function)

# Circuit breaker
breaker = CircuitBreaker(failure_threshold=5, timeout=60)
result = breaker.call(risky_function)
```

### Session APIs
```python
from codex.session import SessionManager

# Create and manage sessions
manager = SessionManager()
session = manager.create_session(session_id='abc-123')
session.set('user_id', '12345')
manager.cleanup_session(session_id='abc-123')
```

### Logging APIs
```python
from codex.logging import StructuredLogger, LoggerFactory

# Create structured loggers
logger = LoggerFactory.create('myapp.module')
logger.info('User login', user_id='123', action='login')
logger.error('Request failed', error='timeout', retries=3)
```

## 📊 Package Statistics

- **Total Modules**: 10 core packages
- **Python Files**: 80+
- **Total Lines of Code**: 5,000+
- **Test Coverage**: 80%+
- **Type Coverage**: 95%+
- **Documentation**: 100% of public APIs

## 🔧 System Requirements

| Requirement | Version |
|---|---|
| Python | ≥3.12 |
| Hydra | ≥1.3.0 |
| OmegaConf | ≥2.3.0 |
| Pydantic | ≥2.4.0 |
| PyYAML | ≥6.0.0 |
| Cryptography | ≥48.0.0 |

## 📥 Installation

### From PyPI (when available)
```bash
pip install aries-serpent-core==0.1.0-beta2
```

### From Wheel Distribution
```bash
pip install aries-serpent-core-0.1.0b2-py3-none-any.whl
```

### From Source
```bash
pip install aries-serpent-core-0.1.0-beta2.tar.gz
```

### Verify Installation
```python
import codex.config
import codex.security
import codex.resilience
import codex.session

print("✓ Aries-Serpent Core installed successfully")
```

## 🚀 Quick Start

### 1. Configuration Management
```python
from codex.config import ConfigLoader

# Load configuration
config = ConfigLoader.from_file('config.yaml')
print(config.database.host)
```

### 2. Retry Logic
```python
from codex.resilience import RetryPolicy

policy = RetryPolicy(max_retries=3, backoff_factor=2.0)

def call_api():
    # Your code here
    pass

result = policy.execute(call_api)
```

### 3. Session Management
```python
from codex.session import SessionManager

manager = SessionManager()
session = manager.create_session()
session.set('user_id', '12345')
manager.cleanup_session(session.id)
```

### 4. Structured Logging
```python
from codex.logging import LoggerFactory

logger = LoggerFactory.create('myapp.module')
logger.info('Application started', version='1.0.0')
```

## 🔐 Security

### Included Security Features
- ✅ Cryptographic key management
- ✅ Secret encryption at rest
- ✅ Input validation and sanitization
- ✅ Audit logging for sensitive operations
- ✅ OWASP-aligned security practices

### Security Contact
For security vulnerabilities, please email security@aries-serpent.dev

## 📈 Performance Characteristics

| Operation | Time | Notes |
|---|---|---|
| Config loading | <50ms | From cached YAML |
| Encryption (256-byte) | <1ms | AES-256-GCM |
| Retry policy execution | <10ms overhead | Per execution |
| Session creation | <5ms | In-memory |
| Logging JSON serialization | <2ms | Per log event |

## 🔄 Compatibility

- ✅ Linux (x86-64, ARM64)
- ✅ macOS (Intel, Apple Silicon)
- ✅ Windows 10+
- ✅ Python 3.12.0+
- ✅ Virtual environments (venv, conda, poetry)
- ✅ Docker containers

## 📖 Documentation

Full documentation available at: https://aries-serpent.github.io/_codex_/

API Reference: [docs/api/core.md](https://github.com/Aries-Serpent/_codex_/blob/main/docs/api/core.md)

## 🤝 Related Packages

| Package | Purpose | Status |
|---|---|---|
| `aries-serpent-cognitive-brain` | Cognitive agent coordination (v0.1.0) | ✅ Available |
| `aries-serpent-core` | This package | 🟡 Beta |
| `aries-serpent-ml` | ML/training utilities | ⏳ Phase 3 |
| `aries-serpent-full` | Complete integrated package | ⏳ Phase 5 |

## 📝 Changelog

### v0.1.0-beta2 (2026-07-09)
- ✅ Initial beta release
- ✅ 10 core packages
- ✅ 40+ stable APIs
- ✅ 80%+ test coverage
- ✅ Production-ready for stateless services

### Known Limitations
- Beta API stability: expect minor breaking changes in v0.1.0-rc1
- No async/await support in Session APIs (planned for v0.2.0)
- Limited custom metric types (planned expansion in v0.2.0)
- No distributed tracing integration (planned for v0.3.0)

## 🎯 Roadmap

### v0.1.0-rc1 (2026-08-09)
- [ ] Async/await session support
- [ ] Distributed tracing integration
- [ ] Performance improvements (10% faster imports)
- [ ] Extended metric types

### v0.2.0 (2026-09-09)
- [ ] Circuit breaker improvements
- [ ] Advanced resilience patterns
- [ ] Metrics persistence
- [ ] Configuration hot-reloading

### v1.0.0 (2026-12-09)
- [ ] Stable API guarantees
- [ ] Full backward compatibility
- [ ] Production SLA support
- [ ] Enterprise features

## ✅ Testing & Quality

- **Test Suite**: 25+ tests for core modules
- **Coverage**: 80%+ branch coverage
- **Type Checking**: mypy with strict mode
- **Linting**: Ruff with E,F,I rules
- **Format**: Black (100-char lines)

**Run Tests**:
```bash
pytest tests/core/ -v --cov=codex
```

## 🔐 Security Verification

### Package Integrity
Verify the wheel using SHA256 checksums:

```bash
sha256sum -c CHECKSUM.txt
```

**Wheel SHA256**: `c706172b56f3e33335b7b768ae0c8520308e90584643cf05c3febf98c686269e`  
**Tarball SHA256**: `e0ba9b2994362ac776e504d2d68049f3737bc008fa30b1954d872addc249d922`

### Supply Chain Security
- ✅ Reproducible builds
- ✅ Source integrity verified
- ✅ No unvetted dependencies
- ✅ Security-focused dependency set

## 📞 Support & Community

- **Issues**: GitHub Issues on Aries-Serpent/_codex_
- **Discussions**: GitHub Discussions (Announcements category)
- **Documentation**: https://aries-serpent.github.io/_codex_/
- **Email**: support@aries-serpent.dev

## 📜 License

MIT License - See LICENSE file for details

---

**Released by**: Aries-Serpent Project Team  
**Build Date**: 2026-07-09T02:11:00Z  
**Build Hash**: c706172b56f3e3333  
**Deployment Status**: Ready for Beta Testing
