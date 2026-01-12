# Dependency Conflict Resolver - Usage Examples

This document provides comprehensive examples of using the Dependency Conflict Resolver Agent across different scenarios and ecosystems.

## Example 1: Resolve Python Requirements Conflict

### Scenario
Your Python project has conflicting version requirements for the `requests` library in `requirements.txt`.

### Input File (requirements.txt)
```
# Web framework
django==4.1.0
djangorestframework>=3.14.0

# HTTP client - version 1
requests>=2.20.0
beautifulsoup4>=4.11.0

# Data processing
pandas>=1.5.0
numpy>=1.23.0

# HTTP client - version 2 (conflict!)
requests>=2.28.0

# Testing
pytest>=7.2.0
pytest-cov>=4.0.0
```

### Detection

```bash
$ python src/agent.py detect --file requirements.txt
```

**Output:**
```
🔍 Dependency Conflict Resolver v1.0.0

📦 Parsing Python dependencies from requirements.txt...
   Found 10 dependencies

🔨 Building dependency graph...
   Graph: 10 nodes, 0 edges (no transitive dependencies provided)

⚠️  Conflicts Detected: 1

┌─────────────────────────────────────────────────────────────┐
│ Conflict #1: requests                                        │
├─────────────────────────────────────────────────────────────┤
│ Type: DIRECT                                                 │
│ Severity: Medium                                             │
│                                                              │
│ Conflicting Versions:                                        │
│   • Line 8:  requests>=2.20.0                               │
│   • Line 17: requests>=2.28.0                               │
│                                                              │
│ Description:                                                 │
│   Multiple incompatible version constraints for 'requests'   │
│                                                              │
│ Suggested Resolution:                                        │
│   Update to requests>=2.28.0 (satisfies both constraints)   │
└─────────────────────────────────────────────────────────────┘

Summary: 1 conflict detected, 0 circular dependencies
```

### Resolution

```bash
$ python src/agent.py resolve --strategy conservative --file requirements.txt
```

**Output:**
```
📋 Generating Resolution Plan (Conservative Strategy)...

Resolution Plan
═══════════════════════════════════════════════════════════

Strategy: Conservative
Conflicts to Resolve: 1
Estimated Risk: Low

Actions:
────────────────────────────────────────────────────────────
1. Update 'requests' version
   Package: requests
   From: Multiple constraints (>=2.20.0, >=2.28.0)
   To: ==2.28.0
   Reason: Minimum version satisfying all constraints
   Risk: Low (minor version bump, backward compatible)
   Security: ✅ No known vulnerabilities
   Files:
     • requirements.txt (line 8)
     • requirements.txt (line 17)

────────────────────────────────────────────────────────────

💾 Resolution plan saved to: resolution-plan.yaml

Next steps:
  1. Review the plan above
  2. Run 'python src/agent.py apply --plan resolution-plan.yaml' to apply
  3. Run your tests to verify compatibility
```

### Application

```bash
$ python src/agent.py apply --plan resolution-plan.yaml
```

**Output:**
```
🔧 Applying Resolution Plan...

✅ Updated requirements.txt (line 8): requests>=2.28.0
✅ Removed duplicate at line 17

✅ Resolution applied successfully!

⚠️  Recommended: Run your test suite to verify compatibility
   $ pytest tests/
```

---

## Example 2: Fix npm Package Version Mismatch

### Scenario
A JavaScript project has conflicting dependencies between main and dev dependencies.

### Input File (package.json)
```json
{
  "name": "my-web-app",
  "version": "1.0.0",
  "dependencies": {
    "express": "^4.17.1",
    "lodash": "^4.17.19",
    "axios": "^0.21.1",
    "moment": "^2.29.1"
  },
  "devDependencies": {
    "jest": "^27.0.0",
    "eslint": "^8.0.0",
    "axios": "^1.3.0"
  }
}
```

### Detection and Resolution

```bash
$ python src/agent.py detect --file package.json
```

