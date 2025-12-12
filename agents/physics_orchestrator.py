"""
Physics-Inspired Orchestrator for AI Agent Decision Making

This module implements a decision-making framework based on physical principles
to help AI Agents assess situations, weigh options, and determine optimal paths forward.

Core Principles:
1. Potential Energy: Measure the "energy" required for different actions
2. Momentum: Consider current trajectory and velocity of progress
3. Friction: Account for resistance and obstacles
4. Path Optimization: Find minimal energy/time path to goal
5. Force Vectors: Decompose complex decisions into force components
"""

import json
import math
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ActionType(Enum):
    """Types of actions the orchestrator can recommend"""
    AUDIT = "audit"
    REFACTOR = "refactor"
    TEST = "test"
    DOCUMENT = "document"
    DEPLOY = "deploy"
    OPTIMIZE = "optimize"
    DEBUG = "debug"
    RESEARCH = "research"


@dataclass
class ForceVector:
    """Represents a force influencing a decision"""
    name: str
    magnitude: float  # 0.0 to 1.0
    direction: float  # angle in radians
    priority: float = 1.0  # weight factor
    
    def get_components(self) -> Tuple[float, float]:
        """Get x, y components of force vector"""
        x = self.magnitude * math.cos(self.direction) * self.priority
        y = self.magnitude * math.sin(self.direction) * self.priority
        return x, y


@dataclass
class ActionPath:
    """Represents a potential action path with physics properties"""
    action_type: ActionType
    description: str
    
    # Physics properties
    potential_energy: float = 0.0  # Effort required (0-100)
    kinetic_energy: float = 0.0    # Progress velocity (0-100)
    friction: float = 0.0           # Resistance/obstacles (0-10)
    momentum: float = 0.0           # Current trajectory alignment (0-10)
    
    # Decision factors
    confidence: float = 0.0         # Confidence in success (0-1)
    risk: float = 0.0               # Risk level (0-1)
    impact: float = 0.0             # Expected impact (0-1)
    urgency: float = 0.0            # Time sensitivity (0-1)
    
    # Calculated scores
    total_energy: float = field(default=0.0, init=False)
    optimization_score: float = field(default=0.0, init=False)
    
    def calculate_total_energy(self) -> float:
        """
        Calculate total energy required for this path
        E_total = E_potential + E_kinetic - E_momentum + E_friction
        """
        self.total_energy = (
            self.potential_energy 
            + self.kinetic_energy 
            - self.momentum * 5.0  # Momentum reduces energy
            + self.friction * 10.0  # Friction increases energy
        )
        return self.total_energy
    
    def calculate_optimization_score(self) -> float:
        """
        Calculate optimization score using physics-inspired formula
        
        Score = (Impact × Confidence × Momentum) / (Energy × (1 + Risk) × (1 + Friction))
        
        Higher score = better path
        """
        # Avoid division by zero
        denominator = max(
            self.total_energy * (1 + self.risk) * (1 + self.friction),
            0.01
        )
        
        numerator = (
            self.impact 
            * self.confidence 
            * max(self.momentum, 0.1)  # Ensure positive momentum factor
            * (1 + self.urgency * 0.5)  # Urgency multiplier
        )
        
        self.optimization_score = numerator / denominator
        return self.optimization_score


@dataclass
class DecisionState:
    """Current state of the system for decision making"""
    current_position: str  # Where we are now
    goal_position: str     # Where we want to be
    available_resources: float = 1.0  # 0-1 scale
    time_available: float = 1.0       # 0-1 scale
    current_velocity: float = 0.5     # Progress rate 0-1
    context: Dict[str, any] = field(default_factory=dict)


