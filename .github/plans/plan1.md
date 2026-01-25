# REFACTORED_PYTHON_312_ONLY_PLANSET.md - Part 1 of 6 

> **Generated**: 2026-01-25T23:45:00Z  
> **Author**: mbaetiong  
> **Purpose**: CI/CD Pipeline & Documentation Enhancement - Python 3.12 Single Version Focus  
> **Repository**: Aries-Serpent/_codex_  
> **PR**: #2968  
> **Python Version**: 3.12.10 (ONLY)

---

## 🎯 Executive Summary

### What Changed from Original Planset

**BEFORE** (Multi-Version Approach):
- Supported Python 3.11, 3.12, and tracked 3.13-dev
- Cross-version compatibility testing
- Migration pathways from 3.11 → 3.12
- Backward compatibility concerns

**AFTER** (Single Version - Python 3.12 ONLY):
- **Python 3.12.10** is the ONLY supported version
- Single-version CI/CD pipeline
- No backward compatibility with 3.11
- No forward compatibility tracking for 3.13
- Simplified development and testing

### Why Single Version?

**Technical Reasons**:
- Reduces CI/CD complexity and execution time
- Eliminates version-specific bugs and edge cases
- Enables use of Python 3.12-specific features without compromise
- Clearer dependency management (no version matrices)

**Operational Reasons**:
- Faster developer onboarding (one environment setup)
- Reduced maintenance burden
- Clearer error messages (no "which Python version?" debugging)
- Simplified documentation

**Strategic Reasons**:
- Modern Python features available (PEP 701, 695, etc.)
- Industry standard moving to 3.12+ (3.11 EOL: Oct 2027)
- Cloud providers defaulting to 3.12

---

## 📋 Document Structure

### Phase 1: Diagnostic & Environment Validation (30 min)
**Focus**: Verify Python 3.12 environment is correctly established

### Phase 2: Python 3.12 Compliance Analysis (30 min)
**Focus**: Identify code/dependencies not fully Python 3.12 compatible

### Phase 3: Python 3.12 Standardization Implementation (45 min)
**Focus**: Apply fixes to achieve 100% Python 3.12 compliance

### Phase 4: Single-Version CI/CD Validation (50 min)
**Focus**: Ensure all CI checks pass with Python 3.12 only

### Phase 5: Python 3.12 Adoption Retrospective (60 min)
**Focus**: Document learnings and establish governance

### Phase 6: Python 3.12 Governance & Enforcement (80 min)
**Focus**: Prevent version drift through automation and policy

---

## 🧠 Agent Configuration

### Roles
- **Primary**: Python 3.12 Compliance Engineer
- **Secondary**: CI/CD Simplification Specialist

### Energy Level: ⚡⚡⚡⚡⚡ (5/5)
*Maximum focus on single-version excellence*

### ⚛️ Physics Principles

**Path 🛤️**: Standardization through elimination
```
Multi-Version Complexity → Python 3.12 Only → Simplified CI → Faster Feedback → Higher Quality
         ↓                        ↓                ↓                 ↓                 ↓
   Matrix Testing          Single Test Run    -60% CI Time      <5 min builds    Zero version bugs
   Version Conditionals    Clean Code         Simpler Logs      Clear Errors     Maintainable
```

**Fields 🔄**: Single-version optimization domains
- **Code Domain**: Python 3.12 syntax exclusively (no `if sys.version_info` checks)
- **Dependency Domain**: Python 3.12 compatible packages only
- **CI/CD Domain**: Single Python version, no matrix
- **Documentation Domain**: One setup guide, one troubleshooting section
- **Developer Domain**: One environment, one workflow

**Patterns 👁️**: Simplification patterns
- Elimination pattern: Remove unnecessary complexity
- Standardization pattern: One way to do things
- Enforcement pattern: Automated validation gates
- Documentation pattern: Single source of truth

**Redundancy 🔀**: Validation layers (even with single version)
- Local pre-commit checks (Python 3.12 validation)
- CI Python version verification
- Dockerfile Python version lock
- Documentation Python version statement
- Policy enforcement (reject PRs using wrong version)

**Balance ⚖**: Simplicity vs. Future-proofing
- 95% focus: Python 3.12 excellence now
- 5% attention: Easy path to 3.13+ when needed
- No support: Python 3.11 or earlier (hard line)

---

# PHASE 1: Diagnostic & Environment Validation

> **Duration**: 30 minutes  
> **Energy**: ⚡⚡⚡⚡  
> **Objective**: Verify Python 3.12.10 is correctly established as the ONLY Python version across all systems

