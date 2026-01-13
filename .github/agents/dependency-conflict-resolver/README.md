# Dependency Conflict Resolver Agent

An intelligent agent that automatically detects and resolves dependency version conflicts across multiple ecosystems (Python, JavaScript, Rust, Go) using graph analysis and semantic versioning.

## Purpose

The Dependency Conflict Resolver Agent helps maintain healthy dependency graphs by:
- **Detecting conflicts** between direct and transitive dependencies
- **Analyzing dependency graphs** to identify circular dependencies and deep transitive issues
- **Resolving conflicts** using configurable strategies (conservative, balanced, aggressive)
- **Integrating with security scanners** for vulnerability-aware resolution
- **Supporting multiple ecosystems** in a unified workflow

## Key Features

### 🔍 Conflict Detection
- Direct dependency conflicts (explicit version mismatches)
- Transitive dependency conflicts (inherited from parent dependencies)
- Circular dependency detection
- Version range incompatibility analysis
- Semantic versioning validation

### 📊 Dependency Graph Analysis
- Build comprehensive dependency graphs
- Analyze transitive relationships up to configurable depth
- Identify critical dependency paths
- Visualize dependency trees
- Calculate impact of version changes

### 🔧 Resolution Strategies
- **Conservative**: Minimal changes, prefer lower stable versions
- **Balanced**: Balance security, stability, and features
- **Aggressive**: Latest compatible versions for maximum features

### 🛡️ Security Integration
- Integration with dependency-vulnerability-scanner (60% component reuse)
- Vulnerability-aware conflict resolution
- Prioritize security patches in version selection
- Fail on critical/high severity vulnerabilities

### 🌍 Multi-Ecosystem Support
- **Python**: requirements.txt, pyproject.toml
- **JavaScript/TypeScript**: package.json, package-lock.json
- **Rust**: Cargo.toml
- **Go**: go.mod

## Installation

```bash
# Clone the repository
git clone https://github.com/your-org/codex.git
cd .github/agents/dependency-conflict-resolver

# Install dependencies
pip install pyyaml

# Run the agent
python src/agent.py detect --file requirements.txt
```

## Quick Start

### Python Projects

```bash
# Detect conflicts in requirements.txt
python src/agent.py detect --file requirements.txt

# Generate resolution plan with conservative strategy
python src/agent.py resolve --strategy conservative --file requirements.txt

# Visualize dependency graph
python src/agent.py visualize --file requirements.txt --output graph.txt
```

Example `requirements.txt` with conflicts:
```
requests>=2.20.0
numpy>=1.20.0
# Another dependency requires different version
requests>=2.28.0  # Conflict!
```

### JavaScript Projects

```bash
# Analyze package.json
python src/agent.py detect --file package.json

# Resolve with balanced strategy
python src/agent.py resolve --strategy balanced --file package.json
```

Example `package.json`:
```json
{
  "dependencies": {
    "express": "^4.18.0",
    "lodash": "^4.17.21"
  },
  "devDependencies": {
    "jest": "^29.0.0"
  }
}
```

### Rust Projects

```bash
# Check Cargo.toml for conflicts
python src/agent.py detect --file Cargo.toml

# Resolve with aggressive strategy
python src/agent.py resolve --strategy aggressive --file Cargo.toml
```

Example `Cargo.toml`:
```toml
[dependencies]
serde = "1.0"
tokio = { version = "1.28", features = ["full"] }
reqwest = "0.11.18"
```

### Go Projects

```bash
# Analyze go.mod
python src/agent.py detect --file go.mod

# Generate resolution plan
python src/agent.py resolve --file go.mod
```

Example `go.mod`:
```go
module example.com/myproject

require (
    github.com/gin-gonic/gin v1.9.0
    github.com/stretchr/testify v1.8.2
)
```

## Configuration

The agent is configured via `config/agent_config.yaml`:

```yaml
agent_name: dependency-conflict-resolver
version: 1.0.0

resolution_strategies:
  default: conservative
  options:
    - conservative
    - balanced
    - aggressive

conflict_detection:
  check_transitive: true
  max_depth: 10
  ignore_dev_dependencies: false

vulnerability_integration:
  enabled: true
  fail_on_high_severity: true
```

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `resolution_strategies.default` | Default resolution strategy | `conservative` |
| `conflict_detection.check_transitive` | Check transitive dependencies | `true` |
| `conflict_detection.max_depth` | Maximum graph traversal depth | `10` |
| `vulnerability_integration.enabled` | Enable vulnerability checking | `true` |

## GitHub Actions Integration