**Output:**
```
🔍 Analyzing JavaScript dependencies from package.json...

📦 Parsed dependencies:
   • 4 production dependencies
   • 3 development dependencies

⚠️  Conflicts Detected: 1

┌─────────────────────────────────────────────────────────────┐
│ Conflict #1: axios                                           │
├─────────────────────────────────────────────────────────────┤
│ Type: DIRECT                                                 │
│ Severity: High (major version difference)                    │
│                                                              │
│ Conflicting Versions:                                        │
│   • dependencies: ^0.21.1 (v0.x)                            │
│   • devDependencies: ^1.3.0 (v1.x)                          │
│                                                              │
│ Impact: Major version mismatch may cause API incompatibility │
│                                                              │
│ Suggested Resolution (Aggressive):                           │
│   Update all to ^1.3.0 (latest stable)                      │
│                                                              │
│ Security Note: axios v0.21.1 has known vulnerabilities!      │
│   CVE-2021-3749: SSRF vulnerability                         │
│   Recommendation: Upgrade to v1.3.0+                         │
└─────────────────────────────────────────────────────────────┘

🛡️  Security Check: 1 vulnerability found
```

```bash
$ python src/agent.py resolve --strategy aggressive --file package.json
```

**Resolution Applied:**
```json
{
  "dependencies": {
    "express": "^4.17.1",
    "lodash": "^4.17.19",
    "axios": "^1.3.0",
    "moment": "^2.29.1"
  },
  "devDependencies": {
    "jest": "^27.0.0",
    "eslint": "^8.0.0",
    "axios": "^1.3.0"
  }
}
```

---

## Example 3: Rust Cargo.toml Conflicts

### Scenario
A Rust project has conflicting feature requirements for `tokio`.

### Input File (Cargo.toml)
```toml
[package]
name = "my-rust-app"
version = "0.1.0"
edition = "2021"

[dependencies]
tokio = { version = "1.25", features = ["fs", "io-util"] }
reqwest = { version = "0.11", features = ["json"] }
serde = { version = "1.0", features = ["derive"] }

[dev-dependencies]
tokio = { version = "1.28", features = ["full"] }
```

### Detection

```bash
$ python src/agent.py detect --file Cargo.toml
```

**Output:**
```
🔍 Analyzing Rust dependencies from Cargo.toml...

⚠️  Conflicts Detected: 1

┌─────────────────────────────────────────────────────────────┐
│ Conflict #1: tokio                                           │
├─────────────────────────────────────────────────────────────┤
│ Type: DIRECT (dependencies vs dev-dependencies)              │
│ Severity: Medium                                             │
│                                                              │
│ Conflicting Versions:                                        │
│   • [dependencies]: 1.25 with features ["fs", "io-util"]    │
│   • [dev-dependencies]: 1.28 with features ["full"]         │
│                                                              │
│ Analysis:                                                    │
│   Different versions between main and dev dependencies       │
│                                                              │
│ Suggested Resolution (Balanced):                             │
│   Use tokio = "1.28" for both, merge features               │
│   Production: ["fs", "io-util"]                             │
│   Development: ["full"] (includes all features)              │
└─────────────────────────────────────────────────────────────┘
```

### Resolution

```bash
$ python src/agent.py resolve --strategy balanced --file Cargo.toml
```

**Resolved Cargo.toml:**
```toml
[dependencies]
tokio = { version = "1.28", features = ["fs", "io-util"] }
reqwest = { version = "0.11", features = ["json"] }
serde = { version = "1.0", features = ["derive"] }

[dev-dependencies]
tokio = { version = "1.28", features = ["full"] }
```

---

## Example 4: Multi-Ecosystem Project

### Scenario
A full-stack project with both Python (backend) and JavaScript (frontend) dependencies.

### Project Structure
```
my-project/
├── backend/
│   └── requirements.txt
├── frontend/
│   └── package.json
└── resolve-all.sh
```

### Script (resolve-all.sh)
```bash
#!/bin/bash

echo "🔍 Checking all dependency files..."

# Check Python backend
echo "\n📦 Backend (Python):"
python src/agent.py detect --file backend/requirements.txt

# Check JavaScript frontend  
echo "\n📦 Frontend (JavaScript):"
python src/agent.py detect --file frontend/package.json

# Generate combined report
echo "\n📊 Generating multi-ecosystem report..."
python src/agent.py multi-report --files backend/requirements.txt,frontend/package.json
```

