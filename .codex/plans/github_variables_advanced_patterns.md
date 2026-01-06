# GitHub Repository Variables - Advanced Implementation Guide
# PR #2685 - Paginated Data, Triggers, and API/Webhook Orchestration

> **Generated**: Current Cycle-01-03T20:04:55Z  
> **Author**: Copilot AI Agent  
> **Branch**: copilot/sub-pr-2682  
> **Purpose**: Advanced GitHub Variables patterns for paginated data, triggers, and autonomous workflow orchestration

---

## 📋 Executive Summary

This document extends the base GitHub Variables implementation plan with advanced patterns for:
1. **Paginated Dataset Storage** - Store large datasets (>48KB) using chunked variables
2. **API/REST Orchestration** - Programmatic variable management via GitHub REST API
3. **Workflow Triggers** - Use variables to gate pre-deploy actions and dispatch events
4. **Cross-Workflow Data Sharing** - Share non-sensitive data across workflows and repositories

**Prerequisites**: Base plan in `github_variables_implementation_plan.md`

---

## 🎯 Part 1: Paginated Dataset Storage Pattern

### 1.1 Chunking Strategy

For datasets exceeding 48KB, use an index + page variables scheme:

| Component | Purpose | Example Variable Name | Size Limit |
|-----------|---------|----------------------|------------|
| Index | Metadata about pages | `DATASET_20260103_INDEX` | < 48KB |
| Page N | Data chunk N | `DATASET_20260103_P001` | ≤ 48KB each |

**Index Schema**:
```json
{
  "dataset_id": "ds-20260103",
  "pages": 5,
  "schema": "json",
  "keys": ["DATASET_20260103_P001", "DATASET_20260103_P002", ...],
  "created_at": "Current Cycle-01-03T12:00:00Z",
  "total_size_bytes": 240000,
  "compression": "none"
}
```

### 1.2 Workflow Writer: Store Paginated Data

**File**: `.github/workflows/store-dataset-pages.yml`

```yaml
name: Store Paginated Dataset

on:
  workflow_dispatch:
    inputs:
      dataset_path:
        description: 'Path to dataset file'
        required: true
        default: 'path/to/output.json'
      dataset_id:
        description: 'Dataset identifier'
        required: true
        default: 'ds-20260103'

jobs:
  store-dataset-pages:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      actions: write
    
    steps:
      - uses: actions/checkout@v4

      - name: Prepare dataset and chunk
        id: chunk
        run: |
          python3 - << 'PY'
          import math, json, os
          
          # Read dataset
          data_path = "${{ github.event.inputs.dataset_path }}"
          with open(data_path, 'rb') as f:
              data = f.read()
          
          # Configuration
          MAX_CHUNK_SIZE = 49152  # 48 KB
          dataset_id = "${{ github.event.inputs.dataset_id }}"
          timestamp = "${{ github.run_started_at }}"
          
          # Calculate pages
          total_size = len(data)
          pages = math.ceil(total_size / MAX_CHUNK_SIZE)
          
          # Create chunks
          chunks = []
          for i in range(pages):
                  start = i * MAX_CHUNK_SIZE
              end = min((i + 1) * MAX_CHUNK_SIZE, total_size)
              chunks.append(data[start:end])
          
          # Generate index
          index = {
              "dataset_id": dataset_id,
              "pages": pages,
              "schema": "json",
              "keys": [f"DATASET_{dataset_id.upper()}_P{str(i+1).zfill(3)}" for i in range(pages)],
              "created_at": timestamp,
              "total_size_bytes": total_size,
              "compression": "none"
          }
          
          # Write index
          with open('index.json', 'w') as f:
              json.dump(index, f, separators=(',', ':'))
          
          # Write pages
          for i, chunk in enumerate(chunks):
              with open(f"page_{i+1:03}.txt", 'wb') as f:
                  f.write(chunk)
          
          print(f"Created {pages} pages totaling {total_size} bytes")
          print(f"::set-output name=pages::{pages}")
          PY

      - name: PUT index variable
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          INDEX_VAR: DATASET_${{ github.event.inputs.dataset_id }}_INDEX
        run: |
          INDEX_VALUE="$(cat index.json)"
          gh variable set "${INDEX_VAR}" --body "${INDEX_VALUE}"

      - name: PUT page variables
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          for f in page_*.txt; do
            PAGE_NUM=$(echo "$f" | sed -E 's/page_0*([0-9]+)\.txt/\1/')
            KEY="DATASET_${{ github.event.inputs.dataset_id }}_P$(printf "%03d" $PAGE_NUM)"
            echo "Uploading ${KEY}..."
            gh variable set "${KEY}" --body "$(cat "$f")"
          done

      - name: Dispatch downstream processing
        run: |
          gh api repos/${{ github.repository }}/dispatches \
            -f event_type="dataset_ready" \
            -f client_payload[index_var]="DATASET_${{ github.event.inputs.dataset_id }}_INDEX" \
            -f client_payload[dataset_id]="${{ github.event.inputs.dataset_id }}"
```

