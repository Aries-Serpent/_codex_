"""Workflow inventory management.

Scans .github/workflows directory, parses workflow files, and builds
a dependency graph. Supports caching and incremental updates.
"""

import logging
from pathlib import Path
from typing import Optional

from .parser import WorkflowParser
from .types import (
    InventoryStats,
    TriggerType,
    WorkflowDependency,
    WorkflowMetadata,
)

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


class WorkflowInventory:
    """Manages inventory of GitHub Actions workflows.

    Features:
    - Scans .github/workflows directory
    - Parses workflow YAML files
    - Builds dependency graph between workflows
    - Caches parsed results
    - Supports incremental updates

    Example:
        ```python
        inventory = WorkflowInventory(".github/workflows")
        inventory.scan()

        print(f"Found {len(inventory.workflows)} workflows")
        print(f"Triggerable: {len(inventory.get_triggerable())}")

        # Get specific workflow
        workflow = inventory.get_workflow("test-suite.yml")
        if workflow:
            print(f"Jobs: {workflow.job_ids}")
        ```
    """

    def xǁWorkflowInventoryǁ__init____mutmut_orig(self, workflows_dir: Path | str):
        """Initialize workflow inventory. 

        Args:
            workflows_dir: Path to .github/workflows directory.
        """
        self.workflows_dir = Path(workflows_dir)
        self.parser = WorkflowParser()
        self._workflows: dict[str, WorkflowMetadata] = {}
        self._dependencies: list[WorkflowDependency] = []

    def xǁWorkflowInventoryǁ__init____mutmut_1(self, workflows_dir: Path | str):
        """Initialize workflow inventory. 

        Args:
            workflows_dir: Path to .github/workflows directory.
        """
        self.workflows_dir = None
        self.parser = WorkflowParser()
        self._workflows: dict[str, WorkflowMetadata] = {}
        self._dependencies: list[WorkflowDependency] = []

    def xǁWorkflowInventoryǁ__init____mutmut_2(self, workflows_dir: Path | str):
        """Initialize workflow inventory. 

        Args:
            workflows_dir: Path to .github/workflows directory.
        """
        self.workflows_dir = Path(None)
        self.parser = WorkflowParser()
        self._workflows: dict[str, WorkflowMetadata] = {}
        self._dependencies: list[WorkflowDependency] = []

    def xǁWorkflowInventoryǁ__init____mutmut_3(self, workflows_dir: Path | str):
        """Initialize workflow inventory. 

        Args:
            workflows_dir: Path to .github/workflows directory.
        """
        self.workflows_dir = Path(workflows_dir)
        self.parser = None
        self._workflows: dict[str, WorkflowMetadata] = {}
        self._dependencies: list[WorkflowDependency] = []

    def xǁWorkflowInventoryǁ__init____mutmut_4(self, workflows_dir: Path | str):
        """Initialize workflow inventory. 

        Args:
            workflows_dir: Path to .github/workflows directory.
        """
        self.workflows_dir = Path(workflows_dir)
        self.parser = WorkflowParser()
        self._workflows: dict[str, WorkflowMetadata] = None
        self._dependencies: list[WorkflowDependency] = []

    def xǁWorkflowInventoryǁ__init____mutmut_5(self, workflows_dir: Path | str):
        """Initialize workflow inventory. 

        Args:
            workflows_dir: Path to .github/workflows directory.
        """
        self.workflows_dir = Path(workflows_dir)
        self.parser = WorkflowParser()
        self._workflows: dict[str, WorkflowMetadata] = {}
        self._dependencies: list[WorkflowDependency] = None
    
    xǁWorkflowInventoryǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁWorkflowInventoryǁ__init____mutmut_1': xǁWorkflowInventoryǁ__init____mutmut_1, 
        'xǁWorkflowInventoryǁ__init____mutmut_2': xǁWorkflowInventoryǁ__init____mutmut_2, 
        'xǁWorkflowInventoryǁ__init____mutmut_3': xǁWorkflowInventoryǁ__init____mutmut_3, 
        'xǁWorkflowInventoryǁ__init____mutmut_4': xǁWorkflowInventoryǁ__init____mutmut_4, 
        'xǁWorkflowInventoryǁ__init____mutmut_5': xǁWorkflowInventoryǁ__init____mutmut_5
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁWorkflowInventoryǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁWorkflowInventoryǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁWorkflowInventoryǁ__init____mutmut_orig)
    xǁWorkflowInventoryǁ__init____mutmut_orig.__name__ = 'xǁWorkflowInventoryǁ__init__'

    @property
    def workflows(self) -> dict[str, WorkflowMetadata]:
        """Get all parsed workflows."""
        return self._workflows

    @property
    def dependencies(self) -> list[WorkflowDependency]:
        """Get all workflow dependencies."""
        return self._dependencies

    def xǁWorkflowInventoryǁscan__mutmut_orig(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_1(self, force_refresh: bool = True) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_2(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_3(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(None)
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_4(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 1

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_5(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = None
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_6(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 1
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_7(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = None

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_8(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.yml")) - list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_9(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(None) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_10(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob(None)) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_11(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("XX*.ymlXX")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_12(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.YML")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_13(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            None
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_14(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob(None)
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_15(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("XX*.yamlXX")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_16(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.YAML")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_17(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(None)

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_18(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" and ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_19(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix != ".disabled" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_20(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == "XX.disabledXX" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_21(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".DISABLED" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_22(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or "XX. disabledXX" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_23(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". DISABLED" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_24(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". disabled" not in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_25(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". disabled" in workflow_file.suffixes:
                logger.debug(None)
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_26(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                break

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_27(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = None
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_28(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(None)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_29(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = None
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_30(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count = 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_31(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count -= 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_32(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 2
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_33(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(None)
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_34(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(None)
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_35(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(None)
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_36(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(None)

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def xǁWorkflowInventoryǁscan__mutmut_37(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh: 
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows
            if workflow_file.suffix == ".disabled" or ". disabled" in workflow_file.suffixes:
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception as e: 
                logger.debug(f"Exception: {e}")
                logger.error(f"Error parsing {workflow_file.name}: {e}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            None
        )
        return parsed_count
    
    xǁWorkflowInventoryǁscan__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁWorkflowInventoryǁscan__mutmut_1': xǁWorkflowInventoryǁscan__mutmut_1, 
        'xǁWorkflowInventoryǁscan__mutmut_2': xǁWorkflowInventoryǁscan__mutmut_2, 
        'xǁWorkflowInventoryǁscan__mutmut_3': xǁWorkflowInventoryǁscan__mutmut_3, 
        'xǁWorkflowInventoryǁscan__mutmut_4': xǁWorkflowInventoryǁscan__mutmut_4, 
        'xǁWorkflowInventoryǁscan__mutmut_5': xǁWorkflowInventoryǁscan__mutmut_5, 
        'xǁWorkflowInventoryǁscan__mutmut_6': xǁWorkflowInventoryǁscan__mutmut_6, 
        'xǁWorkflowInventoryǁscan__mutmut_7': xǁWorkflowInventoryǁscan__mutmut_7, 
        'xǁWorkflowInventoryǁscan__mutmut_8': xǁWorkflowInventoryǁscan__mutmut_8, 
        'xǁWorkflowInventoryǁscan__mutmut_9': xǁWorkflowInventoryǁscan__mutmut_9, 
        'xǁWorkflowInventoryǁscan__mutmut_10': xǁWorkflowInventoryǁscan__mutmut_10, 
        'xǁWorkflowInventoryǁscan__mutmut_11': xǁWorkflowInventoryǁscan__mutmut_11, 
        'xǁWorkflowInventoryǁscan__mutmut_12': xǁWorkflowInventoryǁscan__mutmut_12, 
        'xǁWorkflowInventoryǁscan__mutmut_13': xǁWorkflowInventoryǁscan__mutmut_13, 
        'xǁWorkflowInventoryǁscan__mutmut_14': xǁWorkflowInventoryǁscan__mutmut_14, 
        'xǁWorkflowInventoryǁscan__mutmut_15': xǁWorkflowInventoryǁscan__mutmut_15, 
        'xǁWorkflowInventoryǁscan__mutmut_16': xǁWorkflowInventoryǁscan__mutmut_16, 
        'xǁWorkflowInventoryǁscan__mutmut_17': xǁWorkflowInventoryǁscan__mutmut_17, 
        'xǁWorkflowInventoryǁscan__mutmut_18': xǁWorkflowInventoryǁscan__mutmut_18, 
        'xǁWorkflowInventoryǁscan__mutmut_19': xǁWorkflowInventoryǁscan__mutmut_19, 
        'xǁWorkflowInventoryǁscan__mutmut_20': xǁWorkflowInventoryǁscan__mutmut_20, 
        'xǁWorkflowInventoryǁscan__mutmut_21': xǁWorkflowInventoryǁscan__mutmut_21, 
        'xǁWorkflowInventoryǁscan__mutmut_22': xǁWorkflowInventoryǁscan__mutmut_22, 
        'xǁWorkflowInventoryǁscan__mutmut_23': xǁWorkflowInventoryǁscan__mutmut_23, 
        'xǁWorkflowInventoryǁscan__mutmut_24': xǁWorkflowInventoryǁscan__mutmut_24, 
        'xǁWorkflowInventoryǁscan__mutmut_25': xǁWorkflowInventoryǁscan__mutmut_25, 
        'xǁWorkflowInventoryǁscan__mutmut_26': xǁWorkflowInventoryǁscan__mutmut_26, 
        'xǁWorkflowInventoryǁscan__mutmut_27': xǁWorkflowInventoryǁscan__mutmut_27, 
        'xǁWorkflowInventoryǁscan__mutmut_28': xǁWorkflowInventoryǁscan__mutmut_28, 
        'xǁWorkflowInventoryǁscan__mutmut_29': xǁWorkflowInventoryǁscan__mutmut_29, 
        'xǁWorkflowInventoryǁscan__mutmut_30': xǁWorkflowInventoryǁscan__mutmut_30, 
        'xǁWorkflowInventoryǁscan__mutmut_31': xǁWorkflowInventoryǁscan__mutmut_31, 
        'xǁWorkflowInventoryǁscan__mutmut_32': xǁWorkflowInventoryǁscan__mutmut_32, 
        'xǁWorkflowInventoryǁscan__mutmut_33': xǁWorkflowInventoryǁscan__mutmut_33, 
        'xǁWorkflowInventoryǁscan__mutmut_34': xǁWorkflowInventoryǁscan__mutmut_34, 
        'xǁWorkflowInventoryǁscan__mutmut_35': xǁWorkflowInventoryǁscan__mutmut_35, 
        'xǁWorkflowInventoryǁscan__mutmut_36': xǁWorkflowInventoryǁscan__mutmut_36, 
        'xǁWorkflowInventoryǁscan__mutmut_37': xǁWorkflowInventoryǁscan__mutmut_37
    }
    
    def scan(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁWorkflowInventoryǁscan__mutmut_orig"), object.__getattribute__(self, "xǁWorkflowInventoryǁscan__mutmut_mutants"), args, kwargs, self)
        return result 
    
    scan.__signature__ = _mutmut_signature(xǁWorkflowInventoryǁscan__mutmut_orig)
    xǁWorkflowInventoryǁscan__mutmut_orig.__name__ = 'xǁWorkflowInventoryǁscan'

    def xǁWorkflowInventoryǁget_workflow__mutmut_orig(self, filename: str) -> Optional[WorkflowMetadata]:
        """Get workflow metadata by filename.

        Args:
            filename: Workflow filename (e.g., "test-suite.yml")

        Returns:
            Workflow metadata, or None if not found.
        """
        return self._workflows.get(filename)

    def xǁWorkflowInventoryǁget_workflow__mutmut_1(self, filename: str) -> Optional[WorkflowMetadata]:
        """Get workflow metadata by filename.

        Args:
            filename: Workflow filename (e.g., "test-suite.yml")

        Returns:
            Workflow metadata, or None if not found.
        """
        return self._workflows.get(None)
    
    xǁWorkflowInventoryǁget_workflow__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁWorkflowInventoryǁget_workflow__mutmut_1': xǁWorkflowInventoryǁget_workflow__mutmut_1
    }
    
    def get_workflow(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁWorkflowInventoryǁget_workflow__mutmut_orig"), object.__getattribute__(self, "xǁWorkflowInventoryǁget_workflow__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_workflow.__signature__ = _mutmut_signature(xǁWorkflowInventoryǁget_workflow__mutmut_orig)
    xǁWorkflowInventoryǁget_workflow__mutmut_orig.__name__ = 'xǁWorkflowInventoryǁget_workflow'

    def get_triggerable(self) -> list[WorkflowMetadata]:
        """Get all manually triggerable workflows (workflow_dispatch).

        Returns:
            list of workflows with workflow_dispatch trigger.
        """
        return [w for w in self._workflows.values() if w.is_triggerable]

    def get_reusable(self) -> list[WorkflowMetadata]: 
        """Get all reusable workflows (workflow_call).

        Returns:
            list of workflows with workflow_call trigger.
        """
        return [w for w in self._workflows.values() if w.is_reusable]

    def xǁWorkflowInventoryǁget_by_trigger_type__mutmut_orig(self, trigger_type: TriggerType) -> list[WorkflowMetadata]:
        """Get workflows by trigger type.

        Args:
            trigger_type:  Trigger type to filter by. 

        Returns:
            list of workflows with the specified trigger.
        """
        return [w for w in self._workflows.values() if trigger_type in w.trigger_types]

    def xǁWorkflowInventoryǁget_by_trigger_type__mutmut_1(self, trigger_type: TriggerType) -> list[WorkflowMetadata]:
        """Get workflows by trigger type.

        Args:
            trigger_type:  Trigger type to filter by. 

        Returns:
            list of workflows with the specified trigger.
        """
        return [w for w in self._workflows.values() if trigger_type not in w.trigger_types]
    
    xǁWorkflowInventoryǁget_by_trigger_type__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁWorkflowInventoryǁget_by_trigger_type__mutmut_1': xǁWorkflowInventoryǁget_by_trigger_type__mutmut_1
    }
    
    def get_by_trigger_type(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁWorkflowInventoryǁget_by_trigger_type__mutmut_orig"), object.__getattribute__(self, "xǁWorkflowInventoryǁget_by_trigger_type__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_by_trigger_type.__signature__ = _mutmut_signature(xǁWorkflowInventoryǁget_by_trigger_type__mutmut_orig)
    xǁWorkflowInventoryǁget_by_trigger_type__mutmut_orig.__name__ = 'xǁWorkflowInventoryǁget_by_trigger_type'

    def xǁWorkflowInventoryǁget_workflow_dependencies__mutmut_orig(self, filename: str) -> list[str]:
        """Get workflows that this workflow depends on. 

        Args:
            filename:  Workflow filename.

        Returns:
            list of dependency workflow filenames.
        """
        return [dep.target for dep in self._dependencies if dep.source == filename]

    def xǁWorkflowInventoryǁget_workflow_dependencies__mutmut_1(self, filename: str) -> list[str]:
        """Get workflows that this workflow depends on. 

        Args:
            filename:  Workflow filename.

        Returns:
            list of dependency workflow filenames.
        """
        return [dep.target for dep in self._dependencies if dep.source != filename]
    
    xǁWorkflowInventoryǁget_workflow_dependencies__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁWorkflowInventoryǁget_workflow_dependencies__mutmut_1': xǁWorkflowInventoryǁget_workflow_dependencies__mutmut_1
    }
    
    def get_workflow_dependencies(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁWorkflowInventoryǁget_workflow_dependencies__mutmut_orig"), object.__getattribute__(self, "xǁWorkflowInventoryǁget_workflow_dependencies__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_workflow_dependencies.__signature__ = _mutmut_signature(xǁWorkflowInventoryǁget_workflow_dependencies__mutmut_orig)
    xǁWorkflowInventoryǁget_workflow_dependencies__mutmut_orig.__name__ = 'xǁWorkflowInventoryǁget_workflow_dependencies'

    def xǁWorkflowInventoryǁget_workflow_dependents__mutmut_orig(self, filename: str) -> list[str]:
        """Get workflows that depend on this workflow. 

        Args:
            filename:  Workflow filename.

        Returns:
            list of dependent workflow filenames.
        """
        return [dep.source for dep in self._dependencies if dep.target == filename]

    def xǁWorkflowInventoryǁget_workflow_dependents__mutmut_1(self, filename: str) -> list[str]:
        """Get workflows that depend on this workflow. 

        Args:
            filename:  Workflow filename.

        Returns:
            list of dependent workflow filenames.
        """
        return [dep.source for dep in self._dependencies if dep.target != filename]
    
    xǁWorkflowInventoryǁget_workflow_dependents__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁWorkflowInventoryǁget_workflow_dependents__mutmut_1': xǁWorkflowInventoryǁget_workflow_dependents__mutmut_1
    }
    
    def get_workflow_dependents(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁWorkflowInventoryǁget_workflow_dependents__mutmut_orig"), object.__getattribute__(self, "xǁWorkflowInventoryǁget_workflow_dependents__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_workflow_dependents.__signature__ = _mutmut_signature(xǁWorkflowInventoryǁget_workflow_dependents__mutmut_orig)
    xǁWorkflowInventoryǁget_workflow_dependents__mutmut_orig.__name__ = 'xǁWorkflowInventoryǁget_workflow_dependents'

    def xǁWorkflowInventoryǁget_stats__mutmut_orig(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = 0
        total_triggers = 0

        for workflow in self._workflows.values():
            total_jobs += len(workflow.jobs)
            total_triggers += len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 0) + 1

        return InventoryStats(
            total_workflows=len(self._workflows),
            triggerable_workflows=len(self.get_triggerable()),
            reusable_workflows=len(self.get_reusable()),
            total_jobs=total_jobs,
            total_triggers=total_triggers,
            trigger_type_counts=trigger_counts,
            dependency_count=len(self._dependencies),
        )

    def xǁWorkflowInventoryǁget_stats__mutmut_1(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = None
        total_jobs = 0
        total_triggers = 0

        for workflow in self._workflows.values():
            total_jobs += len(workflow.jobs)
            total_triggers += len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 0) + 1

        return InventoryStats(
            total_workflows=len(self._workflows),
            triggerable_workflows=len(self.get_triggerable()),
            reusable_workflows=len(self.get_reusable()),
            total_jobs=total_jobs,
            total_triggers=total_triggers,
            trigger_type_counts=trigger_counts,
            dependency_count=len(self._dependencies),
        )

    def xǁWorkflowInventoryǁget_stats__mutmut_2(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = None
        total_triggers = 0

        for workflow in self._workflows.values():
            total_jobs += len(workflow.jobs)
            total_triggers += len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 0) + 1

        return InventoryStats(
            total_workflows=len(self._workflows),
            triggerable_workflows=len(self.get_triggerable()),
            reusable_workflows=len(self.get_reusable()),
            total_jobs=total_jobs,
            total_triggers=total_triggers,
            trigger_type_counts=trigger_counts,
            dependency_count=len(self._dependencies),
        )

    def xǁWorkflowInventoryǁget_stats__mutmut_3(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = 1
        total_triggers = 0

        for workflow in self._workflows.values():
            total_jobs += len(workflow.jobs)
            total_triggers += len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 0) + 1

        return InventoryStats(
            total_workflows=len(self._workflows),
            triggerable_workflows=len(self.get_triggerable()),
            reusable_workflows=len(self.get_reusable()),
            total_jobs=total_jobs,
            total_triggers=total_triggers,
            trigger_type_counts=trigger_counts,
            dependency_count=len(self._dependencies),
        )

    def xǁWorkflowInventoryǁget_stats__mutmut_4(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = 0
        total_triggers = None

        for workflow in self._workflows.values():
            total_jobs += len(workflow.jobs)
            total_triggers += len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 0) + 1

        return InventoryStats(
            total_workflows=len(self._workflows),
            triggerable_workflows=len(self.get_triggerable()),
            reusable_workflows=len(self.get_reusable()),
            total_jobs=total_jobs,
            total_triggers=total_triggers,
            trigger_type_counts=trigger_counts,
            dependency_count=len(self._dependencies),
        )

    def xǁWorkflowInventoryǁget_stats__mutmut_5(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = 0
        total_triggers = 1

        for workflow in self._workflows.values():
            total_jobs += len(workflow.jobs)
            total_triggers += len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 0) + 1

        return InventoryStats(
            total_workflows=len(self._workflows),
            triggerable_workflows=len(self.get_triggerable()),
            reusable_workflows=len(self.get_reusable()),
            total_jobs=total_jobs,
            total_triggers=total_triggers,
            trigger_type_counts=trigger_counts,
            dependency_count=len(self._dependencies),
        )

    def xǁWorkflowInventoryǁget_stats__mutmut_6(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = 0
        total_triggers = 0

        for workflow in self._workflows.values():
            total_jobs = len(workflow.jobs)
            total_triggers += len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 0) + 1

        return InventoryStats(
            total_workflows=len(self._workflows),
            triggerable_workflows=len(self.get_triggerable()),
            reusable_workflows=len(self.get_reusable()),
            total_jobs=total_jobs,
            total_triggers=total_triggers,
            trigger_type_counts=trigger_counts,
            dependency_count=len(self._dependencies),
        )

    def xǁWorkflowInventoryǁget_stats__mutmut_7(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = 0
        total_triggers = 0

        for workflow in self._workflows.values():
            total_jobs -= len(workflow.jobs)
            total_triggers += len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 0) + 1

        return InventoryStats(
            total_workflows=len(self._workflows),
            triggerable_workflows=len(self.get_triggerable()),
            reusable_workflows=len(self.get_reusable()),
            total_jobs=total_jobs,
            total_triggers=total_triggers,
            trigger_type_counts=trigger_counts,
            dependency_count=len(self._dependencies),
        )

    def xǁWorkflowInventoryǁget_stats__mutmut_8(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = 0
        total_triggers = 0

        for workflow in self._workflows.values():
            total_jobs += len(workflow.jobs)
            total_triggers = len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 0) + 1

        return InventoryStats(
            total_workflows=len(self._workflows),
            triggerable_workflows=len(self.get_triggerable()),
            reusable_workflows=len(self.get_reusable()),
            total_jobs=total_jobs,
            total_triggers=total_triggers,
            trigger_type_counts=trigger_counts,
            dependency_count=len(self._dependencies),
        )

    def xǁWorkflowInventoryǁget_stats__mutmut_9(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = 0
        total_triggers = 0

        for workflow in self._workflows.values():
            total_jobs += len(workflow.jobs)
            total_triggers -= len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 0) + 1

        return InventoryStats(
            total_workflows=len(self._workflows),
            triggerable_workflows=len(self.get_triggerable()),
            reusable_workflows=len(self.get_reusable()),
            total_jobs=total_jobs,
            total_triggers=total_triggers,
            trigger_type_counts=trigger_counts,
            dependency_count=len(self._dependencies),
        )

    def xǁWorkflowInventoryǁget_stats__mutmut_10(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = 0
        total_triggers = 0

        for workflow in self._workflows.values():
            total_jobs += len(workflow.jobs)
            total_triggers += len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = None
                trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 0) + 1

        return InventoryStats(
            total_workflows=len(self._workflows),
            triggerable_workflows=len(self.get_triggerable()),
            reusable_workflows=len(self.get_reusable()),
            total_jobs=total_jobs,
            total_triggers=total_triggers,
            trigger_type_counts=trigger_counts,
            dependency_count=len(self._dependencies),
        )

    def xǁWorkflowInventoryǁget_stats__mutmut_11(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = 0
        total_triggers = 0

        for workflow in self._workflows.values():
            total_jobs += len(workflow.jobs)
            total_triggers += len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = None

        return InventoryStats(
            total_workflows=len(self._workflows),
            triggerable_workflows=len(self.get_triggerable()),
            reusable_workflows=len(self.get_reusable()),
            total_jobs=total_jobs,
            total_triggers=total_triggers,
            trigger_type_counts=trigger_counts,
            dependency_count=len(self._dependencies),
        )

    def xǁWorkflowInventoryǁget_stats__mutmut_12(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = 0
        total_triggers = 0

        for workflow in self._workflows.values():
            total_jobs += len(workflow.jobs)
            total_triggers += len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 0) - 1

        return InventoryStats(
            total_workflows=len(self._workflows),
            triggerable_workflows=len(self.get_triggerable()),
            reusable_workflows=len(self.get_reusable()),
            total_jobs=total_jobs,
            total_triggers=total_triggers,
            trigger_type_counts=trigger_counts,
            dependency_count=len(self._dependencies),
        )

    def xǁWorkflowInventoryǁget_stats__mutmut_13(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = 0
        total_triggers = 0

        for workflow in self._workflows.values():
            total_jobs += len(workflow.jobs)
            total_triggers += len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = trigger_counts.get(None, 0) + 1

        return InventoryStats(
            total_workflows=len(self._workflows),
            triggerable_workflows=len(self.get_triggerable()),
            reusable_workflows=len(self.get_reusable()),
            total_jobs=total_jobs,
            total_triggers=total_triggers,
            trigger_type_counts=trigger_counts,
            dependency_count=len(self._dependencies),
        )

    def xǁWorkflowInventoryǁget_stats__mutmut_14(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = 0
        total_triggers = 0

        for workflow in self._workflows.values():
            total_jobs += len(workflow.jobs)
            total_triggers += len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = trigger_counts.get(trigger_type, None) + 1

        return InventoryStats(
            total_workflows=len(self._workflows),
            triggerable_workflows=len(self.get_triggerable()),
            reusable_workflows=len(self.get_reusable()),
            total_jobs=total_jobs,
            total_triggers=total_triggers,
            trigger_type_counts=trigger_counts,
            dependency_count=len(self._dependencies),
        )

    def xǁWorkflowInventoryǁget_stats__mutmut_15(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = 0
        total_triggers = 0

        for workflow in self._workflows.values():
            total_jobs += len(workflow.jobs)
            total_triggers += len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = trigger_counts.get(0) + 1

        return InventoryStats(
            total_workflows=len(self._workflows),
            triggerable_workflows=len(self.get_triggerable()),
            reusable_workflows=len(self.get_reusable()),
            total_jobs=total_jobs,
            total_triggers=total_triggers,
            trigger_type_counts=trigger_counts,
            dependency_count=len(self._dependencies),
        )

    def xǁWorkflowInventoryǁget_stats__mutmut_16(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = 0
        total_triggers = 0

        for workflow in self._workflows.values():
            total_jobs += len(workflow.jobs)
            total_triggers += len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = trigger_counts.get(trigger_type, ) + 1

        return InventoryStats(
            total_workflows=len(self._workflows),
            triggerable_workflows=len(self.get_triggerable()),
            reusable_workflows=len(self.get_reusable()),
            total_jobs=total_jobs,
            total_triggers=total_triggers,
            trigger_type_counts=trigger_counts,
            dependency_count=len(self._dependencies),
        )

    def xǁWorkflowInventoryǁget_stats__mutmut_17(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = 0
        total_triggers = 0

        for workflow in self._workflows.values():
            total_jobs += len(workflow.jobs)
            total_triggers += len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 1) + 1

        return InventoryStats(
            total_workflows=len(self._workflows),
            triggerable_workflows=len(self.get_triggerable()),
            reusable_workflows=len(self.get_reusable()),
            total_jobs=total_jobs,
            total_triggers=total_triggers,
            trigger_type_counts=trigger_counts,
            dependency_count=len(self._dependencies),
        )

    def xǁWorkflowInventoryǁget_stats__mutmut_18(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = 0
        total_triggers = 0

        for workflow in self._workflows.values():
            total_jobs += len(workflow.jobs)
            total_triggers += len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 0) + 2

        return InventoryStats(
            total_workflows=len(self._workflows),
            triggerable_workflows=len(self.get_triggerable()),
            reusable_workflows=len(self.get_reusable()),
            total_jobs=total_jobs,
            total_triggers=total_triggers,
            trigger_type_counts=trigger_counts,
            dependency_count=len(self._dependencies),
        )

    def xǁWorkflowInventoryǁget_stats__mutmut_19(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = 0
        total_triggers = 0

        for workflow in self._workflows.values():
            total_jobs += len(workflow.jobs)
            total_triggers += len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 0) + 1

        return InventoryStats(
            total_workflows=None,
            triggerable_workflows=len(self.get_triggerable()),
            reusable_workflows=len(self.get_reusable()),
            total_jobs=total_jobs,
            total_triggers=total_triggers,
            trigger_type_counts=trigger_counts,
            dependency_count=len(self._dependencies),
        )

    def xǁWorkflowInventoryǁget_stats__mutmut_20(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = 0
        total_triggers = 0

        for workflow in self._workflows.values():
            total_jobs += len(workflow.jobs)
            total_triggers += len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 0) + 1

        return InventoryStats(
            total_workflows=len(self._workflows),
            triggerable_workflows=None,
            reusable_workflows=len(self.get_reusable()),
            total_jobs=total_jobs,
            total_triggers=total_triggers,
            trigger_type_counts=trigger_counts,
            dependency_count=len(self._dependencies),
        )

    def xǁWorkflowInventoryǁget_stats__mutmut_21(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = 0
        total_triggers = 0

        for workflow in self._workflows.values():
            total_jobs += len(workflow.jobs)
            total_triggers += len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 0) + 1

        return InventoryStats(
            total_workflows=len(self._workflows),
            triggerable_workflows=len(self.get_triggerable()),
            reusable_workflows=None,
            total_jobs=total_jobs,
            total_triggers=total_triggers,
            trigger_type_counts=trigger_counts,
            dependency_count=len(self._dependencies),
        )

    def xǁWorkflowInventoryǁget_stats__mutmut_22(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = 0
        total_triggers = 0

        for workflow in self._workflows.values():
            total_jobs += len(workflow.jobs)
            total_triggers += len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 0) + 1

        return InventoryStats(
            total_workflows=len(self._workflows),
            triggerable_workflows=len(self.get_triggerable()),
            reusable_workflows=len(self.get_reusable()),
            total_jobs=None,
            total_triggers=total_triggers,
            trigger_type_counts=trigger_counts,
            dependency_count=len(self._dependencies),
        )

    def xǁWorkflowInventoryǁget_stats__mutmut_23(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = 0
        total_triggers = 0

        for workflow in self._workflows.values():
            total_jobs += len(workflow.jobs)
            total_triggers += len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 0) + 1

        return InventoryStats(
            total_workflows=len(self._workflows),
            triggerable_workflows=len(self.get_triggerable()),
            reusable_workflows=len(self.get_reusable()),
            total_jobs=total_jobs,
            total_triggers=None,
            trigger_type_counts=trigger_counts,
            dependency_count=len(self._dependencies),
        )

    def xǁWorkflowInventoryǁget_stats__mutmut_24(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = 0
        total_triggers = 0

        for workflow in self._workflows.values():
            total_jobs += len(workflow.jobs)
            total_triggers += len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 0) + 1

        return InventoryStats(
            total_workflows=len(self._workflows),
            triggerable_workflows=len(self.get_triggerable()),
            reusable_workflows=len(self.get_reusable()),
            total_jobs=total_jobs,
            total_triggers=total_triggers,
            trigger_type_counts=None,
            dependency_count=len(self._dependencies),
        )

    def xǁWorkflowInventoryǁget_stats__mutmut_25(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = 0
        total_triggers = 0

        for workflow in self._workflows.values():
            total_jobs += len(workflow.jobs)
            total_triggers += len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 0) + 1

        return InventoryStats(
            total_workflows=len(self._workflows),
            triggerable_workflows=len(self.get_triggerable()),
            reusable_workflows=len(self.get_reusable()),
            total_jobs=total_jobs,
            total_triggers=total_triggers,
            trigger_type_counts=trigger_counts,
            dependency_count=None,
        )

    def xǁWorkflowInventoryǁget_stats__mutmut_26(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = 0
        total_triggers = 0

        for workflow in self._workflows.values():
            total_jobs += len(workflow.jobs)
            total_triggers += len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 0) + 1

        return InventoryStats(
            triggerable_workflows=len(self.get_triggerable()),
            reusable_workflows=len(self.get_reusable()),
            total_jobs=total_jobs,
            total_triggers=total_triggers,
            trigger_type_counts=trigger_counts,
            dependency_count=len(self._dependencies),
        )

    def xǁWorkflowInventoryǁget_stats__mutmut_27(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = 0
        total_triggers = 0

        for workflow in self._workflows.values():
            total_jobs += len(workflow.jobs)
            total_triggers += len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 0) + 1

        return InventoryStats(
            total_workflows=len(self._workflows),
            reusable_workflows=len(self.get_reusable()),
            total_jobs=total_jobs,
            total_triggers=total_triggers,
            trigger_type_counts=trigger_counts,
            dependency_count=len(self._dependencies),
        )

    def xǁWorkflowInventoryǁget_stats__mutmut_28(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = 0
        total_triggers = 0

        for workflow in self._workflows.values():
            total_jobs += len(workflow.jobs)
            total_triggers += len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 0) + 1

        return InventoryStats(
            total_workflows=len(self._workflows),
            triggerable_workflows=len(self.get_triggerable()),
            total_jobs=total_jobs,
            total_triggers=total_triggers,
            trigger_type_counts=trigger_counts,
            dependency_count=len(self._dependencies),
        )

    def xǁWorkflowInventoryǁget_stats__mutmut_29(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = 0
        total_triggers = 0

        for workflow in self._workflows.values():
            total_jobs += len(workflow.jobs)
            total_triggers += len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 0) + 1

        return InventoryStats(
            total_workflows=len(self._workflows),
            triggerable_workflows=len(self.get_triggerable()),
            reusable_workflows=len(self.get_reusable()),
            total_triggers=total_triggers,
            trigger_type_counts=trigger_counts,
            dependency_count=len(self._dependencies),
        )

    def xǁWorkflowInventoryǁget_stats__mutmut_30(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = 0
        total_triggers = 0

        for workflow in self._workflows.values():
            total_jobs += len(workflow.jobs)
            total_triggers += len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 0) + 1

        return InventoryStats(
            total_workflows=len(self._workflows),
            triggerable_workflows=len(self.get_triggerable()),
            reusable_workflows=len(self.get_reusable()),
            total_jobs=total_jobs,
            trigger_type_counts=trigger_counts,
            dependency_count=len(self._dependencies),
        )

    def xǁWorkflowInventoryǁget_stats__mutmut_31(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = 0
        total_triggers = 0

        for workflow in self._workflows.values():
            total_jobs += len(workflow.jobs)
            total_triggers += len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 0) + 1

        return InventoryStats(
            total_workflows=len(self._workflows),
            triggerable_workflows=len(self.get_triggerable()),
            reusable_workflows=len(self.get_reusable()),
            total_jobs=total_jobs,
            total_triggers=total_triggers,
            dependency_count=len(self._dependencies),
        )

    def xǁWorkflowInventoryǁget_stats__mutmut_32(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = 0
        total_triggers = 0

        for workflow in self._workflows.values():
            total_jobs += len(workflow.jobs)
            total_triggers += len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 0) + 1

        return InventoryStats(
            total_workflows=len(self._workflows),
            triggerable_workflows=len(self.get_triggerable()),
            reusable_workflows=len(self.get_reusable()),
            total_jobs=total_jobs,
            total_triggers=total_triggers,
            trigger_type_counts=trigger_counts,
            )
    
    xǁWorkflowInventoryǁget_stats__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁWorkflowInventoryǁget_stats__mutmut_1': xǁWorkflowInventoryǁget_stats__mutmut_1, 
        'xǁWorkflowInventoryǁget_stats__mutmut_2': xǁWorkflowInventoryǁget_stats__mutmut_2, 
        'xǁWorkflowInventoryǁget_stats__mutmut_3': xǁWorkflowInventoryǁget_stats__mutmut_3, 
        'xǁWorkflowInventoryǁget_stats__mutmut_4': xǁWorkflowInventoryǁget_stats__mutmut_4, 
        'xǁWorkflowInventoryǁget_stats__mutmut_5': xǁWorkflowInventoryǁget_stats__mutmut_5, 
        'xǁWorkflowInventoryǁget_stats__mutmut_6': xǁWorkflowInventoryǁget_stats__mutmut_6, 
        'xǁWorkflowInventoryǁget_stats__mutmut_7': xǁWorkflowInventoryǁget_stats__mutmut_7, 
        'xǁWorkflowInventoryǁget_stats__mutmut_8': xǁWorkflowInventoryǁget_stats__mutmut_8, 
        'xǁWorkflowInventoryǁget_stats__mutmut_9': xǁWorkflowInventoryǁget_stats__mutmut_9, 
        'xǁWorkflowInventoryǁget_stats__mutmut_10': xǁWorkflowInventoryǁget_stats__mutmut_10, 
        'xǁWorkflowInventoryǁget_stats__mutmut_11': xǁWorkflowInventoryǁget_stats__mutmut_11, 
        'xǁWorkflowInventoryǁget_stats__mutmut_12': xǁWorkflowInventoryǁget_stats__mutmut_12, 
        'xǁWorkflowInventoryǁget_stats__mutmut_13': xǁWorkflowInventoryǁget_stats__mutmut_13, 
        'xǁWorkflowInventoryǁget_stats__mutmut_14': xǁWorkflowInventoryǁget_stats__mutmut_14, 
        'xǁWorkflowInventoryǁget_stats__mutmut_15': xǁWorkflowInventoryǁget_stats__mutmut_15, 
        'xǁWorkflowInventoryǁget_stats__mutmut_16': xǁWorkflowInventoryǁget_stats__mutmut_16, 
        'xǁWorkflowInventoryǁget_stats__mutmut_17': xǁWorkflowInventoryǁget_stats__mutmut_17, 
        'xǁWorkflowInventoryǁget_stats__mutmut_18': xǁWorkflowInventoryǁget_stats__mutmut_18, 
        'xǁWorkflowInventoryǁget_stats__mutmut_19': xǁWorkflowInventoryǁget_stats__mutmut_19, 
        'xǁWorkflowInventoryǁget_stats__mutmut_20': xǁWorkflowInventoryǁget_stats__mutmut_20, 
        'xǁWorkflowInventoryǁget_stats__mutmut_21': xǁWorkflowInventoryǁget_stats__mutmut_21, 
        'xǁWorkflowInventoryǁget_stats__mutmut_22': xǁWorkflowInventoryǁget_stats__mutmut_22, 
        'xǁWorkflowInventoryǁget_stats__mutmut_23': xǁWorkflowInventoryǁget_stats__mutmut_23, 
        'xǁWorkflowInventoryǁget_stats__mutmut_24': xǁWorkflowInventoryǁget_stats__mutmut_24, 
        'xǁWorkflowInventoryǁget_stats__mutmut_25': xǁWorkflowInventoryǁget_stats__mutmut_25, 
        'xǁWorkflowInventoryǁget_stats__mutmut_26': xǁWorkflowInventoryǁget_stats__mutmut_26, 
        'xǁWorkflowInventoryǁget_stats__mutmut_27': xǁWorkflowInventoryǁget_stats__mutmut_27, 
        'xǁWorkflowInventoryǁget_stats__mutmut_28': xǁWorkflowInventoryǁget_stats__mutmut_28, 
        'xǁWorkflowInventoryǁget_stats__mutmut_29': xǁWorkflowInventoryǁget_stats__mutmut_29, 
        'xǁWorkflowInventoryǁget_stats__mutmut_30': xǁWorkflowInventoryǁget_stats__mutmut_30, 
        'xǁWorkflowInventoryǁget_stats__mutmut_31': xǁWorkflowInventoryǁget_stats__mutmut_31, 
        'xǁWorkflowInventoryǁget_stats__mutmut_32': xǁWorkflowInventoryǁget_stats__mutmut_32
    }
    
    def get_stats(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁWorkflowInventoryǁget_stats__mutmut_orig"), object.__getattribute__(self, "xǁWorkflowInventoryǁget_stats__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_stats.__signature__ = _mutmut_signature(xǁWorkflowInventoryǁget_stats__mutmut_orig)
    xǁWorkflowInventoryǁget_stats__mutmut_orig.__name__ = 'xǁWorkflowInventoryǁget_stats'

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_orig(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_1(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN or trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_2(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type != TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_3(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = None
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_4(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(None)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_5(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                None
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_6(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=None,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_7(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=None,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_8(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=None,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_9(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=None,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_10(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_11(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_12(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_13(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_14(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=False,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_15(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith(None):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_16(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("XX./XX"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_17(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = None  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_18(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split(None)[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_19(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("XX@XX")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_20(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[1]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_21(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = None
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_22(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(None)
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_23(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip(None))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_24(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.rstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_25(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("XX./XX"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_26(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = None

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_27(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename not in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_28(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                None
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_29(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=None,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_30(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=None,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_31(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=None,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_32(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=None,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_33(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_34(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_35(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    required=True,
                                )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_36(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    )
                            )

    def xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_37(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename: 
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., ". /.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=False,
                                )
                            )
    
    xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_1': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_1, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_2': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_2, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_3': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_3, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_4': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_4, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_5': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_5, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_6': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_6, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_7': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_7, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_8': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_8, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_9': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_9, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_10': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_10, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_11': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_11, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_12': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_12, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_13': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_13, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_14': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_14, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_15': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_15, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_16': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_16, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_17': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_17, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_18': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_18, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_19': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_19, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_20': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_20, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_21': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_21, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_22': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_22, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_23': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_23, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_24': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_24, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_25': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_25, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_26': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_26, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_27': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_27, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_28': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_28, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_29': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_29, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_30': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_30, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_31': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_31, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_32': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_32, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_33': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_33, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_34': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_34, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_35': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_35, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_36': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_36, 
        'xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_37': xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_37
    }
    
    def _build_dependency_graph(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_orig"), object.__getattribute__(self, "xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _build_dependency_graph.__signature__ = _mutmut_signature(xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_orig)
    xǁWorkflowInventoryǁ_build_dependency_graph__mutmut_orig.__name__ = 'xǁWorkflowInventoryǁ_build_dependency_graph'

    def xǁWorkflowInventoryǁ_find_workflow_by_name__mutmut_orig(self, workflow_name: str) -> Optional[str]:
        """Find workflow filename by workflow name. 

        Args:
            workflow_name: Workflow name (from 'name' field).

        Returns:
            Workflow filename, or None if not found.
        """
        for filename, workflow in self._workflows.items():
            if workflow.name == workflow_name:
                return filename
        return None

    def xǁWorkflowInventoryǁ_find_workflow_by_name__mutmut_1(self, workflow_name: str) -> Optional[str]:
        """Find workflow filename by workflow name. 

        Args:
            workflow_name: Workflow name (from 'name' field).

        Returns:
            Workflow filename, or None if not found.
        """
        for filename, workflow in self._workflows.items():
            if workflow.name != workflow_name:
                return filename
        return None
    
    xǁWorkflowInventoryǁ_find_workflow_by_name__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁWorkflowInventoryǁ_find_workflow_by_name__mutmut_1': xǁWorkflowInventoryǁ_find_workflow_by_name__mutmut_1
    }
    
    def _find_workflow_by_name(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁWorkflowInventoryǁ_find_workflow_by_name__mutmut_orig"), object.__getattribute__(self, "xǁWorkflowInventoryǁ_find_workflow_by_name__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _find_workflow_by_name.__signature__ = _mutmut_signature(xǁWorkflowInventoryǁ_find_workflow_by_name__mutmut_orig)
    xǁWorkflowInventoryǁ_find_workflow_by_name__mutmut_orig.__name__ = 'xǁWorkflowInventoryǁ_find_workflow_by_name'

    def xǁWorkflowInventoryǁlist_workflows__mutmut_orig(self) -> list[str]:
        """list all workflow filenames. 

        Returns:
            Sorted list of workflow filenames.
        """
        return sorted(self._workflows.keys())

    def xǁWorkflowInventoryǁlist_workflows__mutmut_1(self) -> list[str]:
        """list all workflow filenames. 

        Returns:
            Sorted list of workflow filenames.
        """
        return sorted(None)
    
    xǁWorkflowInventoryǁlist_workflows__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁWorkflowInventoryǁlist_workflows__mutmut_1': xǁWorkflowInventoryǁlist_workflows__mutmut_1
    }
    
    def list_workflows(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁWorkflowInventoryǁlist_workflows__mutmut_orig"), object.__getattribute__(self, "xǁWorkflowInventoryǁlist_workflows__mutmut_mutants"), args, kwargs, self)
        return result 
    
    list_workflows.__signature__ = _mutmut_signature(xǁWorkflowInventoryǁlist_workflows__mutmut_orig)
    xǁWorkflowInventoryǁlist_workflows__mutmut_orig.__name__ = 'xǁWorkflowInventoryǁlist_workflows'

    def xǁWorkflowInventoryǁrefresh_workflow__mutmut_orig(self, filename: str) -> bool:
        """Refresh a single workflow file.

        Args:
            filename: Workflow filename to refresh.

        Returns:
            True if successfully refreshed, False otherwise.
        """
        workflow_path = self.workflows_dir / filename
        if not workflow_path.exists():
            logger.error(f"Workflow file not found: {workflow_path}")
            return False

        try: 
            metadata = self.parser.parse_file(workflow_path, use_cache=False)
            if metadata:
                self._workflows[filename] = metadata
                self._build_dependency_graph()
                logger.info(f"Refreshed workflow: {filename}")
                return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error refreshing {filename}: {e}")

        return False

    def xǁWorkflowInventoryǁrefresh_workflow__mutmut_1(self, filename: str) -> bool:
        """Refresh a single workflow file.

        Args:
            filename: Workflow filename to refresh.

        Returns:
            True if successfully refreshed, False otherwise.
        """
        workflow_path = None
        if not workflow_path.exists():
            logger.error(f"Workflow file not found: {workflow_path}")
            return False

        try: 
            metadata = self.parser.parse_file(workflow_path, use_cache=False)
            if metadata:
                self._workflows[filename] = metadata
                self._build_dependency_graph()
                logger.info(f"Refreshed workflow: {filename}")
                return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error refreshing {filename}: {e}")

        return False

    def xǁWorkflowInventoryǁrefresh_workflow__mutmut_2(self, filename: str) -> bool:
        """Refresh a single workflow file.

        Args:
            filename: Workflow filename to refresh.

        Returns:
            True if successfully refreshed, False otherwise.
        """
        workflow_path = self.workflows_dir * filename
        if not workflow_path.exists():
            logger.error(f"Workflow file not found: {workflow_path}")
            return False

        try: 
            metadata = self.parser.parse_file(workflow_path, use_cache=False)
            if metadata:
                self._workflows[filename] = metadata
                self._build_dependency_graph()
                logger.info(f"Refreshed workflow: {filename}")
                return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error refreshing {filename}: {e}")

        return False

    def xǁWorkflowInventoryǁrefresh_workflow__mutmut_3(self, filename: str) -> bool:
        """Refresh a single workflow file.

        Args:
            filename: Workflow filename to refresh.

        Returns:
            True if successfully refreshed, False otherwise.
        """
        workflow_path = self.workflows_dir / filename
        if workflow_path.exists():
            logger.error(f"Workflow file not found: {workflow_path}")
            return False

        try: 
            metadata = self.parser.parse_file(workflow_path, use_cache=False)
            if metadata:
                self._workflows[filename] = metadata
                self._build_dependency_graph()
                logger.info(f"Refreshed workflow: {filename}")
                return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error refreshing {filename}: {e}")

        return False

    def xǁWorkflowInventoryǁrefresh_workflow__mutmut_4(self, filename: str) -> bool:
        """Refresh a single workflow file.

        Args:
            filename: Workflow filename to refresh.

        Returns:
            True if successfully refreshed, False otherwise.
        """
        workflow_path = self.workflows_dir / filename
        if not workflow_path.exists():
            logger.error(None)
            return False

        try: 
            metadata = self.parser.parse_file(workflow_path, use_cache=False)
            if metadata:
                self._workflows[filename] = metadata
                self._build_dependency_graph()
                logger.info(f"Refreshed workflow: {filename}")
                return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error refreshing {filename}: {e}")

        return False

    def xǁWorkflowInventoryǁrefresh_workflow__mutmut_5(self, filename: str) -> bool:
        """Refresh a single workflow file.

        Args:
            filename: Workflow filename to refresh.

        Returns:
            True if successfully refreshed, False otherwise.
        """
        workflow_path = self.workflows_dir / filename
        if not workflow_path.exists():
            logger.error(f"Workflow file not found: {workflow_path}")
            return True

        try: 
            metadata = self.parser.parse_file(workflow_path, use_cache=False)
            if metadata:
                self._workflows[filename] = metadata
                self._build_dependency_graph()
                logger.info(f"Refreshed workflow: {filename}")
                return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error refreshing {filename}: {e}")

        return False

    def xǁWorkflowInventoryǁrefresh_workflow__mutmut_6(self, filename: str) -> bool:
        """Refresh a single workflow file.

        Args:
            filename: Workflow filename to refresh.

        Returns:
            True if successfully refreshed, False otherwise.
        """
        workflow_path = self.workflows_dir / filename
        if not workflow_path.exists():
            logger.error(f"Workflow file not found: {workflow_path}")
            return False

        try: 
            metadata = None
            if metadata:
                self._workflows[filename] = metadata
                self._build_dependency_graph()
                logger.info(f"Refreshed workflow: {filename}")
                return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error refreshing {filename}: {e}")

        return False

    def xǁWorkflowInventoryǁrefresh_workflow__mutmut_7(self, filename: str) -> bool:
        """Refresh a single workflow file.

        Args:
            filename: Workflow filename to refresh.

        Returns:
            True if successfully refreshed, False otherwise.
        """
        workflow_path = self.workflows_dir / filename
        if not workflow_path.exists():
            logger.error(f"Workflow file not found: {workflow_path}")
            return False

        try: 
            metadata = self.parser.parse_file(None, use_cache=False)
            if metadata:
                self._workflows[filename] = metadata
                self._build_dependency_graph()
                logger.info(f"Refreshed workflow: {filename}")
                return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error refreshing {filename}: {e}")

        return False

    def xǁWorkflowInventoryǁrefresh_workflow__mutmut_8(self, filename: str) -> bool:
        """Refresh a single workflow file.

        Args:
            filename: Workflow filename to refresh.

        Returns:
            True if successfully refreshed, False otherwise.
        """
        workflow_path = self.workflows_dir / filename
        if not workflow_path.exists():
            logger.error(f"Workflow file not found: {workflow_path}")
            return False

        try: 
            metadata = self.parser.parse_file(workflow_path, use_cache=None)
            if metadata:
                self._workflows[filename] = metadata
                self._build_dependency_graph()
                logger.info(f"Refreshed workflow: {filename}")
                return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error refreshing {filename}: {e}")

        return False

    def xǁWorkflowInventoryǁrefresh_workflow__mutmut_9(self, filename: str) -> bool:
        """Refresh a single workflow file.

        Args:
            filename: Workflow filename to refresh.

        Returns:
            True if successfully refreshed, False otherwise.
        """
        workflow_path = self.workflows_dir / filename
        if not workflow_path.exists():
            logger.error(f"Workflow file not found: {workflow_path}")
            return False

        try: 
            metadata = self.parser.parse_file(use_cache=False)
            if metadata:
                self._workflows[filename] = metadata
                self._build_dependency_graph()
                logger.info(f"Refreshed workflow: {filename}")
                return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error refreshing {filename}: {e}")

        return False

    def xǁWorkflowInventoryǁrefresh_workflow__mutmut_10(self, filename: str) -> bool:
        """Refresh a single workflow file.

        Args:
            filename: Workflow filename to refresh.

        Returns:
            True if successfully refreshed, False otherwise.
        """
        workflow_path = self.workflows_dir / filename
        if not workflow_path.exists():
            logger.error(f"Workflow file not found: {workflow_path}")
            return False

        try: 
            metadata = self.parser.parse_file(workflow_path, )
            if metadata:
                self._workflows[filename] = metadata
                self._build_dependency_graph()
                logger.info(f"Refreshed workflow: {filename}")
                return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error refreshing {filename}: {e}")

        return False

    def xǁWorkflowInventoryǁrefresh_workflow__mutmut_11(self, filename: str) -> bool:
        """Refresh a single workflow file.

        Args:
            filename: Workflow filename to refresh.

        Returns:
            True if successfully refreshed, False otherwise.
        """
        workflow_path = self.workflows_dir / filename
        if not workflow_path.exists():
            logger.error(f"Workflow file not found: {workflow_path}")
            return False

        try: 
            metadata = self.parser.parse_file(workflow_path, use_cache=True)
            if metadata:
                self._workflows[filename] = metadata
                self._build_dependency_graph()
                logger.info(f"Refreshed workflow: {filename}")
                return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error refreshing {filename}: {e}")

        return False

    def xǁWorkflowInventoryǁrefresh_workflow__mutmut_12(self, filename: str) -> bool:
        """Refresh a single workflow file.

        Args:
            filename: Workflow filename to refresh.

        Returns:
            True if successfully refreshed, False otherwise.
        """
        workflow_path = self.workflows_dir / filename
        if not workflow_path.exists():
            logger.error(f"Workflow file not found: {workflow_path}")
            return False

        try: 
            metadata = self.parser.parse_file(workflow_path, use_cache=False)
            if metadata:
                self._workflows[filename] = None
                self._build_dependency_graph()
                logger.info(f"Refreshed workflow: {filename}")
                return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error refreshing {filename}: {e}")

        return False

    def xǁWorkflowInventoryǁrefresh_workflow__mutmut_13(self, filename: str) -> bool:
        """Refresh a single workflow file.

        Args:
            filename: Workflow filename to refresh.

        Returns:
            True if successfully refreshed, False otherwise.
        """
        workflow_path = self.workflows_dir / filename
        if not workflow_path.exists():
            logger.error(f"Workflow file not found: {workflow_path}")
            return False

        try: 
            metadata = self.parser.parse_file(workflow_path, use_cache=False)
            if metadata:
                self._workflows[filename] = metadata
                self._build_dependency_graph()
                logger.info(None)
                return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error refreshing {filename}: {e}")

        return False

    def xǁWorkflowInventoryǁrefresh_workflow__mutmut_14(self, filename: str) -> bool:
        """Refresh a single workflow file.

        Args:
            filename: Workflow filename to refresh.

        Returns:
            True if successfully refreshed, False otherwise.
        """
        workflow_path = self.workflows_dir / filename
        if not workflow_path.exists():
            logger.error(f"Workflow file not found: {workflow_path}")
            return False

        try: 
            metadata = self.parser.parse_file(workflow_path, use_cache=False)
            if metadata:
                self._workflows[filename] = metadata
                self._build_dependency_graph()
                logger.info(f"Refreshed workflow: {filename}")
                return False
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error refreshing {filename}: {e}")

        return False

    def xǁWorkflowInventoryǁrefresh_workflow__mutmut_15(self, filename: str) -> bool:
        """Refresh a single workflow file.

        Args:
            filename: Workflow filename to refresh.

        Returns:
            True if successfully refreshed, False otherwise.
        """
        workflow_path = self.workflows_dir / filename
        if not workflow_path.exists():
            logger.error(f"Workflow file not found: {workflow_path}")
            return False

        try: 
            metadata = self.parser.parse_file(workflow_path, use_cache=False)
            if metadata:
                self._workflows[filename] = metadata
                self._build_dependency_graph()
                logger.info(f"Refreshed workflow: {filename}")
                return True
        except Exception as e:
            logger.debug(None)
            logger.error(f"Error refreshing {filename}: {e}")

        return False

    def xǁWorkflowInventoryǁrefresh_workflow__mutmut_16(self, filename: str) -> bool:
        """Refresh a single workflow file.

        Args:
            filename: Workflow filename to refresh.

        Returns:
            True if successfully refreshed, False otherwise.
        """
        workflow_path = self.workflows_dir / filename
        if not workflow_path.exists():
            logger.error(f"Workflow file not found: {workflow_path}")
            return False

        try: 
            metadata = self.parser.parse_file(workflow_path, use_cache=False)
            if metadata:
                self._workflows[filename] = metadata
                self._build_dependency_graph()
                logger.info(f"Refreshed workflow: {filename}")
                return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(None)

        return False

    def xǁWorkflowInventoryǁrefresh_workflow__mutmut_17(self, filename: str) -> bool:
        """Refresh a single workflow file.

        Args:
            filename: Workflow filename to refresh.

        Returns:
            True if successfully refreshed, False otherwise.
        """
        workflow_path = self.workflows_dir / filename
        if not workflow_path.exists():
            logger.error(f"Workflow file not found: {workflow_path}")
            return False

        try: 
            metadata = self.parser.parse_file(workflow_path, use_cache=False)
            if metadata:
                self._workflows[filename] = metadata
                self._build_dependency_graph()
                logger.info(f"Refreshed workflow: {filename}")
                return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error refreshing {filename}: {e}")

        return True
    
    xǁWorkflowInventoryǁrefresh_workflow__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁWorkflowInventoryǁrefresh_workflow__mutmut_1': xǁWorkflowInventoryǁrefresh_workflow__mutmut_1, 
        'xǁWorkflowInventoryǁrefresh_workflow__mutmut_2': xǁWorkflowInventoryǁrefresh_workflow__mutmut_2, 
        'xǁWorkflowInventoryǁrefresh_workflow__mutmut_3': xǁWorkflowInventoryǁrefresh_workflow__mutmut_3, 
        'xǁWorkflowInventoryǁrefresh_workflow__mutmut_4': xǁWorkflowInventoryǁrefresh_workflow__mutmut_4, 
        'xǁWorkflowInventoryǁrefresh_workflow__mutmut_5': xǁWorkflowInventoryǁrefresh_workflow__mutmut_5, 
        'xǁWorkflowInventoryǁrefresh_workflow__mutmut_6': xǁWorkflowInventoryǁrefresh_workflow__mutmut_6, 
        'xǁWorkflowInventoryǁrefresh_workflow__mutmut_7': xǁWorkflowInventoryǁrefresh_workflow__mutmut_7, 
        'xǁWorkflowInventoryǁrefresh_workflow__mutmut_8': xǁWorkflowInventoryǁrefresh_workflow__mutmut_8, 
        'xǁWorkflowInventoryǁrefresh_workflow__mutmut_9': xǁWorkflowInventoryǁrefresh_workflow__mutmut_9, 
        'xǁWorkflowInventoryǁrefresh_workflow__mutmut_10': xǁWorkflowInventoryǁrefresh_workflow__mutmut_10, 
        'xǁWorkflowInventoryǁrefresh_workflow__mutmut_11': xǁWorkflowInventoryǁrefresh_workflow__mutmut_11, 
        'xǁWorkflowInventoryǁrefresh_workflow__mutmut_12': xǁWorkflowInventoryǁrefresh_workflow__mutmut_12, 
        'xǁWorkflowInventoryǁrefresh_workflow__mutmut_13': xǁWorkflowInventoryǁrefresh_workflow__mutmut_13, 
        'xǁWorkflowInventoryǁrefresh_workflow__mutmut_14': xǁWorkflowInventoryǁrefresh_workflow__mutmut_14, 
        'xǁWorkflowInventoryǁrefresh_workflow__mutmut_15': xǁWorkflowInventoryǁrefresh_workflow__mutmut_15, 
        'xǁWorkflowInventoryǁrefresh_workflow__mutmut_16': xǁWorkflowInventoryǁrefresh_workflow__mutmut_16, 
        'xǁWorkflowInventoryǁrefresh_workflow__mutmut_17': xǁWorkflowInventoryǁrefresh_workflow__mutmut_17
    }
    
    def refresh_workflow(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁWorkflowInventoryǁrefresh_workflow__mutmut_orig"), object.__getattribute__(self, "xǁWorkflowInventoryǁrefresh_workflow__mutmut_mutants"), args, kwargs, self)
        return result 
    
    refresh_workflow.__signature__ = _mutmut_signature(xǁWorkflowInventoryǁrefresh_workflow__mutmut_orig)
    xǁWorkflowInventoryǁrefresh_workflow__mutmut_orig.__name__ = 'xǁWorkflowInventoryǁrefresh_workflow'
