"""AST delta analysis for detecting changes."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codex.ast.baseline import BaselineManager

logger = logging.getLogger(__name__)
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


@dataclass
class DeltaResult:
    """Result of delta analysis."""

    added: list[str]
    removed: list[str]
    modified: list[str]
    unchanged: list[str]

    def summary(self) -> str:
        """Get summary string."""
        return (
            f"Added: {len(self.added)}, "
            f"Removed: {len(self.removed)}, "
            f"Modified: {len(self.modified)}, "
            f"Unchanged: {len(self.unchanged)}"
        )

    def has_changes(self) -> bool:
        """Check if any changes detected."""
        return bool(self.added or self.removed or self.modified)

    def total_changes(self) -> int:
        """Get total number of changed files."""
        return len(self.added) + len(self.removed) + len(self.modified)


class DeltaAnalyzer:
    """Analyzes differences between AST baselines and current state."""

    def xǁDeltaAnalyzerǁ__init____mutmut_orig(self, baseline_manager: "BaselineManager") -> None:
        """Initialize delta analyzer.

        Args:
            baseline_manager: BaselineManager instance
        """
        self.baseline_manager = baseline_manager

    def xǁDeltaAnalyzerǁ__init____mutmut_1(self, baseline_manager: "BaselineManager") -> None:
        """Initialize delta analyzer.

        Args:
            baseline_manager: BaselineManager instance
        """
        self.baseline_manager = None
    
    xǁDeltaAnalyzerǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDeltaAnalyzerǁ__init____mutmut_1': xǁDeltaAnalyzerǁ__init____mutmut_1
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDeltaAnalyzerǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁDeltaAnalyzerǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁDeltaAnalyzerǁ__init____mutmut_orig)
    xǁDeltaAnalyzerǁ__init____mutmut_orig.__name__ = 'xǁDeltaAnalyzerǁ__init__'

    def xǁDeltaAnalyzerǁanalyze__mutmut_orig(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_1(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = None
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_2(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = None
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_3(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = None
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_4(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = None

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_5(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = None
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_6(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["XXfile_pathXX"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_7(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["FILE_PATH"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_8(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = None
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_9(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(None)
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_10(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = None

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_11(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(None)

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_12(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths + baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_13(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(None)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_14(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(None)

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_15(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths + current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_16(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(None)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_17(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(None)

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_18(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths | current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_19(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = None
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_20(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = None

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_21(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["XXast_hashXX"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_22(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["AST_HASH"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_23(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] == current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_24(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get(None):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_25(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("XXast_hashXX"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_26(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("AST_HASH"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_27(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(None)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_28(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(None)
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_29(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(None)

        result = DeltaResult(added, removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_30(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = None
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_31(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(None, removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_32(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, None, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_33(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, None, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_34(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, None)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_35(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(removed, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_36(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, modified, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_37(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, unchanged)
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_38(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, )
        logger.info(f"Delta analysis: {result.summary()}")
        return result

    def xǁDeltaAnalyzerǁanalyze__mutmut_39(self, current_files: dict[str, dict]) -> DeltaResult:
        """Analyze delta between baseline and current state.

        Args:
            current_files: dict mapping file paths to current AST data.
                          Each value should have 'ast_hash' key.

        Returns:
            DeltaResult with categorized changes
        """
        added = []
        removed = []
        modified = []
        unchanged = []

        # Get all baseline file paths
        baselines = {
            b["file_path"]: b for b in self.baseline_manager.list_baselines()
        }
        baseline_paths = set(baselines.keys())
        current_paths = set(current_files.keys())

        # Find added files (in current but not in baseline)
        for file_path in current_paths - baseline_paths:
            added.append(file_path)
            logger.debug(f"Added: {file_path}")

        # Find removed files (in baseline but not in current)
        for file_path in baseline_paths - current_paths:
            removed.append(file_path)
            logger.debug(f"Removed: {file_path}")

        # Check common files for modifications
        for file_path in baseline_paths & current_paths:
            baseline = baselines[file_path]
            current = current_files[file_path]

            if baseline["ast_hash"] != current.get("ast_hash"):
                modified.append(file_path)
                logger.debug(f"Modified: {file_path}")
            else:
                unchanged.append(file_path)

        result = DeltaResult(added, removed, modified, unchanged)
        logger.info(None)
        return result
    
    xǁDeltaAnalyzerǁanalyze__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDeltaAnalyzerǁanalyze__mutmut_1': xǁDeltaAnalyzerǁanalyze__mutmut_1, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_2': xǁDeltaAnalyzerǁanalyze__mutmut_2, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_3': xǁDeltaAnalyzerǁanalyze__mutmut_3, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_4': xǁDeltaAnalyzerǁanalyze__mutmut_4, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_5': xǁDeltaAnalyzerǁanalyze__mutmut_5, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_6': xǁDeltaAnalyzerǁanalyze__mutmut_6, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_7': xǁDeltaAnalyzerǁanalyze__mutmut_7, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_8': xǁDeltaAnalyzerǁanalyze__mutmut_8, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_9': xǁDeltaAnalyzerǁanalyze__mutmut_9, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_10': xǁDeltaAnalyzerǁanalyze__mutmut_10, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_11': xǁDeltaAnalyzerǁanalyze__mutmut_11, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_12': xǁDeltaAnalyzerǁanalyze__mutmut_12, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_13': xǁDeltaAnalyzerǁanalyze__mutmut_13, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_14': xǁDeltaAnalyzerǁanalyze__mutmut_14, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_15': xǁDeltaAnalyzerǁanalyze__mutmut_15, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_16': xǁDeltaAnalyzerǁanalyze__mutmut_16, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_17': xǁDeltaAnalyzerǁanalyze__mutmut_17, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_18': xǁDeltaAnalyzerǁanalyze__mutmut_18, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_19': xǁDeltaAnalyzerǁanalyze__mutmut_19, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_20': xǁDeltaAnalyzerǁanalyze__mutmut_20, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_21': xǁDeltaAnalyzerǁanalyze__mutmut_21, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_22': xǁDeltaAnalyzerǁanalyze__mutmut_22, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_23': xǁDeltaAnalyzerǁanalyze__mutmut_23, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_24': xǁDeltaAnalyzerǁanalyze__mutmut_24, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_25': xǁDeltaAnalyzerǁanalyze__mutmut_25, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_26': xǁDeltaAnalyzerǁanalyze__mutmut_26, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_27': xǁDeltaAnalyzerǁanalyze__mutmut_27, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_28': xǁDeltaAnalyzerǁanalyze__mutmut_28, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_29': xǁDeltaAnalyzerǁanalyze__mutmut_29, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_30': xǁDeltaAnalyzerǁanalyze__mutmut_30, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_31': xǁDeltaAnalyzerǁanalyze__mutmut_31, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_32': xǁDeltaAnalyzerǁanalyze__mutmut_32, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_33': xǁDeltaAnalyzerǁanalyze__mutmut_33, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_34': xǁDeltaAnalyzerǁanalyze__mutmut_34, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_35': xǁDeltaAnalyzerǁanalyze__mutmut_35, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_36': xǁDeltaAnalyzerǁanalyze__mutmut_36, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_37': xǁDeltaAnalyzerǁanalyze__mutmut_37, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_38': xǁDeltaAnalyzerǁanalyze__mutmut_38, 
        'xǁDeltaAnalyzerǁanalyze__mutmut_39': xǁDeltaAnalyzerǁanalyze__mutmut_39
    }
    
    def analyze(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDeltaAnalyzerǁanalyze__mutmut_orig"), object.__getattribute__(self, "xǁDeltaAnalyzerǁanalyze__mutmut_mutants"), args, kwargs, self)
        return result 
    
    analyze.__signature__ = _mutmut_signature(xǁDeltaAnalyzerǁanalyze__mutmut_orig)
    xǁDeltaAnalyzerǁanalyze__mutmut_orig.__name__ = 'xǁDeltaAnalyzerǁanalyze'

    def xǁDeltaAnalyzerǁanalyze_file__mutmut_orig(self, file_path: str, current_data: dict) -> str:
        """Analyze single file change status.

        Args:
            file_path: Path to source file
            current_data: Current AST data with 'ast_hash' key

        Returns:
            Status: 'added', 'modified', or 'unchanged'
        """
        baseline = self.baseline_manager.get_baseline(file_path)

        if not baseline:
            return "added"

        if baseline["ast_hash"] != current_data.get("ast_hash"):
            return "modified"

        return "unchanged"

    def xǁDeltaAnalyzerǁanalyze_file__mutmut_1(self, file_path: str, current_data: dict) -> str:
        """Analyze single file change status.

        Args:
            file_path: Path to source file
            current_data: Current AST data with 'ast_hash' key

        Returns:
            Status: 'added', 'modified', or 'unchanged'
        """
        baseline = None

        if not baseline:
            return "added"

        if baseline["ast_hash"] != current_data.get("ast_hash"):
            return "modified"

        return "unchanged"

    def xǁDeltaAnalyzerǁanalyze_file__mutmut_2(self, file_path: str, current_data: dict) -> str:
        """Analyze single file change status.

        Args:
            file_path: Path to source file
            current_data: Current AST data with 'ast_hash' key

        Returns:
            Status: 'added', 'modified', or 'unchanged'
        """
        baseline = self.baseline_manager.get_baseline(None)

        if not baseline:
            return "added"

        if baseline["ast_hash"] != current_data.get("ast_hash"):
            return "modified"

        return "unchanged"

    def xǁDeltaAnalyzerǁanalyze_file__mutmut_3(self, file_path: str, current_data: dict) -> str:
        """Analyze single file change status.

        Args:
            file_path: Path to source file
            current_data: Current AST data with 'ast_hash' key

        Returns:
            Status: 'added', 'modified', or 'unchanged'
        """
        baseline = self.baseline_manager.get_baseline(file_path)

        if baseline:
            return "added"

        if baseline["ast_hash"] != current_data.get("ast_hash"):
            return "modified"

        return "unchanged"

    def xǁDeltaAnalyzerǁanalyze_file__mutmut_4(self, file_path: str, current_data: dict) -> str:
        """Analyze single file change status.

        Args:
            file_path: Path to source file
            current_data: Current AST data with 'ast_hash' key

        Returns:
            Status: 'added', 'modified', or 'unchanged'
        """
        baseline = self.baseline_manager.get_baseline(file_path)

        if not baseline:
            return "XXaddedXX"

        if baseline["ast_hash"] != current_data.get("ast_hash"):
            return "modified"

        return "unchanged"

    def xǁDeltaAnalyzerǁanalyze_file__mutmut_5(self, file_path: str, current_data: dict) -> str:
        """Analyze single file change status.

        Args:
            file_path: Path to source file
            current_data: Current AST data with 'ast_hash' key

        Returns:
            Status: 'added', 'modified', or 'unchanged'
        """
        baseline = self.baseline_manager.get_baseline(file_path)

        if not baseline:
            return "ADDED"

        if baseline["ast_hash"] != current_data.get("ast_hash"):
            return "modified"

        return "unchanged"

    def xǁDeltaAnalyzerǁanalyze_file__mutmut_6(self, file_path: str, current_data: dict) -> str:
        """Analyze single file change status.

        Args:
            file_path: Path to source file
            current_data: Current AST data with 'ast_hash' key

        Returns:
            Status: 'added', 'modified', or 'unchanged'
        """
        baseline = self.baseline_manager.get_baseline(file_path)

        if not baseline:
            return "added"

        if baseline["XXast_hashXX"] != current_data.get("ast_hash"):
            return "modified"

        return "unchanged"

    def xǁDeltaAnalyzerǁanalyze_file__mutmut_7(self, file_path: str, current_data: dict) -> str:
        """Analyze single file change status.

        Args:
            file_path: Path to source file
            current_data: Current AST data with 'ast_hash' key

        Returns:
            Status: 'added', 'modified', or 'unchanged'
        """
        baseline = self.baseline_manager.get_baseline(file_path)

        if not baseline:
            return "added"

        if baseline["AST_HASH"] != current_data.get("ast_hash"):
            return "modified"

        return "unchanged"

    def xǁDeltaAnalyzerǁanalyze_file__mutmut_8(self, file_path: str, current_data: dict) -> str:
        """Analyze single file change status.

        Args:
            file_path: Path to source file
            current_data: Current AST data with 'ast_hash' key

        Returns:
            Status: 'added', 'modified', or 'unchanged'
        """
        baseline = self.baseline_manager.get_baseline(file_path)

        if not baseline:
            return "added"

        if baseline["ast_hash"] == current_data.get("ast_hash"):
            return "modified"

        return "unchanged"

    def xǁDeltaAnalyzerǁanalyze_file__mutmut_9(self, file_path: str, current_data: dict) -> str:
        """Analyze single file change status.

        Args:
            file_path: Path to source file
            current_data: Current AST data with 'ast_hash' key

        Returns:
            Status: 'added', 'modified', or 'unchanged'
        """
        baseline = self.baseline_manager.get_baseline(file_path)

        if not baseline:
            return "added"

        if baseline["ast_hash"] != current_data.get(None):
            return "modified"

        return "unchanged"

    def xǁDeltaAnalyzerǁanalyze_file__mutmut_10(self, file_path: str, current_data: dict) -> str:
        """Analyze single file change status.

        Args:
            file_path: Path to source file
            current_data: Current AST data with 'ast_hash' key

        Returns:
            Status: 'added', 'modified', or 'unchanged'
        """
        baseline = self.baseline_manager.get_baseline(file_path)

        if not baseline:
            return "added"

        if baseline["ast_hash"] != current_data.get("XXast_hashXX"):
            return "modified"

        return "unchanged"

    def xǁDeltaAnalyzerǁanalyze_file__mutmut_11(self, file_path: str, current_data: dict) -> str:
        """Analyze single file change status.

        Args:
            file_path: Path to source file
            current_data: Current AST data with 'ast_hash' key

        Returns:
            Status: 'added', 'modified', or 'unchanged'
        """
        baseline = self.baseline_manager.get_baseline(file_path)

        if not baseline:
            return "added"

        if baseline["ast_hash"] != current_data.get("AST_HASH"):
            return "modified"

        return "unchanged"

    def xǁDeltaAnalyzerǁanalyze_file__mutmut_12(self, file_path: str, current_data: dict) -> str:
        """Analyze single file change status.

        Args:
            file_path: Path to source file
            current_data: Current AST data with 'ast_hash' key

        Returns:
            Status: 'added', 'modified', or 'unchanged'
        """
        baseline = self.baseline_manager.get_baseline(file_path)

        if not baseline:
            return "added"

        if baseline["ast_hash"] != current_data.get("ast_hash"):
            return "XXmodifiedXX"

        return "unchanged"

    def xǁDeltaAnalyzerǁanalyze_file__mutmut_13(self, file_path: str, current_data: dict) -> str:
        """Analyze single file change status.

        Args:
            file_path: Path to source file
            current_data: Current AST data with 'ast_hash' key

        Returns:
            Status: 'added', 'modified', or 'unchanged'
        """
        baseline = self.baseline_manager.get_baseline(file_path)

        if not baseline:
            return "added"

        if baseline["ast_hash"] != current_data.get("ast_hash"):
            return "MODIFIED"

        return "unchanged"

    def xǁDeltaAnalyzerǁanalyze_file__mutmut_14(self, file_path: str, current_data: dict) -> str:
        """Analyze single file change status.

        Args:
            file_path: Path to source file
            current_data: Current AST data with 'ast_hash' key

        Returns:
            Status: 'added', 'modified', or 'unchanged'
        """
        baseline = self.baseline_manager.get_baseline(file_path)

        if not baseline:
            return "added"

        if baseline["ast_hash"] != current_data.get("ast_hash"):
            return "modified"

        return "XXunchangedXX"

    def xǁDeltaAnalyzerǁanalyze_file__mutmut_15(self, file_path: str, current_data: dict) -> str:
        """Analyze single file change status.

        Args:
            file_path: Path to source file
            current_data: Current AST data with 'ast_hash' key

        Returns:
            Status: 'added', 'modified', or 'unchanged'
        """
        baseline = self.baseline_manager.get_baseline(file_path)

        if not baseline:
            return "added"

        if baseline["ast_hash"] != current_data.get("ast_hash"):
            return "modified"

        return "UNCHANGED"
    
    xǁDeltaAnalyzerǁanalyze_file__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDeltaAnalyzerǁanalyze_file__mutmut_1': xǁDeltaAnalyzerǁanalyze_file__mutmut_1, 
        'xǁDeltaAnalyzerǁanalyze_file__mutmut_2': xǁDeltaAnalyzerǁanalyze_file__mutmut_2, 
        'xǁDeltaAnalyzerǁanalyze_file__mutmut_3': xǁDeltaAnalyzerǁanalyze_file__mutmut_3, 
        'xǁDeltaAnalyzerǁanalyze_file__mutmut_4': xǁDeltaAnalyzerǁanalyze_file__mutmut_4, 
        'xǁDeltaAnalyzerǁanalyze_file__mutmut_5': xǁDeltaAnalyzerǁanalyze_file__mutmut_5, 
        'xǁDeltaAnalyzerǁanalyze_file__mutmut_6': xǁDeltaAnalyzerǁanalyze_file__mutmut_6, 
        'xǁDeltaAnalyzerǁanalyze_file__mutmut_7': xǁDeltaAnalyzerǁanalyze_file__mutmut_7, 
        'xǁDeltaAnalyzerǁanalyze_file__mutmut_8': xǁDeltaAnalyzerǁanalyze_file__mutmut_8, 
        'xǁDeltaAnalyzerǁanalyze_file__mutmut_9': xǁDeltaAnalyzerǁanalyze_file__mutmut_9, 
        'xǁDeltaAnalyzerǁanalyze_file__mutmut_10': xǁDeltaAnalyzerǁanalyze_file__mutmut_10, 
        'xǁDeltaAnalyzerǁanalyze_file__mutmut_11': xǁDeltaAnalyzerǁanalyze_file__mutmut_11, 
        'xǁDeltaAnalyzerǁanalyze_file__mutmut_12': xǁDeltaAnalyzerǁanalyze_file__mutmut_12, 
        'xǁDeltaAnalyzerǁanalyze_file__mutmut_13': xǁDeltaAnalyzerǁanalyze_file__mutmut_13, 
        'xǁDeltaAnalyzerǁanalyze_file__mutmut_14': xǁDeltaAnalyzerǁanalyze_file__mutmut_14, 
        'xǁDeltaAnalyzerǁanalyze_file__mutmut_15': xǁDeltaAnalyzerǁanalyze_file__mutmut_15
    }
    
    def analyze_file(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDeltaAnalyzerǁanalyze_file__mutmut_orig"), object.__getattribute__(self, "xǁDeltaAnalyzerǁanalyze_file__mutmut_mutants"), args, kwargs, self)
        return result 
    
    analyze_file.__signature__ = _mutmut_signature(xǁDeltaAnalyzerǁanalyze_file__mutmut_orig)
    xǁDeltaAnalyzerǁanalyze_file__mutmut_orig.__name__ = 'xǁDeltaAnalyzerǁanalyze_file'


__all__ = ["DeltaAnalyzer", "DeltaResult"]