### 1.3 Workflow Reader: Reconstruct Paginated Data

**File**: `.github/workflows/consume-dataset-pages.yml`

```yaml
name: Consume Paginated Dataset

on:
  repository_dispatch:
    types: [dataset_ready]

jobs:
  consume-dataset:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      actions: read
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Read index variable
        id: read_index
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          INDEX_VAR: ${{ github.event.client_payload.index_var }}
        run: |
          echo "Reading index from ${INDEX_VAR}..."
          gh variable get "${INDEX_VAR}" > index.json
          cat index.json | jq .
          
          # Extract page count
          PAGES=$(jq -r '.pages' index.json)
          echo "::set-output name=pages::${PAGES}"

      - name: Fetch and assemble pages
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          # Read page keys from index
          KEYS=$(jq -r '.keys[]' index.json)
          
          # Initialize output
          : > dataset_assembled.txt
          
          # Fetch each page
          for KEY in $KEYS; do
            echo "Fetching ${KEY}..."
            gh variable get "${KEY}" >> dataset_assembled.txt
          done
          
          # Verify size
          EXPECTED_SIZE=$(jq -r '.total_size_bytes' index.json)
          ACTUAL_SIZE=$(wc -c < dataset_assembled.txt)
          echo "Expected: ${EXPECTED_SIZE} bytes, Actual: ${ACTUAL_SIZE} bytes"
          
          if [ "${EXPECTED_SIZE}" -eq "${ACTUAL_SIZE}" ]; then
            echo "✅ Dataset assembled successfully"
          else
            echo "❌ Size mismatch!"
            exit 1
          fi

      - name: Process dataset
        run: |
          # Your processing logic here
          echo "Processing assembled dataset..."
          wc -l dataset_assembled.txt
```

---

## 🎯 Part 2: Pre-Deploy Triggers and Gates

### 2.1 Variable-Driven Gates

Use variables to control workflow execution without code changes:

| Variable | Purpose | Example Value |
|----------|---------|---------------|
| `PREDEPLOY_ENABLED` | Enable/disable pre-deploy | `true` or `false` |
| `PREDEPLOY_COMMAND` | CLI command to run | `python -m build && twine check dist/*` |
| `PREDEPLOY_SCRIPT` | Multi-line bash script | `#!/bin/bash\nset -e\nmake lint\nmake test` |
| `DEPLOY_GATE_APPROVAL` | Require approval | `manual` or `auto` |

### 2.2 Pre-Deploy Workflow with Variable Gates

**File**: `.github/workflows/predeploy-gate.yml`

