"""StdioTransport for MCP communication over stdin/stdout.

This module provides the stdio transport layer for MCP:
- Reading JSON-RPC messages from stdin
- Writing JSON-RPC responses to stdout
- Message framing and parsing
- Error handling for malformed input
"""

import asyncio
import json
import logging
import sys
from dataclasses import dataclass
from typing import Any, AsyncIterator, Optional

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
class TransportConfig:
    """Configuration for stdio transport."""
    
    max_message_size: int = 1024 * 1024  # 1MB default
    read_timeout_seconds: float = 300.0  # 5 minutes
    encoding: str = "utf-8"


class TransportError(Exception):
    """Base exception for transport errors."""
    pass


class MessageTooLargeError(TransportError):
    """Raised when a message exceeds the maximum size."""
    
    def xǁMessageTooLargeErrorǁ__init____mutmut_orig(self, size: int, max_size: int) -> None:
        self.size = size
        self.max_size = max_size
        super().__init__(
            f"Message size {size} exceeds maximum {max_size}"
        )
    
    def xǁMessageTooLargeErrorǁ__init____mutmut_1(self, size: int, max_size: int) -> None:
        self.size = None
        self.max_size = max_size
        super().__init__(
            f"Message size {size} exceeds maximum {max_size}"
        )
    
    def xǁMessageTooLargeErrorǁ__init____mutmut_2(self, size: int, max_size: int) -> None:
        self.size = size
        self.max_size = None
        super().__init__(
            f"Message size {size} exceeds maximum {max_size}"
        )
    
    def xǁMessageTooLargeErrorǁ__init____mutmut_3(self, size: int, max_size: int) -> None:
        self.size = size
        self.max_size = max_size
        super().__init__(
            None
        )
    
    xǁMessageTooLargeErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMessageTooLargeErrorǁ__init____mutmut_1': xǁMessageTooLargeErrorǁ__init____mutmut_1, 
        'xǁMessageTooLargeErrorǁ__init____mutmut_2': xǁMessageTooLargeErrorǁ__init____mutmut_2, 
        'xǁMessageTooLargeErrorǁ__init____mutmut_3': xǁMessageTooLargeErrorǁ__init____mutmut_3
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMessageTooLargeErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁMessageTooLargeErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁMessageTooLargeErrorǁ__init____mutmut_orig)
    xǁMessageTooLargeErrorǁ__init____mutmut_orig.__name__ = 'xǁMessageTooLargeErrorǁ__init__'


class InvalidMessageError(TransportError):
    """Raised when a message cannot be parsed."""
    
    def xǁInvalidMessageErrorǁ__init____mutmut_orig(self, reason: str, raw_data: Optional[str] = None) -> None:
        self.reason = reason
        self.raw_data = raw_data
        super().__init__(f"Invalid message: {reason}")
    
    def xǁInvalidMessageErrorǁ__init____mutmut_1(self, reason: str, raw_data: Optional[str] = None) -> None:
        self.reason = None
        self.raw_data = raw_data
        super().__init__(f"Invalid message: {reason}")
    
    def xǁInvalidMessageErrorǁ__init____mutmut_2(self, reason: str, raw_data: Optional[str] = None) -> None:
        self.reason = reason
        self.raw_data = None
        super().__init__(f"Invalid message: {reason}")
    
    def xǁInvalidMessageErrorǁ__init____mutmut_3(self, reason: str, raw_data: Optional[str] = None) -> None:
        self.reason = reason
        self.raw_data = raw_data
        super().__init__(None)
    
    xǁInvalidMessageErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁInvalidMessageErrorǁ__init____mutmut_1': xǁInvalidMessageErrorǁ__init____mutmut_1, 
        'xǁInvalidMessageErrorǁ__init____mutmut_2': xǁInvalidMessageErrorǁ__init____mutmut_2, 
        'xǁInvalidMessageErrorǁ__init____mutmut_3': xǁInvalidMessageErrorǁ__init____mutmut_3
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁInvalidMessageErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁInvalidMessageErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁInvalidMessageErrorǁ__init____mutmut_orig)
    xǁInvalidMessageErrorǁ__init____mutmut_orig.__name__ = 'xǁInvalidMessageErrorǁ__init__'


