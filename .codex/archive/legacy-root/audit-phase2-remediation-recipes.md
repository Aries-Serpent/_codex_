# Test Suite Anti-Patterns: Remediation Recipes

Quick reference guide for fixing common anti-patterns found in the test suite.

---

## 🔴 CRITICAL PATTERNS

### Pattern 1: Tests Without Assertions

**❌ BEFORE** (Smoke test, no validation):
```python
def test_config_loading():
    config = load_config("test_config.yaml")
    # No assertion - passes as long as no exception
```

**✅ AFTER** (With assertions):
```python
def test_config_loading():
    config = load_config("test_config.yaml")
    
    # Validate the actual behavior
    assert config is not None, "Config should be loaded"
    assert config.debug is True, "Debug mode should be enabled"
    assert "database" in config, "Database config should be present"
```

**✅ BETTER** (Multiple scenarios):
```python
def test_config_loading_valid():
    config = load_config("test_config.yaml")
    assert config.debug is True

def test_config_loading_missing():
    with pytest.raises(FileNotFoundError):
        load_config("nonexistent.yaml")

def test_config_loading_invalid_format():
    with pytest.raises(ValueError):
        load_config("invalid.yaml")
```

---

### Pattern 2: Test Isolation - Global State Contamination

**❌ BEFORE** (Unscoped monkeypatch):
```python
def test_environment_integration(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("API_KEY", "test-key")
    monkeypatch.setenv("DATABASE_URL", "sqlite://test.db")
    
    # State persists after test if next test doesn't restore
    process_request()
```

**✅ AFTER** (Proper fixture):
```python
@pytest.fixture
def clean_env(monkeypatch):
    """Automatically cleanup all environment changes after test."""
    # monkeypatch fixture already auto-reverts all changes
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("API_KEY", "test-key")
    monkeypatch.setenv("DATABASE_URL", "sqlite://test.db")
    yield  # Test runs here
    # All monkeypatch changes automatically undone

def test_environment_integration(clean_env):
    process_request()  # Environment is clean and isolated
```

**✅ BETTER** (Encapsulated):
```python
@pytest.fixture
def debug_mode(monkeypatch):
    """Enable debug logging for test."""
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    yield

@pytest.fixture
def test_api_credentials(monkeypatch):
    """Provide test API credentials."""
    monkeypatch.setenv("API_KEY", "test-key")
    yield

def test_environment_integration(debug_mode, test_api_credentials):
    process_request()
```

---

### Pattern 3: Flaky Tests - Hardcoded Sleep

**❌ BEFORE** (Brittle timeout):
```python
def test_background_task():
    task = BackgroundTask()
    task.start()
    
    time.sleep(2)  # Hope 2 seconds is enough!
    assert task.is_complete()  # FLAKY on slow CI
```

**✅ AFTER** (Event-based):
```python
def test_background_task():
    task = BackgroundTask()
    task.start()
    
    # Wait for completion event with timeout
    assert task.wait_for_completion(timeout=5), \
        "Task should complete within 5 seconds"
```

**✅ ALTERNATIVE** (Polling):
```python
def test_background_task():
    task = BackgroundTask()
    task.start()
    
    # Poll with exponential backoff
    max_attempts = 50
    for attempt in range(max_attempts):
        if task.is_complete():
            break
        time.sleep(0.1 * (1.2 ** attempt))  # Exponential backoff
    else:
        pytest.fail("Task did not complete in time")
```

**✅ BEST** (Async/await):
```python
@pytest.mark.asyncio
async def test_background_task():
    task = BackgroundTask()
    await task.start()
    
    # Wait with timeout
    try:
        await asyncio.wait_for(task.wait_for_completion(), timeout=5)
    except asyncio.TimeoutError:
        pytest.fail("Task did not complete in time")
    
    assert task.is_complete()
```

---

## 🟠 MEDIUM-PRIORITY PATTERNS

