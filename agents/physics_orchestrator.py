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
import random
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


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
    
    def assess_imports(self, repo_root: Path) -> Dict[str, Any]:
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
            except (OSError, UnicodeDecodeError) as e:
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
    ) -> Dict[str, Any]:
        """
        ACTION PHASE: Execute the selected migrations.
        """
        print(f"\n{'='*60}")
        print(f"IMPORT MIGRATION - ACTION PHASE")
        print(f"{'='*60}")
        print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
        
        results: Dict[str, Any] = {
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
                
                # Split lines once at the start for efficiency
                lines = content.split('\n')
                
                # Apply migrations (in reverse line order to preserve line numbers)
                for m in sorted(file_migrations, key=lambda x: x.line_number, reverse=True):
                    results['migrations_attempted'] += 1
                    
                    # Find and replace the import in the lines list
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
                
                # Join lines once after all modifications
                content = '\n'.join(lines)
                
                # Write back if changed and not dry run
                if content != original_content:
                    results['files_modified'].add(file_path)
                    if not dry_run:
                        Path(file_path).write_text(content, encoding='utf-8')
                        
            except (OSError, UnicodeDecodeError) as e:
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
    ) -> Dict[str, Any]:
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


# =============================================================================
# ADDITIONAL PHYSICS-INSPIRED PATTERNS
# =============================================================================
# Based on research into diffusion models, PIML, energy landscapes, swarm
# intelligence, and task decomposition patterns for enhanced AI orchestration.
# =============================================================================


@dataclass
class FlowVector:
    """
    Represents a flow vector in decision space, inspired by Poisson Flow 
    Generative Models (PFGM) and fluid dynamics.
    
    Flow vectors guide agent navigation through complex decision landscapes,
    analogous to electromagnetic field lines or fluid streamlines.
    """
    position: Tuple[float, float]  # Current position in decision space
    velocity: Tuple[float, float]  # Current velocity (direction + magnitude)
    gradient: Tuple[float, float]  # Gradient of potential field at position
    diffusion_coefficient: float = 0.1  # Controls randomness/exploration
    
    def step(self, dt: float = 0.1) -> Tuple[float, float]:
        """
        Take a step following the flow, with optional diffusion (exploration).
        
        Uses simplified diffusion equation:
        dx = velocity * dt + gradient * dt + noise * sqrt(dt)
        """
        # Generate random noise for exploration (Brownian motion component)
        noise_x = (2 * self.diffusion_coefficient * dt) ** 0.5 * (random.random() - 0.5)
        noise_y = (2 * self.diffusion_coefficient * dt) ** 0.5 * (random.random() - 0.5)
        
        new_x = self.position[0] + self.velocity[0] * dt + self.gradient[0] * dt + noise_x
        new_y = self.position[1] + self.velocity[1] * dt + self.gradient[1] * dt + noise_y
        
        return (new_x, new_y)
    
    def magnitude(self) -> float:
        """Calculate velocity magnitude"""
        return math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)


