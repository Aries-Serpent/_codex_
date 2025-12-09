#!/usr/bin/env python3
"""
Validate audit_artifacts for required structure and content.
"""
import json
from pathlib import Path

ROOT = Path("/home/runner/work/_codex_/_codex_")
ARTIFACTS_DIR = ROOT / "audit_artifacts"

# Required artifacts
REQUIRED_FILES = {
    "FOLLOW_UP_PROMPTS.md": {
        "type": "markdown",
        "min_size": 1000,
        "keywords": ["prompt", "follow", "remediation", "achievement"]
    },
    "capabilities_raw.json": {
        "type": "json",
        "min_size": 100,
        "schema_keys": ["capabilities", "generated"]
    },
    "capabilities_scored.json": {
        "type": "json",
        "min_size": 100,
        "schema_keys": ["capabilities", "generated"]
    },
    "context_index.json": {
        "type": "json",
        "min_size": 100,
        "schema_keys": ["files"]
    }
}

# Optional but recommended
OPTIONAL_FILES = [
    "coverage_map.json",
    "gaps.json",
    "facets.json"
]

validation_results = []

print(f"Validating audit artifacts in {ARTIFACTS_DIR}...")

for filename, requirements in REQUIRED_FILES.items():
    file_path = ARTIFACTS_DIR / filename
    result = {
        "filename": filename,
        "exists": file_path.exists(),
        "checks": {},
        "issues": [],
        "warnings": []
    }
    
    if not file_path.exists():
        result["issues"].append(f"Required file {filename} not found")
        validation_results.append(result)
        continue
    
    try:
        # Check file size
        size = file_path.stat().st_size
        result["checks"]["size"] = size
        if size < requirements["min_size"]:
            result["warnings"].append(f"File size {size} below minimum {requirements['min_size']}")
        
        # Check content based on type
        if requirements["type"] == "json":
            try:
                data = json.loads(file_path.read_text(encoding='utf-8'))
                result["checks"]["valid_json"] = True
                
                # Check schema keys
                if "schema_keys" in requirements:
                    for key in requirements["schema_keys"]:
                        if key in data:
                            result["checks"][f"has_{key}"] = True
                        else:
                            result["issues"].append(f"Missing required key: {key}")
                            
            except json.JSONDecodeError as e:
                result["checks"]["valid_json"] = False
                result["issues"].append(f"Invalid JSON: {e}")
                
        elif requirements["type"] == "markdown":
            content = file_path.read_text(encoding='utf-8')
            result["checks"]["has_content"] = len(content) > 0
            
            # Check for required keywords
            if "keywords" in requirements:
                content_lower = content.lower()
                for kw in requirements["keywords"]:
                    if kw.lower() in content_lower:
                        result["checks"][f"has_keyword_{kw}"] = True
                    else:
                        result["warnings"].append(f"Missing recommended keyword: {kw}")
                        
    except Exception as e:
        result["issues"].append(f"Error validating file: {e}")
    
    validation_results.append(result)

# Check optional files
for filename in OPTIONAL_FILES:
    file_path = ARTIFACTS_DIR / filename
    result = {
        "filename": filename,
        "exists": file_path.exists(),
        "optional": True,
        "checks": {},
        "issues": [],
        "warnings": []
    }
    
    if file_path.exists():
        result["checks"]["size"] = file_path.stat().st_size
        if filename.endswith(".json"):
            try:
                json.loads(file_path.read_text(encoding='utf-8'))
                result["checks"]["valid_json"] = True
            except:
                result["warnings"].append("Invalid JSON")
    else:
        result["warnings"].append("Optional file not found (recommended for v1.4.0)")
    
    validation_results.append(result)

# Generate summary
total_required = len(REQUIRED_FILES)
required_passed = sum(1 for r in validation_results[:total_required] if r["exists"] and not r["issues"])
completeness = (required_passed / total_required * 100) if total_required > 0 else 0

has_coverage_map = (ARTIFACTS_DIR / "coverage_map.json").exists()

output = {
    "validation_date": "2025-12-09",
    "artifacts_directory": str(ARTIFACTS_DIR),
    "required_files": total_required,
    "required_passed": required_passed,
    "completeness_percent": round(completeness, 2),
    "has_coverage_map": has_coverage_map,
    "results": validation_results,
    "summary": {
        "total_required": total_required,
        "passed": required_passed,
        "failed": total_required - required_passed,
        "meets_threshold": completeness >= 90.0,
        "v1_4_0_features": {
            "coverage_map": has_coverage_map,
            "token_similarity": "Check dup_similarity.py module"
        }
    }
}

output_path = ROOT / ".github/audit_artifacts_output/audit_artifacts_validation.json"
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(json.dumps(output, indent=2), encoding='utf-8')

print(f"\nValidation Summary:")
print(f"  Required files: {total_required}")
print(f"  Passed: {required_passed}")
print(f"  Failed: {total_required - required_passed}")
print(f"  Completeness: {completeness:.1f}%")
print(f"  Has coverage_map.json: {has_coverage_map}")
print(f"  Meets 90% threshold: {completeness >= 90.0}")
print(f"\nWrote validation results to {output_path}")

print(json.dumps(output, indent=2))
