# Test Best Practices Guide
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Version**: 1.0.0  
**Last Updated**: 2026-07-08  
**Author**: Test Pattern Guardian Agent  
**Status**:  APPROVED FOR ALL TEST DEVELOPMENT

---

##  Table of Contents

1. [Test Naming & Structure](#test-naming--structure)
2. [Assertion Patterns](#assertion-patterns)
3. [Mock & Fixture Design](#mock--fixture-design)
4. [Async Test Patterns](#async-test-patterns)
5. [Exception Handling](#exception-handling)
6. [Documentation](#documentation)
7. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)

---

## 1. Test Naming & Structure

###  GOOD: Descriptive Test Names

Test names should describe **what** is being tested and **what** the expected behavior is.

```python
#  GOOD - Clear, descriptive, actionable
def test_user_creation_with_valid_email_succeeds():
    """Test that user creation succeeds when email is valid."""
    user = create_user(email="test@example.com")
    assert user.email == "test@example.com"

def test_invalid_email_raises_validation_error():
    """Test that invalid email raises ValidationError."""
    with pytest.raises(ValidationError):
        create_user(email="invalid-email")

def test_duplicate_email_prevents_user_creation():
    """Test that duplicate email prevents user creation."""
    create_user(email="test@example.com")
    with pytest.raises(DuplicateUserError):
        create_user(email="test@example.com")
```

###  BAD: Ambiguous or Single-Word Names

```python
#  BAD - Too short, unclear intent
def test_user():
    # What about the user? Create? Validate? Delete?
    pass

def test_email():
    # Email validation? Parsing? Sending?
    pass

def test_a():
    # Completely unclear
    pass
```

### Naming Convention

```
test_<subject>_<action>_<expected_result>
```

- **Subject**: What entity is being tested (user, email, config, etc.)
- **Action**: What operation is being performed (create, update, delete, validate)
- **Expected Result**: What should happen (succeeds, raises_error, returns_value)

---

## 2. Assertion Patterns

###  GOOD: Specific Assertions

```python
#  GOOD - Specific assertions with clear messages
def test_user_name_is_stored_correctly():
    """Test that user name is stored and retrieved correctly."""
    user = create_user(name="Alice Smith")
    assert user.name == "Alice Smith", f"Expected 'Alice Smith', got {user.name}"
    assert len(user.name) > 0, "User name should not be empty"

#  GOOD - Multiple assertions for different aspects
def test_created_user_has_correct_defaults():
    """Test that new user has correct default values."""
    user = create_user(email="test@example.com")
    
    # Check required fields
    assert user.email == "test@example.com"
    assert user.created_at is not None
    
    # Check defaults
    assert user.status == "active"
    assert user.is_admin is False
```

###  BAD: Broad or Missing Assertions

```python
#  BAD - No assertion (test does nothing)
def test_user_creation():
    user = create_user(email="test@example.com")

#  BAD - Overly broad assertion
def test_user_data():
    user = create_user(email="test@example.com")
    assert user  # Just checks if user exists, not what properties it has

#  BAD - Message says "must not be empty" but tests something else
def test_user_email():
    user = create_user(email="test@example.com")
    assert user.name == "Alice", "Result must not be empty"  # Misleading message
```

---

## 3. Mock & Fixture Design

###  GOOD: Proper Mock Configuration

```python
#  GOOD - Use return_value for repeated calls (infinite)
@pytest.fixture
def mock_api():
    mock = MagicMock()
    mock.get_user.return_value = {"id": 1, "name": "Alice"}
    return mock

def test_fetch_user_multiple_times(mock_api):
    """Test that API can be called multiple times."""
    user1 = mock_api.get_user()
    user2 = mock_api.get_user()
    user3 = mock_api.get_user()
    
    assert user1 == user2 == user3 == {"id": 1, "name": "Alice"}
    assert mock_api.get_user.call_count == 3

#  GOOD - Use side_effect with callable for complex scenarios
@pytest.fixture
def mock_api_with_state():
    mock = MagicMock()
    call_count = [0]
    
    def get_user_with_sequence(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            return {"id": 1, "name": "Alice"}
        else:
            raise RuntimeError("API error")
    
    mock.get_user.side_effect = get_user_with_sequence
    return mock
```

###  BAD: Side Effect List Exhaustion

```python
#  BAD - side_effect with list exhausts after N calls
@pytest.fixture
def mock_api():
    mock = MagicMock()
    mock.get_user.side_effect = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ]
    return mock

def test_fetch_three_users(mock_api):
    """Test that API can fetch three users."""
    user1 = mock_api.get_user()  # Works: {"id": 1, "name": "Alice"}
    user2 = mock_api.get_user()  # Works: {"id": 2, "name": "Bob"}
    user3 = mock_api.get_user()  # BREAKS: StopIteration error!
```

### Fixture Design Principles

```python
#  GOOD - Fixtures with single responsibility
@pytest.fixture
def mock_database():
    """Mock database for testing queries."""
    mock = MagicMock()
    mock.query.return_value = []
    return mock

@pytest.fixture
def mock_api_client():
    """Mock external API client."""
    mock = MagicMock()
    mock.get.return_value = {"status": "ok"}
    return mock

#  GOOD - Factory fixtures for flexibility
@pytest.fixture
def make_user():
    """Factory fixture to create test users with custom properties."""
    def _make(email="test@example.com", name="Test User", **kwargs):
        return User(email=email, name=name, **kwargs)
    return _make

def test_user_with_custom_name(make_user):
    user = make_user(name="Alice")
    assert user.name == "Alice"
```

---

## 4. Async Test Patterns

###  GOOD: Proper Async Test Structure

```python
#  GOOD - Use @pytest.mark.asyncio for async tests
@pytest.mark.asyncio
async def test_async_user_creation():
    """Test async user creation succeeds."""
    user = await create_user_async(email="test@example.com")
    assert user.email == "test@example.com"

#  GOOD - Async fixture with proper setup
@pytest.fixture
async def async_db():
    """Async database fixture."""
    db = AsyncDatabase()
    await db.connect()
    yield db
    await db.disconnect()

@pytest.mark.asyncio
async def test_with_async_db(async_db):
    """Test with async database."""
    await async_db.create_user(email="test@example.com")
    user = await async_db.get_user("test@example.com")
    assert user is not None
```

###  BAD: Async Anti-Patterns

```python
#  BAD - Missing @pytest.mark.asyncio
async def test_async_user_creation():
    user = await create_user_async(email="test@example.com")
    assert user.email == "test@example.com"
    # Will not run as async test!

#  BAD - Blocking call in async test
@pytest.mark.asyncio
async def test_blocking_in_async():
    user = await create_user_async(email="test@example.com")
    time.sleep(1)  # Blocks the event loop!
    assert user.email == "test@example.com"
```

---

## 5. Exception Handling

###  GOOD: Specific Exception Handling

```python
#  GOOD - Catch specific exceptions
try:
    user = create_user(email="invalid@")
except (ValidationError, ValueError) as e:
    logger.error(f"User creation failed: {e}")
    pass

#  GOOD - Specific exception in tests
def test_invalid_email_raises_validation_error():
    """Test that invalid email raises ValidationError."""
    with pytest.raises(ValidationError, match="Invalid email format"):
        create_user(email="invalid@")
```

###  BAD: Bare Except Clauses

```python
#  BAD - Catches all exceptions including KeyboardInterrupt, SystemExit
try:
    user = create_user(email="test@example.com")
except:
    pass  # Silently swallows all errors!

#  BAD - Too broad exception catching
try:
    user = create_user(email="test@example.com")
except Exception:
    pass  # Still too broad
```

### Exception Handling in Tests

```python
#  GOOD - Clear exception expectations
def test_handles_network_error_gracefully():
    """Test that network errors are handled gracefully."""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = ConnectionError("Network unreachable")
        
        with pytest.raises(ConnectionError):
            fetch_user_data("test@example.com")

#  GOOD - Specific exception type matching
def test_invalid_config_raises_config_error():
    """Test that invalid config raises ConfigError with helpful message."""
    with pytest.raises(ConfigError) as exc_info:
        load_config("invalid.yaml")
    
    assert "invalid.yaml" in str(exc_info.value)
    assert "required field" in str(exc_info.value).lower()
```

---

## 6. Documentation

###  GOOD: Clear Test Documentation

```python
def test_user_email_validation_accepts_standard_format():
    """
    Test that email validation accepts standard email format.
    
    This test validates the basic email format: local@domain.ext
    Ensures compliance with RFC 5321 basic format requirements.
    """
    valid_emails = [
        "simple@example.com",
        "user.name@example.co.uk",
        "user+tag@example.com",
    ]
    
    for email in valid_emails:
        user = create_user(email=email)
        assert user.email == email, f"Email {email} should be valid"

#  GOOD - Class-level documentation
class TestUserCreation:
    """Tests for user creation functionality.
    
    This test suite covers:
    - Valid user creation
    - Email validation
    - Duplicate prevention
    - Default value assignment
    """
    
    def test_create_user_with_valid_email(self):
        """Test that user creation succeeds with valid email."""
        pass
```

###  BAD: Missing or Unclear Documentation

```python
#  BAD - No docstring
def test_user():
    user = create_user(email="test@example.com")
    assert user is not None

#  BAD - Misleading message
def test_email():
    """Test email."""  # Too vague
    pass

#  BAD - Documentation that doesn't match code
def test_user_creation():
    """Test that user is created with id."""
    user = create_user(email="test@example.com")
    assert user.email == "test@example.com"  # Testing email, not id
```

---

## 7. Anti-Patterns to Avoid

### Anti-Pattern 1: Test Interdependencies

```python
#  BAD - Tests depend on execution order
class TestUserWorkflow:
    user_id = None
    
    def test_1_create_user(self):
        """First test must run first."""
        self.user_id = create_user(email="test@example.com").id
    
    def test_2_update_user(self):
        """Second test depends on first."""
        update_user(self.user_id, name="Alice")

#  GOOD - Tests are independent
@pytest.fixture
def created_user():
    """Fixture creates user for each test."""
    return create_user(email="test@example.com")

def test_create_user(created_user):
    assert created_user.id is not None

def test_update_user(created_user):
    update_user(created_user.id, name="Alice")
    updated = get_user(created_user.id)
    assert updated.name == "Alice"
```

### Anti-Pattern 2: Hardcoded Timeouts

```python
#  BAD - Hardcoded sleep causes flakiness
def test_async_operation():
    start_operation()
    time.sleep(2)  # What if it takes 2.1 seconds?
    assert operation_completed()

#  GOOD - Use polling with timeout
def test_async_operation():
    start_operation()
    
    max_wait = 5
    start = time.time()
    while time.time() - start < max_wait:
        if operation_completed():
            break
        time.sleep(0.1)
    else:
        pytest.fail(f"Operation did not complete within {max_wait}s")

#  GOOD - Use pytest.mark.timeout
@pytest.mark.timeout(5)
def test_async_operation():
    start_operation()
    wait_for_operation()  # Should complete within 5 seconds
```

### Anti-Pattern 3: Shared Mutable State

```python
#  BAD - Shared mock state between tests
mock_db = MagicMock()

def test_1():
    mock_db.query.return_value = [{"id": 1}]
    result = db.query()
    assert result == [{"id": 1}]

def test_2():
    # Returns [{"id": 1}] from previous test!
    result = db.query()
    assert result == []  # FAILS

#  GOOD - Fresh fixtures for each test
@pytest.fixture
def mock_db():
    return MagicMock()

def test_1(mock_db):
    mock_db.query.return_value = [{"id": 1}]
    result = db.query()
    assert result == [{"id": 1}]

def test_2(mock_db):
    # Fresh mock, returns default MagicMock
    result = db.query()
    assert result is not None
```

### Anti-Pattern 4: Missing Assertions

```python
#  BAD - Test does nothing
def test_user_creation():
    user = create_user(email="test@example.com")
    # No assertions!

#  GOOD - Clear assertions
def test_user_creation_succeeds():
    """Test that user creation succeeds with valid email."""
    user = create_user(email="test@example.com")
    assert user is not None
    assert user.email == "test@example.com"
    assert user.created_at is not None
```

### Anti-Pattern 5: Overly Broad Exception Catching

```python
#  BAD - Catches system exceptions
def test_user_creation():
    try:
        user = create_user(email="test@example.com")
        assert user is not None
    except:
        pytest.fail("Should not raise exception")

#  GOOD - Specific exception handling
def test_user_creation():
    """Test that user creation succeeds."""
    user = create_user(email="test@example.com")
    assert user is not None

def test_invalid_email_raises_error():
    """Test that invalid email raises ValidationError."""
    with pytest.raises(ValidationError):
        create_user(email="invalid@")
```

---

##  Checklist for Every Test

Before merging a test, verify:

- [ ] **Naming**: Test name describes what is being tested
- [ ] **Docstring**: Function has a clear docstring explaining intent
- [ ] **Assertions**: At least one specific assertion that validates behavior
- [ ] **Isolation**: Test is independent and doesn't depend on other tests
- [ ] **Mocks**: Mock objects use `return_value` for repeated calls, not `side_effect` lists
- [ ] **Async**: Async tests have `@pytest.mark.asyncio` decorator
- [ ] **Exceptions**: Specific exception handling (no bare `except:`)
- [ ] **Setup/Teardown**: Resources are properly cleaned up
- [ ] **Documentation**: Intent and edge cases are documented
- [ ] **Performance**: Test completes in reasonable time (< 5 seconds for unit tests)

---

##  Running Tests

```bash
# Run quick tests (not slow, not integration)
python scripts/ci/rvs_preflight.py --group quick

# Run tests on changed files only
python scripts/ci/rvs_preflight.py --group quick --changed-only

# Run with parallel workers
python scripts/ci/rvs_preflight.py --group quick --workers 6

# Run with fail-fast (stop on first failure)
python scripts/ci/rvs_preflight.py --group quick --fail-fast

# Run specific test file
pytest tests/test_user.py -v

# Run specific test function
pytest tests/test_user.py::test_user_creation -v

# Run with output capture disabled (see print statements)
pytest tests/test_user.py -s
```

---

##  Related Resources

- **Testing Guide**: See `CONTRIBUTING.md` for testing requirements
- **Fixtures**: Common test fixtures are in `tests/conftest.py`
- **Mocking Patterns**: Review existing tests in `tests/*/test_*.py` for examples
- **CI/CD**: Test execution in GitHub Actions via `.github/workflows/`

---

**Last Review**: 2026-07-08  
**Next Review**: 2026-08-08 (monthly)  
**Maintainer**: Test Pattern Guardian Agent

