"""
Reference Python plugin implementation.
"""
from pathlib import Path

from codex.ast import parse_python
from codex.ast.node import StandardizedASTNode
from . import ASTPlugin, PluginMetadata
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


class PythonPlugin(ASTPlugin):
    """
    Python language plugin using existing codex parser.
    
    This serves as a reference implementation for other language plugins.
    """
    
    @property
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="python",
            version="1.0.0",
            author="Codex Team",
            description="Python AST parser using libcst",
            languages=["python"],
            file_extensions=[".py", ".pyw"]
        )
    
    @property
    def language(self) -> str:
        """Return language name."""
        return "python"
    
    @property
    def file_extensions(self) -> list[str]:
        """Return supported file extensions."""
        return [".py", ".pyw"]
    
    def xǁPythonPluginǁcan_parse__mutmut_orig(self, file_path: str) -> bool:
        """Check if this plugin can parse the file."""
        ext = Path(file_path).suffix.lower()
        return ext in self.file_extensions
    
    def xǁPythonPluginǁcan_parse__mutmut_1(self, file_path: str) -> bool:
        """Check if this plugin can parse the file."""
        ext = None
        return ext in self.file_extensions
    
    def xǁPythonPluginǁcan_parse__mutmut_2(self, file_path: str) -> bool:
        """Check if this plugin can parse the file."""
        ext = Path(file_path).suffix.upper()
        return ext in self.file_extensions
    
    def xǁPythonPluginǁcan_parse__mutmut_3(self, file_path: str) -> bool:
        """Check if this plugin can parse the file."""
        ext = Path(None).suffix.lower()
        return ext in self.file_extensions
    
    def xǁPythonPluginǁcan_parse__mutmut_4(self, file_path: str) -> bool:
        """Check if this plugin can parse the file."""
        ext = Path(file_path).suffix.lower()
        return ext not in self.file_extensions
    
    xǁPythonPluginǁcan_parse__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPythonPluginǁcan_parse__mutmut_1': xǁPythonPluginǁcan_parse__mutmut_1, 
        'xǁPythonPluginǁcan_parse__mutmut_2': xǁPythonPluginǁcan_parse__mutmut_2, 
        'xǁPythonPluginǁcan_parse__mutmut_3': xǁPythonPluginǁcan_parse__mutmut_3, 
        'xǁPythonPluginǁcan_parse__mutmut_4': xǁPythonPluginǁcan_parse__mutmut_4
    }
    
    def can_parse(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPythonPluginǁcan_parse__mutmut_orig"), object.__getattribute__(self, "xǁPythonPluginǁcan_parse__mutmut_mutants"), args, kwargs, self)
        return result 
    
    can_parse.__signature__ = _mutmut_signature(xǁPythonPluginǁcan_parse__mutmut_orig)
    xǁPythonPluginǁcan_parse__mutmut_orig.__name__ = 'xǁPythonPluginǁcan_parse'
    
    def xǁPythonPluginǁparse__mutmut_orig(self, code: str, file_path: str) -> StandardizedASTNode:
        """Parse Python code using existing parser."""
        # Use existing codex parser
        return parse_python(code, file_path)
    
    def xǁPythonPluginǁparse__mutmut_1(self, code: str, file_path: str) -> StandardizedASTNode:
        """Parse Python code using existing parser."""
        # Use existing codex parser
        return parse_python(None, file_path)
    
    def xǁPythonPluginǁparse__mutmut_2(self, code: str, file_path: str) -> StandardizedASTNode:
        """Parse Python code using existing parser."""
        # Use existing codex parser
        return parse_python(code, None)
    
    def xǁPythonPluginǁparse__mutmut_3(self, code: str, file_path: str) -> StandardizedASTNode:
        """Parse Python code using existing parser."""
        # Use existing codex parser
        return parse_python(file_path)
    
    def xǁPythonPluginǁparse__mutmut_4(self, code: str, file_path: str) -> StandardizedASTNode:
        """Parse Python code using existing parser."""
        # Use existing codex parser
        return parse_python(code, )
    
    xǁPythonPluginǁparse__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPythonPluginǁparse__mutmut_1': xǁPythonPluginǁparse__mutmut_1, 
        'xǁPythonPluginǁparse__mutmut_2': xǁPythonPluginǁparse__mutmut_2, 
        'xǁPythonPluginǁparse__mutmut_3': xǁPythonPluginǁparse__mutmut_3, 
        'xǁPythonPluginǁparse__mutmut_4': xǁPythonPluginǁparse__mutmut_4
    }
    
    def parse(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPythonPluginǁparse__mutmut_orig"), object.__getattribute__(self, "xǁPythonPluginǁparse__mutmut_mutants"), args, kwargs, self)
        return result 
    
    parse.__signature__ = _mutmut_signature(xǁPythonPluginǁparse__mutmut_orig)
    xǁPythonPluginǁparse__mutmut_orig.__name__ = 'xǁPythonPluginǁparse'
    
    def xǁPythonPluginǁvalidate__mutmut_orig(self) -> bool:
        """Validate plugin is ready."""
        try:
            import libcst  # noqa: F401 - Testing optional dependency availability
            return True
        except ImportError:
            return False
    
    def xǁPythonPluginǁvalidate__mutmut_1(self) -> bool:
        """Validate plugin is ready."""
        try:
            import libcst  # noqa: F401 - Testing optional dependency availability
            return False
        except ImportError:
            return False
    
    def xǁPythonPluginǁvalidate__mutmut_2(self) -> bool:
        """Validate plugin is ready."""
        try:
            import libcst  # noqa: F401 - Testing optional dependency availability
            return True
        except ImportError:
            return True
    
    xǁPythonPluginǁvalidate__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPythonPluginǁvalidate__mutmut_1': xǁPythonPluginǁvalidate__mutmut_1, 
        'xǁPythonPluginǁvalidate__mutmut_2': xǁPythonPluginǁvalidate__mutmut_2
    }
    
    def validate(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPythonPluginǁvalidate__mutmut_orig"), object.__getattribute__(self, "xǁPythonPluginǁvalidate__mutmut_mutants"), args, kwargs, self)
        return result 
    
    validate.__signature__ = _mutmut_signature(xǁPythonPluginǁvalidate__mutmut_orig)
    xǁPythonPluginǁvalidate__mutmut_orig.__name__ = 'xǁPythonPluginǁvalidate'
