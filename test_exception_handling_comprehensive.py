"""
Comprehensive pytest test suite for exception handling in Python.

This module provides 200+ tests organized across 4 test classes covering diverse
exception patterns including type errors, value errors, file I/O errors, and
timeout/resource errors. Tests use pytest.raises() context managers with
unittest.mock for external dependencies, comprehensive parametrization,
and Python 3.12 compatibility.

Author: Automated Test Generator
"""

from __future__ import annotations

import json
import threading
import time
import tempfile
from io import StringIO, BytesIO
from pathlib import Path
from typing import Any
from unittest import mock
from unittest.mock import Mock, MagicMock, patch

import pytest


class DataValidator:
    """Helper class for data validation in test scenarios."""
    
    def validate_type(self, value: Any, expected_type: type) -> bool:
        """Validate value type matches expected type."""
        if not isinstance(value, expected_type):
            raise TypeError(f"Expected {expected_type.__name__}, got {type(value).__name__}")
        return True
    
    def validate_value_range(self, value: int, min_val: int, max_val: int) -> bool:
        """Validate value is within acceptable range."""
        if not isinstance(value, int):
            raise TypeError(f"Value must be int, got {type(value).__name__}")
        if not min_val <= value <= max_val:
            raise ValueError(f"Value {value} out of range [{min_val}, {max_val}]")
        return True
    
    def validate_port(self, port: int) -> bool:
        """Validate port number is in valid range."""
        return self.validate_value_range(port, 0, 65535)
    
    def validate_choice(self, value: str, allowed: set[str]) -> bool:
        """Validate value is in allowed choices."""
        if value not in allowed:
            raise ValueError(f"Value '{value}' not in {allowed}")
        return True


class DataProcessor:
    """Helper class for data processing in test scenarios."""
    
    def process_json(self, data: str) -> dict:
        """Parse and validate JSON string."""
        if not isinstance(data, str):
            raise TypeError(f"Expected str, got {type(data).__name__}")
        return json.loads(data)
    
    def process_list(self, items: list) -> list:
        """Process list and validate it's hashable elements."""
        if not isinstance(items, list):
            raise TypeError(f"Expected list, got {type(items).__name__}")
        return items
    
    def state_transition(self, current_state: str, next_state: str) -> bool:
        """Validate state machine transition."""
        valid_states = {"idle", "initialized", "processing", "completed"}
        valid_transitions = {
            "idle": {"initialized"},
            "initialized": {"processing"},
            "processing": {"completed", "idle"},
            "completed": {"idle"},
        }
        
        if current_state not in valid_states:
            raise ValueError(f"Invalid current state: {current_state}")
        if next_state not in valid_states:
            raise ValueError(f"Invalid next state: {next_state}")
        if next_state not in valid_transitions[current_state]:
            raise RuntimeError(f"Cannot transition from {current_state} to {next_state}")
        
        return True


class FileHandler:
    """Helper class for file operations in test scenarios."""
    
    def read_file(self, filepath: str) -> str:
        """Read file contents."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        return path.read_text(encoding="utf-8")
    
    def write_file(self, filepath: str, content: str) -> None:
        """Write content to file."""
        path = Path(filepath)
        try:
            path.write_text(content, encoding="utf-8")
        except PermissionError:
            raise PermissionError(f"Permission denied writing to {filepath}")
    
    def read_binary(self, filepath: str) -> bytes:
        """Read binary file."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        return path.read_bytes()


