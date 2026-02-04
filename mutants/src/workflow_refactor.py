"""
CI/CD Workflow Refactoring Utility

Refactors GitHub Actions workflows to add workflow_dispatch triggers
for manual gating while keeping them in active .github/workflows/ directory.

Part of Phase 4: CI/CD Pipeline Refactoring

Note: Logging is configured using the standard logging module. For production use,
ensure logging is properly configured via logging.basicConfig() or a logging
configuration file before using this module.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Repository root
REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"
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


class WorkflowRefactorer:
    """
    Utility to refactor GitHub Actions workflows.
    
    Adds workflow_dispatch triggers and ensures runs-on: [self-hosted, linux]
    tags for cost control and compliance.
    """
    
    def xǁWorkflowRefactorerǁ__init____mutmut_orig(self, workflows_dir: Optional[Path] = None):
        """
        Initialize workflow refactorer.
        
        Args:
            workflows_dir: Path to workflows directory
        """
        self.workflows_dir = workflows_dir or WORKFLOWS_DIR
        
        if not self.workflows_dir.exists():
            raise ValueError(f"Workflows directory not found: {self.workflows_dir}")
        
        logger.info(f"WorkflowRefactorer initialized: {self.workflows_dir}")
    
    def xǁWorkflowRefactorerǁ__init____mutmut_1(self, workflows_dir: Optional[Path] = None):
        """
        Initialize workflow refactorer.
        
        Args:
            workflows_dir: Path to workflows directory
        """
        self.workflows_dir = None
        
        if not self.workflows_dir.exists():
            raise ValueError(f"Workflows directory not found: {self.workflows_dir}")
        
        logger.info(f"WorkflowRefactorer initialized: {self.workflows_dir}")
    
    def xǁWorkflowRefactorerǁ__init____mutmut_2(self, workflows_dir: Optional[Path] = None):
        """
        Initialize workflow refactorer.
        
        Args:
            workflows_dir: Path to workflows directory
        """
        self.workflows_dir = workflows_dir and WORKFLOWS_DIR
        
        if not self.workflows_dir.exists():
            raise ValueError(f"Workflows directory not found: {self.workflows_dir}")
        
        logger.info(f"WorkflowRefactorer initialized: {self.workflows_dir}")
    
    def xǁWorkflowRefactorerǁ__init____mutmut_3(self, workflows_dir: Optional[Path] = None):
        """
        Initialize workflow refactorer.
        
        Args:
            workflows_dir: Path to workflows directory
        """
        self.workflows_dir = workflows_dir or WORKFLOWS_DIR
        
        if self.workflows_dir.exists():
            raise ValueError(f"Workflows directory not found: {self.workflows_dir}")
        
        logger.info(f"WorkflowRefactorer initialized: {self.workflows_dir}")
    
    def xǁWorkflowRefactorerǁ__init____mutmut_4(self, workflows_dir: Optional[Path] = None):
        """
        Initialize workflow refactorer.
        
        Args:
            workflows_dir: Path to workflows directory
        """
        self.workflows_dir = workflows_dir or WORKFLOWS_DIR
        
        if not self.workflows_dir.exists():
            raise ValueError(None)
        
        logger.info(f"WorkflowRefactorer initialized: {self.workflows_dir}")
    
    def xǁWorkflowRefactorerǁ__init____mutmut_5(self, workflows_dir: Optional[Path] = None):
        """
        Initialize workflow refactorer.
        
        Args:
            workflows_dir: Path to workflows directory
        """
        self.workflows_dir = workflows_dir or WORKFLOWS_DIR
        
        if not self.workflows_dir.exists():
            raise ValueError(f"Workflows directory not found: {self.workflows_dir}")
        
        logger.info(None)
    
    xǁWorkflowRefactorerǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁWorkflowRefactorerǁ__init____mutmut_1': xǁWorkflowRefactorerǁ__init____mutmut_1, 
        'xǁWorkflowRefactorerǁ__init____mutmut_2': xǁWorkflowRefactorerǁ__init____mutmut_2, 
        'xǁWorkflowRefactorerǁ__init____mutmut_3': xǁWorkflowRefactorerǁ__init____mutmut_3, 
        'xǁWorkflowRefactorerǁ__init____mutmut_4': xǁWorkflowRefactorerǁ__init____mutmut_4, 
        'xǁWorkflowRefactorerǁ__init____mutmut_5': xǁWorkflowRefactorerǁ__init____mutmut_5
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁWorkflowRefactorerǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁWorkflowRefactorerǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁWorkflowRefactorerǁ__init____mutmut_orig)
    xǁWorkflowRefactorerǁ__init____mutmut_orig.__name__ = 'xǁWorkflowRefactorerǁ__init__'
    
    def xǁWorkflowRefactorerǁlist_workflows__mutmut_orig(self) -> List[Path]:
        """
        List all workflow files.
        
        Returns:
            List of workflow file paths
        """
        workflows = []
        for ext in ["*.yml", "*.yaml"]:
            workflows.extend(self.workflows_dir.glob(ext))
            workflows.extend(self.workflows_dir.glob(f"**/{ext}"))
        
        return sorted(workflows)
    
    def xǁWorkflowRefactorerǁlist_workflows__mutmut_1(self) -> List[Path]:
        """
        List all workflow files.
        
        Returns:
            List of workflow file paths
        """
        workflows = None
        for ext in ["*.yml", "*.yaml"]:
            workflows.extend(self.workflows_dir.glob(ext))
            workflows.extend(self.workflows_dir.glob(f"**/{ext}"))
        
        return sorted(workflows)
    
    def xǁWorkflowRefactorerǁlist_workflows__mutmut_2(self) -> List[Path]:
        """
        List all workflow files.
        
        Returns:
            List of workflow file paths
        """
        workflows = []
        for ext in ["XX*.ymlXX", "*.yaml"]:
            workflows.extend(self.workflows_dir.glob(ext))
            workflows.extend(self.workflows_dir.glob(f"**/{ext}"))
        
        return sorted(workflows)
    
    def xǁWorkflowRefactorerǁlist_workflows__mutmut_3(self) -> List[Path]:
        """
        List all workflow files.
        
        Returns:
            List of workflow file paths
        """
        workflows = []
        for ext in ["*.YML", "*.yaml"]:
            workflows.extend(self.workflows_dir.glob(ext))
            workflows.extend(self.workflows_dir.glob(f"**/{ext}"))
        
        return sorted(workflows)
    
    def xǁWorkflowRefactorerǁlist_workflows__mutmut_4(self) -> List[Path]:
        """
        List all workflow files.
        
        Returns:
            List of workflow file paths
        """
        workflows = []
        for ext in ["*.yml", "XX*.yamlXX"]:
            workflows.extend(self.workflows_dir.glob(ext))
            workflows.extend(self.workflows_dir.glob(f"**/{ext}"))
        
        return sorted(workflows)
    
    def xǁWorkflowRefactorerǁlist_workflows__mutmut_5(self) -> List[Path]:
        """
        List all workflow files.
        
        Returns:
            List of workflow file paths
        """
        workflows = []
        for ext in ["*.yml", "*.YAML"]:
            workflows.extend(self.workflows_dir.glob(ext))
            workflows.extend(self.workflows_dir.glob(f"**/{ext}"))
        
        return sorted(workflows)
    
    def xǁWorkflowRefactorerǁlist_workflows__mutmut_6(self) -> List[Path]:
        """
        List all workflow files.
        
        Returns:
            List of workflow file paths
        """
        workflows = []
        for ext in ["*.yml", "*.yaml"]:
            workflows.extend(None)
            workflows.extend(self.workflows_dir.glob(f"**/{ext}"))
        
        return sorted(workflows)
    
    def xǁWorkflowRefactorerǁlist_workflows__mutmut_7(self) -> List[Path]:
        """
        List all workflow files.
        
        Returns:
            List of workflow file paths
        """
        workflows = []
        for ext in ["*.yml", "*.yaml"]:
            workflows.extend(self.workflows_dir.glob(None))
            workflows.extend(self.workflows_dir.glob(f"**/{ext}"))
        
        return sorted(workflows)
    
    def xǁWorkflowRefactorerǁlist_workflows__mutmut_8(self) -> List[Path]:
        """
        List all workflow files.
        
        Returns:
            List of workflow file paths
        """
        workflows = []
        for ext in ["*.yml", "*.yaml"]:
            workflows.extend(self.workflows_dir.glob(ext))
            workflows.extend(None)
        
        return sorted(workflows)
    
    def xǁWorkflowRefactorerǁlist_workflows__mutmut_9(self) -> List[Path]:
        """
        List all workflow files.
        
        Returns:
            List of workflow file paths
        """
        workflows = []
        for ext in ["*.yml", "*.yaml"]:
            workflows.extend(self.workflows_dir.glob(ext))
            workflows.extend(self.workflows_dir.glob(None))
        
        return sorted(workflows)
    
    def xǁWorkflowRefactorerǁlist_workflows__mutmut_10(self) -> List[Path]:
        """
        List all workflow files.
        
        Returns:
            List of workflow file paths
        """
        workflows = []
        for ext in ["*.yml", "*.yaml"]:
            workflows.extend(self.workflows_dir.glob(ext))
            workflows.extend(self.workflows_dir.glob(f"**/{ext}"))
        
        return sorted(None)
    
    xǁWorkflowRefactorerǁlist_workflows__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁWorkflowRefactorerǁlist_workflows__mutmut_1': xǁWorkflowRefactorerǁlist_workflows__mutmut_1, 
        'xǁWorkflowRefactorerǁlist_workflows__mutmut_2': xǁWorkflowRefactorerǁlist_workflows__mutmut_2, 
        'xǁWorkflowRefactorerǁlist_workflows__mutmut_3': xǁWorkflowRefactorerǁlist_workflows__mutmut_3, 
        'xǁWorkflowRefactorerǁlist_workflows__mutmut_4': xǁWorkflowRefactorerǁlist_workflows__mutmut_4, 
        'xǁWorkflowRefactorerǁlist_workflows__mutmut_5': xǁWorkflowRefactorerǁlist_workflows__mutmut_5, 
        'xǁWorkflowRefactorerǁlist_workflows__mutmut_6': xǁWorkflowRefactorerǁlist_workflows__mutmut_6, 
        'xǁWorkflowRefactorerǁlist_workflows__mutmut_7': xǁWorkflowRefactorerǁlist_workflows__mutmut_7, 
        'xǁWorkflowRefactorerǁlist_workflows__mutmut_8': xǁWorkflowRefactorerǁlist_workflows__mutmut_8, 
        'xǁWorkflowRefactorerǁlist_workflows__mutmut_9': xǁWorkflowRefactorerǁlist_workflows__mutmut_9, 
        'xǁWorkflowRefactorerǁlist_workflows__mutmut_10': xǁWorkflowRefactorerǁlist_workflows__mutmut_10
    }
    
    def list_workflows(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁWorkflowRefactorerǁlist_workflows__mutmut_orig"), object.__getattribute__(self, "xǁWorkflowRefactorerǁlist_workflows__mutmut_mutants"), args, kwargs, self)
        return result 
    
    list_workflows.__signature__ = _mutmut_signature(xǁWorkflowRefactorerǁlist_workflows__mutmut_orig)
    xǁWorkflowRefactorerǁlist_workflows__mutmut_orig.__name__ = 'xǁWorkflowRefactorerǁlist_workflows'
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_orig(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_1(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error(None)
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_2(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("XXPyYAML not installedXX")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_3(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("pyyaml not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_4(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PYYAML NOT INSTALLED")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_5(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return True
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_6(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(None, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_7(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, None) as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_8(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open('r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_9(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, ) as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_10(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'XXrXX') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_11(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'R') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_12(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = None
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_13(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'XXworkflow_dispatchXX' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_14(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'WORKFLOW_DISPATCH' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_15(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' not in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_16(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(None)
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_17(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return True
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_18(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = None
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_19(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(None)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_20(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(None)
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_21(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return True
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_22(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) and 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_23(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_24(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'XXonXX' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_25(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'ON' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_26(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_27(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(None)
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_28(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return True
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_29(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = ""
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_30(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['XXonXX']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_31(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['ON']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_32(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['XXworkflow_dispatchXX'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_33(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['WORKFLOW_DISPATCH'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_34(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append(None)
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_35(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['XXonXX'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_36(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['ON'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_37(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('XXworkflow_dispatchXX')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_38(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('WORKFLOW_DISPATCH')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_39(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = None
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_40(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['XXonXX'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_41(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['ON'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_42(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['XXonXX'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_43(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['ON'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_44(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'XXworkflow_dispatchXX']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_45(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'WORKFLOW_DISPATCH']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_46(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(None)
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_47(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return True
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_48(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(None, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_49(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, None) as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_50(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open('w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_51(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, ) as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_52(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'XXwXX') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_53(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'W') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_54(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(None, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_55(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, None, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_56(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=None, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_57(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=None)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_58(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_59(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_60(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_61(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, )
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_62(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=True, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_63(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=True)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_64(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(None)
        return True
    
    def xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_65(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if workflow_dispatch already exists
        if 'workflow_dispatch' in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'on' not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False
        
        # Add workflow_dispatch
        if isinstance(data['on'], dict):
            data['on']['workflow_dispatch'] = None
        elif isinstance(data['on'], list):
            data['on'].append('workflow_dispatch')
        elif isinstance(data['on'], str):
            data['on'] = [data['on'], 'workflow_dispatch']
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False
        
        # Write back
        with open(workflow_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return False
    
    xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_1': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_1, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_2': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_2, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_3': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_3, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_4': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_4, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_5': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_5, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_6': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_6, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_7': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_7, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_8': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_8, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_9': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_9, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_10': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_10, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_11': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_11, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_12': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_12, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_13': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_13, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_14': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_14, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_15': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_15, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_16': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_16, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_17': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_17, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_18': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_18, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_19': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_19, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_20': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_20, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_21': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_21, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_22': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_22, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_23': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_23, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_24': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_24, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_25': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_25, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_26': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_26, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_27': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_27, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_28': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_28, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_29': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_29, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_30': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_30, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_31': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_31, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_32': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_32, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_33': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_33, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_34': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_34, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_35': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_35, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_36': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_36, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_37': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_37, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_38': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_38, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_39': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_39, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_40': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_40, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_41': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_41, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_42': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_42, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_43': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_43, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_44': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_44, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_45': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_45, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_46': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_46, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_47': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_47, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_48': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_48, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_49': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_49, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_50': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_50, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_51': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_51, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_52': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_52, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_53': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_53, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_54': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_54, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_55': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_55, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_56': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_56, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_57': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_57, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_58': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_58, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_59': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_59, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_60': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_60, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_61': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_61, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_62': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_62, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_63': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_63, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_64': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_64, 
        'xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_65': xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_65
    }
    
    def add_workflow_dispatch(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_orig"), object.__getattribute__(self, "xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_mutants"), args, kwargs, self)
        return result 
    
    add_workflow_dispatch.__signature__ = _mutmut_signature(xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_orig)
    xǁWorkflowRefactorerǁadd_workflow_dispatch__mutmut_orig.__name__ = 'xǁWorkflowRefactorerǁadd_workflow_dispatch'
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_orig(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_1(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error(None)
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_2(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("XXPyYAML not installedXX")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_3(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("pyyaml not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_4(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PYYAML NOT INSTALLED")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_5(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"XXmodifiedXX": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_6(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"MODIFIED": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_7(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": True, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_8(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "XXerrorXX": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_9(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "ERROR": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_10(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "XXPyYAML not installedXX"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_11(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "pyyaml not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_12(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PYYAML NOT INSTALLED"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_13(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(None, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_14(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, None) as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_15(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open('r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_16(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, ) as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_17(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'XXrXX') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_18(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'R') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_19(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = None
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_20(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = None
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_21(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(None)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_22(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(None)
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_23(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"XXmodifiedXX": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_24(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"MODIFIED": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_25(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": True, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_26(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "XXerrorXX": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_27(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "ERROR": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_28(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(None)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_29(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) and 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_30(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_31(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'XXjobsXX' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_32(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'JOBS' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_33(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_34(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"XXmodifiedXX": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_35(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"MODIFIED": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_36(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": True, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_37(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "XXreasonXX": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_38(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "REASON": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_39(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "XXNo jobs foundXX"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_40(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "no jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_41(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "NO JOBS FOUND"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_42(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = None
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_43(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = True
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_44(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = None
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_45(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['XXjobsXX'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_46(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['JOBS'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_47(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_48(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                break
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_49(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = None
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_50(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get(None)
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_51(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('XXruns-onXX')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_52(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('RUNS-ON')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_53(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on or 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_54(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'XXself-hostedXX' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_55(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'SELF-HOSTED' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_56(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' not in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_57(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'XXlinuxXX' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_58(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'LINUX' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_59(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' not in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_60(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    break  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_61(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = None
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_62(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['XXruns-onXX'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_63(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['RUNS-ON'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_64(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['XXself-hostedXX', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_65(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['SELF-HOSTED', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_66(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'XXlinuxXX']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_67(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'LINUX']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_68(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = None
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_69(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = False
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_70(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(None)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_71(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_72(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['XXself-hostedXX', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_73(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['SELF-HOSTED', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_74(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', 'XX[self-hosted, linux]XX']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_75(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[SELF-HOSTED, LINUX]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_76(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = None
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_77(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['XXruns-onXX'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_78(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['RUNS-ON'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_79(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['XXself-hostedXX', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_80(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['SELF-HOSTED', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_81(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'XXlinuxXX']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_82(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'LINUX']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_83(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = None
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_84(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = False
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_85(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(None)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_86(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(None, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_87(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, None) as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_88(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open('w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_89(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, ) as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_90(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'XXwXX') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_91(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'W') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_92(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(None, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_93(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, None, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_94(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=None, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_95(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=None)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_96(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_97(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_98(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_99(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, )
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_100(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=True, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_101(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=True)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_102(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                None
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_103(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(None)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_104(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{'XX, XX'.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_105(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "XXmodifiedXX": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_106(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "MODIFIED": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_107(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "XXjobs_updatedXX": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_108(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "JOBS_UPDATED": jobs_updated,
            "total_jobs": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_109(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "XXtotal_jobsXX": len(data['jobs'])
        }
    
    def xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_110(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return {"modified": False, "error": str(e)}
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return {"modified": False, "reason": "No jobs found"}
        
        modified = False
        jobs_updated = []
        
        # Process each job
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict):
                continue
            
            runs_on = job_config.get('runs-on')
            
            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if 'self-hosted' in runs_on and 'linux' in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config['runs-on'] = ['self-hosted', 'linux']
                modified = True
                jobs_updated.append(job_name)
            
            elif isinstance(runs_on, str):
                if runs_on not in ['self-hosted', '[self-hosted, linux]']:
                    # Replace with [self-hosted, linux]
                    job_config['runs-on'] = ['self-hosted', 'linux']
                    modified = True
                    jobs_updated.append(job_name)
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(
                f"Updated runs-on for {workflow_path.name}: "
                f"{', '.join(jobs_updated)}"
            )
        
        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "TOTAL_JOBS": len(data['jobs'])
        }
    
    xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_1': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_1, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_2': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_2, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_3': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_3, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_4': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_4, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_5': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_5, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_6': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_6, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_7': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_7, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_8': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_8, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_9': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_9, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_10': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_10, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_11': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_11, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_12': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_12, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_13': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_13, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_14': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_14, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_15': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_15, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_16': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_16, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_17': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_17, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_18': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_18, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_19': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_19, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_20': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_20, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_21': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_21, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_22': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_22, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_23': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_23, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_24': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_24, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_25': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_25, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_26': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_26, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_27': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_27, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_28': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_28, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_29': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_29, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_30': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_30, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_31': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_31, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_32': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_32, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_33': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_33, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_34': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_34, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_35': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_35, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_36': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_36, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_37': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_37, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_38': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_38, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_39': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_39, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_40': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_40, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_41': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_41, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_42': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_42, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_43': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_43, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_44': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_44, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_45': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_45, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_46': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_46, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_47': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_47, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_48': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_48, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_49': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_49, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_50': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_50, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_51': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_51, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_52': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_52, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_53': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_53, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_54': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_54, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_55': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_55, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_56': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_56, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_57': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_57, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_58': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_58, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_59': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_59, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_60': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_60, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_61': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_61, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_62': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_62, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_63': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_63, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_64': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_64, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_65': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_65, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_66': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_66, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_67': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_67, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_68': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_68, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_69': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_69, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_70': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_70, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_71': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_71, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_72': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_72, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_73': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_73, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_74': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_74, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_75': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_75, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_76': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_76, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_77': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_77, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_78': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_78, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_79': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_79, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_80': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_80, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_81': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_81, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_82': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_82, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_83': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_83, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_84': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_84, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_85': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_85, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_86': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_86, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_87': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_87, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_88': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_88, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_89': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_89, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_90': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_90, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_91': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_91, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_92': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_92, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_93': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_93, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_94': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_94, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_95': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_95, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_96': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_96, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_97': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_97, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_98': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_98, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_99': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_99, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_100': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_100, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_101': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_101, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_102': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_102, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_103': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_103, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_104': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_104, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_105': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_105, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_106': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_106, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_107': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_107, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_108': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_108, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_109': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_109, 
        'xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_110': xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_110
    }
    
    def ensure_self_hosted_runner(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_orig"), object.__getattribute__(self, "xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_mutants"), args, kwargs, self)
        return result 
    
    ensure_self_hosted_runner.__signature__ = _mutmut_signature(xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_orig)
    xǁWorkflowRefactorerǁensure_self_hosted_runner__mutmut_orig.__name__ = 'xǁWorkflowRefactorerǁensure_self_hosted_runner'
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_orig(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_1(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error(None)
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_2(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("XXPyYAML not installedXX")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_3(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("pyyaml not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_4(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PYYAML NOT INSTALLED")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_5(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return True
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_6(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(None, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_7(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, None) as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_8(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open('r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_9(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, ) as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_10(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'XXrXX') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_11(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'R') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_12(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = None
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_13(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content and 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_14(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'XXcodex_digestXX' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_15(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'CODEX_DIGEST' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_16(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' not in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_17(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'XXcodex-digestXX' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_18(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'CODEX-DIGEST' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_19(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' not in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_20(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(None)
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_21(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return True
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_22(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = None
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_23(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(None)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_24(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(None)
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_25(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return True
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_26(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) and 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_27(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_28(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'XXjobsXX' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_29(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'JOBS' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_30(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_31(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return True
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_32(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = None
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_33(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = True
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_34(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['XXjobsXX'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_35(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['JOBS'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_36(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) and 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_37(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_38(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'XXstepsXX' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_39(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'STEPS' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_40(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_41(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                break
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_42(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = None
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_43(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'XXnameXX': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_44(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'NAME': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_45(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'XXGenerate context digestXX',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_46(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_47(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'GENERATE CONTEXT DIGEST',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_48(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'XXrunXX': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_49(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'RUN': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_50(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'XXpython -m codex_digest --output context_summary.mdXX',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_51(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'PYTHON -M CODEX_DIGEST --OUTPUT CONTEXT_SUMMARY.MD',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_52(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'XXifXX': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_53(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'IF': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_54(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'XXalways()XX'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_55(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'ALWAYS()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_56(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(None)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_57(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['XXstepsXX'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_58(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['STEPS'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_59(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = None
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_60(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = False
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_61(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(None)
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_62(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            return  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_63(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(None, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_64(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, None) as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_65(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open('w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_66(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, ) as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_67(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'XXwXX') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_68(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'W') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_69(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(None, f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_70(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, None, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_71(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=None, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_72(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=None)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_73(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(f, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_74(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, default_flow_style=False, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_75(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_76(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, )
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_77(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=True, sort_keys=False)
        
        return modified
    
    def xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_78(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False
        
        # Read workflow
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check if codex_digest already present
        if 'codex_digest' in content or 'codex-digest' in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse {workflow_path.name}: {e}")
            return False
        
        if not isinstance(data, dict) or 'jobs' not in data:
            return False
        
        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data['jobs'].items():
            if not isinstance(job_config, dict) or 'steps' not in job_config:
                continue
            
            # Add step
            digest_step = {
                'name': 'Generate context digest',
                'run': 'python -m codex_digest --output context_summary.md',
                'if': 'always()'
            }
            
            job_config['steps'].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job
        
        if modified:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=True)
        
        return modified
    
    xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_1': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_1, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_2': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_2, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_3': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_3, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_4': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_4, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_5': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_5, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_6': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_6, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_7': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_7, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_8': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_8, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_9': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_9, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_10': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_10, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_11': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_11, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_12': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_12, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_13': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_13, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_14': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_14, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_15': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_15, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_16': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_16, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_17': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_17, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_18': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_18, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_19': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_19, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_20': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_20, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_21': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_21, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_22': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_22, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_23': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_23, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_24': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_24, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_25': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_25, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_26': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_26, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_27': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_27, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_28': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_28, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_29': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_29, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_30': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_30, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_31': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_31, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_32': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_32, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_33': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_33, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_34': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_34, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_35': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_35, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_36': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_36, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_37': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_37, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_38': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_38, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_39': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_39, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_40': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_40, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_41': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_41, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_42': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_42, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_43': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_43, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_44': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_44, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_45': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_45, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_46': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_46, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_47': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_47, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_48': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_48, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_49': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_49, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_50': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_50, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_51': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_51, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_52': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_52, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_53': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_53, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_54': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_54, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_55': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_55, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_56': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_56, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_57': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_57, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_58': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_58, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_59': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_59, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_60': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_60, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_61': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_61, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_62': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_62, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_63': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_63, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_64': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_64, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_65': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_65, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_66': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_66, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_67': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_67, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_68': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_68, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_69': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_69, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_70': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_70, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_71': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_71, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_72': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_72, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_73': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_73, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_74': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_74, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_75': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_75, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_76': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_76, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_77': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_77, 
        'xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_78': xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_78
    }
    
    def add_codex_digest_step(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_orig"), object.__getattribute__(self, "xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_mutants"), args, kwargs, self)
        return result 
    
    add_codex_digest_step.__signature__ = _mutmut_signature(xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_orig)
    xǁWorkflowRefactorerǁadd_codex_digest_step__mutmut_orig.__name__ = 'xǁWorkflowRefactorerǁadd_codex_digest_step'
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_orig(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_1(
        self,
        add_dispatch: bool = False,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_2(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = False,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_3(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = True
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_4(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = None
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_5(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = None
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_6(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "XXtotal_workflowsXX": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_7(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "TOTAL_WORKFLOWS": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_8(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "XXdispatch_addedXX": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_9(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "DISPATCH_ADDED": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_10(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 1,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_11(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "XXrunner_updatedXX": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_12(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "RUNNER_UPDATED": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_13(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 1,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_14(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "XXdigest_addedXX": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_15(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "DIGEST_ADDED": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_16(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 1,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_17(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "XXerrorsXX": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_18(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "ERRORS": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_19(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(None):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_20(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] = 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_21(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] -= 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_22(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["XXdispatch_addedXX"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_23(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["DISPATCH_ADDED"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_24(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 2
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_25(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = None
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_26(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(None)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_27(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get(None):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_28(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("XXmodifiedXX"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_29(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("MODIFIED"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_30(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] = 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_31(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] -= 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_32(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["XXrunner_updatedXX"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_33(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["RUNNER_UPDATED"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_34(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 2
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_35(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(None):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_36(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] = 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_37(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] -= 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_38(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["XXdigest_addedXX"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_39(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["DIGEST_ADDED"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_40(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 2
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_41(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(None)
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_42(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append(None)
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_43(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["XXerrorsXX"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_44(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["ERRORS"].append({
                    "workflow": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_45(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "XXworkflowXX": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_46(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "WORKFLOW": workflow_path.name,
                    "error": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_47(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "XXerrorXX": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_48(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "ERROR": str(e)
                })
        
        return results
    
    def xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_49(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False
    ) -> Dict[str, Any]:
        """
        Refactor all workflows in directory.
        
        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps
            
        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()
        
        results = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": []
        }
        
        for workflow_path in workflows:
            try:
                if add_dispatch:
                    if self.add_workflow_dispatch(workflow_path):
                        results["dispatch_added"] += 1
                
                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1
                
                if add_digest:
                    if self.add_codex_digest_step(workflow_path):
                        results["digest_added"] += 1
            
            except Exception as e:
                logger.error(f"Error processing {workflow_path.name}: {e}")
                results["errors"].append({
                    "workflow": workflow_path.name,
                    "error": str(None)
                })
        
        return results
    
    xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_1': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_1, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_2': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_2, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_3': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_3, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_4': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_4, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_5': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_5, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_6': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_6, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_7': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_7, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_8': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_8, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_9': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_9, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_10': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_10, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_11': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_11, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_12': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_12, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_13': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_13, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_14': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_14, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_15': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_15, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_16': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_16, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_17': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_17, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_18': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_18, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_19': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_19, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_20': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_20, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_21': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_21, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_22': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_22, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_23': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_23, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_24': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_24, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_25': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_25, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_26': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_26, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_27': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_27, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_28': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_28, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_29': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_29, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_30': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_30, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_31': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_31, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_32': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_32, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_33': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_33, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_34': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_34, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_35': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_35, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_36': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_36, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_37': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_37, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_38': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_38, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_39': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_39, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_40': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_40, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_41': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_41, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_42': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_42, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_43': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_43, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_44': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_44, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_45': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_45, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_46': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_46, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_47': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_47, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_48': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_48, 
        'xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_49': xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_49
    }
    
    def refactor_all_workflows(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_orig"), object.__getattribute__(self, "xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_mutants"), args, kwargs, self)
        return result 
    
    refactor_all_workflows.__signature__ = _mutmut_signature(xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_orig)
    xǁWorkflowRefactorerǁrefactor_all_workflows__mutmut_orig.__name__ = 'xǁWorkflowRefactorerǁrefactor_all_workflows'
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_orig(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_1(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"XXvalidXX": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_2(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"VALID": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_3(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": True, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_4(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "XXerrorXX": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_5(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "ERROR": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_6(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "XXPyYAML not installedXX"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_7(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "pyyaml not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_8(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PYYAML NOT INSTALLED"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_9(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(None, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_10(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, None) as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_11(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open('r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_12(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, ) as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_13(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'XXrXX') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_14(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'R') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_15(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = None
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_16(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(None)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_17(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_18(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"XXvalidXX": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_19(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"VALID": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_20(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": True, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_21(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "XXerrorXX": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_22(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "ERROR": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_23(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "XXNot a valid YAML dictXX"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_24(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "not a valid yaml dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_25(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "NOT A VALID YAML DICT"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_26(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'XXonXX' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_27(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'ON' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_28(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_29(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"XXvalidXX": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_30(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"VALID": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_31(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": True, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_32(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "XXerrorXX": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_33(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "ERROR": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_34(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "XXMissing 'on' triggerXX"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_35(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_36(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "MISSING 'ON' TRIGGER"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_37(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'XXjobsXX' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_38(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'JOBS' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_39(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_40(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"XXvalidXX": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_41(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"VALID": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_42(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": True, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_43(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "XXerrorXX": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_44(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "ERROR": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_45(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "XXMissing 'jobs' sectionXX"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_46(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_47(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "MISSING 'JOBS' SECTION"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_48(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = None
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_49(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = True
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_50(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = None
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_51(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'XXworkflow_dispatchXX' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_52(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'WORKFLOW_DISPATCH' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_53(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' not in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_54(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['XXonXX']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_55(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['ON']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_56(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = None
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_57(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'XXworkflow_dispatchXX' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_58(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'WORKFLOW_DISPATCH' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_59(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' not in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_60(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['XXonXX']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_61(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['ON']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_62(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = None
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_63(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 1
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_64(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = None
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_65(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['XXjobsXX'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_66(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['JOBS'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_67(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = None
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_68(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get(None, [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_69(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', None)
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_70(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get([])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_71(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', )
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_72(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('XXruns-onXX', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_73(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('RUNS-ON', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_74(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on or 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_75(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'XXself-hostedXX' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_76(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'SELF-HOSTED' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_77(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' not in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_78(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'XXlinuxXX' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_79(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'LINUX' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_80(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' not in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_81(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted = 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_82(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted -= 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_83(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 2
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_84(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "XXvalidXX": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_85(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "VALID": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_86(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": False,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_87(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "XXhas_workflow_dispatchXX": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_88(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "HAS_WORKFLOW_DISPATCH": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_89(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "XXtotal_jobsXX": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_90(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "TOTAL_JOBS": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_91(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "XXjobs_with_self_hostedXX": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_92(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "JOBS_WITH_SELF_HOSTED": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_93(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "XXcomplianceXX": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_94(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "COMPLIANCE": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_95(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted != total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_96(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"XXvalidXX": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_97(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"VALID": False, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_98(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": True, "error": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_99(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "XXerrorXX": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_100(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "ERROR": str(e)}
    
    def xǁWorkflowRefactorerǁvalidate_workflow__mutmut_101(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Validate workflow file.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}
        
        try:
            with open(workflow_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}
            
            if 'on' not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}
            
            if 'jobs' not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}
            
            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data['on'], dict):
                has_dispatch = 'workflow_dispatch' in data['on']
            elif isinstance(data['on'], list):
                has_dispatch = 'workflow_dispatch' in data['on']
            
            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data['jobs'])
            
            for job_config in data['jobs'].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get('runs-on', [])
                    if isinstance(runs_on, list):
                        if 'self-hosted' in runs_on and 'linux' in runs_on:
                            jobs_with_self_hosted += 1
            
            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs
            }
        
        except Exception as e:
            return {"valid": False, "error": str(None)}
    
    xǁWorkflowRefactorerǁvalidate_workflow__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_1': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_1, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_2': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_2, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_3': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_3, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_4': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_4, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_5': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_5, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_6': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_6, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_7': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_7, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_8': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_8, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_9': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_9, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_10': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_10, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_11': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_11, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_12': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_12, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_13': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_13, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_14': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_14, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_15': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_15, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_16': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_16, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_17': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_17, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_18': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_18, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_19': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_19, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_20': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_20, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_21': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_21, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_22': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_22, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_23': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_23, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_24': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_24, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_25': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_25, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_26': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_26, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_27': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_27, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_28': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_28, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_29': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_29, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_30': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_30, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_31': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_31, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_32': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_32, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_33': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_33, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_34': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_34, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_35': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_35, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_36': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_36, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_37': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_37, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_38': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_38, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_39': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_39, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_40': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_40, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_41': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_41, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_42': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_42, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_43': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_43, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_44': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_44, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_45': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_45, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_46': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_46, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_47': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_47, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_48': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_48, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_49': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_49, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_50': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_50, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_51': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_51, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_52': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_52, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_53': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_53, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_54': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_54, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_55': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_55, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_56': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_56, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_57': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_57, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_58': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_58, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_59': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_59, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_60': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_60, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_61': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_61, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_62': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_62, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_63': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_63, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_64': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_64, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_65': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_65, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_66': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_66, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_67': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_67, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_68': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_68, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_69': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_69, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_70': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_70, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_71': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_71, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_72': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_72, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_73': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_73, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_74': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_74, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_75': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_75, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_76': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_76, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_77': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_77, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_78': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_78, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_79': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_79, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_80': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_80, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_81': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_81, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_82': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_82, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_83': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_83, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_84': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_84, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_85': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_85, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_86': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_86, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_87': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_87, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_88': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_88, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_89': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_89, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_90': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_90, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_91': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_91, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_92': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_92, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_93': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_93, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_94': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_94, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_95': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_95, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_96': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_96, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_97': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_97, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_98': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_98, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_99': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_99, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_100': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_100, 
        'xǁWorkflowRefactorerǁvalidate_workflow__mutmut_101': xǁWorkflowRefactorerǁvalidate_workflow__mutmut_101
    }
    
    def validate_workflow(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁWorkflowRefactorerǁvalidate_workflow__mutmut_orig"), object.__getattribute__(self, "xǁWorkflowRefactorerǁvalidate_workflow__mutmut_mutants"), args, kwargs, self)
        return result 
    
    validate_workflow.__signature__ = _mutmut_signature(xǁWorkflowRefactorerǁvalidate_workflow__mutmut_orig)
    xǁWorkflowRefactorerǁvalidate_workflow__mutmut_orig.__name__ = 'xǁWorkflowRefactorerǁvalidate_workflow'


def x_refactor_workflows__mutmut_orig(
    add_dispatch: bool = True,
    ensure_self_hosted: bool = True,
    add_digest: bool = False
) -> Dict[str, Any]:
    """
    Convenience function to refactor all workflows.
    
    Args:
        add_dispatch: Add workflow_dispatch triggers
        ensure_self_hosted: Ensure self-hosted, linux runners
        add_digest: Add codex_digest steps
        
    Returns:
        Summary of changes
    """
    refactorer = WorkflowRefactorer()
    return refactorer.refactor_all_workflows(
        add_dispatch=add_dispatch,
        ensure_self_hosted=ensure_self_hosted,
        add_digest=add_digest
    )


def x_refactor_workflows__mutmut_1(
    add_dispatch: bool = False,
    ensure_self_hosted: bool = True,
    add_digest: bool = False
) -> Dict[str, Any]:
    """
    Convenience function to refactor all workflows.
    
    Args:
        add_dispatch: Add workflow_dispatch triggers
        ensure_self_hosted: Ensure self-hosted, linux runners
        add_digest: Add codex_digest steps
        
    Returns:
        Summary of changes
    """
    refactorer = WorkflowRefactorer()
    return refactorer.refactor_all_workflows(
        add_dispatch=add_dispatch,
        ensure_self_hosted=ensure_self_hosted,
        add_digest=add_digest
    )


def x_refactor_workflows__mutmut_2(
    add_dispatch: bool = True,
    ensure_self_hosted: bool = False,
    add_digest: bool = False
) -> Dict[str, Any]:
    """
    Convenience function to refactor all workflows.
    
    Args:
        add_dispatch: Add workflow_dispatch triggers
        ensure_self_hosted: Ensure self-hosted, linux runners
        add_digest: Add codex_digest steps
        
    Returns:
        Summary of changes
    """
    refactorer = WorkflowRefactorer()
    return refactorer.refactor_all_workflows(
        add_dispatch=add_dispatch,
        ensure_self_hosted=ensure_self_hosted,
        add_digest=add_digest
    )


def x_refactor_workflows__mutmut_3(
    add_dispatch: bool = True,
    ensure_self_hosted: bool = True,
    add_digest: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to refactor all workflows.
    
    Args:
        add_dispatch: Add workflow_dispatch triggers
        ensure_self_hosted: Ensure self-hosted, linux runners
        add_digest: Add codex_digest steps
        
    Returns:
        Summary of changes
    """
    refactorer = WorkflowRefactorer()
    return refactorer.refactor_all_workflows(
        add_dispatch=add_dispatch,
        ensure_self_hosted=ensure_self_hosted,
        add_digest=add_digest
    )


def x_refactor_workflows__mutmut_4(
    add_dispatch: bool = True,
    ensure_self_hosted: bool = True,
    add_digest: bool = False
) -> Dict[str, Any]:
    """
    Convenience function to refactor all workflows.
    
    Args:
        add_dispatch: Add workflow_dispatch triggers
        ensure_self_hosted: Ensure self-hosted, linux runners
        add_digest: Add codex_digest steps
        
    Returns:
        Summary of changes
    """
    refactorer = None
    return refactorer.refactor_all_workflows(
        add_dispatch=add_dispatch,
        ensure_self_hosted=ensure_self_hosted,
        add_digest=add_digest
    )


def x_refactor_workflows__mutmut_5(
    add_dispatch: bool = True,
    ensure_self_hosted: bool = True,
    add_digest: bool = False
) -> Dict[str, Any]:
    """
    Convenience function to refactor all workflows.
    
    Args:
        add_dispatch: Add workflow_dispatch triggers
        ensure_self_hosted: Ensure self-hosted, linux runners
        add_digest: Add codex_digest steps
        
    Returns:
        Summary of changes
    """
    refactorer = WorkflowRefactorer()
    return refactorer.refactor_all_workflows(
        add_dispatch=None,
        ensure_self_hosted=ensure_self_hosted,
        add_digest=add_digest
    )


def x_refactor_workflows__mutmut_6(
    add_dispatch: bool = True,
    ensure_self_hosted: bool = True,
    add_digest: bool = False
) -> Dict[str, Any]:
    """
    Convenience function to refactor all workflows.
    
    Args:
        add_dispatch: Add workflow_dispatch triggers
        ensure_self_hosted: Ensure self-hosted, linux runners
        add_digest: Add codex_digest steps
        
    Returns:
        Summary of changes
    """
    refactorer = WorkflowRefactorer()
    return refactorer.refactor_all_workflows(
        add_dispatch=add_dispatch,
        ensure_self_hosted=None,
        add_digest=add_digest
    )


def x_refactor_workflows__mutmut_7(
    add_dispatch: bool = True,
    ensure_self_hosted: bool = True,
    add_digest: bool = False
) -> Dict[str, Any]:
    """
    Convenience function to refactor all workflows.
    
    Args:
        add_dispatch: Add workflow_dispatch triggers
        ensure_self_hosted: Ensure self-hosted, linux runners
        add_digest: Add codex_digest steps
        
    Returns:
        Summary of changes
    """
    refactorer = WorkflowRefactorer()
    return refactorer.refactor_all_workflows(
        add_dispatch=add_dispatch,
        ensure_self_hosted=ensure_self_hosted,
        add_digest=None
    )


def x_refactor_workflows__mutmut_8(
    add_dispatch: bool = True,
    ensure_self_hosted: bool = True,
    add_digest: bool = False
) -> Dict[str, Any]:
    """
    Convenience function to refactor all workflows.
    
    Args:
        add_dispatch: Add workflow_dispatch triggers
        ensure_self_hosted: Ensure self-hosted, linux runners
        add_digest: Add codex_digest steps
        
    Returns:
        Summary of changes
    """
    refactorer = WorkflowRefactorer()
    return refactorer.refactor_all_workflows(
        ensure_self_hosted=ensure_self_hosted,
        add_digest=add_digest
    )


def x_refactor_workflows__mutmut_9(
    add_dispatch: bool = True,
    ensure_self_hosted: bool = True,
    add_digest: bool = False
) -> Dict[str, Any]:
    """
    Convenience function to refactor all workflows.
    
    Args:
        add_dispatch: Add workflow_dispatch triggers
        ensure_self_hosted: Ensure self-hosted, linux runners
        add_digest: Add codex_digest steps
        
    Returns:
        Summary of changes
    """
    refactorer = WorkflowRefactorer()
    return refactorer.refactor_all_workflows(
        add_dispatch=add_dispatch,
        add_digest=add_digest
    )


def x_refactor_workflows__mutmut_10(
    add_dispatch: bool = True,
    ensure_self_hosted: bool = True,
    add_digest: bool = False
) -> Dict[str, Any]:
    """
    Convenience function to refactor all workflows.
    
    Args:
        add_dispatch: Add workflow_dispatch triggers
        ensure_self_hosted: Ensure self-hosted, linux runners
        add_digest: Add codex_digest steps
        
    Returns:
        Summary of changes
    """
    refactorer = WorkflowRefactorer()
    return refactorer.refactor_all_workflows(
        add_dispatch=add_dispatch,
        ensure_self_hosted=ensure_self_hosted,
        )

x_refactor_workflows__mutmut_mutants : ClassVar[MutantDict] = {
'x_refactor_workflows__mutmut_1': x_refactor_workflows__mutmut_1, 
    'x_refactor_workflows__mutmut_2': x_refactor_workflows__mutmut_2, 
    'x_refactor_workflows__mutmut_3': x_refactor_workflows__mutmut_3, 
    'x_refactor_workflows__mutmut_4': x_refactor_workflows__mutmut_4, 
    'x_refactor_workflows__mutmut_5': x_refactor_workflows__mutmut_5, 
    'x_refactor_workflows__mutmut_6': x_refactor_workflows__mutmut_6, 
    'x_refactor_workflows__mutmut_7': x_refactor_workflows__mutmut_7, 
    'x_refactor_workflows__mutmut_8': x_refactor_workflows__mutmut_8, 
    'x_refactor_workflows__mutmut_9': x_refactor_workflows__mutmut_9, 
    'x_refactor_workflows__mutmut_10': x_refactor_workflows__mutmut_10
}

def refactor_workflows(*args, **kwargs):
    result = _mutmut_trampoline(x_refactor_workflows__mutmut_orig, x_refactor_workflows__mutmut_mutants, args, kwargs)
    return result 

refactor_workflows.__signature__ = _mutmut_signature(x_refactor_workflows__mutmut_orig)
x_refactor_workflows__mutmut_orig.__name__ = 'x_refactor_workflows'


if __name__ == "__main__":
    # Run refactoring when executed as script
    import json
    
    print("🔧 CI/CD Workflow Refactoring Utility\n")
    print("Scanning workflows...\n")
    
    results = refactor_workflows(
        add_dispatch=False,  # Dry run mode for safety
        ensure_self_hosted=False,
        add_digest=False
    )
    
    print("Results:")
    print(json.dumps(results, indent=2))
