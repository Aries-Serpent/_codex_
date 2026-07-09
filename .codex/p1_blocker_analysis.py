"""
P1 BLOCKER: Training/ML Circular Dependency Analysis & Resolution Plan

This module contains comprehensive analysis of circular dependencies between
codex.training and codex_ml, and documents the protocol-based solution.
"""

# ============================================================================
# CIRCULAR DEPENDENCY ANALYSIS
# ============================================================================

CIRCULAR_DEPENDENCIES = {
    "cycle_1_training_to_codex_ml_utils": {
        "description": "training.trainer imports codex_ml utilities",
        "path": "src/training/trainer.py:22",
        "import": "from codex_ml.utils.repro import set_seed",
        "severity": "medium",
        "fix_strategy": "lazy_import_with_fallback",
    },
    "cycle_2_functional_training_to_logging": {
        "description": "functional_training imports codex_ml logging",
        "path": "src/training/functional_training.py:34",
        "imports": [
            "from codex_ml.logging.file_logger import FileLogger",
            "from codex_ml.logging.run_metadata import log_run_metadata",
            "from codex_ml.telemetry import EXAMPLES_PROCESSED, TRAIN_STEP_DURATION",
        ],
        "severity": "high",
        "fix_strategy": "protocol_interface + lazy_import",
    },
    "cycle_3_functional_training_to_checkpoint": {
        "description": "functional_training imports codex_ml checkpointing",
        "path": "src/training/functional_training.py:37-43",
        "imports": [
            "from codex_ml.utils.checkpointing import dump_rng_state, load_rng_state, load_training_checkpoint, save_checkpoint",
        ],
        "severity": "high",
        "fix_strategy": "protocol_interface + lazy_import",
    },
    "cycle_4_engine_hf_trainer_to_codex_ml": {
        "description": "engine_hf_trainer imports multiple codex_ml modules",
        "path": "src/training/engine_hf_trainer.py:20-30",
        "imports": [
            "from codex_ml.data_utils import split_dataset",
            "from codex_ml.monitoring.async_writer import AsyncLogFile",
            "from codex_ml.monitoring.codex_logging import ...",
            "from codex_ml.peft.peft_adapter import apply_lora",
        ],
        "severity": "high",
        "fix_strategy": "protocol_interface + lazy_import",
    },
    "cycle_5_checkpoint_manager_to_checkpointing": {
        "description": "checkpoint_manager imports codex_ml checkpointing utils",
        "path": "src/training/checkpoint_manager.py",
        "severity": "medium",
        "fix_strategy": "protocol_interface + lazy_import",
    },
    "cycle_6_seed_to_repro": {
        "description": "seed module imports codex_ml repro utils",
        "path": "src/training/seed.py:5",
        "import": "from codex_ml.utils.repro import set_seed as _set_seed",
        "severity": "low",
        "fix_strategy": "lazy_import_with_fallback",
    },
}

# ============================================================================
# PROTOCOL-BASED SOLUTION
# ============================================================================

PROTOCOLS_CREATED = [
    "DatasetProtocol",
    "ModelProtocol",
    "OptimizerProtocol",
    "SchedulerProtocol",
    "MetricsProtocol",
    "LossProtocol",
    "EvaluatorProtocol",
    "CheckpointerProtocol",
    "TrainerProtocol",
    "LoggerProtocol",
]

REFACTORING_PLAN = """
PHASE 1: Protocols & Lazy Imports (Week 1)
==========================================
✓ 1.1 Create codex/protocols/ml_protocols.py with zero dependencies
✓ 1.2 Create codex/protocols/__init__.py with exports
✓ 1.3 Add TYPE_CHECKING guards to all trainer modules
✓ 1.4 Implement lazy imports for codex_ml dependencies
- 1.5 Update type hints to use protocols where possible
- 1.6 Add fallback implementations for optional dependencies

PHASE 2: Break Cycle 1-2 (Week 1)
==================================
- 2.1 Refactor training.trainer to use lazy imports
- 2.2 Refactor training.functional_training to use LoggerProtocol
- 2.3 Replace direct imports with TYPE_CHECKING guards
- 2.4 Test: training can import independently
- 2.5 Test: codex_ml can import independently

PHASE 3: Break Cycle 3-4 (Week 2)
==================================
- 3.1 Refactor checkpointing utilities to use CheckpointerProtocol
- 3.2 Refactor engine_hf_trainer to use multiple protocols
- 3.3 Replace direct imports with lazy resolution
- 3.4 Test: No circular imports at module load time

PHASE 4: Break Remaining Cycles (Week 2)
========================================
- 4.1 Apply pattern to remaining 5+ cycles
- 4.2 Validate no new circular imports introduced
- 4.3 Full test suite passes

PHASE 5: Validation & Documentation (Week 3)
=============================================
- 5.1 Bootstrap test: import codex_ml independently
- 5.2 Bootstrap test: import training independently  
- 5.3 Bootstrap test: import both bidirectionally
- 5.4 mypy strict mode validation
- 5.5 Create migration guide
- 5.6 Update architecture documentation
"""

