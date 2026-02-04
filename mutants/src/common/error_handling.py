"""
Standardized error handling utilities for _codex_ project.
"""

import logging
from functools import wraps
from typing import Any, Callable, Optional, Tuple, Type

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


def x_safe_execute__mutmut_orig(
    operation_name: str,
    exception_types: Tuple[Type[Exception], ...] = (Exception,),
    default_return: Optional[Any] = None,
    log_level: str = "warning",
):
    """
    Decorator for safe operation execution with proper error logging.

    Args:
        operation_name: Human-readable operation description
        exception_types: Tuple of exception types to catch
        default_return: Value to return on exception
        log_level: Logging level (debug, info, warning, error, critical)
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception_types as exc:
                log_method = getattr(logger, log_level)
                log_method(f"{operation_name} failed in {func.__name__}: {exc}", exc_info=True)
                return default_return

        return wrapper

    return decorator


def x_safe_execute__mutmut_1(
    operation_name: str,
    exception_types: Tuple[Type[Exception], ...] = (Exception,),
    default_return: Optional[Any] = None,
    log_level: str = "XXwarningXX",
):
    """
    Decorator for safe operation execution with proper error logging.

    Args:
        operation_name: Human-readable operation description
        exception_types: Tuple of exception types to catch
        default_return: Value to return on exception
        log_level: Logging level (debug, info, warning, error, critical)
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception_types as exc:
                log_method = getattr(logger, log_level)
                log_method(f"{operation_name} failed in {func.__name__}: {exc}", exc_info=True)
                return default_return

        return wrapper

    return decorator