### Pattern 4: Mock Side-Effect List Exhaustion

**❌ BEFORE** (Only supports 2 calls):
```python
@pytest.fixture
def mock_api():
    mock = MagicMock()
    mock.fetch.side_effect = [
        {"status": 200},
        {"status": 404},
    ]
    return mock

def test_api_retry(mock_api):
    mock_api.fetch()  # OK
    mock_api.fetch()  # OK
    mock_api.fetch()  # ❌ StopIteration!
```

**✅ AFTER** (Unlimited return value):
```python
@pytest.fixture
def mock_api():
    mock = MagicMock()
    mock.fetch.return_value = {"status": 200}  # Always returns this
    return mock

def test_api_fetch(mock_api):
    result1 = mock_api.fetch()
    result2 = mock_api.fetch()
    result3 = mock_api.fetch()
    # All return {"status": 200}
```

**✅ BETTER** (Parametrized scenarios):
```python
@pytest.fixture
def mock_api():
    mock = MagicMock()
    # Default behavior
    mock.fetch.return_value = {"status": 200}
    return mock

def test_api_success(mock_api):
    result = mock_api.fetch()
    assert result["status"] == 200

def test_api_error(mock_api):
    mock_api.fetch.side_effect = NetworkError("Connection failed")
    with pytest.raises(NetworkError):
        mock_api.fetch()
```

**✅ ADVANCED** (Generator side effect):
```python
@pytest.fixture
def mock_api_sequence():
    def generate_responses():
        yield {"status": 200, "data": "first"}
        yield {"status": 200, "data": "second"}
        while True:  # Unlimited fallback
            yield {"status": 200, "data": "default"}
    
    mock = MagicMock()
    mock.fetch.side_effect = generate_responses()
    return mock
```

---

### Pattern 5: High Fixture Complexity

**❌ BEFORE** (Deep dependency chain):
```python
@pytest.fixture
def db():
    return Database()

@pytest.fixture
def service(db):
    return Service(db)

@pytest.fixture
def api(service):
    return API(service)

@pytest.fixture
def client(api):
    return Client(api)

# Tests need: def test_something(client):
# But really only need client, unclear what the actual dependencies are
```

**✅ AFTER** (Flat, clear dependencies):
```python
@pytest.fixture
def database():
    """Test database instance."""
    return Database()

@pytest.fixture
def service(database):
    """Service with database dependency."""
    return Service(database)

# Clear: tests know exactly what they depend on
def test_service_logic(service):
    assert service.get_user(1) is not None

# Test at different layers as needed
def test_database_connection(database):
    assert database.is_connected()
```

**✅ FACTORY PATTERN** (Maximum flexibility):
```python
@pytest.fixture
def make_service():
    """Factory fixture for creating services."""
    def _make_service(db_type="sqlite"):
        db = Database(db_type)
        return Service(db)
    return _make_service

def test_with_sqlite(make_service):
    service = make_service("sqlite")
    assert service.is_ready()

def test_with_postgresql(make_service):
    service = make_service("postgresql")
    assert service.is_ready()
```

---

### Pattern 6: Test Parametrization Explosion

**❌ BEFORE** (Combinatorial explosion):
```python
@pytest.mark.parametrize("model", ["bert", "gpt", "t5"])
@pytest.mark.parametrize("batch_size", [1, 8, 16, 32])
@pytest.mark.parametrize("dtype", ["float32", "float16"])
@pytest.mark.parametrize("device", ["cpu", "cuda"])
@pytest.mark.parametrize("optimization", ["adam", "sgd", "adamw"])
def test_model_training(model, batch_size, dtype, device, optimization):
    # 3 * 4 * 2 * 2 * 3 = 144 test cases!
    pass
```

