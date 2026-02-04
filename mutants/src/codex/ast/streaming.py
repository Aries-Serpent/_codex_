"""
Streaming AST parser for large files.
Processes files in chunks to minimize memory usage.
"""

import logging
from pathlib import Path
from typing import Iterator

from .node import StandardizedASTNode
from .parser import parse_python

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


class StreamingParser:
    """
    Parse large files in chunks without loading entire file into memory.

    Yields AST nodes incrementally for memory-efficient processing.
    """

    def xǁStreamingParserǁ__init____mutmut_orig(self, chunk_size: int = 1024 * 1024):  # 1MB default
        """
        Initialize streaming parser.

        Args:
            chunk_size: Size of chunks to read (bytes)
        """
        self.chunk_size = chunk_size

    def xǁStreamingParserǁ__init____mutmut_1(self, chunk_size: int = 1024 * 1024):  # 1MB default
        """
        Initialize streaming parser.

        Args:
            chunk_size: Size of chunks to read (bytes)
        """
        self.chunk_size = None
    
    xǁStreamingParserǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStreamingParserǁ__init____mutmut_1': xǁStreamingParserǁ__init____mutmut_1
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStreamingParserǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁStreamingParserǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁStreamingParserǁ__init____mutmut_orig)
    xǁStreamingParserǁ__init____mutmut_orig.__name__ = 'xǁStreamingParserǁ__init__'

    def xǁStreamingParserǁparse_file__mutmut_orig(self, file_path: str) -> Iterator[StandardizedASTNode]:
        """
        Parse file in streaming fashion.

        Args:
            file_path: Path to file to parse

        Yields:
            StandardizedASTNode for each top-level construct
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # For Python files, we need to parse complete syntactic units
        # Can't truly "stream" since Python requires full AST
        # But we can yield top-level nodes incrementally

        try:
            # Read file in chunks to check size
            file_size = path.stat().st_size

            if file_size > self.chunk_size:
                logger.info(f"Large file detected ({file_size} bytes), using streaming mode")

            # Parse entire file (Python requires complete parse)
            tree = parse_python(str(path))

            if tree:
                # Yield top-level nodes incrementally
                for child in tree.children:
                    yield child

        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            raise

    def xǁStreamingParserǁparse_file__mutmut_1(self, file_path: str) -> Iterator[StandardizedASTNode]:
        """
        Parse file in streaming fashion.

        Args:
            file_path: Path to file to parse

        Yields:
            StandardizedASTNode for each top-level construct
        """
        path = None

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # For Python files, we need to parse complete syntactic units
        # Can't truly "stream" since Python requires full AST
        # But we can yield top-level nodes incrementally

        try:
            # Read file in chunks to check size
            file_size = path.stat().st_size

            if file_size > self.chunk_size:
                logger.info(f"Large file detected ({file_size} bytes), using streaming mode")

            # Parse entire file (Python requires complete parse)
            tree = parse_python(str(path))

            if tree:
                # Yield top-level nodes incrementally
                for child in tree.children:
                    yield child

        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            raise

    def xǁStreamingParserǁparse_file__mutmut_2(self, file_path: str) -> Iterator[StandardizedASTNode]:
        """
        Parse file in streaming fashion.

        Args:
            file_path: Path to file to parse

        Yields:
            StandardizedASTNode for each top-level construct
        """
        path = Path(None)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # For Python files, we need to parse complete syntactic units
        # Can't truly "stream" since Python requires full AST
        # But we can yield top-level nodes incrementally

        try:
            # Read file in chunks to check size
            file_size = path.stat().st_size

            if file_size > self.chunk_size:
                logger.info(f"Large file detected ({file_size} bytes), using streaming mode")

            # Parse entire file (Python requires complete parse)
            tree = parse_python(str(path))

            if tree:
                # Yield top-level nodes incrementally
                for child in tree.children:
                    yield child

        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            raise

    def xǁStreamingParserǁparse_file__mutmut_3(self, file_path: str) -> Iterator[StandardizedASTNode]:
        """
        Parse file in streaming fashion.

        Args:
            file_path: Path to file to parse

        Yields:
            StandardizedASTNode for each top-level construct
        """
        path = Path(file_path)

        if path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # For Python files, we need to parse complete syntactic units
        # Can't truly "stream" since Python requires full AST
        # But we can yield top-level nodes incrementally

        try:
            # Read file in chunks to check size
            file_size = path.stat().st_size

            if file_size > self.chunk_size:
                logger.info(f"Large file detected ({file_size} bytes), using streaming mode")

            # Parse entire file (Python requires complete parse)
            tree = parse_python(str(path))

            if tree:
                # Yield top-level nodes incrementally
                for child in tree.children:
                    yield child

        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            raise

    def xǁStreamingParserǁparse_file__mutmut_4(self, file_path: str) -> Iterator[StandardizedASTNode]:
        """
        Parse file in streaming fashion.

        Args:
            file_path: Path to file to parse

        Yields:
            StandardizedASTNode for each top-level construct
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(None)

        # For Python files, we need to parse complete syntactic units
        # Can't truly "stream" since Python requires full AST
        # But we can yield top-level nodes incrementally

        try:
            # Read file in chunks to check size
            file_size = path.stat().st_size

            if file_size > self.chunk_size:
                logger.info(f"Large file detected ({file_size} bytes), using streaming mode")

            # Parse entire file (Python requires complete parse)
            tree = parse_python(str(path))

            if tree:
                # Yield top-level nodes incrementally
                for child in tree.children:
                    yield child

        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            raise

    def xǁStreamingParserǁparse_file__mutmut_5(self, file_path: str) -> Iterator[StandardizedASTNode]:
        """
        Parse file in streaming fashion.

        Args:
            file_path: Path to file to parse

        Yields:
            StandardizedASTNode for each top-level construct
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # For Python files, we need to parse complete syntactic units
        # Can't truly "stream" since Python requires full AST
        # But we can yield top-level nodes incrementally

        try:
            # Read file in chunks to check size
            file_size = None

            if file_size > self.chunk_size:
                logger.info(f"Large file detected ({file_size} bytes), using streaming mode")

            # Parse entire file (Python requires complete parse)
            tree = parse_python(str(path))

            if tree:
                # Yield top-level nodes incrementally
                for child in tree.children:
                    yield child

        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            raise

    def xǁStreamingParserǁparse_file__mutmut_6(self, file_path: str) -> Iterator[StandardizedASTNode]:
        """
        Parse file in streaming fashion.

        Args:
            file_path: Path to file to parse

        Yields:
            StandardizedASTNode for each top-level construct
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # For Python files, we need to parse complete syntactic units
        # Can't truly "stream" since Python requires full AST
        # But we can yield top-level nodes incrementally

        try:
            # Read file in chunks to check size
            file_size = path.stat().st_size

            if file_size >= self.chunk_size:
                logger.info(f"Large file detected ({file_size} bytes), using streaming mode")

            # Parse entire file (Python requires complete parse)
            tree = parse_python(str(path))

            if tree:
                # Yield top-level nodes incrementally
                for child in tree.children:
                    yield child

        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            raise

    def xǁStreamingParserǁparse_file__mutmut_7(self, file_path: str) -> Iterator[StandardizedASTNode]:
        """
        Parse file in streaming fashion.

        Args:
            file_path: Path to file to parse

        Yields:
            StandardizedASTNode for each top-level construct
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # For Python files, we need to parse complete syntactic units
        # Can't truly "stream" since Python requires full AST
        # But we can yield top-level nodes incrementally

        try:
            # Read file in chunks to check size
            file_size = path.stat().st_size

            if file_size > self.chunk_size:
                logger.info(None)

            # Parse entire file (Python requires complete parse)
            tree = parse_python(str(path))

            if tree:
                # Yield top-level nodes incrementally
                for child in tree.children:
                    yield child

        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            raise

    def xǁStreamingParserǁparse_file__mutmut_8(self, file_path: str) -> Iterator[StandardizedASTNode]:
        """
        Parse file in streaming fashion.

        Args:
            file_path: Path to file to parse

        Yields:
            StandardizedASTNode for each top-level construct
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # For Python files, we need to parse complete syntactic units
        # Can't truly "stream" since Python requires full AST
        # But we can yield top-level nodes incrementally

        try:
            # Read file in chunks to check size
            file_size = path.stat().st_size

            if file_size > self.chunk_size:
                logger.info(f"Large file detected ({file_size} bytes), using streaming mode")

            # Parse entire file (Python requires complete parse)
            tree = None

            if tree:
                # Yield top-level nodes incrementally
                for child in tree.children:
                    yield child

        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            raise

    def xǁStreamingParserǁparse_file__mutmut_9(self, file_path: str) -> Iterator[StandardizedASTNode]:
        """
        Parse file in streaming fashion.

        Args:
            file_path: Path to file to parse

        Yields:
            StandardizedASTNode for each top-level construct
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # For Python files, we need to parse complete syntactic units
        # Can't truly "stream" since Python requires full AST
        # But we can yield top-level nodes incrementally

        try:
            # Read file in chunks to check size
            file_size = path.stat().st_size

            if file_size > self.chunk_size:
                logger.info(f"Large file detected ({file_size} bytes), using streaming mode")

            # Parse entire file (Python requires complete parse)
            tree = parse_python(None)

            if tree:
                # Yield top-level nodes incrementally
                for child in tree.children:
                    yield child

        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            raise

    def xǁStreamingParserǁparse_file__mutmut_10(self, file_path: str) -> Iterator[StandardizedASTNode]:
        """
        Parse file in streaming fashion.

        Args:
            file_path: Path to file to parse

        Yields:
            StandardizedASTNode for each top-level construct
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # For Python files, we need to parse complete syntactic units
        # Can't truly "stream" since Python requires full AST
        # But we can yield top-level nodes incrementally

        try:
            # Read file in chunks to check size
            file_size = path.stat().st_size

            if file_size > self.chunk_size:
                logger.info(f"Large file detected ({file_size} bytes), using streaming mode")

            # Parse entire file (Python requires complete parse)
            tree = parse_python(str(None))

            if tree:
                # Yield top-level nodes incrementally
                for child in tree.children:
                    yield child

        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            raise

    def xǁStreamingParserǁparse_file__mutmut_11(self, file_path: str) -> Iterator[StandardizedASTNode]:
        """
        Parse file in streaming fashion.

        Args:
            file_path: Path to file to parse

        Yields:
            StandardizedASTNode for each top-level construct
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # For Python files, we need to parse complete syntactic units
        # Can't truly "stream" since Python requires full AST
        # But we can yield top-level nodes incrementally

        try:
            # Read file in chunks to check size
            file_size = path.stat().st_size

            if file_size > self.chunk_size:
                logger.info(f"Large file detected ({file_size} bytes), using streaming mode")

            # Parse entire file (Python requires complete parse)
            tree = parse_python(str(path))

            if tree:
                # Yield top-level nodes incrementally
                for child in tree.children:
                    yield child

        except Exception as e:
            logger.error(None)
            raise
    
    xǁStreamingParserǁparse_file__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStreamingParserǁparse_file__mutmut_1': xǁStreamingParserǁparse_file__mutmut_1, 
        'xǁStreamingParserǁparse_file__mutmut_2': xǁStreamingParserǁparse_file__mutmut_2, 
        'xǁStreamingParserǁparse_file__mutmut_3': xǁStreamingParserǁparse_file__mutmut_3, 
        'xǁStreamingParserǁparse_file__mutmut_4': xǁStreamingParserǁparse_file__mutmut_4, 
        'xǁStreamingParserǁparse_file__mutmut_5': xǁStreamingParserǁparse_file__mutmut_5, 
        'xǁStreamingParserǁparse_file__mutmut_6': xǁStreamingParserǁparse_file__mutmut_6, 
        'xǁStreamingParserǁparse_file__mutmut_7': xǁStreamingParserǁparse_file__mutmut_7, 
        'xǁStreamingParserǁparse_file__mutmut_8': xǁStreamingParserǁparse_file__mutmut_8, 
        'xǁStreamingParserǁparse_file__mutmut_9': xǁStreamingParserǁparse_file__mutmut_9, 
        'xǁStreamingParserǁparse_file__mutmut_10': xǁStreamingParserǁparse_file__mutmut_10, 
        'xǁStreamingParserǁparse_file__mutmut_11': xǁStreamingParserǁparse_file__mutmut_11
    }
    
    def parse_file(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStreamingParserǁparse_file__mutmut_orig"), object.__getattribute__(self, "xǁStreamingParserǁparse_file__mutmut_mutants"), args, kwargs, self)
        return result 
    
    parse_file.__signature__ = _mutmut_signature(xǁStreamingParserǁparse_file__mutmut_orig)
    xǁStreamingParserǁparse_file__mutmut_orig.__name__ = 'xǁStreamingParserǁparse_file'

    def xǁStreamingParserǁparse_directory__mutmut_orig(
        self, directory: str, pattern: str = "**/*.py"
    ) -> Iterator[tuple[str, StandardizedASTNode]]:
        """
        Parse all files in directory, streaming results.

        Args:
            directory: Directory to scan
            pattern: Glob pattern for files

        Yields:
            Tuples of (file_path, node)
        """
        dir_path = Path(directory)

        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                try:
                    for node in self.parse_file(str(file_path)):
                        yield (str(file_path), node)
                except Exception as e:
                    logger.warning(f"Failed to parse {file_path}: {e}")
                    continue

    def xǁStreamingParserǁparse_directory__mutmut_1(
        self, directory: str, pattern: str = "XX**/*.pyXX"
    ) -> Iterator[tuple[str, StandardizedASTNode]]:
        """
        Parse all files in directory, streaming results.

        Args:
            directory: Directory to scan
            pattern: Glob pattern for files

        Yields:
            Tuples of (file_path, node)
        """
        dir_path = Path(directory)

        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                try:
                    for node in self.parse_file(str(file_path)):
                        yield (str(file_path), node)
                except Exception as e:
                    logger.warning(f"Failed to parse {file_path}: {e}")
                    continue

    def xǁStreamingParserǁparse_directory__mutmut_2(
        self, directory: str, pattern: str = "**/*.PY"
    ) -> Iterator[tuple[str, StandardizedASTNode]]:
        """
        Parse all files in directory, streaming results.

        Args:
            directory: Directory to scan
            pattern: Glob pattern for files

        Yields:
            Tuples of (file_path, node)
        """
        dir_path = Path(directory)

        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                try:
                    for node in self.parse_file(str(file_path)):
                        yield (str(file_path), node)
                except Exception as e:
                    logger.warning(f"Failed to parse {file_path}: {e}")
                    continue

    def xǁStreamingParserǁparse_directory__mutmut_3(
        self, directory: str, pattern: str = "**/*.py"
    ) -> Iterator[tuple[str, StandardizedASTNode]]:
        """
        Parse all files in directory, streaming results.

        Args:
            directory: Directory to scan
            pattern: Glob pattern for files

        Yields:
            Tuples of (file_path, node)
        """
        dir_path = None

        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                try:
                    for node in self.parse_file(str(file_path)):
                        yield (str(file_path), node)
                except Exception as e:
                    logger.warning(f"Failed to parse {file_path}: {e}")
                    continue

    def xǁStreamingParserǁparse_directory__mutmut_4(
        self, directory: str, pattern: str = "**/*.py"
    ) -> Iterator[tuple[str, StandardizedASTNode]]:
        """
        Parse all files in directory, streaming results.

        Args:
            directory: Directory to scan
            pattern: Glob pattern for files

        Yields:
            Tuples of (file_path, node)
        """
        dir_path = Path(None)

        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                try:
                    for node in self.parse_file(str(file_path)):
                        yield (str(file_path), node)
                except Exception as e:
                    logger.warning(f"Failed to parse {file_path}: {e}")
                    continue

    def xǁStreamingParserǁparse_directory__mutmut_5(
        self, directory: str, pattern: str = "**/*.py"
    ) -> Iterator[tuple[str, StandardizedASTNode]]:
        """
        Parse all files in directory, streaming results.

        Args:
            directory: Directory to scan
            pattern: Glob pattern for files

        Yields:
            Tuples of (file_path, node)
        """
        dir_path = Path(directory)

        for file_path in dir_path.glob(None):
            if file_path.is_file():
                try:
                    for node in self.parse_file(str(file_path)):
                        yield (str(file_path), node)
                except Exception as e:
                    logger.warning(f"Failed to parse {file_path}: {e}")
                    continue

    def xǁStreamingParserǁparse_directory__mutmut_6(
        self, directory: str, pattern: str = "**/*.py"
    ) -> Iterator[tuple[str, StandardizedASTNode]]:
        """
        Parse all files in directory, streaming results.

        Args:
            directory: Directory to scan
            pattern: Glob pattern for files

        Yields:
            Tuples of (file_path, node)
        """
        dir_path = Path(directory)

        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                try:
                    for node in self.parse_file(None):
                        yield (str(file_path), node)
                except Exception as e:
                    logger.warning(f"Failed to parse {file_path}: {e}")
                    continue

    def xǁStreamingParserǁparse_directory__mutmut_7(
        self, directory: str, pattern: str = "**/*.py"
    ) -> Iterator[tuple[str, StandardizedASTNode]]:
        """
        Parse all files in directory, streaming results.

        Args:
            directory: Directory to scan
            pattern: Glob pattern for files

        Yields:
            Tuples of (file_path, node)
        """
        dir_path = Path(directory)

        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                try:
                    for node in self.parse_file(str(None)):
                        yield (str(file_path), node)
                except Exception as e:
                    logger.warning(f"Failed to parse {file_path}: {e}")
                    continue

    def xǁStreamingParserǁparse_directory__mutmut_8(
        self, directory: str, pattern: str = "**/*.py"
    ) -> Iterator[tuple[str, StandardizedASTNode]]:
        """
        Parse all files in directory, streaming results.

        Args:
            directory: Directory to scan
            pattern: Glob pattern for files

        Yields:
            Tuples of (file_path, node)
        """
        dir_path = Path(directory)

        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                try:
                    for node in self.parse_file(str(file_path)):
                        yield (str(None), node)
                except Exception as e:
                    logger.warning(f"Failed to parse {file_path}: {e}")
                    continue

    def xǁStreamingParserǁparse_directory__mutmut_9(
        self, directory: str, pattern: str = "**/*.py"
    ) -> Iterator[tuple[str, StandardizedASTNode]]:
        """
        Parse all files in directory, streaming results.

        Args:
            directory: Directory to scan
            pattern: Glob pattern for files

        Yields:
            Tuples of (file_path, node)
        """
        dir_path = Path(directory)

        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                try:
                    for node in self.parse_file(str(file_path)):
                        yield (str(file_path), node)
                except Exception as e:
                    logger.warning(None)
                    continue

    def xǁStreamingParserǁparse_directory__mutmut_10(
        self, directory: str, pattern: str = "**/*.py"
    ) -> Iterator[tuple[str, StandardizedASTNode]]:
        """
        Parse all files in directory, streaming results.

        Args:
            directory: Directory to scan
            pattern: Glob pattern for files

        Yields:
            Tuples of (file_path, node)
        """
        dir_path = Path(directory)

        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                try:
                    for node in self.parse_file(str(file_path)):
                        yield (str(file_path), node)
                except Exception as e:
                    logger.warning(f"Failed to parse {file_path}: {e}")
                    break
    
    xǁStreamingParserǁparse_directory__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStreamingParserǁparse_directory__mutmut_1': xǁStreamingParserǁparse_directory__mutmut_1, 
        'xǁStreamingParserǁparse_directory__mutmut_2': xǁStreamingParserǁparse_directory__mutmut_2, 
        'xǁStreamingParserǁparse_directory__mutmut_3': xǁStreamingParserǁparse_directory__mutmut_3, 
        'xǁStreamingParserǁparse_directory__mutmut_4': xǁStreamingParserǁparse_directory__mutmut_4, 
        'xǁStreamingParserǁparse_directory__mutmut_5': xǁStreamingParserǁparse_directory__mutmut_5, 
        'xǁStreamingParserǁparse_directory__mutmut_6': xǁStreamingParserǁparse_directory__mutmut_6, 
        'xǁStreamingParserǁparse_directory__mutmut_7': xǁStreamingParserǁparse_directory__mutmut_7, 
        'xǁStreamingParserǁparse_directory__mutmut_8': xǁStreamingParserǁparse_directory__mutmut_8, 
        'xǁStreamingParserǁparse_directory__mutmut_9': xǁStreamingParserǁparse_directory__mutmut_9, 
        'xǁStreamingParserǁparse_directory__mutmut_10': xǁStreamingParserǁparse_directory__mutmut_10
    }
    
    def parse_directory(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStreamingParserǁparse_directory__mutmut_orig"), object.__getattribute__(self, "xǁStreamingParserǁparse_directory__mutmut_mutants"), args, kwargs, self)
        return result 
    
    parse_directory.__signature__ = _mutmut_signature(xǁStreamingParserǁparse_directory__mutmut_orig)
    xǁStreamingParserǁparse_directory__mutmut_orig.__name__ = 'xǁStreamingParserǁparse_directory'