**Output:**
```
🔍 Multi-Ecosystem Analysis Report
═══════════════════════════════════════════════════════════

Ecosystems Analyzed: 2 (Python, JavaScript)
Total Dependencies: 23
  • Python: 12 dependencies
  • JavaScript: 11 dependencies

Conflicts Found: 0
Circular Dependencies: 0
Security Vulnerabilities: 1

┌─────────────────────────────────────────────────────────────┐
│ Security Alert: Frontend                                     │
├─────────────────────────────────────────────────────────────┤
│ Package: axios@0.21.1                                        │
│ Vulnerability: CVE-2021-3749 (SSRF)                         │
│ Severity: High                                               │
│ Recommendation: Update to axios@1.3.0 or later              │
└─────────────────────────────────────────────────────────────┘

✅ Overall Health: Good (pending security update)
```

---

## Example 5: Security-Aware Resolution

### Scenario
Resolve conflicts while prioritizing security patches.

### Command
```bash
$ python src/agent.py resolve \
    --strategy balanced \
    --file requirements.txt \
    --prioritize-security \
    --fail-on-high-severity
```

### Input
```
django==3.2.0
requests>=2.20.0
urllib3>=1.26.0
```

### Output
```
🛡️  Security-Aware Resolution (Balanced Strategy)

Vulnerability Scan Results:
───────────────────────────────────────────────────────────
❌ django 3.2.0
   CVE-2023-12345: SQL Injection vulnerability
   Severity: High
   Fixed in: 3.2.18

⚠️  requests 2.20.0  
   CVE-2022-67890: Certificate validation bypass
   Severity: Medium
   Fixed in: 2.27.1

✅ urllib3 1.26.0
   No known vulnerabilities

Resolution Plan (Security Priority):
───────────────────────────────────────────────────────────
1. django: 3.2.0 → 3.2.18 (SECURITY PATCH)
   Fixes: CVE-2023-12345 (High)
   
2. requests: 2.20.0 → 2.27.1 (SECURITY PATCH)
   Fixes: CVE-2022-67890 (Medium)

3. urllib3: No changes needed

Risk Assessment: Low (only security patches)
Compatibility: High (patch versions maintain backward compatibility)

Apply this resolution? [y/N]:
```

---

## Example 6: CI/CD Integration

### GitHub Actions Workflow

```yaml
name: Dependency Conflict Check

on:
  pull_request:
    paths:
      - '**/requirements.txt'
      - '**/package.json'
      - '**/Cargo.toml'
      - '**/go.mod'
  push:
    branches: [main, develop]

jobs:
  check-dependencies:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Resolve Dependency Conflicts
        id: resolve
        uses: ./.github/agents/dependency-conflict-resolver
        with:
          ecosystem: auto-detect
          strategy: balanced
          check-vulnerabilities: true
          fail-on-conflicts: false
          auto-apply: false
      
      - name: Upload Resolution Plan
        if: steps.resolve.outputs.conflicts-found != '0'
        uses: actions/upload-artifact@v3
        with:
          name: resolution-plan
          path: ${{ steps.resolve.outputs.resolution-plan }}
      
      - name: Comment on PR
        if: github.event_name == 'pull_request' && steps.resolve.outputs.conflicts-found != '0'
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## 🔍 Dependency Conflict Report
              
              **Conflicts Found:** ${{ steps.resolve.outputs.conflicts-found }}
              **Ecosystem:** ${{ steps.resolve.outputs.ecosystem-detected }}
              **Strategy:** balanced
              
              📋 Resolution plan available in artifacts.
              
              To resolve conflicts:
              1. Download the resolution plan artifact
              2. Review the suggested changes
              3. Run: \`python agent.py apply --plan resolution-plan.yaml\`
              `
            })
```

---

## Example 7: Pre-commit Hook Setup

### Setup

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash

echo "🔍 Checking for dependency conflicts..."

# Find all dependency files
PYTHON_FILES=$(find . -name "requirements*.txt" -not -path "./.venv/*")
JS_FILES=$(find . -name "package.json" -not -path "./node_modules/*")

HAS_CONFLICTS=0

# Check Python dependencies
for file in $PYTHON_FILES; do
    if [ -f "$file" ]; then
        echo "Checking $file..."
        python .github/agents/dependency-conflict-resolver/src/agent.py detect --file "$file" --quiet
        if [ $? -ne 0 ]; then
            HAS_CONFLICTS=1
        fi
    fi
done

# Check JavaScript dependencies
for file in $JS_FILES; do
    if [ -f "$file" ]; then
        echo "Checking $file..."
        python .github/agents/dependency-conflict-resolver/src/agent.py detect --file "$file" --quiet
        if [ $? -ne 0 ]; then
            HAS_CONFLICTS=1
        fi
    fi
done

if [ $HAS_CONFLICTS -eq 1 ]; then
    echo ""
    echo "❌ Dependency conflicts detected!"
    echo "   Run 'python agent.py detect --file <file>' for details"
    echo "   Or use 'git commit --no-verify' to bypass this check"
    exit 1
fi

echo "✅ No dependency conflicts detected"
exit 0
```