---

## Task 1.1: Python Version Audit (10 minutes)

### 1.1.1: Verify Local Environment

**Check System Python**:
```bash
# Verify Python version
python --version
# Expected output: Python 3.12.10

# Verify no other Python versions in PATH
which -a python python3
# Expected: Only Python 3.12.10 paths

# Check virtual environment (if using venv)
python -c "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"
# Expected output: Python 3.12.10

# Verify pip matches Python version
python -m pip --version
# Expected: pip XX.X.X from .../python3.12/...
```

**Check pyenv Configuration** (if using pyenv):
```bash
# Verify pyenv Python version
pyenv version
# Expected: 3.12.10 (set by ...)

# Check available versions
pyenv versions
# Expected: Only 3.12.10 should be active (marked with *)

# Verify global setting
cat ~/.pyenv/version
# Expected: 3.12.10
```

**Validation Checklist**:
```markdown
- [ ] `python --version` returns `Python 3.12.10`
- [ ] No Python 3.11 or earlier in PATH
- [ ] No Python 3.13+ in PATH (unless intentionally testing future)
- [ ] Virtual environment uses Python 3.12.10
- [ ] pip is from Python 3.12.10 site-packages
```

---

### 1.1.2: Verify Repository Configuration

**Check Configuration Files**:
```bash
# pyproject.toml - Python version requirement
grep -A5 "requires-python" pyproject.toml
# Expected: requires-python = ">=3.12,<3.13"
# OR: requires-python = "==3.12.*"

# .python-version - pyenv configuration
cat .python-version
# Expected: 3.12.10

# runtime.txt - Heroku/Cloud deployment
cat runtime.txt
# Expected: python-3.12.10

# Dockerfile - Container Python version
grep "FROM python" Dockerfile
# Expected: FROM python:3.12.10-slim
# OR: FROM python:3.12-alpine
```

**Validation Script**:
```python
#!/usr/bin/env python3
"""
Verify Python 3.12 is the ONLY version configured across the repository.
"""
import sys
import re
from pathlib import Path

def check_python_version():
    """Verify current Python is 3.12.x"""
    version = sys.version_info
    if version.major != 3 or version.minor != 12:
        print(f"❌ ERROR: Python {version.major}.{version.minor}.{version.micro} detected")
        print(f"   Expected: Python 3.12.x")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def check_pyproject_toml():
    """Verify pyproject.toml requires Python 3.12 only"""
    pyproject = Path("pyproject.toml")
    if not pyproject.exists():
        print("⚠️  pyproject.toml not found")
        return True
    
    content = pyproject.read_text()
    
    # Check requires-python
    if 'requires-python' in content:
        match = re.search(r'requires-python\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            requirement = match.group(1)
            
            # Acceptable patterns:
            # - ">=3.12,<3.13"
            # - "==3.12.*"
            # - "^3.12"
            
            if "3.11" in requirement:
                print(f"❌ ERROR: pyproject.toml allows Python 3.11")
                print(f"   Found: requires-python = \"{requirement}\"")
                print(f"   Fix: requires-python = \">=3.12,<3.13\"")
                return False
            
            if "3.13" in requirement and ">=" not in requirement:
                print(f"⚠️  WARNING: pyproject.toml may allow Python 3.13")
                print(f"   Found: requires-python = \"{requirement}\"")
            
            print(f"✅ pyproject.toml: requires-python = \"{requirement}\"")
    
    return True

def check_python_version_file():
    """Verify .python-version specifies 3.12.x"""
    version_file = Path(".python-version")
    if not version_file.exists():
        print("⚠️  .python-version not found (optional)")
        return True
    
    version = version_file.read_text().strip()
    
    if not version.startswith("3.12"):
        print(f"❌ ERROR: .python-version specifies Python {version}")
        print(f"   Expected: 3.12.x")
        return False
    
    print(f"✅ .python-version: {version}")
    return True

def check_dockerfile():
    """Verify Dockerfile uses Python 3.12"""
    dockerfile = Path("Dockerfile")
    if not dockerfile.exists():
        print("⚠️  Dockerfile not found (optional)")
        return True
    
    content = dockerfile.read_text()
    
    # Find FROM python: lines
    python_images = re.findall(r'FROM python:([^\s]+)', content)
    
    if not python_images:
        print("⚠️  No Python base image found in Dockerfile")
        return True
    
    for image in python_images:
        if not image.startswith("3.12"):
            print(f"❌ ERROR: Dockerfile uses Python {image}")
            print(f"   Expected: 3.12.x")
            return False
        
        print(f"✅ Dockerfile: FROM python:{image}")
    
    return True

def check_github_workflows():
    """Verify GitHub Actions workflows use Python 3.12 only"""
    workflows_dir = Path(".github/workflows")
    if not workflows_dir.exists():
        print("⚠️  .github/workflows not found")
        return True
    
    issues = []
    
    for workflow_file in workflows_dir.glob("*.yml"):
        content = workflow_file.read_text()
        
        # Check for python-version matrix or explicit versions
        # Look for patterns like:
        # python-version: ["3.11", "3.12"]
        # python-version: [3.11, 3.12]
        # python-version: "3.11"
        
        # Find all python-version specifications
        version_specs = re.findall(r'python-version:\s*(.+)', content)
        
        for spec in version_specs:
            # Check for array/list syntax
            if '[' in spec:
                # Extract versions from array
                versions = re.findall(r'["\']?(\d+\.\d+)["\']?', spec)
                for version in versions:
                    if version != "3.12":
                        issues.append(f"{workflow_file.name}: python-version includes {version}")
            else:
                # Single version specified
                version_match = re.search(r'["\']?(\d+\.\d+)["\']?', spec)
                if version_match:
                    version = version_match.group(1)
                    if version != "3.12":
                        issues.append(f"{workflow_file.name}: python-version = {version}")
    
    if issues:
        print(f"❌ ERROR: GitHub workflows use non-3.12 Python versions:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    
    print(f"✅ GitHub workflows: All use Python 3.12 only")
    return True

def main():
    """Run all validation checks"""
    print("🔍 Python 3.12 Single Version Validation\n")
    
    checks = [
        ("Current Python version", check_python_version),
        ("pyproject.toml configuration", check_pyproject_toml),
        (".python-version file", check_python_version_file),
        ("Dockerfile configuration", check_dockerfile),
        ("GitHub Actions workflows", check_github_workflows),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n📋 Checking: {name}")
        print("-" * 60)
        results.append(check_func())
    
    print("\n" + "=" * 60)
    
    if all(results):
        print("✅ All checks passed! Python 3.12 is correctly configured.")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

**Execute Validation**:
```bash
python scripts/validate_python312_only.py
```

**Expected Output**:
```
🔍 Python 3.12 Single Version Validation