# ============================================================================
# KEY FILES FOR REFACTORING
# ============================================================================

FILES_TO_REFACTOR = [
    {
        "file": "src/training/trainer.py",
        "cycles": 1,
        "imports_to_fix": ["from codex_ml.utils.repro import set_seed"],
        "strategy": "lazy_import_with_fallback",
    },
    {
        "file": "src/training/functional_training.py",
        "cycles": 2,
        "imports_to_fix": [
            "from codex_ml.logging.file_logger import FileLogger",
            "from codex_ml.logging.run_metadata import log_run_metadata",
            "from codex_ml.telemetry import EXAMPLES_PROCESSED, TRAIN_STEP_DURATION",
            "from codex_ml.utils.checkpointing import ...",
            "from codex_ml.utils.experiment_tracking_mlflow import ...",
            "from codex_ml.utils.hf_pinning import ...",
        ],
        "strategy": "protocol_interface + lazy_import",
    },
    {
        "file": "src/training/engine_hf_trainer.py",
        "cycles": 2,
        "imports_to_fix": [
            "from codex_ml.data_utils import split_dataset",
            "from codex_ml.monitoring.async_writer import AsyncLogFile",
            "from codex_ml.monitoring.codex_logging import ...",
            "from codex_ml.peft.peft_adapter import apply_lora",
            "from codex_ml.utils.checkpointing import ...",
        ],
        "strategy": "protocol_interface + lazy_import",
    },
    {
        "file": "src/training/checkpoint_manager.py",
        "cycles": 1,
        "imports_to_fix": ["from codex_ml.utils.checkpointing import ..."],
        "strategy": "protocol_interface + lazy_import",
    },
    {
        "file": "src/training/seed.py",
        "cycles": 1,
        "imports_to_fix": ["from codex_ml.utils.repro import set_seed"],
        "strategy": "lazy_import_with_fallback",
    },
]

# ============================================================================
# LAZY IMPORT PATTERN
# ============================================================================

LAZY_IMPORT_PATTERN = '''
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codex_ml.logging import FileLogger
    from codex.protocols import LoggerProtocol

# At runtime, use lazy import in functions:
def use_logger():
    if TYPE_CHECKING:
        # Type checkers see the real type
        logger: LoggerProtocol
    else:
        # At runtime, import only when needed
        try:
            from codex_ml.logging import FileLogger
            logger = FileLogger(...)
        except ImportError:
            # Fallback to protocol implementation
            logger = NoOpLogger()
'''

# ============================================================================
# PROTOCOL ADOPTION PATTERN  
# ============================================================================

PROTOCOL_ADOPTION_PATTERN = '''
# Before: Hard coupling to concrete type
def train(model: ModelBase, data: Dataset) -> None:
    ...

# After: Protocol-based interface
from typing import TYPE_CHECKING
from codex.protocols import ModelProtocol, DatasetProtocol

if TYPE_CHECKING:
    from codex_ml.models import ModelBase
    from codex_ml.data import Dataset

def train(model: ModelProtocol, data: DatasetProtocol) -> None:
    # Works with any implementation of the protocol
    ...
'''

# ============================================================================
# SUCCESS CRITERIA
# ============================================================================

SUCCESS_CRITERIA = [
    ("Protocols Created", "4 core protocols in codex/protocols/ml_protocols.py"),
    ("Bootstrap Test 1", "training can be imported independently"),
    ("Bootstrap Test 2", "codex_ml can be imported independently"),
    ("Bootstrap Test 3", "Both can be imported together bidirectionally"),
    ("Cycles Broken", "All 6+ circular imports replaced with lazy/protocol"),
    ("Type Checking", "mypy strict mode passes on all refactored files"),
    ("Tests Pass", "100% of existing tests still pass"),
    ("No Regressions", "All public APIs remain unchanged"),
]

print(__doc__)
print("\nCIRCULAR DEPENDENCIES IDENTIFIED:")
for name, details in CIRCULAR_DEPENDENCIES.items():
    print(f"  {name}: {details['severity'].upper()}")
    print(f"    Path: {details['path']}")
    print(f"    Fix: {details['fix_strategy']}")

print("\nPROTOCOLS CREATED:")
for proto in PROTOCOLS_CREATED:
    print(f"  ✓ {proto}")

print("\nFILES TO REFACTOR:")
for file_info in FILES_TO_REFACTOR:
    print(f"  {file_info['file']} ({file_info['cycles']} cycles)")

print("\nSUCCESS CRITERIA:")
for criterion, description in SUCCESS_CRITERIA:
    print(f"  ☐ {criterion}: {description}")