### Usage

```bash
# Make hook executable
chmod +x .git/hooks/pre-commit

# Now conflicts are checked automatically on commit
git add requirements.txt
git commit -m "Update dependencies"

# Output:
🔍 Checking for dependency conflicts...
Checking ./requirements.txt...
❌ Dependency conflicts detected!
   Run 'python agent.py detect --file requirements.txt' for details
```

---

## Example 8: Programmatic API Usage

### Python Script

```python
#!/usr/bin/env python3
"""
Custom dependency conflict resolution script
"""

from pathlib import Path
from agent import (
    DependencyConflictResolver,
    ResolutionStrategy,
    Ecosystem
)

def main():
    # Initialize resolver
    resolver = DependencyConflictResolver(
        config_path=Path('config/custom_config.yaml')
    )
    
    # Parse dependencies
    print("📦 Parsing dependencies...")
    deps = resolver.parse_dependency_file(Path('requirements.txt'))
    print(f"   Found {len(deps)} dependencies")
    
    # Build graph
    print("🔨 Building dependency graph...")
    graph = resolver.build_dependency_graph(deps)
    print(f"   Graph: {len(graph)} nodes")
    
    # Detect conflicts
    print("🔍 Detecting conflicts...")
    conflicts = resolver.detect_conflicts()
    
    if not conflicts:
        print("✅ No conflicts detected!")
        return 0
    
    print(f"⚠️  Found {len(conflicts)} conflicts:")
    for i, conflict in enumerate(conflicts, 1):
        print(f"   {i}. {conflict.package_name}: {conflict.description}")
    
    # Check vulnerabilities
    print("\n🛡️  Checking for vulnerabilities...")
    vulns = resolver.check_vulnerabilities()
    if vulns:
        print(f"   ⚠️  {len(vulns)} vulnerable packages found")
    
    # Generate resolution plan
    print("\n📋 Generating resolution plan...")
    report = resolver.generate_resolution_plan()
    plan = report.resolution_plan
    
    print(f"   Strategy: {plan.strategy.value}")
    print(f"   Actions: {len(plan.actions)}")
    print(f"   Risk: {plan.estimated_risk}")
    
    # Prompt for confirmation
    if plan.requires_manual_review:
        print("\n⚠️  Manual review required for some conflicts")
        return 1
    
    response = input("\n Apply resolution? [y/N]: ")
    if response.lower() != 'y':
        print("Aborted.")
        return 1
    
    # Apply resolution
    print("\n🔧 Applying resolution...")
    success = resolver.apply_resolution(plan)
    
    if not success:
        print("❌ Failed to apply resolution")
        return 1
    
    # Validate
    print("✔️  Validating...")
    valid, errors = resolver.validate_resolution()
    
    if valid:
        print("✅ Resolution applied successfully!")
        print("\n⚠️  Remember to:")
        print("   1. Review the changes")
        print("   2. Run your test suite")
        print("   3. Commit the updated dependency files")
        return 0
    else:
        print("❌ Validation failed:")
        for error in errors:
            print(f"   - {error}")
        return 1

if __name__ == '__main__':
    exit(main())
```

---

## Quick Reference Commands

```bash
# Detect conflicts
python agent.py detect --file <dependency-file>

# Resolve with strategy
python agent.py resolve --strategy <conservative|balanced|aggressive> --file <file>

# Visualize graph
python agent.py visualize --file <file> --output graph.txt

# Apply resolution plan
python agent.py apply --plan resolution-plan.yaml

# Validate after resolution
python agent.py validate --file <file>

# Generate report
python agent.py report --file <file> --format <json|yaml|text>
```

These examples demonstrate the agent's capabilities across various scenarios and ecosystems. Adapt them to your specific use case!