📋 Checking: Current Python version
------------------------------------------------------------
✅ Python 3.12.10 detected

📋 Checking: pyproject.toml configuration
------------------------------------------------------------
✅ pyproject.toml: requires-python = ">=3.12,<3.13"

📋 Checking: .python-version file
------------------------------------------------------------
✅ .python-version: 3.12.10

📋 Checking: Dockerfile configuration
------------------------------------------------------------
✅ Dockerfile: FROM python:3.12.10-slim

📋 Checking: GitHub Actions workflows
------------------------------------------------------------
✅ GitHub workflows: All use Python 3.12 only

============================================================
✅ All checks passed! Python 3.12 is correctly configured.
```

---

### 1.1.3: Identify Version Drift Issues

**Search for Multi-Version Code**:
```bash
# Find sys.version_info checks (version-specific code paths)
rg "sys\.version_info" --type py

# Find Python version conditionals
rg "if.*python_version|PYTHON_VERSION" --type py -i

# Find deprecated version compatibility imports
rg "try:.*import.*except.*import" --type py -A 2

# Example issues to fix:
# BEFORE (multi-version):
# if sys.version_info >= (3, 12):
#     from new_module import feature
# else:
#     from old_module import feature
#
# AFTER (Python 3.12 only):
# from new_module import feature  # Python 3.12+ only
```

**Search for Version-Specific Comments**:
```bash
# Find comments referencing multiple Python versions
rg "Python 3\.11|python 3\.11|py311|3\.11" --type py -i
rg "Python 3\.13|python 3\.13|py313|3\.13" --type py -i

# Examples to clean up:
# "Compatible with Python 3.11 and 3.12" → "Requires Python 3.12+"
# "TODO: Remove when dropping 3.11" → (just remove the code)
# "Fallback for Python <3.12" → (delete fallback, keep 3.12 code)
```

**Document Findings**:
```markdown
## Python Version Drift Audit Results

### Issues Found

1. **File**: `src/codex/utils/compat.py`
   - **Issue**: Contains `sys.version_info` checks for 3.11 vs 3.12
   - **Line**: 45-52
   - **Action**: Remove conditional, keep Python 3.12 code only

