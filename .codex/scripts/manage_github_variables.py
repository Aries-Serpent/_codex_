#!/usr/bin/env python3
"""
Manage GitHub Repository Variables via REST API
Usage: python manage_github_variables.py <command> [args]

Supports:
- Creating/updating variables (PUT)
- Reading variables (GET)
- Deleting variables (DELETE)
- Listing all variables
- Uploading paginated datasets
- Downloading paginated datasets
"""

import os
import sys
import json
import math
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime

class GitHubVariableManager:
    """Manage GitHub repository variables via REST API"""
    
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
        
        try:
            response = requests.put(url, headers=self.headers, json=data, timeout=30)
            
            if response.status_code in [201, 204]:
                print(f"✅ Variable '{name}' created/updated successfully")
                return True
            else:
                print(f"❌ Failed to create/update '{name}': {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except requests.RequestException as e:
            print(f"❌ Request failed: {e}")
            return False
    
    def get(self, name: str) -> Optional[str]:
        """Get a variable value (GET)"""
        url = f"{self.base_url}/{name}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                return response.json().get('value')
            elif response.status_code == 404:
                print(f"❌ Variable '{name}' not found")
                return None
            else:
                print(f"❌ Failed to get '{name}': {response.status_code}")
                return None
        except requests.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def delete(self, name: str) -> bool:
        """Delete a variable (DELETE)"""
        url = f"{self.base_url}/{name}"
        
        try:
            response = requests.delete(url, headers=self.headers, timeout=30)
            
            if response.status_code == 204:
                print(f"✅ Variable '{name}' deleted successfully")
                return True
            elif response.status_code == 404:
                print(f"⚠️  Variable '{name}' not found")
                return False
            else:
                print(f"❌ Failed to delete '{name}': {response.status_code}")
                return False
        except requests.RequestException as e:
            print(f"❌ Request failed: {e}")
            return False
    
    def list_all(self) -> List[Dict[str, Any]]:
        """List all variables"""
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                return response.json().get('variables', [])
            else:
                print(f"❌ Failed to list variables: {response.status_code}")
                return []
        except requests.RequestException as e:
            print(f"❌ Request failed: {e}")
            return []
    
    def upload_paginated_dataset(self, dataset_path: str, dataset_id: str) -> bool:
        """Upload a large dataset as paginated variables"""
        # Read dataset
        try:
            with open(dataset_path, 'rb') as f:
                data = f.read()
        except IOError as e:
            print(f"❌ Failed to read dataset: {e}")
            return False
        
        # Configuration
        MAX_CHUNK_SIZE = 49152  # 48 KB
        total_size = len(data)
        pages = math.ceil(total_size / MAX_CHUNK_SIZE)
        
        print(f"📊 Dataset size: {total_size} bytes, will create {pages} pages")
        
        # Create chunks
        chunks = []
        for i in range(pages):
            start = i * MAX_CHUNK_SIZE
            end = min((i + 1) * MAX_CHUNK_SIZE, total_size)
            chunk_data = data[start:end]
            # Try to decode as text, fallback to base64 if binary
            try:
                chunks.append(chunk_data.decode('utf-8'))
            except UnicodeDecodeError:
                import base64
                chunks.append(base64.b64encode(chunk_data).decode('ascii'))
        
        # Generate index
        index = {
            "dataset_id": dataset_id,
            "pages": pages,
            "schema": "json",
            "keys": [f"DATASET_{dataset_id.upper()}_P{str(i+1).zfill(3)}" for i in range(pages)],
            "created_at": datetime.utcnow().isoformat() + "Z",
            "total_size_bytes": total_size,
            "compression": "none"
        }
        
        # Upload index
        index_var = f"DATASET_{dataset_id.upper()}_INDEX"
        print(f"📤 Uploading index: {index_var}")
        if not self.create_or_update(index_var, json.dumps(index, separators=(',', ':'))):
            return False
        
        # Upload pages
        for i, chunk in enumerate(chunks):
            page_var = f"DATASET_{dataset_id.upper()}_P{str(i+1).zfill(3)}"
            print(f"📤 Uploading page {i+1}/{pages}: {page_var} ({len(chunk)} chars)")
            if not self.create_or_update(page_var, chunk):
                print(f"❌ Failed to upload page {i+1}, aborting")
                return False
        
        print(f"✅ Successfully uploaded {pages} pages totaling {total_size} bytes")
        return True
    
    def download_paginated_dataset(self, dataset_id: str, output_path: str) -> bool:
        """Download and reconstruct a paginated dataset"""
        # Read index
        index_var = f"DATASET_{dataset_id.upper()}_INDEX"
        print(f"📥 Reading index: {index_var}")
        
        index_json = self.get(index_var)
        if not index_json:
            print(f"❌ Index variable not found: {index_var}")
            return False
        
        try:
            index = json.loads(index_json)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in index: {e}")
            return False
        
        pages = index['pages']
        keys = index['keys']
        total_size = index.get('total_size_bytes', 0)
        
        print(f"📊 Dataset has {pages} pages, total size: {total_size} bytes")
        
        # Download pages
        chunks = []
        for i, key in enumerate(keys):
            print(f"📥 Downloading page {i+1}/{pages}: {key}")
            chunk = self.get(key)
            if chunk is None:
                print(f"❌ Failed to download page: {key}")
                return False
            chunks.append(chunk)
        
        # Assemble
        assembled = ''.join(chunks)
        
        # Check if data was base64 encoded
        if len(assembled) != total_size:
            try:
                import base64
                assembled_bytes = base64.b64decode(assembled)
                print(f"📦 Decoded base64 data")
            except Exception:
                assembled_bytes = assembled.encode('utf-8')
        else:
            assembled_bytes = assembled.encode('utf-8')
        
        # Write to file
        try:
            with open(output_path, 'wb') as f:
                f.write(assembled_bytes)
            print(f"✅ Downloaded and assembled {len(assembled_bytes)} bytes to {output_path}")
            return True
        except IOError as e:
            print(f"❌ Failed to write output: {e}")
            return False
    
    def create_v10_variables(self) -> bool:
        """Create all V10 agent and audit variables"""
        variables = {
            # V10 Agent Seeds
            "AGENT_SEEDS": "46,47,48,49,50,51",
            "VALIDATION_SEED": "42",
            "EMERGENT_AGENT_SEED": "46",
            "PERF_MONITOR_SEED": "47",
            "DOC_AGENT_SEED": "48",
            "CI_OPTIMIZER_SEED": "49",
            "REASONING_ADVISOR_SEED": "50",
            "ECOSYSTEM_COORD_SEED": "51",
            "WANDB_MODE": "offline",
            "CI_DURATION_NORMALIZATION_MS": "1000",
            
            # Audit Infrastructure
            "AUDIT_SAFEGUARD_KEYWORDS": json.dumps([
                "sha256", "checksum", "rng", "seed", "offline", 
                "WANDB_MODE", "deterministic", "nosec"
            ]),
            "AUDIT_MAX_READ_BYTES": "200000",
            "AUDIT_WEIGHTS": json.dumps({
                "functionality": 0.25,
                "consistency": 0.20,
                "tests": 0.25,
                "safeguards": 0.15,
                "documentation": 0.15
            }),
            "AUDIT_LOW_THRESHOLD": "0.70",
            "AUDIT_REGRESSION_DELTA": "0.02",
            "AUDIT_OUTPUT_DIRS": json.dumps({
                "reports": "reports",
                "artifacts": "audit_artifacts"
            }),
            
            # Pre-deploy gates
            "PREDEPLOY_ENABLED": "false",  # Disabled by default
            "AUDIT_PREDEPLOY_GATE": "false"  # Disabled by default
        }
        
        success = True
        for name, value in variables.items():
            print(f"\n📤 Creating variable: {name}")
            if not self.create_or_update(name, value):
                success = False
        
        return success

def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("GitHub Variable Manager")
        print("=" * 50)
        print("\nUsage: python manage_github_variables.py <command> [args]")
        print("\nCommands:")
        print("  set <name> <value>           - Create/update variable")
        print("  get <name>                   - Get variable value")
        print("  delete <name>                - Delete variable")
        print("  list                         - List all variables")
        print("  upload <path> <dataset_id>   - Upload paginated dataset")
        print("  download <dataset_id> <path> - Download paginated dataset")
        print("  init-v10                     - Initialize all V10 variables")
        print("\nEnvironment variables required:")
        print("  GITHUB_TOKEN  - GitHub personal access token")
        print("  GITHUB_OWNER  - Repository owner (default: Aries-Serpent)")
        print("  GITHUB_REPO   - Repository name (default: _codex_)")
        sys.exit(1)
    
    # Get credentials from environment
    owner = os.getenv('GITHUB_OWNER', 'Aries-Serpent')
    repo = os.getenv('GITHUB_REPO', '_codex_')
    token = os.getenv('GITHUB_TOKEN')
    
    if not token:
        print("❌ GITHUB_TOKEN environment variable required")
        print("Set it with: export GITHUB_TOKEN=your_token_here")
        sys.exit(1)
    
    manager = GitHubVariableManager(owner, repo, token)
    command = sys.argv[1]
    
    try:
        if command == 'set' and len(sys.argv) >= 4:
            name = sys.argv[2]
            value = sys.argv[3]
            sys.exit(0 if manager.create_or_update(name, value) else 1)
        
        elif command == 'get' and len(sys.argv) >= 3:
            name = sys.argv[2]
            value = manager.get(name)
            if value:
                print(value)
                sys.exit(0)
            else:
                sys.exit(1)
        
        elif command == 'delete' and len(sys.argv) >= 3:
            name = sys.argv[2]
            sys.exit(0 if manager.delete(name) else 1)
        
        elif command == 'list':
            variables = manager.list_all()
            if variables:
                print(f"\n{'Name':<40} {'Updated':<30}")
                print("=" * 70)
                for var in variables:
                    print(f"{var['name']:<40} {var['updated_at']:<30}")
                print(f"\nTotal: {len(variables)} variables")
            else:
                print("No variables found")
            sys.exit(0)
        
        elif command == 'upload' and len(sys.argv) >= 4:
            dataset_path = sys.argv[2]
            dataset_id = sys.argv[3]
            sys.exit(0 if manager.upload_paginated_dataset(dataset_path, dataset_id) else 1)
        
        elif command == 'download' and len(sys.argv) >= 4:
            dataset_id = sys.argv[2]
            output_path = sys.argv[3]
            sys.exit(0 if manager.download_paginated_dataset(dataset_id, output_path) else 1)
        
        elif command == 'init-v10':
            print("🚀 Initializing V10 variables...")
            sys.exit(0 if manager.create_v10_variables() else 1)
        
        else:
            print("❌ Invalid command or missing arguments")
            print("Run without arguments to see usage")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
