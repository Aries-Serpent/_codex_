"""
Phase 3 Security Factory Pipeline (Lane B: S1-S7)

A comprehensive security findings orchestration system that:
- Ingests findings from multiple security scanners (S1)
- Groups similar findings by root-cause family (S2)
- Prioritizes and plans remediation waves (S3)
- Executes parallel wave-based remediation (S4)
- Validates post-remediation security & regressions (S5)
- Prevents finding recurrence via policy enforcement (S6)
- Tracks metrics and provides adaptive feedback (S7)

Pipeline Flow:
  Scanner Sources → S1 Ingest → S2 Clustering → S3 Scoring & Wave Planning
  → S4 Wave Executor → S5 Validation Gates → S6 Recurrence Prevention → S7 Burndown

Author: Security Factory Lane B
Phase: 3 (Weeks 7-10)
Status: ACTIVE
"""

from .ingest import SecurityIngestor, normalize_finding, deduplicate_findings
from .clustering import FindingClusterer, build_finding_families
from .scoring import RiskScorer, plan_waves
from .wave_executor import WaveExecutor, execute_wave
from .validation_gates import ValidationGateEngine, run_validation_gates
from .recurrence_prevention import RecurrencePrevention, generate_suppression_patterns
from .burndown_intelligence import BurndownTracker, compute_metrics

__all__ = [
    # S1: Ingest
    'SecurityIngestor',
    'normalize_finding',
    'deduplicate_findings',
    # S2: Clustering
    'FindingClusterer',
    'build_finding_families',
    # S3: Scoring & Wave Planning
    'RiskScorer',
    'plan_waves',
    # S4: Wave Executor
    'WaveExecutor',
    'execute_wave',
    # S5: Validation Gates
    'ValidationGateEngine',
    'run_validation_gates',
    # S6: Recurrence Prevention
    'RecurrencePrevention',
    'generate_suppression_patterns',
    # S7: Burndown Intelligence
    'BurndownTracker',
    'compute_metrics',
]

__version__ = '1.0.0-m01'