2. **File**: `.github/workflows/comprehensive_tests.yml`
   - **Issue**: Matrix includes Python 3.11
   - **Line**: 23-25
   - **Action**: Remove matrix, hardcode Python 3.12.10

3. **File**: `docs/CONTRIBUTING.md`
   - **Issue**: Instructions mention "Python 3.11 or 3.12"
   - **Line**: 78
   - **Action**: Update to "Python 3.12.10 required"

### Summary
- **Total Files with Issues**: 3
- **Critical Issues**: 1 (CI workflow)
- **Documentation Issues**: 1
- **Code Issues**: 1
```

---

## Task 1.2: Dependency Compatibility Audit (10 minutes)

### 1.2.1: Check All Dependencies for Python 3.12 Support

**Audit Script**:
```python
#!/usr/bin/env python3
"""
Verify all dependencies support Python 3.12 ONLY.
"""
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib

def parse_dependencies():
    """Extract dependencies from pyproject.toml"""
    pyproject = Path("pyproject.toml")
    data = tomllib.loads(pyproject.read_text())
    
    deps = data.get("project", {}).get("dependencies", [])
    optional = data.get("project", {}).get("optional-dependencies", {})
    
    all_deps = []
    
    # Parse main dependencies
    for dep in deps:
        # Remove version specifiers
        package = dep.split("[")[0].split(">=")[0].split("==")[0].split("<")[0].split(">")[0].strip()
        all_deps.append((package, "main", dep))
    
    # Parse optional dependencies
    for group, group_deps in optional.items():
        for dep in group_deps:
            package = dep.split("[")[0].split(">=")[0].split("==")[0].split("<")[0].split(">")[0].strip()
            all_deps.append((package, f"optional:{group}", dep))
    
    return all_deps

def check_package_python312(package: str) -> dict:
    """Check if package supports Python 3.12"""
    try:
        # Get package metadata from PyPI
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", package],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return {"supported": None, "error": "Package not installed"}
        
        # Check if package has Python version requirements
        metadata = result.stdout
        
        # Look for "Requires-Python" line
        for line in metadata.split("\n"):
            if line.startswith("Requires-Python:"):
                requires = line.split(":", 1)[1].strip()
                
                # Check if Python 3.12 is supported
                # Simple check: if requirement includes ">=3.12" or doesn't restrict upper bound
                if "3.13" in requires or "3.14" in requires:
                    return {"supported": True, "requires": requires, "note": "May support 3.13+"}
                elif ">=3.12" in requires or ">3.11" in requires:
                    return {"supported": True, "requires": requires}
                elif "<3.12" in requires or "<=3.11" in requires:
                    return {"supported": False, "requires": requires, "error": "Python 3.12 not supported"}
                else:
                    return {"supported": True, "requires": requires, "note": "No upper bound"}
        
        # No Requires-Python specified - assume compatible
        return {"supported": True, "requires": "Not specified"}
    
    except Exception as e:
        return {"supported": None, "error": str(e)}