def x_safe_execute__mutmut_2(
    operation_name: str,
    exception_types: Tuple[Type[Exception], ...] = (Exception,),
    default_return: Optional[Any] = None,
    log_level: str = "WARNING",
):
    """
    Decorator for safe operation execution with proper error logging.

    Args:
        operation_name: Human-readable operation description
        exception_types: Tuple of exception types to catch
        default_return: Value to return on exception
        log_level: Logging level (debug, info, warning, error, critical)
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception_types as exc:
                log_method = getattr(logger, log_level)
                log_method(f"{operation_name} failed in {func.__name__}: {exc}", exc_info=True)
                return default_return

        return wrapper

    return decorator

x_safe_execute__mutmut_mutants : ClassVar[MutantDict] = {
'x_safe_execute__mutmut_1': x_safe_execute__mutmut_1, 
    'x_safe_execute__mutmut_2': x_safe_execute__mutmut_2
}

def safe_execute(*args, **kwargs):
    result = _mutmut_trampoline(x_safe_execute__mutmut_orig, x_safe_execute__mutmut_mutants, args, kwargs)
    return result 

safe_execute.__signature__ = _mutmut_signature(x_safe_execute__mutmut_orig)
x_safe_execute__mutmut_orig.__name__ = 'x_safe_execute'


def x_safe_call__mutmut_orig(
    func: Callable,
    *args,
    operation_name: str = "Operation",
    exception_types: Tuple[Type[Exception], ...] = (Exception,),
    default_return: Optional[Any] = None,
    log_level: str = "warning",
    **kwargs,
) -> Any:
    """
    Inline function for safe operation execution with proper error logging.

    Args:
        func: Function to execute safely
        *args: Positional arguments to pass to func
        operation_name: Human-readable operation description
        exception_types: Tuple of exception types to catch
        default_return: Value to return on exception
        log_level: Logging level (debug, info, warning, error, critical)
        **kwargs: Keyword arguments to pass to func

    Returns:
        Result of func or default_return on exception

    Example:
        result = safe_call(risky_operation, arg1, arg2,
                          operation_name="risky operation",
                          default_return=[])
    """
    try:
        return func(*args, **kwargs)
    except exception_types as exc:
        log_method = getattr(logger, log_level)
        log_method(f"{operation_name} failed in {func.__name__}: {exc}", exc_info=True)
        return default_return


def x_safe_call__mutmut_1(
    func: Callable,
    *args,
    operation_name: str = "XXOperationXX",
    exception_types: Tuple[Type[Exception], ...] = (Exception,),
    default_return: Optional[Any] = None,
    log_level: str = "warning",
    **kwargs,
) -> Any:
    """
    Inline function for safe operation execution with proper error logging.

    Args:
        func: Function to execute safely
        *args: Positional arguments to pass to func
        operation_name: Human-readable operation description
        exception_types: Tuple of exception types to catch
        default_return: Value to return on exception
        log_level: Logging level (debug, info, warning, error, critical)
        **kwargs: Keyword arguments to pass to func

    Returns:
        Result of func or default_return on exception

    Example:
        result = safe_call(risky_operation, arg1, arg2,
                          operation_name="risky operation",
                          default_return=[])
    """
    try:
        return func(*args, **kwargs)
    except exception_types as exc:
        log_method = getattr(logger, log_level)
        log_method(f"{operation_name} failed in {func.__name__}: {exc}", exc_info=True)
        return default_return


def x_safe_call__mutmut_2(
    func: Callable,
    *args,
    operation_name: str = "operation",
    exception_types: Tuple[Type[Exception], ...] = (Exception,),
    default_return: Optional[Any] = None,
    log_level: str = "warning",
    **kwargs,
) -> Any:
    """
    Inline function for safe operation execution with proper error logging.

    Args:
        func: Function to execute safely
        *args: Positional arguments to pass to func
        operation_name: Human-readable operation description
        exception_types: Tuple of exception types to catch
        default_return: Value to return on exception
        log_level: Logging level (debug, info, warning, error, critical)
        **kwargs: Keyword arguments to pass to func

    Returns:
        Result of func or default_return on exception

    Example:
        result = safe_call(risky_operation, arg1, arg2,
                          operation_name="risky operation",
                          default_return=[])
    """
    try:
        return func(*args, **kwargs)
    except exception_types as exc:
        log_method = getattr(logger, log_level)
        log_method(f"{operation_name} failed in {func.__name__}: {exc}", exc_info=True)
        return default_return


def x_safe_call__mutmut_3(
    func: Callable,
    *args,
    operation_name: str = "OPERATION",
    exception_types: Tuple[Type[Exception], ...] = (Exception,),
    default_return: Optional[Any] = None,
    log_level: str = "warning",
    **kwargs,
) -> Any:
    """
    Inline function for safe operation execution with proper error logging.

    Args:
        func: Function to execute safely
        *args: Positional arguments to pass to func
        operation_name: Human-readable operation description
        exception_types: Tuple of exception types to catch
        default_return: Value to return on exception
        log_level: Logging level (debug, info, warning, error, critical)
        **kwargs: Keyword arguments to pass to func

    Returns:
        Result of func or default_return on exception

    Example:
        result = safe_call(risky_operation, arg1, arg2,
                          operation_name="risky operation",
                          default_return=[])
    """
    try:
        return func(*args, **kwargs)
    except exception_types as exc:
        log_method = getattr(logger, log_level)
        log_method(f"{operation_name} failed in {func.__name__}: {exc}", exc_info=True)
        return default_return


def x_safe_call__mutmut_4(
    func: Callable,
    *args,
    operation_name: str = "Operation",
    exception_types: Tuple[Type[Exception], ...] = (Exception,),
    default_return: Optional[Any] = None,
    log_level: str = "XXwarningXX",
    **kwargs,
) -> Any:
    """
    Inline function for safe operation execution with proper error logging.

    Args:
        func: Function to execute safely
        *args: Positional arguments to pass to func
        operation_name: Human-readable operation description
        exception_types: Tuple of exception types to catch
        default_return: Value to return on exception
        log_level: Logging level (debug, info, warning, error, critical)
        **kwargs: Keyword arguments to pass to func

    Returns:
        Result of func or default_return on exception

    Example:
        result = safe_call(risky_operation, arg1, arg2,
                          operation_name="risky operation",
                          default_return=[])
    """
    try:
        return func(*args, **kwargs)
    except exception_types as exc:
        log_method = getattr(logger, log_level)
        log_method(f"{operation_name} failed in {func.__name__}: {exc}", exc_info=True)
        return default_return


def x_safe_call__mutmut_5(
    func: Callable,
    *args,
    operation_name: str = "Operation",
    exception_types: Tuple[Type[Exception], ...] = (Exception,),
    default_return: Optional[Any] = None,
    log_level: str = "WARNING",
    **kwargs,
) -> Any:
    """
    Inline function for safe operation execution with proper error logging.

    Args:
        func: Function to execute safely
        *args: Positional arguments to pass to func
        operation_name: Human-readable operation description
        exception_types: Tuple of exception types to catch
        default_return: Value to return on exception
        log_level: Logging level (debug, info, warning, error, critical)
        **kwargs: Keyword arguments to pass to func

    Returns:
        Result of func or default_return on exception

    Example:
        result = safe_call(risky_operation, arg1, arg2,
                          operation_name="risky operation",
                          default_return=[])
    """
    try:
        return func(*args, **kwargs)
    except exception_types as exc:
        log_method = getattr(logger, log_level)
        log_method(f"{operation_name} failed in {func.__name__}: {exc}", exc_info=True)
        return default_return


def x_safe_call__mutmut_6(
    func: Callable,
    *args,
    operation_name: str = "Operation",
    exception_types: Tuple[Type[Exception], ...] = (Exception,),
    default_return: Optional[Any] = None,
    log_level: str = "warning",
    **kwargs,
) -> Any:
    """
    Inline function for safe operation execution with proper error logging.

    Args:
        func: Function to execute safely
        *args: Positional arguments to pass to func
        operation_name: Human-readable operation description
        exception_types: Tuple of exception types to catch
        default_return: Value to return on exception
        log_level: Logging level (debug, info, warning, error, critical)
        **kwargs: Keyword arguments to pass to func

    Returns:
        Result of func or default_return on exception

    Example:
        result = safe_call(risky_operation, arg1, arg2,
                          operation_name="risky operation",
                          default_return=[])
    """
    try:
        return func(**kwargs)
    except exception_types as exc:
        log_method = getattr(logger, log_level)
        log_method(f"{operation_name} failed in {func.__name__}: {exc}", exc_info=True)
        return default_return


def x_safe_call__mutmut_7(
    func: Callable,
    *args,
    operation_name: str = "Operation",
    exception_types: Tuple[Type[Exception], ...] = (Exception,),
    default_return: Optional[Any] = None,
    log_level: str = "warning",
    **kwargs,
) -> Any:
    """
    Inline function for safe operation execution with proper error logging.

    Args:
        func: Function to execute safely
        *args: Positional arguments to pass to func
        operation_name: Human-readable operation description
        exception_types: Tuple of exception types to catch
        default_return: Value to return on exception
        log_level: Logging level (debug, info, warning, error, critical)
        **kwargs: Keyword arguments to pass to func

    Returns:
        Result of func or default_return on exception

    Example:
        result = safe_call(risky_operation, arg1, arg2,
                          operation_name="risky operation",
                          default_return=[])
    """
    try:
        return func(*args, )
    except exception_types as exc:
        log_method = getattr(logger, log_level)
        log_method(f"{operation_name} failed in {func.__name__}: {exc}", exc_info=True)
        return default_return


def x_safe_call__mutmut_8(
    func: Callable,
    *args,
    operation_name: str = "Operation",
    exception_types: Tuple[Type[Exception], ...] = (Exception,),
    default_return: Optional[Any] = None,
    log_level: str = "warning",
    **kwargs,
) -> Any:
    """
    Inline function for safe operation execution with proper error logging.

    Args:
        func: Function to execute safely
        *args: Positional arguments to pass to func
        operation_name: Human-readable operation description
        exception_types: Tuple of exception types to catch
        default_return: Value to return on exception
        log_level: Logging level (debug, info, warning, error, critical)
        **kwargs: Keyword arguments to pass to func

    Returns:
        Result of func or default_return on exception

    Example:
        result = safe_call(risky_operation, arg1, arg2,
                          operation_name="risky operation",
                          default_return=[])
    """
    try:
        return func(*args, **kwargs)
    except exception_types as exc:
        log_method = None
        log_method(f"{operation_name} failed in {func.__name__}: {exc}", exc_info=True)
        return default_return


def x_safe_call__mutmut_9(
    func: Callable,
    *args,
    operation_name: str = "Operation",
    exception_types: Tuple[Type[Exception], ...] = (Exception,),
    default_return: Optional[Any] = None,
    log_level: str = "warning",
    **kwargs,
) -> Any:
    """
    Inline function for safe operation execution with proper error logging.

    Args:
        func: Function to execute safely
        *args: Positional arguments to pass to func
        operation_name: Human-readable operation description
        exception_types: Tuple of exception types to catch
        default_return: Value to return on exception
        log_level: Logging level (debug, info, warning, error, critical)
        **kwargs: Keyword arguments to pass to func

    Returns:
        Result of func or default_return on exception

    Example:
        result = safe_call(risky_operation, arg1, arg2,
                          operation_name="risky operation",
                          default_return=[])
    """
    try:
        return func(*args, **kwargs)
    except exception_types as exc:
        log_method = getattr(None, log_level)
        log_method(f"{operation_name} failed in {func.__name__}: {exc}", exc_info=True)
        return default_return


def x_safe_call__mutmut_10(
    func: Callable,
    *args,
    operation_name: str = "Operation",
    exception_types: Tuple[Type[Exception], ...] = (Exception,),
    default_return: Optional[Any] = None,
    log_level: str = "warning",
    **kwargs,
) -> Any:
    """
    Inline function for safe operation execution with proper error logging.

    Args:
        func: Function to execute safely
        *args: Positional arguments to pass to func
        operation_name: Human-readable operation description
        exception_types: Tuple of exception types to catch
        default_return: Value to return on exception
        log_level: Logging level (debug, info, warning, error, critical)
        **kwargs: Keyword arguments to pass to func

    Returns:
        Result of func or default_return on exception

    Example:
        result = safe_call(risky_operation, arg1, arg2,
                          operation_name="risky operation",
                          default_return=[])
    """
    try:
        return func(*args, **kwargs)
    except exception_types as exc:
        log_method = getattr(logger, None)
        log_method(f"{operation_name} failed in {func.__name__}: {exc}", exc_info=True)
        return default_return


def x_safe_call__mutmut_11(
    func: Callable,
    *args,
    operation_name: str = "Operation",
    exception_types: Tuple[Type[Exception], ...] = (Exception,),
    default_return: Optional[Any] = None,
    log_level: str = "warning",
    **kwargs,
) -> Any:
    """
    Inline function for safe operation execution with proper error logging.

    Args:
        func: Function to execute safely
        *args: Positional arguments to pass to func
        operation_name: Human-readable operation description
        exception_types: Tuple of exception types to catch
        default_return: Value to return on exception
        log_level: Logging level (debug, info, warning, error, critical)
        **kwargs: Keyword arguments to pass to func

    Returns:
        Result of func or default_return on exception

    Example:
        result = safe_call(risky_operation, arg1, arg2,
                          operation_name="risky operation",
                          default_return=[])
    """
    try:
        return func(*args, **kwargs)
    except exception_types as exc:
        log_method = getattr(log_level)
        log_method(f"{operation_name} failed in {func.__name__}: {exc}", exc_info=True)
        return default_return


def x_safe_call__mutmut_12(
    func: Callable,
    *args,
    operation_name: str = "Operation",
    exception_types: Tuple[Type[Exception], ...] = (Exception,),
    default_return: Optional[Any] = None,
    log_level: str = "warning",
    **kwargs,
) -> Any:
    """
    Inline function for safe operation execution with proper error logging.

    Args:
        func: Function to execute safely
        *args: Positional arguments to pass to func
        operation_name: Human-readable operation description
        exception_types: Tuple of exception types to catch
        default_return: Value to return on exception
        log_level: Logging level (debug, info, warning, error, critical)
        **kwargs: Keyword arguments to pass to func

    Returns:
        Result of func or default_return on exception

    Example:
        result = safe_call(risky_operation, arg1, arg2,
                          operation_name="risky operation",
                          default_return=[])
    """
    try:
        return func(*args, **kwargs)
    except exception_types as exc:
        log_method = getattr(logger, )
        log_method(f"{operation_name} failed in {func.__name__}: {exc}", exc_info=True)
        return default_return


def x_safe_call__mutmut_13(
    func: Callable,
    *args,
    operation_name: str = "Operation",
    exception_types: Tuple[Type[Exception], ...] = (Exception,),
    default_return: Optional[Any] = None,
    log_level: str = "warning",
    **kwargs,
) -> Any:
    """
    Inline function for safe operation execution with proper error logging.

    Args:
        func: Function to execute safely
        *args: Positional arguments to pass to func
        operation_name: Human-readable operation description
        exception_types: Tuple of exception types to catch
        default_return: Value to return on exception
        log_level: Logging level (debug, info, warning, error, critical)
        **kwargs: Keyword arguments to pass to func

    Returns:
        Result of func or default_return on exception

    Example:
        result = safe_call(risky_operation, arg1, arg2,
                          operation_name="risky operation",
                          default_return=[])
    """
    try:
        return func(*args, **kwargs)
    except exception_types as exc:
        log_method = getattr(logger, log_level)
        log_method(None, exc_info=True)
        return default_return


def x_safe_call__mutmut_14(
    func: Callable,
    *args,
    operation_name: str = "Operation",
    exception_types: Tuple[Type[Exception], ...] = (Exception,),
    default_return: Optional[Any] = None,
    log_level: str = "warning",
    **kwargs,
) -> Any:
    """
    Inline function for safe operation execution with proper error logging.

    Args:
        func: Function to execute safely
        *args: Positional arguments to pass to func
        operation_name: Human-readable operation description
        exception_types: Tuple of exception types to catch
        default_return: Value to return on exception
        log_level: Logging level (debug, info, warning, error, critical)
        **kwargs: Keyword arguments to pass to func

    Returns:
        Result of func or default_return on exception

    Example:
        result = safe_call(risky_operation, arg1, arg2,
                          operation_name="risky operation",
                          default_return=[])
    """
    try:
        return func(*args, **kwargs)
    except exception_types as exc:
        log_method = getattr(logger, log_level)
        log_method(f"{operation_name} failed in {func.__name__}: {exc}", exc_info=None)
        return default_return


def x_safe_call__mutmut_15(
    func: Callable,
    *args,
    operation_name: str = "Operation",
    exception_types: Tuple[Type[Exception], ...] = (Exception,),
    default_return: Optional[Any] = None,
    log_level: str = "warning",
    **kwargs,
) -> Any:
    """
    Inline function for safe operation execution with proper error logging.

    Args:
        func: Function to execute safely
        *args: Positional arguments to pass to func
        operation_name: Human-readable operation description
        exception_types: Tuple of exception types to catch
        default_return: Value to return on exception
        log_level: Logging level (debug, info, warning, error, critical)
        **kwargs: Keyword arguments to pass to func

    Returns:
        Result of func or default_return on exception

    Example:
        result = safe_call(risky_operation, arg1, arg2,
                          operation_name="risky operation",
                          default_return=[])
    """
    try:
        return func(*args, **kwargs)
    except exception_types as exc:
        log_method = getattr(logger, log_level)
        log_method(exc_info=True)
        return default_return


def x_safe_call__mutmut_16(
    func: Callable,
    *args,
    operation_name: str = "Operation",
    exception_types: Tuple[Type[Exception], ...] = (Exception,),
    default_return: Optional[Any] = None,
    log_level: str = "warning",
    **kwargs,
) -> Any:
    """
    Inline function for safe operation execution with proper error logging.

    Args:
        func: Function to execute safely
        *args: Positional arguments to pass to func
        operation_name: Human-readable operation description
        exception_types: Tuple of exception types to catch
        default_return: Value to return on exception
        log_level: Logging level (debug, info, warning, error, critical)
        **kwargs: Keyword arguments to pass to func

    Returns:
        Result of func or default_return on exception

    Example:
        result = safe_call(risky_operation, arg1, arg2,
                          operation_name="risky operation",
                          default_return=[])
    """
    try:
        return func(*args, **kwargs)
    except exception_types as exc:
        log_method = getattr(logger, log_level)
        log_method(f"{operation_name} failed in {func.__name__}: {exc}", )
        return default_return


def x_safe_call__mutmut_17(
    func: Callable,
    *args,
    operation_name: str = "Operation",
    exception_types: Tuple[Type[Exception], ...] = (Exception,),
    default_return: Optional[Any] = None,
    log_level: str = "warning",
    **kwargs,
) -> Any:
    """
    Inline function for safe operation execution with proper error logging.

    Args:
        func: Function to execute safely
        *args: Positional arguments to pass to func
        operation_name: Human-readable operation description
        exception_types: Tuple of exception types to catch
        default_return: Value to return on exception
        log_level: Logging level (debug, info, warning, error, critical)
        **kwargs: Keyword arguments to pass to func

    Returns:
        Result of func or default_return on exception

    Example:
        result = safe_call(risky_operation, arg1, arg2,
                          operation_name="risky operation",
                          default_return=[])
    """
    try:
        return func(*args, **kwargs)
    except exception_types as exc:
        log_method = getattr(logger, log_level)
        log_method(f"{operation_name} failed in {func.__name__}: {exc}", exc_info=False)
        return default_return

x_safe_call__mutmut_mutants : ClassVar[MutantDict] = {
'x_safe_call__mutmut_1': x_safe_call__mutmut_1, 
    'x_safe_call__mutmut_2': x_safe_call__mutmut_2, 
    'x_safe_call__mutmut_3': x_safe_call__mutmut_3, 
    'x_safe_call__mutmut_4': x_safe_call__mutmut_4, 
    'x_safe_call__mutmut_5': x_safe_call__mutmut_5, 
    'x_safe_call__mutmut_6': x_safe_call__mutmut_6, 
    'x_safe_call__mutmut_7': x_safe_call__mutmut_7, 
    'x_safe_call__mutmut_8': x_safe_call__mutmut_8, 
    'x_safe_call__mutmut_9': x_safe_call__mutmut_9, 
    'x_safe_call__mutmut_10': x_safe_call__mutmut_10, 
    'x_safe_call__mutmut_11': x_safe_call__mutmut_11, 
    'x_safe_call__mutmut_12': x_safe_call__mutmut_12, 
    'x_safe_call__mutmut_13': x_safe_call__mutmut_13, 
    'x_safe_call__mutmut_14': x_safe_call__mutmut_14, 
    'x_safe_call__mutmut_15': x_safe_call__mutmut_15, 
    'x_safe_call__mutmut_16': x_safe_call__mutmut_16, 
    'x_safe_call__mutmut_17': x_safe_call__mutmut_17
}

def safe_call(*args, **kwargs):
    result = _mutmut_trampoline(x_safe_call__mutmut_orig, x_safe_call__mutmut_mutants, args, kwargs)
    return result 

safe_call.__signature__ = _mutmut_signature(x_safe_call__mutmut_orig)
x_safe_call__mutmut_orig.__name__ = 'x_safe_call'
