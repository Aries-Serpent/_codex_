# T6: Dataset Hash Manifest - Autonomous Copilot Prompt

🎯 **COPILOT INSTRUCTION:** @workspace Execute with self-expansion

## Metadata
```yaml
task_id: T6
priority: P1
phase: phase_2_reproducibility
effort: 2-3 days
dependencies: []
```

## Context
- **Gap:** No dataset versioning/hashing (drift undetected)
- **Target:** Compute SHA256 for data files, embed in manifests
- **Impact:** +18% reproducibility

## Implementation

### 1. Create Hash Utility
**File:** `src/codex_ml/utils/repro.py`
```python
"""Reproducibility utilities for dataset and config hashing."""
import hashlib
from pathlib import Path
from typing import Dict, List

def compute_file_hash(filepath: Path, algorithm="sha256") -> str:
    """Compute hash of file contents."""
    h = hashlib.new(algorithm)
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def compute_directory_hash(dirpath: Path, extensions: List[str] = None) -> Dict[str, str]:
    """Compute hashes for all files in directory."""
    hashes = {}
    
    files = sorted(dirpath.rglob("*"))
    for filepath in files:
        if filepath.is_file():
            if extensions and filepath.suffix not in extensions:
                continue
            
            rel_path = filepath.relative_to(dirpath)
            hashes[str(rel_path)] = compute_file_hash(filepath)
    
    return hashes

class DatasetManifest:
    def __init__(self, dataset_path: Path):
        self.dataset_path = Path(dataset_path)
        self.manifest = {
            "dataset_path": str(self.dataset_path),
            "file_hashes": {},
            "total_files": 0,
            "total_size_bytes": 0,
        }
    
    def generate(self, extensions=None):
        """Generate manifest with file hashes."""
        self.manifest["file_hashes"] = compute_directory_hash(
            self.dataset_path, extensions
        )
        self.manifest["total_files"] = len(self.manifest["file_hashes"])
        
        # Compute total size
        total_size = sum(
            (self.dataset_path / f).stat().st_size
            for f in self.manifest["file_hashes"].keys()
        )
        self.manifest["total_size_bytes"] = total_size
        
        return self.manifest
    
    def save(self, output_path: Path):
        """Save manifest to JSON."""
        import json
        with open(output_path, "w") as f:
            json.dump(self.manifest, f, indent=2)
    
    def verify(self, manifest_path: Path) -> Dict[str, List[str]]:
        """Verify current dataset against saved manifest."""
        import json
        with open(manifest_path) as f:
            saved_manifest = json.load(f)
        
        current_hashes = compute_directory_hash(self.dataset_path)
        
        results = {
            "missing": [],
            "modified": [],
            "added": [],
        }
        
        saved_files = set(saved_manifest["file_hashes"].keys())
        current_files = set(current_hashes.keys())
        
        results["missing"] = list(saved_files - current_files)
        results["added"] = list(current_files - saved_files)
        
        for file in saved_files & current_files:
            if saved_manifest["file_hashes"][file] != current_hashes[file]:
                results["modified"].append(file)
        
        return results
```

### 2. Integrate into Training
**File:** `training/checkpoint_manager.py`
```python
from codex_ml.utils.repro import DatasetManifest

class CheckpointManager:
    def save_checkpoint(self, checkpoint_dir, dataset_path=None):
        # Save model/optimizer
        self._save_model(checkpoint_dir)
        
        # Generate dataset manifest
        if dataset_path:
            manifest = DatasetManifest(dataset_path)
            manifest.generate()
            manifest.save(checkpoint_dir / "dataset_manifest.json")
            print(f"✓ Dataset manifest saved ({manifest.manifest['total_files']} files)")
    
    def load_checkpoint(self, checkpoint_dir, verify_dataset=True):
        # Load model/optimizer
        self._load_model(checkpoint_dir)
        
        # Verify dataset hasn't changed
        if verify_dataset:
            manifest_path = checkpoint_dir / "dataset_manifest.json"
            if manifest_path.exists():
                import json
                with open(manifest_path) as f:
                    saved = json.load(f)
                
                dataset_path = Path(saved["dataset_path"])
                if dataset_path.exists():
                    manifest = DatasetManifest(dataset_path)
                    diff = manifest.verify(manifest_path)
                    
                    if diff["modified"] or diff["missing"]:
                        print(f"⚠️ Dataset drift detected:")
                        print(f"  Modified: {len(diff['modified'])}")
                        print(f"  Missing: {len(diff['missing'])}")
```

### 3. Add CLI Commands
```python
# Add to main CLI
parser.add_argument("--generate-dataset-manifest", action="store_true")
parser.add_argument("--verify-dataset-manifest", type=str)

if args.generate_dataset_manifest:
    manifest = DatasetManifest(args.data_path)
    manifest.generate()
    manifest.save("dataset_manifest.json")
    print("Dataset manifest generated")
```

## Testing
```python
def test_file_hash_deterministic(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("test content")
    
    hash1 = compute_file_hash(file)
    hash2 = compute_file_hash(file)
    assert hash1 == hash2

def test_dataset_manifest_generation(tmp_path):
    # Create dummy dataset
    (tmp_path / "train.txt").write_text("data")
    (tmp_path / "val.txt").write_text("data")
    
    manifest = DatasetManifest(tmp_path)
    result = manifest.generate()
    
    assert len(result["file_hashes"]) == 2
    assert "train.txt" in result["file_hashes"]

def test_dataset_drift_detection(tmp_path):
    # Generate initial manifest
    (tmp_path / "data.txt").write_text("original")
    manifest = DatasetManifest(tmp_path)
    manifest.generate()
    manifest.save(tmp_path / "manifest.json")
    
    # Modify file
    (tmp_path / "data.txt").write_text("modified")
    
    # Verify detects change
    diff = manifest.verify(tmp_path / "manifest.json")
    assert "data.txt" in diff["modified"]
```

## Validation
```bash
# Generate manifest
python cli/train_codex.py --data-path data/ --generate-dataset-manifest

# Verify manifest exists
ls dataset_manifest.json

# Modify dataset and verify drift detected
echo "new data" >> data/train.txt
python cli/train_codex.py --verify-dataset-manifest dataset_manifest.json
# Expected: Drift warning
```

## Acceptance
- [ ] Hash utilities created (file, directory)
- [ ] DatasetManifest class with generate/verify methods
- [ ] Integrated into checkpoint_manager.py
- [ ] CLI commands for manifest generation/verification
- [ ] Drift detection alerts on modified files
- [ ] Tests verify determinism and drift detection

## Audit Reference
- `reports/_codex_task_sequences-20251206.md` lines 45-50
- `workbench/exhaustive_audit/reproducibility_checklist.md` → dataset hashing

🤖 **Auto-expand:** Generate sub-prompt for large dataset handling if needed