```yaml
name: Pre-Deploy Gate

on:
  push:
    branches: [main, develop]
  workflow_dispatch:

jobs:
  predeploy-gate:
    runs-on: ubuntu-latest
    # Gate: Only run if enabled
    if: ${{ vars.PREDEPLOY_ENABLED == 'true' }}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Execute shared predeploy command
        if: ${{ vars.PREDEPLOY_COMMAND != '' }}
        run: ${{ vars.PREDEPLOY_COMMAND }}
      
      - name: Execute shared predeploy script
        if: ${{ vars.PREDEPLOY_SCRIPT != '' }}
        run: |
          cat > /tmp/predeploy.sh << 'EOF'
          ${{ vars.PREDEPLOY_SCRIPT }}
          EOF
          chmod +x /tmp/predeploy.sh
          bash -x /tmp/predeploy.sh
      
      - name: Run deterministic audit
        if: ${{ vars.AUDIT_PREDEPLOY_GATE == 'true' }}
        env:
          AUDIT_WEIGHTS: ${{ vars.AUDIT_WEIGHTS }}
          AUDIT_LOW_THRESHOLD: ${{ vars.AUDIT_LOW_THRESHOLD }}
          WANDB_MODE: ${{ vars.WANDB_MODE }}
        run: |
          python scripts/space_traversal/audit_runner.py stage S1
          python scripts/space_traversal/audit_runner.py stage S2
          python scripts/space_traversal/audit_runner.py stage S3
          python scripts/space_traversal/audit_runner.py stage S4
          python scripts/space_traversal/audit_runner.py stage S5
          python scripts/space_traversal/audit_runner.py stage S6
          python scripts/space_traversal/audit_runner.py stage S7
      
      # SECURITY: Manual approval gate (use with caution)
      # WARNING: Third-party action creates supply chain risk. Prefer native GitHub solutions.
      # 
      # RECOMMENDED APPROACH: Use GitHub Environment Protection Rules instead
      # 1. Create a "production" environment in repo settings
      # 2. Configure required reviewers (Settings > Environments > production > Required reviewers)
      # 3. Update job to target environment:
      #    jobs:
      #      deploy:
      #        environment: production
      #        steps: [...]
      # This provides native approval gates without third-party dependencies or supply chain risks.
      #
      # IF YOU MUST USE THIRD-PARTY ACTION:
      # Pin to specific commit SHA (not mutable tag) to prevent supply chain attacks:
      # Example with commit SHA pinning:
      # uses: trstringer/manual-approval@842780cd9e1c69cc5ec2fca64054f553f9b979f4  # v1.9.0
      #
      # CURRENT EXAMPLE (INSECURE - FOR DOCUMENTATION ONLY):
      - name: Manual approval gate (INSECURE EXAMPLE - DO NOT USE AS-IS)
        if: ${{ vars.DEPLOY_GATE_APPROVAL == 'manual' }}
        uses: trstringer/manual-approval@v1  # ⚠️ SECURITY RISK: Mutable tag
        with:
          approvers: mbaetiong
          minimum-approvals: 1
          issue-title: "Deploy approval required"
```

### 2.3 V10 Agent Deployment with Variable Seeds

**File**: `.github/workflows/deploy-v10-agents.yml`

```yaml
name: Deploy V10 Agents

on:
  workflow_dispatch:
    inputs:
      agent_name:
        description: 'Agent to deploy'
        required: true
        type: choice
        options:
          - performance-monitor
          - documentation
          - ci-optimizer
          - reasoning-advisor
          - ecosystem-coordinator

jobs:
  deploy-agent:
    runs-on: ubuntu-latest
    env:
      # Use variable seeds for deterministic execution
      EMERGENT_AGENT_SEED: ${{ vars.EMERGENT_AGENT_SEED }}
      PERF_MONITOR_SEED: ${{ vars.PERF_MONITOR_SEED }}
      DOC_AGENT_SEED: ${{ vars.DOC_AGENT_SEED }}
      CI_OPTIMIZER_SEED: ${{ vars.CI_OPTIMIZER_SEED }}
      REASONING_ADVISOR_SEED: ${{ vars.REASONING_ADVISOR_SEED }}
      ECOSYSTEM_COORD_SEED: ${{ vars.ECOSYSTEM_COORD_SEED }}
      VALIDATION_SEED: ${{ vars.VALIDATION_SEED }}
      WANDB_MODE: ${{ vars.WANDB_MODE }}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Deploy agent
        run: |
          AGENT="${{ github.event.inputs.agent_name }}"
          echo "Deploying ${AGENT} agent..."
          
          # Get appropriate seed from environment
          case "${AGENT}" in
            performance-monitor)
              AGENT_SEED="${PERF_MONITOR_SEED}"
              ;;
            documentation)
              AGENT_SEED="${DOC_AGENT_SEED}"
              ;;
            ci-optimizer)
              AGENT_SEED="${CI_OPTIMIZER_SEED}"
              ;;
            reasoning-advisor)
              AGENT_SEED="${REASONING_ADVISOR_SEED}"
              ;;
            ecosystem-coordinator)
              AGENT_SEED="${ECOSYSTEM_COORD_SEED}"
              ;;
          esac
          
          echo "Using seed: ${AGENT_SEED}"
          
          # Run agent with deterministic seed
          python .github/agents/${AGENT}-agent/src/main.py \
            --seed "${AGENT_SEED}" \
            --mode deploy
```

