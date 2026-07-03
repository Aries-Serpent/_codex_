#!/usr/bin/env python3
"""
Dependency Conflict Resolver Agent

Detects, diagnoses, and resolves Python dependency conflicts. Validates schema
compatibility across versions and generates version matrices for machine-readable
documentation system (Phase 9.1 integration).

Component Reuse Strategy:
- Base: dependency-conflict-agent (70% reuse)
- Extension: pip resolver analysis, version matrix generation
- Integration: Phase 9.1 decision logger, docs-agent compatibility

Usage:
    python -m src.agent analyze --path requirements/
    python -m src.agent validate-schema --schema docs_agent_v1
    python -m src.agent generate-matrix --packages coverage,pytest
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml
from packaging import version as pkg_version
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet


class ConflictSeverity(Enum):
    """Severity levels for dependency conflicts"""
    NONE = "none"
    LOW = "low"          # Works but suboptimal versions
    MEDIUM = "medium"    # Requires workaround or pin
    HIGH = "high"        # Direct conflict, fails install
    CRITICAL = "critical"  # Blocks entire resolution


class ConflictType(Enum):
    """Types of dependency conflicts"""
    VERSION_INCOMPATIBILITY = "version_incompatibility"
    CIRCULAR_DEPENDENCY = "circular_dependency"
    MISSING_DEPENDENCY = "missing_dependency"
    CONFLICTING_PINS = "conflicting_pins"
    PLATFORM_MISMATCH = "platform_mismatch"
    DEPRECATED_VERSION = "deprecated_version"
    SCHEMA_INCOMPATIBILITY = "schema_incompatibility"


@dataclass
class DependencyNode:
    """Represents a dependency in the dependency graph"""
    name: str
    version: str
    required_by: List[str] = field(default_factory=list)
    requires: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    python_version: Optional[str] = None


@dataclass
class ConflictIssue:
    """Represents a detected dependency conflict"""
    conflict_id: str
    conflict_type: ConflictType
    severity: ConflictSeverity
    packages: List[str]
    description: str
    affected_dependencies: List[Tuple[str, str]] = field(default_factory=list)
    resolution_options: List[str] = field(default_factory=list)
    confidence: float = 1.0
    root_cause: Optional[str] = None
    introduced_by: Optional[str] = None


@dataclass
class VersionMatrix:
    """Compatibility matrix for package versions"""
    package_name: str
    versions_analyzed: List[str] = field(default_factory=list)
    compatibility_matrix: Dict[str, Dict[str, bool]] = field(default_factory=dict)
    safe_version_ranges: List[str] = field(default_factory=list)
    deprecated_versions: List[str] = field(default_factory=list)
    recommended_version: Optional[str] = None


@dataclass
class SchemaCompatibility:
    """Validates schema compatibility across versions"""
    schema_name: str
    schema_version: str
    compatible_packages: Dict[str, str] = field(default_factory=dict)
    incompatibilities: List[Tuple[str, str, str]] = field(default_factory=list)
    migration_path: Optional[List[str]] = None


@dataclass
class ResolutionResult:
    """Result of conflict resolution"""
    success: bool
    conflicts_found: int
    conflicts_resolved: int
    critical_remaining: int
    recommendations: List[str] = field(default_factory=list)
    updated_requirements: Optional[str] = None
    confidence_score: float = 0.0


class PipResolverAnalyzer:
    """Analyzes pip resolver conflicts and resolution paths"""

    def __init__(self):
        self.conflicts: List[ConflictIssue] = []
        self.dependency_graph: Dict[str, DependencyNode] = {}
        self.version_matrices: Dict[str, VersionMatrix] = {}

    def detect_conflicts(self, requirements: List[str]) -> List[ConflictIssue]:
        """
        Detect conflicts in a set of requirements.
        
        Args:
            requirements: List of requirement strings (e.g., ["pytest>=6.0", "coverage"])
            
        Returns:
            List of detected ConflictIssue objects
        """
        detected = []
        
        # Parse requirements
        parsed_reqs = []
        for req_str in requirements:
            try:
                parsed_reqs.append(Requirement(req_str))
            except Exception as e:
                detected.append(ConflictIssue(
                    conflict_id=f"parse_error_{len(detected)}",
                    conflict_type=ConflictType.MISSING_DEPENDENCY,
                    severity=ConflictSeverity.HIGH,
                    packages=[req_str],
                    description=f"Failed to parse requirement: {str(e)}",
                    root_cause=f"Invalid requirement syntax: {req_str}"
                ))
                continue

        # Check for explicit conflicts
        for i, req1 in enumerate(parsed_reqs):
            for j, req2 in enumerate(parsed_reqs[i+1:], i+1):
                if req1.name.lower() == req2.name.lower():
                    # Same package with potentially conflicting specs
                    if not self._specs_compatible(req1.specifier, req2.specifier):
                        detected.append(ConflictIssue(
                            conflict_id=f"version_conflict_{len(detected)}",
                            conflict_type=ConflictType.VERSION_INCOMPATIBILITY,
                            severity=ConflictSeverity.HIGH,
                            packages=[req1.name, req2.name],
                            description=(
                                f"Version specifiers incompatible: "
                                f"{req1.specifier} vs {req2.specifier}"
                            ),
                            affected_dependencies=[
                                (req1.name, str(req1.specifier)),
                                (req2.name, str(req2.specifier))
                            ],
                            root_cause=(
                                "Conflicting version constraints on same package"
                            )
                        ))

        self.conflicts = detected
        return detected

    def _specs_compatible(self, spec1: SpecifierSet, spec2: SpecifierSet) -> bool:
        """Check if two version specifiers are compatible"""
        try:
            # If specs are identical, they're compatible
            if str(spec1) == str(spec2):
                return True
            
            # If either is empty (no constraint), they're compatible
            if len(spec1) == 0 or len(spec2) == 0:
                return True
             
            # Try a range of test versions
            test_versions = [
                "0.1.0", "0.9.0", "1.0.0", "1.5.0", "2.0.0",
                "3.0.0", "5.0.0", "6.2.4", "10.0.0"
            ]
            for test_ver in test_versions:
                try:
                    if test_ver in spec1 and test_ver in spec2:
                        return True
                except Exception:
                    pass
            return False
        except Exception:
            return False

    def build_dependency_graph(self, requirements: List[str]) -> Dict[str, DependencyNode]:
        """
        Build a dependency graph from requirements.
        
        Args:
            requirements: List of requirement strings
            
        Returns:
            Dictionary mapping package names to DependencyNode objects
        """
        graph = {}
        
        for req_str in requirements:
            try:
                req = Requirement(req_str)
                node = DependencyNode(
                    name=req.name,
                    version="*",
                    constraints=[str(req.specifier)] if req.specifier else []
                )
                graph[req.name.lower()] = node
            except Exception:
                pass
        
        self.dependency_graph = graph
        return graph

    def find_circular_dependencies(self) -> List[Tuple[str, str]]:
        """Find circular dependency patterns"""
        circles = []
        visited = set()
        
        def dfs(node_name: str, path: Set[str]) -> None:
            if node_name in path:
                circles.append((node_name, "->".join(path)))
                return
            
            if node_name in visited:
                return
            
            visited.add(node_name)
            path = path | {node_name}
            
            if node_name in self.dependency_graph:
                for dep in self.dependency_graph[node_name].requires:
                    dfs(dep, path)
        
        for node_name in self.dependency_graph:
            dfs(node_name, set())
        
        return circles


class VersionMatrixGenerator:
    """Generates version compatibility matrices"""

    def __init__(self):
        self.matrices: Dict[str, VersionMatrix] = {}

    def generate_matrix(self, package_name: str, versions: List[str]) -> VersionMatrix:
        """Generate a compatibility matrix for a package across versions."""
        matrix = VersionMatrix(package_name=package_name)
        matrix.versions_analyzed = sorted(versions, key=lambda v: pkg_version.parse(v))
        
        # Build compatibility matrix
        compatibility = {}
        for v1 in matrix.versions_analyzed:
            compatibility[v1] = {}
            for v2 in matrix.versions_analyzed:
                # Simple heuristic: same major.minor = compatible
                try:
                    pv1 = pkg_version.parse(v1)
                    pv2 = pkg_version.parse(v2)
                    compat = (pv1.major == pv2.major and pv1.minor == pv2.minor)
                    compatibility[v1][v2] = compat
                except Exception:
                    compatibility[v1][v2] = v1 == v2
        
        matrix.compatibility_matrix = compatibility
        
        # Find safe ranges
        if matrix.versions_analyzed:
            try:
                latest = max(
                    matrix.versions_analyzed,
                    key=lambda v: pkg_version.parse(v)
                )
                pv = pkg_version.parse(latest)
                matrix.recommended_version = latest
                matrix.safe_version_ranges = [
                    f">={pv.major}.{pv.minor}.0,"
                    f"<{pv.major}.{pv.minor + 1}.0"
                ]
            except Exception:
                pass
        
        self.matrices[package_name] = matrix
        return matrix


class SchemaValidator:
    """Validates schema compatibility across package versions"""

    def __init__(self, schemas_path: Optional[Path] = None):
        self.schemas: Dict[str, Dict] = {}
        self.compatibilities: List[SchemaCompatibility] = []
        
        if schemas_path:
            self._load_schemas(schemas_path)

    def _load_schemas(self, schemas_path: Path) -> None:
        """Load schema definitions from files"""
        if schemas_path.exists() and schemas_path.is_dir():
            for schema_file in schemas_path.glob("*.json"):
                try:
                    with open(schema_file) as f:
                        schema_data = json.load(f)
                        schema_name = schema_file.stem
                        self.schemas[schema_name] = schema_data
                except Exception:
                    pass

    def validate_package_compatibility(
        self,
        schema_name: str,
        schema_version: str,
        package_versions: Dict[str, str]
    ) -> SchemaCompatibility:
        """Validate package versions compatibility with a schema version."""
        compat = SchemaCompatibility(
            schema_name=schema_name,
            schema_version=schema_version
        )
        
        # Check each package
        for pkg_name, version in package_versions.items():
            if self._is_compatible(schema_name, pkg_name, version):
                compat.compatible_packages[pkg_name] = version
            else:
                compat.incompatibilities.append((pkg_name, version, schema_name))
        
        return compat

    def _is_compatible(self, schema_name: str, pkg_name: str, version: str) -> bool:
        """Check if package version is compatible with schema"""
        if schema_name not in self.schemas:
            return True
        
        schema = self.schemas[schema_name]
        if "incompatible_packages" in schema:
            incomp = schema["incompatible_packages"]
            if pkg_name in incomp:
                blocked_versions = incomp[pkg_name]
                if version in blocked_versions:
                    return False
        
        return True


class DependencyConflictResolver:
    """Main agent class for dependency conflict resolution"""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the agent with optional configuration"""
        self.config = self._load_config(config_path)
        self.analyzer = PipResolverAnalyzer()
        self.matrix_gen = VersionMatrixGenerator()
        self.validator = SchemaValidator()
        self.issues: List[ConflictIssue] = []
        self.resolutions: List[ResolutionResult] = []

    def _load_config(self, config_path: Optional[Path]) -> dict:
        """Load agent configuration from YAML file"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "agent_config.yaml"

        if not config_path.exists():
            return self._default_config()

        try:
            with open(config_path) as f:
                return yaml.safe_load(f) or self._default_config()
        except Exception:
            return self._default_config()

    def _default_config(self) -> dict:
        """Return default configuration"""
        return {
            "conflict_detection": {
                "enabled": True,
                "severity_threshold": "LOW"
            },
            "schema_validation": {
                "enabled": True,
                "strict_mode": False
            },
            "version_matrix": {
                "generate_on_conflict": True,
                "matrix_depth": 5
            },
            "auto_resolution": False
        }

    def analyze_requirements(self, requirements_path: Path) -> ResolutionResult:
        """Analyze requirements file for conflicts."""
        requirements = self._load_requirements(requirements_path)
        
        conflicts = self.analyzer.detect_conflicts(requirements)
        self.issues = conflicts
        
        result = ResolutionResult(
            success=len(conflicts) == 0,
            conflicts_found=len(conflicts),
            conflicts_resolved=0,
            critical_remaining=len([
                c for c in conflicts
                if c.severity == ConflictSeverity.CRITICAL
            ])
        )
        
        # Generate resolution recommendations
        for conflict in conflicts:
            if conflict.severity in [ConflictSeverity.HIGH, ConflictSeverity.CRITICAL]:
                result.recommendations.append(
                    f"Resolve {conflict.conflict_type.value}: {conflict.description}"
                )
        
        self.resolutions.append(result)
        return result

    def _load_requirements(self, path: Path) -> List[str]:
        """Load requirements from file"""
        requirements = []
        
        if not path.exists():
            return requirements
        
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    requirements.append(line)
        
        return requirements

    def validate_schema_compatibility(
        self,
        schema_name: str,
        requirements_path: Path
    ) -> Dict[str, Any]:
        """Validate requirements compatibility with a schema."""
        requirements = self._load_requirements(requirements_path)
        
        # Parse versions from requirements
        package_versions = {}
        for req_str in requirements:
            try:
                req = Requirement(req_str)
                package_versions[req.name] = str(req.specifier) if req.specifier else "*"
            except Exception:
                pass
        
        compat = self.validator.validate_package_compatibility(
            schema_name,
            "1.0.0",
            package_versions
        )
        
        return {
            "schema_name": schema_name,
            "compatible_packages": compat.compatible_packages,
            "incompatibilities": compat.incompatibilities,
            "is_compatible": len(compat.incompatibilities) == 0
        }

    def generate_version_matrix(
        self,
        package_names: List[str],
        versions_per_package: Dict[str, List[str]]
    ) -> Dict[str, VersionMatrix]:
        """Generate version compatibility matrices for packages."""
        matrices = {}
        
        for pkg_name in package_names:
            versions = versions_per_package.get(pkg_name, ["1.0.0"])
            matrix = self.matrix_gen.generate_matrix(pkg_name, versions)
            matrices[pkg_name] = matrix
        
        return matrices

    def export_analysis_report(self, output_path: Path) -> None:
        """Export analysis report to JSON file."""
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_issues": len(self.issues),
            "issues": [
                {
                    "id": issue.conflict_id,
                    "type": issue.conflict_type.value,
                    "severity": issue.severity.value,
                    "packages": issue.packages,
                    "description": issue.description,
                    "root_cause": issue.root_cause
                }
                for issue in self.issues
            ],
            "resolutions": [
                {
                    "success": res.success,
                    "conflicts_found": res.conflicts_found,
                    "conflicts_resolved": res.conflicts_resolved,
                    "critical_remaining": res.critical_remaining,
                    "recommendations": res.recommendations
                }
                for res in self.resolutions
            ]
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)


def main():
    """CLI entry point for the agent"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Dependency Conflict Resolver Agent"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze requirements for conflicts")
    analyze_parser.add_argument("--path", type=Path, default=Path("requirements.txt"))
    
    # validate-schema command
    schema_parser = subparsers.add_parser("validate-schema", help="Validate schema compatibility")
    schema_parser.add_argument("--schema", type=str, required=True)
    schema_parser.add_argument("--requirements", type=Path, default=Path("requirements.txt"))
    
    # generate-matrix command
    matrix_parser = subparsers.add_parser(
        "generate-matrix", help="Generate version matrix"
    )
    matrix_parser.add_argument(
        "--packages", type=str, required=True,
        help="Comma-separated package names"
    )
    matrix_parser.add_argument(
        "--versions", type=str,
        help="Comma-separated versions per package"
    )
    
    args = parser.parse_args()
    
    agent = DependencyConflictResolver()
    
    if args.command == "analyze":
        result = agent.analyze_requirements(args.path)
        print(json.dumps({
            "success": result.success,
            "conflicts_found": result.conflicts_found,
            "critical_remaining": result.critical_remaining,
            "recommendations": result.recommendations
        }, indent=2))
    
    elif args.command == "validate-schema":
        result = agent.validate_schema_compatibility(args.schema, args.requirements)
        print(json.dumps(result, indent=2))
    
    elif args.command == "generate-matrix":
        packages = [p.strip() for p in args.packages.split(",")]
        versions_per_package = {}
        if args.versions:
            # Parse versions in format: pkg1:v1,v2;pkg2:v1,v2
            for pkg_spec in args.versions.split(";"):
                pkg, versions = pkg_spec.split(":")
                versions_per_package[pkg.strip()] = [v.strip() for v in versions.split(",")]
        
        matrices = agent.generate_version_matrix(packages, versions_per_package)
        print(json.dumps({
            "matrices": {
                name: {
                    "package": matrix.package_name,
                    "versions_analyzed": matrix.versions_analyzed,
                    "safe_ranges": matrix.safe_version_ranges,
                    "recommended": matrix.recommended_version
                }
                for name, matrix in matrices.items()
            }
        }, indent=2))


if __name__ == "__main__":
    main()