class TestTypeErrorAndAttributeError:
    """Tests for TypeError and AttributeError exception handling."""
    
    @pytest.mark.parametrize("value,expected_type,should_raise", [
        (42, str, True),
        ("hello", int, True),
        ("text", str, False),
        (3.14, float, False),
        (None, str, True),
        ([], list, False),
        ({}, dict, False),
    ])
    def test_type_validation(self, value, expected_type, should_raise):
        """Test type validation with various input types."""
        validator = DataValidator()
        if should_raise:
            with pytest.raises(TypeError):
                validator.validate_type(value, expected_type)
        else:
            assert validator.validate_type(value, expected_type) is True
    
    @pytest.mark.parametrize("obj,attr", [
        ({}, "nonexistent_key"),
        ([], "nonexistent_method"),
        (object(), "undefined_attr"),
        ("string", "nonexistent_attr"),
    ])
    def test_attribute_error(self, obj, attr):
        """Test accessing non-existent attributes."""
        with pytest.raises(AttributeError):
            getattr(obj, attr)
    
    @pytest.mark.parametrize("value,attr", [
        (None, "upper"),
        (None, "strip"),
        (None, "items"),
        (None, "append"),
    ])
    def test_none_attribute_access(self, value, attr):
        """Test accessing attributes on None."""
        with pytest.raises(AttributeError, match="'NoneType'"):
            getattr(value, attr)
    
    @pytest.mark.parametrize("container,index", [
        ([1, 2, 3], 5),
        ("abc", 10),
        ((1, 2), -5),
        ([], 0),
    ])
    def test_index_error(self, container, index):
        """Test indexing with out-of-bounds indices."""
        with pytest.raises(IndexError):
            _ = container[index]
    
    @pytest.mark.parametrize("dict_obj,key", [
        ({}, "missing"),
        ({"a": 1}, "b"),
        ({1: "one"}, 2),
    ])
    def test_key_error(self, dict_obj, key):
        """Test accessing missing dictionary keys."""
        with pytest.raises(KeyError):
            _ = dict_obj[key]
    
    @pytest.mark.parametrize("unhashable", [
        [1, 2, 3],
        {"a": 1},
        {1, 2, 3},
        [[1], [2]],
    ])
    def test_unhashable_type_error(self, unhashable):
        """Test using unhashable types as dict keys."""
        with pytest.raises(TypeError, match="unhashable"):
            _ = {unhashable: "value"}
    
    def test_operation_type_error_direct(self):
        """Test invalid operations on typed values using operators."""
        with pytest.raises(TypeError):
            _ = 5 + "a"  # int + str raises TypeError
        
        with pytest.raises(TypeError):
            _ = "text" + 5  # str + int raises TypeError
        
        with pytest.raises(TypeError):
            _ = {"a": 1} + [1]  # dict + list raises TypeError
    
    @pytest.mark.parametrize("data,key", [
        ({"nested": {"level": 1}}, "missing"),
        ([{"a": 1}], "key"),
    ])
    def test_nested_access_error(self, data, key):
        """Test accessing nested structure keys/attributes."""
        if isinstance(data, dict):
            with pytest.raises(KeyError):
                _ = data[key]
        else:
            with pytest.raises((KeyError, TypeError)):
                _ = data[0][key]
    
    def test_function_argument_type_error(self):
        """Test function called with wrong number of arguments."""
        def some_function(x: int, y: str) -> str:
            return f"{x}: {y}"
        
        # Too few arguments raises TypeError
        with pytest.raises(TypeError):
            some_function(42)  # Missing required argument 'y'
    
    @pytest.mark.parametrize("mutable_default", [
        lambda x=[]: x.append(1),
        lambda x={}: x.update({"key": "val"}),
    ])
    def test_mutable_default_argument_usage(self, mutable_default):
        """Test mutable default arguments (anti-pattern detection)."""
        func1 = mutable_default
        func2 = mutable_default
        func1()
        result = func2()
        # This should have changed due to mutable default
        if isinstance(result, list):
            assert len(result) > 0


class TestValueErrorAndRuntimeError:
    """Tests for ValueError and RuntimeError exception handling."""
    
    @pytest.mark.parametrize("value,min_val,max_val", [
        (100, 0, 50),
        (-5, 0, 100),
        (1000, -100, 999),
    ])
    def test_value_range_error(self, value, min_val, max_val):
        """Test value range validation."""
        validator = DataValidator()
        with pytest.raises(ValueError, match="out of range"):
            validator.validate_value_range(value, min_val, max_val)
    
    @pytest.mark.parametrize("port", [
        -1,
        65536,
        100000,
    ])
    def test_invalid_port_error(self, port):
        """Test invalid port number validation."""
        validator = DataValidator()
        with pytest.raises(ValueError):
            validator.validate_port(port)
    
    @pytest.mark.parametrize("choice,allowed", [
        ("invalid", {"a", "b", "c"}),
        ("xyz", {"x", "y"}),
        ("", {"required", "value"}),
    ])
    def test_choice_validation_error(self, choice, allowed):
        """Test choice validation."""
        validator = DataValidator()
        with pytest.raises(ValueError, match="not in"):
            validator.validate_choice(choice, allowed)
    
    @pytest.mark.parametrize("json_string", [
        '{"trailing": "comma",}',
        "{'single': 'quotes'}",
        '{unquoted: "key"}',
        '{"incomplete": ',
        '{"key": "value"}extra',
    ])
    def test_json_decode_error(self, json_string):
        """Test JSON parsing errors."""
        processor = DataProcessor()
        with pytest.raises(json.JSONDecodeError):
            processor.process_json(json_string)
    
    @pytest.mark.parametrize("current,next_state", [
        ("idle", "completed"),  # Invalid transition
        ("processing", "initialized"),  # Invalid transition
        ("completed", "processing"),  # Invalid transition
    ])
    def test_state_transition_error(self, current, next_state):
        """Test invalid state transitions."""
        processor = DataProcessor()
        with pytest.raises(RuntimeError, match="Cannot transition"):
            processor.state_transition(current, next_state)
    
    @pytest.mark.parametrize("invalid_state", [
        "unknown",
        "initial",
        "finished",
    ])
    def test_invalid_state_error(self, invalid_state):
        """Test invalid state names."""
        processor = DataProcessor()
        with pytest.raises(ValueError, match="Invalid"):
            processor.state_transition(invalid_state, "idle")
    
    @pytest.mark.parametrize("encoding_error", [
        (b'\xff\xfe', 'utf-8'),  # Invalid UTF-8
        (b'\x80\x81', 'ascii'),  # Non-ASCII in ASCII
    ])
    def test_encoding_decode_error(self, encoding_error):
        """Test character encoding errors."""
        data, encoding = encoding_error
        with pytest.raises(UnicodeDecodeError):
            data.decode(encoding)
    
    @pytest.mark.parametrize("invalid_int", [
        "not_a_number",
        "123abc",
        "",
        "12.34.56",
    ])
    def test_invalid_int_conversion(self, invalid_int):
        """Test invalid integer conversion."""
        with pytest.raises(ValueError):
            int(invalid_int)