**✅ AFTER** (Focused test cases):
```python
# Test models separately
@pytest.mark.parametrize("model", ["bert", "gpt", "t5"])
def test_model_loading(model):
    m = load_model(model)
    assert m is not None

# Test configurations separately
@pytest.mark.parametrize("batch_size", [1, 8, 16, 32])
def test_batch_sizes(batch_size):
    loader = DataLoader(batch_size=batch_size)
    assert loader.batch_size == batch_size

# Test specific combinations that matter
@pytest.mark.parametrize("dtype,device", [
    ("float32", "cpu"),
    ("float16", "cuda"),
])
def test_dtype_device_combinations(dtype, device):
    model = load_model(dtype=dtype, device=device)
    assert model.dtype == dtype
```

---

## 🟡 PATTERNS TO AVOID

### Pattern 7: Tests Without Clear Purpose

**❌ BEFORE** (Unclear what's being tested):
```python
def test_user_model():
    user = User("John", "john@example.com")
    # What are we testing? Just that it doesn't crash?
```

**✅ AFTER** (Clear assertion):
```python
def test_user_creation_with_valid_email():
    user = User("John", "john@example.com")
    assert user.name == "John"
    assert user.email == "john@example.com"

def test_user_creation_with_invalid_email():
    with pytest.raises(ValueError):
        user = User("John", "invalid-email")
```

---

### Pattern 8: Shared Mutable State

**❌ BEFORE** (State leaks between tests):
```python
@pytest.fixture(scope="session")
def shared_cache():
    cache = {}
    yield cache
    # Cleanup happens AFTER all tests

def test_cache_1(shared_cache):
    shared_cache["key"] = "value1"

def test_cache_2(shared_cache):
    # May see state from test_cache_1!
    assert shared_cache.get("key") == "value1"  # Flaky
```

**✅ AFTER** (Per-test fixtures):
```python
@pytest.fixture
def cache():
    """Fresh cache for each test."""
    return {}

def test_cache_1(cache):
    cache["key"] = "value1"
    assert cache["key"] == "value1"

def test_cache_2(cache):
    # Fresh cache, no state from test_cache_1
    assert "key" not in cache
```

---

## Implementation Checklist

### For Each Test File

- [ ] Add assertions to all tests without them
- [ ] Replace `time.sleep()` with events/timeouts
- [ ] Check monkeypatch usage (limit to 1-2 per test)
- [ ] Verify fixture scopes are `function`-level
- [ ] Ensure parametrization focuses on key scenarios
- [ ] Add docstrings explaining what's tested
- [ ] Remove debug/commented code
- [ ] Ensure each test is independent

### For Test Suite

- [ ] Create shared fixtures in conftest.py (but limit depth)
- [ ] Document fixture dependencies
- [ ] Add pre-commit hooks for validation
- [ ] Enable pytest-randomly for order testing
- [ ] Create testing best practices guide
- [ ] Train team on patterns

---

## Quick Fixes (Do These First)

1. **Find tests without assertions** (30 min)
   ```bash
   grep -r "def test_" tests/ | grep -v "assert\|raise\|yield"
   ```

2. **Fix most obvious monkeypatch** (1-2 hours)
   ```bash
   grep -r "monkeypatch\." tests/ | grep -v "monkeypatch\.setenv" | head
   ```

3. **Replace hardcoded sleep** (1-2 hours)
   ```bash
   grep -r "time\.sleep\|sleep(" tests/
   ```

4. **Fix side_effect lists** (30 min)
   ```bash
   grep -r "side_effect = \[" tests/
   ```

---

## Further Reading

- **Pytest Documentation**: https://docs.pytest.org/
- **Mock Best Practices**: https://docs.python.org/3/library/unittest.mock.html
- **Async Testing**: https://docs.pytest.org/en/latest/how-to-write-and-report-assertions.html
- **Fixtures**: https://docs.pytest.org/en/latest/how-to-use-fixtures.html

---

**Last Updated**: 2026-01-23  
**Companion Report**: audit-phase2-test-patterns.md