class DiffusionFlowModel:
    """
    Diffusion and Flow Model for AI Agent Decision Navigation.
    
    Inspired by Poisson Flow Generative Models (PFGM) from electromagnetism
    and fluid dynamics. Models decision spaces as diffusive fields where 
    agents flow toward optima.
    
    Key Concepts:
    - Decision space as a potential field
    - Agents follow flow lines toward minima (optimal decisions)
    - Diffusion allows exploration of alternative paths
    - Poisson-like equations guide field structure: ∇²φ = ρ
    
    Applications:
    - Mental mapping navigation in complex decision landscapes
    - Pathfinding with context-awareness
    - Iterative review with flow convergence
    """
    
    def __init__(self, dimensions: int = 2, resolution: int = 10):
        self.dimensions = dimensions
        self.resolution = resolution
        self.potential_field: Dict[Tuple[int, ...], float] = {}
        self.flow_vectors: List[FlowVector] = []
        self.attractors: List[Tuple[float, ...]] = []  # Goal positions
        self.repulsors: List[Tuple[float, ...]] = []   # Obstacles
        
    def add_attractor(self, position: Tuple[float, ...], strength: float = 1.0) -> None:
        """Add an attractor (goal) to the field"""
        self.attractors.append((*position, strength))
        self._recalculate_field()
        
    def add_repulsor(self, position: Tuple[float, ...], strength: float = 1.0) -> None:
        """Add a repulsor (obstacle) to the field"""
        self.repulsors.append((*position, strength))
        self._recalculate_field()
        
    def _recalculate_field(self) -> None:
        """
        Recalculate potential field using simplified Poisson equation.
        
        φ(r) = Σ q_i / |r - r_i| for point charges (attractors/repulsors)
        """
        self.potential_field.clear()
        
        for i in range(self.resolution):
            for j in range(self.resolution):
                x = i / self.resolution
                y = j / self.resolution
                potential = 0.0
                
                # Attractive potential (negative, pulls toward)
                for ax, ay, strength in self.attractors:
                    dist = math.sqrt((x - ax)**2 + (y - ay)**2) + 0.01
                    potential -= strength / dist
                    
                # Repulsive potential (positive, pushes away)
                for rx, ry, strength in self.repulsors:
                    dist = math.sqrt((x - rx)**2 + (y - ry)**2) + 0.01
                    potential += strength / dist
                    
                self.potential_field[(i, j)] = potential
                
    def get_gradient(self, position: Tuple[float, float]) -> Tuple[float, float]:
        """
        Calculate gradient of potential field at position.
        
        Gradient points in direction of steepest descent (toward attractors).
        """
        x, y = position
        h = 1.0 / self.resolution
        
        # Numerical gradient using central differences
        i, j = int(x * self.resolution), int(y * self.resolution)
        i = max(1, min(i, self.resolution - 2))
        j = max(1, min(j, self.resolution - 2))
        
        grad_x = (self.potential_field.get((i+1, j), 0) - 
                  self.potential_field.get((i-1, j), 0)) / (2 * h)
        grad_y = (self.potential_field.get((i, j+1), 0) - 
                  self.potential_field.get((i, j-1), 0)) / (2 * h)
        
        # Negate for descent direction
        return (-grad_x, -grad_y)
    
    def create_flow_at(
        self, 
        position: Tuple[float, float],
        diffusion: float = 0.1
    ) -> FlowVector:
        """Create a flow vector at the given position"""
        gradient = self.get_gradient(position)
        # Initial velocity follows gradient
        velocity = gradient
        
        flow = FlowVector(
            position=position,
            velocity=velocity,
            gradient=gradient,
            diffusion_coefficient=diffusion
        )
        self.flow_vectors.append(flow)
        return flow
    
    def simulate_flow(
        self,
        start_position: Tuple[float, float],
        steps: int = 100,
        dt: float = 0.1
    ) -> List[Tuple[float, float]]:
        """
        Simulate agent flow from start position toward attractors.
        
        Returns trajectory as list of positions.
        """
        trajectory = [start_position]
        position = start_position
        
        for _ in range(steps):
            gradient = self.get_gradient(position)
            
            # Update position following flow
            new_x = position[0] + gradient[0] * dt
            new_y = position[1] + gradient[1] * dt
            
            # Clamp to bounds
            new_x = max(0.0, min(1.0, new_x))
            new_y = max(0.0, min(1.0, new_y))
            
            position = (new_x, new_y)
            trajectory.append(position)
            
            # Check for convergence
            if math.sqrt(gradient[0]**2 + gradient[1]**2) < 0.001:
                break
                
        return trajectory
    
    def integrate_with_mental_mapping(
        self,
        problem_position: Tuple[float, float],
        goal_position: Tuple[float, float]
    ) -> Dict[str, Any]:
        """
        Integration point for MentalMappingModel.
        
        Uses flow simulation to find optimal path from problem to goal.
        """
        self.add_attractor(goal_position, strength=2.0)
        trajectory = self.simulate_flow(problem_position)
        
        return {
            'trajectory': trajectory,
            'steps_to_goal': len(trajectory),
            'final_position': trajectory[-1],
            'convergence_distance': math.sqrt(
                (trajectory[-1][0] - goal_position[0])**2 +
                (trajectory[-1][1] - goal_position[1])**2
            )
        }