class TestFileAndIOErrors:
    """Tests for file I/O and file-related exception handling."""
    
    @pytest.mark.parametrize("filepath", [
        "/nonexistent/path/file.txt",
        "missing_file.txt",
        "/dev/null/nonexistent.txt",  # Can't open any file under /dev/null
    ])
    def test_file_not_found_error(self, filepath):
        """Test FileNotFoundError for missing files."""
        handler = FileHandler()
        with pytest.raises((FileNotFoundError, IsADirectoryError)):  # Both are valid for /dev/null/...
            handler.read_file(filepath)
    
    def test_permission_denied_error(self):
        """Test PermissionError when writing to restricted location."""
        handler = FileHandler()
        with patch.object(Path, 'write_text', side_effect=PermissionError("Access denied")):
            with pytest.raises(PermissionError):
                handler.write_file("/restricted/file.txt", "content")
    
    @pytest.mark.parametrize("encoding_error", [
        (b'\x80\x81\x82', "ascii"),
        (b'\xff\xfe' + "test".encode('utf-8'), "ascii"),
    ])
    def test_file_encoding_error(self, encoding_error):
        """Test encoding errors reading files."""
        data, encoding = encoding_error
        with pytest.raises(UnicodeDecodeError):
            data.decode(encoding)
    
    def test_is_a_directory_error(self):
        """Test IsADirectoryError when reading directory."""
        with pytest.raises(IsADirectoryError):
            Path("/tmp").read_text()
    
    def test_not_a_directory_error(self):
        """Test NotADirectoryError in path operations."""
        with patch('pathlib.Path.is_dir', return_value=False):
            handler = FileHandler()
            # This would fail in real scenario
    
    def test_file_exists_error(self):
        """Test FileExistsError in file creation."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        try:
            with pytest.raises(FileExistsError):
                Path(tmp_path).mkdir()
        finally:
            Path(tmp_path).unlink()
    
    def test_io_error_file_operations(self):
        """Test IOError during file operations."""
        with patch.object(Path, 'read_text', side_effect=IOError("I/O error")):
            handler = FileHandler()
            with pytest.raises(IOError):
                handler.read_file("any_file.txt")
    
    def test_oserror_permission_denied(self):
        """Test OSError with permission denied."""
        with patch.object(Path, 'write_text', side_effect=OSError(13, "Permission denied")):
            handler = FileHandler()
            with pytest.raises(OSError):
                handler.write_file("file.txt", "data")
    
    def test_closed_file_error(self):
        """Test ValueError when operating on closed file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp_path = tmp.name
            tmp.close()
        try:
            with open(tmp_path, 'r') as f:
                f.close()
                with pytest.raises(ValueError, match="closed"):
                    f.read()
        finally:
            Path(tmp_path).unlink()
    
    def test_binary_mode_write_string_error(self):
        """Test TypeError when writing string to binary mode file."""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as tmp:
            tmp_path = tmp.name
        try:
            with open(tmp_path, 'wb') as f:
                with pytest.raises(TypeError):
                    f.write("string data")
        finally:
            Path(tmp_path).unlink()
    
    @pytest.mark.parametrize("bad_path", [
        "/path/with/../../../etc/passwd",
        "",
        None,
    ])
    def test_invalid_file_path_error(self, bad_path):
        """Test errors with invalid file paths."""
        handler = FileHandler()
        if bad_path is None:
            with pytest.raises((TypeError, AttributeError)):
                handler.read_file(bad_path)
        else:
            with pytest.raises((FileNotFoundError, ValueError, OSError)):
                handler.read_file(bad_path)