---

## 🎯 Part 3: REST API Orchestration

### 3.1 HTTP Methods Reference

| Method | Purpose | Idempotency | Use Case |
|--------|---------|-------------|----------|
| GET | Retrieve variable | Safe, idempotent | Read variable value |
| PUT | Create/replace | Idempotent | Write or overwrite variable |
| PATCH | Partial update | Not guaranteed | Update value only |
| DELETE | Remove variable | Idempotent | Cleanup old chunks |

### 3.2 curl Examples for REST API

**Create/Update Variable (PUT)**:
```bash
#!/bin/bash
# Create or replace a repository variable

OWNER="Aries-Serpent"
REPO="_codex_"
VAR_NAME="DATASET_20260103_P001"
VAR_VALUE="<chunk data here>"

curl -X PUT \
  -H "Authorization: Bearer ${GITHUB_TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/repos/${OWNER}/${REPO}/actions/variables/${VAR_NAME}" \
  -d "$(jq -n \
    --arg name "${VAR_NAME}" \
    --arg value "${VAR_VALUE}" \
    '{name: $name, value: $value}'
  )"
```

**Read Variable (GET)**:
```bash
#!/bin/bash
# Read a repository variable

curl -s \
  -H "Authorization: Bearer ${GITHUB_TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/repos/${OWNER}/${REPO}/actions/variables/${VAR_NAME}" \
  | jq -r '.value'
```

**Delete Variable (DELETE)**:
```bash
#!/bin/bash
# Delete a repository variable

curl -X DELETE \
  -H "Authorization: Bearer ${GITHUB_TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/repos/${OWNER}/${REPO}/actions/variables/${VAR_NAME}"
```

**List All Variables (GET)**:
```bash
#!/bin/bash
# List all repository variables

curl -s \
  -H "Authorization: Bearer ${GITHUB_TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/repos/${OWNER}/${REPO}/actions/variables" \
  | jq '.variables[] | {name: .name, updated_at: .updated_at}'
```

### 3.3 Python Script for Variable Management

**File**: `.codex/scripts/manage_github_variables.py`