@dataclass
class EnergyState:
    """
    Represents a state in an energy landscape.
    
    Inspired by statistical mechanics and thermodynamics.
    """
    configuration: Dict[str, Any]
    energy: float = 0.0
    entropy: float = 0.0
    temperature: float = 1.0
    
    def free_energy(self) -> float:
        """
        Calculate Helmholtz free energy: F = E - T*S
        
        Lower free energy = more favorable state.
        """
        return self.energy - self.temperature * self.entropy
    
    def boltzmann_probability(self, reference_energy: float = 0.0) -> float:
        """
        Calculate Boltzmann probability: P ∝ exp(-E/kT)
        
        Higher probability = more likely to be selected.
        """
        delta_e = self.energy - reference_energy
        return math.exp(-delta_e / max(self.temperature, 0.01))


class EnergyLandscape:
    """
    Energy-Based Model for Decision Optimization.
    
    Models decision states as an energy landscape where minimization
    equates to optimal choices, drawing from thermodynamics.
    
    Key Concepts:
    - States have energy (cost/effort)
    - States have entropy (complexity/disorder)
    - Temperature controls exploration vs exploitation
    - Gibbs distribution for probabilistic selection
    - Free energy minimization for optimization
    
    Applications:
    - Self-appraisal as equilibrium-seeking
    - Feedback loops for iterative refinement
    - Decision confidence via Boltzmann probabilities
    """
    
    def __init__(self, temperature: float = 1.0):
        self.temperature = temperature
        self.states: List[EnergyState] = []
        self.history: List[EnergyState] = []
        self.partition_function: float = 0.0
        
    def add_state(self, state: EnergyState) -> None:
        """Add a state to the landscape"""
        state.temperature = self.temperature
        self.states.append(state)
        self._update_partition_function()
        
    def _update_partition_function(self) -> None:
        """
        Calculate partition function: Z = Σ exp(-E_i/kT)
        
        Used for normalization in Gibbs distribution.
        """
        min_energy = min(s.energy for s in self.states) if self.states else 0
        self.partition_function = sum(
            s.boltzmann_probability(min_energy) for s in self.states
        )
        
    def gibbs_probability(self, state: EnergyState) -> float:
        """
        Calculate Gibbs probability: P_i = exp(-E_i/kT) / Z
        
        Normalized probability for state selection.
        """
        if self.partition_function == 0:
            return 1.0 / max(len(self.states), 1)
            
        min_energy = min(s.energy for s in self.states) if self.states else 0
        return state.boltzmann_probability(min_energy) / self.partition_function
    
    def select_state(self) -> Optional[EnergyState]:
        """
        Select a state using Gibbs distribution.
        
        Lower energy states are more likely to be selected,
        with temperature controlling the selection sharpness.
        """
        if not self.states:
            return None
            
        # Calculate selection probabilities
        probabilities = [self.gibbs_probability(s) for s in self.states]
        
        # Deterministic selection (highest probability for low temperature)
        max_prob_idx = probabilities.index(max(probabilities))
        return self.states[max_prob_idx]
    
    def minimize_free_energy(self, max_iterations: int = 100) -> EnergyState:
        """
        Find state with minimum free energy through iterative refinement.
        
        Analogous to system reaching thermal equilibrium.
        """
        if not self.states:
            raise ValueError("No states in landscape")
            
        current = min(self.states, key=lambda s: s.free_energy())
        
        for iteration in range(max_iterations):
            self.history.append(current)
            
            # Find neighboring states (states with similar configurations)
            neighbors = [s for s in self.states 
                        if s != current and s.free_energy() < current.free_energy()]
            
            if not neighbors:
                break
                
            # Move to lowest free energy neighbor
            current = min(neighbors, key=lambda s: s.free_energy())
            
        return current
    
    def cool_system(self, cooling_rate: float = 0.95) -> None:
        """
        Simulated annealing: gradually reduce temperature.
        
        High temperature → exploration
        Low temperature → exploitation
        """
        self.temperature *= cooling_rate
        for state in self.states:
            state.temperature = self.temperature
        self._update_partition_function()
    
    def calculate_system_entropy(self) -> float:
        """
        Calculate total system entropy: S = -Σ P_i * ln(P_i)
        
        Higher entropy = more uncertain/disordered system.
        """
        if not self.states:
            return 0.0
            
        entropy = 0.0
        for state in self.states:
            p = self.gibbs_probability(state)
            if p > 0:
                entropy -= p * math.log(p)
                
        return entropy
    
    def integrate_with_self_appraisal(
        self,
        decision_quality: float,
        expected_confidence: float
    ) -> Dict[str, Any]:
        """
        Integration point for self-appraisal system.
        
        Models decision quality as energy minimization problem.
        """
        # Create energy state from decision outcome
        state = EnergyState(
            configuration={
                'quality': decision_quality,
                'confidence': expected_confidence
            },
            energy=1.0 - decision_quality,  # Lower quality = higher energy
            entropy=abs(decision_quality - expected_confidence),  # Surprise as entropy
            temperature=self.temperature
        )
        
        self.add_state(state)
        
        return {
            'free_energy': state.free_energy(),
            'probability': self.gibbs_probability(state),
            'system_entropy': self.calculate_system_entropy(),
            'recommendation': 'equilibrium_reached' if state.free_energy() < 0.5 else 'continue_refinement'
        }


