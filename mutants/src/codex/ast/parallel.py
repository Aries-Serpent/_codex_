"""
Parallel AST parsing for improved performance.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Optional
from pathlib import Path
import threading
import logging

from .parser import parse_python
from .node import StandardizedASTNode

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


class ParallelParser:
    """
    Parse multiple files concurrently using thread pool.
    
    Provides thread-safe node ID generation and progress tracking.
    """
    
    def xǁParallelParserǁ__init____mutmut_orig(self, max_workers: Optional[int] = None):
        """
        Initialize parallel parser.
        
        Args:
            max_workers: Maximum number of worker threads (None = CPU count)
        """
        self.max_workers = max_workers
        self._node_id_counter = 0
        self._lock = threading.Lock()
    
    def xǁParallelParserǁ__init____mutmut_1(self, max_workers: Optional[int] = None):
        """
        Initialize parallel parser.
        
        Args:
            max_workers: Maximum number of worker threads (None = CPU count)
        """
        self.max_workers = None
        self._node_id_counter = 0
        self._lock = threading.Lock()
    
    def xǁParallelParserǁ__init____mutmut_2(self, max_workers: Optional[int] = None):
        """
        Initialize parallel parser.
        
        Args:
            max_workers: Maximum number of worker threads (None = CPU count)
        """
        self.max_workers = max_workers
        self._node_id_counter = None
        self._lock = threading.Lock()
    
    def xǁParallelParserǁ__init____mutmut_3(self, max_workers: Optional[int] = None):
        """
        Initialize parallel parser.
        
        Args:
            max_workers: Maximum number of worker threads (None = CPU count)
        """
        self.max_workers = max_workers
        self._node_id_counter = 1
        self._lock = threading.Lock()
    
    def xǁParallelParserǁ__init____mutmut_4(self, max_workers: Optional[int] = None):
        """
        Initialize parallel parser.
        
        Args:
            max_workers: Maximum number of worker threads (None = CPU count)
        """
        self.max_workers = max_workers
        self._node_id_counter = 0
        self._lock = None
    
    xǁParallelParserǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁParallelParserǁ__init____mutmut_1': xǁParallelParserǁ__init____mutmut_1, 
        'xǁParallelParserǁ__init____mutmut_2': xǁParallelParserǁ__init____mutmut_2, 
        'xǁParallelParserǁ__init____mutmut_3': xǁParallelParserǁ__init____mutmut_3, 
        'xǁParallelParserǁ__init____mutmut_4': xǁParallelParserǁ__init____mutmut_4
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁParallelParserǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁParallelParserǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁParallelParserǁ__init____mutmut_orig)
    xǁParallelParserǁ__init____mutmut_orig.__name__ = 'xǁParallelParserǁ__init__'
    
    def xǁParallelParserǁ_generate_node_id__mutmut_orig(self) -> int:
        """Generate thread-safe unique node ID."""
        with self._lock:
            self._node_id_counter += 1
            return self._node_id_counter
    
    def xǁParallelParserǁ_generate_node_id__mutmut_1(self) -> int:
        """Generate thread-safe unique node ID."""
        with self._lock:
            self._node_id_counter = 1
            return self._node_id_counter
    
    def xǁParallelParserǁ_generate_node_id__mutmut_2(self) -> int:
        """Generate thread-safe unique node ID."""
        with self._lock:
            self._node_id_counter -= 1
            return self._node_id_counter
    
    def xǁParallelParserǁ_generate_node_id__mutmut_3(self) -> int:
        """Generate thread-safe unique node ID."""
        with self._lock:
            self._node_id_counter += 2
            return self._node_id_counter
    
    xǁParallelParserǁ_generate_node_id__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁParallelParserǁ_generate_node_id__mutmut_1': xǁParallelParserǁ_generate_node_id__mutmut_1, 
        'xǁParallelParserǁ_generate_node_id__mutmut_2': xǁParallelParserǁ_generate_node_id__mutmut_2, 
        'xǁParallelParserǁ_generate_node_id__mutmut_3': xǁParallelParserǁ_generate_node_id__mutmut_3
    }
    
    def _generate_node_id(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁParallelParserǁ_generate_node_id__mutmut_orig"), object.__getattribute__(self, "xǁParallelParserǁ_generate_node_id__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _generate_node_id.__signature__ = _mutmut_signature(xǁParallelParserǁ_generate_node_id__mutmut_orig)
    xǁParallelParserǁ_generate_node_id__mutmut_orig.__name__ = 'xǁParallelParserǁ_generate_node_id'
    
    def xǁParallelParserǁparse_files__mutmut_orig(
        self,
        file_paths: list[str],
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse multiple files in parallel.
        
        Args:
            file_paths: list of file paths to parse
            progress_callback: Optional callback(file_path, completed, total)
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        results = {}
        total = len(file_paths)
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all parse tasks
            future_to_path = {
                executor.submit(self._parse_file, path): path
                for path in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_path):
                file_path = future_to_path[future]
                
                try:
                    node = future.result()
                    if node:
                        results[file_path] = node
                except Exception as e:
                    logger.error(f"Failed to parse {file_path}: {e}")
                
                # Update progress
                completed += 1
                if progress_callback:
                    progress_callback(file_path, completed, total)
        
        return results
    
    def xǁParallelParserǁparse_files__mutmut_1(
        self,
        file_paths: list[str],
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse multiple files in parallel.
        
        Args:
            file_paths: list of file paths to parse
            progress_callback: Optional callback(file_path, completed, total)
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        results = None
        total = len(file_paths)
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all parse tasks
            future_to_path = {
                executor.submit(self._parse_file, path): path
                for path in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_path):
                file_path = future_to_path[future]
                
                try:
                    node = future.result()
                    if node:
                        results[file_path] = node
                except Exception as e:
                    logger.error(f"Failed to parse {file_path}: {e}")
                
                # Update progress
                completed += 1
                if progress_callback:
                    progress_callback(file_path, completed, total)
        
        return results
    
    def xǁParallelParserǁparse_files__mutmut_2(
        self,
        file_paths: list[str],
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse multiple files in parallel.
        
        Args:
            file_paths: list of file paths to parse
            progress_callback: Optional callback(file_path, completed, total)
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        results = {}
        total = None
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all parse tasks
            future_to_path = {
                executor.submit(self._parse_file, path): path
                for path in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_path):
                file_path = future_to_path[future]
                
                try:
                    node = future.result()
                    if node:
                        results[file_path] = node
                except Exception as e:
                    logger.error(f"Failed to parse {file_path}: {e}")
                
                # Update progress
                completed += 1
                if progress_callback:
                    progress_callback(file_path, completed, total)
        
        return results
    
    def xǁParallelParserǁparse_files__mutmut_3(
        self,
        file_paths: list[str],
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse multiple files in parallel.
        
        Args:
            file_paths: list of file paths to parse
            progress_callback: Optional callback(file_path, completed, total)
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        results = {}
        total = len(file_paths)
        completed = None
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all parse tasks
            future_to_path = {
                executor.submit(self._parse_file, path): path
                for path in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_path):
                file_path = future_to_path[future]
                
                try:
                    node = future.result()
                    if node:
                        results[file_path] = node
                except Exception as e:
                    logger.error(f"Failed to parse {file_path}: {e}")
                
                # Update progress
                completed += 1
                if progress_callback:
                    progress_callback(file_path, completed, total)
        
        return results
    
    def xǁParallelParserǁparse_files__mutmut_4(
        self,
        file_paths: list[str],
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse multiple files in parallel.
        
        Args:
            file_paths: list of file paths to parse
            progress_callback: Optional callback(file_path, completed, total)
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        results = {}
        total = len(file_paths)
        completed = 1
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all parse tasks
            future_to_path = {
                executor.submit(self._parse_file, path): path
                for path in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_path):
                file_path = future_to_path[future]
                
                try:
                    node = future.result()
                    if node:
                        results[file_path] = node
                except Exception as e:
                    logger.error(f"Failed to parse {file_path}: {e}")
                
                # Update progress
                completed += 1
                if progress_callback:
                    progress_callback(file_path, completed, total)
        
        return results
    
    def xǁParallelParserǁparse_files__mutmut_5(
        self,
        file_paths: list[str],
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse multiple files in parallel.
        
        Args:
            file_paths: list of file paths to parse
            progress_callback: Optional callback(file_path, completed, total)
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        results = {}
        total = len(file_paths)
        completed = 0
        
        with ThreadPoolExecutor(max_workers=None) as executor:
            # Submit all parse tasks
            future_to_path = {
                executor.submit(self._parse_file, path): path
                for path in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_path):
                file_path = future_to_path[future]
                
                try:
                    node = future.result()
                    if node:
                        results[file_path] = node
                except Exception as e:
                    logger.error(f"Failed to parse {file_path}: {e}")
                
                # Update progress
                completed += 1
                if progress_callback:
                    progress_callback(file_path, completed, total)
        
        return results
    
    def xǁParallelParserǁparse_files__mutmut_6(
        self,
        file_paths: list[str],
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse multiple files in parallel.
        
        Args:
            file_paths: list of file paths to parse
            progress_callback: Optional callback(file_path, completed, total)
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        results = {}
        total = len(file_paths)
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all parse tasks
            future_to_path = None
            
            # Collect results as they complete
            for future in as_completed(future_to_path):
                file_path = future_to_path[future]
                
                try:
                    node = future.result()
                    if node:
                        results[file_path] = node
                except Exception as e:
                    logger.error(f"Failed to parse {file_path}: {e}")
                
                # Update progress
                completed += 1
                if progress_callback:
                    progress_callback(file_path, completed, total)
        
        return results
    
    def xǁParallelParserǁparse_files__mutmut_7(
        self,
        file_paths: list[str],
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse multiple files in parallel.
        
        Args:
            file_paths: list of file paths to parse
            progress_callback: Optional callback(file_path, completed, total)
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        results = {}
        total = len(file_paths)
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all parse tasks
            future_to_path = {
                executor.submit(None, path): path
                for path in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_path):
                file_path = future_to_path[future]
                
                try:
                    node = future.result()
                    if node:
                        results[file_path] = node
                except Exception as e:
                    logger.error(f"Failed to parse {file_path}: {e}")
                
                # Update progress
                completed += 1
                if progress_callback:
                    progress_callback(file_path, completed, total)
        
        return results
    
    def xǁParallelParserǁparse_files__mutmut_8(
        self,
        file_paths: list[str],
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse multiple files in parallel.
        
        Args:
            file_paths: list of file paths to parse
            progress_callback: Optional callback(file_path, completed, total)
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        results = {}
        total = len(file_paths)
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all parse tasks
            future_to_path = {
                executor.submit(self._parse_file, None): path
                for path in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_path):
                file_path = future_to_path[future]
                
                try:
                    node = future.result()
                    if node:
                        results[file_path] = node
                except Exception as e:
                    logger.error(f"Failed to parse {file_path}: {e}")
                
                # Update progress
                completed += 1
                if progress_callback:
                    progress_callback(file_path, completed, total)
        
        return results
    
    def xǁParallelParserǁparse_files__mutmut_9(
        self,
        file_paths: list[str],
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse multiple files in parallel.
        
        Args:
            file_paths: list of file paths to parse
            progress_callback: Optional callback(file_path, completed, total)
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        results = {}
        total = len(file_paths)
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all parse tasks
            future_to_path = {
                executor.submit(path): path
                for path in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_path):
                file_path = future_to_path[future]
                
                try:
                    node = future.result()
                    if node:
                        results[file_path] = node
                except Exception as e:
                    logger.error(f"Failed to parse {file_path}: {e}")
                
                # Update progress
                completed += 1
                if progress_callback:
                    progress_callback(file_path, completed, total)
        
        return results
    
    def xǁParallelParserǁparse_files__mutmut_10(
        self,
        file_paths: list[str],
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse multiple files in parallel.
        
        Args:
            file_paths: list of file paths to parse
            progress_callback: Optional callback(file_path, completed, total)
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        results = {}
        total = len(file_paths)
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all parse tasks
            future_to_path = {
                executor.submit(self._parse_file, ): path
                for path in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_path):
                file_path = future_to_path[future]
                
                try:
                    node = future.result()
                    if node:
                        results[file_path] = node
                except Exception as e:
                    logger.error(f"Failed to parse {file_path}: {e}")
                
                # Update progress
                completed += 1
                if progress_callback:
                    progress_callback(file_path, completed, total)
        
        return results
    
    def xǁParallelParserǁparse_files__mutmut_11(
        self,
        file_paths: list[str],
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse multiple files in parallel.
        
        Args:
            file_paths: list of file paths to parse
            progress_callback: Optional callback(file_path, completed, total)
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        results = {}
        total = len(file_paths)
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all parse tasks
            future_to_path = {
                executor.submit(self._parse_file, path): path
                for path in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(None):
                file_path = future_to_path[future]
                
                try:
                    node = future.result()
                    if node:
                        results[file_path] = node
                except Exception as e:
                    logger.error(f"Failed to parse {file_path}: {e}")
                
                # Update progress
                completed += 1
                if progress_callback:
                    progress_callback(file_path, completed, total)
        
        return results
    
    def xǁParallelParserǁparse_files__mutmut_12(
        self,
        file_paths: list[str],
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse multiple files in parallel.
        
        Args:
            file_paths: list of file paths to parse
            progress_callback: Optional callback(file_path, completed, total)
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        results = {}
        total = len(file_paths)
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all parse tasks
            future_to_path = {
                executor.submit(self._parse_file, path): path
                for path in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_path):
                file_path = None
                
                try:
                    node = future.result()
                    if node:
                        results[file_path] = node
                except Exception as e:
                    logger.error(f"Failed to parse {file_path}: {e}")
                
                # Update progress
                completed += 1
                if progress_callback:
                    progress_callback(file_path, completed, total)
        
        return results
    
    def xǁParallelParserǁparse_files__mutmut_13(
        self,
        file_paths: list[str],
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse multiple files in parallel.
        
        Args:
            file_paths: list of file paths to parse
            progress_callback: Optional callback(file_path, completed, total)
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        results = {}
        total = len(file_paths)
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all parse tasks
            future_to_path = {
                executor.submit(self._parse_file, path): path
                for path in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_path):
                file_path = future_to_path[future]
                
                try:
                    node = None
                    if node:
                        results[file_path] = node
                except Exception as e:
                    logger.error(f"Failed to parse {file_path}: {e}")
                
                # Update progress
                completed += 1
                if progress_callback:
                    progress_callback(file_path, completed, total)
        
        return results
    
    def xǁParallelParserǁparse_files__mutmut_14(
        self,
        file_paths: list[str],
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse multiple files in parallel.
        
        Args:
            file_paths: list of file paths to parse
            progress_callback: Optional callback(file_path, completed, total)
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        results = {}
        total = len(file_paths)
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all parse tasks
            future_to_path = {
                executor.submit(self._parse_file, path): path
                for path in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_path):
                file_path = future_to_path[future]
                
                try:
                    node = future.result()
                    if node:
                        results[file_path] = None
                except Exception as e:
                    logger.error(f"Failed to parse {file_path}: {e}")
                
                # Update progress
                completed += 1
                if progress_callback:
                    progress_callback(file_path, completed, total)
        
        return results
    
    def xǁParallelParserǁparse_files__mutmut_15(
        self,
        file_paths: list[str],
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse multiple files in parallel.
        
        Args:
            file_paths: list of file paths to parse
            progress_callback: Optional callback(file_path, completed, total)
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        results = {}
        total = len(file_paths)
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all parse tasks
            future_to_path = {
                executor.submit(self._parse_file, path): path
                for path in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_path):
                file_path = future_to_path[future]
                
                try:
                    node = future.result()
                    if node:
                        results[file_path] = node
                except Exception as e:
                    logger.error(None)
                
                # Update progress
                completed += 1
                if progress_callback:
                    progress_callback(file_path, completed, total)
        
        return results
    
    def xǁParallelParserǁparse_files__mutmut_16(
        self,
        file_paths: list[str],
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse multiple files in parallel.
        
        Args:
            file_paths: list of file paths to parse
            progress_callback: Optional callback(file_path, completed, total)
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        results = {}
        total = len(file_paths)
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all parse tasks
            future_to_path = {
                executor.submit(self._parse_file, path): path
                for path in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_path):
                file_path = future_to_path[future]
                
                try:
                    node = future.result()
                    if node:
                        results[file_path] = node
                except Exception as e:
                    logger.error(f"Failed to parse {file_path}: {e}")
                
                # Update progress
                completed = 1
                if progress_callback:
                    progress_callback(file_path, completed, total)
        
        return results
    
    def xǁParallelParserǁparse_files__mutmut_17(
        self,
        file_paths: list[str],
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse multiple files in parallel.
        
        Args:
            file_paths: list of file paths to parse
            progress_callback: Optional callback(file_path, completed, total)
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        results = {}
        total = len(file_paths)
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all parse tasks
            future_to_path = {
                executor.submit(self._parse_file, path): path
                for path in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_path):
                file_path = future_to_path[future]
                
                try:
                    node = future.result()
                    if node:
                        results[file_path] = node
                except Exception as e:
                    logger.error(f"Failed to parse {file_path}: {e}")
                
                # Update progress
                completed -= 1
                if progress_callback:
                    progress_callback(file_path, completed, total)
        
        return results
    
    def xǁParallelParserǁparse_files__mutmut_18(
        self,
        file_paths: list[str],
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse multiple files in parallel.
        
        Args:
            file_paths: list of file paths to parse
            progress_callback: Optional callback(file_path, completed, total)
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        results = {}
        total = len(file_paths)
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all parse tasks
            future_to_path = {
                executor.submit(self._parse_file, path): path
                for path in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_path):
                file_path = future_to_path[future]
                
                try:
                    node = future.result()
                    if node:
                        results[file_path] = node
                except Exception as e:
                    logger.error(f"Failed to parse {file_path}: {e}")
                
                # Update progress
                completed += 2
                if progress_callback:
                    progress_callback(file_path, completed, total)
        
        return results
    
    def xǁParallelParserǁparse_files__mutmut_19(
        self,
        file_paths: list[str],
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse multiple files in parallel.
        
        Args:
            file_paths: list of file paths to parse
            progress_callback: Optional callback(file_path, completed, total)
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        results = {}
        total = len(file_paths)
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all parse tasks
            future_to_path = {
                executor.submit(self._parse_file, path): path
                for path in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_path):
                file_path = future_to_path[future]
                
                try:
                    node = future.result()
                    if node:
                        results[file_path] = node
                except Exception as e:
                    logger.error(f"Failed to parse {file_path}: {e}")
                
                # Update progress
                completed += 1
                if progress_callback:
                    progress_callback(None, completed, total)
        
        return results
    
    def xǁParallelParserǁparse_files__mutmut_20(
        self,
        file_paths: list[str],
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse multiple files in parallel.
        
        Args:
            file_paths: list of file paths to parse
            progress_callback: Optional callback(file_path, completed, total)
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        results = {}
        total = len(file_paths)
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all parse tasks
            future_to_path = {
                executor.submit(self._parse_file, path): path
                for path in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_path):
                file_path = future_to_path[future]
                
                try:
                    node = future.result()
                    if node:
                        results[file_path] = node
                except Exception as e:
                    logger.error(f"Failed to parse {file_path}: {e}")
                
                # Update progress
                completed += 1
                if progress_callback:
                    progress_callback(file_path, None, total)
        
        return results
    
    def xǁParallelParserǁparse_files__mutmut_21(
        self,
        file_paths: list[str],
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse multiple files in parallel.
        
        Args:
            file_paths: list of file paths to parse
            progress_callback: Optional callback(file_path, completed, total)
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        results = {}
        total = len(file_paths)
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all parse tasks
            future_to_path = {
                executor.submit(self._parse_file, path): path
                for path in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_path):
                file_path = future_to_path[future]
                
                try:
                    node = future.result()
                    if node:
                        results[file_path] = node
                except Exception as e:
                    logger.error(f"Failed to parse {file_path}: {e}")
                
                # Update progress
                completed += 1
                if progress_callback:
                    progress_callback(file_path, completed, None)
        
        return results
    
    def xǁParallelParserǁparse_files__mutmut_22(
        self,
        file_paths: list[str],
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse multiple files in parallel.
        
        Args:
            file_paths: list of file paths to parse
            progress_callback: Optional callback(file_path, completed, total)
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        results = {}
        total = len(file_paths)
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all parse tasks
            future_to_path = {
                executor.submit(self._parse_file, path): path
                for path in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_path):
                file_path = future_to_path[future]
                
                try:
                    node = future.result()
                    if node:
                        results[file_path] = node
                except Exception as e:
                    logger.error(f"Failed to parse {file_path}: {e}")
                
                # Update progress
                completed += 1
                if progress_callback:
                    progress_callback(completed, total)
        
        return results
    
    def xǁParallelParserǁparse_files__mutmut_23(
        self,
        file_paths: list[str],
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse multiple files in parallel.
        
        Args:
            file_paths: list of file paths to parse
            progress_callback: Optional callback(file_path, completed, total)
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        results = {}
        total = len(file_paths)
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all parse tasks
            future_to_path = {
                executor.submit(self._parse_file, path): path
                for path in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_path):
                file_path = future_to_path[future]
                
                try:
                    node = future.result()
                    if node:
                        results[file_path] = node
                except Exception as e:
                    logger.error(f"Failed to parse {file_path}: {e}")
                
                # Update progress
                completed += 1
                if progress_callback:
                    progress_callback(file_path, total)
        
        return results
    
    def xǁParallelParserǁparse_files__mutmut_24(
        self,
        file_paths: list[str],
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse multiple files in parallel.
        
        Args:
            file_paths: list of file paths to parse
            progress_callback: Optional callback(file_path, completed, total)
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        results = {}
        total = len(file_paths)
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all parse tasks
            future_to_path = {
                executor.submit(self._parse_file, path): path
                for path in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_path):
                file_path = future_to_path[future]
                
                try:
                    node = future.result()
                    if node:
                        results[file_path] = node
                except Exception as e:
                    logger.error(f"Failed to parse {file_path}: {e}")
                
                # Update progress
                completed += 1
                if progress_callback:
                    progress_callback(file_path, completed, )
        
        return results
    
    xǁParallelParserǁparse_files__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁParallelParserǁparse_files__mutmut_1': xǁParallelParserǁparse_files__mutmut_1, 
        'xǁParallelParserǁparse_files__mutmut_2': xǁParallelParserǁparse_files__mutmut_2, 
        'xǁParallelParserǁparse_files__mutmut_3': xǁParallelParserǁparse_files__mutmut_3, 
        'xǁParallelParserǁparse_files__mutmut_4': xǁParallelParserǁparse_files__mutmut_4, 
        'xǁParallelParserǁparse_files__mutmut_5': xǁParallelParserǁparse_files__mutmut_5, 
        'xǁParallelParserǁparse_files__mutmut_6': xǁParallelParserǁparse_files__mutmut_6, 
        'xǁParallelParserǁparse_files__mutmut_7': xǁParallelParserǁparse_files__mutmut_7, 
        'xǁParallelParserǁparse_files__mutmut_8': xǁParallelParserǁparse_files__mutmut_8, 
        'xǁParallelParserǁparse_files__mutmut_9': xǁParallelParserǁparse_files__mutmut_9, 
        'xǁParallelParserǁparse_files__mutmut_10': xǁParallelParserǁparse_files__mutmut_10, 
        'xǁParallelParserǁparse_files__mutmut_11': xǁParallelParserǁparse_files__mutmut_11, 
        'xǁParallelParserǁparse_files__mutmut_12': xǁParallelParserǁparse_files__mutmut_12, 
        'xǁParallelParserǁparse_files__mutmut_13': xǁParallelParserǁparse_files__mutmut_13, 
        'xǁParallelParserǁparse_files__mutmut_14': xǁParallelParserǁparse_files__mutmut_14, 
        'xǁParallelParserǁparse_files__mutmut_15': xǁParallelParserǁparse_files__mutmut_15, 
        'xǁParallelParserǁparse_files__mutmut_16': xǁParallelParserǁparse_files__mutmut_16, 
        'xǁParallelParserǁparse_files__mutmut_17': xǁParallelParserǁparse_files__mutmut_17, 
        'xǁParallelParserǁparse_files__mutmut_18': xǁParallelParserǁparse_files__mutmut_18, 
        'xǁParallelParserǁparse_files__mutmut_19': xǁParallelParserǁparse_files__mutmut_19, 
        'xǁParallelParserǁparse_files__mutmut_20': xǁParallelParserǁparse_files__mutmut_20, 
        'xǁParallelParserǁparse_files__mutmut_21': xǁParallelParserǁparse_files__mutmut_21, 
        'xǁParallelParserǁparse_files__mutmut_22': xǁParallelParserǁparse_files__mutmut_22, 
        'xǁParallelParserǁparse_files__mutmut_23': xǁParallelParserǁparse_files__mutmut_23, 
        'xǁParallelParserǁparse_files__mutmut_24': xǁParallelParserǁparse_files__mutmut_24
    }
    
    def parse_files(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁParallelParserǁparse_files__mutmut_orig"), object.__getattribute__(self, "xǁParallelParserǁparse_files__mutmut_mutants"), args, kwargs, self)
        return result 
    
    parse_files.__signature__ = _mutmut_signature(xǁParallelParserǁparse_files__mutmut_orig)
    xǁParallelParserǁparse_files__mutmut_orig.__name__ = 'xǁParallelParserǁparse_files'
    
    def xǁParallelParserǁ_parse_file__mutmut_orig(self, file_path: str) -> Optional[StandardizedASTNode]:
        """Parse a single file (called in worker thread)."""
        try:
            return parse_python(file_path)
        except Exception as e:
            logger.debug(f"Parse error in {file_path}: {e}")
            return None
    
    def xǁParallelParserǁ_parse_file__mutmut_1(self, file_path: str) -> Optional[StandardizedASTNode]:
        """Parse a single file (called in worker thread)."""
        try:
            return parse_python(None)
        except Exception as e:
            logger.debug(f"Parse error in {file_path}: {e}")
            return None
    
    def xǁParallelParserǁ_parse_file__mutmut_2(self, file_path: str) -> Optional[StandardizedASTNode]:
        """Parse a single file (called in worker thread)."""
        try:
            return parse_python(file_path)
        except Exception as e:
            logger.debug(None)
            return None
    
    xǁParallelParserǁ_parse_file__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁParallelParserǁ_parse_file__mutmut_1': xǁParallelParserǁ_parse_file__mutmut_1, 
        'xǁParallelParserǁ_parse_file__mutmut_2': xǁParallelParserǁ_parse_file__mutmut_2
    }
    
    def _parse_file(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁParallelParserǁ_parse_file__mutmut_orig"), object.__getattribute__(self, "xǁParallelParserǁ_parse_file__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _parse_file.__signature__ = _mutmut_signature(xǁParallelParserǁ_parse_file__mutmut_orig)
    xǁParallelParserǁ_parse_file__mutmut_orig.__name__ = 'xǁParallelParserǁ_parse_file'
    
    def xǁParallelParserǁparse_directory__mutmut_orig(
        self,
        directory: str,
        pattern: str = "**/*.py",
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse all files in directory in parallel.
        
        Args:
            directory: Directory to scan
            pattern: Glob pattern for files
            progress_callback: Optional progress callback
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        dir_path = Path(directory)
        file_paths = [str(p) for p in dir_path.glob(pattern) if p.is_file()]
        
        logger.info(f"Parsing {len(file_paths)} files in parallel")
        return self.parse_files(file_paths, progress_callback)
    
    def xǁParallelParserǁparse_directory__mutmut_1(
        self,
        directory: str,
        pattern: str = "XX**/*.pyXX",
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse all files in directory in parallel.
        
        Args:
            directory: Directory to scan
            pattern: Glob pattern for files
            progress_callback: Optional progress callback
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        dir_path = Path(directory)
        file_paths = [str(p) for p in dir_path.glob(pattern) if p.is_file()]
        
        logger.info(f"Parsing {len(file_paths)} files in parallel")
        return self.parse_files(file_paths, progress_callback)
    
    def xǁParallelParserǁparse_directory__mutmut_2(
        self,
        directory: str,
        pattern: str = "**/*.PY",
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse all files in directory in parallel.
        
        Args:
            directory: Directory to scan
            pattern: Glob pattern for files
            progress_callback: Optional progress callback
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        dir_path = Path(directory)
        file_paths = [str(p) for p in dir_path.glob(pattern) if p.is_file()]
        
        logger.info(f"Parsing {len(file_paths)} files in parallel")
        return self.parse_files(file_paths, progress_callback)
    
    def xǁParallelParserǁparse_directory__mutmut_3(
        self,
        directory: str,
        pattern: str = "**/*.py",
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse all files in directory in parallel.
        
        Args:
            directory: Directory to scan
            pattern: Glob pattern for files
            progress_callback: Optional progress callback
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        dir_path = None
        file_paths = [str(p) for p in dir_path.glob(pattern) if p.is_file()]
        
        logger.info(f"Parsing {len(file_paths)} files in parallel")
        return self.parse_files(file_paths, progress_callback)
    
    def xǁParallelParserǁparse_directory__mutmut_4(
        self,
        directory: str,
        pattern: str = "**/*.py",
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse all files in directory in parallel.
        
        Args:
            directory: Directory to scan
            pattern: Glob pattern for files
            progress_callback: Optional progress callback
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        dir_path = Path(None)
        file_paths = [str(p) for p in dir_path.glob(pattern) if p.is_file()]
        
        logger.info(f"Parsing {len(file_paths)} files in parallel")
        return self.parse_files(file_paths, progress_callback)
    
    def xǁParallelParserǁparse_directory__mutmut_5(
        self,
        directory: str,
        pattern: str = "**/*.py",
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse all files in directory in parallel.
        
        Args:
            directory: Directory to scan
            pattern: Glob pattern for files
            progress_callback: Optional progress callback
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        dir_path = Path(directory)
        file_paths = None
        
        logger.info(f"Parsing {len(file_paths)} files in parallel")
        return self.parse_files(file_paths, progress_callback)
    
    def xǁParallelParserǁparse_directory__mutmut_6(
        self,
        directory: str,
        pattern: str = "**/*.py",
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse all files in directory in parallel.
        
        Args:
            directory: Directory to scan
            pattern: Glob pattern for files
            progress_callback: Optional progress callback
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        dir_path = Path(directory)
        file_paths = [str(None) for p in dir_path.glob(pattern) if p.is_file()]
        
        logger.info(f"Parsing {len(file_paths)} files in parallel")
        return self.parse_files(file_paths, progress_callback)
    
    def xǁParallelParserǁparse_directory__mutmut_7(
        self,
        directory: str,
        pattern: str = "**/*.py",
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse all files in directory in parallel.
        
        Args:
            directory: Directory to scan
            pattern: Glob pattern for files
            progress_callback: Optional progress callback
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        dir_path = Path(directory)
        file_paths = [str(p) for p in dir_path.glob(None) if p.is_file()]
        
        logger.info(f"Parsing {len(file_paths)} files in parallel")
        return self.parse_files(file_paths, progress_callback)
    
    def xǁParallelParserǁparse_directory__mutmut_8(
        self,
        directory: str,
        pattern: str = "**/*.py",
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse all files in directory in parallel.
        
        Args:
            directory: Directory to scan
            pattern: Glob pattern for files
            progress_callback: Optional progress callback
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        dir_path = Path(directory)
        file_paths = [str(p) for p in dir_path.glob(pattern) if p.is_file()]
        
        logger.info(None)
        return self.parse_files(file_paths, progress_callback)
    
    def xǁParallelParserǁparse_directory__mutmut_9(
        self,
        directory: str,
        pattern: str = "**/*.py",
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse all files in directory in parallel.
        
        Args:
            directory: Directory to scan
            pattern: Glob pattern for files
            progress_callback: Optional progress callback
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        dir_path = Path(directory)
        file_paths = [str(p) for p in dir_path.glob(pattern) if p.is_file()]
        
        logger.info(f"Parsing {len(file_paths)} files in parallel")
        return self.parse_files(None, progress_callback)
    
    def xǁParallelParserǁparse_directory__mutmut_10(
        self,
        directory: str,
        pattern: str = "**/*.py",
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse all files in directory in parallel.
        
        Args:
            directory: Directory to scan
            pattern: Glob pattern for files
            progress_callback: Optional progress callback
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        dir_path = Path(directory)
        file_paths = [str(p) for p in dir_path.glob(pattern) if p.is_file()]
        
        logger.info(f"Parsing {len(file_paths)} files in parallel")
        return self.parse_files(file_paths, None)
    
    def xǁParallelParserǁparse_directory__mutmut_11(
        self,
        directory: str,
        pattern: str = "**/*.py",
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse all files in directory in parallel.
        
        Args:
            directory: Directory to scan
            pattern: Glob pattern for files
            progress_callback: Optional progress callback
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        dir_path = Path(directory)
        file_paths = [str(p) for p in dir_path.glob(pattern) if p.is_file()]
        
        logger.info(f"Parsing {len(file_paths)} files in parallel")
        return self.parse_files(progress_callback)
    
    def xǁParallelParserǁparse_directory__mutmut_12(
        self,
        directory: str,
        pattern: str = "**/*.py",
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse all files in directory in parallel.
        
        Args:
            directory: Directory to scan
            pattern: Glob pattern for files
            progress_callback: Optional progress callback
            
        Returns:
            Dictionary mapping file_path to parsed node
        """
        dir_path = Path(directory)
        file_paths = [str(p) for p in dir_path.glob(pattern) if p.is_file()]
        
        logger.info(f"Parsing {len(file_paths)} files in parallel")
        return self.parse_files(file_paths, )
    
    xǁParallelParserǁparse_directory__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁParallelParserǁparse_directory__mutmut_1': xǁParallelParserǁparse_directory__mutmut_1, 
        'xǁParallelParserǁparse_directory__mutmut_2': xǁParallelParserǁparse_directory__mutmut_2, 
        'xǁParallelParserǁparse_directory__mutmut_3': xǁParallelParserǁparse_directory__mutmut_3, 
        'xǁParallelParserǁparse_directory__mutmut_4': xǁParallelParserǁparse_directory__mutmut_4, 
        'xǁParallelParserǁparse_directory__mutmut_5': xǁParallelParserǁparse_directory__mutmut_5, 
        'xǁParallelParserǁparse_directory__mutmut_6': xǁParallelParserǁparse_directory__mutmut_6, 
        'xǁParallelParserǁparse_directory__mutmut_7': xǁParallelParserǁparse_directory__mutmut_7, 
        'xǁParallelParserǁparse_directory__mutmut_8': xǁParallelParserǁparse_directory__mutmut_8, 
        'xǁParallelParserǁparse_directory__mutmut_9': xǁParallelParserǁparse_directory__mutmut_9, 
        'xǁParallelParserǁparse_directory__mutmut_10': xǁParallelParserǁparse_directory__mutmut_10, 
        'xǁParallelParserǁparse_directory__mutmut_11': xǁParallelParserǁparse_directory__mutmut_11, 
        'xǁParallelParserǁparse_directory__mutmut_12': xǁParallelParserǁparse_directory__mutmut_12
    }
    
    def parse_directory(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁParallelParserǁparse_directory__mutmut_orig"), object.__getattribute__(self, "xǁParallelParserǁparse_directory__mutmut_mutants"), args, kwargs, self)
        return result 
    
    parse_directory.__signature__ = _mutmut_signature(xǁParallelParserǁparse_directory__mutmut_orig)
    xǁParallelParserǁparse_directory__mutmut_orig.__name__ = 'xǁParallelParserǁparse_directory'