```python
#!/usr/bin/env python3
"""
Manage GitHub Repository Variables via REST API
Usage: python manage_github_variables.py <command> [args]
"""

import os
import sys
import json
import requests
from typing import Dict, Any, Optional, List

class GitHubVariableManager:
    """Manage GitHub repository variables"""
    
    def __init__(self, owner: str, repo: str, token: str):
        self.owner = owner
        self.repo = repo
        self.token = token
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}/actions/variables"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    
    def create_or_update(self, name: str, value: str) -> bool:
        """Create or update a variable (PUT)"""
        url = f"{self.base_url}/{name}"
        data = {"name": name, "value": value}
        
        response = requests.put(url, headers=self.headers, json=data)
        
        if response.status_code in [201, 204]:
            print(f"✅ Variable '{name}' created/updated successfully")
            return True
        else:
            print(f"❌ Failed to create/update '{name}': {response.status_code}")
            print(response.text)
            return False
    
    def get(self, name: str) -> Optional[str]:
        """Get a variable value (GET)"""
        url = f"{self.base_url}/{name}"
        
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json().get('value')
        else:
            print(f"❌ Failed to get '{name}': {response.status_code}")
            return None
    
    def delete(self, name: str) -> bool:
        """Delete a variable (DELETE)"""
        url = f"{self.base_url}/{name}"
        
        response = requests.delete(url, headers=self.headers)
        
        if response.status_code == 204:
            print(f"✅ Variable '{name}' deleted successfully")
            return True
        else:
            print(f"❌ Failed to delete '{name}': {response.status_code}")
            return False
    
    def list_all(self) -> List[Dict[str, Any]]:
        """List all variables"""
        response = requests.get(self.base_url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json().get('variables', [])
        else:
            print(f"❌ Failed to list variables: {response.status_code}")
            return []
    
    def upload_paginated_dataset(self, dataset_path: str, dataset_id: str) -> bool:
        """Upload a large dataset as paginated variables"""
        import math
        
        # Read dataset
        with open(dataset_path, 'rb') as f:
            data = f.read()
        
        # Configuration
        MAX_CHUNK_SIZE = 49152  # 48 KB
        total_size = len(data)
        pages = math.ceil(total_size / MAX_CHUNK_SIZE)
        
        # Create chunks
        chunks = []
        for i in range(pages):
            start = i * MAX_CHUNK_SIZE
            end = min((i + 1) * MAX_CHUNK_SIZE, total_size)
            chunks.append(data[start:end].decode('utf-8', errors='ignore'))
        
        # Generate index
        index = {
            "dataset_id": dataset_id,
            "pages": pages,
            "schema": "json",
            "keys": [f"DATASET_{dataset_id.upper()}_P{str(i+1).zfill(3)}" for i in range(pages)],
            "created_at": "Current Cycle-01-03T20:00:00Z",
            "total_size_bytes": total_size,
            "compression": "none"
        }
        
        # Upload index
        index_var = f"DATASET_{dataset_id.upper()}_INDEX"
        if not self.create_or_update(index_var, json.dumps(index, separators=(',', ':'))):
            return False
        
        # Upload pages
        for i, chunk in enumerate(chunks):
            page_var = f"DATASET_{dataset_id.upper()}_P{str(i+1).zfill(3)}"
            print(f"Uploading page {i+1}/{pages}...")
            if not self.create_or_update(page_var, chunk):
                return False
        
        print(f"✅ Uploaded {pages} pages totaling {total_size} bytes")
        return True
    
    def download_paginated_dataset(self, dataset_id: str, output_path: str) -> bool:
        """Download and reconstruct a paginated dataset"""
        # Read index
        index_var = f"DATASET_{dataset_id.upper()}_INDEX"
        index_json = self.get(index_var)
        
        if not index_json:
            print(f"❌ Index variable not found: {index_var}")
            return False
        
        index = json.loads(index_json)
        pages = index['pages']
        keys = index['keys']
        
        # Download pages
        chunks = []
        for i, key in enumerate(keys):
            print(f"Downloading page {i+1}/{pages}...")
            chunk = self.get(key)
            if chunk is None:
                print(f"❌ Failed to download page: {key}")
                return False
            chunks.append(chunk)
        
        # Assemble
        assembled = ''.join(chunks)
        
        # Write to file
        with open(output_path, 'w') as f:
            f.write(assembled)
        
        print(f"✅ Downloaded and assembled {len(assembled)} bytes to {output_path}")
        return True

def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python manage_github_variables.py <command> [args]")
        print("Commands:")
        print("  set <name> <value>           - Create/update variable")
        print("  get <name>                   - Get variable value")
        print("  delete <name>                - Delete variable")
        print("  list                         - List all variables")
        print("  upload <path> <dataset_id>   - Upload paginated dataset")
        print("  download <dataset_id> <path> - Download paginated dataset")
        sys.exit(1)
    
    # Get credentials from environment
    owner = os.getenv('GITHUB_OWNER', 'Aries-Serpent')
    repo = os.getenv('GITHUB_REPO', '_codex_')
    token = os.getenv('GITHUB_TOKEN')
    
    if not token:
        print("❌ GITHUB_TOKEN environment variable required")
        sys.exit(1)
    
    manager = GitHubVariableManager(owner, repo, token)
    command = sys.argv[1]
    
    if command == 'set' and len(sys.argv) >= 4:
        manager.create_or_update(sys.argv[2], sys.argv[3])
    elif command == 'get' and len(sys.argv) >= 3:
        value = manager.get(sys.argv[2])
        if value:
            print(value)
    elif command == 'delete' and len(sys.argv) >= 3:
        manager.delete(sys.argv[2])
    elif command == 'list':
        variables = manager.list_all()
        for var in variables:
            print(f"{var['name']}: updated {var['updated_at']}")
    elif command == 'upload' and len(sys.argv) >= 4:
        manager.upload_paginated_dataset(sys.argv[2], sys.argv[3])
    elif command == 'download' and len(sys.argv) >= 4:
        manager.download_paginated_dataset(sys.argv[2], sys.argv[3])
    else:
        print("❌ Invalid command or arguments")
        sys.exit(1)

if __name__ == '__main__':
    main()
```

---

## 🎯 Part 4: Cleanup Workflow

