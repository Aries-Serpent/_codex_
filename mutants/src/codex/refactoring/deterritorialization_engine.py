"""
Deterritorialization Engine

Implements Deleuzian deterritorialization for identifying and breaking
rigid code patterns to enable creativity and innovation.

Reference: .codex/docs/PHILOSOPHICAL_FRAMEWORK.md#deterritorialization
Philosophical Foundation: Deleuze & Guattari - Anti-Oedipus (1972)

Core Concepts:
- Territorialization: Formation of stable patterns/structures
- Deterritorialization: Breaking fixed patterns to enable creativity
- Reterritorialization: Formation of new patterns
- Line of Flight: Escape route from rigid structure

Deterritorialization is NOT:
- Random destruction
- Rebellion against structure
- Chaos for chaos's sake

Deterritorialization IS:
- Strategic pattern-breaking for innovation
- Creating "lines of flight" to new possibilities
- Productive transformation, not mere negation
"""

from __future__ import annotations

import ast
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

LOGGER = logging.getLogger(__name__)
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


class RigidityType(Enum):
    """Types of rigidity in code that may benefit from deterritorialization."""

    DEEP_NESTING = "deep_nesting"  # Excessive nesting (> 4 levels)
    LONG_METHOD = "long_method"  # Methods > 50 lines
    GOD_CLASS = "god_class"  # Classes with too many responsibilities
    TIGHT_COUPLING = "tight_coupling"  # Excessive dependencies
    HARDCODED_VALUES = "hardcoded_values"  # Magic numbers/strings
    REPEATED_PATTERNS = "repeated_patterns"  # Code duplication
    OVERLY_COMPLEX = "overly_complex"  # High cyclomatic complexity


@dataclass
class RigidityDetection:
    """A detected instance of rigidity in the codebase."""

    rigidity_type: RigidityType
    file_path: str
    line_number: int
    severity: float  # 0.0 (low) to 1.0 (high)
    description: str
    context: str  # Code snippet showing the issue
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return (
            f"{self.rigidity_type.value} at {self.file_path}:{self.line_number} "
            f"(severity: {self.severity:.2f})"
        )


@dataclass
class LineOfFlight:
    """
    A "line of flight" - an escape route from rigidity.

    Following Deleuze: Not rebellion, but creation of something new.
    """

    rigidity: RigidityDetection
    proposed_action: str
    expected_outcome: str
    innovation_potential: float  # 0.0 to 1.0
    risk_level: float  # 0.0 (low) to 1.0 (high)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __str__(self) -> str:
        return (
            f"Line of flight from {self.rigidity.rigidity_type.value}: "
            f"{self.proposed_action} (innovation: {self.innovation_potential:.2%}, "
            f"risk: {self.risk_level:.2%})"
        )