def main():
    print("🔍 Dependency Python 3.12 Compatibility Check\n")
    
    dependencies = parse_dependencies()
    
    print(f"Found {len(dependencies)} dependencies to check\n")
    
    issues = []
    warnings = []
    
    for package, group, full_spec in dependencies:
        result = check_package_python312(package)
        
        status = "✅" if result["supported"] else "❌" if result["supported"] is False else "⚠️"
        
        print(f"{status} {package} ({group})")
        
        if result.get("requires"):
            print(f"   Requires-Python: {result['requires']}")
        
        if result.get("note"):
            print(f"   Note: {result['note']}")
            warnings.append(f"{package}: {result['note']}")
        
        if result.get("error"):
            print(f"   Error: {result['error']}")
            if result["supported"] is False:
                issues.append(f"{package}: {result['error']}")
        
        print()
    
    print("=" * 60)
    
    if issues:
        print(f"\n❌ {len(issues)} package(s) incompatible with Python 3.12:")
        for issue in issues:
            print(f"   - {issue}")
        return 1
    
    if warnings:
        print(f"\n⚠️  {len(warnings)} package(s) with notes:")
        for warning in warnings:
            print(f"   - {warning}")
    
    print("\n✅ All dependencies support Python 3.12!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

**Execute Check**:
```bash
python scripts/check_python312_dependencies.py
```

---

### 1.2.2: Update Incompatible Dependencies

**If Issues Found**:
```bash
# For each incompatible dependency, check for updates
pip index versions <package-name>

# Update to compatible version
pip install --upgrade <package-name>

# Update pyproject.toml with new version constraint
# BEFORE: package>=1.0.0,<2.0.0
# AFTER:  package>=1.5.0,<2.0.0  # 1.5.0+ supports Python 3.12
```

**Regenerate Lock File**:
```bash
# If using pip-tools
pip-compile pyproject.toml --upgrade

# If using poetry
poetry lock --no-update

# If using pipenv
pipenv lock

# Verify all dependencies install cleanly
pip install -e ".[dev,test]"
```

---

## Task 1.3: CI/CD Pipeline Audit (10 minutes)

### 1.3.1: Review GitHub Actions Workflows

**Check All Workflow Files**:
```bash
# List all workflows
ls -la .github/workflows/

# Check each for Python version specifications
for file in .github/workflows/*.yml; do
    echo "=== $file ==="
    grep -A 3 "python-version" "$file" || echo "No python-version found"
    echo ""
done
```

**Expected Issues to Fix**:
```yaml
# BEFORE (Multi-version matrix):
strategy:
  matrix:
    python-version: ["3.11", "3.12"]

# AFTER (Python 3.12 only):
# Remove matrix entirely, use single version:
- uses: actions/setup-python@v5
  with:
    python-version: "3.12.10"
```

---

### 1.3.2: Simplify CI Workflows

**Workflow Simplification Checklist**:
```markdown
## Workflow Simplification Plan

### Files to Modify

1. **`.github/workflows/comprehensive_tests.yml`**
   - [x] Remove `strategy.matrix.python-version`
   - [x] Hardcode `python-version: "3.12.10"`
   - [x] Update job names (remove version suffix)
   - [x] Simplify artifact names (no version number needed)

2. **`.github/workflows/test-rag.yml`**
   - [x] Remove matrix
   - [x] Hardcode Python 3.12.10
   - [x] Single test run instead of parallel

3. **`.github/workflows/rust_swarm_ci.yml`**
   - [x] Verify Python version for Rust/Python integration
   - [x] Ensure uses Python 3.12.10

### Expected CI Time Savings
- **Before**: 2 parallel jobs (3.11 + 3.12) = 6 min each = 12 min total
- **After**: 1 job (3.12 only) = 6 min total
- **Savings**: 50% CI time reduction
```

---

## Task 1.4: Documentation Audit (5 minutes)

### 1.4.1: Update All Documentation

**Files to Review**:
```bash
# Find all documentation mentioning Python versions
rg "Python 3\.(11|13)|python 3\.(11|13)|3\.(11|13)" \
   --type md \
   --type rst \
   --type txt \
   -l

# Common files requiring updates:
# - README.md
# - CONTRIBUTING.md
# - docs/installation.md
# - docs/development.md
# - AGENTS.md
```

**Documentation Update Template**:
```markdown
<!-- BEFORE -->
## Requirements
- Python 3.11 or 3.12
- pip 23.0+

<!-- AFTER -->
## Requirements
- **Python 3.12.10** (REQUIRED - no other versions supported)
- pip 23.0+

## Installation

### Step 1: Verify Python Version
\`\`\`bash
python --version
# Must output: Python 3.12.10
\`\`\`

If you don't have Python 3.12.10:
- **macOS**: `brew install python@3.12`
- **Ubuntu**: `sudo apt install python3.12`
- **Windows**: Download from [python.org](https://www.python.org/downloads/)

### Step 2: Install Package
\`\`\`bash
pip install -e ".[dev,test]"
\`\`\`
```

---

## Phase 1 Deliverables

### ✅ Checklist

- [ ] **Python version validation script** executed successfully
- [ ] **Dependency compatibility check** passed (all deps support 3.12)
- [ ] **Version drift audit** completed (all multi-version code identified)
- [ ] **CI/CD workflows** audited (matrix strategies identified)
- [ ] **Documentation** audited (version references cataloged)
- [ ] **Findings document** created with all issues listed

### 📊 Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Python version consistency | 100% | ⬜ TBD |
| Dependencies compatible | 100% | ⬜ TBD |
| CI workflows simplified | All | ⬜ TBD |
| Documentation updated | All files | ⬜ TBD |

### 📁 Artifacts

1. `analysis/phase1/python312_validation_report.json`
2. `analysis/phase1/dependency_compatibility_report.txt`
3. `analysis/phase1/version_drift_issues.md`
4. `analysis/phase1/ci_workflow_audit.md`
5. `analysis/phase1/documentation_updates_needed.md`

---

**End of Phase 1 - Part 1 of 6**

**Next**: Part 2 of 6 - Phase 2: Python 3.12 Compliance Analysis