class StdioTransport:
    """Stdio transport for MCP JSON-RPC communication.
    
    This transport reads JSON-RPC messages from stdin and writes
    responses to stdout. Each message is expected to be on a single
    line (newline-delimited JSON).
    """
    
    def xǁStdioTransportǁ__init____mutmut_orig(
        self,
        config: Optional[TransportConfig] = None,
        reader: Optional[asyncio.StreamReader] = None,
        writer: Optional[asyncio.StreamWriter] = None
    ) -> None:
        """Initialize the stdio transport.
        
        Args:
            config: Transport configuration.
            reader: Optional custom reader (for testing).
            writer: Optional custom writer (for testing).
        """
        self._config = config or TransportConfig()
        self._reader = reader
        self._writer = writer
        self._running = False
        self._logger = logging.getLogger(__name__)
        
    
    def xǁStdioTransportǁ__init____mutmut_1(
        self,
        config: Optional[TransportConfig] = None,
        reader: Optional[asyncio.StreamReader] = None,
        writer: Optional[asyncio.StreamWriter] = None
    ) -> None:
        """Initialize the stdio transport.
        
        Args:
            config: Transport configuration.
            reader: Optional custom reader (for testing).
            writer: Optional custom writer (for testing).
        """
        self._config = None
        self._reader = reader
        self._writer = writer
        self._running = False
        self._logger = logging.getLogger(__name__)
        
    
    def xǁStdioTransportǁ__init____mutmut_2(
        self,
        config: Optional[TransportConfig] = None,
        reader: Optional[asyncio.StreamReader] = None,
        writer: Optional[asyncio.StreamWriter] = None
    ) -> None:
        """Initialize the stdio transport.
        
        Args:
            config: Transport configuration.
            reader: Optional custom reader (for testing).
            writer: Optional custom writer (for testing).
        """
        self._config = config and TransportConfig()
        self._reader = reader
        self._writer = writer
        self._running = False
        self._logger = logging.getLogger(__name__)
        
    
    def xǁStdioTransportǁ__init____mutmut_3(
        self,
        config: Optional[TransportConfig] = None,
        reader: Optional[asyncio.StreamReader] = None,
        writer: Optional[asyncio.StreamWriter] = None
    ) -> None:
        """Initialize the stdio transport.
        
        Args:
            config: Transport configuration.
            reader: Optional custom reader (for testing).
            writer: Optional custom writer (for testing).
        """
        self._config = config or TransportConfig()
        self._reader = None
        self._writer = writer
        self._running = False
        self._logger = logging.getLogger(__name__)
        
    
    def xǁStdioTransportǁ__init____mutmut_4(
        self,
        config: Optional[TransportConfig] = None,
        reader: Optional[asyncio.StreamReader] = None,
        writer: Optional[asyncio.StreamWriter] = None
    ) -> None:
        """Initialize the stdio transport.
        
        Args:
            config: Transport configuration.
            reader: Optional custom reader (for testing).
            writer: Optional custom writer (for testing).
        """
        self._config = config or TransportConfig()
        self._reader = reader
        self._writer = None
        self._running = False
        self._logger = logging.getLogger(__name__)
        
    
    def xǁStdioTransportǁ__init____mutmut_5(
        self,
        config: Optional[TransportConfig] = None,
        reader: Optional[asyncio.StreamReader] = None,
        writer: Optional[asyncio.StreamWriter] = None
    ) -> None:
        """Initialize the stdio transport.
        
        Args:
            config: Transport configuration.
            reader: Optional custom reader (for testing).
            writer: Optional custom writer (for testing).
        """
        self._config = config or TransportConfig()
        self._reader = reader
        self._writer = writer
        self._running = None
        self._logger = logging.getLogger(__name__)
        
    
    def xǁStdioTransportǁ__init____mutmut_6(
        self,
        config: Optional[TransportConfig] = None,
        reader: Optional[asyncio.StreamReader] = None,
        writer: Optional[asyncio.StreamWriter] = None
    ) -> None:
        """Initialize the stdio transport.
        
        Args:
            config: Transport configuration.
            reader: Optional custom reader (for testing).
            writer: Optional custom writer (for testing).
        """
        self._config = config or TransportConfig()
        self._reader = reader
        self._writer = writer
        self._running = True
        self._logger = logging.getLogger(__name__)
        
    
    def xǁStdioTransportǁ__init____mutmut_7(
        self,
        config: Optional[TransportConfig] = None,
        reader: Optional[asyncio.StreamReader] = None,
        writer: Optional[asyncio.StreamWriter] = None
    ) -> None:
        """Initialize the stdio transport.
        
        Args:
            config: Transport configuration.
            reader: Optional custom reader (for testing).
            writer: Optional custom writer (for testing).
        """
        self._config = config or TransportConfig()
        self._reader = reader
        self._writer = writer
        self._running = False
        self._logger = None
        
    
    def xǁStdioTransportǁ__init____mutmut_8(
        self,
        config: Optional[TransportConfig] = None,
        reader: Optional[asyncio.StreamReader] = None,
        writer: Optional[asyncio.StreamWriter] = None
    ) -> None:
        """Initialize the stdio transport.
        
        Args:
            config: Transport configuration.
            reader: Optional custom reader (for testing).
            writer: Optional custom writer (for testing).
        """
        self._config = config or TransportConfig()
        self._reader = reader
        self._writer = writer
        self._running = False
        self._logger = logging.getLogger(None)
        
    
    xǁStdioTransportǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStdioTransportǁ__init____mutmut_1': xǁStdioTransportǁ__init____mutmut_1, 
        'xǁStdioTransportǁ__init____mutmut_2': xǁStdioTransportǁ__init____mutmut_2, 
        'xǁStdioTransportǁ__init____mutmut_3': xǁStdioTransportǁ__init____mutmut_3, 
        'xǁStdioTransportǁ__init____mutmut_4': xǁStdioTransportǁ__init____mutmut_4, 
        'xǁStdioTransportǁ__init____mutmut_5': xǁStdioTransportǁ__init____mutmut_5, 
        'xǁStdioTransportǁ__init____mutmut_6': xǁStdioTransportǁ__init____mutmut_6, 
        'xǁStdioTransportǁ__init____mutmut_7': xǁStdioTransportǁ__init____mutmut_7, 
        'xǁStdioTransportǁ__init____mutmut_8': xǁStdioTransportǁ__init____mutmut_8
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStdioTransportǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁStdioTransportǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁStdioTransportǁ__init____mutmut_orig)
    xǁStdioTransportǁ__init____mutmut_orig.__name__ = 'xǁStdioTransportǁ__init__'
    async def xǁStdioTransportǁ_get_reader__mutmut_orig(self) -> asyncio.StreamReader:
        """Get or create the stdin reader."""
        if self._reader is not None:
            return self._reader
        
        # Create reader from stdin
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)
        self._reader = reader
        return reader
    async def xǁStdioTransportǁ_get_reader__mutmut_1(self) -> asyncio.StreamReader:
        """Get or create the stdin reader."""
        if self._reader is None:
            return self._reader
        
        # Create reader from stdin
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)
        self._reader = reader
        return reader
    async def xǁStdioTransportǁ_get_reader__mutmut_2(self) -> asyncio.StreamReader:
        """Get or create the stdin reader."""
        if self._reader is not None:
            return self._reader
        
        # Create reader from stdin
        loop = None
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)
        self._reader = reader
        return reader
    async def xǁStdioTransportǁ_get_reader__mutmut_3(self) -> asyncio.StreamReader:
        """Get or create the stdin reader."""
        if self._reader is not None:
            return self._reader
        
        # Create reader from stdin
        loop = asyncio.get_event_loop()
        reader = None
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)
        self._reader = reader
        return reader
    async def xǁStdioTransportǁ_get_reader__mutmut_4(self) -> asyncio.StreamReader:
        """Get or create the stdin reader."""
        if self._reader is not None:
            return self._reader
        
        # Create reader from stdin
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = None
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)
        self._reader = reader
        return reader
    async def xǁStdioTransportǁ_get_reader__mutmut_5(self) -> asyncio.StreamReader:
        """Get or create the stdin reader."""
        if self._reader is not None:
            return self._reader
        
        # Create reader from stdin
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(None)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)
        self._reader = reader
        return reader
    async def xǁStdioTransportǁ_get_reader__mutmut_6(self) -> asyncio.StreamReader:
        """Get or create the stdin reader."""
        if self._reader is not None:
            return self._reader
        
        # Create reader from stdin
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(None, sys.stdin)
        self._reader = reader
        return reader
    async def xǁStdioTransportǁ_get_reader__mutmut_7(self) -> asyncio.StreamReader:
        """Get or create the stdin reader."""
        if self._reader is not None:
            return self._reader
        
        # Create reader from stdin
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, None)
        self._reader = reader
        return reader
    async def xǁStdioTransportǁ_get_reader__mutmut_8(self) -> asyncio.StreamReader:
        """Get or create the stdin reader."""
        if self._reader is not None:
            return self._reader
        
        # Create reader from stdin
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(sys.stdin)
        self._reader = reader
        return reader
    async def xǁStdioTransportǁ_get_reader__mutmut_9(self) -> asyncio.StreamReader:
        """Get or create the stdin reader."""
        if self._reader is not None:
            return self._reader
        
        # Create reader from stdin
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, )
        self._reader = reader
        return reader
    async def xǁStdioTransportǁ_get_reader__mutmut_10(self) -> asyncio.StreamReader:
        """Get or create the stdin reader."""
        if self._reader is not None:
            return self._reader
        
        # Create reader from stdin
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: None, sys.stdin)
        self._reader = reader
        return reader
    async def xǁStdioTransportǁ_get_reader__mutmut_11(self) -> asyncio.StreamReader:
        """Get or create the stdin reader."""
        if self._reader is not None:
            return self._reader
        
        # Create reader from stdin
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)
        self._reader = None
        return reader
    
    xǁStdioTransportǁ_get_reader__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStdioTransportǁ_get_reader__mutmut_1': xǁStdioTransportǁ_get_reader__mutmut_1, 
        'xǁStdioTransportǁ_get_reader__mutmut_2': xǁStdioTransportǁ_get_reader__mutmut_2, 
        'xǁStdioTransportǁ_get_reader__mutmut_3': xǁStdioTransportǁ_get_reader__mutmut_3, 
        'xǁStdioTransportǁ_get_reader__mutmut_4': xǁStdioTransportǁ_get_reader__mutmut_4, 
        'xǁStdioTransportǁ_get_reader__mutmut_5': xǁStdioTransportǁ_get_reader__mutmut_5, 
        'xǁStdioTransportǁ_get_reader__mutmut_6': xǁStdioTransportǁ_get_reader__mutmut_6, 
        'xǁStdioTransportǁ_get_reader__mutmut_7': xǁStdioTransportǁ_get_reader__mutmut_7, 
        'xǁStdioTransportǁ_get_reader__mutmut_8': xǁStdioTransportǁ_get_reader__mutmut_8, 
        'xǁStdioTransportǁ_get_reader__mutmut_9': xǁStdioTransportǁ_get_reader__mutmut_9, 
        'xǁStdioTransportǁ_get_reader__mutmut_10': xǁStdioTransportǁ_get_reader__mutmut_10, 
        'xǁStdioTransportǁ_get_reader__mutmut_11': xǁStdioTransportǁ_get_reader__mutmut_11
    }
    
    def _get_reader(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStdioTransportǁ_get_reader__mutmut_orig"), object.__getattribute__(self, "xǁStdioTransportǁ_get_reader__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _get_reader.__signature__ = _mutmut_signature(xǁStdioTransportǁ_get_reader__mutmut_orig)
    xǁStdioTransportǁ_get_reader__mutmut_orig.__name__ = 'xǁStdioTransportǁ_get_reader'
    
    async def xǁStdioTransportǁ_get_writer__mutmut_orig(self) -> asyncio.StreamWriter:
        """Get or create the stdout writer."""
        if self._writer is not None:
            return self._writer
        
        # Create writer to stdout
        loop = asyncio.get_event_loop()
        transport, protocol = await loop.connect_write_pipe(
            asyncio.Protocol,
            sys.stdout
        )
        writer = asyncio.StreamWriter(transport, protocol, None, loop)
        self._writer = writer
        return writer
    
    async def xǁStdioTransportǁ_get_writer__mutmut_1(self) -> asyncio.StreamWriter:
        """Get or create the stdout writer."""
        if self._writer is None:
            return self._writer
        
        # Create writer to stdout
        loop = asyncio.get_event_loop()
        transport, protocol = await loop.connect_write_pipe(
            asyncio.Protocol,
            sys.stdout
        )
        writer = asyncio.StreamWriter(transport, protocol, None, loop)
        self._writer = writer
        return writer
    
    async def xǁStdioTransportǁ_get_writer__mutmut_2(self) -> asyncio.StreamWriter:
        """Get or create the stdout writer."""
        if self._writer is not None:
            return self._writer
        
        # Create writer to stdout
        loop = None
        transport, protocol = await loop.connect_write_pipe(
            asyncio.Protocol,
            sys.stdout
        )
        writer = asyncio.StreamWriter(transport, protocol, None, loop)
        self._writer = writer
        return writer
    
    async def xǁStdioTransportǁ_get_writer__mutmut_3(self) -> asyncio.StreamWriter:
        """Get or create the stdout writer."""
        if self._writer is not None:
            return self._writer
        
        # Create writer to stdout
        loop = asyncio.get_event_loop()
        transport, protocol = None
        writer = asyncio.StreamWriter(transport, protocol, None, loop)
        self._writer = writer
        return writer
    
    async def xǁStdioTransportǁ_get_writer__mutmut_4(self) -> asyncio.StreamWriter:
        """Get or create the stdout writer."""
        if self._writer is not None:
            return self._writer
        
        # Create writer to stdout
        loop = asyncio.get_event_loop()
        transport, protocol = await loop.connect_write_pipe(
            None,
            sys.stdout
        )
        writer = asyncio.StreamWriter(transport, protocol, None, loop)
        self._writer = writer
        return writer
    
    async def xǁStdioTransportǁ_get_writer__mutmut_5(self) -> asyncio.StreamWriter:
        """Get or create the stdout writer."""
        if self._writer is not None:
            return self._writer
        
        # Create writer to stdout
        loop = asyncio.get_event_loop()
        transport, protocol = await loop.connect_write_pipe(
            asyncio.Protocol,
            None
        )
        writer = asyncio.StreamWriter(transport, protocol, None, loop)
        self._writer = writer
        return writer
    
    async def xǁStdioTransportǁ_get_writer__mutmut_6(self) -> asyncio.StreamWriter:
        """Get or create the stdout writer."""
        if self._writer is not None:
            return self._writer
        
        # Create writer to stdout
        loop = asyncio.get_event_loop()
        transport, protocol = await loop.connect_write_pipe(
            sys.stdout
        )
        writer = asyncio.StreamWriter(transport, protocol, None, loop)
        self._writer = writer
        return writer
    
    async def xǁStdioTransportǁ_get_writer__mutmut_7(self) -> asyncio.StreamWriter:
        """Get or create the stdout writer."""
        if self._writer is not None:
            return self._writer
        
        # Create writer to stdout
        loop = asyncio.get_event_loop()
        transport, protocol = await loop.connect_write_pipe(
            asyncio.Protocol,
            )
        writer = asyncio.StreamWriter(transport, protocol, None, loop)
        self._writer = writer
        return writer
    
    async def xǁStdioTransportǁ_get_writer__mutmut_8(self) -> asyncio.StreamWriter:
        """Get or create the stdout writer."""
        if self._writer is not None:
            return self._writer
        
        # Create writer to stdout
        loop = asyncio.get_event_loop()
        transport, protocol = await loop.connect_write_pipe(
            asyncio.Protocol,
            sys.stdout
        )
        writer = None
        self._writer = writer
        return writer
    
    async def xǁStdioTransportǁ_get_writer__mutmut_9(self) -> asyncio.StreamWriter:
        """Get or create the stdout writer."""
        if self._writer is not None:
            return self._writer
        
        # Create writer to stdout
        loop = asyncio.get_event_loop()
        transport, protocol = await loop.connect_write_pipe(
            asyncio.Protocol,
            sys.stdout
        )
        writer = asyncio.StreamWriter(None, protocol, None, loop)
        self._writer = writer
        return writer
    
    async def xǁStdioTransportǁ_get_writer__mutmut_10(self) -> asyncio.StreamWriter:
        """Get or create the stdout writer."""
        if self._writer is not None:
            return self._writer
        
        # Create writer to stdout
        loop = asyncio.get_event_loop()
        transport, protocol = await loop.connect_write_pipe(
            asyncio.Protocol,
            sys.stdout
        )
        writer = asyncio.StreamWriter(transport, None, None, loop)
        self._writer = writer
        return writer
    
    async def xǁStdioTransportǁ_get_writer__mutmut_11(self) -> asyncio.StreamWriter:
        """Get or create the stdout writer."""
        if self._writer is not None:
            return self._writer
        
        # Create writer to stdout
        loop = asyncio.get_event_loop()
        transport, protocol = await loop.connect_write_pipe(
            asyncio.Protocol,
            sys.stdout
        )
        writer = asyncio.StreamWriter(transport, protocol, None, None)
        self._writer = writer
        return writer
    
    async def xǁStdioTransportǁ_get_writer__mutmut_12(self) -> asyncio.StreamWriter:
        """Get or create the stdout writer."""
        if self._writer is not None:
            return self._writer
        
        # Create writer to stdout
        loop = asyncio.get_event_loop()
        transport, protocol = await loop.connect_write_pipe(
            asyncio.Protocol,
            sys.stdout
        )
        writer = asyncio.StreamWriter(protocol, None, loop)
        self._writer = writer
        return writer
    
    async def xǁStdioTransportǁ_get_writer__mutmut_13(self) -> asyncio.StreamWriter:
        """Get or create the stdout writer."""
        if self._writer is not None:
            return self._writer
        
        # Create writer to stdout
        loop = asyncio.get_event_loop()
        transport, protocol = await loop.connect_write_pipe(
            asyncio.Protocol,
            sys.stdout
        )
        writer = asyncio.StreamWriter(transport, None, loop)
        self._writer = writer
        return writer
    
    async def xǁStdioTransportǁ_get_writer__mutmut_14(self) -> asyncio.StreamWriter:
        """Get or create the stdout writer."""
        if self._writer is not None:
            return self._writer
        
        # Create writer to stdout
        loop = asyncio.get_event_loop()
        transport, protocol = await loop.connect_write_pipe(
            asyncio.Protocol,
            sys.stdout
        )
        writer = asyncio.StreamWriter(transport, protocol, loop)
        self._writer = writer
        return writer
    
    async def xǁStdioTransportǁ_get_writer__mutmut_15(self) -> asyncio.StreamWriter:
        """Get or create the stdout writer."""
        if self._writer is not None:
            return self._writer
        
        # Create writer to stdout
        loop = asyncio.get_event_loop()
        transport, protocol = await loop.connect_write_pipe(
            asyncio.Protocol,
            sys.stdout
        )
        writer = asyncio.StreamWriter(transport, protocol, None, )
        self._writer = writer
        return writer
    
    async def xǁStdioTransportǁ_get_writer__mutmut_16(self) -> asyncio.StreamWriter:
        """Get or create the stdout writer."""
        if self._writer is not None:
            return self._writer
        
        # Create writer to stdout
        loop = asyncio.get_event_loop()
        transport, protocol = await loop.connect_write_pipe(
            asyncio.Protocol,
            sys.stdout
        )
        writer = asyncio.StreamWriter(transport, protocol, None, loop)
        self._writer = None
        return writer
    
    xǁStdioTransportǁ_get_writer__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStdioTransportǁ_get_writer__mutmut_1': xǁStdioTransportǁ_get_writer__mutmut_1, 
        'xǁStdioTransportǁ_get_writer__mutmut_2': xǁStdioTransportǁ_get_writer__mutmut_2, 
        'xǁStdioTransportǁ_get_writer__mutmut_3': xǁStdioTransportǁ_get_writer__mutmut_3, 
        'xǁStdioTransportǁ_get_writer__mutmut_4': xǁStdioTransportǁ_get_writer__mutmut_4, 
        'xǁStdioTransportǁ_get_writer__mutmut_5': xǁStdioTransportǁ_get_writer__mutmut_5, 
        'xǁStdioTransportǁ_get_writer__mutmut_6': xǁStdioTransportǁ_get_writer__mutmut_6, 
        'xǁStdioTransportǁ_get_writer__mutmut_7': xǁStdioTransportǁ_get_writer__mutmut_7, 
        'xǁStdioTransportǁ_get_writer__mutmut_8': xǁStdioTransportǁ_get_writer__mutmut_8, 
        'xǁStdioTransportǁ_get_writer__mutmut_9': xǁStdioTransportǁ_get_writer__mutmut_9, 
        'xǁStdioTransportǁ_get_writer__mutmut_10': xǁStdioTransportǁ_get_writer__mutmut_10, 
        'xǁStdioTransportǁ_get_writer__mutmut_11': xǁStdioTransportǁ_get_writer__mutmut_11, 
        'xǁStdioTransportǁ_get_writer__mutmut_12': xǁStdioTransportǁ_get_writer__mutmut_12, 
        'xǁStdioTransportǁ_get_writer__mutmut_13': xǁStdioTransportǁ_get_writer__mutmut_13, 
        'xǁStdioTransportǁ_get_writer__mutmut_14': xǁStdioTransportǁ_get_writer__mutmut_14, 
        'xǁStdioTransportǁ_get_writer__mutmut_15': xǁStdioTransportǁ_get_writer__mutmut_15, 
        'xǁStdioTransportǁ_get_writer__mutmut_16': xǁStdioTransportǁ_get_writer__mutmut_16
    }
    
    def _get_writer(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStdioTransportǁ_get_writer__mutmut_orig"), object.__getattribute__(self, "xǁStdioTransportǁ_get_writer__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _get_writer.__signature__ = _mutmut_signature(xǁStdioTransportǁ_get_writer__mutmut_orig)
    xǁStdioTransportǁ_get_writer__mutmut_orig.__name__ = 'xǁStdioTransportǁ_get_writer'
    
    async def xǁStdioTransportǁread_message__mutmut_orig(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                reader.readline(),
                timeout=self._config.read_timeout_seconds
            )
        except asyncio.TimeoutError:
            self._logger.warning("Read timeout reached")
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(line),
                self._config.max_message_size
            )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(self._config.encoding).strip()
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                f"Invalid encoding: {e}",
                str(line[:100])
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                f"Invalid JSON: {e}",
                text[:100] if text else None
            )
    
    async def xǁStdioTransportǁread_message__mutmut_1(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = None
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                reader.readline(),
                timeout=self._config.read_timeout_seconds
            )
        except asyncio.TimeoutError:
            self._logger.warning("Read timeout reached")
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(line),
                self._config.max_message_size
            )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(self._config.encoding).strip()
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                f"Invalid encoding: {e}",
                str(line[:100])
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                f"Invalid JSON: {e}",
                text[:100] if text else None
            )
    
    async def xǁStdioTransportǁread_message__mutmut_2(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = None
        except asyncio.TimeoutError:
            self._logger.warning("Read timeout reached")
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(line),
                self._config.max_message_size
            )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(self._config.encoding).strip()
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                f"Invalid encoding: {e}",
                str(line[:100])
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                f"Invalid JSON: {e}",
                text[:100] if text else None
            )
    
    async def xǁStdioTransportǁread_message__mutmut_3(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                None,
                timeout=self._config.read_timeout_seconds
            )
        except asyncio.TimeoutError:
            self._logger.warning("Read timeout reached")
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(line),
                self._config.max_message_size
            )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(self._config.encoding).strip()
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                f"Invalid encoding: {e}",
                str(line[:100])
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                f"Invalid JSON: {e}",
                text[:100] if text else None
            )
    
    async def xǁStdioTransportǁread_message__mutmut_4(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                reader.readline(),
                timeout=None
            )
        except asyncio.TimeoutError:
            self._logger.warning("Read timeout reached")
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(line),
                self._config.max_message_size
            )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(self._config.encoding).strip()
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                f"Invalid encoding: {e}",
                str(line[:100])
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                f"Invalid JSON: {e}",
                text[:100] if text else None
            )
    
    async def xǁStdioTransportǁread_message__mutmut_5(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                timeout=self._config.read_timeout_seconds
            )
        except asyncio.TimeoutError:
            self._logger.warning("Read timeout reached")
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(line),
                self._config.max_message_size
            )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(self._config.encoding).strip()
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                f"Invalid encoding: {e}",
                str(line[:100])
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                f"Invalid JSON: {e}",
                text[:100] if text else None
            )
    
    async def xǁStdioTransportǁread_message__mutmut_6(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                reader.readline(),
                )
        except asyncio.TimeoutError:
            self._logger.warning("Read timeout reached")
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(line),
                self._config.max_message_size
            )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(self._config.encoding).strip()
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                f"Invalid encoding: {e}",
                str(line[:100])
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                f"Invalid JSON: {e}",
                text[:100] if text else None
            )
    
    async def xǁStdioTransportǁread_message__mutmut_7(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                reader.readline(),
                timeout=self._config.read_timeout_seconds
            )
        except asyncio.TimeoutError:
            self._logger.warning(None)
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(line),
                self._config.max_message_size
            )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(self._config.encoding).strip()
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                f"Invalid encoding: {e}",
                str(line[:100])
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                f"Invalid JSON: {e}",
                text[:100] if text else None
            )
    
    async def xǁStdioTransportǁread_message__mutmut_8(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                reader.readline(),
                timeout=self._config.read_timeout_seconds
            )
        except asyncio.TimeoutError:
            self._logger.warning("XXRead timeout reachedXX")
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(line),
                self._config.max_message_size
            )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(self._config.encoding).strip()
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                f"Invalid encoding: {e}",
                str(line[:100])
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                f"Invalid JSON: {e}",
                text[:100] if text else None
            )
    
    async def xǁStdioTransportǁread_message__mutmut_9(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                reader.readline(),
                timeout=self._config.read_timeout_seconds
            )
        except asyncio.TimeoutError:
            self._logger.warning("read timeout reached")
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(line),
                self._config.max_message_size
            )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(self._config.encoding).strip()
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                f"Invalid encoding: {e}",
                str(line[:100])
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                f"Invalid JSON: {e}",
                text[:100] if text else None
            )
    
    async def xǁStdioTransportǁread_message__mutmut_10(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                reader.readline(),
                timeout=self._config.read_timeout_seconds
            )
        except asyncio.TimeoutError:
            self._logger.warning("READ TIMEOUT REACHED")
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(line),
                self._config.max_message_size
            )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(self._config.encoding).strip()
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                f"Invalid encoding: {e}",
                str(line[:100])
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                f"Invalid JSON: {e}",
                text[:100] if text else None
            )
    
    async def xǁStdioTransportǁread_message__mutmut_11(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                reader.readline(),
                timeout=self._config.read_timeout_seconds
            )
        except asyncio.TimeoutError:
            self._logger.warning("Read timeout reached")
            return None
        
        if line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(line),
                self._config.max_message_size
            )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(self._config.encoding).strip()
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                f"Invalid encoding: {e}",
                str(line[:100])
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                f"Invalid JSON: {e}",
                text[:100] if text else None
            )
    
    async def xǁStdioTransportǁread_message__mutmut_12(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                reader.readline(),
                timeout=self._config.read_timeout_seconds
            )
        except asyncio.TimeoutError:
            self._logger.warning("Read timeout reached")
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) >= self._config.max_message_size:
            raise MessageTooLargeError(
                len(line),
                self._config.max_message_size
            )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(self._config.encoding).strip()
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                f"Invalid encoding: {e}",
                str(line[:100])
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                f"Invalid JSON: {e}",
                text[:100] if text else None
            )
    
    async def xǁStdioTransportǁread_message__mutmut_13(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                reader.readline(),
                timeout=self._config.read_timeout_seconds
            )
        except asyncio.TimeoutError:
            self._logger.warning("Read timeout reached")
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                None,
                self._config.max_message_size
            )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(self._config.encoding).strip()
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                f"Invalid encoding: {e}",
                str(line[:100])
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                f"Invalid JSON: {e}",
                text[:100] if text else None
            )
    
    async def xǁStdioTransportǁread_message__mutmut_14(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                reader.readline(),
                timeout=self._config.read_timeout_seconds
            )
        except asyncio.TimeoutError:
            self._logger.warning("Read timeout reached")
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(line),
                None
            )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(self._config.encoding).strip()
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                f"Invalid encoding: {e}",
                str(line[:100])
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                f"Invalid JSON: {e}",
                text[:100] if text else None
            )
    
    async def xǁStdioTransportǁread_message__mutmut_15(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                reader.readline(),
                timeout=self._config.read_timeout_seconds
            )
        except asyncio.TimeoutError:
            self._logger.warning("Read timeout reached")
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                self._config.max_message_size
            )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(self._config.encoding).strip()
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                f"Invalid encoding: {e}",
                str(line[:100])
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                f"Invalid JSON: {e}",
                text[:100] if text else None
            )
    
    async def xǁStdioTransportǁread_message__mutmut_16(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                reader.readline(),
                timeout=self._config.read_timeout_seconds
            )
        except asyncio.TimeoutError:
            self._logger.warning("Read timeout reached")
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(line),
                )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(self._config.encoding).strip()
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                f"Invalid encoding: {e}",
                str(line[:100])
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                f"Invalid JSON: {e}",
                text[:100] if text else None
            )
    
    async def xǁStdioTransportǁread_message__mutmut_17(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                reader.readline(),
                timeout=self._config.read_timeout_seconds
            )
        except asyncio.TimeoutError:
            self._logger.warning("Read timeout reached")
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(line),
                self._config.max_message_size
            )
        
        # Decode and parse
        text: Optional[str] = ""
        try:
            text = line.decode(self._config.encoding).strip()
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                f"Invalid encoding: {e}",
                str(line[:100])
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                f"Invalid JSON: {e}",
                text[:100] if text else None
            )
    
    async def xǁStdioTransportǁread_message__mutmut_18(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                reader.readline(),
                timeout=self._config.read_timeout_seconds
            )
        except asyncio.TimeoutError:
            self._logger.warning("Read timeout reached")
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(line),
                self._config.max_message_size
            )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = None
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                f"Invalid encoding: {e}",
                str(line[:100])
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                f"Invalid JSON: {e}",
                text[:100] if text else None
            )
    
    async def xǁStdioTransportǁread_message__mutmut_19(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                reader.readline(),
                timeout=self._config.read_timeout_seconds
            )
        except asyncio.TimeoutError:
            self._logger.warning("Read timeout reached")
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(line),
                self._config.max_message_size
            )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(None).strip()
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                f"Invalid encoding: {e}",
                str(line[:100])
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                f"Invalid JSON: {e}",
                text[:100] if text else None
            )
    
    async def xǁStdioTransportǁread_message__mutmut_20(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                reader.readline(),
                timeout=self._config.read_timeout_seconds
            )
        except asyncio.TimeoutError:
            self._logger.warning("Read timeout reached")
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(line),
                self._config.max_message_size
            )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(self._config.encoding).strip()
            if text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                f"Invalid encoding: {e}",
                str(line[:100])
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                f"Invalid JSON: {e}",
                text[:100] if text else None
            )
    
    async def xǁStdioTransportǁread_message__mutmut_21(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                reader.readline(),
                timeout=self._config.read_timeout_seconds
            )
        except asyncio.TimeoutError:
            self._logger.warning("Read timeout reached")
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(line),
                self._config.max_message_size
            )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(self._config.encoding).strip()
            if not text:
                return None
            return json.loads(None)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                f"Invalid encoding: {e}",
                str(line[:100])
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                f"Invalid JSON: {e}",
                text[:100] if text else None
            )
    
    async def xǁStdioTransportǁread_message__mutmut_22(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                reader.readline(),
                timeout=self._config.read_timeout_seconds
            )
        except asyncio.TimeoutError:
            self._logger.warning("Read timeout reached")
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(line),
                self._config.max_message_size
            )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(self._config.encoding).strip()
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(None)
            raise InvalidMessageError(
                f"Invalid encoding: {e}",
                str(line[:100])
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                f"Invalid JSON: {e}",
                text[:100] if text else None
            )
    
    async def xǁStdioTransportǁread_message__mutmut_23(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                reader.readline(),
                timeout=self._config.read_timeout_seconds
            )
        except asyncio.TimeoutError:
            self._logger.warning("Read timeout reached")
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(line),
                self._config.max_message_size
            )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(self._config.encoding).strip()
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                None,
                str(line[:100])
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                f"Invalid JSON: {e}",
                text[:100] if text else None
            )
    
    async def xǁStdioTransportǁread_message__mutmut_24(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                reader.readline(),
                timeout=self._config.read_timeout_seconds
            )
        except asyncio.TimeoutError:
            self._logger.warning("Read timeout reached")
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(line),
                self._config.max_message_size
            )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(self._config.encoding).strip()
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                f"Invalid encoding: {e}",
                None
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                f"Invalid JSON: {e}",
                text[:100] if text else None
            )
    
    async def xǁStdioTransportǁread_message__mutmut_25(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                reader.readline(),
                timeout=self._config.read_timeout_seconds
            )
        except asyncio.TimeoutError:
            self._logger.warning("Read timeout reached")
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(line),
                self._config.max_message_size
            )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(self._config.encoding).strip()
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                str(line[:100])
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                f"Invalid JSON: {e}",
                text[:100] if text else None
            )
    
    async def xǁStdioTransportǁread_message__mutmut_26(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                reader.readline(),
                timeout=self._config.read_timeout_seconds
            )
        except asyncio.TimeoutError:
            self._logger.warning("Read timeout reached")
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(line),
                self._config.max_message_size
            )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(self._config.encoding).strip()
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                f"Invalid encoding: {e}",
                )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                f"Invalid JSON: {e}",
                text[:100] if text else None
            )
    
    async def xǁStdioTransportǁread_message__mutmut_27(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                reader.readline(),
                timeout=self._config.read_timeout_seconds
            )
        except asyncio.TimeoutError:
            self._logger.warning("Read timeout reached")
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(line),
                self._config.max_message_size
            )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(self._config.encoding).strip()
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                f"Invalid encoding: {e}",
                str(None)
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                f"Invalid JSON: {e}",
                text[:100] if text else None
            )
    
    async def xǁStdioTransportǁread_message__mutmut_28(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                reader.readline(),
                timeout=self._config.read_timeout_seconds
            )
        except asyncio.TimeoutError:
            self._logger.warning("Read timeout reached")
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(line),
                self._config.max_message_size
            )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(self._config.encoding).strip()
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                f"Invalid encoding: {e}",
                str(line[:101])
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                f"Invalid JSON: {e}",
                text[:100] if text else None
            )
    
    async def xǁStdioTransportǁread_message__mutmut_29(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                reader.readline(),
                timeout=self._config.read_timeout_seconds
            )
        except asyncio.TimeoutError:
            self._logger.warning("Read timeout reached")
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(line),
                self._config.max_message_size
            )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(self._config.encoding).strip()
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                f"Invalid encoding: {e}",
                str(line[:100])
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                None,
                text[:100] if text else None
            )
    
    async def xǁStdioTransportǁread_message__mutmut_30(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                reader.readline(),
                timeout=self._config.read_timeout_seconds
            )
        except asyncio.TimeoutError:
            self._logger.warning("Read timeout reached")
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(line),
                self._config.max_message_size
            )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(self._config.encoding).strip()
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                f"Invalid encoding: {e}",
                str(line[:100])
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                f"Invalid JSON: {e}",
                None
            )
    
    async def xǁStdioTransportǁread_message__mutmut_31(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                reader.readline(),
                timeout=self._config.read_timeout_seconds
            )
        except asyncio.TimeoutError:
            self._logger.warning("Read timeout reached")
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(line),
                self._config.max_message_size
            )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(self._config.encoding).strip()
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                f"Invalid encoding: {e}",
                str(line[:100])
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                text[:100] if text else None
            )
    
    async def xǁStdioTransportǁread_message__mutmut_32(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                reader.readline(),
                timeout=self._config.read_timeout_seconds
            )
        except asyncio.TimeoutError:
            self._logger.warning("Read timeout reached")
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(line),
                self._config.max_message_size
            )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(self._config.encoding).strip()
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                f"Invalid encoding: {e}",
                str(line[:100])
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                f"Invalid JSON: {e}",
                )
    
    async def xǁStdioTransportǁread_message__mutmut_33(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.
        
        Returns:
            Parsed JSON-RPC message, or None if EOF reached.
            
        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()
        
        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                reader.readline(),
                timeout=self._config.read_timeout_seconds
            )
        except asyncio.TimeoutError:
            self._logger.warning("Read timeout reached")
            return None
        
        if not line:
            # EOF reached
            return None
        
        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(line),
                self._config.max_message_size
            )
        
        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(self._config.encoding).strip()
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            raise InvalidMessageError(
                f"Invalid encoding: {e}",
                str(line[:100])
            )
        except json.JSONDecodeError as e:
            raise InvalidMessageError(
                f"Invalid JSON: {e}",
                text[:101] if text else None
            )
    
    xǁStdioTransportǁread_message__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStdioTransportǁread_message__mutmut_1': xǁStdioTransportǁread_message__mutmut_1, 
        'xǁStdioTransportǁread_message__mutmut_2': xǁStdioTransportǁread_message__mutmut_2, 
        'xǁStdioTransportǁread_message__mutmut_3': xǁStdioTransportǁread_message__mutmut_3, 
        'xǁStdioTransportǁread_message__mutmut_4': xǁStdioTransportǁread_message__mutmut_4, 
        'xǁStdioTransportǁread_message__mutmut_5': xǁStdioTransportǁread_message__mutmut_5, 
        'xǁStdioTransportǁread_message__mutmut_6': xǁStdioTransportǁread_message__mutmut_6, 
        'xǁStdioTransportǁread_message__mutmut_7': xǁStdioTransportǁread_message__mutmut_7, 
        'xǁStdioTransportǁread_message__mutmut_8': xǁStdioTransportǁread_message__mutmut_8, 
        'xǁStdioTransportǁread_message__mutmut_9': xǁStdioTransportǁread_message__mutmut_9, 
        'xǁStdioTransportǁread_message__mutmut_10': xǁStdioTransportǁread_message__mutmut_10, 
        'xǁStdioTransportǁread_message__mutmut_11': xǁStdioTransportǁread_message__mutmut_11, 
        'xǁStdioTransportǁread_message__mutmut_12': xǁStdioTransportǁread_message__mutmut_12, 
        'xǁStdioTransportǁread_message__mutmut_13': xǁStdioTransportǁread_message__mutmut_13, 
        'xǁStdioTransportǁread_message__mutmut_14': xǁStdioTransportǁread_message__mutmut_14, 
        'xǁStdioTransportǁread_message__mutmut_15': xǁStdioTransportǁread_message__mutmut_15, 
        'xǁStdioTransportǁread_message__mutmut_16': xǁStdioTransportǁread_message__mutmut_16, 
        'xǁStdioTransportǁread_message__mutmut_17': xǁStdioTransportǁread_message__mutmut_17, 
        'xǁStdioTransportǁread_message__mutmut_18': xǁStdioTransportǁread_message__mutmut_18, 
        'xǁStdioTransportǁread_message__mutmut_19': xǁStdioTransportǁread_message__mutmut_19, 
        'xǁStdioTransportǁread_message__mutmut_20': xǁStdioTransportǁread_message__mutmut_20, 
        'xǁStdioTransportǁread_message__mutmut_21': xǁStdioTransportǁread_message__mutmut_21, 
        'xǁStdioTransportǁread_message__mutmut_22': xǁStdioTransportǁread_message__mutmut_22, 
        'xǁStdioTransportǁread_message__mutmut_23': xǁStdioTransportǁread_message__mutmut_23, 
        'xǁStdioTransportǁread_message__mutmut_24': xǁStdioTransportǁread_message__mutmut_24, 
        'xǁStdioTransportǁread_message__mutmut_25': xǁStdioTransportǁread_message__mutmut_25, 
        'xǁStdioTransportǁread_message__mutmut_26': xǁStdioTransportǁread_message__mutmut_26, 
        'xǁStdioTransportǁread_message__mutmut_27': xǁStdioTransportǁread_message__mutmut_27, 
        'xǁStdioTransportǁread_message__mutmut_28': xǁStdioTransportǁread_message__mutmut_28, 
        'xǁStdioTransportǁread_message__mutmut_29': xǁStdioTransportǁread_message__mutmut_29, 
        'xǁStdioTransportǁread_message__mutmut_30': xǁStdioTransportǁread_message__mutmut_30, 
        'xǁStdioTransportǁread_message__mutmut_31': xǁStdioTransportǁread_message__mutmut_31, 
        'xǁStdioTransportǁread_message__mutmut_32': xǁStdioTransportǁread_message__mutmut_32, 
        'xǁStdioTransportǁread_message__mutmut_33': xǁStdioTransportǁread_message__mutmut_33
    }
    
    def read_message(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStdioTransportǁread_message__mutmut_orig"), object.__getattribute__(self, "xǁStdioTransportǁread_message__mutmut_mutants"), args, kwargs, self)
        return result 
    
    read_message.__signature__ = _mutmut_signature(xǁStdioTransportǁread_message__mutmut_orig)
    xǁStdioTransportǁread_message__mutmut_orig.__name__ = 'xǁStdioTransportǁread_message'
    
    async def xǁStdioTransportǁwrite_message__mutmut_orig(self, message: dict[str, Any]) -> None:
        """Write a JSON-RPC message to stdout.
        
        Args:
            message: JSON-RPC message to write.
        """
        writer = await self._get_writer()
        
        # Serialize and encode
        text = json.dumps(message, separators=(",", ":"))
        data = (text + "\n").encode(self._config.encoding)
        
        # Check size
        if len(data) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(data),
                self._config.max_message_size
            )
        
        writer.write(data)
        await writer.drain()
    
    async def xǁStdioTransportǁwrite_message__mutmut_1(self, message: dict[str, Any]) -> None:
        """Write a JSON-RPC message to stdout.
        
        Args:
            message: JSON-RPC message to write.
        """
        writer = None
        
        # Serialize and encode
        text = json.dumps(message, separators=(",", ":"))
        data = (text + "\n").encode(self._config.encoding)
        
        # Check size
        if len(data) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(data),
                self._config.max_message_size
            )
        
        writer.write(data)
        await writer.drain()
    
    async def xǁStdioTransportǁwrite_message__mutmut_2(self, message: dict[str, Any]) -> None:
        """Write a JSON-RPC message to stdout.
        
        Args:
            message: JSON-RPC message to write.
        """
        writer = await self._get_writer()
        
        # Serialize and encode
        text = None
        data = (text + "\n").encode(self._config.encoding)
        
        # Check size
        if len(data) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(data),
                self._config.max_message_size
            )
        
        writer.write(data)
        await writer.drain()
    
    async def xǁStdioTransportǁwrite_message__mutmut_3(self, message: dict[str, Any]) -> None:
        """Write a JSON-RPC message to stdout.
        
        Args:
            message: JSON-RPC message to write.
        """
        writer = await self._get_writer()
        
        # Serialize and encode
        text = json.dumps(None, separators=(",", ":"))
        data = (text + "\n").encode(self._config.encoding)
        
        # Check size
        if len(data) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(data),
                self._config.max_message_size
            )
        
        writer.write(data)
        await writer.drain()
    
    async def xǁStdioTransportǁwrite_message__mutmut_4(self, message: dict[str, Any]) -> None:
        """Write a JSON-RPC message to stdout.
        
        Args:
            message: JSON-RPC message to write.
        """
        writer = await self._get_writer()
        
        # Serialize and encode
        text = json.dumps(message, separators=None)
        data = (text + "\n").encode(self._config.encoding)
        
        # Check size
        if len(data) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(data),
                self._config.max_message_size
            )
        
        writer.write(data)
        await writer.drain()
    
    async def xǁStdioTransportǁwrite_message__mutmut_5(self, message: dict[str, Any]) -> None:
        """Write a JSON-RPC message to stdout.
        
        Args:
            message: JSON-RPC message to write.
        """
        writer = await self._get_writer()
        
        # Serialize and encode
        text = json.dumps(separators=(",", ":"))
        data = (text + "\n").encode(self._config.encoding)
        
        # Check size
        if len(data) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(data),
                self._config.max_message_size
            )
        
        writer.write(data)
        await writer.drain()
    
    async def xǁStdioTransportǁwrite_message__mutmut_6(self, message: dict[str, Any]) -> None:
        """Write a JSON-RPC message to stdout.
        
        Args:
            message: JSON-RPC message to write.
        """
        writer = await self._get_writer()
        
        # Serialize and encode
        text = json.dumps(message, )
        data = (text + "\n").encode(self._config.encoding)
        
        # Check size
        if len(data) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(data),
                self._config.max_message_size
            )
        
        writer.write(data)
        await writer.drain()
    
    async def xǁStdioTransportǁwrite_message__mutmut_7(self, message: dict[str, Any]) -> None:
        """Write a JSON-RPC message to stdout.
        
        Args:
            message: JSON-RPC message to write.
        """
        writer = await self._get_writer()
        
        # Serialize and encode
        text = json.dumps(message, separators=("XX,XX", ":"))
        data = (text + "\n").encode(self._config.encoding)
        
        # Check size
        if len(data) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(data),
                self._config.max_message_size
            )
        
        writer.write(data)
        await writer.drain()
    
    async def xǁStdioTransportǁwrite_message__mutmut_8(self, message: dict[str, Any]) -> None:
        """Write a JSON-RPC message to stdout.
        
        Args:
            message: JSON-RPC message to write.
        """
        writer = await self._get_writer()
        
        # Serialize and encode
        text = json.dumps(message, separators=(",", "XX:XX"))
        data = (text + "\n").encode(self._config.encoding)
        
        # Check size
        if len(data) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(data),
                self._config.max_message_size
            )
        
        writer.write(data)
        await writer.drain()
    
    async def xǁStdioTransportǁwrite_message__mutmut_9(self, message: dict[str, Any]) -> None:
        """Write a JSON-RPC message to stdout.
        
        Args:
            message: JSON-RPC message to write.
        """
        writer = await self._get_writer()
        
        # Serialize and encode
        text = json.dumps(message, separators=(",", ":"))
        data = None
        
        # Check size
        if len(data) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(data),
                self._config.max_message_size
            )
        
        writer.write(data)
        await writer.drain()
    
    async def xǁStdioTransportǁwrite_message__mutmut_10(self, message: dict[str, Any]) -> None:
        """Write a JSON-RPC message to stdout.
        
        Args:
            message: JSON-RPC message to write.
        """
        writer = await self._get_writer()
        
        # Serialize and encode
        text = json.dumps(message, separators=(",", ":"))
        data = (text + "\n").encode(None)
        
        # Check size
        if len(data) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(data),
                self._config.max_message_size
            )
        
        writer.write(data)
        await writer.drain()
    
    async def xǁStdioTransportǁwrite_message__mutmut_11(self, message: dict[str, Any]) -> None:
        """Write a JSON-RPC message to stdout.
        
        Args:
            message: JSON-RPC message to write.
        """
        writer = await self._get_writer()
        
        # Serialize and encode
        text = json.dumps(message, separators=(",", ":"))
        data = (text - "\n").encode(self._config.encoding)
        
        # Check size
        if len(data) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(data),
                self._config.max_message_size
            )
        
        writer.write(data)
        await writer.drain()
    
    async def xǁStdioTransportǁwrite_message__mutmut_12(self, message: dict[str, Any]) -> None:
        """Write a JSON-RPC message to stdout.
        
        Args:
            message: JSON-RPC message to write.
        """
        writer = await self._get_writer()
        
        # Serialize and encode
        text = json.dumps(message, separators=(",", ":"))
        data = (text + "XX\nXX").encode(self._config.encoding)
        
        # Check size
        if len(data) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(data),
                self._config.max_message_size
            )
        
        writer.write(data)
        await writer.drain()
    
    async def xǁStdioTransportǁwrite_message__mutmut_13(self, message: dict[str, Any]) -> None:
        """Write a JSON-RPC message to stdout.
        
        Args:
            message: JSON-RPC message to write.
        """
        writer = await self._get_writer()
        
        # Serialize and encode
        text = json.dumps(message, separators=(",", ":"))
        data = (text + "\n").encode(self._config.encoding)
        
        # Check size
        if len(data) >= self._config.max_message_size:
            raise MessageTooLargeError(
                len(data),
                self._config.max_message_size
            )
        
        writer.write(data)
        await writer.drain()
    
    async def xǁStdioTransportǁwrite_message__mutmut_14(self, message: dict[str, Any]) -> None:
        """Write a JSON-RPC message to stdout.
        
        Args:
            message: JSON-RPC message to write.
        """
        writer = await self._get_writer()
        
        # Serialize and encode
        text = json.dumps(message, separators=(",", ":"))
        data = (text + "\n").encode(self._config.encoding)
        
        # Check size
        if len(data) > self._config.max_message_size:
            raise MessageTooLargeError(
                None,
                self._config.max_message_size
            )
        
        writer.write(data)
        await writer.drain()
    
    async def xǁStdioTransportǁwrite_message__mutmut_15(self, message: dict[str, Any]) -> None:
        """Write a JSON-RPC message to stdout.
        
        Args:
            message: JSON-RPC message to write.
        """
        writer = await self._get_writer()
        
        # Serialize and encode
        text = json.dumps(message, separators=(",", ":"))
        data = (text + "\n").encode(self._config.encoding)
        
        # Check size
        if len(data) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(data),
                None
            )
        
        writer.write(data)
        await writer.drain()
    
    async def xǁStdioTransportǁwrite_message__mutmut_16(self, message: dict[str, Any]) -> None:
        """Write a JSON-RPC message to stdout.
        
        Args:
            message: JSON-RPC message to write.
        """
        writer = await self._get_writer()
        
        # Serialize and encode
        text = json.dumps(message, separators=(",", ":"))
        data = (text + "\n").encode(self._config.encoding)
        
        # Check size
        if len(data) > self._config.max_message_size:
            raise MessageTooLargeError(
                self._config.max_message_size
            )
        
        writer.write(data)
        await writer.drain()
    
    async def xǁStdioTransportǁwrite_message__mutmut_17(self, message: dict[str, Any]) -> None:
        """Write a JSON-RPC message to stdout.
        
        Args:
            message: JSON-RPC message to write.
        """
        writer = await self._get_writer()
        
        # Serialize and encode
        text = json.dumps(message, separators=(",", ":"))
        data = (text + "\n").encode(self._config.encoding)
        
        # Check size
        if len(data) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(data),
                )
        
        writer.write(data)
        await writer.drain()
    
    async def xǁStdioTransportǁwrite_message__mutmut_18(self, message: dict[str, Any]) -> None:
        """Write a JSON-RPC message to stdout.
        
        Args:
            message: JSON-RPC message to write.
        """
        writer = await self._get_writer()
        
        # Serialize and encode
        text = json.dumps(message, separators=(",", ":"))
        data = (text + "\n").encode(self._config.encoding)
        
        # Check size
        if len(data) > self._config.max_message_size:
            raise MessageTooLargeError(
                len(data),
                self._config.max_message_size
            )
        
        writer.write(None)
        await writer.drain()
    
    xǁStdioTransportǁwrite_message__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStdioTransportǁwrite_message__mutmut_1': xǁStdioTransportǁwrite_message__mutmut_1, 
        'xǁStdioTransportǁwrite_message__mutmut_2': xǁStdioTransportǁwrite_message__mutmut_2, 
        'xǁStdioTransportǁwrite_message__mutmut_3': xǁStdioTransportǁwrite_message__mutmut_3, 
        'xǁStdioTransportǁwrite_message__mutmut_4': xǁStdioTransportǁwrite_message__mutmut_4, 
        'xǁStdioTransportǁwrite_message__mutmut_5': xǁStdioTransportǁwrite_message__mutmut_5, 
        'xǁStdioTransportǁwrite_message__mutmut_6': xǁStdioTransportǁwrite_message__mutmut_6, 
        'xǁStdioTransportǁwrite_message__mutmut_7': xǁStdioTransportǁwrite_message__mutmut_7, 
        'xǁStdioTransportǁwrite_message__mutmut_8': xǁStdioTransportǁwrite_message__mutmut_8, 
        'xǁStdioTransportǁwrite_message__mutmut_9': xǁStdioTransportǁwrite_message__mutmut_9, 
        'xǁStdioTransportǁwrite_message__mutmut_10': xǁStdioTransportǁwrite_message__mutmut_10, 
        'xǁStdioTransportǁwrite_message__mutmut_11': xǁStdioTransportǁwrite_message__mutmut_11, 
        'xǁStdioTransportǁwrite_message__mutmut_12': xǁStdioTransportǁwrite_message__mutmut_12, 
        'xǁStdioTransportǁwrite_message__mutmut_13': xǁStdioTransportǁwrite_message__mutmut_13, 
        'xǁStdioTransportǁwrite_message__mutmut_14': xǁStdioTransportǁwrite_message__mutmut_14, 
        'xǁStdioTransportǁwrite_message__mutmut_15': xǁStdioTransportǁwrite_message__mutmut_15, 
        'xǁStdioTransportǁwrite_message__mutmut_16': xǁStdioTransportǁwrite_message__mutmut_16, 
        'xǁStdioTransportǁwrite_message__mutmut_17': xǁStdioTransportǁwrite_message__mutmut_17, 
        'xǁStdioTransportǁwrite_message__mutmut_18': xǁStdioTransportǁwrite_message__mutmut_18
    }
    
    def write_message(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStdioTransportǁwrite_message__mutmut_orig"), object.__getattribute__(self, "xǁStdioTransportǁwrite_message__mutmut_mutants"), args, kwargs, self)
        return result 
    
    write_message.__signature__ = _mutmut_signature(xǁStdioTransportǁwrite_message__mutmut_orig)
    xǁStdioTransportǁwrite_message__mutmut_orig.__name__ = 'xǁStdioTransportǁwrite_message'
    
    async def xǁStdioTransportǁmessage_stream__mutmut_orig(self) -> AsyncIterator[dict[str, Any]]:
        """Iterate over incoming messages.
        
        Yields:
            Parsed JSON-RPC messages until EOF or error.
        """
        self._running = True
        
        while self._running:
            try:
                message = await self.read_message()
                if message is None:
                    break
                yield message
            except TransportError as e:
                logger.debug(f"TransportError: {e}")
                self._logger.error("Transport error: %s", e)
                # Continue reading after recoverable errors
                continue
    
    async def xǁStdioTransportǁmessage_stream__mutmut_1(self) -> AsyncIterator[dict[str, Any]]:
        """Iterate over incoming messages.
        
        Yields:
            Parsed JSON-RPC messages until EOF or error.
        """
        self._running = None
        
        while self._running:
            try:
                message = await self.read_message()
                if message is None:
                    break
                yield message
            except TransportError as e:
                logger.debug(f"TransportError: {e}")
                self._logger.error("Transport error: %s", e)
                # Continue reading after recoverable errors
                continue
    
    async def xǁStdioTransportǁmessage_stream__mutmut_2(self) -> AsyncIterator[dict[str, Any]]:
        """Iterate over incoming messages.
        
        Yields:
            Parsed JSON-RPC messages until EOF or error.
        """
        self._running = False
        
        while self._running:
            try:
                message = await self.read_message()
                if message is None:
                    break
                yield message
            except TransportError as e:
                logger.debug(f"TransportError: {e}")
                self._logger.error("Transport error: %s", e)
                # Continue reading after recoverable errors
                continue
    
    async def xǁStdioTransportǁmessage_stream__mutmut_3(self) -> AsyncIterator[dict[str, Any]]:
        """Iterate over incoming messages.
        
        Yields:
            Parsed JSON-RPC messages until EOF or error.
        """
        self._running = True
        
        while self._running:
            try:
                message = None
                if message is None:
                    break
                yield message
            except TransportError as e:
                logger.debug(f"TransportError: {e}")
                self._logger.error("Transport error: %s", e)
                # Continue reading after recoverable errors
                continue
    
    async def xǁStdioTransportǁmessage_stream__mutmut_4(self) -> AsyncIterator[dict[str, Any]]:
        """Iterate over incoming messages.
        
        Yields:
            Parsed JSON-RPC messages until EOF or error.
        """
        self._running = True
        
        while self._running:
            try:
                message = await self.read_message()
                if message is not None:
                    break
                yield message
            except TransportError as e:
                logger.debug(f"TransportError: {e}")
                self._logger.error("Transport error: %s", e)
                # Continue reading after recoverable errors
                continue
    
    async def xǁStdioTransportǁmessage_stream__mutmut_5(self) -> AsyncIterator[dict[str, Any]]:
        """Iterate over incoming messages.
        
        Yields:
            Parsed JSON-RPC messages until EOF or error.
        """
        self._running = True
        
        while self._running:
            try:
                message = await self.read_message()
                if message is None:
                    return
                yield message
            except TransportError as e:
                logger.debug(f"TransportError: {e}")
                self._logger.error("Transport error: %s", e)
                # Continue reading after recoverable errors
                continue
    
    async def xǁStdioTransportǁmessage_stream__mutmut_6(self) -> AsyncIterator[dict[str, Any]]:
        """Iterate over incoming messages.
        
        Yields:
            Parsed JSON-RPC messages until EOF or error.
        """
        self._running = True
        
        while self._running:
            try:
                message = await self.read_message()
                if message is None:
                    break
                yield message
            except TransportError as e:
                logger.debug(None)
                self._logger.error("Transport error: %s", e)
                # Continue reading after recoverable errors
                continue
    
    async def xǁStdioTransportǁmessage_stream__mutmut_7(self) -> AsyncIterator[dict[str, Any]]:
        """Iterate over incoming messages.
        
        Yields:
            Parsed JSON-RPC messages until EOF or error.
        """
        self._running = True
        
        while self._running:
            try:
                message = await self.read_message()
                if message is None:
                    break
                yield message
            except TransportError as e:
                logger.debug(f"TransportError: {e}")
                self._logger.error(None, e)
                # Continue reading after recoverable errors
                continue
    
    async def xǁStdioTransportǁmessage_stream__mutmut_8(self) -> AsyncIterator[dict[str, Any]]:
        """Iterate over incoming messages.
        
        Yields:
            Parsed JSON-RPC messages until EOF or error.
        """
        self._running = True
        
        while self._running:
            try:
                message = await self.read_message()
                if message is None:
                    break
                yield message
            except TransportError as e:
                logger.debug(f"TransportError: {e}")
                self._logger.error("Transport error: %s", None)
                # Continue reading after recoverable errors
                continue
    
    async def xǁStdioTransportǁmessage_stream__mutmut_9(self) -> AsyncIterator[dict[str, Any]]:
        """Iterate over incoming messages.
        
        Yields:
            Parsed JSON-RPC messages until EOF or error.
        """
        self._running = True
        
        while self._running:
            try:
                message = await self.read_message()
                if message is None:
                    break
                yield message
            except TransportError as e:
                logger.debug(f"TransportError: {e}")
                self._logger.error(e)
                # Continue reading after recoverable errors
                continue
    
    async def xǁStdioTransportǁmessage_stream__mutmut_10(self) -> AsyncIterator[dict[str, Any]]:
        """Iterate over incoming messages.
        
        Yields:
            Parsed JSON-RPC messages until EOF or error.
        """
        self._running = True
        
        while self._running:
            try:
                message = await self.read_message()
                if message is None:
                    break
                yield message
            except TransportError as e:
                logger.debug(f"TransportError: {e}")
                self._logger.error("Transport error: %s", )
                # Continue reading after recoverable errors
                continue
    
    async def xǁStdioTransportǁmessage_stream__mutmut_11(self) -> AsyncIterator[dict[str, Any]]:
        """Iterate over incoming messages.
        
        Yields:
            Parsed JSON-RPC messages until EOF or error.
        """
        self._running = True
        
        while self._running:
            try:
                message = await self.read_message()
                if message is None:
                    break
                yield message
            except TransportError as e:
                logger.debug(f"TransportError: {e}")
                self._logger.error("XXTransport error: %sXX", e)
                # Continue reading after recoverable errors
                continue
    
    async def xǁStdioTransportǁmessage_stream__mutmut_12(self) -> AsyncIterator[dict[str, Any]]:
        """Iterate over incoming messages.
        
        Yields:
            Parsed JSON-RPC messages until EOF or error.
        """
        self._running = True
        
        while self._running:
            try:
                message = await self.read_message()
                if message is None:
                    break
                yield message
            except TransportError as e:
                logger.debug(f"TransportError: {e}")
                self._logger.error("transport error: %s", e)
                # Continue reading after recoverable errors
                continue
    
    async def xǁStdioTransportǁmessage_stream__mutmut_13(self) -> AsyncIterator[dict[str, Any]]:
        """Iterate over incoming messages.
        
        Yields:
            Parsed JSON-RPC messages until EOF or error.
        """
        self._running = True
        
        while self._running:
            try:
                message = await self.read_message()
                if message is None:
                    break
                yield message
            except TransportError as e:
                logger.debug(f"TransportError: {e}")
                self._logger.error("TRANSPORT ERROR: %S", e)
                # Continue reading after recoverable errors
                continue
    
    async def xǁStdioTransportǁmessage_stream__mutmut_14(self) -> AsyncIterator[dict[str, Any]]:
        """Iterate over incoming messages.
        
        Yields:
            Parsed JSON-RPC messages until EOF or error.
        """
        self._running = True
        
        while self._running:
            try:
                message = await self.read_message()
                if message is None:
                    break
                yield message
            except TransportError as e:
                logger.debug(f"TransportError: {e}")
                self._logger.error("Transport error: %s", e)
                # Continue reading after recoverable errors
                break
    
    xǁStdioTransportǁmessage_stream__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStdioTransportǁmessage_stream__mutmut_1': xǁStdioTransportǁmessage_stream__mutmut_1, 
        'xǁStdioTransportǁmessage_stream__mutmut_2': xǁStdioTransportǁmessage_stream__mutmut_2, 
        'xǁStdioTransportǁmessage_stream__mutmut_3': xǁStdioTransportǁmessage_stream__mutmut_3, 
        'xǁStdioTransportǁmessage_stream__mutmut_4': xǁStdioTransportǁmessage_stream__mutmut_4, 
        'xǁStdioTransportǁmessage_stream__mutmut_5': xǁStdioTransportǁmessage_stream__mutmut_5, 
        'xǁStdioTransportǁmessage_stream__mutmut_6': xǁStdioTransportǁmessage_stream__mutmut_6, 
        'xǁStdioTransportǁmessage_stream__mutmut_7': xǁStdioTransportǁmessage_stream__mutmut_7, 
        'xǁStdioTransportǁmessage_stream__mutmut_8': xǁStdioTransportǁmessage_stream__mutmut_8, 
        'xǁStdioTransportǁmessage_stream__mutmut_9': xǁStdioTransportǁmessage_stream__mutmut_9, 
        'xǁStdioTransportǁmessage_stream__mutmut_10': xǁStdioTransportǁmessage_stream__mutmut_10, 
        'xǁStdioTransportǁmessage_stream__mutmut_11': xǁStdioTransportǁmessage_stream__mutmut_11, 
        'xǁStdioTransportǁmessage_stream__mutmut_12': xǁStdioTransportǁmessage_stream__mutmut_12, 
        'xǁStdioTransportǁmessage_stream__mutmut_13': xǁStdioTransportǁmessage_stream__mutmut_13, 
        'xǁStdioTransportǁmessage_stream__mutmut_14': xǁStdioTransportǁmessage_stream__mutmut_14
    }
    
    def message_stream(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStdioTransportǁmessage_stream__mutmut_orig"), object.__getattribute__(self, "xǁStdioTransportǁmessage_stream__mutmut_mutants"), args, kwargs, self)
        return result 
    
    message_stream.__signature__ = _mutmut_signature(xǁStdioTransportǁmessage_stream__mutmut_orig)
    xǁStdioTransportǁmessage_stream__mutmut_orig.__name__ = 'xǁStdioTransportǁmessage_stream'
    
    def xǁStdioTransportǁstop__mutmut_orig(self) -> None:
        """Stop reading messages."""
        self._running = False
    
    def xǁStdioTransportǁstop__mutmut_1(self) -> None:
        """Stop reading messages."""
        self._running = None
    
    def xǁStdioTransportǁstop__mutmut_2(self) -> None:
        """Stop reading messages."""
        self._running = True
    
    xǁStdioTransportǁstop__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStdioTransportǁstop__mutmut_1': xǁStdioTransportǁstop__mutmut_1, 
        'xǁStdioTransportǁstop__mutmut_2': xǁStdioTransportǁstop__mutmut_2
    }
    
    def stop(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStdioTransportǁstop__mutmut_orig"), object.__getattribute__(self, "xǁStdioTransportǁstop__mutmut_mutants"), args, kwargs, self)
        return result 
    
    stop.__signature__ = _mutmut_signature(xǁStdioTransportǁstop__mutmut_orig)
    xǁStdioTransportǁstop__mutmut_orig.__name__ = 'xǁStdioTransportǁstop'
    
    async def xǁStdioTransportǁclose__mutmut_orig(self) -> None:
        """Close the transport."""
        self.stop()
        if self._writer:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                # Ignore errors during writer closure - the stream may already be closed
                # or in an invalid state. This is a cleanup operation and errors are non-critical.
                self._logger.debug("Writer close failed: %s", exc)
    
    async def xǁStdioTransportǁclose__mutmut_1(self) -> None:
        """Close the transport."""
        self.stop()
        if self._writer:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except Exception as exc:
                logger.debug(None)
                # Ignore errors during writer closure - the stream may already be closed
                # or in an invalid state. This is a cleanup operation and errors are non-critical.
                self._logger.debug("Writer close failed: %s", exc)
    
    async def xǁStdioTransportǁclose__mutmut_2(self) -> None:
        """Close the transport."""
        self.stop()
        if self._writer:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                # Ignore errors during writer closure - the stream may already be closed
                # or in an invalid state. This is a cleanup operation and errors are non-critical.
                self._logger.debug(None, exc)
    
    async def xǁStdioTransportǁclose__mutmut_3(self) -> None:
        """Close the transport."""
        self.stop()
        if self._writer:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                # Ignore errors during writer closure - the stream may already be closed
                # or in an invalid state. This is a cleanup operation and errors are non-critical.
                self._logger.debug("Writer close failed: %s", None)
    
    async def xǁStdioTransportǁclose__mutmut_4(self) -> None:
        """Close the transport."""
        self.stop()
        if self._writer:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                # Ignore errors during writer closure - the stream may already be closed
                # or in an invalid state. This is a cleanup operation and errors are non-critical.
                self._logger.debug(exc)
    
    async def xǁStdioTransportǁclose__mutmut_5(self) -> None:
        """Close the transport."""
        self.stop()
        if self._writer:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                # Ignore errors during writer closure - the stream may already be closed
                # or in an invalid state. This is a cleanup operation and errors are non-critical.
                self._logger.debug("Writer close failed: %s", )
    
    async def xǁStdioTransportǁclose__mutmut_6(self) -> None:
        """Close the transport."""
        self.stop()
        if self._writer:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                # Ignore errors during writer closure - the stream may already be closed
                # or in an invalid state. This is a cleanup operation and errors are non-critical.
                self._logger.debug("XXWriter close failed: %sXX", exc)
    
    async def xǁStdioTransportǁclose__mutmut_7(self) -> None:
        """Close the transport."""
        self.stop()
        if self._writer:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                # Ignore errors during writer closure - the stream may already be closed
                # or in an invalid state. This is a cleanup operation and errors are non-critical.
                self._logger.debug("writer close failed: %s", exc)
    
    async def xǁStdioTransportǁclose__mutmut_8(self) -> None:
        """Close the transport."""
        self.stop()
        if self._writer:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                # Ignore errors during writer closure - the stream may already be closed
                # or in an invalid state. This is a cleanup operation and errors are non-critical.
                self._logger.debug("WRITER CLOSE FAILED: %S", exc)
    
    xǁStdioTransportǁclose__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStdioTransportǁclose__mutmut_1': xǁStdioTransportǁclose__mutmut_1, 
        'xǁStdioTransportǁclose__mutmut_2': xǁStdioTransportǁclose__mutmut_2, 
        'xǁStdioTransportǁclose__mutmut_3': xǁStdioTransportǁclose__mutmut_3, 
        'xǁStdioTransportǁclose__mutmut_4': xǁStdioTransportǁclose__mutmut_4, 
        'xǁStdioTransportǁclose__mutmut_5': xǁStdioTransportǁclose__mutmut_5, 
        'xǁStdioTransportǁclose__mutmut_6': xǁStdioTransportǁclose__mutmut_6, 
        'xǁStdioTransportǁclose__mutmut_7': xǁStdioTransportǁclose__mutmut_7, 
        'xǁStdioTransportǁclose__mutmut_8': xǁStdioTransportǁclose__mutmut_8
    }
    
    def close(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStdioTransportǁclose__mutmut_orig"), object.__getattribute__(self, "xǁStdioTransportǁclose__mutmut_mutants"), args, kwargs, self)
        return result 
    
    close.__signature__ = _mutmut_signature(xǁStdioTransportǁclose__mutmut_orig)
    xǁStdioTransportǁclose__mutmut_orig.__name__ = 'xǁStdioTransportǁclose'


class MockStdioTransport(StdioTransport):
    """Mock transport for testing without actual stdio."""
    
    def xǁMockStdioTransportǁ__init____mutmut_orig(self, messages: Optional[list] = None) -> None:
        """Initialize mock transport.
        
        Args:
            messages: list of messages to return from read_message.
        """
        super().__init__()
        self._mock_messages = messages or []
        self._written_messages: list = []
        self._message_index = 0
    
    def xǁMockStdioTransportǁ__init____mutmut_1(self, messages: Optional[list] = None) -> None:
        """Initialize mock transport.
        
        Args:
            messages: list of messages to return from read_message.
        """
        super().__init__()
        self._mock_messages = None
        self._written_messages: list = []
        self._message_index = 0
    
    def xǁMockStdioTransportǁ__init____mutmut_2(self, messages: Optional[list] = None) -> None:
        """Initialize mock transport.
        
        Args:
            messages: list of messages to return from read_message.
        """
        super().__init__()
        self._mock_messages = messages and []
        self._written_messages: list = []
        self._message_index = 0
    
    def xǁMockStdioTransportǁ__init____mutmut_3(self, messages: Optional[list] = None) -> None:
        """Initialize mock transport.
        
        Args:
            messages: list of messages to return from read_message.
        """
        super().__init__()
        self._mock_messages = messages or []
        self._written_messages: list = None
        self._message_index = 0
    
    def xǁMockStdioTransportǁ__init____mutmut_4(self, messages: Optional[list] = None) -> None:
        """Initialize mock transport.
        
        Args:
            messages: list of messages to return from read_message.
        """
        super().__init__()
        self._mock_messages = messages or []
        self._written_messages: list = []
        self._message_index = None
    
    def xǁMockStdioTransportǁ__init____mutmut_5(self, messages: Optional[list] = None) -> None:
        """Initialize mock transport.
        
        Args:
            messages: list of messages to return from read_message.
        """
        super().__init__()
        self._mock_messages = messages or []
        self._written_messages: list = []
        self._message_index = 1
    
    xǁMockStdioTransportǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMockStdioTransportǁ__init____mutmut_1': xǁMockStdioTransportǁ__init____mutmut_1, 
        'xǁMockStdioTransportǁ__init____mutmut_2': xǁMockStdioTransportǁ__init____mutmut_2, 
        'xǁMockStdioTransportǁ__init____mutmut_3': xǁMockStdioTransportǁ__init____mutmut_3, 
        'xǁMockStdioTransportǁ__init____mutmut_4': xǁMockStdioTransportǁ__init____mutmut_4, 
        'xǁMockStdioTransportǁ__init____mutmut_5': xǁMockStdioTransportǁ__init____mutmut_5
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMockStdioTransportǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁMockStdioTransportǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁMockStdioTransportǁ__init____mutmut_orig)
    xǁMockStdioTransportǁ__init____mutmut_orig.__name__ = 'xǁMockStdioTransportǁ__init__'
    
    async def xǁMockStdioTransportǁread_message__mutmut_orig(self) -> Optional[dict[str, Any]]:
        """Read from the mock message queue."""
        if self._message_index >= len(self._mock_messages):
            return None
        
        message = self._mock_messages[self._message_index]
        self._message_index += 1
        return message
    
    async def xǁMockStdioTransportǁread_message__mutmut_1(self) -> Optional[dict[str, Any]]:
        """Read from the mock message queue."""
        if self._message_index > len(self._mock_messages):
            return None
        
        message = self._mock_messages[self._message_index]
        self._message_index += 1
        return message
    
    async def xǁMockStdioTransportǁread_message__mutmut_2(self) -> Optional[dict[str, Any]]:
        """Read from the mock message queue."""
        if self._message_index >= len(self._mock_messages):
            return None
        
        message = None
        self._message_index += 1
        return message
    
    async def xǁMockStdioTransportǁread_message__mutmut_3(self) -> Optional[dict[str, Any]]:
        """Read from the mock message queue."""
        if self._message_index >= len(self._mock_messages):
            return None
        
        message = self._mock_messages[self._message_index]
        self._message_index = 1
        return message
    
    async def xǁMockStdioTransportǁread_message__mutmut_4(self) -> Optional[dict[str, Any]]:
        """Read from the mock message queue."""
        if self._message_index >= len(self._mock_messages):
            return None
        
        message = self._mock_messages[self._message_index]
        self._message_index -= 1
        return message
    
    async def xǁMockStdioTransportǁread_message__mutmut_5(self) -> Optional[dict[str, Any]]:
        """Read from the mock message queue."""
        if self._message_index >= len(self._mock_messages):
            return None
        
        message = self._mock_messages[self._message_index]
        self._message_index += 2
        return message
    
    xǁMockStdioTransportǁread_message__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMockStdioTransportǁread_message__mutmut_1': xǁMockStdioTransportǁread_message__mutmut_1, 
        'xǁMockStdioTransportǁread_message__mutmut_2': xǁMockStdioTransportǁread_message__mutmut_2, 
        'xǁMockStdioTransportǁread_message__mutmut_3': xǁMockStdioTransportǁread_message__mutmut_3, 
        'xǁMockStdioTransportǁread_message__mutmut_4': xǁMockStdioTransportǁread_message__mutmut_4, 
        'xǁMockStdioTransportǁread_message__mutmut_5': xǁMockStdioTransportǁread_message__mutmut_5
    }
    
    def read_message(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMockStdioTransportǁread_message__mutmut_orig"), object.__getattribute__(self, "xǁMockStdioTransportǁread_message__mutmut_mutants"), args, kwargs, self)
        return result 
    
    read_message.__signature__ = _mutmut_signature(xǁMockStdioTransportǁread_message__mutmut_orig)
    xǁMockStdioTransportǁread_message__mutmut_orig.__name__ = 'xǁMockStdioTransportǁread_message'
    
    async def xǁMockStdioTransportǁwrite_message__mutmut_orig(self, message: dict[str, Any]) -> None:
        """Write to the mock message buffer."""
        self._written_messages.append(message)
    
    async def xǁMockStdioTransportǁwrite_message__mutmut_1(self, message: dict[str, Any]) -> None:
        """Write to the mock message buffer."""
        self._written_messages.append(None)
    
    xǁMockStdioTransportǁwrite_message__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMockStdioTransportǁwrite_message__mutmut_1': xǁMockStdioTransportǁwrite_message__mutmut_1
    }
    
    def write_message(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMockStdioTransportǁwrite_message__mutmut_orig"), object.__getattribute__(self, "xǁMockStdioTransportǁwrite_message__mutmut_mutants"), args, kwargs, self)
        return result 
    
    write_message.__signature__ = _mutmut_signature(xǁMockStdioTransportǁwrite_message__mutmut_orig)
    xǁMockStdioTransportǁwrite_message__mutmut_orig.__name__ = 'xǁMockStdioTransportǁwrite_message'
    
    def get_written_messages(self) -> list:
        """Get all messages written to this transport."""
        return self._written_messages
    
    def xǁMockStdioTransportǁadd_mock_message__mutmut_orig(self, message: dict[str, Any]) -> None:
        """Add a message to the mock queue."""
        self._mock_messages.append(message)
    
    def xǁMockStdioTransportǁadd_mock_message__mutmut_1(self, message: dict[str, Any]) -> None:
        """Add a message to the mock queue."""
        self._mock_messages.append(None)
    
    xǁMockStdioTransportǁadd_mock_message__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMockStdioTransportǁadd_mock_message__mutmut_1': xǁMockStdioTransportǁadd_mock_message__mutmut_1
    }
    
    def add_mock_message(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMockStdioTransportǁadd_mock_message__mutmut_orig"), object.__getattribute__(self, "xǁMockStdioTransportǁadd_mock_message__mutmut_mutants"), args, kwargs, self)
        return result 
    
    add_mock_message.__signature__ = _mutmut_signature(xǁMockStdioTransportǁadd_mock_message__mutmut_orig)
    xǁMockStdioTransportǁadd_mock_message__mutmut_orig.__name__ = 'xǁMockStdioTransportǁadd_mock_message'
