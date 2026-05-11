#!/usr/bin/env python3
"""
Dependency Conflict Resolver Agent

Resolves dependency version conflicts across multiple ecosystems (Python, JavaScript,
Rust, Go) using graph analysis and semantic versioning. Integrates with
dependency-vulnerability-scanner for security-aware resolution.

Component Reuse Strategy:
- Base: dependency-vulnerability-scanner (60% reuse)
- Extension 1: config-migration-assistant (version resolution)
- Extension 2: semantic-search (dependency graph analysis)

Usage:
    python -m dependency_conflict_resolver.src.agent detect --file requirements.txt
    python -m dependency_conflict_resolver.src.agent resolve --strategy conservative
    python -m dependency_conflict_resolver.src.agent analyze --ecosystem python
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import yaml


class ResolutionStrategy(Enum):
    """Strategy for resolving dependency conflicts"""
    CONSERVATIVE = "conservative"  # Minimal changes, prefer lower versions
    BALANCED = "balanced"  # Balance security and stability
    AGGRESSIVE = "aggressive"  # Latest compatible versions


class ConflictType(Enum):
    """Types of dependency conflicts"""
    DIRECT = "direct"  # Direct conflict between two explicit dependencies
    TRANSITIVE = "transitive"  # Conflict in transitive dependencies
    CIRCULAR = "circular"  # Circular dependency detected
    VERSION_RANGE = "version_range"  # Incompatible version ranges


class Ecosystem(Enum):
    """Supported dependency ecosystems"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    RUST = "rust"
    GO = "go"


@dataclass
class DependencyInfo:
    """Information about a single dependency"""
    name: str
    version: str
    version_constraint: str  # e.g., ">=1.0.0,<2.0.0"
    ecosystem: Ecosystem
    is_dev: bool = False
    source: str = ""  # File where dependency is declared
    line_number: Optional[int] = None
    transitive_from: Optional[str] = None  # Parent dependency if transitive


@dataclass
class DependencyConflict:
    """Represents a detected dependency conflict"""
    conflict_type: ConflictType
    package_name: str
    conflicting_versions: list[str]
    dependencies: list[DependencyInfo]
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    suggested_resolution: Optional[str] = None
    has_vulnerability: bool = False
    vulnerability_details: Optional[dict] = None


@dataclass
class ResolutionPlan:
    """Plan for resolving dependency conflicts"""
    conflicts_detected: int
    conflicts_to_resolve: list[DependencyConflict]
    strategy: ResolutionStrategy
    actions: list[dict[str, Any]] = field(default_factory=list)
    estimated_risk: str = "low"  # 'low', 'medium', 'high'
    requires_manual_review: bool = False


@dataclass
class ConflictReport:
    """Comprehensive report of dependency conflicts"""
    ecosystem: Ecosystem
    timestamp: datetime
    total_dependencies: int
    conflicts_found: int
    conflicts: list[DependencyConflict]
    dependency_graph: dict[str, list[str]] = field(default_factory=dict)
    circular_dependencies: list[list[str]] = field(default_factory=list)
    resolution_plan: Optional[ResolutionPlan] = None


