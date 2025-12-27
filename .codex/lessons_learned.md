# Lessons Learned - AI Agent Knowledge Base

**Total Lessons:** 6
**Last Updated:** 2025-12-26T20:46:37.713433

---

## Api-Access

### GitHub CLI requires explicit token in some environments
*Added: 2025-12-26T20:46:26.336961*

**Problem:**
In automated environments, gh CLI commands may fail even when git operations work. Git uses credential helper but gh requires explicit GITHUB_TOKEN or GH_TOKEN environment variable.

**Solution:**
Workaround 1: Use git commands instead of gh CLI. Workaround 2: Document operations requiring API access. Workaround 3: Request human admin to configure GITHUB_TOKEN. For workflows: Use GitHub Actions context variables.

**Tags:** github-cli, authentication, api-access, workaround

---

### GitHub CLI requires explicit token in some environments
*Added: 2025-12-26T20:46:37.709006*

**Problem:**
In automated environments, gh CLI commands may fail even when git operations work. Git uses credential helper but gh requires explicit GITHUB_TOKEN or GH_TOKEN environment variable.

**Solution:**
Workaround 1: Use git commands instead of gh CLI. Workaround 2: Document operations requiring API access. Workaround 3: Request human admin to configure GITHUB_TOKEN. For workflows: Use GitHub Actions context variables.

**Tags:** github-cli, authentication, api-access, workaround

---

## Dependency-Testing

### pip install hangs with large ML packages
*Added: 2025-12-26T20:46:26.336803*

**Problem:**
When attempting to install packages like torch (2.6.0), transformers (4.48.0), or mlflow (2.22.4) in virtual environment, pip install -e . hangs without output for 180+ seconds

**Solution:**
Use incremental installation: Install packages one at a time with progress indicators. Alternative: Use existing environment or defer to CI/CD pipeline. For future: Add --progress-bar on and --verbose flags to pip commands.

**Tags:** pip, installation, timeout, ml-packages

---

### pip install hangs with large ML packages
*Added: 2025-12-26T20:46:37.708757*

**Problem:**
When attempting to install packages like torch (2.6.0), transformers (4.48.0), or mlflow (2.22.4) in virtual environment, pip install -e . hangs without output for 180+ seconds

**Solution:**
Use incremental installation: Install packages one at a time with progress indicators. Alternative: Use existing environment or defer to CI/CD pipeline. For future: Add --progress-bar on and --verbose flags to pip commands.

**Tags:** pip, installation, timeout, ml-packages

---

## Testing

### JSON serialization fails with Enum objects in dataclasses
*Added: 2025-12-26T20:46:26.337136*

**Problem:**
When using asdict() from dataclasses with Enum fields, json.dump() raises TypeError: Object of type HealthStatus is not JSON serializable

**Solution:**
Create recursive enum_to_value helper function that converts Enum objects to their .value property before serialization. Apply to all dict/list structures before json.dump().

**Tags:** json, enum, serialization, dataclass

---

### JSON serialization fails with Enum objects in dataclasses
*Added: 2025-12-26T20:46:37.709259*

**Problem:**
When using asdict() from dataclasses with Enum fields, json.dump() raises TypeError: Object of type HealthStatus is not JSON serializable

**Solution:**
Create recursive enum_to_value helper function that converts Enum objects to their .value property before serialization. Apply to all dict/list structures before json.dump().

**Tags:** json, enum, serialization, dataclass

---