@dataclass
class SwarmParticle:
    """
    Represents an agent in a swarm, inspired by particle swarm optimization.
    """
    position: Tuple[float, ...]
    velocity: Tuple[float, ...]
    personal_best_position: Tuple[float, ...] = field(default=None)
    personal_best_score: float = field(default=float('-inf'))
    
    def __post_init__(self):
        if self.personal_best_position is None:
            self.personal_best_position = self.position


class SwarmIntelligence:
    """
    Swarm Intelligence for Multi-Agent Coordination.
    
    Multi-agent systems that mimic particle behaviors (flocking, 
    repulsion/attraction) for collective decision-making.
    
    Key Concepts:
    - Particles (agents) have position and velocity
    - Attraction to personal best and global best
    - Repulsion from other particles (diversity)
    - Collective emergent behavior
    
    Applications:
    - Distributed orchestration
    - Influence propagation
    - Coordinated exploration of solution space
    
    Equations:
    - Velocity update: v = w*v + c1*r1*(pbest-x) + c2*r2*(gbest-x)
    - Position update: x = x + v
    """
    
    def __init__(
        self,
        num_particles: int = 10,
        dimensions: int = 2,
        inertia: float = 0.7,
        cognitive: float = 1.5,
        social: float = 1.5
    ):
        self.num_particles = num_particles
        self.dimensions = dimensions
        self.inertia = inertia  # w: tendency to continue current direction
        self.cognitive = cognitive  # c1: attraction to personal best
        self.social = social  # c2: attraction to global best
        
        self.particles: List[SwarmParticle] = []
        self.global_best_position: Optional[Tuple[float, ...]] = None
        self.global_best_score: float = float('-inf')
        self.iteration_history: List[Dict] = []
        
    def initialize_swarm(self, bounds: List[Tuple[float, float]]) -> None:
        """
        Initialize swarm with random positions within bounds.
        """
        self.particles = []
        
        for _ in range(self.num_particles):
            position = tuple(
                bounds[d][0] + (bounds[d][1] - bounds[d][0]) * 0.5
                for d in range(self.dimensions)
            )
            velocity = tuple(0.0 for _ in range(self.dimensions))
            
            particle = SwarmParticle(
                position=position,
                velocity=velocity
            )
            self.particles.append(particle)
            
    def evaluate_fitness(
        self,
        position: Tuple[float, ...],
        fitness_function: Optional[callable] = None
    ) -> float:
        """
        Evaluate fitness at a position.
        
        Default: negative distance from origin (maximize closeness)
        """
        if fitness_function:
            return fitness_function(position)
            
        # Default: inverse of distance from center
        return -math.sqrt(sum(x**2 for x in position))
    
    def update_swarm(
        self,
        fitness_function: Optional[callable] = None,
        bounds: Optional[List[Tuple[float, float]]] = None
    ) -> Dict[str, Any]:
        """
        Perform one iteration of swarm optimization.
        
        Updates velocities and positions of all particles.
        """
        iteration_result = {
            'particles': [],
            'global_best_score': self.global_best_score,
            'global_best_position': self.global_best_position
        }
        
        for particle in self.particles:
            # Evaluate fitness
            score = self.evaluate_fitness(particle.position, fitness_function)
            
            # Update personal best
            if score > particle.personal_best_score:
                particle.personal_best_score = score
                particle.personal_best_position = particle.position
                
            # Update global best
            if score > self.global_best_score:
                self.global_best_score = score
                self.global_best_position = particle.position
                
        # Update velocities and positions
        for particle in self.particles:
            new_velocity = []
            new_position = []
            
            for d in range(self.dimensions):
                # Velocity update equation
                r1, r2 = 0.5, 0.5  # Simplified random factors
                
                cognitive_component = self.cognitive * r1 * (
                    particle.personal_best_position[d] - particle.position[d]
                )
                social_component = self.social * r2 * (
                    (self.global_best_position[d] if self.global_best_position else 0) 
                    - particle.position[d]
                )
                
                v = (self.inertia * particle.velocity[d] + 
                     cognitive_component + social_component)
                new_velocity.append(v)
                
                # Position update
                p = particle.position[d] + v
                
                # Apply bounds if specified
                if bounds:
                    p = max(bounds[d][0], min(bounds[d][1], p))
                    
                new_position.append(p)
                
            particle.velocity = tuple(new_velocity)
            particle.position = tuple(new_position)
            
            iteration_result['particles'].append({
                'position': particle.position,
                'velocity': particle.velocity,
                'score': self.evaluate_fitness(particle.position, fitness_function)
            })
            
        iteration_result['global_best_score'] = self.global_best_score
        iteration_result['global_best_position'] = self.global_best_position
        self.iteration_history.append(iteration_result)
        
        return iteration_result
    
    def run_optimization(
        self,
        fitness_function: callable,
        bounds: List[Tuple[float, float]],
        max_iterations: int = 50
    ) -> Dict[str, Any]:
        """
        Run full swarm optimization.
        """
        self.initialize_swarm(bounds)
        
        for iteration in range(max_iterations):
            result = self.update_swarm(fitness_function, bounds)
            
            # Check for convergence (all particles near global best)
            if self.global_best_position:
                max_distance = max(
                    math.sqrt(sum(
                        (p.position[d] - self.global_best_position[d])**2
                        for d in range(self.dimensions)
                    ))
                    for p in self.particles
                )
                if max_distance < 0.01:
                    break
                    
        return {
            'best_position': self.global_best_position,
            'best_score': self.global_best_score,
            'iterations': len(self.iteration_history),
            'converged': len(self.iteration_history) < max_iterations
        }
    
    def coordinate_agents(
        self,
        agent_positions: List[Tuple[float, ...]],
        target_position: Tuple[float, ...]
    ) -> List[Tuple[float, ...]]:
        """
        Integration point for multi-agent coordination.
        
        Coordinates multiple agents to move toward target while
        maintaining separation (avoiding collisions).
        """
        # Initialize particles at agent positions
        self.particles = [
            SwarmParticle(position=pos, velocity=tuple(0.0 for _ in pos))
            for pos in agent_positions
        ]
        
        # Set target as global best
        self.global_best_position = target_position
        self.global_best_score = float('inf')
        
        # Single coordination step
        for particle in self.particles:
            new_velocity = []
            new_position = []
            
            for d in range(len(particle.position)):
                # Move toward target
                v = 0.1 * (target_position[d] - particle.position[d])
                new_velocity.append(v)
                new_position.append(particle.position[d] + v)
                
            particle.velocity = tuple(new_velocity)
            particle.position = tuple(new_position)
            
        return [p.position for p in self.particles]