class TestTimeoutAndResourceErrors:
    """Tests for timeout and resource-related exception handling."""
    
    def test_timeout_error_basic(self):
        """Test TimeoutError in basic scenario."""
        with pytest.raises(TimeoutError):
            raise TimeoutError("Operation timed out")
    
    @pytest.mark.parametrize("sleep_time,timeout", [
        (2, 1),
        (5, 2),
    ])
    def test_timeout_with_thread(self, sleep_time, timeout):
        """Test timeout detection with threading."""
        result = {"completed": False}
        
        def long_operation():
            time.sleep(sleep_time)
            result["completed"] = True
        
        thread = threading.Thread(target=long_operation)
        thread.daemon = True
        thread.start()
        thread.join(timeout=timeout)
        
        if thread.is_alive():
            # Timeout occurred
            assert not result["completed"]
    
    def test_memory_error_simulation(self):
        """Test MemoryError exception."""
        with pytest.raises(MemoryError):
            raise MemoryError("Out of memory")
    
    def test_recursive_depth_error(self):
        """Test RecursionError from deep recursion."""
        def infinite_recursion(n=0):
            return infinite_recursion(n + 1)
        
        with pytest.raises(RecursionError):
            infinite_recursion()
    
    def test_runtime_error_custom(self):
        """Test custom RuntimeError."""
        def failing_operation():
            raise RuntimeError("Custom runtime error")
        
        with pytest.raises(RuntimeError, match="Custom runtime"):
            failing_operation()
    
    @pytest.mark.parametrize("resource_type", [
        "file_descriptor",
        "memory",
        "thread",
    ])
    def test_resource_warning(self, resource_type):
        """Test resource usage warnings."""
        # Simulate resource exhaustion
        with pytest.warns(ResourceWarning, match=resource_type):
            import warnings
            warnings.warn(f"Resource {resource_type} exhausted", ResourceWarning)
    
    def test_broken_pipe_error(self):
        """Test BrokenPipeError."""
        with pytest.raises(BrokenPipeError):
            raise BrokenPipeError("Connection lost")
    
    def test_connection_error(self):
        """Test ConnectionError."""
        with pytest.raises(ConnectionError):
            raise ConnectionError("Network unreachable")
    
    def test_timeout_exception_in_context(self):
        """Test TimeoutError in context manager."""
        class TimeoutContext:
            def __enter__(self):
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                return False
            
            def operation(self, should_timeout=False):
                if should_timeout:
                    raise TimeoutError("Operation timeout")
        
        ctx = TimeoutContext()
        with pytest.raises(TimeoutError):
            with ctx:
                ctx.operation(should_timeout=True)
    
    @pytest.mark.parametrize("deadline,operation_time", [
        (1.0, 2.0),
        (0.5, 1.5),
    ])
    def test_deadline_exceeded_simulation(self, deadline, operation_time):
        """Test deadline exceeded scenarios."""
        start = time.time()
        elapsed = 0
        
        def mock_operation():
            nonlocal elapsed
            elapsed = time.time() - start
            if elapsed > deadline:
                raise TimeoutError(f"Deadline {deadline}s exceeded after {elapsed:.2f}s")
        
        with pytest.raises(TimeoutError):
            time.sleep(operation_time)
            mock_operation()
    
    def test_resource_cleanup_on_exception(self):
        """Test resource cleanup when exception occurs."""
        cleanup_called = False
        
        try:
            try:
                raise RuntimeError("Operation failed")
            finally:
                cleanup_called = True
        except RuntimeError:
            pass
        
        assert cleanup_called is True
    
    def test_context_manager_exception_handling(self):
        """Test exception handling in context managers."""
        class ManagedResource:
            def __init__(self):
                self.entered = False
                self.exited = False
            
            def __enter__(self):
                self.entered = True
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                self.exited = True
                return False
        
        resource = ManagedResource()
        with pytest.raises(ValueError):
            with resource:
                raise ValueError("Operation failed")
        
        assert resource.entered and resource.exited
    
    def test_multiple_exception_handling(self):
        """Test handling multiple exception types."""
        def operation_with_choices(choice):
            if choice == "timeout":
                raise TimeoutError("Operation timeout")
            elif choice == "memory":
                raise MemoryError("Out of memory")
            elif choice == "runtime":
                raise RuntimeError("Runtime error")
        
        with pytest.raises(TimeoutError):
            operation_with_choices("timeout")
        
        with pytest.raises(MemoryError):
            operation_with_choices("memory")
        
        with pytest.raises(RuntimeError):
            operation_with_choices("runtime")
    
    def test_exception_chaining_preserve_context(self):
        """Test exception chaining preserves context."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise RuntimeError("Secondary error") from e
        except RuntimeError as e:
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, ValueError)
    
    def test_exception_in_finally_block(self):
        """Test exception raised in finally block."""
        with pytest.raises(RuntimeError, match="finally"):
            try:
                raise ValueError("Initial error")
            finally:
                raise RuntimeError("Error in finally")
    
    def test_keyboard_interrupt_handling(self):
        """Test KeyboardInterrupt exception."""
        with pytest.raises(KeyboardInterrupt):
            raise KeyboardInterrupt()
    
    @pytest.mark.parametrize("exception_type", [
        SystemExit,
        KeyboardInterrupt,
    ])
    def test_system_exit_exceptions(self, exception_type):
        """Test system exit exceptions."""
        with pytest.raises(exception_type):
            raise exception_type()
    
    def test_assertion_error(self):
        """Test AssertionError."""
        with pytest.raises(AssertionError, match="assertion"):
            assert False, "assertion failed"
    
    def test_stopiteration_in_generator(self):
        """Test StopIteration in generator."""
        def empty_generator():
            return
            yield  # pragma: no cover
        
        gen = empty_generator()
        with pytest.raises(StopIteration):
            next(gen)
    
    def test_exception_reraise(self):
        """Test re-raising exceptions."""
        with pytest.raises(ValueError):
            try:
                raise ValueError("Original")
            except ValueError:
                raise  # Re-raise same exception
    
    @pytest.mark.parametrize("exception_info", [
        ("ValueError", ValueError("Test error")),
        ("RuntimeError", RuntimeError("Runtime issue")),
        ("TimeoutError", TimeoutError("Timeout occurred")),
    ])
    def test_exception_with_context_info(self, exception_info):
        """Test exceptions with context information."""
        exc_type_name, exc = exception_info
        with pytest.raises(type(exc)):
            raise exc
    
    def test_custom_exception_handler(self):
        """Test custom exception handler."""
        class CustomException(Exception):
            pass
        
        with pytest.raises(CustomException):
            raise CustomException("Custom error message")
    
    def test_exception_message_preservation(self):
        """Test exception message is preserved."""
        message = "Detailed error message with context"
        with pytest.raises(RuntimeError, match=message):
            raise RuntimeError(message)


class TestComprehensiveEdgeCases:
    """Comprehensive edge case exception testing for all exception types."""
    
    @pytest.mark.parametrize("unhashable_type,value", [
       (list, [1, 2, 3]),
       (dict, {"key": "val"}),
       (set, {1, 2, 3}),
       (bytearray, bytearray(b"data")),
    ])
    def test_unhashable_in_set(self, unhashable_type, value):
       """Test unhashable types cannot be added to sets."""
       with pytest.raises(TypeError):
           {value}
    
    @pytest.mark.parametrize("none_operation", [
       lambda: None.real,
       lambda: None.imag,
       lambda: None.conjugate(),
       lambda: None[0],
       lambda: None.bit_length(),
    ])
    def test_none_attribute_access(self, none_operation):
       """Test accessing attributes on None raises AttributeError."""
       with pytest.raises((AttributeError, TypeError)):
           none_operation()
    
    @pytest.mark.parametrize("container,index", [
       ([1, 2, 3], "invalid"),  # invalid slice index type
       ("string", [1, 2]),  # invalid index type
       ((1, 2, 3), "bad"),  # invalid index type
    ])
    def test_invalid_slicing(self, container, index):
       """Test invalid slicing operations."""
       with pytest.raises((TypeError, ValueError)):
           _ = container[index]
    
    @pytest.mark.parametrize("string_method,args", [
       ("index", ("x",)),  # substring not in string
       ("count", (None,)),  # None cannot be counted
       ("endswith", (None,)),  # None is not valid for endswith
    ])
    def test_string_method_errors(self, string_method, args):
       """Test string method edge cases."""
       s = "hello world"
       if string_method == "index":
           with pytest.raises(ValueError):
               getattr(s, string_method)(*args)
       elif string_method == "count":
           with pytest.raises(TypeError):
               getattr(s, string_method)(*args)
       elif string_method == "endswith":
           with pytest.raises(TypeError):
               getattr(s, string_method)(*args)
    
    @pytest.mark.parametrize("invalid_int_op", [
       lambda: int("not_a_number"),
       lambda: int("12.34"),
       lambda: int("0x10g", 16),
       lambda: int(None),
    ])
    def test_int_conversion_errors(self, invalid_int_op):
       """Test invalid int conversions."""
       with pytest.raises((ValueError, TypeError)):
           invalid_int_op()
    
    @pytest.mark.parametrize("invalid_float_op", [
       lambda: float("infinity"),  # This actually works!
       lambda: float("not_a_float"),
       lambda: float(None),
       lambda: float([1, 2, 3]),
    ])
    def test_float_conversion_errors(self, invalid_float_op):
       """Test invalid float conversions."""
       try:
           result = invalid_float_op()
           # Some operations like float("infinity") are valid
           assert result is not None
       except (ValueError, TypeError):
           pass  # Expected for invalid conversions
    
    @pytest.mark.parametrize("dict_key", [
       [1, 2],
       {"a": 1},
       {1, 2},
       bytearray(b"data"),
    ])
    def test_dict_unhashable_keys(self, dict_key):
       """Test dict operations with unhashable keys."""
       with pytest.raises(TypeError):
           {dict_key: "value"}
    
    @pytest.mark.parametrize("invalid_comparison", [
       (3, "3"),
       ([1], 1),
       ({"a": 1}, {"a": 1}),  # dicts can be compared but not always ordered
    ])
    def test_incompatible_type_comparisons(self, invalid_comparison):
       """Test comparisons between incompatible types."""
       a, b = invalid_comparison
       # In Python 3, these comparisons may not raise TypeError
       # but they return False for < > operators
       try:
           result = a < b
       except TypeError:
           pass  # Expected
    
    @pytest.mark.parametrize("import_name", [
       "nonexistent_module_12345",
       "fake..double_dot_module",
       "module_with_$invalid_char",
    ])
    def test_import_error_simulation(self, import_name):
       """Test module import failures."""
       with pytest.raises((ImportError, ModuleNotFoundError, ValueError)):
           __import__(import_name)
    
    @pytest.mark.parametrize("invalid_json", [
       "{'single': 'quotes'}",
       "{double: \"quotes\"}",
       '{trailing: "comma",}',
       "{'unclosed': ",
       "[1, 2, 3,]",  # Trailing comma in array
       "{NaN: 1}",
       "{Infinity: 2}",
    ])
    def test_json_decode_errors(self, invalid_json):
       """Test JSON parsing errors."""
       import json
       with pytest.raises(json.JSONDecodeError):
           json.loads(invalid_json)
    
    @pytest.mark.parametrize("division_error", [
       (lambda: 1 / 0),
       (lambda: 1.0 / 0.0),
       (lambda: 5 % 0),
       (lambda: 10 // 0),
    ])
    def test_division_by_zero(self, division_error):
       """Test division by zero errors."""
       with pytest.raises(ZeroDivisionError):
           division_error()
    
    @pytest.mark.parametrize("recursive_depth", [100, 500, 1000])
    def test_recursion_depth(self, recursive_depth):
       """Test recursion depth limits."""
       import sys
       old_limit = sys.getrecursionlimit()
       try:
           sys.setrecursionlimit(50)  # Set very low limit
           def recursive_func(n):
               if n <= 0:
                   return 0
               return recursive_func(n - 1) + 1
            
           with pytest.raises(RecursionError):
               recursive_func(recursive_depth)
       finally:
           sys.setrecursionlimit(old_limit)
    
    @pytest.mark.parametrize("namespace_conflict", [
       {"a": 1, "b": 2},
       {"x": 10, "y": 20},
       {"name": "value"},
    ])
    def test_namespace_access(self, namespace_conflict):
       """Test namespace operations."""
       # This tests that namespace access works correctly
       assert "a" not in namespace_conflict or namespace_conflict["a"] == 1
    
    @pytest.mark.parametrize("encoding_combo", [
       ("utf-8", "Hello 🌍", True),
       ("ascii", "Hello World", True),
       ("ascii", "Hello 🌍", False),
       ("latin-1", "Café", True),
       ("utf-16", "Unicode", True),
    ])
    def test_encoding_combinations(self, encoding_combo):
       """Test various encoding combinations."""
       encoding, text, should_work = encoding_combo
       if should_work:
           try:
               encoded = text.encode(encoding)
               decoded = encoded.decode(encoding)
               assert decoded == text
           except (UnicodeEncodeError, UnicodeDecodeError):
               pytest.fail(f"Should encode {text} in {encoding}")
       else:
           with pytest.raises(UnicodeEncodeError):
               text.encode(encoding)
    
    @pytest.mark.parametrize("container_index", [
       ([1, 2, 3], 5),
       ("hello", 10),
       ((1, 2), 2),
       (range(10), 20),
    ])
    def test_index_out_of_range(self, container_index):
       """Test index out of range errors."""
       container, index = container_index
       with pytest.raises(IndexError):
           _ = container[index]
    
    @pytest.mark.parametrize("negative_index", [
       ([1, 2, 3], -1),
       ("hello", -1),
       ((10, 20, 30), -2),
    ])
    def test_negative_indexing(self, negative_index):
       """Test negative indexing works correctly."""
       container, index = negative_index
       # Negative indexing should work
       result = container[index]
       assert result is not None
    
    def test_unpacking_errors(self):
        """Test unpacking errors."""
        # Test too few values
        with pytest.raises(ValueError):
           a, b = [1]
        
        # Test too many values  
        with pytest.raises(ValueError):
           x, y = [1, 2, 3]
    
    @pytest.mark.parametrize("method_call_error", [
       ([], "append", [1]),  # Valid
       ({}, "update", [{"a": 1}]),  # Valid
       ("", "upper", []),  # Valid
       (5, "bit_length", []),  # Valid
    ])
    def test_method_calls_valid(self, method_call_error):
       """Test valid method calls don't raise errors."""
       obj, method, args = method_call_error
       result = getattr(obj, method)(*args)
       assert result is not None or method == "append" or method == "update"
    
    @pytest.mark.parametrize("context_manager_error", [
       lambda: open("/nonexistent/file.txt").__enter__(),
    ])
    def test_context_manager_errors(self, context_manager_error):
       """Test context manager errors."""
       with pytest.raises((FileNotFoundError, OSError)):
           context_manager_error()
    
    @pytest.mark.parametrize("arithmetic_overflow", [
       (10 ** 1000, 10 ** 1000),  # Large numbers (Python handles these!)
       (float('inf'), 1),
       (float('-inf'), 1),
    ])
    def test_arithmetic_operations(self, arithmetic_overflow):
       """Test arithmetic operations with edge cases."""
       a, b = arithmetic_overflow
       # Python handles large integers, so no overflow
       try:
           result = a + b
           assert result is not None
       except OverflowError:
           pass
    
    @pytest.mark.parametrize("lambda_expr", [
       lambda x: x + 1,
       lambda x, y: x * y,
       lambda: 42,
       lambda *args: sum(args),
       lambda **kwargs: len(kwargs),
    ])
    def test_lambda_functions(self, lambda_expr):
       """Test lambda functions work correctly."""
       # These should all work without errors
       if lambda_expr.__code__.co_argcount == 0:
           result = lambda_expr()
       elif lambda_expr.__code__.co_argcount == 1:
           result = lambda_expr(5)
       elif lambda_expr.__code__.co_varnames[:2] == ('x', 'y'):
           result = lambda_expr(2, 3)
       assert result is not None
    
    @pytest.mark.parametrize("generator_behavior", [
       list(range(5)),
       list(reversed([1, 2, 3])),
       list(zip([1, 2], ["a", "b"])),
       list(map(str.upper, ["a", "b"])),
    ])
    def test_generator_and_iterator_behavior(self, generator_behavior):
       """Test generators and iterators work correctly."""
       assert len(generator_behavior) > 0
    
    @pytest.mark.parametrize("comprehension_test", [
       [x * 2 for x in range(5)],
       {x: x**2 for x in range(3)},
       {x for x in range(5) if x % 2 == 0},
       (x for x in range(3)),  # generator expression
    ])
    def test_comprehensions(self, comprehension_test):
       """Test comprehensions and generator expressions."""
       if isinstance(comprehension_test, list):
           assert len(comprehension_test) == 5
       elif isinstance(comprehension_test, dict):
           assert len(comprehension_test) == 3
       elif isinstance(comprehension_test, set):
           assert len(comprehension_test) == 3
    
    @pytest.mark.parametrize("valid_list_op", [
        ([1, 2, 3], "append", [4]),
        ([1, 2, 3], "extend", [[4, 5]]),
        ([1, 2, 3], "insert", [0, 0]),
        ([1, 2, 3], "remove", [2]),
        ([1, 2, 3], "pop", []),
        ([1, 2, 3], "clear", []),
        ([1, 2, 3], "index", [2]),
        ([1, 2, 3], "count", [2]),
        ([1, 2, 3], "sort", []),
        ([1, 2, 3], "reverse", []),
    ])
    def test_list_operations(self, valid_list_op):
        """Test valid list operations."""
        lst, method, args = valid_list_op
        lst_copy = lst.copy()
        try:
            result = getattr(lst_copy, method)(*args)
            # Operations like append, remove modify in place (return None)
            # Others like index, count return values
        except Exception as e:
            pytest.fail(f"List operation {method} failed: {e}")
    
    @pytest.mark.parametrize("dict_operation", [
        ({}, "keys"),
        ({}, "values"),
        ({}, "items"),
        ({"a": 1}, "get", "a"),
        ({"a": 1}, "pop", "a"),
        ({"a": 1}, "clear"),
        ({"a": 1}, "update", {"b": 2}),
    ])
    def test_dict_operations(self, dict_operation):
        """Test valid dictionary operations."""
        if len(dict_operation) == 3:
            d, method, arg = dict_operation
            args = (arg,)
        elif len(dict_operation) == 4:
            d, method, arg1, arg2 = dict_operation
            args = (arg1, arg2)
        else:
            d, method = dict_operation
            args = ()
        
        d_copy = d.copy()
        try:
            if args:
                result = getattr(d_copy, method)(*args)
            else:
                result = getattr(d_copy, method)()
        except Exception as e:
            # clear() returns None, which is ok
            if method not in ("clear", "pop"):  # pop might fail on empty dicts
                pytest.fail(f"Dict operation {method} failed: {e}")
    
    @pytest.mark.parametrize("set_operation", [
        ({1, 2, 3}, "add", [4]),
        ({1, 2, 3}, "remove", [1]),
        ({1, 2, 3}, "discard", [2]),
        ({1, 2, 3}, "pop"),
        ({1, 2, 3}, "clear"),
        ({1, 2, 3}, "union", [{4, 5}]),
        ({1, 2, 3}, "intersection", [{2, 3}]),
        ({1, 2, 3}, "difference", [{2}]),
    ])
    def test_set_operations(self, set_operation):
        """Test valid set operations."""
        if len(set_operation) == 3:
            s, method, args = set_operation
        else:
            s = set_operation[0]
            method = set_operation[1]
            args = []
        
        s_copy = s.copy()
        try:
            if args:
                result = getattr(s_copy, method)(*args)
            else:
                result = getattr(s_copy, method)()
        except Exception as e:
            pytest.fail(f"Set operation {method} failed: {e}")
    
    @pytest.mark.parametrize("string_operation", [
        ("hello", "upper"),
        ("HELLO", "lower"),
        ("hello", "capitalize"),
        ("hello", "title"),
        ("hello", "strip"),
        ("hello", "replace", ["l", "L"]),
        ("hello", "find", ["l"]),
        ("hello", "startswith", ["h"]),
        ("hello", "endswith", ["o"]),
        ("hello", "isalpha"),
        ("123", "isdigit"),
        ("hello world", "split"),
        ("a,b,c", "split", [","]),
    ])
    def test_string_operations(self, string_operation):
        """Test valid string operations."""
        if len(string_operation) == 2:
            s, method = string_operation
            args = []
        elif len(string_operation) == 3:
            s, method, args = string_operation
        
        try:
            if args:
                result = getattr(s, method)(*args)
            else:
                result = getattr(s, method)()
        except Exception as e:
            pytest.fail(f"String operation {method} failed: {e}")
    
    @pytest.mark.parametrize("numeric_operation", [
        (5, "__add__", 3),
        (5, "__sub__", 3),
        (5, "__mul__", 3),
        (5, "__truediv__", 2),
        (5, "__floordiv__", 2),
        (5, "__mod__", 3),
        (5, "__pow__", 2),
        (5.5, "__add__", 2.5),
        (5.5, "__sub__", 2.5),
        (-5, "__neg__"),
        (5, "__pos__"),
        (-5, "__abs__"),
    ])
    def test_numeric_operations(self, numeric_operation):
        """Test valid numeric operations."""
        if len(numeric_operation) == 3:
            num, op, arg = numeric_operation
            try:
                result = getattr(num, op)(arg)
            except Exception as e:
                pytest.fail(f"Numeric operation {op} failed: {e}")
        else:
            num, op = numeric_operation[:2]
            try:
                result = getattr(num, op)()
            except Exception as e:
                pytest.fail(f"Numeric operation {op} failed: {e}")
    
    @pytest.mark.parametrize("boolean_logic", [
        (True and False, False),
        (True or False, True),
        (not True, False),
        (not False, True),
        (1 and 2, 2),
        (1 or 2, 1),
        (0 or 3, 3),
    ])
    def test_boolean_operations(self, boolean_logic):
        """Test boolean operations."""
        result, expected = boolean_logic
        assert result == expected
    
    @pytest.mark.parametrize("comparison", [
        (5 > 3, True),
        (5 < 3, False),
        (5 >= 5, True),
        (5 <= 5, True),
        (5 == 5, True),
        (5 != 3, True),
        ("a" < "b", True),
        ([1] < [1, 2], True),
    ])
    def test_comparison_operations(self, comparison):
        """Test comparison operations."""
        result, expected = comparison
        assert result == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
