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

from .burndown_intelligence import BurndownMetrics, BurndownReport, BurndownTracker, compute_metrics
from .clustering import FindingClusterer, FindingFamily, build_finding_families
from .ingest import FindingSeverity, IngestMetrics, NormalizedFinding, SecurityIngestor, deduplicate_findings, normalize_finding
from .recurrence_prevention import RecurrencePrevention, SuppressionPattern, generate_suppression_patterns
from .scoring import Exploitability, RiskScorer, ScoredFamily, WavePlan, plan_waves
from .validation_gates import GateResult, GateStatus, ValidationGateEngine, ValidationGateReport, run_validation_gates
from .wave_executor import ExecutionResult, ExecutionStatus, WaveExecutionReport, WaveExecutor, execute_wave

__all__ = [
    # S1: Ingest
    'SecurityIngestor',
    'NormalizedFinding',
    'FindingSeverity',
    'IngestMetrics',
    'normalize_finding',
    'deduplicate_findings',
    # S2: Clustering
    'FindingClusterer',
    'FindingFamily',
    'build_finding_families',
    # S3: Scoring & Wave Planning
    'RiskScorer',
    'ScoredFamily',
    'Exploitability',
    'WavePlan',
    'plan_waves',
    # S4: Wave Executor
    'WaveExecutor',
    'ExecutionResult',
    'ExecutionStatus',
    'WaveExecutionReport',
    'execute_wave',
    # S5: Validation Gates
    'ValidationGateEngine',
    'ValidationGateReport',
    'GateResult',
    'GateStatus',
    'run_validation_gates',
    # S6: Recurrence Prevention
    'RecurrencePrevention',
    'SuppressionPattern',
    'generate_suppression_patterns',
    # S7: Burndown Intelligence
    'BurndownTracker',
    'BurndownMetrics',
    'BurndownReport',
    'compute_metrics',
]

__version__ = '1.0.0-m01'