class RigidityDetector:
    """
    Detects rigid patterns in code that may benefit from deterritorialization.

    Uses AST analysis to identify structural rigidity.
    """

    def xǁRigidityDetectorǁ__init____mutmut_orig(
        self,
        max_nesting: int = 4,
        max_method_lines: int = 50,
        max_class_methods: int = 20,
    ) -> None:
        self.max_nesting = max_nesting
        self.max_method_lines = max_method_lines
        self.max_class_methods = max_class_methods
        self.detections: List[RigidityDetection] = []

    def xǁRigidityDetectorǁ__init____mutmut_1(
        self,
        max_nesting: int = 5,
        max_method_lines: int = 50,
        max_class_methods: int = 20,
    ) -> None:
        self.max_nesting = max_nesting
        self.max_method_lines = max_method_lines
        self.max_class_methods = max_class_methods
        self.detections: List[RigidityDetection] = []

    def xǁRigidityDetectorǁ__init____mutmut_2(
        self,
        max_nesting: int = 4,
        max_method_lines: int = 51,
        max_class_methods: int = 20,
    ) -> None:
        self.max_nesting = max_nesting
        self.max_method_lines = max_method_lines
        self.max_class_methods = max_class_methods
        self.detections: List[RigidityDetection] = []

    def xǁRigidityDetectorǁ__init____mutmut_3(
        self,
        max_nesting: int = 4,
        max_method_lines: int = 50,
        max_class_methods: int = 21,
    ) -> None:
        self.max_nesting = max_nesting
        self.max_method_lines = max_method_lines
        self.max_class_methods = max_class_methods
        self.detections: List[RigidityDetection] = []

    def xǁRigidityDetectorǁ__init____mutmut_4(
        self,
        max_nesting: int = 4,
        max_method_lines: int = 50,
        max_class_methods: int = 20,
    ) -> None:
        self.max_nesting = None
        self.max_method_lines = max_method_lines
        self.max_class_methods = max_class_methods
        self.detections: List[RigidityDetection] = []

    def xǁRigidityDetectorǁ__init____mutmut_5(
        self,
        max_nesting: int = 4,
        max_method_lines: int = 50,
        max_class_methods: int = 20,
    ) -> None:
        self.max_nesting = max_nesting
        self.max_method_lines = None
        self.max_class_methods = max_class_methods
        self.detections: List[RigidityDetection] = []

    def xǁRigidityDetectorǁ__init____mutmut_6(
        self,
        max_nesting: int = 4,
        max_method_lines: int = 50,
        max_class_methods: int = 20,
    ) -> None:
        self.max_nesting = max_nesting
        self.max_method_lines = max_method_lines
        self.max_class_methods = None
        self.detections: List[RigidityDetection] = []

    def xǁRigidityDetectorǁ__init____mutmut_7(
        self,
        max_nesting: int = 4,
        max_method_lines: int = 50,
        max_class_methods: int = 20,
    ) -> None:
        self.max_nesting = max_nesting
        self.max_method_lines = max_method_lines
        self.max_class_methods = max_class_methods
        self.detections: List[RigidityDetection] = None
    
    xǁRigidityDetectorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRigidityDetectorǁ__init____mutmut_1': xǁRigidityDetectorǁ__init____mutmut_1, 
        'xǁRigidityDetectorǁ__init____mutmut_2': xǁRigidityDetectorǁ__init____mutmut_2, 
        'xǁRigidityDetectorǁ__init____mutmut_3': xǁRigidityDetectorǁ__init____mutmut_3, 
        'xǁRigidityDetectorǁ__init____mutmut_4': xǁRigidityDetectorǁ__init____mutmut_4, 
        'xǁRigidityDetectorǁ__init____mutmut_5': xǁRigidityDetectorǁ__init____mutmut_5, 
        'xǁRigidityDetectorǁ__init____mutmut_6': xǁRigidityDetectorǁ__init____mutmut_6, 
        'xǁRigidityDetectorǁ__init____mutmut_7': xǁRigidityDetectorǁ__init____mutmut_7
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRigidityDetectorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁRigidityDetectorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁRigidityDetectorǁ__init____mutmut_orig)
    xǁRigidityDetectorǁ__init____mutmut_orig.__name__ = 'xǁRigidityDetectorǁ__init__'

    def xǁRigidityDetectorǁanalyze_file__mutmut_orig(self, file_path: Path) -> List[RigidityDetection]:
        """
        Analyze a Python file for rigidity.

        Args:
            file_path: Path to Python file

        Returns:
            List of detected rigidities
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=str(file_path))
            self._analyze_ast(tree, str(file_path), source)

        except SyntaxError as e:
            LOGGER.warning(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            LOGGER.error(f"Error analyzing {file_path}: {e}")

        return self.detections

    def xǁRigidityDetectorǁanalyze_file__mutmut_1(self, file_path: Path) -> List[RigidityDetection]:
        """
        Analyze a Python file for rigidity.

        Args:
            file_path: Path to Python file

        Returns:
            List of detected rigidities
        """
        try:
            with open(None, encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=str(file_path))
            self._analyze_ast(tree, str(file_path), source)

        except SyntaxError as e:
            LOGGER.warning(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            LOGGER.error(f"Error analyzing {file_path}: {e}")

        return self.detections

    def xǁRigidityDetectorǁanalyze_file__mutmut_2(self, file_path: Path) -> List[RigidityDetection]:
        """
        Analyze a Python file for rigidity.

        Args:
            file_path: Path to Python file

        Returns:
            List of detected rigidities
        """
        try:
            with open(file_path, encoding=None) as f:
                source = f.read()

            tree = ast.parse(source, filename=str(file_path))
            self._analyze_ast(tree, str(file_path), source)

        except SyntaxError as e:
            LOGGER.warning(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            LOGGER.error(f"Error analyzing {file_path}: {e}")

        return self.detections

    def xǁRigidityDetectorǁanalyze_file__mutmut_3(self, file_path: Path) -> List[RigidityDetection]:
        """
        Analyze a Python file for rigidity.

        Args:
            file_path: Path to Python file

        Returns:
            List of detected rigidities
        """
        try:
            with open(encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=str(file_path))
            self._analyze_ast(tree, str(file_path), source)

        except SyntaxError as e:
            LOGGER.warning(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            LOGGER.error(f"Error analyzing {file_path}: {e}")

        return self.detections

    def xǁRigidityDetectorǁanalyze_file__mutmut_4(self, file_path: Path) -> List[RigidityDetection]:
        """
        Analyze a Python file for rigidity.

        Args:
            file_path: Path to Python file

        Returns:
            List of detected rigidities
        """
        try:
            with open(file_path, ) as f:
                source = f.read()

            tree = ast.parse(source, filename=str(file_path))
            self._analyze_ast(tree, str(file_path), source)

        except SyntaxError as e:
            LOGGER.warning(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            LOGGER.error(f"Error analyzing {file_path}: {e}")

        return self.detections

    def xǁRigidityDetectorǁanalyze_file__mutmut_5(self, file_path: Path) -> List[RigidityDetection]:
        """
        Analyze a Python file for rigidity.

        Args:
            file_path: Path to Python file

        Returns:
            List of detected rigidities
        """
        try:
            with open(file_path, encoding="XXutf-8XX") as f:
                source = f.read()

            tree = ast.parse(source, filename=str(file_path))
            self._analyze_ast(tree, str(file_path), source)

        except SyntaxError as e:
            LOGGER.warning(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            LOGGER.error(f"Error analyzing {file_path}: {e}")

        return self.detections

    def xǁRigidityDetectorǁanalyze_file__mutmut_6(self, file_path: Path) -> List[RigidityDetection]:
        """
        Analyze a Python file for rigidity.

        Args:
            file_path: Path to Python file

        Returns:
            List of detected rigidities
        """
        try:
            with open(file_path, encoding="UTF-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=str(file_path))
            self._analyze_ast(tree, str(file_path), source)

        except SyntaxError as e:
            LOGGER.warning(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            LOGGER.error(f"Error analyzing {file_path}: {e}")

        return self.detections

    def xǁRigidityDetectorǁanalyze_file__mutmut_7(self, file_path: Path) -> List[RigidityDetection]:
        """
        Analyze a Python file for rigidity.

        Args:
            file_path: Path to Python file

        Returns:
            List of detected rigidities
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                source = None

            tree = ast.parse(source, filename=str(file_path))
            self._analyze_ast(tree, str(file_path), source)

        except SyntaxError as e:
            LOGGER.warning(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            LOGGER.error(f"Error analyzing {file_path}: {e}")

        return self.detections

    def xǁRigidityDetectorǁanalyze_file__mutmut_8(self, file_path: Path) -> List[RigidityDetection]:
        """
        Analyze a Python file for rigidity.

        Args:
            file_path: Path to Python file

        Returns:
            List of detected rigidities
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()

            tree = None
            self._analyze_ast(tree, str(file_path), source)

        except SyntaxError as e:
            LOGGER.warning(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            LOGGER.error(f"Error analyzing {file_path}: {e}")

        return self.detections

    def xǁRigidityDetectorǁanalyze_file__mutmut_9(self, file_path: Path) -> List[RigidityDetection]:
        """
        Analyze a Python file for rigidity.

        Args:
            file_path: Path to Python file

        Returns:
            List of detected rigidities
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(None, filename=str(file_path))
            self._analyze_ast(tree, str(file_path), source)

        except SyntaxError as e:
            LOGGER.warning(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            LOGGER.error(f"Error analyzing {file_path}: {e}")

        return self.detections

    def xǁRigidityDetectorǁanalyze_file__mutmut_10(self, file_path: Path) -> List[RigidityDetection]:
        """
        Analyze a Python file for rigidity.

        Args:
            file_path: Path to Python file

        Returns:
            List of detected rigidities
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=None)
            self._analyze_ast(tree, str(file_path), source)

        except SyntaxError as e:
            LOGGER.warning(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            LOGGER.error(f"Error analyzing {file_path}: {e}")

        return self.detections

    def xǁRigidityDetectorǁanalyze_file__mutmut_11(self, file_path: Path) -> List[RigidityDetection]:
        """
        Analyze a Python file for rigidity.

        Args:
            file_path: Path to Python file

        Returns:
            List of detected rigidities
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(filename=str(file_path))
            self._analyze_ast(tree, str(file_path), source)

        except SyntaxError as e:
            LOGGER.warning(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            LOGGER.error(f"Error analyzing {file_path}: {e}")

        return self.detections

    def xǁRigidityDetectorǁanalyze_file__mutmut_12(self, file_path: Path) -> List[RigidityDetection]:
        """
        Analyze a Python file for rigidity.

        Args:
            file_path: Path to Python file

        Returns:
            List of detected rigidities
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, )
            self._analyze_ast(tree, str(file_path), source)

        except SyntaxError as e:
            LOGGER.warning(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            LOGGER.error(f"Error analyzing {file_path}: {e}")

        return self.detections

    def xǁRigidityDetectorǁanalyze_file__mutmut_13(self, file_path: Path) -> List[RigidityDetection]:
        """
        Analyze a Python file for rigidity.

        Args:
            file_path: Path to Python file

        Returns:
            List of detected rigidities
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=str(None))
            self._analyze_ast(tree, str(file_path), source)

        except SyntaxError as e:
            LOGGER.warning(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            LOGGER.error(f"Error analyzing {file_path}: {e}")

        return self.detections

    def xǁRigidityDetectorǁanalyze_file__mutmut_14(self, file_path: Path) -> List[RigidityDetection]:
        """
        Analyze a Python file for rigidity.

        Args:
            file_path: Path to Python file

        Returns:
            List of detected rigidities
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=str(file_path))
            self._analyze_ast(None, str(file_path), source)

        except SyntaxError as e:
            LOGGER.warning(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            LOGGER.error(f"Error analyzing {file_path}: {e}")

        return self.detections

    def xǁRigidityDetectorǁanalyze_file__mutmut_15(self, file_path: Path) -> List[RigidityDetection]:
        """
        Analyze a Python file for rigidity.

        Args:
            file_path: Path to Python file

        Returns:
            List of detected rigidities
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=str(file_path))
            self._analyze_ast(tree, None, source)

        except SyntaxError as e:
            LOGGER.warning(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            LOGGER.error(f"Error analyzing {file_path}: {e}")

        return self.detections

    def xǁRigidityDetectorǁanalyze_file__mutmut_16(self, file_path: Path) -> List[RigidityDetection]:
        """
        Analyze a Python file for rigidity.

        Args:
            file_path: Path to Python file

        Returns:
            List of detected rigidities
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=str(file_path))
            self._analyze_ast(tree, str(file_path), None)

        except SyntaxError as e:
            LOGGER.warning(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            LOGGER.error(f"Error analyzing {file_path}: {e}")

        return self.detections

    def xǁRigidityDetectorǁanalyze_file__mutmut_17(self, file_path: Path) -> List[RigidityDetection]:
        """
        Analyze a Python file for rigidity.

        Args:
            file_path: Path to Python file

        Returns:
            List of detected rigidities
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=str(file_path))
            self._analyze_ast(str(file_path), source)

        except SyntaxError as e:
            LOGGER.warning(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            LOGGER.error(f"Error analyzing {file_path}: {e}")

        return self.detections

    def xǁRigidityDetectorǁanalyze_file__mutmut_18(self, file_path: Path) -> List[RigidityDetection]:
        """
        Analyze a Python file for rigidity.

        Args:
            file_path: Path to Python file

        Returns:
            List of detected rigidities
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=str(file_path))
            self._analyze_ast(tree, source)

        except SyntaxError as e:
            LOGGER.warning(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            LOGGER.error(f"Error analyzing {file_path}: {e}")

        return self.detections

    def xǁRigidityDetectorǁanalyze_file__mutmut_19(self, file_path: Path) -> List[RigidityDetection]:
        """
        Analyze a Python file for rigidity.

        Args:
            file_path: Path to Python file

        Returns:
            List of detected rigidities
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=str(file_path))
            self._analyze_ast(tree, str(file_path), )

        except SyntaxError as e:
            LOGGER.warning(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            LOGGER.error(f"Error analyzing {file_path}: {e}")

        return self.detections

    def xǁRigidityDetectorǁanalyze_file__mutmut_20(self, file_path: Path) -> List[RigidityDetection]:
        """
        Analyze a Python file for rigidity.

        Args:
            file_path: Path to Python file

        Returns:
            List of detected rigidities
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=str(file_path))
            self._analyze_ast(tree, str(None), source)

        except SyntaxError as e:
            LOGGER.warning(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            LOGGER.error(f"Error analyzing {file_path}: {e}")

        return self.detections

    def xǁRigidityDetectorǁanalyze_file__mutmut_21(self, file_path: Path) -> List[RigidityDetection]:
        """
        Analyze a Python file for rigidity.

        Args:
            file_path: Path to Python file

        Returns:
            List of detected rigidities
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=str(file_path))
            self._analyze_ast(tree, str(file_path), source)

        except SyntaxError as e:
            LOGGER.warning(None)
        except Exception as e:
            LOGGER.error(f"Error analyzing {file_path}: {e}")

        return self.detections

    def xǁRigidityDetectorǁanalyze_file__mutmut_22(self, file_path: Path) -> List[RigidityDetection]:
        """
        Analyze a Python file for rigidity.

        Args:
            file_path: Path to Python file

        Returns:
            List of detected rigidities
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=str(file_path))
            self._analyze_ast(tree, str(file_path), source)

        except SyntaxError as e:
            LOGGER.warning(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            LOGGER.error(None)

        return self.detections
    
    xǁRigidityDetectorǁanalyze_file__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRigidityDetectorǁanalyze_file__mutmut_1': xǁRigidityDetectorǁanalyze_file__mutmut_1, 
        'xǁRigidityDetectorǁanalyze_file__mutmut_2': xǁRigidityDetectorǁanalyze_file__mutmut_2, 
        'xǁRigidityDetectorǁanalyze_file__mutmut_3': xǁRigidityDetectorǁanalyze_file__mutmut_3, 
        'xǁRigidityDetectorǁanalyze_file__mutmut_4': xǁRigidityDetectorǁanalyze_file__mutmut_4, 
        'xǁRigidityDetectorǁanalyze_file__mutmut_5': xǁRigidityDetectorǁanalyze_file__mutmut_5, 
        'xǁRigidityDetectorǁanalyze_file__mutmut_6': xǁRigidityDetectorǁanalyze_file__mutmut_6, 
        'xǁRigidityDetectorǁanalyze_file__mutmut_7': xǁRigidityDetectorǁanalyze_file__mutmut_7, 
        'xǁRigidityDetectorǁanalyze_file__mutmut_8': xǁRigidityDetectorǁanalyze_file__mutmut_8, 
        'xǁRigidityDetectorǁanalyze_file__mutmut_9': xǁRigidityDetectorǁanalyze_file__mutmut_9, 
        'xǁRigidityDetectorǁanalyze_file__mutmut_10': xǁRigidityDetectorǁanalyze_file__mutmut_10, 
        'xǁRigidityDetectorǁanalyze_file__mutmut_11': xǁRigidityDetectorǁanalyze_file__mutmut_11, 
        'xǁRigidityDetectorǁanalyze_file__mutmut_12': xǁRigidityDetectorǁanalyze_file__mutmut_12, 
        'xǁRigidityDetectorǁanalyze_file__mutmut_13': xǁRigidityDetectorǁanalyze_file__mutmut_13, 
        'xǁRigidityDetectorǁanalyze_file__mutmut_14': xǁRigidityDetectorǁanalyze_file__mutmut_14, 
        'xǁRigidityDetectorǁanalyze_file__mutmut_15': xǁRigidityDetectorǁanalyze_file__mutmut_15, 
        'xǁRigidityDetectorǁanalyze_file__mutmut_16': xǁRigidityDetectorǁanalyze_file__mutmut_16, 
        'xǁRigidityDetectorǁanalyze_file__mutmut_17': xǁRigidityDetectorǁanalyze_file__mutmut_17, 
        'xǁRigidityDetectorǁanalyze_file__mutmut_18': xǁRigidityDetectorǁanalyze_file__mutmut_18, 
        'xǁRigidityDetectorǁanalyze_file__mutmut_19': xǁRigidityDetectorǁanalyze_file__mutmut_19, 
        'xǁRigidityDetectorǁanalyze_file__mutmut_20': xǁRigidityDetectorǁanalyze_file__mutmut_20, 
        'xǁRigidityDetectorǁanalyze_file__mutmut_21': xǁRigidityDetectorǁanalyze_file__mutmut_21, 
        'xǁRigidityDetectorǁanalyze_file__mutmut_22': xǁRigidityDetectorǁanalyze_file__mutmut_22
    }
    
    def analyze_file(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRigidityDetectorǁanalyze_file__mutmut_orig"), object.__getattribute__(self, "xǁRigidityDetectorǁanalyze_file__mutmut_mutants"), args, kwargs, self)
        return result 
    
    analyze_file.__signature__ = _mutmut_signature(xǁRigidityDetectorǁanalyze_file__mutmut_orig)
    xǁRigidityDetectorǁanalyze_file__mutmut_orig.__name__ = 'xǁRigidityDetectorǁanalyze_file'

    def xǁRigidityDetectorǁ_analyze_ast__mutmut_orig(self, tree: ast.AST, file_path: str, source: str) -> None:
        """Analyze AST for rigid patterns."""
        for node in ast.walk(tree):
            # Check for god classes
            if isinstance(node, ast.ClassDef):
                self._check_god_class(node, file_path, source)

            # Check for long methods
            if isinstance(node, ast.FunctionDef):
                self._check_long_method(node, file_path, source)
                self._check_deep_nesting(node, file_path, source)

    def xǁRigidityDetectorǁ_analyze_ast__mutmut_1(self, tree: ast.AST, file_path: str, source: str) -> None:
        """Analyze AST for rigid patterns."""
        for node in ast.walk(None):
            # Check for god classes
            if isinstance(node, ast.ClassDef):
                self._check_god_class(node, file_path, source)

            # Check for long methods
            if isinstance(node, ast.FunctionDef):
                self._check_long_method(node, file_path, source)
                self._check_deep_nesting(node, file_path, source)

    def xǁRigidityDetectorǁ_analyze_ast__mutmut_2(self, tree: ast.AST, file_path: str, source: str) -> None:
        """Analyze AST for rigid patterns."""
        for node in ast.walk(tree):
            # Check for god classes
            if isinstance(node, ast.ClassDef):
                self._check_god_class(None, file_path, source)

            # Check for long methods
            if isinstance(node, ast.FunctionDef):
                self._check_long_method(node, file_path, source)
                self._check_deep_nesting(node, file_path, source)

    def xǁRigidityDetectorǁ_analyze_ast__mutmut_3(self, tree: ast.AST, file_path: str, source: str) -> None:
        """Analyze AST for rigid patterns."""
        for node in ast.walk(tree):
            # Check for god classes
            if isinstance(node, ast.ClassDef):
                self._check_god_class(node, None, source)

            # Check for long methods
            if isinstance(node, ast.FunctionDef):
                self._check_long_method(node, file_path, source)
                self._check_deep_nesting(node, file_path, source)

    def xǁRigidityDetectorǁ_analyze_ast__mutmut_4(self, tree: ast.AST, file_path: str, source: str) -> None:
        """Analyze AST for rigid patterns."""
        for node in ast.walk(tree):
            # Check for god classes
            if isinstance(node, ast.ClassDef):
                self._check_god_class(node, file_path, None)

            # Check for long methods
            if isinstance(node, ast.FunctionDef):
                self._check_long_method(node, file_path, source)
                self._check_deep_nesting(node, file_path, source)

    def xǁRigidityDetectorǁ_analyze_ast__mutmut_5(self, tree: ast.AST, file_path: str, source: str) -> None:
        """Analyze AST for rigid patterns."""
        for node in ast.walk(tree):
            # Check for god classes
            if isinstance(node, ast.ClassDef):
                self._check_god_class(file_path, source)

            # Check for long methods
            if isinstance(node, ast.FunctionDef):
                self._check_long_method(node, file_path, source)
                self._check_deep_nesting(node, file_path, source)

    def xǁRigidityDetectorǁ_analyze_ast__mutmut_6(self, tree: ast.AST, file_path: str, source: str) -> None:
        """Analyze AST for rigid patterns."""
        for node in ast.walk(tree):
            # Check for god classes
            if isinstance(node, ast.ClassDef):
                self._check_god_class(node, source)

            # Check for long methods
            if isinstance(node, ast.FunctionDef):
                self._check_long_method(node, file_path, source)
                self._check_deep_nesting(node, file_path, source)

    def xǁRigidityDetectorǁ_analyze_ast__mutmut_7(self, tree: ast.AST, file_path: str, source: str) -> None:
        """Analyze AST for rigid patterns."""
        for node in ast.walk(tree):
            # Check for god classes
            if isinstance(node, ast.ClassDef):
                self._check_god_class(node, file_path, )

            # Check for long methods
            if isinstance(node, ast.FunctionDef):
                self._check_long_method(node, file_path, source)
                self._check_deep_nesting(node, file_path, source)

    def xǁRigidityDetectorǁ_analyze_ast__mutmut_8(self, tree: ast.AST, file_path: str, source: str) -> None:
        """Analyze AST for rigid patterns."""
        for node in ast.walk(tree):
            # Check for god classes
            if isinstance(node, ast.ClassDef):
                self._check_god_class(node, file_path, source)

            # Check for long methods
            if isinstance(node, ast.FunctionDef):
                self._check_long_method(None, file_path, source)
                self._check_deep_nesting(node, file_path, source)

    def xǁRigidityDetectorǁ_analyze_ast__mutmut_9(self, tree: ast.AST, file_path: str, source: str) -> None:
        """Analyze AST for rigid patterns."""
        for node in ast.walk(tree):
            # Check for god classes
            if isinstance(node, ast.ClassDef):
                self._check_god_class(node, file_path, source)

            # Check for long methods
            if isinstance(node, ast.FunctionDef):
                self._check_long_method(node, None, source)
                self._check_deep_nesting(node, file_path, source)

    def xǁRigidityDetectorǁ_analyze_ast__mutmut_10(self, tree: ast.AST, file_path: str, source: str) -> None:
        """Analyze AST for rigid patterns."""
        for node in ast.walk(tree):
            # Check for god classes
            if isinstance(node, ast.ClassDef):
                self._check_god_class(node, file_path, source)

            # Check for long methods
            if isinstance(node, ast.FunctionDef):
                self._check_long_method(node, file_path, None)
                self._check_deep_nesting(node, file_path, source)

    def xǁRigidityDetectorǁ_analyze_ast__mutmut_11(self, tree: ast.AST, file_path: str, source: str) -> None:
        """Analyze AST for rigid patterns."""
        for node in ast.walk(tree):
            # Check for god classes
            if isinstance(node, ast.ClassDef):
                self._check_god_class(node, file_path, source)

            # Check for long methods
            if isinstance(node, ast.FunctionDef):
                self._check_long_method(file_path, source)
                self._check_deep_nesting(node, file_path, source)

    def xǁRigidityDetectorǁ_analyze_ast__mutmut_12(self, tree: ast.AST, file_path: str, source: str) -> None:
        """Analyze AST for rigid patterns."""
        for node in ast.walk(tree):
            # Check for god classes
            if isinstance(node, ast.ClassDef):
                self._check_god_class(node, file_path, source)

            # Check for long methods
            if isinstance(node, ast.FunctionDef):
                self._check_long_method(node, source)
                self._check_deep_nesting(node, file_path, source)

    def xǁRigidityDetectorǁ_analyze_ast__mutmut_13(self, tree: ast.AST, file_path: str, source: str) -> None:
        """Analyze AST for rigid patterns."""
        for node in ast.walk(tree):
            # Check for god classes
            if isinstance(node, ast.ClassDef):
                self._check_god_class(node, file_path, source)

            # Check for long methods
            if isinstance(node, ast.FunctionDef):
                self._check_long_method(node, file_path, )
                self._check_deep_nesting(node, file_path, source)

    def xǁRigidityDetectorǁ_analyze_ast__mutmut_14(self, tree: ast.AST, file_path: str, source: str) -> None:
        """Analyze AST for rigid patterns."""
        for node in ast.walk(tree):
            # Check for god classes
            if isinstance(node, ast.ClassDef):
                self._check_god_class(node, file_path, source)

            # Check for long methods
            if isinstance(node, ast.FunctionDef):
                self._check_long_method(node, file_path, source)
                self._check_deep_nesting(None, file_path, source)

    def xǁRigidityDetectorǁ_analyze_ast__mutmut_15(self, tree: ast.AST, file_path: str, source: str) -> None:
        """Analyze AST for rigid patterns."""
        for node in ast.walk(tree):
            # Check for god classes
            if isinstance(node, ast.ClassDef):
                self._check_god_class(node, file_path, source)

            # Check for long methods
            if isinstance(node, ast.FunctionDef):
                self._check_long_method(node, file_path, source)
                self._check_deep_nesting(node, None, source)

    def xǁRigidityDetectorǁ_analyze_ast__mutmut_16(self, tree: ast.AST, file_path: str, source: str) -> None:
        """Analyze AST for rigid patterns."""
        for node in ast.walk(tree):
            # Check for god classes
            if isinstance(node, ast.ClassDef):
                self._check_god_class(node, file_path, source)

            # Check for long methods
            if isinstance(node, ast.FunctionDef):
                self._check_long_method(node, file_path, source)
                self._check_deep_nesting(node, file_path, None)

    def xǁRigidityDetectorǁ_analyze_ast__mutmut_17(self, tree: ast.AST, file_path: str, source: str) -> None:
        """Analyze AST for rigid patterns."""
        for node in ast.walk(tree):
            # Check for god classes
            if isinstance(node, ast.ClassDef):
                self._check_god_class(node, file_path, source)

            # Check for long methods
            if isinstance(node, ast.FunctionDef):
                self._check_long_method(node, file_path, source)
                self._check_deep_nesting(file_path, source)

    def xǁRigidityDetectorǁ_analyze_ast__mutmut_18(self, tree: ast.AST, file_path: str, source: str) -> None:
        """Analyze AST for rigid patterns."""
        for node in ast.walk(tree):
            # Check for god classes
            if isinstance(node, ast.ClassDef):
                self._check_god_class(node, file_path, source)

            # Check for long methods
            if isinstance(node, ast.FunctionDef):
                self._check_long_method(node, file_path, source)
                self._check_deep_nesting(node, source)

    def xǁRigidityDetectorǁ_analyze_ast__mutmut_19(self, tree: ast.AST, file_path: str, source: str) -> None:
        """Analyze AST for rigid patterns."""
        for node in ast.walk(tree):
            # Check for god classes
            if isinstance(node, ast.ClassDef):
                self._check_god_class(node, file_path, source)

            # Check for long methods
            if isinstance(node, ast.FunctionDef):
                self._check_long_method(node, file_path, source)
                self._check_deep_nesting(node, file_path, )
    
    xǁRigidityDetectorǁ_analyze_ast__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRigidityDetectorǁ_analyze_ast__mutmut_1': xǁRigidityDetectorǁ_analyze_ast__mutmut_1, 
        'xǁRigidityDetectorǁ_analyze_ast__mutmut_2': xǁRigidityDetectorǁ_analyze_ast__mutmut_2, 
        'xǁRigidityDetectorǁ_analyze_ast__mutmut_3': xǁRigidityDetectorǁ_analyze_ast__mutmut_3, 
        'xǁRigidityDetectorǁ_analyze_ast__mutmut_4': xǁRigidityDetectorǁ_analyze_ast__mutmut_4, 
        'xǁRigidityDetectorǁ_analyze_ast__mutmut_5': xǁRigidityDetectorǁ_analyze_ast__mutmut_5, 
        'xǁRigidityDetectorǁ_analyze_ast__mutmut_6': xǁRigidityDetectorǁ_analyze_ast__mutmut_6, 
        'xǁRigidityDetectorǁ_analyze_ast__mutmut_7': xǁRigidityDetectorǁ_analyze_ast__mutmut_7, 
        'xǁRigidityDetectorǁ_analyze_ast__mutmut_8': xǁRigidityDetectorǁ_analyze_ast__mutmut_8, 
        'xǁRigidityDetectorǁ_analyze_ast__mutmut_9': xǁRigidityDetectorǁ_analyze_ast__mutmut_9, 
        'xǁRigidityDetectorǁ_analyze_ast__mutmut_10': xǁRigidityDetectorǁ_analyze_ast__mutmut_10, 
        'xǁRigidityDetectorǁ_analyze_ast__mutmut_11': xǁRigidityDetectorǁ_analyze_ast__mutmut_11, 
        'xǁRigidityDetectorǁ_analyze_ast__mutmut_12': xǁRigidityDetectorǁ_analyze_ast__mutmut_12, 
        'xǁRigidityDetectorǁ_analyze_ast__mutmut_13': xǁRigidityDetectorǁ_analyze_ast__mutmut_13, 
        'xǁRigidityDetectorǁ_analyze_ast__mutmut_14': xǁRigidityDetectorǁ_analyze_ast__mutmut_14, 
        'xǁRigidityDetectorǁ_analyze_ast__mutmut_15': xǁRigidityDetectorǁ_analyze_ast__mutmut_15, 
        'xǁRigidityDetectorǁ_analyze_ast__mutmut_16': xǁRigidityDetectorǁ_analyze_ast__mutmut_16, 
        'xǁRigidityDetectorǁ_analyze_ast__mutmut_17': xǁRigidityDetectorǁ_analyze_ast__mutmut_17, 
        'xǁRigidityDetectorǁ_analyze_ast__mutmut_18': xǁRigidityDetectorǁ_analyze_ast__mutmut_18, 
        'xǁRigidityDetectorǁ_analyze_ast__mutmut_19': xǁRigidityDetectorǁ_analyze_ast__mutmut_19
    }
    
    def _analyze_ast(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRigidityDetectorǁ_analyze_ast__mutmut_orig"), object.__getattribute__(self, "xǁRigidityDetectorǁ_analyze_ast__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _analyze_ast.__signature__ = _mutmut_signature(xǁRigidityDetectorǁ_analyze_ast__mutmut_orig)
    xǁRigidityDetectorǁ_analyze_ast__mutmut_orig.__name__ = 'xǁRigidityDetectorǁ_analyze_ast'

    def xǁRigidityDetectorǁ_check_god_class__mutmut_orig(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(source, node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_1(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = None

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(source, node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_2(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) >= self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(source, node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_3(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = None

            context = self._get_code_snippet(source, node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_4(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(None, (len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(source, node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_5(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, None)

            context = self._get_code_snippet(source, node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_6(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min((len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(source, node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_7(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, )

            context = self._get_code_snippet(source, node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_8(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(2.0, (len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(source, node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_9(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) * 20.0)

            context = self._get_code_snippet(source, node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_10(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) + self.max_class_methods) / 20.0)

            context = self._get_code_snippet(source, node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_11(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) / 21.0)

            context = self._get_code_snippet(source, node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_12(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) / 20.0)

            context = None

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_13(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(None, node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_14(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(source, None, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_15(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(source, node.lineno, None)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_16(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_17(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(source, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_18(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(source, node.lineno, )

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_19(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(source, node.lineno, 4)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_20(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(source, node.lineno, 3)

            self.detections.append(
                None
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_21(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(source, node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=None,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_22(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(source, node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=None,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_23(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(source, node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=None,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_24(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(source, node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=None,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_25(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(source, node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=None,
                    context=context,
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_26(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(source, node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=None,
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_27(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(source, node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata=None,
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_28(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(source, node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_29(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(source, node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_30(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(source, node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_31(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(source, node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_32(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(source, node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    context=context,
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_33(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(source, node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_34(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(source, node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_35(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(source, node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"XXnum_methodsXX": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_36(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(source, node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"NUM_METHODS": len(methods), "class_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_37(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(source, node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"num_methods": len(methods), "XXclass_nameXX": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_god_class__mutmut_38(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [
            n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(source, node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"num_methods": len(methods), "CLASS_NAME": node.name},
                )
            )
    
    xǁRigidityDetectorǁ_check_god_class__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRigidityDetectorǁ_check_god_class__mutmut_1': xǁRigidityDetectorǁ_check_god_class__mutmut_1, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_2': xǁRigidityDetectorǁ_check_god_class__mutmut_2, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_3': xǁRigidityDetectorǁ_check_god_class__mutmut_3, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_4': xǁRigidityDetectorǁ_check_god_class__mutmut_4, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_5': xǁRigidityDetectorǁ_check_god_class__mutmut_5, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_6': xǁRigidityDetectorǁ_check_god_class__mutmut_6, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_7': xǁRigidityDetectorǁ_check_god_class__mutmut_7, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_8': xǁRigidityDetectorǁ_check_god_class__mutmut_8, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_9': xǁRigidityDetectorǁ_check_god_class__mutmut_9, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_10': xǁRigidityDetectorǁ_check_god_class__mutmut_10, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_11': xǁRigidityDetectorǁ_check_god_class__mutmut_11, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_12': xǁRigidityDetectorǁ_check_god_class__mutmut_12, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_13': xǁRigidityDetectorǁ_check_god_class__mutmut_13, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_14': xǁRigidityDetectorǁ_check_god_class__mutmut_14, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_15': xǁRigidityDetectorǁ_check_god_class__mutmut_15, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_16': xǁRigidityDetectorǁ_check_god_class__mutmut_16, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_17': xǁRigidityDetectorǁ_check_god_class__mutmut_17, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_18': xǁRigidityDetectorǁ_check_god_class__mutmut_18, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_19': xǁRigidityDetectorǁ_check_god_class__mutmut_19, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_20': xǁRigidityDetectorǁ_check_god_class__mutmut_20, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_21': xǁRigidityDetectorǁ_check_god_class__mutmut_21, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_22': xǁRigidityDetectorǁ_check_god_class__mutmut_22, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_23': xǁRigidityDetectorǁ_check_god_class__mutmut_23, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_24': xǁRigidityDetectorǁ_check_god_class__mutmut_24, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_25': xǁRigidityDetectorǁ_check_god_class__mutmut_25, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_26': xǁRigidityDetectorǁ_check_god_class__mutmut_26, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_27': xǁRigidityDetectorǁ_check_god_class__mutmut_27, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_28': xǁRigidityDetectorǁ_check_god_class__mutmut_28, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_29': xǁRigidityDetectorǁ_check_god_class__mutmut_29, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_30': xǁRigidityDetectorǁ_check_god_class__mutmut_30, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_31': xǁRigidityDetectorǁ_check_god_class__mutmut_31, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_32': xǁRigidityDetectorǁ_check_god_class__mutmut_32, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_33': xǁRigidityDetectorǁ_check_god_class__mutmut_33, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_34': xǁRigidityDetectorǁ_check_god_class__mutmut_34, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_35': xǁRigidityDetectorǁ_check_god_class__mutmut_35, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_36': xǁRigidityDetectorǁ_check_god_class__mutmut_36, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_37': xǁRigidityDetectorǁ_check_god_class__mutmut_37, 
        'xǁRigidityDetectorǁ_check_god_class__mutmut_38': xǁRigidityDetectorǁ_check_god_class__mutmut_38
    }
    
    def _check_god_class(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRigidityDetectorǁ_check_god_class__mutmut_orig"), object.__getattribute__(self, "xǁRigidityDetectorǁ_check_god_class__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _check_god_class.__signature__ = _mutmut_signature(xǁRigidityDetectorǁ_check_god_class__mutmut_orig)
    xǁRigidityDetectorǁ_check_god_class__mutmut_orig.__name__ = 'xǁRigidityDetectorǁ_check_god_class'

    def xǁRigidityDetectorǁ_check_long_method__mutmut_orig(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_1(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") and node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_2(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_3(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(None, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_4(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, None) or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_5(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr("end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_6(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, ) or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_7(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "XXend_linenoXX") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_8(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "END_LINENO") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_9(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is not None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_10(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = None

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_11(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno - 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_12(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno + node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_13(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 2

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_14(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines >= self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_15(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = None

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_16(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(None, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_17(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, None)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_18(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min((method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_19(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, )

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_20(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(2.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_21(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) * 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_22(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines + self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_23(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 51.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_24(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = None

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_25(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(None, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_26(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, None, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_27(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, None)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_28(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_29(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_30(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, )

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_31(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 6)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_32(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                None
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_33(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=None,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_34(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=None,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_35(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=None,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_36(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=None,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_37(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=None,
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_38(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=None,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_39(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata=None,
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_40(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_41(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_42(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_43(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_44(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_45(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_46(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_47(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"XXnum_linesXX": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_48(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"NUM_LINES": method_lines, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_49(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "XXmethod_nameXX": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_long_method__mutmut_50(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "METHOD_NAME": node.name},
                )
            )
    
    xǁRigidityDetectorǁ_check_long_method__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRigidityDetectorǁ_check_long_method__mutmut_1': xǁRigidityDetectorǁ_check_long_method__mutmut_1, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_2': xǁRigidityDetectorǁ_check_long_method__mutmut_2, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_3': xǁRigidityDetectorǁ_check_long_method__mutmut_3, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_4': xǁRigidityDetectorǁ_check_long_method__mutmut_4, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_5': xǁRigidityDetectorǁ_check_long_method__mutmut_5, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_6': xǁRigidityDetectorǁ_check_long_method__mutmut_6, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_7': xǁRigidityDetectorǁ_check_long_method__mutmut_7, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_8': xǁRigidityDetectorǁ_check_long_method__mutmut_8, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_9': xǁRigidityDetectorǁ_check_long_method__mutmut_9, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_10': xǁRigidityDetectorǁ_check_long_method__mutmut_10, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_11': xǁRigidityDetectorǁ_check_long_method__mutmut_11, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_12': xǁRigidityDetectorǁ_check_long_method__mutmut_12, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_13': xǁRigidityDetectorǁ_check_long_method__mutmut_13, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_14': xǁRigidityDetectorǁ_check_long_method__mutmut_14, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_15': xǁRigidityDetectorǁ_check_long_method__mutmut_15, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_16': xǁRigidityDetectorǁ_check_long_method__mutmut_16, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_17': xǁRigidityDetectorǁ_check_long_method__mutmut_17, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_18': xǁRigidityDetectorǁ_check_long_method__mutmut_18, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_19': xǁRigidityDetectorǁ_check_long_method__mutmut_19, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_20': xǁRigidityDetectorǁ_check_long_method__mutmut_20, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_21': xǁRigidityDetectorǁ_check_long_method__mutmut_21, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_22': xǁRigidityDetectorǁ_check_long_method__mutmut_22, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_23': xǁRigidityDetectorǁ_check_long_method__mutmut_23, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_24': xǁRigidityDetectorǁ_check_long_method__mutmut_24, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_25': xǁRigidityDetectorǁ_check_long_method__mutmut_25, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_26': xǁRigidityDetectorǁ_check_long_method__mutmut_26, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_27': xǁRigidityDetectorǁ_check_long_method__mutmut_27, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_28': xǁRigidityDetectorǁ_check_long_method__mutmut_28, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_29': xǁRigidityDetectorǁ_check_long_method__mutmut_29, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_30': xǁRigidityDetectorǁ_check_long_method__mutmut_30, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_31': xǁRigidityDetectorǁ_check_long_method__mutmut_31, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_32': xǁRigidityDetectorǁ_check_long_method__mutmut_32, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_33': xǁRigidityDetectorǁ_check_long_method__mutmut_33, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_34': xǁRigidityDetectorǁ_check_long_method__mutmut_34, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_35': xǁRigidityDetectorǁ_check_long_method__mutmut_35, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_36': xǁRigidityDetectorǁ_check_long_method__mutmut_36, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_37': xǁRigidityDetectorǁ_check_long_method__mutmut_37, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_38': xǁRigidityDetectorǁ_check_long_method__mutmut_38, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_39': xǁRigidityDetectorǁ_check_long_method__mutmut_39, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_40': xǁRigidityDetectorǁ_check_long_method__mutmut_40, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_41': xǁRigidityDetectorǁ_check_long_method__mutmut_41, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_42': xǁRigidityDetectorǁ_check_long_method__mutmut_42, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_43': xǁRigidityDetectorǁ_check_long_method__mutmut_43, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_44': xǁRigidityDetectorǁ_check_long_method__mutmut_44, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_45': xǁRigidityDetectorǁ_check_long_method__mutmut_45, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_46': xǁRigidityDetectorǁ_check_long_method__mutmut_46, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_47': xǁRigidityDetectorǁ_check_long_method__mutmut_47, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_48': xǁRigidityDetectorǁ_check_long_method__mutmut_48, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_49': xǁRigidityDetectorǁ_check_long_method__mutmut_49, 
        'xǁRigidityDetectorǁ_check_long_method__mutmut_50': xǁRigidityDetectorǁ_check_long_method__mutmut_50
    }
    
    def _check_long_method(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRigidityDetectorǁ_check_long_method__mutmut_orig"), object.__getattribute__(self, "xǁRigidityDetectorǁ_check_long_method__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _check_long_method.__signature__ = _mutmut_signature(xǁRigidityDetectorǁ_check_long_method__mutmut_orig)
    xǁRigidityDetectorǁ_check_long_method__mutmut_orig.__name__ = 'xǁRigidityDetectorǁ_check_long_method'

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_orig(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_1(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = None

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_2(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(None)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_3(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth >= self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_4(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = None

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_5(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(None, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_6(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, None)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_7(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min((max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_8(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, )

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_9(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(2.0, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_10(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) * 4.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_11(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth + self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_12(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 5.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_13(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 4.0)

            context = None

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_14(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(None, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_15(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, None, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_16(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, node.lineno, None)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_17(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_18(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_19(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, node.lineno, )

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_20(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, node.lineno, 6)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_21(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                None
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_22(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=None,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_23(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=None,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_24(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=None,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_25(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=None,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_26(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=None,
                    context=context,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_27(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=None,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_28(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata=None,
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_29(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_30(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_31(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_32(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_33(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    context=context,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_34(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_35(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_36(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"XXmax_depthXX": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_37(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"MAX_DEPTH": max_depth, "method_name": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_38(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"max_depth": max_depth, "XXmethod_nameXX": node.name},
                )
            )

    def xǁRigidityDetectorǁ_check_deep_nesting__mutmut_39(
        self, node: ast.FunctionDef, file_path: str, source: str
    ) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"max_depth": max_depth, "METHOD_NAME": node.name},
                )
            )
    
    xǁRigidityDetectorǁ_check_deep_nesting__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_1': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_1, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_2': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_2, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_3': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_3, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_4': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_4, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_5': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_5, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_6': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_6, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_7': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_7, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_8': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_8, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_9': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_9, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_10': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_10, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_11': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_11, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_12': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_12, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_13': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_13, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_14': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_14, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_15': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_15, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_16': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_16, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_17': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_17, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_18': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_18, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_19': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_19, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_20': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_20, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_21': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_21, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_22': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_22, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_23': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_23, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_24': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_24, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_25': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_25, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_26': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_26, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_27': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_27, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_28': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_28, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_29': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_29, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_30': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_30, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_31': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_31, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_32': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_32, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_33': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_33, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_34': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_34, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_35': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_35, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_36': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_36, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_37': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_37, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_38': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_38, 
        'xǁRigidityDetectorǁ_check_deep_nesting__mutmut_39': xǁRigidityDetectorǁ_check_deep_nesting__mutmut_39
    }
    
    def _check_deep_nesting(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRigidityDetectorǁ_check_deep_nesting__mutmut_orig"), object.__getattribute__(self, "xǁRigidityDetectorǁ_check_deep_nesting__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _check_deep_nesting.__signature__ = _mutmut_signature(xǁRigidityDetectorǁ_check_deep_nesting__mutmut_orig)
    xǁRigidityDetectorǁ_check_deep_nesting__mutmut_orig.__name__ = 'xǁRigidityDetectorǁ_check_deep_nesting'

    def xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_orig(self, node: ast.AST, current_depth: int = 0) -> int:
        """Recursively calculate maximum nesting depth."""
        max_depth = current_depth

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._get_max_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)

        return max_depth

    def xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_1(self, node: ast.AST, current_depth: int = 1) -> int:
        """Recursively calculate maximum nesting depth."""
        max_depth = current_depth

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._get_max_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)

        return max_depth

    def xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_2(self, node: ast.AST, current_depth: int = 0) -> int:
        """Recursively calculate maximum nesting depth."""
        max_depth = None

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._get_max_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)

        return max_depth

    def xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_3(self, node: ast.AST, current_depth: int = 0) -> int:
        """Recursively calculate maximum nesting depth."""
        max_depth = current_depth

        for child in ast.iter_child_nodes(None):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._get_max_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)

        return max_depth

    def xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_4(self, node: ast.AST, current_depth: int = 0) -> int:
        """Recursively calculate maximum nesting depth."""
        max_depth = current_depth

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = None
                max_depth = max(max_depth, child_depth)

        return max_depth

    def xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_5(self, node: ast.AST, current_depth: int = 0) -> int:
        """Recursively calculate maximum nesting depth."""
        max_depth = current_depth

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._get_max_nesting_depth(None, current_depth + 1)
                max_depth = max(max_depth, child_depth)

        return max_depth

    def xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_6(self, node: ast.AST, current_depth: int = 0) -> int:
        """Recursively calculate maximum nesting depth."""
        max_depth = current_depth

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._get_max_nesting_depth(child, None)
                max_depth = max(max_depth, child_depth)

        return max_depth

    def xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_7(self, node: ast.AST, current_depth: int = 0) -> int:
        """Recursively calculate maximum nesting depth."""
        max_depth = current_depth

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._get_max_nesting_depth(current_depth + 1)
                max_depth = max(max_depth, child_depth)

        return max_depth

    def xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_8(self, node: ast.AST, current_depth: int = 0) -> int:
        """Recursively calculate maximum nesting depth."""
        max_depth = current_depth

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._get_max_nesting_depth(child, )
                max_depth = max(max_depth, child_depth)

        return max_depth

    def xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_9(self, node: ast.AST, current_depth: int = 0) -> int:
        """Recursively calculate maximum nesting depth."""
        max_depth = current_depth

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._get_max_nesting_depth(child, current_depth - 1)
                max_depth = max(max_depth, child_depth)

        return max_depth

    def xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_10(self, node: ast.AST, current_depth: int = 0) -> int:
        """Recursively calculate maximum nesting depth."""
        max_depth = current_depth

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._get_max_nesting_depth(child, current_depth + 2)
                max_depth = max(max_depth, child_depth)

        return max_depth

    def xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_11(self, node: ast.AST, current_depth: int = 0) -> int:
        """Recursively calculate maximum nesting depth."""
        max_depth = current_depth

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._get_max_nesting_depth(child, current_depth + 1)
                max_depth = None

        return max_depth

    def xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_12(self, node: ast.AST, current_depth: int = 0) -> int:
        """Recursively calculate maximum nesting depth."""
        max_depth = current_depth

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._get_max_nesting_depth(child, current_depth + 1)
                max_depth = max(None, child_depth)

        return max_depth

    def xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_13(self, node: ast.AST, current_depth: int = 0) -> int:
        """Recursively calculate maximum nesting depth."""
        max_depth = current_depth

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._get_max_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, None)

        return max_depth

    def xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_14(self, node: ast.AST, current_depth: int = 0) -> int:
        """Recursively calculate maximum nesting depth."""
        max_depth = current_depth

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._get_max_nesting_depth(child, current_depth + 1)
                max_depth = max(child_depth)

        return max_depth

    def xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_15(self, node: ast.AST, current_depth: int = 0) -> int:
        """Recursively calculate maximum nesting depth."""
        max_depth = current_depth

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._get_max_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, )

        return max_depth
    
    xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_1': xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_1, 
        'xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_2': xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_2, 
        'xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_3': xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_3, 
        'xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_4': xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_4, 
        'xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_5': xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_5, 
        'xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_6': xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_6, 
        'xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_7': xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_7, 
        'xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_8': xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_8, 
        'xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_9': xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_9, 
        'xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_10': xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_10, 
        'xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_11': xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_11, 
        'xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_12': xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_12, 
        'xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_13': xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_13, 
        'xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_14': xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_14, 
        'xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_15': xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_15
    }
    
    def _get_max_nesting_depth(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_orig"), object.__getattribute__(self, "xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _get_max_nesting_depth.__signature__ = _mutmut_signature(xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_orig)
    xǁRigidityDetectorǁ_get_max_nesting_depth__mutmut_orig.__name__ = 'xǁRigidityDetectorǁ_get_max_nesting_depth'

    def xǁRigidityDetectorǁ_get_code_snippet__mutmut_orig(self, source: str, line_num: int, num_lines: int = 3) -> str:
        """Extract a code snippet around a line number."""
        lines = source.splitlines()
        start = max(0, line_num - 1)
        end = min(len(lines), line_num + num_lines)
        return "\n".join(lines[start:end])

    def xǁRigidityDetectorǁ_get_code_snippet__mutmut_1(self, source: str, line_num: int, num_lines: int = 4) -> str:
        """Extract a code snippet around a line number."""
        lines = source.splitlines()
        start = max(0, line_num - 1)
        end = min(len(lines), line_num + num_lines)
        return "\n".join(lines[start:end])

    def xǁRigidityDetectorǁ_get_code_snippet__mutmut_2(self, source: str, line_num: int, num_lines: int = 3) -> str:
        """Extract a code snippet around a line number."""
        lines = None
        start = max(0, line_num - 1)
        end = min(len(lines), line_num + num_lines)
        return "\n".join(lines[start:end])

    def xǁRigidityDetectorǁ_get_code_snippet__mutmut_3(self, source: str, line_num: int, num_lines: int = 3) -> str:
        """Extract a code snippet around a line number."""
        lines = source.splitlines()
        start = None
        end = min(len(lines), line_num + num_lines)
        return "\n".join(lines[start:end])

    def xǁRigidityDetectorǁ_get_code_snippet__mutmut_4(self, source: str, line_num: int, num_lines: int = 3) -> str:
        """Extract a code snippet around a line number."""
        lines = source.splitlines()
        start = max(None, line_num - 1)
        end = min(len(lines), line_num + num_lines)
        return "\n".join(lines[start:end])

    def xǁRigidityDetectorǁ_get_code_snippet__mutmut_5(self, source: str, line_num: int, num_lines: int = 3) -> str:
        """Extract a code snippet around a line number."""
        lines = source.splitlines()
        start = max(0, None)
        end = min(len(lines), line_num + num_lines)
        return "\n".join(lines[start:end])

    def xǁRigidityDetectorǁ_get_code_snippet__mutmut_6(self, source: str, line_num: int, num_lines: int = 3) -> str:
        """Extract a code snippet around a line number."""
        lines = source.splitlines()
        start = max(line_num - 1)
        end = min(len(lines), line_num + num_lines)
        return "\n".join(lines[start:end])

    def xǁRigidityDetectorǁ_get_code_snippet__mutmut_7(self, source: str, line_num: int, num_lines: int = 3) -> str:
        """Extract a code snippet around a line number."""
        lines = source.splitlines()
        start = max(0, )
        end = min(len(lines), line_num + num_lines)
        return "\n".join(lines[start:end])

    def xǁRigidityDetectorǁ_get_code_snippet__mutmut_8(self, source: str, line_num: int, num_lines: int = 3) -> str:
        """Extract a code snippet around a line number."""
        lines = source.splitlines()
        start = max(1, line_num - 1)
        end = min(len(lines), line_num + num_lines)
        return "\n".join(lines[start:end])

    def xǁRigidityDetectorǁ_get_code_snippet__mutmut_9(self, source: str, line_num: int, num_lines: int = 3) -> str:
        """Extract a code snippet around a line number."""
        lines = source.splitlines()
        start = max(0, line_num + 1)
        end = min(len(lines), line_num + num_lines)
        return "\n".join(lines[start:end])

    def xǁRigidityDetectorǁ_get_code_snippet__mutmut_10(self, source: str, line_num: int, num_lines: int = 3) -> str:
        """Extract a code snippet around a line number."""
        lines = source.splitlines()
        start = max(0, line_num - 2)
        end = min(len(lines), line_num + num_lines)
        return "\n".join(lines[start:end])

    def xǁRigidityDetectorǁ_get_code_snippet__mutmut_11(self, source: str, line_num: int, num_lines: int = 3) -> str:
        """Extract a code snippet around a line number."""
        lines = source.splitlines()
        start = max(0, line_num - 1)
        end = None
        return "\n".join(lines[start:end])

    def xǁRigidityDetectorǁ_get_code_snippet__mutmut_12(self, source: str, line_num: int, num_lines: int = 3) -> str:
        """Extract a code snippet around a line number."""
        lines = source.splitlines()
        start = max(0, line_num - 1)
        end = min(None, line_num + num_lines)
        return "\n".join(lines[start:end])

    def xǁRigidityDetectorǁ_get_code_snippet__mutmut_13(self, source: str, line_num: int, num_lines: int = 3) -> str:
        """Extract a code snippet around a line number."""
        lines = source.splitlines()
        start = max(0, line_num - 1)
        end = min(len(lines), None)
        return "\n".join(lines[start:end])

    def xǁRigidityDetectorǁ_get_code_snippet__mutmut_14(self, source: str, line_num: int, num_lines: int = 3) -> str:
        """Extract a code snippet around a line number."""
        lines = source.splitlines()
        start = max(0, line_num - 1)
        end = min(line_num + num_lines)
        return "\n".join(lines[start:end])

    def xǁRigidityDetectorǁ_get_code_snippet__mutmut_15(self, source: str, line_num: int, num_lines: int = 3) -> str:
        """Extract a code snippet around a line number."""
        lines = source.splitlines()
        start = max(0, line_num - 1)
        end = min(len(lines), )
        return "\n".join(lines[start:end])

    def xǁRigidityDetectorǁ_get_code_snippet__mutmut_16(self, source: str, line_num: int, num_lines: int = 3) -> str:
        """Extract a code snippet around a line number."""
        lines = source.splitlines()
        start = max(0, line_num - 1)
        end = min(len(lines), line_num - num_lines)
        return "\n".join(lines[start:end])

    def xǁRigidityDetectorǁ_get_code_snippet__mutmut_17(self, source: str, line_num: int, num_lines: int = 3) -> str:
        """Extract a code snippet around a line number."""
        lines = source.splitlines()
        start = max(0, line_num - 1)
        end = min(len(lines), line_num + num_lines)
        return "\n".join(None)

    def xǁRigidityDetectorǁ_get_code_snippet__mutmut_18(self, source: str, line_num: int, num_lines: int = 3) -> str:
        """Extract a code snippet around a line number."""
        lines = source.splitlines()
        start = max(0, line_num - 1)
        end = min(len(lines), line_num + num_lines)
        return "XX\nXX".join(lines[start:end])
    
    xǁRigidityDetectorǁ_get_code_snippet__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRigidityDetectorǁ_get_code_snippet__mutmut_1': xǁRigidityDetectorǁ_get_code_snippet__mutmut_1, 
        'xǁRigidityDetectorǁ_get_code_snippet__mutmut_2': xǁRigidityDetectorǁ_get_code_snippet__mutmut_2, 
        'xǁRigidityDetectorǁ_get_code_snippet__mutmut_3': xǁRigidityDetectorǁ_get_code_snippet__mutmut_3, 
        'xǁRigidityDetectorǁ_get_code_snippet__mutmut_4': xǁRigidityDetectorǁ_get_code_snippet__mutmut_4, 
        'xǁRigidityDetectorǁ_get_code_snippet__mutmut_5': xǁRigidityDetectorǁ_get_code_snippet__mutmut_5, 
        'xǁRigidityDetectorǁ_get_code_snippet__mutmut_6': xǁRigidityDetectorǁ_get_code_snippet__mutmut_6, 
        'xǁRigidityDetectorǁ_get_code_snippet__mutmut_7': xǁRigidityDetectorǁ_get_code_snippet__mutmut_7, 
        'xǁRigidityDetectorǁ_get_code_snippet__mutmut_8': xǁRigidityDetectorǁ_get_code_snippet__mutmut_8, 
        'xǁRigidityDetectorǁ_get_code_snippet__mutmut_9': xǁRigidityDetectorǁ_get_code_snippet__mutmut_9, 
        'xǁRigidityDetectorǁ_get_code_snippet__mutmut_10': xǁRigidityDetectorǁ_get_code_snippet__mutmut_10, 
        'xǁRigidityDetectorǁ_get_code_snippet__mutmut_11': xǁRigidityDetectorǁ_get_code_snippet__mutmut_11, 
        'xǁRigidityDetectorǁ_get_code_snippet__mutmut_12': xǁRigidityDetectorǁ_get_code_snippet__mutmut_12, 
        'xǁRigidityDetectorǁ_get_code_snippet__mutmut_13': xǁRigidityDetectorǁ_get_code_snippet__mutmut_13, 
        'xǁRigidityDetectorǁ_get_code_snippet__mutmut_14': xǁRigidityDetectorǁ_get_code_snippet__mutmut_14, 
        'xǁRigidityDetectorǁ_get_code_snippet__mutmut_15': xǁRigidityDetectorǁ_get_code_snippet__mutmut_15, 
        'xǁRigidityDetectorǁ_get_code_snippet__mutmut_16': xǁRigidityDetectorǁ_get_code_snippet__mutmut_16, 
        'xǁRigidityDetectorǁ_get_code_snippet__mutmut_17': xǁRigidityDetectorǁ_get_code_snippet__mutmut_17, 
        'xǁRigidityDetectorǁ_get_code_snippet__mutmut_18': xǁRigidityDetectorǁ_get_code_snippet__mutmut_18
    }
    
    def _get_code_snippet(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRigidityDetectorǁ_get_code_snippet__mutmut_orig"), object.__getattribute__(self, "xǁRigidityDetectorǁ_get_code_snippet__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _get_code_snippet.__signature__ = _mutmut_signature(xǁRigidityDetectorǁ_get_code_snippet__mutmut_orig)
    xǁRigidityDetectorǁ_get_code_snippet__mutmut_orig.__name__ = 'xǁRigidityDetectorǁ_get_code_snippet'


class DeterritorializationEngine:
    """
    Engine for identifying rigid patterns and proposing lines of flight.

    Implements Deleuzian deterritorialization principles to enable
    creative refactoring and innovation.

    Example:
        >>> engine = DeterritorializationEngine()
        >>> detections = engine.detect_rigidity("src/codex/")
        >>> lines_of_flight = engine.propose_lines_of_flight()
        >>> for line in lines_of_flight:
        ...     print(line)
    """

    def xǁDeterritorializationEngineǁ__init____mutmut_orig(self) -> None:
        self.detector = RigidityDetector()
        self.rigidities: List[RigidityDetection] = []
        self.lines_of_flight: List[LineOfFlight] = []
        LOGGER.info("DeterritorializationEngine initialized")

    def xǁDeterritorializationEngineǁ__init____mutmut_1(self) -> None:
        self.detector = None
        self.rigidities: List[RigidityDetection] = []
        self.lines_of_flight: List[LineOfFlight] = []
        LOGGER.info("DeterritorializationEngine initialized")

    def xǁDeterritorializationEngineǁ__init____mutmut_2(self) -> None:
        self.detector = RigidityDetector()
        self.rigidities: List[RigidityDetection] = None
        self.lines_of_flight: List[LineOfFlight] = []
        LOGGER.info("DeterritorializationEngine initialized")

    def xǁDeterritorializationEngineǁ__init____mutmut_3(self) -> None:
        self.detector = RigidityDetector()
        self.rigidities: List[RigidityDetection] = []
        self.lines_of_flight: List[LineOfFlight] = None
        LOGGER.info("DeterritorializationEngine initialized")

    def xǁDeterritorializationEngineǁ__init____mutmut_4(self) -> None:
        self.detector = RigidityDetector()
        self.rigidities: List[RigidityDetection] = []
        self.lines_of_flight: List[LineOfFlight] = []
        LOGGER.info(None)

    def xǁDeterritorializationEngineǁ__init____mutmut_5(self) -> None:
        self.detector = RigidityDetector()
        self.rigidities: List[RigidityDetection] = []
        self.lines_of_flight: List[LineOfFlight] = []
        LOGGER.info("XXDeterritorializationEngine initializedXX")

    def xǁDeterritorializationEngineǁ__init____mutmut_6(self) -> None:
        self.detector = RigidityDetector()
        self.rigidities: List[RigidityDetection] = []
        self.lines_of_flight: List[LineOfFlight] = []
        LOGGER.info("deterritorializationengine initialized")

    def xǁDeterritorializationEngineǁ__init____mutmut_7(self) -> None:
        self.detector = RigidityDetector()
        self.rigidities: List[RigidityDetection] = []
        self.lines_of_flight: List[LineOfFlight] = []
        LOGGER.info("DETERRITORIALIZATIONENGINE INITIALIZED")
    
    xǁDeterritorializationEngineǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDeterritorializationEngineǁ__init____mutmut_1': xǁDeterritorializationEngineǁ__init____mutmut_1, 
        'xǁDeterritorializationEngineǁ__init____mutmut_2': xǁDeterritorializationEngineǁ__init____mutmut_2, 
        'xǁDeterritorializationEngineǁ__init____mutmut_3': xǁDeterritorializationEngineǁ__init____mutmut_3, 
        'xǁDeterritorializationEngineǁ__init____mutmut_4': xǁDeterritorializationEngineǁ__init____mutmut_4, 
        'xǁDeterritorializationEngineǁ__init____mutmut_5': xǁDeterritorializationEngineǁ__init____mutmut_5, 
        'xǁDeterritorializationEngineǁ__init____mutmut_6': xǁDeterritorializationEngineǁ__init____mutmut_6, 
        'xǁDeterritorializationEngineǁ__init____mutmut_7': xǁDeterritorializationEngineǁ__init____mutmut_7
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDeterritorializationEngineǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁDeterritorializationEngineǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁDeterritorializationEngineǁ__init____mutmut_orig)
    xǁDeterritorializationEngineǁ__init____mutmut_orig.__name__ = 'xǁDeterritorializationEngineǁ__init__'

    def xǁDeterritorializationEngineǁdetect_rigidity__mutmut_orig(self, path: str | Path) -> List[RigidityDetection]:
        """
        Detect rigidity in code at the given path.

        Args:
            path: File or directory path to analyze

        Returns:
            List of detected rigidities
        """
        path = Path(path)

        if path.is_file() and path.suffix == ".py":
            self.rigidities.extend(self.detector.analyze_file(path))

        elif path.is_dir():
            for py_file in path.rglob("*.py"):
                self.rigidities.extend(self.detector.analyze_file(py_file))

        LOGGER.info(f"Detected {len(self.rigidities)} rigidities in {path}")
        return self.rigidities

    def xǁDeterritorializationEngineǁdetect_rigidity__mutmut_1(self, path: str | Path) -> List[RigidityDetection]:
        """
        Detect rigidity in code at the given path.

        Args:
            path: File or directory path to analyze

        Returns:
            List of detected rigidities
        """
        path = None

        if path.is_file() and path.suffix == ".py":
            self.rigidities.extend(self.detector.analyze_file(path))

        elif path.is_dir():
            for py_file in path.rglob("*.py"):
                self.rigidities.extend(self.detector.analyze_file(py_file))

        LOGGER.info(f"Detected {len(self.rigidities)} rigidities in {path}")
        return self.rigidities

    def xǁDeterritorializationEngineǁdetect_rigidity__mutmut_2(self, path: str | Path) -> List[RigidityDetection]:
        """
        Detect rigidity in code at the given path.

        Args:
            path: File or directory path to analyze

        Returns:
            List of detected rigidities
        """
        path = Path(None)

        if path.is_file() and path.suffix == ".py":
            self.rigidities.extend(self.detector.analyze_file(path))

        elif path.is_dir():
            for py_file in path.rglob("*.py"):
                self.rigidities.extend(self.detector.analyze_file(py_file))

        LOGGER.info(f"Detected {len(self.rigidities)} rigidities in {path}")
        return self.rigidities

    def xǁDeterritorializationEngineǁdetect_rigidity__mutmut_3(self, path: str | Path) -> List[RigidityDetection]:
        """
        Detect rigidity in code at the given path.

        Args:
            path: File or directory path to analyze

        Returns:
            List of detected rigidities
        """
        path = Path(path)

        if path.is_file() or path.suffix == ".py":
            self.rigidities.extend(self.detector.analyze_file(path))

        elif path.is_dir():
            for py_file in path.rglob("*.py"):
                self.rigidities.extend(self.detector.analyze_file(py_file))

        LOGGER.info(f"Detected {len(self.rigidities)} rigidities in {path}")
        return self.rigidities

    def xǁDeterritorializationEngineǁdetect_rigidity__mutmut_4(self, path: str | Path) -> List[RigidityDetection]:
        """
        Detect rigidity in code at the given path.

        Args:
            path: File or directory path to analyze

        Returns:
            List of detected rigidities
        """
        path = Path(path)

        if path.is_file() and path.suffix != ".py":
            self.rigidities.extend(self.detector.analyze_file(path))

        elif path.is_dir():
            for py_file in path.rglob("*.py"):
                self.rigidities.extend(self.detector.analyze_file(py_file))

        LOGGER.info(f"Detected {len(self.rigidities)} rigidities in {path}")
        return self.rigidities

    def xǁDeterritorializationEngineǁdetect_rigidity__mutmut_5(self, path: str | Path) -> List[RigidityDetection]:
        """
        Detect rigidity in code at the given path.

        Args:
            path: File or directory path to analyze

        Returns:
            List of detected rigidities
        """
        path = Path(path)

        if path.is_file() and path.suffix == "XX.pyXX":
            self.rigidities.extend(self.detector.analyze_file(path))

        elif path.is_dir():
            for py_file in path.rglob("*.py"):
                self.rigidities.extend(self.detector.analyze_file(py_file))

        LOGGER.info(f"Detected {len(self.rigidities)} rigidities in {path}")
        return self.rigidities

    def xǁDeterritorializationEngineǁdetect_rigidity__mutmut_6(self, path: str | Path) -> List[RigidityDetection]:
        """
        Detect rigidity in code at the given path.

        Args:
            path: File or directory path to analyze

        Returns:
            List of detected rigidities
        """
        path = Path(path)

        if path.is_file() and path.suffix == ".PY":
            self.rigidities.extend(self.detector.analyze_file(path))

        elif path.is_dir():
            for py_file in path.rglob("*.py"):
                self.rigidities.extend(self.detector.analyze_file(py_file))

        LOGGER.info(f"Detected {len(self.rigidities)} rigidities in {path}")
        return self.rigidities

    def xǁDeterritorializationEngineǁdetect_rigidity__mutmut_7(self, path: str | Path) -> List[RigidityDetection]:
        """
        Detect rigidity in code at the given path.

        Args:
            path: File or directory path to analyze

        Returns:
            List of detected rigidities
        """
        path = Path(path)

        if path.is_file() and path.suffix == ".py":
            self.rigidities.extend(None)

        elif path.is_dir():
            for py_file in path.rglob("*.py"):
                self.rigidities.extend(self.detector.analyze_file(py_file))

        LOGGER.info(f"Detected {len(self.rigidities)} rigidities in {path}")
        return self.rigidities

    def xǁDeterritorializationEngineǁdetect_rigidity__mutmut_8(self, path: str | Path) -> List[RigidityDetection]:
        """
        Detect rigidity in code at the given path.

        Args:
            path: File or directory path to analyze

        Returns:
            List of detected rigidities
        """
        path = Path(path)

        if path.is_file() and path.suffix == ".py":
            self.rigidities.extend(self.detector.analyze_file(None))

        elif path.is_dir():
            for py_file in path.rglob("*.py"):
                self.rigidities.extend(self.detector.analyze_file(py_file))

        LOGGER.info(f"Detected {len(self.rigidities)} rigidities in {path}")
        return self.rigidities

    def xǁDeterritorializationEngineǁdetect_rigidity__mutmut_9(self, path: str | Path) -> List[RigidityDetection]:
        """
        Detect rigidity in code at the given path.

        Args:
            path: File or directory path to analyze

        Returns:
            List of detected rigidities
        """
        path = Path(path)

        if path.is_file() and path.suffix == ".py":
            self.rigidities.extend(self.detector.analyze_file(path))

        elif path.is_dir():
            for py_file in path.rglob(None):
                self.rigidities.extend(self.detector.analyze_file(py_file))

        LOGGER.info(f"Detected {len(self.rigidities)} rigidities in {path}")
        return self.rigidities

    def xǁDeterritorializationEngineǁdetect_rigidity__mutmut_10(self, path: str | Path) -> List[RigidityDetection]:
        """
        Detect rigidity in code at the given path.

        Args:
            path: File or directory path to analyze

        Returns:
            List of detected rigidities
        """
        path = Path(path)

        if path.is_file() and path.suffix == ".py":
            self.rigidities.extend(self.detector.analyze_file(path))

        elif path.is_dir():
            for py_file in path.rglob("XX*.pyXX"):
                self.rigidities.extend(self.detector.analyze_file(py_file))

        LOGGER.info(f"Detected {len(self.rigidities)} rigidities in {path}")
        return self.rigidities

    def xǁDeterritorializationEngineǁdetect_rigidity__mutmut_11(self, path: str | Path) -> List[RigidityDetection]:
        """
        Detect rigidity in code at the given path.

        Args:
            path: File or directory path to analyze

        Returns:
            List of detected rigidities
        """
        path = Path(path)

        if path.is_file() and path.suffix == ".py":
            self.rigidities.extend(self.detector.analyze_file(path))

        elif path.is_dir():
            for py_file in path.rglob("*.PY"):
                self.rigidities.extend(self.detector.analyze_file(py_file))

        LOGGER.info(f"Detected {len(self.rigidities)} rigidities in {path}")
        return self.rigidities

    def xǁDeterritorializationEngineǁdetect_rigidity__mutmut_12(self, path: str | Path) -> List[RigidityDetection]:
        """
        Detect rigidity in code at the given path.

        Args:
            path: File or directory path to analyze

        Returns:
            List of detected rigidities
        """
        path = Path(path)

        if path.is_file() and path.suffix == ".py":
            self.rigidities.extend(self.detector.analyze_file(path))

        elif path.is_dir():
            for py_file in path.rglob("*.py"):
                self.rigidities.extend(None)

        LOGGER.info(f"Detected {len(self.rigidities)} rigidities in {path}")
        return self.rigidities

    def xǁDeterritorializationEngineǁdetect_rigidity__mutmut_13(self, path: str | Path) -> List[RigidityDetection]:
        """
        Detect rigidity in code at the given path.

        Args:
            path: File or directory path to analyze

        Returns:
            List of detected rigidities
        """
        path = Path(path)

        if path.is_file() and path.suffix == ".py":
            self.rigidities.extend(self.detector.analyze_file(path))

        elif path.is_dir():
            for py_file in path.rglob("*.py"):
                self.rigidities.extend(self.detector.analyze_file(None))

        LOGGER.info(f"Detected {len(self.rigidities)} rigidities in {path}")
        return self.rigidities

    def xǁDeterritorializationEngineǁdetect_rigidity__mutmut_14(self, path: str | Path) -> List[RigidityDetection]:
        """
        Detect rigidity in code at the given path.

        Args:
            path: File or directory path to analyze

        Returns:
            List of detected rigidities
        """
        path = Path(path)

        if path.is_file() and path.suffix == ".py":
            self.rigidities.extend(self.detector.analyze_file(path))

        elif path.is_dir():
            for py_file in path.rglob("*.py"):
                self.rigidities.extend(self.detector.analyze_file(py_file))

        LOGGER.info(None)
        return self.rigidities
    
    xǁDeterritorializationEngineǁdetect_rigidity__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDeterritorializationEngineǁdetect_rigidity__mutmut_1': xǁDeterritorializationEngineǁdetect_rigidity__mutmut_1, 
        'xǁDeterritorializationEngineǁdetect_rigidity__mutmut_2': xǁDeterritorializationEngineǁdetect_rigidity__mutmut_2, 
        'xǁDeterritorializationEngineǁdetect_rigidity__mutmut_3': xǁDeterritorializationEngineǁdetect_rigidity__mutmut_3, 
        'xǁDeterritorializationEngineǁdetect_rigidity__mutmut_4': xǁDeterritorializationEngineǁdetect_rigidity__mutmut_4, 
        'xǁDeterritorializationEngineǁdetect_rigidity__mutmut_5': xǁDeterritorializationEngineǁdetect_rigidity__mutmut_5, 
        'xǁDeterritorializationEngineǁdetect_rigidity__mutmut_6': xǁDeterritorializationEngineǁdetect_rigidity__mutmut_6, 
        'xǁDeterritorializationEngineǁdetect_rigidity__mutmut_7': xǁDeterritorializationEngineǁdetect_rigidity__mutmut_7, 
        'xǁDeterritorializationEngineǁdetect_rigidity__mutmut_8': xǁDeterritorializationEngineǁdetect_rigidity__mutmut_8, 
        'xǁDeterritorializationEngineǁdetect_rigidity__mutmut_9': xǁDeterritorializationEngineǁdetect_rigidity__mutmut_9, 
        'xǁDeterritorializationEngineǁdetect_rigidity__mutmut_10': xǁDeterritorializationEngineǁdetect_rigidity__mutmut_10, 
        'xǁDeterritorializationEngineǁdetect_rigidity__mutmut_11': xǁDeterritorializationEngineǁdetect_rigidity__mutmut_11, 
        'xǁDeterritorializationEngineǁdetect_rigidity__mutmut_12': xǁDeterritorializationEngineǁdetect_rigidity__mutmut_12, 
        'xǁDeterritorializationEngineǁdetect_rigidity__mutmut_13': xǁDeterritorializationEngineǁdetect_rigidity__mutmut_13, 
        'xǁDeterritorializationEngineǁdetect_rigidity__mutmut_14': xǁDeterritorializationEngineǁdetect_rigidity__mutmut_14
    }
    
    def detect_rigidity(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDeterritorializationEngineǁdetect_rigidity__mutmut_orig"), object.__getattribute__(self, "xǁDeterritorializationEngineǁdetect_rigidity__mutmut_mutants"), args, kwargs, self)
        return result 
    
    detect_rigidity.__signature__ = _mutmut_signature(xǁDeterritorializationEngineǁdetect_rigidity__mutmut_orig)
    xǁDeterritorializationEngineǁdetect_rigidity__mutmut_orig.__name__ = 'xǁDeterritorializationEngineǁdetect_rigidity'

    def xǁDeterritorializationEngineǁpropose_lines_of_flight__mutmut_orig(
        self, min_severity: float = 0.5
    ) -> List[LineOfFlight]:
        """
        Propose lines of flight for detected rigidities.

        A "line of flight" is an escape route from rigidity - not destruction,
        but creation of new possibilities.

        Args:
            min_severity: Minimum severity to propose lines of flight (0.0 to 1.0)

        Returns:
            List of proposed lines of flight
        """
        for rigidity in self.rigidities:
            if rigidity.severity < min_severity:
                continue

            line_of_flight = self._create_line_of_flight(rigidity)
            if line_of_flight:
                self.lines_of_flight.append(line_of_flight)

        LOGGER.info(
            f"Proposed {len(self.lines_of_flight)} lines of flight "
            f"(min_severity={min_severity})"
        )
        return self.lines_of_flight

    def xǁDeterritorializationEngineǁpropose_lines_of_flight__mutmut_1(
        self, min_severity: float = 1.5
    ) -> List[LineOfFlight]:
        """
        Propose lines of flight for detected rigidities.

        A "line of flight" is an escape route from rigidity - not destruction,
        but creation of new possibilities.

        Args:
            min_severity: Minimum severity to propose lines of flight (0.0 to 1.0)

        Returns:
            List of proposed lines of flight
        """
        for rigidity in self.rigidities:
            if rigidity.severity < min_severity:
                continue

            line_of_flight = self._create_line_of_flight(rigidity)
            if line_of_flight:
                self.lines_of_flight.append(line_of_flight)

        LOGGER.info(
            f"Proposed {len(self.lines_of_flight)} lines of flight "
            f"(min_severity={min_severity})"
        )
        return self.lines_of_flight

    def xǁDeterritorializationEngineǁpropose_lines_of_flight__mutmut_2(
        self, min_severity: float = 0.5
    ) -> List[LineOfFlight]:
        """
        Propose lines of flight for detected rigidities.

        A "line of flight" is an escape route from rigidity - not destruction,
        but creation of new possibilities.

        Args:
            min_severity: Minimum severity to propose lines of flight (0.0 to 1.0)

        Returns:
            List of proposed lines of flight
        """
        for rigidity in self.rigidities:
            if rigidity.severity <= min_severity:
                continue

            line_of_flight = self._create_line_of_flight(rigidity)
            if line_of_flight:
                self.lines_of_flight.append(line_of_flight)

        LOGGER.info(
            f"Proposed {len(self.lines_of_flight)} lines of flight "
            f"(min_severity={min_severity})"
        )
        return self.lines_of_flight

    def xǁDeterritorializationEngineǁpropose_lines_of_flight__mutmut_3(
        self, min_severity: float = 0.5
    ) -> List[LineOfFlight]:
        """
        Propose lines of flight for detected rigidities.

        A "line of flight" is an escape route from rigidity - not destruction,
        but creation of new possibilities.

        Args:
            min_severity: Minimum severity to propose lines of flight (0.0 to 1.0)

        Returns:
            List of proposed lines of flight
        """
        for rigidity in self.rigidities:
            if rigidity.severity < min_severity:
                break

            line_of_flight = self._create_line_of_flight(rigidity)
            if line_of_flight:
                self.lines_of_flight.append(line_of_flight)

        LOGGER.info(
            f"Proposed {len(self.lines_of_flight)} lines of flight "
            f"(min_severity={min_severity})"
        )
        return self.lines_of_flight

    def xǁDeterritorializationEngineǁpropose_lines_of_flight__mutmut_4(
        self, min_severity: float = 0.5
    ) -> List[LineOfFlight]:
        """
        Propose lines of flight for detected rigidities.

        A "line of flight" is an escape route from rigidity - not destruction,
        but creation of new possibilities.

        Args:
            min_severity: Minimum severity to propose lines of flight (0.0 to 1.0)

        Returns:
            List of proposed lines of flight
        """
        for rigidity in self.rigidities:
            if rigidity.severity < min_severity:
                continue

            line_of_flight = None
            if line_of_flight:
                self.lines_of_flight.append(line_of_flight)

        LOGGER.info(
            f"Proposed {len(self.lines_of_flight)} lines of flight "
            f"(min_severity={min_severity})"
        )
        return self.lines_of_flight

    def xǁDeterritorializationEngineǁpropose_lines_of_flight__mutmut_5(
        self, min_severity: float = 0.5
    ) -> List[LineOfFlight]:
        """
        Propose lines of flight for detected rigidities.

        A "line of flight" is an escape route from rigidity - not destruction,
        but creation of new possibilities.

        Args:
            min_severity: Minimum severity to propose lines of flight (0.0 to 1.0)

        Returns:
            List of proposed lines of flight
        """
        for rigidity in self.rigidities:
            if rigidity.severity < min_severity:
                continue

            line_of_flight = self._create_line_of_flight(None)
            if line_of_flight:
                self.lines_of_flight.append(line_of_flight)

        LOGGER.info(
            f"Proposed {len(self.lines_of_flight)} lines of flight "
            f"(min_severity={min_severity})"
        )
        return self.lines_of_flight

    def xǁDeterritorializationEngineǁpropose_lines_of_flight__mutmut_6(
        self, min_severity: float = 0.5
    ) -> List[LineOfFlight]:
        """
        Propose lines of flight for detected rigidities.

        A "line of flight" is an escape route from rigidity - not destruction,
        but creation of new possibilities.

        Args:
            min_severity: Minimum severity to propose lines of flight (0.0 to 1.0)

        Returns:
            List of proposed lines of flight
        """
        for rigidity in self.rigidities:
            if rigidity.severity < min_severity:
                continue

            line_of_flight = self._create_line_of_flight(rigidity)
            if line_of_flight:
                self.lines_of_flight.append(None)

        LOGGER.info(
            f"Proposed {len(self.lines_of_flight)} lines of flight "
            f"(min_severity={min_severity})"
        )
        return self.lines_of_flight

    def xǁDeterritorializationEngineǁpropose_lines_of_flight__mutmut_7(
        self, min_severity: float = 0.5
    ) -> List[LineOfFlight]:
        """
        Propose lines of flight for detected rigidities.

        A "line of flight" is an escape route from rigidity - not destruction,
        but creation of new possibilities.

        Args:
            min_severity: Minimum severity to propose lines of flight (0.0 to 1.0)

        Returns:
            List of proposed lines of flight
        """
        for rigidity in self.rigidities:
            if rigidity.severity < min_severity:
                continue

            line_of_flight = self._create_line_of_flight(rigidity)
            if line_of_flight:
                self.lines_of_flight.append(line_of_flight)

        LOGGER.info(
            None
        )
        return self.lines_of_flight
    
    xǁDeterritorializationEngineǁpropose_lines_of_flight__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDeterritorializationEngineǁpropose_lines_of_flight__mutmut_1': xǁDeterritorializationEngineǁpropose_lines_of_flight__mutmut_1, 
        'xǁDeterritorializationEngineǁpropose_lines_of_flight__mutmut_2': xǁDeterritorializationEngineǁpropose_lines_of_flight__mutmut_2, 
        'xǁDeterritorializationEngineǁpropose_lines_of_flight__mutmut_3': xǁDeterritorializationEngineǁpropose_lines_of_flight__mutmut_3, 
        'xǁDeterritorializationEngineǁpropose_lines_of_flight__mutmut_4': xǁDeterritorializationEngineǁpropose_lines_of_flight__mutmut_4, 
        'xǁDeterritorializationEngineǁpropose_lines_of_flight__mutmut_5': xǁDeterritorializationEngineǁpropose_lines_of_flight__mutmut_5, 
        'xǁDeterritorializationEngineǁpropose_lines_of_flight__mutmut_6': xǁDeterritorializationEngineǁpropose_lines_of_flight__mutmut_6, 
        'xǁDeterritorializationEngineǁpropose_lines_of_flight__mutmut_7': xǁDeterritorializationEngineǁpropose_lines_of_flight__mutmut_7
    }
    
    def propose_lines_of_flight(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDeterritorializationEngineǁpropose_lines_of_flight__mutmut_orig"), object.__getattribute__(self, "xǁDeterritorializationEngineǁpropose_lines_of_flight__mutmut_mutants"), args, kwargs, self)
        return result 
    
    propose_lines_of_flight.__signature__ = _mutmut_signature(xǁDeterritorializationEngineǁpropose_lines_of_flight__mutmut_orig)
    xǁDeterritorializationEngineǁpropose_lines_of_flight__mutmut_orig.__name__ = 'xǁDeterritorializationEngineǁpropose_lines_of_flight'

    def xǁDeterritorializationEngineǁ_create_line_of_flight__mutmut_orig(self, rigidity: RigidityDetection) -> Optional[LineOfFlight]:
        """Create a line of flight for a specific rigidity."""
        strategies = {
            RigidityType.DEEP_NESTING: self._propose_flatten_nesting,
            RigidityType.LONG_METHOD: self._propose_extract_method,
            RigidityType.GOD_CLASS: self._propose_split_class,
            RigidityType.TIGHT_COUPLING: self._propose_decouple,
            RigidityType.HARDCODED_VALUES: self._propose_extract_constant,
            RigidityType.REPEATED_PATTERNS: self._propose_extract_function,
            RigidityType.OVERLY_COMPLEX: self._propose_simplify,
        }

        strategy = strategies.get(rigidity.rigidity_type)
        if strategy:
            return strategy(rigidity)

        return None

    def xǁDeterritorializationEngineǁ_create_line_of_flight__mutmut_1(self, rigidity: RigidityDetection) -> Optional[LineOfFlight]:
        """Create a line of flight for a specific rigidity."""
        strategies = None

        strategy = strategies.get(rigidity.rigidity_type)
        if strategy:
            return strategy(rigidity)

        return None

    def xǁDeterritorializationEngineǁ_create_line_of_flight__mutmut_2(self, rigidity: RigidityDetection) -> Optional[LineOfFlight]:
        """Create a line of flight for a specific rigidity."""
        strategies = {
            RigidityType.DEEP_NESTING: self._propose_flatten_nesting,
            RigidityType.LONG_METHOD: self._propose_extract_method,
            RigidityType.GOD_CLASS: self._propose_split_class,
            RigidityType.TIGHT_COUPLING: self._propose_decouple,
            RigidityType.HARDCODED_VALUES: self._propose_extract_constant,
            RigidityType.REPEATED_PATTERNS: self._propose_extract_function,
            RigidityType.OVERLY_COMPLEX: self._propose_simplify,
        }

        strategy = None
        if strategy:
            return strategy(rigidity)

        return None

    def xǁDeterritorializationEngineǁ_create_line_of_flight__mutmut_3(self, rigidity: RigidityDetection) -> Optional[LineOfFlight]:
        """Create a line of flight for a specific rigidity."""
        strategies = {
            RigidityType.DEEP_NESTING: self._propose_flatten_nesting,
            RigidityType.LONG_METHOD: self._propose_extract_method,
            RigidityType.GOD_CLASS: self._propose_split_class,
            RigidityType.TIGHT_COUPLING: self._propose_decouple,
            RigidityType.HARDCODED_VALUES: self._propose_extract_constant,
            RigidityType.REPEATED_PATTERNS: self._propose_extract_function,
            RigidityType.OVERLY_COMPLEX: self._propose_simplify,
        }

        strategy = strategies.get(None)
        if strategy:
            return strategy(rigidity)

        return None

    def xǁDeterritorializationEngineǁ_create_line_of_flight__mutmut_4(self, rigidity: RigidityDetection) -> Optional[LineOfFlight]:
        """Create a line of flight for a specific rigidity."""
        strategies = {
            RigidityType.DEEP_NESTING: self._propose_flatten_nesting,
            RigidityType.LONG_METHOD: self._propose_extract_method,
            RigidityType.GOD_CLASS: self._propose_split_class,
            RigidityType.TIGHT_COUPLING: self._propose_decouple,
            RigidityType.HARDCODED_VALUES: self._propose_extract_constant,
            RigidityType.REPEATED_PATTERNS: self._propose_extract_function,
            RigidityType.OVERLY_COMPLEX: self._propose_simplify,
        }

        strategy = strategies.get(rigidity.rigidity_type)
        if strategy:
            return strategy(None)

        return None
    
    xǁDeterritorializationEngineǁ_create_line_of_flight__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDeterritorializationEngineǁ_create_line_of_flight__mutmut_1': xǁDeterritorializationEngineǁ_create_line_of_flight__mutmut_1, 
        'xǁDeterritorializationEngineǁ_create_line_of_flight__mutmut_2': xǁDeterritorializationEngineǁ_create_line_of_flight__mutmut_2, 
        'xǁDeterritorializationEngineǁ_create_line_of_flight__mutmut_3': xǁDeterritorializationEngineǁ_create_line_of_flight__mutmut_3, 
        'xǁDeterritorializationEngineǁ_create_line_of_flight__mutmut_4': xǁDeterritorializationEngineǁ_create_line_of_flight__mutmut_4
    }
    
    def _create_line_of_flight(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDeterritorializationEngineǁ_create_line_of_flight__mutmut_orig"), object.__getattribute__(self, "xǁDeterritorializationEngineǁ_create_line_of_flight__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _create_line_of_flight.__signature__ = _mutmut_signature(xǁDeterritorializationEngineǁ_create_line_of_flight__mutmut_orig)
    xǁDeterritorializationEngineǁ_create_line_of_flight__mutmut_orig.__name__ = 'xǁDeterritorializationEngineǁ_create_line_of_flight'

    def xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_orig(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose flattening deep nesting."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Flatten nesting by extracting nested blocks into separate methods. "
                "Use early returns to reduce indentation levels."
            ),
            expected_outcome="Reduced nesting depth, improved readability",
            innovation_potential=0.6,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_1(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose flattening deep nesting."""
        return LineOfFlight(
            rigidity=None,
            proposed_action=(
                "Flatten nesting by extracting nested blocks into separate methods. "
                "Use early returns to reduce indentation levels."
            ),
            expected_outcome="Reduced nesting depth, improved readability",
            innovation_potential=0.6,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_2(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose flattening deep nesting."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=None,
            expected_outcome="Reduced nesting depth, improved readability",
            innovation_potential=0.6,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_3(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose flattening deep nesting."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Flatten nesting by extracting nested blocks into separate methods. "
                "Use early returns to reduce indentation levels."
            ),
            expected_outcome=None,
            innovation_potential=0.6,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_4(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose flattening deep nesting."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Flatten nesting by extracting nested blocks into separate methods. "
                "Use early returns to reduce indentation levels."
            ),
            expected_outcome="Reduced nesting depth, improved readability",
            innovation_potential=None,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_5(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose flattening deep nesting."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Flatten nesting by extracting nested blocks into separate methods. "
                "Use early returns to reduce indentation levels."
            ),
            expected_outcome="Reduced nesting depth, improved readability",
            innovation_potential=0.6,
            risk_level=None,
        )

    def xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_6(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose flattening deep nesting."""
        return LineOfFlight(
            proposed_action=(
                "Flatten nesting by extracting nested blocks into separate methods. "
                "Use early returns to reduce indentation levels."
            ),
            expected_outcome="Reduced nesting depth, improved readability",
            innovation_potential=0.6,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_7(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose flattening deep nesting."""
        return LineOfFlight(
            rigidity=rigidity,
            expected_outcome="Reduced nesting depth, improved readability",
            innovation_potential=0.6,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_8(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose flattening deep nesting."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Flatten nesting by extracting nested blocks into separate methods. "
                "Use early returns to reduce indentation levels."
            ),
            innovation_potential=0.6,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_9(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose flattening deep nesting."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Flatten nesting by extracting nested blocks into separate methods. "
                "Use early returns to reduce indentation levels."
            ),
            expected_outcome="Reduced nesting depth, improved readability",
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_10(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose flattening deep nesting."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Flatten nesting by extracting nested blocks into separate methods. "
                "Use early returns to reduce indentation levels."
            ),
            expected_outcome="Reduced nesting depth, improved readability",
            innovation_potential=0.6,
            )

    def xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_11(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose flattening deep nesting."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "XXFlatten nesting by extracting nested blocks into separate methods. XX"
                "Use early returns to reduce indentation levels."
            ),
            expected_outcome="Reduced nesting depth, improved readability",
            innovation_potential=0.6,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_12(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose flattening deep nesting."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "flatten nesting by extracting nested blocks into separate methods. "
                "Use early returns to reduce indentation levels."
            ),
            expected_outcome="Reduced nesting depth, improved readability",
            innovation_potential=0.6,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_13(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose flattening deep nesting."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "FLATTEN NESTING BY EXTRACTING NESTED BLOCKS INTO SEPARATE METHODS. "
                "Use early returns to reduce indentation levels."
            ),
            expected_outcome="Reduced nesting depth, improved readability",
            innovation_potential=0.6,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_14(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose flattening deep nesting."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Flatten nesting by extracting nested blocks into separate methods. "
                "XXUse early returns to reduce indentation levels.XX"
            ),
            expected_outcome="Reduced nesting depth, improved readability",
            innovation_potential=0.6,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_15(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose flattening deep nesting."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Flatten nesting by extracting nested blocks into separate methods. "
                "use early returns to reduce indentation levels."
            ),
            expected_outcome="Reduced nesting depth, improved readability",
            innovation_potential=0.6,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_16(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose flattening deep nesting."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Flatten nesting by extracting nested blocks into separate methods. "
                "USE EARLY RETURNS TO REDUCE INDENTATION LEVELS."
            ),
            expected_outcome="Reduced nesting depth, improved readability",
            innovation_potential=0.6,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_17(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose flattening deep nesting."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Flatten nesting by extracting nested blocks into separate methods. "
                "Use early returns to reduce indentation levels."
            ),
            expected_outcome="XXReduced nesting depth, improved readabilityXX",
            innovation_potential=0.6,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_18(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose flattening deep nesting."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Flatten nesting by extracting nested blocks into separate methods. "
                "Use early returns to reduce indentation levels."
            ),
            expected_outcome="reduced nesting depth, improved readability",
            innovation_potential=0.6,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_19(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose flattening deep nesting."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Flatten nesting by extracting nested blocks into separate methods. "
                "Use early returns to reduce indentation levels."
            ),
            expected_outcome="REDUCED NESTING DEPTH, IMPROVED READABILITY",
            innovation_potential=0.6,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_20(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose flattening deep nesting."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Flatten nesting by extracting nested blocks into separate methods. "
                "Use early returns to reduce indentation levels."
            ),
            expected_outcome="Reduced nesting depth, improved readability",
            innovation_potential=1.6,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_21(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose flattening deep nesting."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Flatten nesting by extracting nested blocks into separate methods. "
                "Use early returns to reduce indentation levels."
            ),
            expected_outcome="Reduced nesting depth, improved readability",
            innovation_potential=0.6,
            risk_level=1.2,
        )
    
    xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_1': xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_1, 
        'xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_2': xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_2, 
        'xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_3': xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_3, 
        'xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_4': xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_4, 
        'xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_5': xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_5, 
        'xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_6': xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_6, 
        'xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_7': xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_7, 
        'xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_8': xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_8, 
        'xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_9': xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_9, 
        'xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_10': xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_10, 
        'xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_11': xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_11, 
        'xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_12': xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_12, 
        'xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_13': xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_13, 
        'xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_14': xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_14, 
        'xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_15': xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_15, 
        'xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_16': xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_16, 
        'xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_17': xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_17, 
        'xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_18': xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_18, 
        'xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_19': xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_19, 
        'xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_20': xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_20, 
        'xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_21': xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_21
    }
    
    def _propose_flatten_nesting(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_orig"), object.__getattribute__(self, "xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _propose_flatten_nesting.__signature__ = _mutmut_signature(xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_orig)
    xǁDeterritorializationEngineǁ_propose_flatten_nesting__mutmut_orig.__name__ = 'xǁDeterritorializationEngineǁ_propose_flatten_nesting'

    def xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_orig(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting long method into smaller methods."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract logical blocks into separate methods with clear names. "
                "Follow Single Responsibility Principle."
            ),
            expected_outcome="Smaller, focused methods that are easier to test",
            innovation_potential=0.7,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_1(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting long method into smaller methods."""
        return LineOfFlight(
            rigidity=None,
            proposed_action=(
                "Extract logical blocks into separate methods with clear names. "
                "Follow Single Responsibility Principle."
            ),
            expected_outcome="Smaller, focused methods that are easier to test",
            innovation_potential=0.7,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_2(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting long method into smaller methods."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=None,
            expected_outcome="Smaller, focused methods that are easier to test",
            innovation_potential=0.7,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_3(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting long method into smaller methods."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract logical blocks into separate methods with clear names. "
                "Follow Single Responsibility Principle."
            ),
            expected_outcome=None,
            innovation_potential=0.7,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_4(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting long method into smaller methods."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract logical blocks into separate methods with clear names. "
                "Follow Single Responsibility Principle."
            ),
            expected_outcome="Smaller, focused methods that are easier to test",
            innovation_potential=None,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_5(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting long method into smaller methods."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract logical blocks into separate methods with clear names. "
                "Follow Single Responsibility Principle."
            ),
            expected_outcome="Smaller, focused methods that are easier to test",
            innovation_potential=0.7,
            risk_level=None,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_6(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting long method into smaller methods."""
        return LineOfFlight(
            proposed_action=(
                "Extract logical blocks into separate methods with clear names. "
                "Follow Single Responsibility Principle."
            ),
            expected_outcome="Smaller, focused methods that are easier to test",
            innovation_potential=0.7,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_7(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting long method into smaller methods."""
        return LineOfFlight(
            rigidity=rigidity,
            expected_outcome="Smaller, focused methods that are easier to test",
            innovation_potential=0.7,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_8(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting long method into smaller methods."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract logical blocks into separate methods with clear names. "
                "Follow Single Responsibility Principle."
            ),
            innovation_potential=0.7,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_9(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting long method into smaller methods."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract logical blocks into separate methods with clear names. "
                "Follow Single Responsibility Principle."
            ),
            expected_outcome="Smaller, focused methods that are easier to test",
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_10(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting long method into smaller methods."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract logical blocks into separate methods with clear names. "
                "Follow Single Responsibility Principle."
            ),
            expected_outcome="Smaller, focused methods that are easier to test",
            innovation_potential=0.7,
            )

    def xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_11(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting long method into smaller methods."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "XXExtract logical blocks into separate methods with clear names. XX"
                "Follow Single Responsibility Principle."
            ),
            expected_outcome="Smaller, focused methods that are easier to test",
            innovation_potential=0.7,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_12(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting long method into smaller methods."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "extract logical blocks into separate methods with clear names. "
                "Follow Single Responsibility Principle."
            ),
            expected_outcome="Smaller, focused methods that are easier to test",
            innovation_potential=0.7,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_13(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting long method into smaller methods."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "EXTRACT LOGICAL BLOCKS INTO SEPARATE METHODS WITH CLEAR NAMES. "
                "Follow Single Responsibility Principle."
            ),
            expected_outcome="Smaller, focused methods that are easier to test",
            innovation_potential=0.7,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_14(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting long method into smaller methods."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract logical blocks into separate methods with clear names. "
                "XXFollow Single Responsibility Principle.XX"
            ),
            expected_outcome="Smaller, focused methods that are easier to test",
            innovation_potential=0.7,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_15(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting long method into smaller methods."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract logical blocks into separate methods with clear names. "
                "follow single responsibility principle."
            ),
            expected_outcome="Smaller, focused methods that are easier to test",
            innovation_potential=0.7,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_16(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting long method into smaller methods."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract logical blocks into separate methods with clear names. "
                "FOLLOW SINGLE RESPONSIBILITY PRINCIPLE."
            ),
            expected_outcome="Smaller, focused methods that are easier to test",
            innovation_potential=0.7,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_17(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting long method into smaller methods."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract logical blocks into separate methods with clear names. "
                "Follow Single Responsibility Principle."
            ),
            expected_outcome="XXSmaller, focused methods that are easier to testXX",
            innovation_potential=0.7,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_18(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting long method into smaller methods."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract logical blocks into separate methods with clear names. "
                "Follow Single Responsibility Principle."
            ),
            expected_outcome="smaller, focused methods that are easier to test",
            innovation_potential=0.7,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_19(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting long method into smaller methods."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract logical blocks into separate methods with clear names. "
                "Follow Single Responsibility Principle."
            ),
            expected_outcome="SMALLER, FOCUSED METHODS THAT ARE EASIER TO TEST",
            innovation_potential=0.7,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_20(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting long method into smaller methods."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract logical blocks into separate methods with clear names. "
                "Follow Single Responsibility Principle."
            ),
            expected_outcome="Smaller, focused methods that are easier to test",
            innovation_potential=1.7,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_21(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting long method into smaller methods."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract logical blocks into separate methods with clear names. "
                "Follow Single Responsibility Principle."
            ),
            expected_outcome="Smaller, focused methods that are easier to test",
            innovation_potential=0.7,
            risk_level=1.3,
        )
    
    xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_1': xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_1, 
        'xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_2': xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_2, 
        'xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_3': xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_3, 
        'xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_4': xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_4, 
        'xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_5': xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_5, 
        'xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_6': xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_6, 
        'xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_7': xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_7, 
        'xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_8': xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_8, 
        'xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_9': xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_9, 
        'xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_10': xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_10, 
        'xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_11': xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_11, 
        'xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_12': xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_12, 
        'xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_13': xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_13, 
        'xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_14': xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_14, 
        'xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_15': xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_15, 
        'xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_16': xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_16, 
        'xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_17': xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_17, 
        'xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_18': xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_18, 
        'xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_19': xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_19, 
        'xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_20': xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_20, 
        'xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_21': xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_21
    }
    
    def _propose_extract_method(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_orig"), object.__getattribute__(self, "xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _propose_extract_method.__signature__ = _mutmut_signature(xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_orig)
    xǁDeterritorializationEngineǁ_propose_extract_method__mutmut_orig.__name__ = 'xǁDeterritorializationEngineǁ_propose_extract_method'

    def xǁDeterritorializationEngineǁ_propose_split_class__mutmut_orig(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose splitting a god class."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Identify distinct responsibilities and split into separate classes. "
                "Consider using composition or strategy pattern."
            ),
            expected_outcome="Cohesive classes with clear responsibilities",
            innovation_potential=0.8,
            risk_level=0.6,
        )

    def xǁDeterritorializationEngineǁ_propose_split_class__mutmut_1(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose splitting a god class."""
        return LineOfFlight(
            rigidity=None,
            proposed_action=(
                "Identify distinct responsibilities and split into separate classes. "
                "Consider using composition or strategy pattern."
            ),
            expected_outcome="Cohesive classes with clear responsibilities",
            innovation_potential=0.8,
            risk_level=0.6,
        )

    def xǁDeterritorializationEngineǁ_propose_split_class__mutmut_2(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose splitting a god class."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=None,
            expected_outcome="Cohesive classes with clear responsibilities",
            innovation_potential=0.8,
            risk_level=0.6,
        )

    def xǁDeterritorializationEngineǁ_propose_split_class__mutmut_3(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose splitting a god class."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Identify distinct responsibilities and split into separate classes. "
                "Consider using composition or strategy pattern."
            ),
            expected_outcome=None,
            innovation_potential=0.8,
            risk_level=0.6,
        )

    def xǁDeterritorializationEngineǁ_propose_split_class__mutmut_4(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose splitting a god class."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Identify distinct responsibilities and split into separate classes. "
                "Consider using composition or strategy pattern."
            ),
            expected_outcome="Cohesive classes with clear responsibilities",
            innovation_potential=None,
            risk_level=0.6,
        )

    def xǁDeterritorializationEngineǁ_propose_split_class__mutmut_5(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose splitting a god class."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Identify distinct responsibilities and split into separate classes. "
                "Consider using composition or strategy pattern."
            ),
            expected_outcome="Cohesive classes with clear responsibilities",
            innovation_potential=0.8,
            risk_level=None,
        )

    def xǁDeterritorializationEngineǁ_propose_split_class__mutmut_6(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose splitting a god class."""
        return LineOfFlight(
            proposed_action=(
                "Identify distinct responsibilities and split into separate classes. "
                "Consider using composition or strategy pattern."
            ),
            expected_outcome="Cohesive classes with clear responsibilities",
            innovation_potential=0.8,
            risk_level=0.6,
        )

    def xǁDeterritorializationEngineǁ_propose_split_class__mutmut_7(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose splitting a god class."""
        return LineOfFlight(
            rigidity=rigidity,
            expected_outcome="Cohesive classes with clear responsibilities",
            innovation_potential=0.8,
            risk_level=0.6,
        )

    def xǁDeterritorializationEngineǁ_propose_split_class__mutmut_8(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose splitting a god class."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Identify distinct responsibilities and split into separate classes. "
                "Consider using composition or strategy pattern."
            ),
            innovation_potential=0.8,
            risk_level=0.6,
        )

    def xǁDeterritorializationEngineǁ_propose_split_class__mutmut_9(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose splitting a god class."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Identify distinct responsibilities and split into separate classes. "
                "Consider using composition or strategy pattern."
            ),
            expected_outcome="Cohesive classes with clear responsibilities",
            risk_level=0.6,
        )

    def xǁDeterritorializationEngineǁ_propose_split_class__mutmut_10(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose splitting a god class."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Identify distinct responsibilities and split into separate classes. "
                "Consider using composition or strategy pattern."
            ),
            expected_outcome="Cohesive classes with clear responsibilities",
            innovation_potential=0.8,
            )

    def xǁDeterritorializationEngineǁ_propose_split_class__mutmut_11(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose splitting a god class."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "XXIdentify distinct responsibilities and split into separate classes. XX"
                "Consider using composition or strategy pattern."
            ),
            expected_outcome="Cohesive classes with clear responsibilities",
            innovation_potential=0.8,
            risk_level=0.6,
        )

    def xǁDeterritorializationEngineǁ_propose_split_class__mutmut_12(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose splitting a god class."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "identify distinct responsibilities and split into separate classes. "
                "Consider using composition or strategy pattern."
            ),
            expected_outcome="Cohesive classes with clear responsibilities",
            innovation_potential=0.8,
            risk_level=0.6,
        )

    def xǁDeterritorializationEngineǁ_propose_split_class__mutmut_13(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose splitting a god class."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "IDENTIFY DISTINCT RESPONSIBILITIES AND SPLIT INTO SEPARATE CLASSES. "
                "Consider using composition or strategy pattern."
            ),
            expected_outcome="Cohesive classes with clear responsibilities",
            innovation_potential=0.8,
            risk_level=0.6,
        )

    def xǁDeterritorializationEngineǁ_propose_split_class__mutmut_14(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose splitting a god class."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Identify distinct responsibilities and split into separate classes. "
                "XXConsider using composition or strategy pattern.XX"
            ),
            expected_outcome="Cohesive classes with clear responsibilities",
            innovation_potential=0.8,
            risk_level=0.6,
        )

    def xǁDeterritorializationEngineǁ_propose_split_class__mutmut_15(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose splitting a god class."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Identify distinct responsibilities and split into separate classes. "
                "consider using composition or strategy pattern."
            ),
            expected_outcome="Cohesive classes with clear responsibilities",
            innovation_potential=0.8,
            risk_level=0.6,
        )

    def xǁDeterritorializationEngineǁ_propose_split_class__mutmut_16(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose splitting a god class."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Identify distinct responsibilities and split into separate classes. "
                "CONSIDER USING COMPOSITION OR STRATEGY PATTERN."
            ),
            expected_outcome="Cohesive classes with clear responsibilities",
            innovation_potential=0.8,
            risk_level=0.6,
        )

    def xǁDeterritorializationEngineǁ_propose_split_class__mutmut_17(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose splitting a god class."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Identify distinct responsibilities and split into separate classes. "
                "Consider using composition or strategy pattern."
            ),
            expected_outcome="XXCohesive classes with clear responsibilitiesXX",
            innovation_potential=0.8,
            risk_level=0.6,
        )

    def xǁDeterritorializationEngineǁ_propose_split_class__mutmut_18(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose splitting a god class."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Identify distinct responsibilities and split into separate classes. "
                "Consider using composition or strategy pattern."
            ),
            expected_outcome="cohesive classes with clear responsibilities",
            innovation_potential=0.8,
            risk_level=0.6,
        )

    def xǁDeterritorializationEngineǁ_propose_split_class__mutmut_19(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose splitting a god class."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Identify distinct responsibilities and split into separate classes. "
                "Consider using composition or strategy pattern."
            ),
            expected_outcome="COHESIVE CLASSES WITH CLEAR RESPONSIBILITIES",
            innovation_potential=0.8,
            risk_level=0.6,
        )

    def xǁDeterritorializationEngineǁ_propose_split_class__mutmut_20(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose splitting a god class."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Identify distinct responsibilities and split into separate classes. "
                "Consider using composition or strategy pattern."
            ),
            expected_outcome="Cohesive classes with clear responsibilities",
            innovation_potential=1.8,
            risk_level=0.6,
        )

    def xǁDeterritorializationEngineǁ_propose_split_class__mutmut_21(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose splitting a god class."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Identify distinct responsibilities and split into separate classes. "
                "Consider using composition or strategy pattern."
            ),
            expected_outcome="Cohesive classes with clear responsibilities",
            innovation_potential=0.8,
            risk_level=1.6,
        )
    
    xǁDeterritorializationEngineǁ_propose_split_class__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDeterritorializationEngineǁ_propose_split_class__mutmut_1': xǁDeterritorializationEngineǁ_propose_split_class__mutmut_1, 
        'xǁDeterritorializationEngineǁ_propose_split_class__mutmut_2': xǁDeterritorializationEngineǁ_propose_split_class__mutmut_2, 
        'xǁDeterritorializationEngineǁ_propose_split_class__mutmut_3': xǁDeterritorializationEngineǁ_propose_split_class__mutmut_3, 
        'xǁDeterritorializationEngineǁ_propose_split_class__mutmut_4': xǁDeterritorializationEngineǁ_propose_split_class__mutmut_4, 
        'xǁDeterritorializationEngineǁ_propose_split_class__mutmut_5': xǁDeterritorializationEngineǁ_propose_split_class__mutmut_5, 
        'xǁDeterritorializationEngineǁ_propose_split_class__mutmut_6': xǁDeterritorializationEngineǁ_propose_split_class__mutmut_6, 
        'xǁDeterritorializationEngineǁ_propose_split_class__mutmut_7': xǁDeterritorializationEngineǁ_propose_split_class__mutmut_7, 
        'xǁDeterritorializationEngineǁ_propose_split_class__mutmut_8': xǁDeterritorializationEngineǁ_propose_split_class__mutmut_8, 
        'xǁDeterritorializationEngineǁ_propose_split_class__mutmut_9': xǁDeterritorializationEngineǁ_propose_split_class__mutmut_9, 
        'xǁDeterritorializationEngineǁ_propose_split_class__mutmut_10': xǁDeterritorializationEngineǁ_propose_split_class__mutmut_10, 
        'xǁDeterritorializationEngineǁ_propose_split_class__mutmut_11': xǁDeterritorializationEngineǁ_propose_split_class__mutmut_11, 
        'xǁDeterritorializationEngineǁ_propose_split_class__mutmut_12': xǁDeterritorializationEngineǁ_propose_split_class__mutmut_12, 
        'xǁDeterritorializationEngineǁ_propose_split_class__mutmut_13': xǁDeterritorializationEngineǁ_propose_split_class__mutmut_13, 
        'xǁDeterritorializationEngineǁ_propose_split_class__mutmut_14': xǁDeterritorializationEngineǁ_propose_split_class__mutmut_14, 
        'xǁDeterritorializationEngineǁ_propose_split_class__mutmut_15': xǁDeterritorializationEngineǁ_propose_split_class__mutmut_15, 
        'xǁDeterritorializationEngineǁ_propose_split_class__mutmut_16': xǁDeterritorializationEngineǁ_propose_split_class__mutmut_16, 
        'xǁDeterritorializationEngineǁ_propose_split_class__mutmut_17': xǁDeterritorializationEngineǁ_propose_split_class__mutmut_17, 
        'xǁDeterritorializationEngineǁ_propose_split_class__mutmut_18': xǁDeterritorializationEngineǁ_propose_split_class__mutmut_18, 
        'xǁDeterritorializationEngineǁ_propose_split_class__mutmut_19': xǁDeterritorializationEngineǁ_propose_split_class__mutmut_19, 
        'xǁDeterritorializationEngineǁ_propose_split_class__mutmut_20': xǁDeterritorializationEngineǁ_propose_split_class__mutmut_20, 
        'xǁDeterritorializationEngineǁ_propose_split_class__mutmut_21': xǁDeterritorializationEngineǁ_propose_split_class__mutmut_21
    }
    
    def _propose_split_class(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDeterritorializationEngineǁ_propose_split_class__mutmut_orig"), object.__getattribute__(self, "xǁDeterritorializationEngineǁ_propose_split_class__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _propose_split_class.__signature__ = _mutmut_signature(xǁDeterritorializationEngineǁ_propose_split_class__mutmut_orig)
    xǁDeterritorializationEngineǁ_propose_split_class__mutmut_orig.__name__ = 'xǁDeterritorializationEngineǁ_propose_split_class'

    def xǁDeterritorializationEngineǁ_propose_decouple__mutmut_orig(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose decoupling tightly coupled code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Introduce interfaces or abstract base classes. "
                "Use dependency injection to reduce coupling."
            ),
            expected_outcome="Loosely coupled modules that are easier to test and maintain",
            innovation_potential=0.7,
            risk_level=0.5,
        )

    def xǁDeterritorializationEngineǁ_propose_decouple__mutmut_1(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose decoupling tightly coupled code."""
        return LineOfFlight(
            rigidity=None,
            proposed_action=(
                "Introduce interfaces or abstract base classes. "
                "Use dependency injection to reduce coupling."
            ),
            expected_outcome="Loosely coupled modules that are easier to test and maintain",
            innovation_potential=0.7,
            risk_level=0.5,
        )

    def xǁDeterritorializationEngineǁ_propose_decouple__mutmut_2(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose decoupling tightly coupled code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=None,
            expected_outcome="Loosely coupled modules that are easier to test and maintain",
            innovation_potential=0.7,
            risk_level=0.5,
        )

    def xǁDeterritorializationEngineǁ_propose_decouple__mutmut_3(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose decoupling tightly coupled code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Introduce interfaces or abstract base classes. "
                "Use dependency injection to reduce coupling."
            ),
            expected_outcome=None,
            innovation_potential=0.7,
            risk_level=0.5,
        )

    def xǁDeterritorializationEngineǁ_propose_decouple__mutmut_4(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose decoupling tightly coupled code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Introduce interfaces or abstract base classes. "
                "Use dependency injection to reduce coupling."
            ),
            expected_outcome="Loosely coupled modules that are easier to test and maintain",
            innovation_potential=None,
            risk_level=0.5,
        )

    def xǁDeterritorializationEngineǁ_propose_decouple__mutmut_5(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose decoupling tightly coupled code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Introduce interfaces or abstract base classes. "
                "Use dependency injection to reduce coupling."
            ),
            expected_outcome="Loosely coupled modules that are easier to test and maintain",
            innovation_potential=0.7,
            risk_level=None,
        )

    def xǁDeterritorializationEngineǁ_propose_decouple__mutmut_6(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose decoupling tightly coupled code."""
        return LineOfFlight(
            proposed_action=(
                "Introduce interfaces or abstract base classes. "
                "Use dependency injection to reduce coupling."
            ),
            expected_outcome="Loosely coupled modules that are easier to test and maintain",
            innovation_potential=0.7,
            risk_level=0.5,
        )

    def xǁDeterritorializationEngineǁ_propose_decouple__mutmut_7(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose decoupling tightly coupled code."""
        return LineOfFlight(
            rigidity=rigidity,
            expected_outcome="Loosely coupled modules that are easier to test and maintain",
            innovation_potential=0.7,
            risk_level=0.5,
        )

    def xǁDeterritorializationEngineǁ_propose_decouple__mutmut_8(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose decoupling tightly coupled code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Introduce interfaces or abstract base classes. "
                "Use dependency injection to reduce coupling."
            ),
            innovation_potential=0.7,
            risk_level=0.5,
        )

    def xǁDeterritorializationEngineǁ_propose_decouple__mutmut_9(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose decoupling tightly coupled code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Introduce interfaces or abstract base classes. "
                "Use dependency injection to reduce coupling."
            ),
            expected_outcome="Loosely coupled modules that are easier to test and maintain",
            risk_level=0.5,
        )

    def xǁDeterritorializationEngineǁ_propose_decouple__mutmut_10(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose decoupling tightly coupled code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Introduce interfaces or abstract base classes. "
                "Use dependency injection to reduce coupling."
            ),
            expected_outcome="Loosely coupled modules that are easier to test and maintain",
            innovation_potential=0.7,
            )

    def xǁDeterritorializationEngineǁ_propose_decouple__mutmut_11(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose decoupling tightly coupled code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "XXIntroduce interfaces or abstract base classes. XX"
                "Use dependency injection to reduce coupling."
            ),
            expected_outcome="Loosely coupled modules that are easier to test and maintain",
            innovation_potential=0.7,
            risk_level=0.5,
        )

    def xǁDeterritorializationEngineǁ_propose_decouple__mutmut_12(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose decoupling tightly coupled code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "introduce interfaces or abstract base classes. "
                "Use dependency injection to reduce coupling."
            ),
            expected_outcome="Loosely coupled modules that are easier to test and maintain",
            innovation_potential=0.7,
            risk_level=0.5,
        )

    def xǁDeterritorializationEngineǁ_propose_decouple__mutmut_13(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose decoupling tightly coupled code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "INTRODUCE INTERFACES OR ABSTRACT BASE CLASSES. "
                "Use dependency injection to reduce coupling."
            ),
            expected_outcome="Loosely coupled modules that are easier to test and maintain",
            innovation_potential=0.7,
            risk_level=0.5,
        )

    def xǁDeterritorializationEngineǁ_propose_decouple__mutmut_14(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose decoupling tightly coupled code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Introduce interfaces or abstract base classes. "
                "XXUse dependency injection to reduce coupling.XX"
            ),
            expected_outcome="Loosely coupled modules that are easier to test and maintain",
            innovation_potential=0.7,
            risk_level=0.5,
        )

    def xǁDeterritorializationEngineǁ_propose_decouple__mutmut_15(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose decoupling tightly coupled code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Introduce interfaces or abstract base classes. "
                "use dependency injection to reduce coupling."
            ),
            expected_outcome="Loosely coupled modules that are easier to test and maintain",
            innovation_potential=0.7,
            risk_level=0.5,
        )

    def xǁDeterritorializationEngineǁ_propose_decouple__mutmut_16(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose decoupling tightly coupled code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Introduce interfaces or abstract base classes. "
                "USE DEPENDENCY INJECTION TO REDUCE COUPLING."
            ),
            expected_outcome="Loosely coupled modules that are easier to test and maintain",
            innovation_potential=0.7,
            risk_level=0.5,
        )

    def xǁDeterritorializationEngineǁ_propose_decouple__mutmut_17(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose decoupling tightly coupled code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Introduce interfaces or abstract base classes. "
                "Use dependency injection to reduce coupling."
            ),
            expected_outcome="XXLoosely coupled modules that are easier to test and maintainXX",
            innovation_potential=0.7,
            risk_level=0.5,
        )

    def xǁDeterritorializationEngineǁ_propose_decouple__mutmut_18(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose decoupling tightly coupled code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Introduce interfaces or abstract base classes. "
                "Use dependency injection to reduce coupling."
            ),
            expected_outcome="loosely coupled modules that are easier to test and maintain",
            innovation_potential=0.7,
            risk_level=0.5,
        )

    def xǁDeterritorializationEngineǁ_propose_decouple__mutmut_19(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose decoupling tightly coupled code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Introduce interfaces or abstract base classes. "
                "Use dependency injection to reduce coupling."
            ),
            expected_outcome="LOOSELY COUPLED MODULES THAT ARE EASIER TO TEST AND MAINTAIN",
            innovation_potential=0.7,
            risk_level=0.5,
        )

    def xǁDeterritorializationEngineǁ_propose_decouple__mutmut_20(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose decoupling tightly coupled code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Introduce interfaces or abstract base classes. "
                "Use dependency injection to reduce coupling."
            ),
            expected_outcome="Loosely coupled modules that are easier to test and maintain",
            innovation_potential=1.7,
            risk_level=0.5,
        )

    def xǁDeterritorializationEngineǁ_propose_decouple__mutmut_21(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose decoupling tightly coupled code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Introduce interfaces or abstract base classes. "
                "Use dependency injection to reduce coupling."
            ),
            expected_outcome="Loosely coupled modules that are easier to test and maintain",
            innovation_potential=0.7,
            risk_level=1.5,
        )
    
    xǁDeterritorializationEngineǁ_propose_decouple__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDeterritorializationEngineǁ_propose_decouple__mutmut_1': xǁDeterritorializationEngineǁ_propose_decouple__mutmut_1, 
        'xǁDeterritorializationEngineǁ_propose_decouple__mutmut_2': xǁDeterritorializationEngineǁ_propose_decouple__mutmut_2, 
        'xǁDeterritorializationEngineǁ_propose_decouple__mutmut_3': xǁDeterritorializationEngineǁ_propose_decouple__mutmut_3, 
        'xǁDeterritorializationEngineǁ_propose_decouple__mutmut_4': xǁDeterritorializationEngineǁ_propose_decouple__mutmut_4, 
        'xǁDeterritorializationEngineǁ_propose_decouple__mutmut_5': xǁDeterritorializationEngineǁ_propose_decouple__mutmut_5, 
        'xǁDeterritorializationEngineǁ_propose_decouple__mutmut_6': xǁDeterritorializationEngineǁ_propose_decouple__mutmut_6, 
        'xǁDeterritorializationEngineǁ_propose_decouple__mutmut_7': xǁDeterritorializationEngineǁ_propose_decouple__mutmut_7, 
        'xǁDeterritorializationEngineǁ_propose_decouple__mutmut_8': xǁDeterritorializationEngineǁ_propose_decouple__mutmut_8, 
        'xǁDeterritorializationEngineǁ_propose_decouple__mutmut_9': xǁDeterritorializationEngineǁ_propose_decouple__mutmut_9, 
        'xǁDeterritorializationEngineǁ_propose_decouple__mutmut_10': xǁDeterritorializationEngineǁ_propose_decouple__mutmut_10, 
        'xǁDeterritorializationEngineǁ_propose_decouple__mutmut_11': xǁDeterritorializationEngineǁ_propose_decouple__mutmut_11, 
        'xǁDeterritorializationEngineǁ_propose_decouple__mutmut_12': xǁDeterritorializationEngineǁ_propose_decouple__mutmut_12, 
        'xǁDeterritorializationEngineǁ_propose_decouple__mutmut_13': xǁDeterritorializationEngineǁ_propose_decouple__mutmut_13, 
        'xǁDeterritorializationEngineǁ_propose_decouple__mutmut_14': xǁDeterritorializationEngineǁ_propose_decouple__mutmut_14, 
        'xǁDeterritorializationEngineǁ_propose_decouple__mutmut_15': xǁDeterritorializationEngineǁ_propose_decouple__mutmut_15, 
        'xǁDeterritorializationEngineǁ_propose_decouple__mutmut_16': xǁDeterritorializationEngineǁ_propose_decouple__mutmut_16, 
        'xǁDeterritorializationEngineǁ_propose_decouple__mutmut_17': xǁDeterritorializationEngineǁ_propose_decouple__mutmut_17, 
        'xǁDeterritorializationEngineǁ_propose_decouple__mutmut_18': xǁDeterritorializationEngineǁ_propose_decouple__mutmut_18, 
        'xǁDeterritorializationEngineǁ_propose_decouple__mutmut_19': xǁDeterritorializationEngineǁ_propose_decouple__mutmut_19, 
        'xǁDeterritorializationEngineǁ_propose_decouple__mutmut_20': xǁDeterritorializationEngineǁ_propose_decouple__mutmut_20, 
        'xǁDeterritorializationEngineǁ_propose_decouple__mutmut_21': xǁDeterritorializationEngineǁ_propose_decouple__mutmut_21
    }
    
    def _propose_decouple(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDeterritorializationEngineǁ_propose_decouple__mutmut_orig"), object.__getattribute__(self, "xǁDeterritorializationEngineǁ_propose_decouple__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _propose_decouple.__signature__ = _mutmut_signature(xǁDeterritorializationEngineǁ_propose_decouple__mutmut_orig)
    xǁDeterritorializationEngineǁ_propose_decouple__mutmut_orig.__name__ = 'xǁDeterritorializationEngineǁ_propose_decouple'

    def xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_orig(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting hardcoded values."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract magic numbers and strings into named constants. "
                "Consider using configuration files for values that may change."
            ),
            expected_outcome="Self-documenting code with maintainable configuration",
            innovation_potential=0.5,
            risk_level=0.1,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_1(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting hardcoded values."""
        return LineOfFlight(
            rigidity=None,
            proposed_action=(
                "Extract magic numbers and strings into named constants. "
                "Consider using configuration files for values that may change."
            ),
            expected_outcome="Self-documenting code with maintainable configuration",
            innovation_potential=0.5,
            risk_level=0.1,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_2(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting hardcoded values."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=None,
            expected_outcome="Self-documenting code with maintainable configuration",
            innovation_potential=0.5,
            risk_level=0.1,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_3(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting hardcoded values."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract magic numbers and strings into named constants. "
                "Consider using configuration files for values that may change."
            ),
            expected_outcome=None,
            innovation_potential=0.5,
            risk_level=0.1,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_4(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting hardcoded values."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract magic numbers and strings into named constants. "
                "Consider using configuration files for values that may change."
            ),
            expected_outcome="Self-documenting code with maintainable configuration",
            innovation_potential=None,
            risk_level=0.1,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_5(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting hardcoded values."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract magic numbers and strings into named constants. "
                "Consider using configuration files for values that may change."
            ),
            expected_outcome="Self-documenting code with maintainable configuration",
            innovation_potential=0.5,
            risk_level=None,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_6(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting hardcoded values."""
        return LineOfFlight(
            proposed_action=(
                "Extract magic numbers and strings into named constants. "
                "Consider using configuration files for values that may change."
            ),
            expected_outcome="Self-documenting code with maintainable configuration",
            innovation_potential=0.5,
            risk_level=0.1,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_7(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting hardcoded values."""
        return LineOfFlight(
            rigidity=rigidity,
            expected_outcome="Self-documenting code with maintainable configuration",
            innovation_potential=0.5,
            risk_level=0.1,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_8(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting hardcoded values."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract magic numbers and strings into named constants. "
                "Consider using configuration files for values that may change."
            ),
            innovation_potential=0.5,
            risk_level=0.1,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_9(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting hardcoded values."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract magic numbers and strings into named constants. "
                "Consider using configuration files for values that may change."
            ),
            expected_outcome="Self-documenting code with maintainable configuration",
            risk_level=0.1,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_10(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting hardcoded values."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract magic numbers and strings into named constants. "
                "Consider using configuration files for values that may change."
            ),
            expected_outcome="Self-documenting code with maintainable configuration",
            innovation_potential=0.5,
            )

    def xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_11(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting hardcoded values."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "XXExtract magic numbers and strings into named constants. XX"
                "Consider using configuration files for values that may change."
            ),
            expected_outcome="Self-documenting code with maintainable configuration",
            innovation_potential=0.5,
            risk_level=0.1,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_12(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting hardcoded values."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "extract magic numbers and strings into named constants. "
                "Consider using configuration files for values that may change."
            ),
            expected_outcome="Self-documenting code with maintainable configuration",
            innovation_potential=0.5,
            risk_level=0.1,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_13(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting hardcoded values."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "EXTRACT MAGIC NUMBERS AND STRINGS INTO NAMED CONSTANTS. "
                "Consider using configuration files for values that may change."
            ),
            expected_outcome="Self-documenting code with maintainable configuration",
            innovation_potential=0.5,
            risk_level=0.1,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_14(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting hardcoded values."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract magic numbers and strings into named constants. "
                "XXConsider using configuration files for values that may change.XX"
            ),
            expected_outcome="Self-documenting code with maintainable configuration",
            innovation_potential=0.5,
            risk_level=0.1,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_15(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting hardcoded values."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract magic numbers and strings into named constants. "
                "consider using configuration files for values that may change."
            ),
            expected_outcome="Self-documenting code with maintainable configuration",
            innovation_potential=0.5,
            risk_level=0.1,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_16(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting hardcoded values."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract magic numbers and strings into named constants. "
                "CONSIDER USING CONFIGURATION FILES FOR VALUES THAT MAY CHANGE."
            ),
            expected_outcome="Self-documenting code with maintainable configuration",
            innovation_potential=0.5,
            risk_level=0.1,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_17(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting hardcoded values."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract magic numbers and strings into named constants. "
                "Consider using configuration files for values that may change."
            ),
            expected_outcome="XXSelf-documenting code with maintainable configurationXX",
            innovation_potential=0.5,
            risk_level=0.1,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_18(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting hardcoded values."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract magic numbers and strings into named constants. "
                "Consider using configuration files for values that may change."
            ),
            expected_outcome="self-documenting code with maintainable configuration",
            innovation_potential=0.5,
            risk_level=0.1,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_19(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting hardcoded values."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract magic numbers and strings into named constants. "
                "Consider using configuration files for values that may change."
            ),
            expected_outcome="SELF-DOCUMENTING CODE WITH MAINTAINABLE CONFIGURATION",
            innovation_potential=0.5,
            risk_level=0.1,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_20(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting hardcoded values."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract magic numbers and strings into named constants. "
                "Consider using configuration files for values that may change."
            ),
            expected_outcome="Self-documenting code with maintainable configuration",
            innovation_potential=1.5,
            risk_level=0.1,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_21(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting hardcoded values."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract magic numbers and strings into named constants. "
                "Consider using configuration files for values that may change."
            ),
            expected_outcome="Self-documenting code with maintainable configuration",
            innovation_potential=0.5,
            risk_level=1.1,
        )
    
    xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_1': xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_1, 
        'xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_2': xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_2, 
        'xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_3': xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_3, 
        'xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_4': xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_4, 
        'xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_5': xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_5, 
        'xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_6': xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_6, 
        'xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_7': xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_7, 
        'xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_8': xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_8, 
        'xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_9': xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_9, 
        'xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_10': xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_10, 
        'xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_11': xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_11, 
        'xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_12': xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_12, 
        'xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_13': xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_13, 
        'xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_14': xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_14, 
        'xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_15': xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_15, 
        'xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_16': xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_16, 
        'xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_17': xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_17, 
        'xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_18': xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_18, 
        'xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_19': xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_19, 
        'xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_20': xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_20, 
        'xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_21': xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_21
    }
    
    def _propose_extract_constant(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_orig"), object.__getattribute__(self, "xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _propose_extract_constant.__signature__ = _mutmut_signature(xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_orig)
    xǁDeterritorializationEngineǁ_propose_extract_constant__mutmut_orig.__name__ = 'xǁDeterritorializationEngineǁ_propose_extract_constant'

    def xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_orig(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting repeated patterns."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract repeated code into reusable functions or classes. "
                "Use parameterization to handle variations."
            ),
            expected_outcome="DRY code with reduced maintenance burden",
            innovation_potential=0.6,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_1(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting repeated patterns."""
        return LineOfFlight(
            rigidity=None,
            proposed_action=(
                "Extract repeated code into reusable functions or classes. "
                "Use parameterization to handle variations."
            ),
            expected_outcome="DRY code with reduced maintenance burden",
            innovation_potential=0.6,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_2(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting repeated patterns."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=None,
            expected_outcome="DRY code with reduced maintenance burden",
            innovation_potential=0.6,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_3(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting repeated patterns."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract repeated code into reusable functions or classes. "
                "Use parameterization to handle variations."
            ),
            expected_outcome=None,
            innovation_potential=0.6,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_4(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting repeated patterns."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract repeated code into reusable functions or classes. "
                "Use parameterization to handle variations."
            ),
            expected_outcome="DRY code with reduced maintenance burden",
            innovation_potential=None,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_5(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting repeated patterns."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract repeated code into reusable functions or classes. "
                "Use parameterization to handle variations."
            ),
            expected_outcome="DRY code with reduced maintenance burden",
            innovation_potential=0.6,
            risk_level=None,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_6(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting repeated patterns."""
        return LineOfFlight(
            proposed_action=(
                "Extract repeated code into reusable functions or classes. "
                "Use parameterization to handle variations."
            ),
            expected_outcome="DRY code with reduced maintenance burden",
            innovation_potential=0.6,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_7(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting repeated patterns."""
        return LineOfFlight(
            rigidity=rigidity,
            expected_outcome="DRY code with reduced maintenance burden",
            innovation_potential=0.6,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_8(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting repeated patterns."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract repeated code into reusable functions or classes. "
                "Use parameterization to handle variations."
            ),
            innovation_potential=0.6,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_9(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting repeated patterns."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract repeated code into reusable functions or classes. "
                "Use parameterization to handle variations."
            ),
            expected_outcome="DRY code with reduced maintenance burden",
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_10(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting repeated patterns."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract repeated code into reusable functions or classes. "
                "Use parameterization to handle variations."
            ),
            expected_outcome="DRY code with reduced maintenance burden",
            innovation_potential=0.6,
            )

    def xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_11(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting repeated patterns."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "XXExtract repeated code into reusable functions or classes. XX"
                "Use parameterization to handle variations."
            ),
            expected_outcome="DRY code with reduced maintenance burden",
            innovation_potential=0.6,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_12(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting repeated patterns."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "extract repeated code into reusable functions or classes. "
                "Use parameterization to handle variations."
            ),
            expected_outcome="DRY code with reduced maintenance burden",
            innovation_potential=0.6,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_13(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting repeated patterns."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "EXTRACT REPEATED CODE INTO REUSABLE FUNCTIONS OR CLASSES. "
                "Use parameterization to handle variations."
            ),
            expected_outcome="DRY code with reduced maintenance burden",
            innovation_potential=0.6,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_14(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting repeated patterns."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract repeated code into reusable functions or classes. "
                "XXUse parameterization to handle variations.XX"
            ),
            expected_outcome="DRY code with reduced maintenance burden",
            innovation_potential=0.6,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_15(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting repeated patterns."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract repeated code into reusable functions or classes. "
                "use parameterization to handle variations."
            ),
            expected_outcome="DRY code with reduced maintenance burden",
            innovation_potential=0.6,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_16(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting repeated patterns."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract repeated code into reusable functions or classes. "
                "USE PARAMETERIZATION TO HANDLE VARIATIONS."
            ),
            expected_outcome="DRY code with reduced maintenance burden",
            innovation_potential=0.6,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_17(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting repeated patterns."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract repeated code into reusable functions or classes. "
                "Use parameterization to handle variations."
            ),
            expected_outcome="XXDRY code with reduced maintenance burdenXX",
            innovation_potential=0.6,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_18(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting repeated patterns."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract repeated code into reusable functions or classes. "
                "Use parameterization to handle variations."
            ),
            expected_outcome="dry code with reduced maintenance burden",
            innovation_potential=0.6,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_19(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting repeated patterns."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract repeated code into reusable functions or classes. "
                "Use parameterization to handle variations."
            ),
            expected_outcome="DRY CODE WITH REDUCED MAINTENANCE BURDEN",
            innovation_potential=0.6,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_20(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting repeated patterns."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract repeated code into reusable functions or classes. "
                "Use parameterization to handle variations."
            ),
            expected_outcome="DRY code with reduced maintenance burden",
            innovation_potential=1.6,
            risk_level=0.3,
        )

    def xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_21(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting repeated patterns."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract repeated code into reusable functions or classes. "
                "Use parameterization to handle variations."
            ),
            expected_outcome="DRY code with reduced maintenance burden",
            innovation_potential=0.6,
            risk_level=1.3,
        )
    
    xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_1': xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_1, 
        'xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_2': xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_2, 
        'xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_3': xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_3, 
        'xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_4': xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_4, 
        'xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_5': xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_5, 
        'xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_6': xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_6, 
        'xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_7': xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_7, 
        'xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_8': xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_8, 
        'xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_9': xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_9, 
        'xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_10': xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_10, 
        'xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_11': xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_11, 
        'xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_12': xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_12, 
        'xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_13': xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_13, 
        'xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_14': xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_14, 
        'xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_15': xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_15, 
        'xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_16': xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_16, 
        'xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_17': xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_17, 
        'xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_18': xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_18, 
        'xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_19': xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_19, 
        'xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_20': xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_20, 
        'xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_21': xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_21
    }
    
    def _propose_extract_function(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_orig"), object.__getattribute__(self, "xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _propose_extract_function.__signature__ = _mutmut_signature(xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_orig)
    xǁDeterritorializationEngineǁ_propose_extract_function__mutmut_orig.__name__ = 'xǁDeterritorializationEngineǁ_propose_extract_function'

    def xǁDeterritorializationEngineǁ_propose_simplify__mutmut_orig(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose simplifying overly complex code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Simplify complex logic by breaking into smaller steps. "
                "Use descriptive variable names and comments to clarify intent."
            ),
            expected_outcome="Clearer, more maintainable code",
            innovation_potential=0.5,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_simplify__mutmut_1(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose simplifying overly complex code."""
        return LineOfFlight(
            rigidity=None,
            proposed_action=(
                "Simplify complex logic by breaking into smaller steps. "
                "Use descriptive variable names and comments to clarify intent."
            ),
            expected_outcome="Clearer, more maintainable code",
            innovation_potential=0.5,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_simplify__mutmut_2(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose simplifying overly complex code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=None,
            expected_outcome="Clearer, more maintainable code",
            innovation_potential=0.5,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_simplify__mutmut_3(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose simplifying overly complex code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Simplify complex logic by breaking into smaller steps. "
                "Use descriptive variable names and comments to clarify intent."
            ),
            expected_outcome=None,
            innovation_potential=0.5,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_simplify__mutmut_4(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose simplifying overly complex code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Simplify complex logic by breaking into smaller steps. "
                "Use descriptive variable names and comments to clarify intent."
            ),
            expected_outcome="Clearer, more maintainable code",
            innovation_potential=None,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_simplify__mutmut_5(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose simplifying overly complex code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Simplify complex logic by breaking into smaller steps. "
                "Use descriptive variable names and comments to clarify intent."
            ),
            expected_outcome="Clearer, more maintainable code",
            innovation_potential=0.5,
            risk_level=None,
        )

    def xǁDeterritorializationEngineǁ_propose_simplify__mutmut_6(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose simplifying overly complex code."""
        return LineOfFlight(
            proposed_action=(
                "Simplify complex logic by breaking into smaller steps. "
                "Use descriptive variable names and comments to clarify intent."
            ),
            expected_outcome="Clearer, more maintainable code",
            innovation_potential=0.5,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_simplify__mutmut_7(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose simplifying overly complex code."""
        return LineOfFlight(
            rigidity=rigidity,
            expected_outcome="Clearer, more maintainable code",
            innovation_potential=0.5,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_simplify__mutmut_8(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose simplifying overly complex code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Simplify complex logic by breaking into smaller steps. "
                "Use descriptive variable names and comments to clarify intent."
            ),
            innovation_potential=0.5,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_simplify__mutmut_9(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose simplifying overly complex code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Simplify complex logic by breaking into smaller steps. "
                "Use descriptive variable names and comments to clarify intent."
            ),
            expected_outcome="Clearer, more maintainable code",
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_simplify__mutmut_10(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose simplifying overly complex code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Simplify complex logic by breaking into smaller steps. "
                "Use descriptive variable names and comments to clarify intent."
            ),
            expected_outcome="Clearer, more maintainable code",
            innovation_potential=0.5,
            )

    def xǁDeterritorializationEngineǁ_propose_simplify__mutmut_11(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose simplifying overly complex code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "XXSimplify complex logic by breaking into smaller steps. XX"
                "Use descriptive variable names and comments to clarify intent."
            ),
            expected_outcome="Clearer, more maintainable code",
            innovation_potential=0.5,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_simplify__mutmut_12(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose simplifying overly complex code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "simplify complex logic by breaking into smaller steps. "
                "Use descriptive variable names and comments to clarify intent."
            ),
            expected_outcome="Clearer, more maintainable code",
            innovation_potential=0.5,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_simplify__mutmut_13(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose simplifying overly complex code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "SIMPLIFY COMPLEX LOGIC BY BREAKING INTO SMALLER STEPS. "
                "Use descriptive variable names and comments to clarify intent."
            ),
            expected_outcome="Clearer, more maintainable code",
            innovation_potential=0.5,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_simplify__mutmut_14(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose simplifying overly complex code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Simplify complex logic by breaking into smaller steps. "
                "XXUse descriptive variable names and comments to clarify intent.XX"
            ),
            expected_outcome="Clearer, more maintainable code",
            innovation_potential=0.5,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_simplify__mutmut_15(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose simplifying overly complex code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Simplify complex logic by breaking into smaller steps. "
                "use descriptive variable names and comments to clarify intent."
            ),
            expected_outcome="Clearer, more maintainable code",
            innovation_potential=0.5,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_simplify__mutmut_16(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose simplifying overly complex code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Simplify complex logic by breaking into smaller steps. "
                "USE DESCRIPTIVE VARIABLE NAMES AND COMMENTS TO CLARIFY INTENT."
            ),
            expected_outcome="Clearer, more maintainable code",
            innovation_potential=0.5,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_simplify__mutmut_17(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose simplifying overly complex code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Simplify complex logic by breaking into smaller steps. "
                "Use descriptive variable names and comments to clarify intent."
            ),
            expected_outcome="XXClearer, more maintainable codeXX",
            innovation_potential=0.5,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_simplify__mutmut_18(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose simplifying overly complex code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Simplify complex logic by breaking into smaller steps. "
                "Use descriptive variable names and comments to clarify intent."
            ),
            expected_outcome="clearer, more maintainable code",
            innovation_potential=0.5,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_simplify__mutmut_19(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose simplifying overly complex code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Simplify complex logic by breaking into smaller steps. "
                "Use descriptive variable names and comments to clarify intent."
            ),
            expected_outcome="CLEARER, MORE MAINTAINABLE CODE",
            innovation_potential=0.5,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_simplify__mutmut_20(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose simplifying overly complex code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Simplify complex logic by breaking into smaller steps. "
                "Use descriptive variable names and comments to clarify intent."
            ),
            expected_outcome="Clearer, more maintainable code",
            innovation_potential=1.5,
            risk_level=0.2,
        )

    def xǁDeterritorializationEngineǁ_propose_simplify__mutmut_21(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose simplifying overly complex code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Simplify complex logic by breaking into smaller steps. "
                "Use descriptive variable names and comments to clarify intent."
            ),
            expected_outcome="Clearer, more maintainable code",
            innovation_potential=0.5,
            risk_level=1.2,
        )
    
    xǁDeterritorializationEngineǁ_propose_simplify__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDeterritorializationEngineǁ_propose_simplify__mutmut_1': xǁDeterritorializationEngineǁ_propose_simplify__mutmut_1, 
        'xǁDeterritorializationEngineǁ_propose_simplify__mutmut_2': xǁDeterritorializationEngineǁ_propose_simplify__mutmut_2, 
        'xǁDeterritorializationEngineǁ_propose_simplify__mutmut_3': xǁDeterritorializationEngineǁ_propose_simplify__mutmut_3, 
        'xǁDeterritorializationEngineǁ_propose_simplify__mutmut_4': xǁDeterritorializationEngineǁ_propose_simplify__mutmut_4, 
        'xǁDeterritorializationEngineǁ_propose_simplify__mutmut_5': xǁDeterritorializationEngineǁ_propose_simplify__mutmut_5, 
        'xǁDeterritorializationEngineǁ_propose_simplify__mutmut_6': xǁDeterritorializationEngineǁ_propose_simplify__mutmut_6, 
        'xǁDeterritorializationEngineǁ_propose_simplify__mutmut_7': xǁDeterritorializationEngineǁ_propose_simplify__mutmut_7, 
        'xǁDeterritorializationEngineǁ_propose_simplify__mutmut_8': xǁDeterritorializationEngineǁ_propose_simplify__mutmut_8, 
        'xǁDeterritorializationEngineǁ_propose_simplify__mutmut_9': xǁDeterritorializationEngineǁ_propose_simplify__mutmut_9, 
        'xǁDeterritorializationEngineǁ_propose_simplify__mutmut_10': xǁDeterritorializationEngineǁ_propose_simplify__mutmut_10, 
        'xǁDeterritorializationEngineǁ_propose_simplify__mutmut_11': xǁDeterritorializationEngineǁ_propose_simplify__mutmut_11, 
        'xǁDeterritorializationEngineǁ_propose_simplify__mutmut_12': xǁDeterritorializationEngineǁ_propose_simplify__mutmut_12, 
        'xǁDeterritorializationEngineǁ_propose_simplify__mutmut_13': xǁDeterritorializationEngineǁ_propose_simplify__mutmut_13, 
        'xǁDeterritorializationEngineǁ_propose_simplify__mutmut_14': xǁDeterritorializationEngineǁ_propose_simplify__mutmut_14, 
        'xǁDeterritorializationEngineǁ_propose_simplify__mutmut_15': xǁDeterritorializationEngineǁ_propose_simplify__mutmut_15, 
        'xǁDeterritorializationEngineǁ_propose_simplify__mutmut_16': xǁDeterritorializationEngineǁ_propose_simplify__mutmut_16, 
        'xǁDeterritorializationEngineǁ_propose_simplify__mutmut_17': xǁDeterritorializationEngineǁ_propose_simplify__mutmut_17, 
        'xǁDeterritorializationEngineǁ_propose_simplify__mutmut_18': xǁDeterritorializationEngineǁ_propose_simplify__mutmut_18, 
        'xǁDeterritorializationEngineǁ_propose_simplify__mutmut_19': xǁDeterritorializationEngineǁ_propose_simplify__mutmut_19, 
        'xǁDeterritorializationEngineǁ_propose_simplify__mutmut_20': xǁDeterritorializationEngineǁ_propose_simplify__mutmut_20, 
        'xǁDeterritorializationEngineǁ_propose_simplify__mutmut_21': xǁDeterritorializationEngineǁ_propose_simplify__mutmut_21
    }
    
    def _propose_simplify(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDeterritorializationEngineǁ_propose_simplify__mutmut_orig"), object.__getattribute__(self, "xǁDeterritorializationEngineǁ_propose_simplify__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _propose_simplify.__signature__ = _mutmut_signature(xǁDeterritorializationEngineǁ_propose_simplify__mutmut_orig)
    xǁDeterritorializationEngineǁ_propose_simplify__mutmut_orig.__name__ = 'xǁDeterritorializationEngineǁ_propose_simplify'

    def xǁDeterritorializationEngineǁcalculate_deterritorialization_force__mutmut_orig(
        self, rigidity_score: float, innovation_score: float
    ) -> float:
        """
        Calculate deterritorialization force.

        F_deterr = Innovation_Pressure - Rigidity

        Where:
        - Positive: Deterritorialization needed
        - Negative: Reterritorialization occurring
        - Zero: Equilibrium

        Reference: .codex/docs/PHILOSOPHICAL_FRAMEWORK.md#deterritorialization-force
        """
        force = innovation_score - rigidity_score
        LOGGER.debug(
            f"Deterritorialization force: {force:.2f} "
            f"(innovation: {innovation_score:.2f}, rigidity: {rigidity_score:.2f})"
        )
        return force

    def xǁDeterritorializationEngineǁcalculate_deterritorialization_force__mutmut_1(
        self, rigidity_score: float, innovation_score: float
    ) -> float:
        """
        Calculate deterritorialization force.

        F_deterr = Innovation_Pressure - Rigidity

        Where:
        - Positive: Deterritorialization needed
        - Negative: Reterritorialization occurring
        - Zero: Equilibrium

        Reference: .codex/docs/PHILOSOPHICAL_FRAMEWORK.md#deterritorialization-force
        """
        force = None
        LOGGER.debug(
            f"Deterritorialization force: {force:.2f} "
            f"(innovation: {innovation_score:.2f}, rigidity: {rigidity_score:.2f})"
        )
        return force

    def xǁDeterritorializationEngineǁcalculate_deterritorialization_force__mutmut_2(
        self, rigidity_score: float, innovation_score: float
    ) -> float:
        """
        Calculate deterritorialization force.

        F_deterr = Innovation_Pressure - Rigidity

        Where:
        - Positive: Deterritorialization needed
        - Negative: Reterritorialization occurring
        - Zero: Equilibrium

        Reference: .codex/docs/PHILOSOPHICAL_FRAMEWORK.md#deterritorialization-force
        """
        force = innovation_score + rigidity_score
        LOGGER.debug(
            f"Deterritorialization force: {force:.2f} "
            f"(innovation: {innovation_score:.2f}, rigidity: {rigidity_score:.2f})"
        )
        return force

    def xǁDeterritorializationEngineǁcalculate_deterritorialization_force__mutmut_3(
        self, rigidity_score: float, innovation_score: float
    ) -> float:
        """
        Calculate deterritorialization force.

        F_deterr = Innovation_Pressure - Rigidity

        Where:
        - Positive: Deterritorialization needed
        - Negative: Reterritorialization occurring
        - Zero: Equilibrium

        Reference: .codex/docs/PHILOSOPHICAL_FRAMEWORK.md#deterritorialization-force
        """
        force = innovation_score - rigidity_score
        LOGGER.debug(
            None
        )
        return force
    
    xǁDeterritorializationEngineǁcalculate_deterritorialization_force__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDeterritorializationEngineǁcalculate_deterritorialization_force__mutmut_1': xǁDeterritorializationEngineǁcalculate_deterritorialization_force__mutmut_1, 
        'xǁDeterritorializationEngineǁcalculate_deterritorialization_force__mutmut_2': xǁDeterritorializationEngineǁcalculate_deterritorialization_force__mutmut_2, 
        'xǁDeterritorializationEngineǁcalculate_deterritorialization_force__mutmut_3': xǁDeterritorializationEngineǁcalculate_deterritorialization_force__mutmut_3
    }
    
    def calculate_deterritorialization_force(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDeterritorializationEngineǁcalculate_deterritorialization_force__mutmut_orig"), object.__getattribute__(self, "xǁDeterritorializationEngineǁcalculate_deterritorialization_force__mutmut_mutants"), args, kwargs, self)
        return result 
    
    calculate_deterritorialization_force.__signature__ = _mutmut_signature(xǁDeterritorializationEngineǁcalculate_deterritorialization_force__mutmut_orig)
    xǁDeterritorializationEngineǁcalculate_deterritorialization_force__mutmut_orig.__name__ = 'xǁDeterritorializationEngineǁcalculate_deterritorialization_force'

    def xǁDeterritorializationEngineǁget_stats__mutmut_orig(self) -> Dict[str, Any]:
        """Get statistics about detected rigidities and lines of flight."""
        rigidity_counts = {}
        for rigidity in self.rigidities:
            rtype = rigidity.rigidity_type.value
            rigidity_counts[rtype] = rigidity_counts.get(rtype, 0) + 1

        avg_severity = (
            sum(r.severity for r in self.rigidities) / len(self.rigidities)
            if self.rigidities
            else 0.0
        )

        return {
            "total_rigidities": len(self.rigidities),
            "rigidity_by_type": rigidity_counts,
            "average_severity": avg_severity,
            "lines_of_flight": len(self.lines_of_flight),
            "high_priority_rigidities": sum(
                1 for r in self.rigidities if r.severity >= 0.7
            ),
        }

    def xǁDeterritorializationEngineǁget_stats__mutmut_1(self) -> Dict[str, Any]:
        """Get statistics about detected rigidities and lines of flight."""
        rigidity_counts = None
        for rigidity in self.rigidities:
            rtype = rigidity.rigidity_type.value
            rigidity_counts[rtype] = rigidity_counts.get(rtype, 0) + 1

        avg_severity = (
            sum(r.severity for r in self.rigidities) / len(self.rigidities)
            if self.rigidities
            else 0.0
        )

        return {
            "total_rigidities": len(self.rigidities),
            "rigidity_by_type": rigidity_counts,
            "average_severity": avg_severity,
            "lines_of_flight": len(self.lines_of_flight),
            "high_priority_rigidities": sum(
                1 for r in self.rigidities if r.severity >= 0.7
            ),
        }

    def xǁDeterritorializationEngineǁget_stats__mutmut_2(self) -> Dict[str, Any]:
        """Get statistics about detected rigidities and lines of flight."""
        rigidity_counts = {}
        for rigidity in self.rigidities:
            rtype = None
            rigidity_counts[rtype] = rigidity_counts.get(rtype, 0) + 1

        avg_severity = (
            sum(r.severity for r in self.rigidities) / len(self.rigidities)
            if self.rigidities
            else 0.0
        )

        return {
            "total_rigidities": len(self.rigidities),
            "rigidity_by_type": rigidity_counts,
            "average_severity": avg_severity,
            "lines_of_flight": len(self.lines_of_flight),
            "high_priority_rigidities": sum(
                1 for r in self.rigidities if r.severity >= 0.7
            ),
        }

    def xǁDeterritorializationEngineǁget_stats__mutmut_3(self) -> Dict[str, Any]:
        """Get statistics about detected rigidities and lines of flight."""
        rigidity_counts = {}
        for rigidity in self.rigidities:
            rtype = rigidity.rigidity_type.value
            rigidity_counts[rtype] = None

        avg_severity = (
            sum(r.severity for r in self.rigidities) / len(self.rigidities)
            if self.rigidities
            else 0.0
        )

        return {
            "total_rigidities": len(self.rigidities),
            "rigidity_by_type": rigidity_counts,
            "average_severity": avg_severity,
            "lines_of_flight": len(self.lines_of_flight),
            "high_priority_rigidities": sum(
                1 for r in self.rigidities if r.severity >= 0.7
            ),
        }

    def xǁDeterritorializationEngineǁget_stats__mutmut_4(self) -> Dict[str, Any]:
        """Get statistics about detected rigidities and lines of flight."""
        rigidity_counts = {}
        for rigidity in self.rigidities:
            rtype = rigidity.rigidity_type.value
            rigidity_counts[rtype] = rigidity_counts.get(rtype, 0) - 1

        avg_severity = (
            sum(r.severity for r in self.rigidities) / len(self.rigidities)
            if self.rigidities
            else 0.0
        )

        return {
            "total_rigidities": len(self.rigidities),
            "rigidity_by_type": rigidity_counts,
            "average_severity": avg_severity,
            "lines_of_flight": len(self.lines_of_flight),
            "high_priority_rigidities": sum(
                1 for r in self.rigidities if r.severity >= 0.7
            ),
        }

    def xǁDeterritorializationEngineǁget_stats__mutmut_5(self) -> Dict[str, Any]:
        """Get statistics about detected rigidities and lines of flight."""
        rigidity_counts = {}
        for rigidity in self.rigidities:
            rtype = rigidity.rigidity_type.value
            rigidity_counts[rtype] = rigidity_counts.get(None, 0) + 1

        avg_severity = (
            sum(r.severity for r in self.rigidities) / len(self.rigidities)
            if self.rigidities
            else 0.0
        )

        return {
            "total_rigidities": len(self.rigidities),
            "rigidity_by_type": rigidity_counts,
            "average_severity": avg_severity,
            "lines_of_flight": len(self.lines_of_flight),
            "high_priority_rigidities": sum(
                1 for r in self.rigidities if r.severity >= 0.7
            ),
        }

    def xǁDeterritorializationEngineǁget_stats__mutmut_6(self) -> Dict[str, Any]:
        """Get statistics about detected rigidities and lines of flight."""
        rigidity_counts = {}
        for rigidity in self.rigidities:
            rtype = rigidity.rigidity_type.value
            rigidity_counts[rtype] = rigidity_counts.get(rtype, None) + 1

        avg_severity = (
            sum(r.severity for r in self.rigidities) / len(self.rigidities)
            if self.rigidities
            else 0.0
        )

        return {
            "total_rigidities": len(self.rigidities),
            "rigidity_by_type": rigidity_counts,
            "average_severity": avg_severity,
            "lines_of_flight": len(self.lines_of_flight),
            "high_priority_rigidities": sum(
                1 for r in self.rigidities if r.severity >= 0.7
            ),
        }

    def xǁDeterritorializationEngineǁget_stats__mutmut_7(self) -> Dict[str, Any]:
        """Get statistics about detected rigidities and lines of flight."""
        rigidity_counts = {}
        for rigidity in self.rigidities:
            rtype = rigidity.rigidity_type.value
            rigidity_counts[rtype] = rigidity_counts.get(0) + 1

        avg_severity = (
            sum(r.severity for r in self.rigidities) / len(self.rigidities)
            if self.rigidities
            else 0.0
        )

        return {
            "total_rigidities": len(self.rigidities),
            "rigidity_by_type": rigidity_counts,
            "average_severity": avg_severity,
            "lines_of_flight": len(self.lines_of_flight),
            "high_priority_rigidities": sum(
                1 for r in self.rigidities if r.severity >= 0.7
            ),
        }

    def xǁDeterritorializationEngineǁget_stats__mutmut_8(self) -> Dict[str, Any]:
        """Get statistics about detected rigidities and lines of flight."""
        rigidity_counts = {}
        for rigidity in self.rigidities:
            rtype = rigidity.rigidity_type.value
            rigidity_counts[rtype] = rigidity_counts.get(rtype, ) + 1

        avg_severity = (
            sum(r.severity for r in self.rigidities) / len(self.rigidities)
            if self.rigidities
            else 0.0
        )

        return {
            "total_rigidities": len(self.rigidities),
            "rigidity_by_type": rigidity_counts,
            "average_severity": avg_severity,
            "lines_of_flight": len(self.lines_of_flight),
            "high_priority_rigidities": sum(
                1 for r in self.rigidities if r.severity >= 0.7
            ),
        }

    def xǁDeterritorializationEngineǁget_stats__mutmut_9(self) -> Dict[str, Any]:
        """Get statistics about detected rigidities and lines of flight."""
        rigidity_counts = {}
        for rigidity in self.rigidities:
            rtype = rigidity.rigidity_type.value
            rigidity_counts[rtype] = rigidity_counts.get(rtype, 1) + 1

        avg_severity = (
            sum(r.severity for r in self.rigidities) / len(self.rigidities)
            if self.rigidities
            else 0.0
        )

        return {
            "total_rigidities": len(self.rigidities),
            "rigidity_by_type": rigidity_counts,
            "average_severity": avg_severity,
            "lines_of_flight": len(self.lines_of_flight),
            "high_priority_rigidities": sum(
                1 for r in self.rigidities if r.severity >= 0.7
            ),
        }

    def xǁDeterritorializationEngineǁget_stats__mutmut_10(self) -> Dict[str, Any]:
        """Get statistics about detected rigidities and lines of flight."""
        rigidity_counts = {}
        for rigidity in self.rigidities:
            rtype = rigidity.rigidity_type.value
            rigidity_counts[rtype] = rigidity_counts.get(rtype, 0) + 2

        avg_severity = (
            sum(r.severity for r in self.rigidities) / len(self.rigidities)
            if self.rigidities
            else 0.0
        )

        return {
            "total_rigidities": len(self.rigidities),
            "rigidity_by_type": rigidity_counts,
            "average_severity": avg_severity,
            "lines_of_flight": len(self.lines_of_flight),
            "high_priority_rigidities": sum(
                1 for r in self.rigidities if r.severity >= 0.7
            ),
        }

    def xǁDeterritorializationEngineǁget_stats__mutmut_11(self) -> Dict[str, Any]:
        """Get statistics about detected rigidities and lines of flight."""
        rigidity_counts = {}
        for rigidity in self.rigidities:
            rtype = rigidity.rigidity_type.value
            rigidity_counts[rtype] = rigidity_counts.get(rtype, 0) + 1

        avg_severity = None

        return {
            "total_rigidities": len(self.rigidities),
            "rigidity_by_type": rigidity_counts,
            "average_severity": avg_severity,
            "lines_of_flight": len(self.lines_of_flight),
            "high_priority_rigidities": sum(
                1 for r in self.rigidities if r.severity >= 0.7
            ),
        }

    def xǁDeterritorializationEngineǁget_stats__mutmut_12(self) -> Dict[str, Any]:
        """Get statistics about detected rigidities and lines of flight."""
        rigidity_counts = {}
        for rigidity in self.rigidities:
            rtype = rigidity.rigidity_type.value
            rigidity_counts[rtype] = rigidity_counts.get(rtype, 0) + 1

        avg_severity = (
            sum(r.severity for r in self.rigidities) * len(self.rigidities)
            if self.rigidities
            else 0.0
        )

        return {
            "total_rigidities": len(self.rigidities),
            "rigidity_by_type": rigidity_counts,
            "average_severity": avg_severity,
            "lines_of_flight": len(self.lines_of_flight),
            "high_priority_rigidities": sum(
                1 for r in self.rigidities if r.severity >= 0.7
            ),
        }

    def xǁDeterritorializationEngineǁget_stats__mutmut_13(self) -> Dict[str, Any]:
        """Get statistics about detected rigidities and lines of flight."""
        rigidity_counts = {}
        for rigidity in self.rigidities:
            rtype = rigidity.rigidity_type.value
            rigidity_counts[rtype] = rigidity_counts.get(rtype, 0) + 1

        avg_severity = (
            sum(None) / len(self.rigidities)
            if self.rigidities
            else 0.0
        )

        return {
            "total_rigidities": len(self.rigidities),
            "rigidity_by_type": rigidity_counts,
            "average_severity": avg_severity,
            "lines_of_flight": len(self.lines_of_flight),
            "high_priority_rigidities": sum(
                1 for r in self.rigidities if r.severity >= 0.7
            ),
        }

    def xǁDeterritorializationEngineǁget_stats__mutmut_14(self) -> Dict[str, Any]:
        """Get statistics about detected rigidities and lines of flight."""
        rigidity_counts = {}
        for rigidity in self.rigidities:
            rtype = rigidity.rigidity_type.value
            rigidity_counts[rtype] = rigidity_counts.get(rtype, 0) + 1

        avg_severity = (
            sum(r.severity for r in self.rigidities) / len(self.rigidities)
            if self.rigidities
            else 1.0
        )

        return {
            "total_rigidities": len(self.rigidities),
            "rigidity_by_type": rigidity_counts,
            "average_severity": avg_severity,
            "lines_of_flight": len(self.lines_of_flight),
            "high_priority_rigidities": sum(
                1 for r in self.rigidities if r.severity >= 0.7
            ),
        }

    def xǁDeterritorializationEngineǁget_stats__mutmut_15(self) -> Dict[str, Any]:
        """Get statistics about detected rigidities and lines of flight."""
        rigidity_counts = {}
        for rigidity in self.rigidities:
            rtype = rigidity.rigidity_type.value
            rigidity_counts[rtype] = rigidity_counts.get(rtype, 0) + 1

        avg_severity = (
            sum(r.severity for r in self.rigidities) / len(self.rigidities)
            if self.rigidities
            else 0.0
        )

        return {
            "XXtotal_rigiditiesXX": len(self.rigidities),
            "rigidity_by_type": rigidity_counts,
            "average_severity": avg_severity,
            "lines_of_flight": len(self.lines_of_flight),
            "high_priority_rigidities": sum(
                1 for r in self.rigidities if r.severity >= 0.7
            ),
        }

    def xǁDeterritorializationEngineǁget_stats__mutmut_16(self) -> Dict[str, Any]:
        """Get statistics about detected rigidities and lines of flight."""
        rigidity_counts = {}
        for rigidity in self.rigidities:
            rtype = rigidity.rigidity_type.value
            rigidity_counts[rtype] = rigidity_counts.get(rtype, 0) + 1

        avg_severity = (
            sum(r.severity for r in self.rigidities) / len(self.rigidities)
            if self.rigidities
            else 0.0
        )

        return {
            "TOTAL_RIGIDITIES": len(self.rigidities),
            "rigidity_by_type": rigidity_counts,
            "average_severity": avg_severity,
            "lines_of_flight": len(self.lines_of_flight),
            "high_priority_rigidities": sum(
                1 for r in self.rigidities if r.severity >= 0.7
            ),
        }

    def xǁDeterritorializationEngineǁget_stats__mutmut_17(self) -> Dict[str, Any]:
        """Get statistics about detected rigidities and lines of flight."""
        rigidity_counts = {}
        for rigidity in self.rigidities:
            rtype = rigidity.rigidity_type.value
            rigidity_counts[rtype] = rigidity_counts.get(rtype, 0) + 1

        avg_severity = (
            sum(r.severity for r in self.rigidities) / len(self.rigidities)
            if self.rigidities
            else 0.0
        )

        return {
            "total_rigidities": len(self.rigidities),
            "XXrigidity_by_typeXX": rigidity_counts,
            "average_severity": avg_severity,
            "lines_of_flight": len(self.lines_of_flight),
            "high_priority_rigidities": sum(
                1 for r in self.rigidities if r.severity >= 0.7
            ),
        }

    def xǁDeterritorializationEngineǁget_stats__mutmut_18(self) -> Dict[str, Any]:
        """Get statistics about detected rigidities and lines of flight."""
        rigidity_counts = {}
        for rigidity in self.rigidities:
            rtype = rigidity.rigidity_type.value
            rigidity_counts[rtype] = rigidity_counts.get(rtype, 0) + 1

        avg_severity = (
            sum(r.severity for r in self.rigidities) / len(self.rigidities)
            if self.rigidities
            else 0.0
        )

        return {
            "total_rigidities": len(self.rigidities),
            "RIGIDITY_BY_TYPE": rigidity_counts,
            "average_severity": avg_severity,
            "lines_of_flight": len(self.lines_of_flight),
            "high_priority_rigidities": sum(
                1 for r in self.rigidities if r.severity >= 0.7
            ),
        }

    def xǁDeterritorializationEngineǁget_stats__mutmut_19(self) -> Dict[str, Any]:
        """Get statistics about detected rigidities and lines of flight."""
        rigidity_counts = {}
        for rigidity in self.rigidities:
            rtype = rigidity.rigidity_type.value
            rigidity_counts[rtype] = rigidity_counts.get(rtype, 0) + 1

        avg_severity = (
            sum(r.severity for r in self.rigidities) / len(self.rigidities)
            if self.rigidities
            else 0.0
        )

        return {
            "total_rigidities": len(self.rigidities),
            "rigidity_by_type": rigidity_counts,
            "XXaverage_severityXX": avg_severity,
            "lines_of_flight": len(self.lines_of_flight),
            "high_priority_rigidities": sum(
                1 for r in self.rigidities if r.severity >= 0.7
            ),
        }

    def xǁDeterritorializationEngineǁget_stats__mutmut_20(self) -> Dict[str, Any]:
        """Get statistics about detected rigidities and lines of flight."""
        rigidity_counts = {}
        for rigidity in self.rigidities:
            rtype = rigidity.rigidity_type.value
            rigidity_counts[rtype] = rigidity_counts.get(rtype, 0) + 1

        avg_severity = (
            sum(r.severity for r in self.rigidities) / len(self.rigidities)
            if self.rigidities
            else 0.0
        )

        return {
            "total_rigidities": len(self.rigidities),
            "rigidity_by_type": rigidity_counts,
            "AVERAGE_SEVERITY": avg_severity,
            "lines_of_flight": len(self.lines_of_flight),
            "high_priority_rigidities": sum(
                1 for r in self.rigidities if r.severity >= 0.7
            ),
        }

    def xǁDeterritorializationEngineǁget_stats__mutmut_21(self) -> Dict[str, Any]:
        """Get statistics about detected rigidities and lines of flight."""
        rigidity_counts = {}
        for rigidity in self.rigidities:
            rtype = rigidity.rigidity_type.value
            rigidity_counts[rtype] = rigidity_counts.get(rtype, 0) + 1

        avg_severity = (
            sum(r.severity for r in self.rigidities) / len(self.rigidities)
            if self.rigidities
            else 0.0
        )

        return {
            "total_rigidities": len(self.rigidities),
            "rigidity_by_type": rigidity_counts,
            "average_severity": avg_severity,
            "XXlines_of_flightXX": len(self.lines_of_flight),
            "high_priority_rigidities": sum(
                1 for r in self.rigidities if r.severity >= 0.7
            ),
        }

    def xǁDeterritorializationEngineǁget_stats__mutmut_22(self) -> Dict[str, Any]:
        """Get statistics about detected rigidities and lines of flight."""
        rigidity_counts = {}
        for rigidity in self.rigidities:
            rtype = rigidity.rigidity_type.value
            rigidity_counts[rtype] = rigidity_counts.get(rtype, 0) + 1

        avg_severity = (
            sum(r.severity for r in self.rigidities) / len(self.rigidities)
            if self.rigidities
            else 0.0
        )

        return {
            "total_rigidities": len(self.rigidities),
            "rigidity_by_type": rigidity_counts,
            "average_severity": avg_severity,
            "LINES_OF_FLIGHT": len(self.lines_of_flight),
            "high_priority_rigidities": sum(
                1 for r in self.rigidities if r.severity >= 0.7
            ),
        }

    def xǁDeterritorializationEngineǁget_stats__mutmut_23(self) -> Dict[str, Any]:
        """Get statistics about detected rigidities and lines of flight."""
        rigidity_counts = {}
        for rigidity in self.rigidities:
            rtype = rigidity.rigidity_type.value
            rigidity_counts[rtype] = rigidity_counts.get(rtype, 0) + 1

        avg_severity = (
            sum(r.severity for r in self.rigidities) / len(self.rigidities)
            if self.rigidities
            else 0.0
        )

        return {
            "total_rigidities": len(self.rigidities),
            "rigidity_by_type": rigidity_counts,
            "average_severity": avg_severity,
            "lines_of_flight": len(self.lines_of_flight),
            "XXhigh_priority_rigiditiesXX": sum(
                1 for r in self.rigidities if r.severity >= 0.7
            ),
        }

    def xǁDeterritorializationEngineǁget_stats__mutmut_24(self) -> Dict[str, Any]:
        """Get statistics about detected rigidities and lines of flight."""
        rigidity_counts = {}
        for rigidity in self.rigidities:
            rtype = rigidity.rigidity_type.value
            rigidity_counts[rtype] = rigidity_counts.get(rtype, 0) + 1

        avg_severity = (
            sum(r.severity for r in self.rigidities) / len(self.rigidities)
            if self.rigidities
            else 0.0
        )

        return {
            "total_rigidities": len(self.rigidities),
            "rigidity_by_type": rigidity_counts,
            "average_severity": avg_severity,
            "lines_of_flight": len(self.lines_of_flight),
            "HIGH_PRIORITY_RIGIDITIES": sum(
                1 for r in self.rigidities if r.severity >= 0.7
            ),
        }

    def xǁDeterritorializationEngineǁget_stats__mutmut_25(self) -> Dict[str, Any]:
        """Get statistics about detected rigidities and lines of flight."""
        rigidity_counts = {}
        for rigidity in self.rigidities:
            rtype = rigidity.rigidity_type.value
            rigidity_counts[rtype] = rigidity_counts.get(rtype, 0) + 1

        avg_severity = (
            sum(r.severity for r in self.rigidities) / len(self.rigidities)
            if self.rigidities
            else 0.0
        )

        return {
            "total_rigidities": len(self.rigidities),
            "rigidity_by_type": rigidity_counts,
            "average_severity": avg_severity,
            "lines_of_flight": len(self.lines_of_flight),
            "high_priority_rigidities": sum(
                None
            ),
        }

    def xǁDeterritorializationEngineǁget_stats__mutmut_26(self) -> Dict[str, Any]:
        """Get statistics about detected rigidities and lines of flight."""
        rigidity_counts = {}
        for rigidity in self.rigidities:
            rtype = rigidity.rigidity_type.value
            rigidity_counts[rtype] = rigidity_counts.get(rtype, 0) + 1

        avg_severity = (
            sum(r.severity for r in self.rigidities) / len(self.rigidities)
            if self.rigidities
            else 0.0
        )

        return {
            "total_rigidities": len(self.rigidities),
            "rigidity_by_type": rigidity_counts,
            "average_severity": avg_severity,
            "lines_of_flight": len(self.lines_of_flight),
            "high_priority_rigidities": sum(
                2 for r in self.rigidities if r.severity >= 0.7
            ),
        }

    def xǁDeterritorializationEngineǁget_stats__mutmut_27(self) -> Dict[str, Any]:
        """Get statistics about detected rigidities and lines of flight."""
        rigidity_counts = {}
        for rigidity in self.rigidities:
            rtype = rigidity.rigidity_type.value
            rigidity_counts[rtype] = rigidity_counts.get(rtype, 0) + 1

        avg_severity = (
            sum(r.severity for r in self.rigidities) / len(self.rigidities)
            if self.rigidities
            else 0.0
        )

        return {
            "total_rigidities": len(self.rigidities),
            "rigidity_by_type": rigidity_counts,
            "average_severity": avg_severity,
            "lines_of_flight": len(self.lines_of_flight),
            "high_priority_rigidities": sum(
                1 for r in self.rigidities if r.severity > 0.7
            ),
        }

    def xǁDeterritorializationEngineǁget_stats__mutmut_28(self) -> Dict[str, Any]:
        """Get statistics about detected rigidities and lines of flight."""
        rigidity_counts = {}
        for rigidity in self.rigidities:
            rtype = rigidity.rigidity_type.value
            rigidity_counts[rtype] = rigidity_counts.get(rtype, 0) + 1

        avg_severity = (
            sum(r.severity for r in self.rigidities) / len(self.rigidities)
            if self.rigidities
            else 0.0
        )

        return {
            "total_rigidities": len(self.rigidities),
            "rigidity_by_type": rigidity_counts,
            "average_severity": avg_severity,
            "lines_of_flight": len(self.lines_of_flight),
            "high_priority_rigidities": sum(
                1 for r in self.rigidities if r.severity >= 1.7
            ),
        }
    
    xǁDeterritorializationEngineǁget_stats__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDeterritorializationEngineǁget_stats__mutmut_1': xǁDeterritorializationEngineǁget_stats__mutmut_1, 
        'xǁDeterritorializationEngineǁget_stats__mutmut_2': xǁDeterritorializationEngineǁget_stats__mutmut_2, 
        'xǁDeterritorializationEngineǁget_stats__mutmut_3': xǁDeterritorializationEngineǁget_stats__mutmut_3, 
        'xǁDeterritorializationEngineǁget_stats__mutmut_4': xǁDeterritorializationEngineǁget_stats__mutmut_4, 
        'xǁDeterritorializationEngineǁget_stats__mutmut_5': xǁDeterritorializationEngineǁget_stats__mutmut_5, 
        'xǁDeterritorializationEngineǁget_stats__mutmut_6': xǁDeterritorializationEngineǁget_stats__mutmut_6, 
        'xǁDeterritorializationEngineǁget_stats__mutmut_7': xǁDeterritorializationEngineǁget_stats__mutmut_7, 
        'xǁDeterritorializationEngineǁget_stats__mutmut_8': xǁDeterritorializationEngineǁget_stats__mutmut_8, 
        'xǁDeterritorializationEngineǁget_stats__mutmut_9': xǁDeterritorializationEngineǁget_stats__mutmut_9, 
        'xǁDeterritorializationEngineǁget_stats__mutmut_10': xǁDeterritorializationEngineǁget_stats__mutmut_10, 
        'xǁDeterritorializationEngineǁget_stats__mutmut_11': xǁDeterritorializationEngineǁget_stats__mutmut_11, 
        'xǁDeterritorializationEngineǁget_stats__mutmut_12': xǁDeterritorializationEngineǁget_stats__mutmut_12, 
        'xǁDeterritorializationEngineǁget_stats__mutmut_13': xǁDeterritorializationEngineǁget_stats__mutmut_13, 
        'xǁDeterritorializationEngineǁget_stats__mutmut_14': xǁDeterritorializationEngineǁget_stats__mutmut_14, 
        'xǁDeterritorializationEngineǁget_stats__mutmut_15': xǁDeterritorializationEngineǁget_stats__mutmut_15, 
        'xǁDeterritorializationEngineǁget_stats__mutmut_16': xǁDeterritorializationEngineǁget_stats__mutmut_16, 
        'xǁDeterritorializationEngineǁget_stats__mutmut_17': xǁDeterritorializationEngineǁget_stats__mutmut_17, 
        'xǁDeterritorializationEngineǁget_stats__mutmut_18': xǁDeterritorializationEngineǁget_stats__mutmut_18, 
        'xǁDeterritorializationEngineǁget_stats__mutmut_19': xǁDeterritorializationEngineǁget_stats__mutmut_19, 
        'xǁDeterritorializationEngineǁget_stats__mutmut_20': xǁDeterritorializationEngineǁget_stats__mutmut_20, 
        'xǁDeterritorializationEngineǁget_stats__mutmut_21': xǁDeterritorializationEngineǁget_stats__mutmut_21, 
        'xǁDeterritorializationEngineǁget_stats__mutmut_22': xǁDeterritorializationEngineǁget_stats__mutmut_22, 
        'xǁDeterritorializationEngineǁget_stats__mutmut_23': xǁDeterritorializationEngineǁget_stats__mutmut_23, 
        'xǁDeterritorializationEngineǁget_stats__mutmut_24': xǁDeterritorializationEngineǁget_stats__mutmut_24, 
        'xǁDeterritorializationEngineǁget_stats__mutmut_25': xǁDeterritorializationEngineǁget_stats__mutmut_25, 
        'xǁDeterritorializationEngineǁget_stats__mutmut_26': xǁDeterritorializationEngineǁget_stats__mutmut_26, 
        'xǁDeterritorializationEngineǁget_stats__mutmut_27': xǁDeterritorializationEngineǁget_stats__mutmut_27, 
        'xǁDeterritorializationEngineǁget_stats__mutmut_28': xǁDeterritorializationEngineǁget_stats__mutmut_28
    }
    
    def get_stats(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDeterritorializationEngineǁget_stats__mutmut_orig"), object.__getattribute__(self, "xǁDeterritorializationEngineǁget_stats__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_stats.__signature__ = _mutmut_signature(xǁDeterritorializationEngineǁget_stats__mutmut_orig)
    xǁDeterritorializationEngineǁget_stats__mutmut_orig.__name__ = 'xǁDeterritorializationEngineǁget_stats'

    def xǁDeterritorializationEngineǁexport_report__mutmut_orig(self) -> Dict[str, Any]:
        """
        Export a comprehensive deterritorialization report.

        Returns:
            Dictionary with rigidities, lines of flight, and recommendations
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rigidities": [
                {
                    "type": r.rigidity_type.value,
                    "file": r.file_path,
                    "line": r.line_number,
                    "severity": r.severity,
                    "description": r.description,
                }
                for r in self.rigidities
            ],
            "lines_of_flight": [
                {
                    "rigidity_type": lof.rigidity.rigidity_type.value,
                    "action": lof.proposed_action,
                    "outcome": lof.expected_outcome,
                    "innovation_potential": lof.innovation_potential,
                    "risk_level": lof.risk_level,
                }
                for lof in self.lines_of_flight
            ],
            "stats": self.get_stats(),
        }

    def xǁDeterritorializationEngineǁexport_report__mutmut_1(self) -> Dict[str, Any]:
        """
        Export a comprehensive deterritorialization report.

        Returns:
            Dictionary with rigidities, lines of flight, and recommendations
        """
        return {
            "XXtimestampXX": datetime.now(timezone.utc).isoformat(),
            "rigidities": [
                {
                    "type": r.rigidity_type.value,
                    "file": r.file_path,
                    "line": r.line_number,
                    "severity": r.severity,
                    "description": r.description,
                }
                for r in self.rigidities
            ],
            "lines_of_flight": [
                {
                    "rigidity_type": lof.rigidity.rigidity_type.value,
                    "action": lof.proposed_action,
                    "outcome": lof.expected_outcome,
                    "innovation_potential": lof.innovation_potential,
                    "risk_level": lof.risk_level,
                }
                for lof in self.lines_of_flight
            ],
            "stats": self.get_stats(),
        }

    def xǁDeterritorializationEngineǁexport_report__mutmut_2(self) -> Dict[str, Any]:
        """
        Export a comprehensive deterritorialization report.

        Returns:
            Dictionary with rigidities, lines of flight, and recommendations
        """
        return {
            "TIMESTAMP": datetime.now(timezone.utc).isoformat(),
            "rigidities": [
                {
                    "type": r.rigidity_type.value,
                    "file": r.file_path,
                    "line": r.line_number,
                    "severity": r.severity,
                    "description": r.description,
                }
                for r in self.rigidities
            ],
            "lines_of_flight": [
                {
                    "rigidity_type": lof.rigidity.rigidity_type.value,
                    "action": lof.proposed_action,
                    "outcome": lof.expected_outcome,
                    "innovation_potential": lof.innovation_potential,
                    "risk_level": lof.risk_level,
                }
                for lof in self.lines_of_flight
            ],
            "stats": self.get_stats(),
        }

    def xǁDeterritorializationEngineǁexport_report__mutmut_3(self) -> Dict[str, Any]:
        """
        Export a comprehensive deterritorialization report.

        Returns:
            Dictionary with rigidities, lines of flight, and recommendations
        """
        return {
            "timestamp": datetime.now(None).isoformat(),
            "rigidities": [
                {
                    "type": r.rigidity_type.value,
                    "file": r.file_path,
                    "line": r.line_number,
                    "severity": r.severity,
                    "description": r.description,
                }
                for r in self.rigidities
            ],
            "lines_of_flight": [
                {
                    "rigidity_type": lof.rigidity.rigidity_type.value,
                    "action": lof.proposed_action,
                    "outcome": lof.expected_outcome,
                    "innovation_potential": lof.innovation_potential,
                    "risk_level": lof.risk_level,
                }
                for lof in self.lines_of_flight
            ],
            "stats": self.get_stats(),
        }

    def xǁDeterritorializationEngineǁexport_report__mutmut_4(self) -> Dict[str, Any]:
        """
        Export a comprehensive deterritorialization report.

        Returns:
            Dictionary with rigidities, lines of flight, and recommendations
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "XXrigiditiesXX": [
                {
                    "type": r.rigidity_type.value,
                    "file": r.file_path,
                    "line": r.line_number,
                    "severity": r.severity,
                    "description": r.description,
                }
                for r in self.rigidities
            ],
            "lines_of_flight": [
                {
                    "rigidity_type": lof.rigidity.rigidity_type.value,
                    "action": lof.proposed_action,
                    "outcome": lof.expected_outcome,
                    "innovation_potential": lof.innovation_potential,
                    "risk_level": lof.risk_level,
                }
                for lof in self.lines_of_flight
            ],
            "stats": self.get_stats(),
        }

    def xǁDeterritorializationEngineǁexport_report__mutmut_5(self) -> Dict[str, Any]:
        """
        Export a comprehensive deterritorialization report.

        Returns:
            Dictionary with rigidities, lines of flight, and recommendations
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "RIGIDITIES": [
                {
                    "type": r.rigidity_type.value,
                    "file": r.file_path,
                    "line": r.line_number,
                    "severity": r.severity,
                    "description": r.description,
                }
                for r in self.rigidities
            ],
            "lines_of_flight": [
                {
                    "rigidity_type": lof.rigidity.rigidity_type.value,
                    "action": lof.proposed_action,
                    "outcome": lof.expected_outcome,
                    "innovation_potential": lof.innovation_potential,
                    "risk_level": lof.risk_level,
                }
                for lof in self.lines_of_flight
            ],
            "stats": self.get_stats(),
        }

    def xǁDeterritorializationEngineǁexport_report__mutmut_6(self) -> Dict[str, Any]:
        """
        Export a comprehensive deterritorialization report.

        Returns:
            Dictionary with rigidities, lines of flight, and recommendations
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rigidities": [
                {
                    "XXtypeXX": r.rigidity_type.value,
                    "file": r.file_path,
                    "line": r.line_number,
                    "severity": r.severity,
                    "description": r.description,
                }
                for r in self.rigidities
            ],
            "lines_of_flight": [
                {
                    "rigidity_type": lof.rigidity.rigidity_type.value,
                    "action": lof.proposed_action,
                    "outcome": lof.expected_outcome,
                    "innovation_potential": lof.innovation_potential,
                    "risk_level": lof.risk_level,
                }
                for lof in self.lines_of_flight
            ],
            "stats": self.get_stats(),
        }

    def xǁDeterritorializationEngineǁexport_report__mutmut_7(self) -> Dict[str, Any]:
        """
        Export a comprehensive deterritorialization report.

        Returns:
            Dictionary with rigidities, lines of flight, and recommendations
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rigidities": [
                {
                    "TYPE": r.rigidity_type.value,
                    "file": r.file_path,
                    "line": r.line_number,
                    "severity": r.severity,
                    "description": r.description,
                }
                for r in self.rigidities
            ],
            "lines_of_flight": [
                {
                    "rigidity_type": lof.rigidity.rigidity_type.value,
                    "action": lof.proposed_action,
                    "outcome": lof.expected_outcome,
                    "innovation_potential": lof.innovation_potential,
                    "risk_level": lof.risk_level,
                }
                for lof in self.lines_of_flight
            ],
            "stats": self.get_stats(),
        }

    def xǁDeterritorializationEngineǁexport_report__mutmut_8(self) -> Dict[str, Any]:
        """
        Export a comprehensive deterritorialization report.

        Returns:
            Dictionary with rigidities, lines of flight, and recommendations
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rigidities": [
                {
                    "type": r.rigidity_type.value,
                    "XXfileXX": r.file_path,
                    "line": r.line_number,
                    "severity": r.severity,
                    "description": r.description,
                }
                for r in self.rigidities
            ],
            "lines_of_flight": [
                {
                    "rigidity_type": lof.rigidity.rigidity_type.value,
                    "action": lof.proposed_action,
                    "outcome": lof.expected_outcome,
                    "innovation_potential": lof.innovation_potential,
                    "risk_level": lof.risk_level,
                }
                for lof in self.lines_of_flight
            ],
            "stats": self.get_stats(),
        }

    def xǁDeterritorializationEngineǁexport_report__mutmut_9(self) -> Dict[str, Any]:
        """
        Export a comprehensive deterritorialization report.

        Returns:
            Dictionary with rigidities, lines of flight, and recommendations
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rigidities": [
                {
                    "type": r.rigidity_type.value,
                    "FILE": r.file_path,
                    "line": r.line_number,
                    "severity": r.severity,
                    "description": r.description,
                }
                for r in self.rigidities
            ],
            "lines_of_flight": [
                {
                    "rigidity_type": lof.rigidity.rigidity_type.value,
                    "action": lof.proposed_action,
                    "outcome": lof.expected_outcome,
                    "innovation_potential": lof.innovation_potential,
                    "risk_level": lof.risk_level,
                }
                for lof in self.lines_of_flight
            ],
            "stats": self.get_stats(),
        }

    def xǁDeterritorializationEngineǁexport_report__mutmut_10(self) -> Dict[str, Any]:
        """
        Export a comprehensive deterritorialization report.

        Returns:
            Dictionary with rigidities, lines of flight, and recommendations
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rigidities": [
                {
                    "type": r.rigidity_type.value,
                    "file": r.file_path,
                    "XXlineXX": r.line_number,
                    "severity": r.severity,
                    "description": r.description,
                }
                for r in self.rigidities
            ],
            "lines_of_flight": [
                {
                    "rigidity_type": lof.rigidity.rigidity_type.value,
                    "action": lof.proposed_action,
                    "outcome": lof.expected_outcome,
                    "innovation_potential": lof.innovation_potential,
                    "risk_level": lof.risk_level,
                }
                for lof in self.lines_of_flight
            ],
            "stats": self.get_stats(),
        }

    def xǁDeterritorializationEngineǁexport_report__mutmut_11(self) -> Dict[str, Any]:
        """
        Export a comprehensive deterritorialization report.

        Returns:
            Dictionary with rigidities, lines of flight, and recommendations
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rigidities": [
                {
                    "type": r.rigidity_type.value,
                    "file": r.file_path,
                    "LINE": r.line_number,
                    "severity": r.severity,
                    "description": r.description,
                }
                for r in self.rigidities
            ],
            "lines_of_flight": [
                {
                    "rigidity_type": lof.rigidity.rigidity_type.value,
                    "action": lof.proposed_action,
                    "outcome": lof.expected_outcome,
                    "innovation_potential": lof.innovation_potential,
                    "risk_level": lof.risk_level,
                }
                for lof in self.lines_of_flight
            ],
            "stats": self.get_stats(),
        }

    def xǁDeterritorializationEngineǁexport_report__mutmut_12(self) -> Dict[str, Any]:
        """
        Export a comprehensive deterritorialization report.

        Returns:
            Dictionary with rigidities, lines of flight, and recommendations
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rigidities": [
                {
                    "type": r.rigidity_type.value,
                    "file": r.file_path,
                    "line": r.line_number,
                    "XXseverityXX": r.severity,
                    "description": r.description,
                }
                for r in self.rigidities
            ],
            "lines_of_flight": [
                {
                    "rigidity_type": lof.rigidity.rigidity_type.value,
                    "action": lof.proposed_action,
                    "outcome": lof.expected_outcome,
                    "innovation_potential": lof.innovation_potential,
                    "risk_level": lof.risk_level,
                }
                for lof in self.lines_of_flight
            ],
            "stats": self.get_stats(),
        }

    def xǁDeterritorializationEngineǁexport_report__mutmut_13(self) -> Dict[str, Any]:
        """
        Export a comprehensive deterritorialization report.

        Returns:
            Dictionary with rigidities, lines of flight, and recommendations
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rigidities": [
                {
                    "type": r.rigidity_type.value,
                    "file": r.file_path,
                    "line": r.line_number,
                    "SEVERITY": r.severity,
                    "description": r.description,
                }
                for r in self.rigidities
            ],
            "lines_of_flight": [
                {
                    "rigidity_type": lof.rigidity.rigidity_type.value,
                    "action": lof.proposed_action,
                    "outcome": lof.expected_outcome,
                    "innovation_potential": lof.innovation_potential,
                    "risk_level": lof.risk_level,
                }
                for lof in self.lines_of_flight
            ],
            "stats": self.get_stats(),
        }

    def xǁDeterritorializationEngineǁexport_report__mutmut_14(self) -> Dict[str, Any]:
        """
        Export a comprehensive deterritorialization report.

        Returns:
            Dictionary with rigidities, lines of flight, and recommendations
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rigidities": [
                {
                    "type": r.rigidity_type.value,
                    "file": r.file_path,
                    "line": r.line_number,
                    "severity": r.severity,
                    "XXdescriptionXX": r.description,
                }
                for r in self.rigidities
            ],
            "lines_of_flight": [
                {
                    "rigidity_type": lof.rigidity.rigidity_type.value,
                    "action": lof.proposed_action,
                    "outcome": lof.expected_outcome,
                    "innovation_potential": lof.innovation_potential,
                    "risk_level": lof.risk_level,
                }
                for lof in self.lines_of_flight
            ],
            "stats": self.get_stats(),
        }

    def xǁDeterritorializationEngineǁexport_report__mutmut_15(self) -> Dict[str, Any]:
        """
        Export a comprehensive deterritorialization report.

        Returns:
            Dictionary with rigidities, lines of flight, and recommendations
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rigidities": [
                {
                    "type": r.rigidity_type.value,
                    "file": r.file_path,
                    "line": r.line_number,
                    "severity": r.severity,
                    "DESCRIPTION": r.description,
                }
                for r in self.rigidities
            ],
            "lines_of_flight": [
                {
                    "rigidity_type": lof.rigidity.rigidity_type.value,
                    "action": lof.proposed_action,
                    "outcome": lof.expected_outcome,
                    "innovation_potential": lof.innovation_potential,
                    "risk_level": lof.risk_level,
                }
                for lof in self.lines_of_flight
            ],
            "stats": self.get_stats(),
        }

    def xǁDeterritorializationEngineǁexport_report__mutmut_16(self) -> Dict[str, Any]:
        """
        Export a comprehensive deterritorialization report.

        Returns:
            Dictionary with rigidities, lines of flight, and recommendations
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rigidities": [
                {
                    "type": r.rigidity_type.value,
                    "file": r.file_path,
                    "line": r.line_number,
                    "severity": r.severity,
                    "description": r.description,
                }
                for r in self.rigidities
            ],
            "XXlines_of_flightXX": [
                {
                    "rigidity_type": lof.rigidity.rigidity_type.value,
                    "action": lof.proposed_action,
                    "outcome": lof.expected_outcome,
                    "innovation_potential": lof.innovation_potential,
                    "risk_level": lof.risk_level,
                }
                for lof in self.lines_of_flight
            ],
            "stats": self.get_stats(),
        }

    def xǁDeterritorializationEngineǁexport_report__mutmut_17(self) -> Dict[str, Any]:
        """
        Export a comprehensive deterritorialization report.

        Returns:
            Dictionary with rigidities, lines of flight, and recommendations
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rigidities": [
                {
                    "type": r.rigidity_type.value,
                    "file": r.file_path,
                    "line": r.line_number,
                    "severity": r.severity,
                    "description": r.description,
                }
                for r in self.rigidities
            ],
            "LINES_OF_FLIGHT": [
                {
                    "rigidity_type": lof.rigidity.rigidity_type.value,
                    "action": lof.proposed_action,
                    "outcome": lof.expected_outcome,
                    "innovation_potential": lof.innovation_potential,
                    "risk_level": lof.risk_level,
                }
                for lof in self.lines_of_flight
            ],
            "stats": self.get_stats(),
        }

    def xǁDeterritorializationEngineǁexport_report__mutmut_18(self) -> Dict[str, Any]:
        """
        Export a comprehensive deterritorialization report.

        Returns:
            Dictionary with rigidities, lines of flight, and recommendations
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rigidities": [
                {
                    "type": r.rigidity_type.value,
                    "file": r.file_path,
                    "line": r.line_number,
                    "severity": r.severity,
                    "description": r.description,
                }
                for r in self.rigidities
            ],
            "lines_of_flight": [
                {
                    "XXrigidity_typeXX": lof.rigidity.rigidity_type.value,
                    "action": lof.proposed_action,
                    "outcome": lof.expected_outcome,
                    "innovation_potential": lof.innovation_potential,
                    "risk_level": lof.risk_level,
                }
                for lof in self.lines_of_flight
            ],
            "stats": self.get_stats(),
        }

    def xǁDeterritorializationEngineǁexport_report__mutmut_19(self) -> Dict[str, Any]:
        """
        Export a comprehensive deterritorialization report.

        Returns:
            Dictionary with rigidities, lines of flight, and recommendations
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rigidities": [
                {
                    "type": r.rigidity_type.value,
                    "file": r.file_path,
                    "line": r.line_number,
                    "severity": r.severity,
                    "description": r.description,
                }
                for r in self.rigidities
            ],
            "lines_of_flight": [
                {
                    "RIGIDITY_TYPE": lof.rigidity.rigidity_type.value,
                    "action": lof.proposed_action,
                    "outcome": lof.expected_outcome,
                    "innovation_potential": lof.innovation_potential,
                    "risk_level": lof.risk_level,
                }
                for lof in self.lines_of_flight
            ],
            "stats": self.get_stats(),
        }

    def xǁDeterritorializationEngineǁexport_report__mutmut_20(self) -> Dict[str, Any]:
        """
        Export a comprehensive deterritorialization report.

        Returns:
            Dictionary with rigidities, lines of flight, and recommendations
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rigidities": [
                {
                    "type": r.rigidity_type.value,
                    "file": r.file_path,
                    "line": r.line_number,
                    "severity": r.severity,
                    "description": r.description,
                }
                for r in self.rigidities
            ],
            "lines_of_flight": [
                {
                    "rigidity_type": lof.rigidity.rigidity_type.value,
                    "XXactionXX": lof.proposed_action,
                    "outcome": lof.expected_outcome,
                    "innovation_potential": lof.innovation_potential,
                    "risk_level": lof.risk_level,
                }
                for lof in self.lines_of_flight
            ],
            "stats": self.get_stats(),
        }

    def xǁDeterritorializationEngineǁexport_report__mutmut_21(self) -> Dict[str, Any]:
        """
        Export a comprehensive deterritorialization report.

        Returns:
            Dictionary with rigidities, lines of flight, and recommendations
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rigidities": [
                {
                    "type": r.rigidity_type.value,
                    "file": r.file_path,
                    "line": r.line_number,
                    "severity": r.severity,
                    "description": r.description,
                }
                for r in self.rigidities
            ],
            "lines_of_flight": [
                {
                    "rigidity_type": lof.rigidity.rigidity_type.value,
                    "ACTION": lof.proposed_action,
                    "outcome": lof.expected_outcome,
                    "innovation_potential": lof.innovation_potential,
                    "risk_level": lof.risk_level,
                }
                for lof in self.lines_of_flight
            ],
            "stats": self.get_stats(),
        }

    def xǁDeterritorializationEngineǁexport_report__mutmut_22(self) -> Dict[str, Any]:
        """
        Export a comprehensive deterritorialization report.

        Returns:
            Dictionary with rigidities, lines of flight, and recommendations
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rigidities": [
                {
                    "type": r.rigidity_type.value,
                    "file": r.file_path,
                    "line": r.line_number,
                    "severity": r.severity,
                    "description": r.description,
                }
                for r in self.rigidities
            ],
            "lines_of_flight": [
                {
                    "rigidity_type": lof.rigidity.rigidity_type.value,
                    "action": lof.proposed_action,
                    "XXoutcomeXX": lof.expected_outcome,
                    "innovation_potential": lof.innovation_potential,
                    "risk_level": lof.risk_level,
                }
                for lof in self.lines_of_flight
            ],
            "stats": self.get_stats(),
        }

    def xǁDeterritorializationEngineǁexport_report__mutmut_23(self) -> Dict[str, Any]:
        """
        Export a comprehensive deterritorialization report.

        Returns:
            Dictionary with rigidities, lines of flight, and recommendations
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rigidities": [
                {
                    "type": r.rigidity_type.value,
                    "file": r.file_path,
                    "line": r.line_number,
                    "severity": r.severity,
                    "description": r.description,
                }
                for r in self.rigidities
            ],
            "lines_of_flight": [
                {
                    "rigidity_type": lof.rigidity.rigidity_type.value,
                    "action": lof.proposed_action,
                    "OUTCOME": lof.expected_outcome,
                    "innovation_potential": lof.innovation_potential,
                    "risk_level": lof.risk_level,
                }
                for lof in self.lines_of_flight
            ],
            "stats": self.get_stats(),
        }

    def xǁDeterritorializationEngineǁexport_report__mutmut_24(self) -> Dict[str, Any]:
        """
        Export a comprehensive deterritorialization report.

        Returns:
            Dictionary with rigidities, lines of flight, and recommendations
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rigidities": [
                {
                    "type": r.rigidity_type.value,
                    "file": r.file_path,
                    "line": r.line_number,
                    "severity": r.severity,
                    "description": r.description,
                }
                for r in self.rigidities
            ],
            "lines_of_flight": [
                {
                    "rigidity_type": lof.rigidity.rigidity_type.value,
                    "action": lof.proposed_action,
                    "outcome": lof.expected_outcome,
                    "XXinnovation_potentialXX": lof.innovation_potential,
                    "risk_level": lof.risk_level,
                }
                for lof in self.lines_of_flight
            ],
            "stats": self.get_stats(),
        }

    def xǁDeterritorializationEngineǁexport_report__mutmut_25(self) -> Dict[str, Any]:
        """
        Export a comprehensive deterritorialization report.

        Returns:
            Dictionary with rigidities, lines of flight, and recommendations
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rigidities": [
                {
                    "type": r.rigidity_type.value,
                    "file": r.file_path,
                    "line": r.line_number,
                    "severity": r.severity,
                    "description": r.description,
                }
                for r in self.rigidities
            ],
            "lines_of_flight": [
                {
                    "rigidity_type": lof.rigidity.rigidity_type.value,
                    "action": lof.proposed_action,
                    "outcome": lof.expected_outcome,
                    "INNOVATION_POTENTIAL": lof.innovation_potential,
                    "risk_level": lof.risk_level,
                }
                for lof in self.lines_of_flight
            ],
            "stats": self.get_stats(),
        }

    def xǁDeterritorializationEngineǁexport_report__mutmut_26(self) -> Dict[str, Any]:
        """
        Export a comprehensive deterritorialization report.

        Returns:
            Dictionary with rigidities, lines of flight, and recommendations
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rigidities": [
                {
                    "type": r.rigidity_type.value,
                    "file": r.file_path,
                    "line": r.line_number,
                    "severity": r.severity,
                    "description": r.description,
                }
                for r in self.rigidities
            ],
            "lines_of_flight": [
                {
                    "rigidity_type": lof.rigidity.rigidity_type.value,
                    "action": lof.proposed_action,
                    "outcome": lof.expected_outcome,
                    "innovation_potential": lof.innovation_potential,
                    "XXrisk_levelXX": lof.risk_level,
                }
                for lof in self.lines_of_flight
            ],
            "stats": self.get_stats(),
        }

    def xǁDeterritorializationEngineǁexport_report__mutmut_27(self) -> Dict[str, Any]:
        """
        Export a comprehensive deterritorialization report.

        Returns:
            Dictionary with rigidities, lines of flight, and recommendations
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rigidities": [
                {
                    "type": r.rigidity_type.value,
                    "file": r.file_path,
                    "line": r.line_number,
                    "severity": r.severity,
                    "description": r.description,
                }
                for r in self.rigidities
            ],
            "lines_of_flight": [
                {
                    "rigidity_type": lof.rigidity.rigidity_type.value,
                    "action": lof.proposed_action,
                    "outcome": lof.expected_outcome,
                    "innovation_potential": lof.innovation_potential,
                    "RISK_LEVEL": lof.risk_level,
                }
                for lof in self.lines_of_flight
            ],
            "stats": self.get_stats(),
        }

    def xǁDeterritorializationEngineǁexport_report__mutmut_28(self) -> Dict[str, Any]:
        """
        Export a comprehensive deterritorialization report.

        Returns:
            Dictionary with rigidities, lines of flight, and recommendations
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rigidities": [
                {
                    "type": r.rigidity_type.value,
                    "file": r.file_path,
                    "line": r.line_number,
                    "severity": r.severity,
                    "description": r.description,
                }
                for r in self.rigidities
            ],
            "lines_of_flight": [
                {
                    "rigidity_type": lof.rigidity.rigidity_type.value,
                    "action": lof.proposed_action,
                    "outcome": lof.expected_outcome,
                    "innovation_potential": lof.innovation_potential,
                    "risk_level": lof.risk_level,
                }
                for lof in self.lines_of_flight
            ],
            "XXstatsXX": self.get_stats(),
        }

    def xǁDeterritorializationEngineǁexport_report__mutmut_29(self) -> Dict[str, Any]:
        """
        Export a comprehensive deterritorialization report.

        Returns:
            Dictionary with rigidities, lines of flight, and recommendations
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rigidities": [
                {
                    "type": r.rigidity_type.value,
                    "file": r.file_path,
                    "line": r.line_number,
                    "severity": r.severity,
                    "description": r.description,
                }
                for r in self.rigidities
            ],
            "lines_of_flight": [
                {
                    "rigidity_type": lof.rigidity.rigidity_type.value,
                    "action": lof.proposed_action,
                    "outcome": lof.expected_outcome,
                    "innovation_potential": lof.innovation_potential,
                    "risk_level": lof.risk_level,
                }
                for lof in self.lines_of_flight
            ],
            "STATS": self.get_stats(),
        }
    
    xǁDeterritorializationEngineǁexport_report__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDeterritorializationEngineǁexport_report__mutmut_1': xǁDeterritorializationEngineǁexport_report__mutmut_1, 
        'xǁDeterritorializationEngineǁexport_report__mutmut_2': xǁDeterritorializationEngineǁexport_report__mutmut_2, 
        'xǁDeterritorializationEngineǁexport_report__mutmut_3': xǁDeterritorializationEngineǁexport_report__mutmut_3, 
        'xǁDeterritorializationEngineǁexport_report__mutmut_4': xǁDeterritorializationEngineǁexport_report__mutmut_4, 
        'xǁDeterritorializationEngineǁexport_report__mutmut_5': xǁDeterritorializationEngineǁexport_report__mutmut_5, 
        'xǁDeterritorializationEngineǁexport_report__mutmut_6': xǁDeterritorializationEngineǁexport_report__mutmut_6, 
        'xǁDeterritorializationEngineǁexport_report__mutmut_7': xǁDeterritorializationEngineǁexport_report__mutmut_7, 
        'xǁDeterritorializationEngineǁexport_report__mutmut_8': xǁDeterritorializationEngineǁexport_report__mutmut_8, 
        'xǁDeterritorializationEngineǁexport_report__mutmut_9': xǁDeterritorializationEngineǁexport_report__mutmut_9, 
        'xǁDeterritorializationEngineǁexport_report__mutmut_10': xǁDeterritorializationEngineǁexport_report__mutmut_10, 
        'xǁDeterritorializationEngineǁexport_report__mutmut_11': xǁDeterritorializationEngineǁexport_report__mutmut_11, 
        'xǁDeterritorializationEngineǁexport_report__mutmut_12': xǁDeterritorializationEngineǁexport_report__mutmut_12, 
        'xǁDeterritorializationEngineǁexport_report__mutmut_13': xǁDeterritorializationEngineǁexport_report__mutmut_13, 
        'xǁDeterritorializationEngineǁexport_report__mutmut_14': xǁDeterritorializationEngineǁexport_report__mutmut_14, 
        'xǁDeterritorializationEngineǁexport_report__mutmut_15': xǁDeterritorializationEngineǁexport_report__mutmut_15, 
        'xǁDeterritorializationEngineǁexport_report__mutmut_16': xǁDeterritorializationEngineǁexport_report__mutmut_16, 
        'xǁDeterritorializationEngineǁexport_report__mutmut_17': xǁDeterritorializationEngineǁexport_report__mutmut_17, 
        'xǁDeterritorializationEngineǁexport_report__mutmut_18': xǁDeterritorializationEngineǁexport_report__mutmut_18, 
        'xǁDeterritorializationEngineǁexport_report__mutmut_19': xǁDeterritorializationEngineǁexport_report__mutmut_19, 
        'xǁDeterritorializationEngineǁexport_report__mutmut_20': xǁDeterritorializationEngineǁexport_report__mutmut_20, 
        'xǁDeterritorializationEngineǁexport_report__mutmut_21': xǁDeterritorializationEngineǁexport_report__mutmut_21, 
        'xǁDeterritorializationEngineǁexport_report__mutmut_22': xǁDeterritorializationEngineǁexport_report__mutmut_22, 
        'xǁDeterritorializationEngineǁexport_report__mutmut_23': xǁDeterritorializationEngineǁexport_report__mutmut_23, 
        'xǁDeterritorializationEngineǁexport_report__mutmut_24': xǁDeterritorializationEngineǁexport_report__mutmut_24, 
        'xǁDeterritorializationEngineǁexport_report__mutmut_25': xǁDeterritorializationEngineǁexport_report__mutmut_25, 
        'xǁDeterritorializationEngineǁexport_report__mutmut_26': xǁDeterritorializationEngineǁexport_report__mutmut_26, 
        'xǁDeterritorializationEngineǁexport_report__mutmut_27': xǁDeterritorializationEngineǁexport_report__mutmut_27, 
        'xǁDeterritorializationEngineǁexport_report__mutmut_28': xǁDeterritorializationEngineǁexport_report__mutmut_28, 
        'xǁDeterritorializationEngineǁexport_report__mutmut_29': xǁDeterritorializationEngineǁexport_report__mutmut_29
    }
    
    def export_report(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDeterritorializationEngineǁexport_report__mutmut_orig"), object.__getattribute__(self, "xǁDeterritorializationEngineǁexport_report__mutmut_mutants"), args, kwargs, self)
        return result 
    
    export_report.__signature__ = _mutmut_signature(xǁDeterritorializationEngineǁexport_report__mutmut_orig)
    xǁDeterritorializationEngineǁexport_report__mutmut_orig.__name__ = 'xǁDeterritorializationEngineǁexport_report'
