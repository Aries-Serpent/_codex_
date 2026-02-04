"""
AST Plugin Architecture.

Provides base interface for extending AST analysis to new languages
and custom analysis tools.
"""
from abc import ABC, abstractmethod
from typing import Optional, Any
from pathlib import Path
from dataclasses import dataclass

from codex.ast.node import StandardizedASTNode
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
class PluginMetadata:
    """Metadata about a plugin."""
    name: str
    version: str
    author: str
    description: str
    languages: list[str]
    file_extensions: list[str]


class ASTPlugin(ABC):
    """
    Base class for AST analysis plugins.
    
    Implement this interface to add support for new languages
    or custom analysis capabilities.
    """
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        pass
    
    @property
    @abstractmethod
    def language(self) -> str:
        """
        Return primary language name this plugin handles.
        
        Examples: 'python', 'javascript', 'rust'
        """
        pass
    
    @property
    @abstractmethod
    def file_extensions(self) -> list[str]:
        """
        Return list of file extensions this plugin handles.
        
        Examples: ['.py', '.pyw'], ['.js', '.jsx']
        """
        pass
    
    @abstractmethod
    def can_parse(self, file_path: str) -> bool:
        """
        Check if this plugin can parse the given file.
        
        Args:
            file_path: Path to file to check
            
        Returns:
            True if plugin can handle this file
        """
        pass
    
    @abstractmethod
    def parse(self, code: str, file_path: str) -> StandardizedASTNode:
        """
        Parse code and return standardized AST node.
        
        Args:
            code: Source code to parse
            file_path: Path to source file
            
        Returns:
            StandardizedASTNode representing the AST
            
        Raises:
            SyntaxError: If code cannot be parsed
        """
        pass
    
    def analyze(self, node: StandardizedASTNode) -> dict[str, Any]:
        """
        Perform custom analysis on AST node.
        
        Optional hook for plugins to provide additional analysis.
        
        Args:
            node: AST node to analyze
            
        Returns:
            Dictionary of analysis results
        """
        return {}
    
    def xǁASTPluginǁvalidate__mutmut_orig(self) -> bool:
        """
        Validate plugin is properly configured.
        
        Returns:
            True if plugin is ready to use
        """
        return True
    
    def xǁASTPluginǁvalidate__mutmut_1(self) -> bool:
        """
        Validate plugin is properly configured.
        
        Returns:
            True if plugin is ready to use
        """
        return False
    
    xǁASTPluginǁvalidate__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁASTPluginǁvalidate__mutmut_1': xǁASTPluginǁvalidate__mutmut_1
    }
    
    def validate(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁASTPluginǁvalidate__mutmut_orig"), object.__getattribute__(self, "xǁASTPluginǁvalidate__mutmut_mutants"), args, kwargs, self)
        return result 
    
    validate.__signature__ = _mutmut_signature(xǁASTPluginǁvalidate__mutmut_orig)
    xǁASTPluginǁvalidate__mutmut_orig.__name__ = 'xǁASTPluginǁvalidate'


class AnalysisPlugin(ABC):
    """
    Base class for custom analysis plugins.
    
    Use this for plugins that analyze existing AST nodes
    rather than parsing new languages.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return plugin name."""
        pass
    
    @abstractmethod
    def analyze(self, node: StandardizedASTNode) -> dict[str, Any]:
        """
        Analyze an AST node.
        
        Args:
            node: Node to analyze
            
        Returns:
            Analysis results
        """
        pass


__all__ = ['ASTPlugin', 'AnalysisPlugin', 'PluginMetadata']
