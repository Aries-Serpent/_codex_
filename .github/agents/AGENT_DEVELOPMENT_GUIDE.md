# Agent Development Guide

**Version**: 1.0.0  
**Last Updated**: 2026-01-12  
**Purpose**: Standardized guide for creating and maintaining custom GitHub Copilot agents

## Table of Contents

1. [Overview](#overview)
2. [Agent Template Structure](#agent-template-structure)
3. [Creating a New Agent](#creating-a-new-agent)
4. [Migrating Existing Agents](#migrating-existing-agents)
5. [Best Practices](#best-practices)
6. [Testing Guidelines](#testing-guidelines)
7. [Integration Patterns](#integration-patterns)
8. [Deployment](#deployment)

---

## Overview

This guide provides instructions for creating standardized custom agents that integrate with the GitHub Copilot ecosystem and cognitive brain system.

### Why Standardization?

- **Consistency**: All agents follow the same structure
- **Maintainability**: Easier to update and fix issues
- **Discoverability**: Clear documentation and examples
- **Integration**: Seamless cognitive brain integration
- **Quality**: Built-in testing and validation

---

## Agent Template Structure

The standard agent structure is located in `.github/agents/.template/`:

```
.github/agents/.template/
├── README.md                 # Agent documentation
├── CHANGELOG.md              # Version history
├── prompts/
│   ├── main.md              # Primary agent prompt
│   ├── examples.md          # Usage examples
│   └── advanced.md          # Advanced scenarios
├── src/
│   ├── __init__.py
│   └── agent.py             # Main agent implementation
├── tests/
│   ├── __init__.py
│   ├── test_agent.py        # Unit tests
│   └── test_integration.py  # Integration tests
└── config/
    └── agent_config.yaml    # Configuration schema
```

### Component Descriptions

#### README.md
- Agent purpose and capabilities
- Usage instructions (CLI and Copilot)
- Configuration options
- Integration points
- Testing instructions

#### prompts/main.md
- Agent role and responsibilities
- Capabilities and limitations
- Guidelines (always/never do)
- Input/output formats
- Examples

#### src/agent.py
- Main agent implementation
- CLI interface using Click
- Configuration loading
- Core logic

#### tests/
- Comprehensive unit tests
- Integration tests
- Performance tests (if applicable)

#### config/agent_config.yaml
- Default configuration
- Settings schema
- Integration flags

---

## Creating a New Agent

### Step 1: Copy Template

```bash
# Navigate to agents directory
cd .github/agents

# Copy template to new agent directory
cp -r .template my-new-agent

# Navigate to new agent
cd my-new-agent
```

### Step 2: Customize Files

#### README.md
Replace placeholders:
- `[Agent Name]` → Your agent name
- `[One-line description]` → Brief purpose
- `[agent-name]` → Lowercase with hyphens
- `[Capability 1/2/3]` → Actual capabilities
- `[System 1/2]` → Integration points

#### prompts/main.md
Define:
- Agent role and responsibilities
- Specific capabilities
- Guidelines for operation
- Input/output formats
- Concrete examples

#### src/agent.py
Implement:
- `AgentClass.__init__()` - Initialization logic
- `AgentClass.execute()` - Core execution logic
- `AgentClass._default_config()` - Default configuration
- Additional helper methods as needed

#### config/agent_config.yaml
Configure:
- Agent name and version
- Capabilities list
- Integration flags
- Agent-specific settings

### Step 3: Implement Tests

#### tests/test_agent.py
Add tests for:
- Initialization
- Configuration loading
- Core functionality
- Error handling
- Edge cases

#### tests/test_integration.py
Add tests for:
- End-to-end workflows
- External integrations
- Performance (if needed)

### Step 4: Update Agent Registry

Add entry to `.github/agents/AGENT_REGISTRY.yaml`:

```yaml
- id: my-new-agent
  name: "My New Agent"
  directory: .github/agents/my-new-agent
  purpose: "Brief description of agent purpose"
  status: active
  maturity: experimental  # experimental → beta → production
  has_prompts: true
  has_tests: true
  has_docs: true
  has_src: true
  priority: medium
  capabilities:
    - capability1
    - capability2
  integration_points:
    - system1
    - system2
```

### Step 5: Test Agent

```bash
# Run unit tests
pytest .github/agents/my-new-agent/tests/test_agent.py

# Run integration tests
pytest .github/agents/my-new-agent/tests/test_integration.py

# Test CLI
python .github/agents/my-new-agent/src/agent.py --task "test task"

# Test with config
python .github/agents/my-new-agent/src/agent.py \
  --config .github/agents/my-new-agent/config/agent_config.yaml \
  --task "test task" \
  --verbose
```

### Step 6: Document

Update `CHANGELOG.md` with initial release information.

---

## Migrating Existing Agents

### Migration Process

1. **Assess Current Structure**
   ```bash
   # Check what's present
   ls -la .github/agents/existing-agent/
   ```

2. **Create Missing Directories**
   ```bash
   cd .github/agents/existing-agent
   mkdir -p prompts src tests config
   ```

3. **Copy Template Files**
   ```bash
   # Copy only missing files
   [ ! -f README.md ] && cp ../.template/README.md .
   [ ! -f prompts/main.md ] && cp ../.template/prompts/main.md prompts/
   [ ! -f tests/test_agent.py ] && cp ../.template/tests/test_agent.py tests/
   # ... etc
   ```

4. **Customize Copied Files**
   - Replace all placeholders
   - Add agent-specific content
   - Update based on existing implementation

5. **Migrate Existing Code**
   - Move Python files to `src/`
   - Update imports if needed
   - Ensure CLI interface uses Click

6. **Add Tests**
   - Write tests for existing functionality
   - Ensure all public methods are tested
   - Add integration tests

7. **Update Registry**
   - Update agent entry in `AGENT_REGISTRY.yaml`
   - Mark maturity level appropriately
   - Update compliance status

8. **Validate**
   ```bash
   # Run all tests
   pytest .github/agents/existing-agent/tests/
   
   # Test CLI
   python .github/agents/existing-agent/src/agent.py --help
   ```

### Migration Helper Script

```bash
#!/bin/bash
# migrate_agent.sh - Migrate agent to standard structure

AGENT_NAME=$1
AGENT_DIR=".github/agents/$AGENT_NAME"
TEMPLATE_DIR=".github/agents/.template"

if [ ! -d "$AGENT_DIR" ]; then
    echo "Error: Agent directory not found: $AGENT_DIR"
    exit 1
fi

echo "Migrating agent: $AGENT_NAME"

# Create missing directories
mkdir -p "$AGENT_DIR/prompts"
mkdir -p "$AGENT_DIR/src"
mkdir -p "$AGENT_DIR/tests"
mkdir -p "$AGENT_DIR/config"

# Copy template files if they don't exist
[ ! -f "$AGENT_DIR/README.md" ] && cp "$TEMPLATE_DIR/README.md" "$AGENT_DIR/README.md"
[ ! -f "$AGENT_DIR/CHANGELOG.md" ] && cp "$TEMPLATE_DIR/CHANGELOG.md" "$AGENT_DIR/CHANGELOG.md"
[ ! -f "$AGENT_DIR/prompts/main.md" ] && cp "$TEMPLATE_DIR/prompts/main.md" "$AGENT_DIR/prompts/"
[ ! -f "$AGENT_DIR/prompts/examples.md" ] && cp "$TEMPLATE_DIR/prompts/examples.md" "$AGENT_DIR/prompts/"
[ ! -f "$AGENT_DIR/prompts/advanced.md" ] && cp "$TEMPLATE_DIR/prompts/advanced.md" "$AGENT_DIR/prompts/"
[ ! -f "$AGENT_DIR/tests/test_agent.py" ] && cp "$TEMPLATE_DIR/tests/test_agent.py" "$AGENT_DIR/tests/"
[ ! -f "$AGENT_DIR/tests/test_integration.py" ] && cp "$TEMPLATE_DIR/tests/test_integration.py" "$AGENT_DIR/tests/"
[ ! -f "$AGENT_DIR/config/agent_config.yaml" ] && cp "$TEMPLATE_DIR/config/agent_config.yaml" "$AGENT_DIR/config/"

echo "✅ Migration complete. Please customize template files for $AGENT_NAME"
echo "📝 Next steps:"
echo "   1. Update README.md with agent details"
echo "   2. Create prompts/main.md with agent prompt"
echo "   3. Implement tests in tests/"
echo "   4. Update config/agent_config.yaml"
echo "   5. Update AGENT_REGISTRY.yaml"
```

---

## Best Practices

### Code Quality

1. **Type Hints**: Use Python type hints for all functions
   ```python
   def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
       ...
   ```

2. **Docstrings**: Provide comprehensive docstrings
   ```python
   """
   Execute agent task.
   
   Args:
       task: Task specification with required 'description' field
   
   Returns:
       Result dictionary with 'status', 'output', and 'timestamp'
   
   Raises:
       ValueError: If task specification is invalid
   """
   ```

3. **Error Handling**: Handle errors gracefully
   ```python
   try:
       result = self._process(task)
   except Exception as e:
       return {
           'status': 'error',
           'error': str(e),
           'timestamp': self._get_timestamp()
       }
   ```

4. **Logging**: Use structured logging
   ```python
   import logging
   
   logger = logging.getLogger(__name__)
   logger.info(f"Executing task: {task['description']}")
   ```

### Configuration

1. **Environment Variables**: Support environment variable overrides
   ```python
   timeout = os.getenv('AGENT_TIMEOUT', self.config['timeout_seconds'])
   ```

2. **Validation**: Validate configuration on load
   ```python
   def _validate_config(self, config: Dict) -> None:
       required = ['version', 'enabled']
       for key in required:
           if key not in config:
               raise ValueError(f"Missing required config: {key}")
   ```

3. **Defaults**: Provide sensible defaults
   ```python
   def _default_config(self) -> Dict:
       return {
           'timeout_seconds': 300,
           'max_retries': 3,
           'log_level': 'INFO',
       }
   ```

### Testing

1. **Coverage**: Aim for >80% test coverage
2. **Fixtures**: Use pytest fixtures for setup
3. **Mocking**: Mock external dependencies
4. **Parametrize**: Test multiple scenarios

```python
@pytest.mark.parametrize("input,expected", [
    ("valid", "success"),
    ("", "error"),
    (None, "error"),
])
def test_execute(agent, input, expected):
    result = agent.execute({'description': input})
    assert result['status'] == expected
```

### Documentation

1. **Clear Purpose**: State what the agent does
2. **Examples**: Provide concrete examples
3. **Limitations**: Document what agent can't do
4. **Integration**: Explain integration points

---

## Testing Guidelines

### Unit Tests

Test individual components in isolation:

```python
def test_config_loading(agent):
    """Test configuration loading"""
    assert agent.config is not None
    assert 'version' in agent.config

def test_execute_valid_input(agent):
    """Test execution with valid input"""
    result = agent.execute({'description': 'test'})
    assert result['status'] == 'success'

def test_execute_invalid_input(agent):
    """Test execution with invalid input"""
    with pytest.raises(ValueError):
        agent.execute({})
```

### Integration Tests

Test complete workflows:

```python
def test_end_to_end(agent):
    """Test complete workflow"""
    # Setup
    task = {'description': 'integration test'}
    
    # Execute
    result = agent.execute(task)
    
    # Verify
    assert result['status'] == 'success'
    assert 'output' in result
```

### Performance Tests

Test with realistic workloads:

```python
@pytest.mark.slow
def test_performance(agent):
    """Test agent can handle multiple tasks"""
    tasks = [{'description': f'task {i}'} for i in range(1000)]
    
    start = time.time()
    results = [agent.execute(t) for t in tasks]
    duration = time.time() - start
    
    assert duration < 60  # Should complete in under 60s
    assert all(r['status'] == 'success' for r in results)
```

---

## Integration Patterns

### GitHub Copilot Integration

Agents can be invoked by GitHub Copilot:

```
@copilot use my-agent to analyze code for security issues
```

The agent receives:
- Context from conversation
- Repository information
- User's request

### Cognitive Brain Integration

Update cognitive brain after execution:

```python
def execute(self, task: Dict) -> Dict:
    result = self._do_work(task)
    
    # Update cognitive brain
    self._update_cognitive_brain({
        'agent': 'my-agent',
        'task': task['description'],
        'outcome': result['status'],
        'timestamp': self._get_timestamp()
    })
    
    return result
```

### GitHub Actions Integration

Use agent in workflows:

```yaml
- name: Run Agent
  run: |
    python .github/agents/my-agent/src/agent.py \
      --task "${{ github.event.inputs.task }}" \
      --config .github/agents/my-agent/config/agent_config.yaml
```

### CLI Integration

Provide rich CLI experience:

```python
@click.group()
def cli():
    """My Agent CLI"""
    pass

@cli.command()
@click.argument('task')
def execute(task):
    """Execute a task"""
    agent = AgentClass()
    result = agent.execute({'description': task})
    click.echo(result['output'])

@cli.command()
def status():
    """Check agent status"""
    click.echo("Agent is operational")

if __name__ == '__main__':
    cli()
```

---

## Deployment

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run agent
python src/agent.py --task "development test"

# Run tests
pytest tests/
```

### CI/CD

Add agent tests to CI pipeline:

```yaml
- name: Test Agents
  run: |
    pytest .github/agents/my-agent/tests/ -v --cov
```

### Production

1. **Validation**: All tests pass
2. **Documentation**: Complete and accurate
3. **Registry**: Entry updated with production maturity
4. **Monitoring**: Integrated with cognitive brain
5. **Approval**: Code reviewed and approved

---

## Maturity Levels

### Experimental
- Basic functionality implemented
- Minimal documentation
- Few or no tests
- Not production-ready

### Beta
- Core functionality complete
- Documentation exists
- Some tests present
- Suitable for testing environments

### Production
- Fully implemented and tested
- Comprehensive documentation
- Full test coverage
- Integrated with cognitive brain
- Monitoring and alerting configured

---

## Getting Help

- **Documentation Issues**: Update this guide
- **Template Problems**: Create issue with "template" label
- **Migration Help**: Tag issue with "migration"
- **General Questions**: Ask in team chat or discussions

---

## Changelog

### 1.0.0 - 2026-01-12
- Initial agent development guide
- Template structure documented
- Migration process defined
- Best practices established