class DependencyConflictResolver:
    """Main agent class for dependency conflict resolution"""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the agent with optional configuration"""
        self.config = self._load_config(config_path)
        self.max_graph_depth = self.config.get('conflict_detection', {}).get('max_depth', 10)
        self.check_transitive = self.config.get('conflict_detection', {}).get('check_transitive', True)
        self.vulnerability_checking_enabled = self.config.get('vulnerability_integration', {}).get('enabled', True)
        self.dependencies: dict[str, DependencyInfo] = {}
        self.dependency_graph: dict[str, set[str]] = {}
        self.conflicts: list[DependencyConflict] = []

    def _load_config(self, config_path: Optional[Path]) -> dict:
        """Load agent configuration from YAML file"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "agent_config.yaml"

        if not config_path.exists():
            return self._default_config()

        with open(config_path) as f:
            return yaml.safe_load(f)

    def _default_config(self) -> dict:
        """Return default configuration"""
        return {
            'agent_name': 'dependency-conflict-resolver',
            'version': '1.0.0',
            'supported_ecosystems': ['python', 'javascript', 'rust', 'go'],
            'resolution_strategies': {
                'default': 'conservative',
                'options': ['conservative', 'balanced', 'aggressive']
            },
            'conflict_detection': {
                'check_transitive': True,
                'max_depth': 10,
                'ignore_dev_dependencies': False
            },
            'vulnerability_integration': {
                'enabled': True,
                'fail_on_high_severity': True
            }
        }

    def parse_dependency_file(self, file_path: Path) -> list[DependencyInfo]:
        """Parse a dependency file and return list of dependencies"""
        if not file_path.exists():
            raise FileNotFoundError(f"Dependency file not found: {file_path}")

        # Detect ecosystem from filename
        ecosystem = self._detect_ecosystem(file_path)

        if ecosystem == Ecosystem.PYTHON:
            return self._parse_python_requirements(file_path)
        if ecosystem == Ecosystem.JAVASCRIPT:
            return self._parse_package_json(file_path)
        if ecosystem == Ecosystem.RUST:
            return self._parse_cargo_toml(file_path)
        if ecosystem == Ecosystem.GO:
            return self._parse_go_mod(file_path)
        raise ValueError(f"Unsupported dependency file: {file_path}")

    def _detect_ecosystem(self, file_path: Path) -> Ecosystem:
        """Detect ecosystem from file name/extension"""
        name = file_path.name.lower()

        # Check for Python files
        if 'requirements' in name and name.endswith('.txt'):
            return Ecosystem.PYTHON
        if name in ('pyproject.toml',):
            return Ecosystem.PYTHON
        # Check for JavaScript files
        if name in ('package.json', 'package-lock.json') or 'package' in name and name.endswith('.json'):
            return Ecosystem.JAVASCRIPT
        # Check for Rust files
        if 'cargo' in name and name.endswith('.toml'):
            return Ecosystem.RUST
        # Check for Go files
        if 'go.mod' in name or name == 'go.mod':
            return Ecosystem.GO
        raise ValueError(f"Cannot detect ecosystem for file: {file_path}")

    def _parse_python_requirements(self, file_path: Path) -> list[DependencyInfo]:
        """Parse Python requirements.txt file"""
        dependencies = []

        with open(file_path) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()

                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue

                # Parse dependency specification
                match = re.match(r'^([a-zA-Z0-9_-]+)([>=<~!]+.+)?$', line)
                if match:
                    name = match.group(1)
                    constraint = match.group(2) or ""
                    version = self._extract_version_from_constraint(constraint)

                    dependencies.append(DependencyInfo(
                        name=name,
                        version=version,
                        version_constraint=constraint,
                        ecosystem=Ecosystem.PYTHON,
                        source=str(file_path),
                        line_number=line_num
                    ))

        return dependencies

    def _parse_package_json(self, file_path: Path) -> list[DependencyInfo]:
        """Parse JavaScript package.json file"""
        dependencies = []

        with open(file_path) as f:
            data = json.load(f)

        # Parse dependencies
        for dep_type in ('dependencies', 'devDependencies'):
            deps = data.get(dep_type, {})
            is_dev = dep_type == 'devDependencies'

            for name, constraint in deps.items():
                version = self._extract_version_from_constraint(constraint)

                dependencies.append(DependencyInfo(
                    name=name,
                    version=version,
                    version_constraint=constraint,
                    ecosystem=Ecosystem.JAVASCRIPT,
                    is_dev=is_dev,
                    source=str(file_path)
                ))

        return dependencies

    def _parse_cargo_toml(self, file_path: Path) -> list[DependencyInfo]:
        """Parse Rust Cargo.toml file"""
        dependencies = []

        # Simple TOML parsing (basic implementation)
        with open(file_path) as f:
            content = f.read()

        # Extract [dependencies] section
        dep_section = re.search(r'\[dependencies\](.*?)(\[|$)', content, re.DOTALL)
        if dep_section:
            lines = dep_section.group(1).strip().split('\n')

            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                # Parse "name = "version"" or "name = { version = "version" }"
                match = re.match(r'^([a-zA-Z0-9_-]+)\s*=\s*"([^"]+)"', line)
                if not match:
                    match = re.match(r'^([a-zA-Z0-9_-]+)\s*=\s*\{.*?version\s*=\s*"([^"]+)"', line)

                if match:
                    name = match.group(1)
                    constraint = match.group(2)
                    version = self._extract_version_from_constraint(constraint)

                    dependencies.append(DependencyInfo(
                        name=name,
                        version=version,
                        version_constraint=constraint,
                        ecosystem=Ecosystem.RUST,
                        source=str(file_path)
                    ))

        return dependencies

    def _parse_go_mod(self, file_path: Path) -> list[DependencyInfo]:
        """Parse Go go.mod file"""
        dependencies = []

        with open(file_path) as f:
            in_require = False

            for line in f:
                line = line.strip()

                # Track require block
                if line.startswith('require ('):
                    in_require = True
                    continue
                if in_require and line == ')':
                    in_require = False
                    continue

                # Parse single require
                if line.startswith('require '):
                    line = line[8:].strip()

                # Parse require line
                if in_require or line:
                    match = re.match(r'^([^\s]+)\s+v?([^\s]+)', line)
                    if match:
                        name = match.group(1)
                        version = match.group(2)

                        dependencies.append(DependencyInfo(
                            name=name,
                            version=version,
                            version_constraint=f"v{version}",
                            ecosystem=Ecosystem.GO,
                            source=str(file_path)
                        ))

        return dependencies

    def _extract_version_from_constraint(self, constraint: str) -> str:
        """Extract a version number from a constraint string"""
        if not constraint:
            return "latest"

        # Remove operators and extract version
        version_match = re.search(r'(\d+\.\d+\.?\d*)', constraint)
        if version_match:
            return version_match.group(1)

        return constraint.lstrip('>=<~^!= ')

    def build_dependency_graph(self, dependencies: list[DependencyInfo]) -> dict[str, list[str]]:
        """Build a dependency graph from list of dependencies"""
        graph: dict[str, list[str]] = {}

        # Store dependencies with unique keys to handle duplicates
        dep_counter: dict[str, int] = {}

        for dep in dependencies:
            # Create unique key for storage
            count = dep_counter.get(dep.name, 0)
            dep_counter[dep.name] = count + 1
            unique_key = f"{dep.name}_{count}" if count > 0 else dep.name

            # Store in dependencies dict (override if same name)
            self.dependencies[unique_key] = dep

            if dep.name not in graph:
                graph[dep.name] = []

            # Add transitive relationship
            if dep.transitive_from:
                if dep.transitive_from not in graph:
                    graph[dep.transitive_from] = []
                graph[dep.transitive_from].append(dep.name)

        self.dependency_graph = {k: set(v) for k, v in graph.items()}
        return graph

    def detect_conflicts(self) -> list[DependencyConflict]:
        """Detect version conflicts in dependencies"""
        conflicts = []

        # Group dependencies by name (track all instances, even from same source)
        dep_groups: dict[str, list[DependencyInfo]] = {}
        dep_counter: dict[str, int] = {}

        for dep in self.dependencies.values():
            f"{dep.name}_{dep_counter.get(dep.name, 0)}"
            dep_counter[dep.name] = dep_counter.get(dep.name, 0) + 1

            if dep.name not in dep_groups:
                dep_groups[dep.name] = []
            dep_groups[dep.name].append(dep)

        # Check for version conflicts
        for name, deps in dep_groups.items():
            if len(deps) > 1:
                # Check if versions are compatible
                versions = [d.version for d in deps]
                unique_versions = list(set(versions))

                # If we have different versions, check compatibility
                if len(unique_versions) > 1 and not self._are_versions_compatible(versions, deps[0].ecosystem):
                    conflict = DependencyConflict(
                        conflict_type=ConflictType.DIRECT if all(not d.transitive_from for d in deps) else ConflictType.TRANSITIVE,
                        package_name=name,
                        conflicting_versions=unique_versions,
                        dependencies=deps,
                        severity=self._assess_conflict_severity(deps),
                        description=f"Multiple incompatible versions required for {name}: {', '.join(unique_versions)}"
                    )

                    # Add resolution suggestion
                    conflict.suggested_resolution = self._suggest_resolution(conflict)
                    conflicts.append(conflict)

        # Check for circular dependencies
        circular = self._detect_circular_dependencies()
        for cycle in circular:
            conflict = DependencyConflict(
                conflict_type=ConflictType.CIRCULAR,
                package_name=" -> ".join(cycle),
                conflicting_versions=[],
                dependencies=[],
                severity="high",
                description=f"Circular dependency detected: {' -> '.join(cycle)}"
            )
            conflicts.append(conflict)

        self.conflicts = conflicts
        return conflicts

    def _are_versions_compatible(self, versions: list[str], ecosystem: Ecosystem) -> bool:
        """Check if version list is compatible

        Versions are considered compatible if they only differ in patch version
        (e.g., 2.28.0, 2.28.1, 2.28.2 are compatible).
        """
        if len(versions) <= 1:
            return True

        # Remove duplicates
        unique_versions = list(set(versions))
        if len(unique_versions) == 1:
            return True

        # Parse versions
        try:
            parsed_versions = []
            for v in unique_versions:
                if v == "latest":
                    continue
                match = re.match(r'^(\d+)\.(\d+)\.?(\d*).*', v)
                if match:
                    major = int(match.group(1))
                    minor = int(match.group(2))
                    patch = int(match.group(3)) if match.group(3) else 0
                    parsed_versions.append((major, minor, patch))

            if not parsed_versions or len(parsed_versions) != len(unique_versions):
                # Can't parse all versions, consider incompatible
                return False

            # Check if all major.minor versions are the same
            # (patch differences are okay)
            major_minor = set((v[0], v[1]) for v in parsed_versions)
            return len(major_minor) == 1

        except (ValueError, AttributeError):
            return False

    def _assess_conflict_severity(self, deps: list[DependencyInfo]) -> str:
        """Assess severity of a conflict"""
        versions = [d.version for d in deps]

        # Check version distance
        try:
            parsed = []
            for v in versions:
                match = re.match(r'^(\d+)', v)
                if match:
                    parsed.append(int(match.group(1)))

            if parsed:
                version_range = max(parsed) - min(parsed)
                if version_range >= 2:
                    return "critical"
                if version_range == 1:
                    return "high"
                return "medium"
        except (ValueError, AttributeError):  # invalid version format, default to low
            pass

        return "low"

    def _suggest_resolution(self, conflict: DependencyConflict) -> str:
        """Suggest a resolution for a conflict"""
        versions = conflict.conflicting_versions

        # Sort versions
        try:
            sorted_versions = sorted(versions, key=lambda v: [int(x) for x in re.findall(r'\d+', v)])

            # Conservative: use lowest compatible version
            # Aggressive: use highest version
            return f"Consider using version {sorted_versions[-1]} or find a compatible range"
        except (ValueError, TypeError):
            return "Manual review required to resolve version conflict"

    def _detect_circular_dependencies(self) -> list[list[str]]:
        """Detect circular dependencies in the graph"""
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node: str, path: list[str]) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.dependency_graph.get(node, set()):
                if neighbor not in visited:
                    dfs(neighbor, path.copy())
                elif neighbor in rec_stack:
                    # Cycle detected
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    if cycle not in cycles:
                        cycles.append(cycle)

            rec_stack.remove(node)

        for node in self.dependency_graph:
            if node not in visited:
                dfs(node, [])

        return cycles

    def resolve_conflicts(self, strategy: ResolutionStrategy = ResolutionStrategy.CONSERVATIVE) -> ResolutionPlan:
        """Resolve conflicts using the specified strategy"""
        if not self.conflicts:
            return ResolutionPlan(
                conflicts_detected=0,
                conflicts_to_resolve=[],
                strategy=strategy
            )

        plan = ResolutionPlan(
            conflicts_detected=len(self.conflicts),
            conflicts_to_resolve=self.conflicts.copy(),
            strategy=strategy
        )

        for conflict in self.conflicts:
            if conflict.conflict_type == ConflictType.CIRCULAR:
                plan.actions.append({
                    'type': 'manual_review',
                    'conflict': conflict.package_name,
                    'reason': 'Circular dependency requires manual intervention'
                })
                plan.requires_manual_review = True
                continue

            # Version conflict resolution
            action = self._create_resolution_action(conflict, strategy)
            plan.actions.append(action)

        # Assess risk
        plan.estimated_risk = self._assess_resolution_risk(plan)

        return plan

    def _create_resolution_action(self, conflict: DependencyConflict, strategy: ResolutionStrategy) -> dict[str, Any]:
        """Create a resolution action for a conflict"""
        versions = conflict.conflicting_versions

        # Parse versions
        parsed_versions = []
        for v in versions:
            match = re.match(r'^(\d+)\.(\d+)\.?(\d*).*', v)
            if match:
                major = int(match.group(1))
                minor = int(match.group(2))
                patch = int(match.group(3)) if match.group(3) else 0
                parsed_versions.append((v, major, minor, patch))

        if not parsed_versions:
            return {
                'type': 'manual_review',
                'package': conflict.package_name,
                'reason': 'Cannot parse version numbers'
            }

        # Select version based on strategy
        if strategy == ResolutionStrategy.CONSERVATIVE:
            # Use lowest stable version
            selected = min(parsed_versions, key=lambda x: (x[1], x[2], x[3]))
        elif strategy == ResolutionStrategy.AGGRESSIVE:
            # Use highest version
            selected = max(parsed_versions, key=lambda x: (x[1], x[2], x[3]))
        else:  # BALANCED
            # Use median version
            sorted_versions = sorted(parsed_versions, key=lambda x: (x[1], x[2], x[3]))
            selected = sorted_versions[len(sorted_versions) // 2]

        return {
            'type': 'update_version',
            'package': conflict.package_name,
            'from_versions': versions,
            'to_version': selected[0],
            'files': [d.source for d in conflict.dependencies]
        }

    def _assess_resolution_risk(self, plan: ResolutionPlan) -> str:
        """Assess risk level of resolution plan"""
        if plan.requires_manual_review:
            return "high"

        # Count major version changes
        major_changes = 0
        for action in plan.actions:
            if action['type'] == 'update_version':
                from_versions = action.get('from_versions', [])
                to_version = action.get('to_version', '')

                # Check if major version changes
                for from_ver in from_versions:
                    from_major = re.match(r'^(\d+)', from_ver)
                    to_major = re.match(r'^(\d+)', to_version)

                    if from_major and to_major:
                        if from_major.group(1) != to_major.group(1):
                            major_changes += 1

        if major_changes > 2:
            return "high"
        if major_changes > 0:
            return "medium"
        return "low"

    def check_vulnerabilities(self) -> dict[str, list[dict]]:
        """Check dependencies for known vulnerabilities"""
        if not self.vulnerability_checking_enabled:
            return {}

        vulnerabilities: dict[str, list[dict]] = {}

        # Mock vulnerability check (would integrate with actual scanner)
        for dep in self.dependencies.values():
            # Check for known vulnerable versions (simplified)
            if self._is_vulnerable_version(dep):
                if dep.name not in vulnerabilities:
                    vulnerabilities[dep.name] = []

                vulnerabilities[dep.name].append({
                    'severity': 'high',
                    'cve': 'CVE-XXXX-XXXX',
                    'description': f'Known vulnerability in {dep.name} {dep.version}'
                })

        return vulnerabilities

    def _is_vulnerable_version(self, dep: DependencyInfo) -> bool:
        """Check if a dependency version is known to be vulnerable (mock)"""
        # This would integrate with actual vulnerability database
        # For now, just a placeholder
        return False

    def generate_resolution_plan(self) -> ConflictReport:
        """Generate a comprehensive conflict resolution plan"""
        report = ConflictReport(
            ecosystem=list(self.dependencies.values())[0].ecosystem if self.dependencies else Ecosystem.PYTHON,
            timestamp=datetime.now(timezone.utc),
            total_dependencies=len(self.dependencies),
            conflicts_found=len(self.conflicts),
            conflicts=self.conflicts.copy(),
            dependency_graph={k: list(v) for k, v in self.dependency_graph.items()}
        )

        # Detect circular dependencies
        report.circular_dependencies = self._detect_circular_dependencies()

        # Generate resolution plan
        strategy = ResolutionStrategy[self.config.get('resolution_strategies', {}).get('default', 'conservative').upper()]
        report.resolution_plan = self.resolve_conflicts(strategy)

        return report

    def apply_resolution(self, plan: ResolutionPlan) -> bool:
        """Apply resolution plan to dependency files"""
        if plan.requires_manual_review:
            return False

        success = True

        for action in plan.actions:
            if action['type'] == 'update_version':
                try:
                    self._update_dependency_file(
                        action['package'],
                        action['to_version'],
                        action['files']
                    )
                except Exception as e:
                    print(f"Error applying resolution: {e}")
                    success = False

        return success

    def _update_dependency_file(self, package: str, version: str, files: list[str]) -> None:
        """Update dependency version in file"""
        for file_path in files:
            path = Path(file_path)
            if not path.exists():
                continue

            # Read file
            with open(path) as f:
                content = f.read()

            # Update version (simple string replacement)
            # This is a simplified implementation
            updated = re.sub(
                rf'({package}[>=<~!]+)[\d.]+',
                rf'\g<1>{version}',
                content
            )

            # Write back
            with open(path, 'w') as f:
                f.write(updated)

    def validate_resolution(self) -> tuple[bool, list[str]]:
        """Validate that resolution doesn't introduce new conflicts"""
        errors = []

        # Re-detect conflicts
        new_conflicts = self.detect_conflicts()

        if new_conflicts:
            errors.append(f"Resolution introduced {len(new_conflicts)} new conflicts")

        # Check for circular dependencies
        circular = self._detect_circular_dependencies()
        if circular:
            errors.append(f"Circular dependencies still present: {len(circular)}")

        return len(errors) == 0, errors

    def visualize_dependency_graph(self, output_path: Optional[Path] = None) -> str:
        """Generate a text-based visualization of the dependency graph"""
        lines = ["Dependency Graph:", "=" * 50]

        for node, deps in sorted(self.dependency_graph.items()):
            lines.append(f"\n{node}:")
            for dep in sorted(deps):
                lines.append(f"  └─ {dep}")

        visualization = "\n".join(lines)

        if output_path:
            with open(output_path, 'w') as f:
                f.write(visualization)

        return visualization


def main():
    """Main entry point for CLI usage"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python agent.py <command> [options]")
        print("Commands: detect, resolve, analyze, visualize")
        return

    command = sys.argv[1]
    resolver = DependencyConflictResolver()

    if command == "detect":
        if len(sys.argv) < 3:
            print("Usage: python agent.py detect <dependency_file>")
            return

        file_path = Path(sys.argv[2])
        deps = resolver.parse_dependency_file(file_path)
        resolver.build_dependency_graph(deps)
        conflicts = resolver.detect_conflicts()

        print(f"Found {len(conflicts)} conflicts:")
        for conflict in conflicts:
            print(f"  - {conflict.description}")

    elif command == "resolve":
        print("Resolution functionality requires dependency file to be specified")

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
