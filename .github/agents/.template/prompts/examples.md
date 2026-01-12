# [Agent Name] Examples

## Basic Usage

### Example 1: [Simple Task]
**Scenario**: [Description]

**Command**:
```bash
python src/agent.py --task "example task"
```

**Expected Output**:
```
[Output description]
```

## Intermediate Usage

### Example 2: [Complex Task]
**Scenario**: [Description]

**Command**:
```bash
python src/agent.py --task "complex task" --config custom_config.yaml
```

**Expected Output**:
```
[Output description]
```

## Advanced Usage

### Example 3: [Advanced Scenario]
**Scenario**: [Description]

**Command**:
```bash
python src/agent.py --task "advanced" --verbose --output results.json
```

**Expected Output**:
```
[Output description]
```

## Integration Examples

### Example 4: GitHub Copilot Integration
```
@copilot use [agent-name] to [specific task with context]
```

### Example 5: CI/CD Integration
```yaml
- name: Run [Agent Name]
  run: |
    python .github/agents/[agent-name]/src/agent.py \
      --task "${{ github.event.inputs.task }}"
```