### Workflow Example

```yaml
name: Dependency Conflict Check

on:
  pull_request:
    paths:
      - 'requirements.txt'
      - 'package.json'
      - 'Cargo.toml'
      - 'go.mod'

jobs:
  resolve-conflicts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Resolve Dependency Conflicts
        uses: ./.github/agents/dependency-conflict-resolver
        with:
          ecosystem: auto-detect
          strategy: balanced
          check-vulnerabilities: true
          fail-on-conflicts: true
```

### Action Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `ecosystem` | Target ecosystem or auto-detect | No | `auto-detect` |
| `strategy` | Resolution strategy | No | `conservative` |
| `check-vulnerabilities` | Enable vulnerability checks | No | `true` |
| `auto-apply` | Automatically apply fixes | No | `false` |

### Action Outputs

| Output | Description |
|--------|-------------|
| `conflicts-found` | Number of conflicts detected |
| `conflicts-resolved` | Number of conflicts resolved |
| `resolution-plan` | Path to resolution plan file |
| `validation-status` | Validation result (passed/failed) |

## Component Reuse

This agent leverages 60% component reuse from existing agents:

### Base Component: dependency-vulnerability-scanner (60%)
- Dependency parsing logic
- Vulnerability checking
- Security assessment

### Extension 1: config-migration-assistant
- Version resolution algorithms
- Constraint solving
- Migration planning

### Extension 2: semantic-search
- Dependency graph analysis
- Relationship mapping
- Pattern detection

## API Usage

### Python API

```python
from agent import DependencyConflictResolver, ResolutionStrategy

# Initialize resolver
resolver = DependencyConflictResolver()

# Parse dependencies
deps = resolver.parse_dependency_file(Path('requirements.txt'))

# Build graph
graph = resolver.build_dependency_graph(deps)

# Detect conflicts
conflicts = resolver.detect_conflicts()

# Generate resolution plan
report = resolver.generate_resolution_plan()

# Resolve with specific strategy
plan = resolver.resolve_conflicts(ResolutionStrategy.BALANCED)

# Apply resolution
success = resolver.apply_resolution(plan)

# Validate
valid, errors = resolver.validate_resolution()
```

## Testing

The agent includes 20+ comprehensive tests:

```bash
# Run unit tests
python -m pytest tests/test_agent.py -v

# Run integration tests
python -m pytest tests/test_integration.py -v

# Run all tests with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Test Coverage

- ✅ Agent initialization and configuration
- ✅ Dependency parsing (Python, JS, Rust, Go)
- ✅ Dependency graph building
- ✅ Conflict detection (direct, transitive, circular)
- ✅ Resolution strategies
- ✅ Semantic versioning
- ✅ Vulnerability integration
- ✅ End-to-end workflows
- ✅ Graph visualization

## Success Criteria

- ✅ **20+ comprehensive tests** covering all functionality
- ✅ **Multi-ecosystem support** for Python, JavaScript, Rust, Go
- ✅ **Conflict resolution** with multiple strategies
- ✅ **Security integration** with vulnerability scanning
- ✅ **Graph analysis** for transitive dependencies
- ✅ **Complete documentation** (30-40KB)

## Advanced Usage

### Custom Resolution Strategy

```python
# Create custom resolution logic
def custom_strategy(conflict):
    # Your custom logic here
    return selected_version

resolver = DependencyConflictResolver()
# Apply custom strategy
```

### Programmatic Graph Analysis

```python
# Analyze specific dependency path
resolver = DependencyConflictResolver()
deps = resolver.parse_dependency_file(Path('requirements.txt'))
graph = resolver.build_dependency_graph(deps)

# Find all paths to a specific package
def find_paths(graph, target, path=[]):
    for node in graph:
        if target in graph[node]:
            yield path + [node, target]
```

### Batch Processing

```bash
# Process multiple files
for file in requirements*.txt; do
    python src/agent.py detect --file "$file"
done
```

## Troubleshooting

### Common Issues

**Issue**: "Cannot detect ecosystem for file"
- **Solution**: Specify ecosystem explicitly: `--ecosystem python`

**Issue**: "Circular dependency detected"
- **Solution**: Review dependency graph, remove circular references manually

**Issue**: "Resolution validation failed"
- **Solution**: Check resolution plan, may require manual intervention

## Contributing

Contributions are welcome! Please ensure:
- All tests pass
- New features include tests
- Documentation is updated
- Code follows existing style

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Open an issue on GitHub
- Contact the Codex team
- See documentation at `.github/agents/dependency-conflict-resolver/prompts/`

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.