class PhysicsInspiredOrchestrator:
    """
    Orchestrator that uses physics-inspired equations to determine best path forward.
    
    Philosophy: "Take time to think and weigh/assess the situation then action"
    
    Process:
    1. ASSESS: Gather state information and evaluate forces
    2. DELIBERATE: Calculate physics properties for each potential path
    3. OPTIMIZE: Find path with best energy/impact ratio
    4. ACT: Execute chosen path with confidence
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path)
        self.decision_history: List[Dict] = []
        self.force_vectors: List[ForceVector] = []
    
    def _load_config(self, config_path: Optional[Path]) -> Dict:
        """Load orchestrator configuration"""
        default_config = {
            'deliberation_time': 5.0,  # seconds to think before acting
            'confidence_threshold': 0.6,  # minimum confidence to act
            'energy_budget': 100.0,  # maximum energy to expend
            'risk_tolerance': 0.5,  # 0 = risk-averse, 1 = risk-tolerant
            'momentum_weight': 0.3,  # importance of momentum
            'friction_weight': 0.2,  # importance of friction
        }
        
        if config_path and config_path.exists():
            with open(config_path) as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def assess_situation(self, state: DecisionState) -> Dict[str, float]:
        """
        ASSESS: Analyze current situation and gather information
        
        Returns metrics about current state
        """
        print(f"\n{'='*60}")
        print(f"ASSESSMENT PHASE")
        print(f"{'='*60}")
        print(f"Current Position: {state.current_position}")
        print(f"Goal Position: {state.goal_position}")
        print(f"Available Resources: {state.available_resources:.2f}")
        print(f"Time Available: {state.time_available:.2f}")
        print(f"Current Velocity: {state.current_velocity:.2f}")
        
        # Calculate distance to goal (conceptual)
        distance = self._calculate_distance(state)
        
        # Calculate system entropy (disorder/complexity)
        entropy = self._calculate_entropy(state)
        
        # Calculate potential fields
        attractive_potential = self._calculate_attractive_potential(state)
        repulsive_potential = self._calculate_repulsive_potential(state)
        
        assessment = {
            'distance_to_goal': distance,
            'system_entropy': entropy,
            'attractive_potential': attractive_potential,
            'repulsive_potential': repulsive_potential,
            'net_potential': attractive_potential - repulsive_potential,
        }
        
        print(f"\nAssessment Results:")
        for key, value in assessment.items():
            print(f"  {key}: {value:.3f}")
        
        return assessment
    
    def deliberate_paths(
        self,
        state: DecisionState,
        possible_actions: List[ActionPath]
    ) -> List[ActionPath]:
        """
        DELIBERATE: Calculate physics properties for each path and rank them
        
        This is the "thinking" phase where we weigh all options
        """
        print(f"\n{'='*60}")
        print(f"DELIBERATION PHASE")
        print(f"{'='*60}")
        print(f"Analyzing {len(possible_actions)} possible action paths...")
        print(f"Deliberation time: {self.config['deliberation_time']}s")
        
        # Simulate deliberation time (in real use, this is actual thinking)
        import time
        time.sleep(min(self.config['deliberation_time'], 2.0))  # Cap for demo
        
        # Calculate physics properties for each path
        for i, path in enumerate(possible_actions):
            print(f"\n--- Analyzing Path {i+1}: {path.action_type.value} ---")
            print(f"Description: {path.description}")
            
            # Calculate energies
            total_energy = path.calculate_total_energy()
            print(f"  Potential Energy: {path.potential_energy:.2f}")
            print(f"  Kinetic Energy: {path.kinetic_energy:.2f}")
            print(f"  Momentum: {path.momentum:.2f}")
            print(f"  Friction: {path.friction:.2f}")
            print(f"  Total Energy: {total_energy:.2f}")
            
            # Calculate optimization score
            opt_score = path.calculate_optimization_score()
            print(f"  Impact: {path.impact:.2f}")
            print(f"  Confidence: {path.confidence:.2f}")
            print(f"  Risk: {path.risk:.2f}")
            print(f"  Urgency: {path.urgency:.2f}")
            print(f"  ⭐ Optimization Score: {opt_score:.4f}")
        
        # Sort by optimization score
        ranked_paths = sorted(
            possible_actions,
            key=lambda p: p.optimization_score,
            reverse=True
        )
        
        print(f"\n{'='*60}")
        print(f"RANKING SUMMARY")
        print(f"{'='*60}")
        for i, path in enumerate(ranked_paths):
            print(f"{i+1}. {path.action_type.value:12s} "
                  f"(score: {path.optimization_score:.4f}, "
                  f"energy: {path.total_energy:.1f})")
        
        return ranked_paths
    
    def optimize_path(
        self,
        ranked_paths: List[ActionPath],
        state: DecisionState
    ) -> Optional[ActionPath]:
        """
        OPTIMIZE: Select the best path based on constraints and optimization
        
        Returns the optimal path or None if no path meets criteria
        """
        print(f"\n{'='*60}")
        print(f"OPTIMIZATION PHASE")
        print(f"{'='*60}")
        
        # Apply constraints
        energy_budget = self.config['energy_budget']
        confidence_threshold = self.config['confidence_threshold']
        risk_tolerance = self.config['risk_tolerance']
        
        print(f"Constraints:")
        print(f"  Energy Budget: {energy_budget:.1f}")
        print(f"  Confidence Threshold: {confidence_threshold:.2f}")
        print(f"  Risk Tolerance: {risk_tolerance:.2f}")
        
        # Find first path that satisfies constraints
        for path in ranked_paths:
            meets_energy = path.total_energy <= energy_budget
            meets_confidence = path.confidence >= confidence_threshold
            meets_risk = path.risk <= risk_tolerance
            
            print(f"\nEvaluating: {path.action_type.value}")
            print(f"  ✓ Energy: {path.total_energy:.1f} <= {energy_budget:.1f}? {meets_energy}")
            print(f"  ✓ Confidence: {path.confidence:.2f} >= {confidence_threshold:.2f}? {meets_confidence}")
            print(f"  ✓ Risk: {path.risk:.2f} <= {risk_tolerance:.2f}? {meets_risk}")
            
            if meets_energy and meets_confidence and meets_risk:
                print(f"\n✅ OPTIMAL PATH FOUND: {path.action_type.value}")
                print(f"   Optimization Score: {path.optimization_score:.4f}")
                print(f"   Expected Impact: {path.impact:.2f}")
                return path
            else:
                print(f"   ❌ Does not meet constraints")
        
        print(f"\n⚠️  No path meets all constraints")
        return None
    
    def act(
        self,
        optimal_path: Optional[ActionPath],
        state: DecisionState
    ) -> Dict:
        """
        ACT: Execute the chosen path with full commitment
        
        Returns execution result
        """
        print(f"\n{'='*60}")
        print(f"ACTION PHASE")
        print(f"{'='*60}")
        
        if optimal_path is None:
            print("⚠️  DECISION: WAIT AND REASSESS")
            print("   No optimal path found. Recommend gathering more information.")
            
            result = {
                'action_taken': 'wait',
                'rationale': 'No path met constraints',
                'recommendation': 'Gather more information or adjust constraints',
                'timestamp': datetime.now().isoformat(),
            }
        else:
            print(f"🚀 EXECUTING: {optimal_path.action_type.value}")
            print(f"   Description: {optimal_path.description}")
            print(f"   Confidence: {optimal_path.confidence:.2%}")
            print(f"   Expected Impact: {optimal_path.impact:.2%}")
            print(f"   Energy Required: {optimal_path.total_energy:.1f}")
            
            result = {
                'action_taken': optimal_path.action_type.value,
                'description': optimal_path.description,
                'confidence': optimal_path.confidence,
                'expected_impact': optimal_path.impact,
                'energy_required': optimal_path.total_energy,
                'optimization_score': optimal_path.optimization_score,
                'timestamp': datetime.now().isoformat(),
            }
        
        # Record decision
        self.decision_history.append(result)
        
        return result
    
    def orchestrate(
        self,
        state: DecisionState,
        possible_actions: List[ActionPath]
    ) -> Dict:
        """
        Complete orchestration cycle: ASSESS → DELIBERATE → OPTIMIZE → ACT
        
        This is the main entry point for decision making
        """
        print(f"\n{'#'*60}")
        print(f"# PHYSICS-INSPIRED ORCHESTRATION CYCLE")
        print(f"{'#'*60}")
        
        # Phase 1: ASSESS
        self.assess_situation(state)
        
        # Phase 2: DELIBERATE
        ranked_paths = self.deliberate_paths(state, possible_actions)
        
        # Phase 3: OPTIMIZE
        optimal_path = self.optimize_path(ranked_paths, state)
        
        # Phase 4: ACT
        result = self.act(optimal_path, state)
        
        # Final summary
        print(f"\n{'#'*60}")
        print(f"# ORCHESTRATION COMPLETE")
        print(f"{'#'*60}")
        print(f"Decision: {result['action_taken']}")
        print(f"Timestamp: {result['timestamp']}")
        
        return result
    
    def _calculate_distance(self, state: DecisionState) -> float:
        """Calculate conceptual distance to goal"""
        # Simplified: use velocity and resources as proxy
        return (1.0 - state.available_resources) * 10.0
    
    def _calculate_entropy(self, state: DecisionState) -> float:
        """Calculate system entropy (disorder/complexity)"""
        # Higher entropy = more complex/disordered system
        complexity_factors = [
            1.0 - state.available_resources,
            1.0 - state.time_available,
            1.0 - state.current_velocity,
        ]
        return sum(complexity_factors) / len(complexity_factors)
    
    def _calculate_attractive_potential(self, state: DecisionState) -> float:
        """Calculate attractive potential towards goal"""
        # Goal pulls us forward
        return state.available_resources * state.time_available * 10.0
    
    def _calculate_repulsive_potential(self, state: DecisionState) -> float:
        """Calculate repulsive potential (obstacles)"""
        # Obstacles push us back
        return (1.0 - state.current_velocity) * 5.0
    
    def save_decision_history(self, output_path: Path) -> None:
        """Save decision history to file"""
        with open(output_path, 'w') as f:
            json.dump(self.decision_history, f, indent=2)
        print(f"Decision history saved to: {output_path}")


# Example usage
if __name__ == '__main__':
    # Create orchestrator
    orchestrator = PhysicsInspiredOrchestrator()
    
    # Define current state
    state = DecisionState(
        current_position="code_changes_made",
        goal_position="code_reviewed_and_merged",
        available_resources=0.8,
        time_available=0.6,
        current_velocity=0.7,
        context={
            'files_changed': 4,
            'tests_passing': True,
            'security_scan': 'passed',
        }
    )
    
    # Define possible action paths
    possible_actions = [
        ActionPath(
            action_type=ActionType.TEST,
            description="Run comprehensive test suite",
            potential_energy=30.0,
            kinetic_energy=20.0,
            friction=2.0,
            momentum=7.0,
            confidence=0.85,
            risk=0.2,
            impact=0.7,
            urgency=0.6,
        ),
        ActionPath(
            action_type=ActionType.AUDIT,
            description="Run full audit pipeline",
            potential_energy=40.0,
            kinetic_energy=15.0,
            friction=3.0,
            momentum=5.0,
            confidence=0.9,
            risk=0.1,
            impact=0.8,
            urgency=0.5,
        ),
        ActionPath(
            action_type=ActionType.DEPLOY,
            description="Deploy to pre-release",
            potential_energy=60.0,
            kinetic_energy=40.0,
            friction=5.0,
            momentum=3.0,
            confidence=0.7,
            risk=0.5,
            impact=0.9,
            urgency=0.8,
        ),
        ActionPath(
            action_type=ActionType.DOCUMENT,
            description="Update documentation",
            potential_energy=20.0,
            kinetic_energy=10.0,
            friction=1.0,
            momentum=8.0,
            confidence=0.95,
            risk=0.05,
            impact=0.5,
            urgency=0.3,
        ),
    ]
    
    # Run orchestration
    result = orchestrator.orchestrate(state, possible_actions)
    
    # Save decision history
    orchestrator.save_decision_history(Path('decision_history.json'))


# =============================================================================
# IMPORT MIGRATION ORCHESTRATOR
# =============================================================================

@dataclass
class ImportMigration:
    """Represents an import migration task with physics properties."""
    
    file_path: str
    old_import: str
    new_import: str
    line_number: int
    
    # Auto-calculated physics properties
    potential_energy: float = field(default=0.0, init=False)  # Effort required
    momentum: float = field(default=0.0, init=False)          # Alignment with patterns
    friction: float = field(default=0.0, init=False)          # Resistance/risk
    impact: float = field(default=0.0, init=False)            # Importance of file
    confidence: float = field(default=0.0, init=False)        # Straightforwardness
    risk: float = field(default=0.0, init=False)              # Could break things
    urgency: float = field(default=0.0, init=False)           # Actively causing issues
    optimization_score: float = field(default=0.0, init=False)
    
    def calculate_properties(self) -> None:
        """Calculate physics properties based on migration characteristics."""
        # Determine file importance (impact)
        if '/cli/' in self.file_path:
            self.impact = 0.9  # CLI files are high impact
        elif '/tests/' in self.file_path:
            self.impact = 0.7  # Tests are medium-high impact
        elif '/agents/' in self.file_path:
            self.impact = 0.85  # Agent files are high impact
        else:
            self.impact = 0.6
        
        # Determine effort (potential energy)
        # Simple imports need less energy
        self.potential_energy = 10.0 if 'import' in self.old_import else 20.0
        
        # Determine momentum (alignment with codebase patterns)
        # Migrating to src.* aligns with canonical pattern
        self.momentum = 0.9
        
        # Determine friction (obstacles)
        # Files in tests/training/ are related to training module - lower friction
        if '/tests/training/' in self.file_path or '/cli/' in self.file_path:
            self.friction = 0.1  # Training-related files have low friction
        else:
            self.friction = 0.3
        
        # Determine confidence
        self.confidence = 0.95  # Import changes are straightforward
        
        # Determine risk
        if 'functional_training' in self.old_import:
            self.risk = 0.3  # Critical module
        elif 'checkpoint' in self.old_import:
            self.risk = 0.25
        else:
            self.risk = 0.1
        
        # Determine urgency (deprecation warnings active)
        self.urgency = 0.8  # All deprecated imports are urgent
        
        # Calculate optimization score
        # Score = (Impact × Confidence × Momentum) / (Energy × (1 + Risk) × (1 + Friction))
        numerator = self.impact * self.confidence * self.momentum * (1 + self.urgency * 0.5)
        denominator = max(self.potential_energy * (1 + self.risk) * (1 + self.friction), 0.01)
        self.optimization_score = numerator / denominator


class ImportMigrationOrchestrator(PhysicsInspiredOrchestrator):
    """
    Specialized orchestrator for migrating deprecated imports to canonical paths.
    
    Uses physics-inspired logic to:
    1. ASSESS: Identify all deprecated imports
    2. DELIBERATE: Calculate physics properties for each migration
    3. OPTIMIZE: Rank migrations by optimization score
    4. ACT: Execute migrations in optimal order
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        super().__init__(config_path)
        self.migrations: List[ImportMigration] = []
        self.completed_migrations: List[ImportMigration] = []
        self.migration_map = {
            # Training module migrations
            'from training.': 'from src.training.',
            'from models.': 'from src.models.',
            'import training.': 'import src.training.',
            'import models.': 'import src.models.',
        }
    
    def assess_imports(self, repo_root: Path) -> Dict[str, any]:
        """
        ASSESS PHASE: Identify all deprecated imports in the codebase.
        
        Returns assessment metrics and populates self.migrations.
        """
        print(f"\n{'='*60}")
        print(f"IMPORT MIGRATION - ASSESSMENT PHASE")
        print(f"{'='*60}")
        
        self.migrations = []
        files_scanned = 0
        deprecated_found = 0
        
        # Scan Python files for deprecated imports
        for py_file in repo_root.rglob("*.py"):
            # Skip __pycache__ and other non-source directories
            if '__pycache__' in str(py_file):
                continue
            if '.git' in str(py_file):
                continue
                
            files_scanned += 1
            
            try:
                content = py_file.read_text(encoding='utf-8')
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    for old_pattern, new_pattern in self.migration_map.items():
                        if old_pattern in line and new_pattern not in line:
                            # Don't migrate files in the training/ or models/ compat layers
                            rel_path = str(py_file.relative_to(repo_root))
                            if rel_path.startswith('training/') or rel_path.startswith('models/'):
                                continue
                            if 'src/training/' in rel_path or 'src/models/' in rel_path:
                                continue
                                
                            migration = ImportMigration(
                                file_path=str(py_file),
                                old_import=line.strip(),
                                new_import=line.replace(old_pattern, new_pattern).strip(),
                                line_number=line_num,
                            )
                            migration.calculate_properties()
                            self.migrations.append(migration)
                            deprecated_found += 1
            except Exception as e:
                print(f"  Warning: Could not read {py_file}: {e}")
        
        assessment = {
            'files_scanned': files_scanned,
            'deprecated_found': deprecated_found,
            'unique_files': len(set(m.file_path for m in self.migrations)),
            'total_energy_required': sum(m.potential_energy for m in self.migrations),
            'average_risk': sum(m.risk for m in self.migrations) / max(len(self.migrations), 1),
        }
        
        print(f"\nAssessment Results:")
        print(f"  Files scanned: {assessment['files_scanned']}")
        print(f"  Deprecated imports found: {assessment['deprecated_found']}")
        print(f"  Unique files affected: {assessment['unique_files']}")
        print(f"  Total energy required: {assessment['total_energy_required']:.1f}")
        print(f"  Average risk: {assessment['average_risk']:.3f}")
        
        return assessment
    
    def deliberate_migrations(self) -> List[ImportMigration]:
        """
        DELIBERATE PHASE: Rank migrations by optimization score.
        """
        print(f"\n{'='*60}")
        print(f"IMPORT MIGRATION - DELIBERATION PHASE")
        print(f"{'='*60}")
        
        # Sort by optimization score (highest first)
        ranked = sorted(
            self.migrations,
            key=lambda m: m.optimization_score,
            reverse=True
        )
        
        print(f"\nTop migrations by optimization score:")
        for i, m in enumerate(ranked[:10]):
            print(f"  {i+1}. Score: {m.optimization_score:.4f} | "
                  f"Impact: {m.impact:.2f} | "
                  f"Risk: {m.risk:.2f}")
            print(f"      File: {Path(m.file_path).name}:{m.line_number}")
            print(f"      {m.old_import[:60]}...")
        
        return ranked
    
    def optimize_migration_plan(
        self,
        ranked_migrations: List[ImportMigration],
        energy_budget: float = 500.0
    ) -> List[ImportMigration]:
        """
        OPTIMIZE PHASE: Select migrations within energy budget.
        """
        print(f"\n{'='*60}")
        print(f"IMPORT MIGRATION - OPTIMIZATION PHASE")
        print(f"{'='*60}")
        print(f"Energy budget: {energy_budget:.1f}")
        
        selected = []
        total_energy = 0.0
        
        for migration in ranked_migrations:
            if total_energy + migration.potential_energy <= energy_budget:
                selected.append(migration)
                total_energy += migration.potential_energy
            else:
                break
        
        print(f"\nSelected {len(selected)} migrations within budget")
        print(f"Total energy: {total_energy:.1f}")
        print(f"Budget remaining: {energy_budget - total_energy:.1f}")
        
        return selected
    
    def execute_migrations(
        self,
        migrations: List[ImportMigration],
        dry_run: bool = True
    ) -> Dict[str, any]:
        """
        ACTION PHASE: Execute the selected migrations.
        """
        print(f"\n{'='*60}")
        print(f"IMPORT MIGRATION - ACTION PHASE")
        print(f"{'='*60}")
        print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
        
        results = {
            'migrations_attempted': 0,
            'migrations_successful': 0,
            'migrations_failed': 0,
            'files_modified': set(),
            'errors': [],
        }
        
        # Group migrations by file for efficiency
        by_file: Dict[str, List[ImportMigration]] = {}
        for m in migrations:
            by_file.setdefault(m.file_path, []).append(m)
        
        for file_path, file_migrations in by_file.items():
            try:
                content = Path(file_path).read_text(encoding='utf-8')
                original_content = content
                
                # Apply migrations (in reverse line order to preserve line numbers)
                for m in sorted(file_migrations, key=lambda x: x.line_number, reverse=True):
                    results['migrations_attempted'] += 1
                    
                    # Find and replace the import
                    lines = content.split('\n')
                    if m.line_number - 1 < len(lines):
                        old_line = lines[m.line_number - 1]
                        for old_pattern, new_pattern in self.migration_map.items():
                            if old_pattern in old_line:
                                new_line = old_line.replace(old_pattern, new_pattern)
                                lines[m.line_number - 1] = new_line
                                results['migrations_successful'] += 1
                                self.completed_migrations.append(m)
                                
                                if not dry_run:
                                    print(f"  ✓ {Path(file_path).name}:{m.line_number}")
                                    print(f"    - {old_line.strip()}")
                                    print(f"    + {new_line.strip()}")
                                break
                    
                    content = '\n'.join(lines)
                
                # Write back if changed and not dry run
                if content != original_content:
                    results['files_modified'].add(file_path)
                    if not dry_run:
                        Path(file_path).write_text(content, encoding='utf-8')
                        
            except Exception as e:
                results['migrations_failed'] += len(file_migrations)
                results['errors'].append(f"{file_path}: {str(e)}")
        
        results['files_modified'] = len(results['files_modified'])
        
        print(f"\nMigration Results:")
        print(f"  Attempted: {results['migrations_attempted']}")
        print(f"  Successful: {results['migrations_successful']}")
        print(f"  Failed: {results['migrations_failed']}")
        print(f"  Files modified: {results['files_modified']}")
        
        if results['errors']:
            print(f"\nErrors:")
            for error in results['errors']:
                print(f"  - {error}")
        
        return results
    
    def run_migration_cycle(
        self,
        repo_root: Path,
        energy_budget: float = 500.0,
        dry_run: bool = True
    ) -> Dict[str, any]:
        """
        Complete migration cycle using physics-inspired orchestration.
        
        Process:
        1. ASSESS: Identify deprecated imports
        2. DELIBERATE: Calculate optimization scores
        3. OPTIMIZE: Select migrations within budget
        4. ACT: Execute migrations
        """
        print(f"\n{'#'*60}")
        print(f"# IMPORT MIGRATION ORCHESTRATION CYCLE")
        print(f"{'#'*60}")
        
        # Phase 1: ASSESS
        assessment = self.assess_imports(repo_root)
        
        if not self.migrations:
            print("\n✅ No deprecated imports found. Codebase is clean!")
            return {'status': 'clean', 'assessment': assessment}
        
        # Phase 2: DELIBERATE
        ranked = self.deliberate_migrations()
        
        # Phase 3: OPTIMIZE
        selected = self.optimize_migration_plan(ranked, energy_budget)
        
        # Phase 4: ACT
        results = self.execute_migrations(selected, dry_run=dry_run)
        
        # Final summary
        print(f"\n{'#'*60}")
        print(f"# MIGRATION CYCLE COMPLETE")
        print(f"{'#'*60}")
        
        return {
            'status': 'completed',
            'assessment': assessment,
            'migrations_executed': results,
            'energy_spent': sum(m.potential_energy for m in self.completed_migrations),
            'momentum_gained': len(self.completed_migrations) * 0.1,
        }