**File**: `.github/workflows/cleanup-dataset-variables.yml`

```yaml
name: Cleanup Dataset Variables

on:
  workflow_dispatch:
    inputs:
      dataset_id:
        description: 'Dataset ID to cleanup'
        required: true
        type: string
      confirm:
        description: 'Type DELETE to confirm'
        required: true
        type: string

jobs:
  cleanup:
    runs-on: ubuntu-latest
    if: ${{ github.event.inputs.confirm == 'DELETE' }}
    permissions:
      actions: write
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Delete dataset variables
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          DATASET_ID: ${{ github.event.inputs.dataset_id }}
        run: |
          # Read index to get page keys
          INDEX_VAR="DATASET_${DATASET_ID}_INDEX"
          
          if gh variable get "${INDEX_VAR}" > index.json 2>/dev/null; then
            # Extract page keys
            KEYS=$(jq -r '.keys[]' index.json)
            
            # Delete each page
            for KEY in $KEYS; do
              echo "Deleting ${KEY}..."
              gh variable delete "${KEY}" || true
            done
            
            # Delete index
            echo "Deleting ${INDEX_VAR}..."
            gh variable delete "${INDEX_VAR}" || true
            
            echo "✅ Cleanup complete"
          else
            echo "❌ Index variable not found: ${INDEX_VAR}"
            exit 1
          fi
```

---

## 🎯 Part 5: Integration with V10 Agents

### 5.1 Agent Configuration from Variables

Update V10 agents to read configuration from GitHub Variables:

**Pattern**: `.github/agents/*/src/config_loader.py`

```python
"""
Load agent configuration from GitHub Variables
Falls back to defaults if variables not available
"""
import os
import json
from typing import Dict, Any

class AgentConfigLoader:
    """Load agent configuration from environment variables (GitHub Variables)"""
    
    @staticmethod
    def get_seed(agent_name: str, default: int) -> int:
        """Get agent seed from environment"""
        env_var_map = {
            "emergent-intelligence": "EMERGENT_AGENT_SEED",
            "performance-monitor": "PERF_MONITOR_SEED",
            "documentation": "DOC_AGENT_SEED",
            "ci-optimizer": "CI_OPTIMIZER_SEED",
            "reasoning-advisor": "REASONING_ADVISOR_SEED",
            "ecosystem-coordinator": "ECOSYSTEM_COORD_SEED"
        }
        
        var_name = env_var_map.get(agent_name)
        if var_name:
            return int(os.getenv(var_name, str(default)))
        return default
    
    @staticmethod
    def get_audit_config() -> Dict[str, Any]:
        """Get audit configuration from variables"""
        config = {}
        
        # Safeguard keywords
        keywords_json = os.getenv('AUDIT_SAFEGUARD_KEYWORDS')
        if keywords_json:
            try:
                config['safeguard_keywords'] = json.loads(keywords_json)
            except json.JSONDecodeError:
                config['safeguard_keywords'] = keywords_json.split(',')
        
        # Weights
        weights_json = os.getenv('AUDIT_WEIGHTS')
        if weights_json:
            try:
                config['weights'] = json.loads(weights_json)
            except json.JSONDecodeError:
                pass
        
        # Thresholds
        if os.getenv('AUDIT_LOW_THRESHOLD'):
            config['low_threshold'] = float(os.getenv('AUDIT_LOW_THRESHOLD'))
        
        if os.getenv('AUDIT_REGRESSION_DELTA'):
            config['regression_delta'] = float(os.getenv('AUDIT_REGRESSION_DELTA'))
        
        # Max read bytes
        if os.getenv('AUDIT_MAX_READ_BYTES'):
            config['max_read_bytes'] = int(os.getenv('AUDIT_MAX_READ_BYTES'))
        
        return config
```

### 5.2 Autonomous Promptset for Variables Integration

**Promptset Addition** for each V10 agent:

```markdown
## GITHUB VARIABLES INTEGRATION

### Environment Variables to Support
Your agent must read configuration from these GitHub Variables (via environment):

1. **Agent Seed**: `${{ vars.<AGENT>_SEED }}`
   ```python
   from config_loader import AgentConfigLoader
   seed = AgentConfigLoader.get_seed("agent-name", default=XX)
   ```

2. **Validation Seed**: `${{ vars.VALIDATION_SEED }}`
   - Use for deterministic validation/testing

3. **Wandb Mode**: `${{ vars.WANDB_MODE }}`
   - Set to "offline" for deterministic runs

4. **Audit Configuration** (if applicable):
   - `AUDIT_WEIGHTS`, `AUDIT_LOW_THRESHOLD`, etc.
   - Use `AgentConfigLoader.get_audit_config()`

### Implementation Checklist
- [ ] Add `config_loader.py` to agent src/
- [ ] Update agent initialization to use `get_seed()`
- [ ] Add environment variable fallbacks
- [ ] Test with and without variables set
- [ ] Document required variables in README.md
```

---

## 🎯 Part 6: Security and Best Practices

### 6.1 Security Guidelines

1. **Never store secrets/PII in variables**
   - Use `${{ secrets.NAME }}` for sensitive data
   - Variables are plain text and visible to repository contributors

2. **Validate variable content before execution**
   ```bash
   # Validate JSON structure
   if ! jq empty <<< "${VAR_VALUE}"; then
     echo "Invalid JSON"
     exit 1
   fi
   
   # Validate commands (basic check)
   if echo "${PREDEPLOY_COMMAND}" | grep -qE '(rm -rf|dd|fork|bomb)'; then
     echo "Potentially dangerous command detected"
     exit 1
   fi
   ```

3. **Size management**
   - Monitor variable sizes: `jq length <<< "${VAR_VALUE}"`
   - Implement cleanup policies for paginated data
   - Use compression for large datasets

4. **Access control**
   - Repository variables: visible to all repo workflows
   - Organization variables: visible to all org repos (if allowed)
   - Environment variables: restricted to specific deployment environments

### 6.2 Retention and Cleanup

Implement automated cleanup for temporary variables:

```yaml
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

jobs:
  cleanup-old-datasets:
    runs-on: ubuntu-latest
    steps:
      - name: Cleanup datasets older than 7 sessions
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          # List all variables
          gh api repos/${{ github.repository }}/actions/variables --paginate | jq -r '.variables[] | select(.name | startswith("DATASET_")) | .name' | while read VAR; do
            # Check if it's an index
            if [[ "$VAR" == *"_INDEX" ]]; then
              # Read created_at from index
              CREATED_AT=$(gh variable get "${VAR}" | jq -r '.created_at')
              # Check if older than 7 sessions
              # (Implement date comparison logic)
              # gh variable delete "${VAR}"
            fi
          done
```

---

## 🎯 Part 7: Quick Reference

### Variable Scope Comparison

| Feature | Repository | Organization | Environment |
|---------|-----------|--------------|-------------|
| Visibility | All repo workflows | All org repos | Specific environment |
| Size Limit | 48KB/variable | 48KB/variable | 48KB/variable |
| Access Control | Repository level | Organization level | Environment level |
| Override | No | Yes (repo overrides org) | Yes (env overrides repo/org) |
| Use Case | Repo-specific config | Shared CLI/scripts | Stage-specific gates |

### gh CLI Quick Commands

```bash
# Set variable
gh variable set VAR_NAME --body "value"

# Get variable
gh variable get VAR_NAME

# Delete variable
gh variable delete VAR_NAME

# List variables
gh variable list

# Set from file
gh variable set VAR_NAME --body "$(cat file.txt)"
```

### REST API Endpoints

```
GET    /repos/{owner}/{repo}/actions/variables
GET    /repos/{owner}/{repo}/actions/variables/{name}
POST   /repos/{owner}/{repo}/actions/variables
PATCH  /repos/{owner}/{repo}/actions/variables/{name}
DELETE /repos/{owner}/{repo}/actions/variables/{name}

GET    /orgs/{org}/actions/variables
POST   /orgs/{org}/actions/variables
...
```

---

## 📊 Success Metrics

- [ ] Can store datasets > 48KB via pagination
- [ ] Can trigger workflows via repository_dispatch
- [ ] Pre-deploy gates functioning with variable control
- [ ] V10 agents reading seeds from variables
- [ ] Cleanup workflow removes stale variables
- [ ] Zero secrets/PII in variables (audit passed)

---

*End of Advanced GitHub Variables Implementation Guide*
*Generated for PR #2685 - Autonomous V10 Development*