@dataclass
class SubTask:
    """
    Represents a decomposed sub-task for parallel execution.
    """
    task_id: str
    description: str
    parent_task_id: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    
    # Task properties
    estimated_energy: float = 10.0
    priority: float = 0.5
    status: str = "pending"  # pending, running, completed, failed
    
    # Result storage
    result: Optional[Any] = None
    error: Optional[str] = None


class TaskDecomposer:
    """
    Task Decomposition and Orchestrator-Workers Pattern.
    
    Modular agents act as parallel processors with clear communication,
    analogous to parallel physical processes.
    
    Key Concepts:
    - Complex tasks decomposed into sub-tasks
    - Sub-tasks executed in parallel where possible
    - Dependency graph determines execution order
    - Results aggregated and propagated upward
    
    Applications:
    - Scalable orchestration
    - Balanced energy distribution
    - Redundancy through parallel paths
    
    Integrates with ActionPath for hierarchical planning.
    """
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.tasks: Dict[str, SubTask] = {}
        self.execution_order: List[List[str]] = []  # Batches of parallel tasks
        self.completed_tasks: List[str] = []
        
    def decompose_task(
        self,
        task: ActionPath,
        decomposition_strategy: str = "energy_balanced"
    ) -> List[SubTask]:
        """
        Decompose a high-level task into sub-tasks.
        
        Strategies:
        - energy_balanced: Split to balance energy across workers
        - impact_focused: Split by impact areas
        - dependency_chain: Split by sequential dependencies
        """
        parent_id = f"task_{id(task)}"
        sub_tasks = []
        
        if decomposition_strategy == "energy_balanced":
            # Split task energy evenly across workers
            energy_per_worker = task.potential_energy / self.max_workers
            
            for i in range(min(self.max_workers, int(task.potential_energy / 10))):
                sub_task = SubTask(
                    task_id=f"{parent_id}_sub_{i}",
                    description=f"{task.description} - Part {i+1}",
                    parent_task_id=parent_id,
                    estimated_energy=energy_per_worker,
                    priority=task.impact
                )
                sub_tasks.append(sub_task)
                self.tasks[sub_task.task_id] = sub_task
                
        elif decomposition_strategy == "impact_focused":
            # Create sub-tasks for different impact areas
            impact_areas = ["assessment", "implementation", "verification", "documentation"]
            
            for i, area in enumerate(impact_areas):
                sub_task = SubTask(
                    task_id=f"{parent_id}_{area}",
                    description=f"{task.description} - {area.capitalize()}",
                    parent_task_id=parent_id,
                    dependencies=[f"{parent_id}_{impact_areas[i-1]}"] if i > 0 else [],
                    estimated_energy=task.potential_energy / len(impact_areas),
                    priority=task.impact * (1.0 - i * 0.1)  # Earlier areas higher priority
                )
                sub_tasks.append(sub_task)
                self.tasks[sub_task.task_id] = sub_task
                
        elif decomposition_strategy == "dependency_chain":
            # Create sequential chain with dependencies
            phases = ["analyze", "plan", "execute", "verify"]
            
            for i, phase in enumerate(phases):
                sub_task = SubTask(
                    task_id=f"{parent_id}_{phase}",
                    description=f"{task.description} - {phase.capitalize()} Phase",
                    parent_task_id=parent_id,
                    dependencies=[f"{parent_id}_{phases[i-1]}"] if i > 0 else [],
                    estimated_energy=task.potential_energy * (0.1 if phase == "analyze" else 
                                                              0.2 if phase == "plan" else
                                                              0.5 if phase == "execute" else 0.2),
                    priority=task.urgency if phase in ["analyze", "plan"] else task.impact
                )
                sub_tasks.append(sub_task)
                self.tasks[sub_task.task_id] = sub_task
                
        return sub_tasks
    
    def build_execution_plan(self) -> List[List[str]]:
        """
        Build execution plan respecting dependencies.
        
        Returns batches of task IDs that can be executed in parallel.
        """
        self.execution_order = []
        remaining = set(self.tasks.keys())
        completed = set()
        
        while remaining:
            # Find tasks with all dependencies satisfied
            batch = []
            for task_id in remaining:
                task = self.tasks[task_id]
                if all(dep in completed for dep in task.dependencies):
                    batch.append(task_id)
                    
            if not batch:
                # Circular dependency or error
                break
                
            # Limit batch size to max_workers
            batch = batch[:self.max_workers]
            self.execution_order.append(batch)
            
            for task_id in batch:
                remaining.discard(task_id)
                completed.add(task_id)
                
        return self.execution_order
    
    def execute_batch(
        self,
        batch: List[str],
        executor: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Execute a batch of tasks (simulated parallel execution).
        """
        results = {}
        
        for task_id in batch:
            task = self.tasks[task_id]
            task.status = "running"
            
            try:
                if executor:
                    task.result = executor(task)
                else:
                    # Simulated execution
                    task.result = {
                        'task_id': task_id,
                        'energy_spent': task.estimated_energy,
                        'success': True
                    }
                    
                task.status = "completed"
                self.completed_tasks.append(task_id)
                results[task_id] = task.result
                
            except Exception as e:
                task.status = "failed"
                task.error = str(e)
                results[task_id] = {'error': str(e)}
                
        return results
    
    def run_orchestration(
        self,
        executor: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Run full task orchestration.
        """
        self.build_execution_plan()
        
        all_results = {}
        total_energy = 0.0
        
        for batch_idx, batch in enumerate(self.execution_order):
            batch_results = self.execute_batch(batch, executor)
            all_results[f"batch_{batch_idx}"] = batch_results
            
            # Sum energy spent
            for task_id in batch:
                total_energy += self.tasks[task_id].estimated_energy
                
        return {
            'total_batches': len(self.execution_order),
            'total_tasks': len(self.tasks),
            'completed_tasks': len(self.completed_tasks),
            'total_energy_spent': total_energy,
            'results': all_results
        }
    
    def integrate_with_action_path(self, action: ActionPath) -> Dict[str, Any]:
        """
        Integration point for ActionPath hierarchical planning.
        
        Decomposes an ActionPath into executable sub-tasks.
        """
        # Choose strategy based on action properties
        if action.potential_energy > 50:
            strategy = "energy_balanced"
        elif action.impact > 0.8:
            strategy = "impact_focused"
        else:
            strategy = "dependency_chain"
            
        sub_tasks = self.decompose_task(action, strategy)
        
        return {
            'strategy': strategy,
            'sub_tasks': len(sub_tasks),
            'execution_plan': self.build_execution_plan(),
            'estimated_total_energy': sum(t.estimated_energy for t in sub_tasks)
        }


class ReflectionLoop:
    """
    Reflection, Self-Appraisal, and Feedback Loop System.
    
    Agents perform explicit self-checks and corrections, inspired by 
    control systems and error minimization in physics.
    
    Key Concepts:
    - Record outcomes and compare to predictions
    - Adjust confidence thresholds based on track record
    - Implement feedback control for continuous improvement
    - Error minimization through iterative correction
    
    Applications:
    - Continuous learning from decisions
    - Threshold adjustment for decision-making
    - Drift correction in long-running processes
    
    Control Equation:
    u(t) = K_p * e(t) + K_i * ∫e(τ)dτ + K_d * de/dt
    (PID control for decision quality)
    """
    
    def __init__(
        self,
        k_proportional: float = 0.5,
        k_integral: float = 0.1,
        k_derivative: float = 0.05
    ):
        # PID control parameters
        self.k_p = k_proportional  # Immediate response to error
        self.k_i = k_integral      # Accumulated error correction
        self.k_d = k_derivative    # Rate of change response
        
        # Tracking
        self.decision_history: List[Dict[str, Any]] = []
        self.error_history: List[float] = []
        self.cumulative_error: float = 0.0
        self.last_error: float = 0.0
        
        # Adaptive thresholds
        self.confidence_threshold: float = 0.6
        self.risk_threshold: float = 0.5
        
    def record_decision(
        self,
        decision: Dict[str, Any],
        predicted_outcome: float,
        actual_outcome: float
    ) -> Dict[str, Any]:
        """
        Record a decision and its outcome for learning.
        """
        error = actual_outcome - predicted_outcome
        
        # Calculate PID correction
        self.cumulative_error += error
        error_derivative = error - self.last_error
        
        correction = (
            self.k_p * error +
            self.k_i * self.cumulative_error +
            self.k_d * error_derivative
        )
        
        self.last_error = error
        self.error_history.append(error)
        
        # Record decision with analysis
        record = {
            'decision': decision,
            'predicted_outcome': predicted_outcome,
            'actual_outcome': actual_outcome,
            'error': error,
            'correction': correction,
            'timestamp': datetime.now().isoformat()
        }
        self.decision_history.append(record)
        
        # Adjust thresholds based on track record
        self._adjust_thresholds()
        
        return {
            'error': error,
            'correction': correction,
            'new_confidence_threshold': self.confidence_threshold,
            'new_risk_threshold': self.risk_threshold,
            'recommendation': self._generate_recommendation(error, correction)
        }
    
    def _adjust_thresholds(self) -> None:
        """
        Adjust decision thresholds based on recent performance.
        """
        if len(self.error_history) < 5:
            return
            
        # Calculate recent error statistics
        recent_errors = self.error_history[-10:]
        avg_error = sum(recent_errors) / len(recent_errors)
        error_variance = sum((e - avg_error)**2 for e in recent_errors) / len(recent_errors)
        
        # If consistently overconfident (negative errors), increase confidence threshold
        if avg_error < -0.1:
            self.confidence_threshold = min(0.9, self.confidence_threshold + 0.02)
            
        # If consistently underconfident, decrease threshold
        elif avg_error > 0.1:
            self.confidence_threshold = max(0.4, self.confidence_threshold - 0.02)
            
        # Adjust risk threshold based on variance
        if error_variance > 0.1:
            self.risk_threshold = max(0.3, self.risk_threshold - 0.01)
        else:
            self.risk_threshold = min(0.7, self.risk_threshold + 0.01)
            
    def _generate_recommendation(self, error: float, correction: float) -> str:
        """
        Generate actionable recommendation based on error analysis.
        """
        if abs(error) < 0.05:
            return "calibration_optimal"
        elif error > 0.2:
            return "increase_confidence_in_predictions"
        elif error < -0.2:
            return "be_more_conservative"
        elif abs(correction) > 0.3:
            return "significant_adjustment_needed"
        else:
            return "minor_calibration_recommended"
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Calculate overall performance metrics.
        """
        if not self.error_history:
            return {'status': 'no_data'}
            
        errors = self.error_history
        
        return {
            'total_decisions': len(self.decision_history),
            'average_error': sum(errors) / len(errors),
            'error_variance': sum((e - sum(errors)/len(errors))**2 for e in errors) / len(errors),
            'max_error': max(abs(e) for e in errors),
            'current_confidence_threshold': self.confidence_threshold,
            'current_risk_threshold': self.risk_threshold,
            'cumulative_error': self.cumulative_error,
            'trend': 'improving' if len(errors) > 1 and abs(errors[-1]) < abs(errors[0]) else 'stable'
        }
    
    def reset_integration(self) -> None:
        """
        Reset integral term (useful when changing contexts).
        """
        self.cumulative_error = 0.0
        
    def integrate_with_orchestrator(
        self,
        orchestrator: PhysicsInspiredOrchestrator
    ) -> None:
        """
        Integration point for PhysicsInspiredOrchestrator.
        
        Updates orchestrator config based on learned thresholds.
        """
        orchestrator.config['confidence_threshold'] = self.confidence_threshold
        orchestrator.config['risk_tolerance'] = self.risk_threshold
