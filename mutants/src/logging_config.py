"""
Logging Config Module

This module provides functionality for logging config.

Usage:
    from src.logging_config import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

import logging
from logging.handlers import RotatingFileHandler
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


def x_configure_logging__mutmut_orig(
    level: int = logging.INFO,
    to_file: str | None = None,
    max_bytes: int = 5_000_000,
    backup_count: int = 3,
):
    logger = logging.getLogger()
    logger.setLevel(level)
    if to_file:
        fh = RotatingFileHandler(to_file, maxBytes=max_bytes, backupCount=backup_count)
        logger.addHandler(fh)
    ch = logging.StreamHandler()
    logger.addHandler(ch)
    return logger


def x_configure_logging__mutmut_1(
    level: int = logging.INFO,
    to_file: str | None = None,
    max_bytes: int = 5000001,
    backup_count: int = 3,
):
    logger = logging.getLogger()
    logger.setLevel(level)
    if to_file:
        fh = RotatingFileHandler(to_file, maxBytes=max_bytes, backupCount=backup_count)
        logger.addHandler(fh)
    ch = logging.StreamHandler()
    logger.addHandler(ch)
    return logger


def x_configure_logging__mutmut_2(
    level: int = logging.INFO,
    to_file: str | None = None,
    max_bytes: int = 5_000_000,
    backup_count: int = 4,
):
    logger = logging.getLogger()
    logger.setLevel(level)
    if to_file:
        fh = RotatingFileHandler(to_file, maxBytes=max_bytes, backupCount=backup_count)
        logger.addHandler(fh)
    ch = logging.StreamHandler()
    logger.addHandler(ch)
    return logger


def x_configure_logging__mutmut_3(
    level: int = logging.INFO,
    to_file: str | None = None,
    max_bytes: int = 5_000_000,
    backup_count: int = 3,
):
    logger = None
    logger.setLevel(level)
    if to_file:
        fh = RotatingFileHandler(to_file, maxBytes=max_bytes, backupCount=backup_count)
        logger.addHandler(fh)
    ch = logging.StreamHandler()
    logger.addHandler(ch)
    return logger


def x_configure_logging__mutmut_4(
    level: int = logging.INFO,
    to_file: str | None = None,
    max_bytes: int = 5_000_000,
    backup_count: int = 3,
):
    logger = logging.getLogger()
    logger.setLevel(None)
    if to_file:
        fh = RotatingFileHandler(to_file, maxBytes=max_bytes, backupCount=backup_count)
        logger.addHandler(fh)
    ch = logging.StreamHandler()
    logger.addHandler(ch)
    return logger


def x_configure_logging__mutmut_5(
    level: int = logging.INFO,
    to_file: str | None = None,
    max_bytes: int = 5_000_000,
    backup_count: int = 3,
):
    logger = logging.getLogger()
    logger.setLevel(level)
    if to_file:
        fh = None
        logger.addHandler(fh)
    ch = logging.StreamHandler()
    logger.addHandler(ch)
    return logger


def x_configure_logging__mutmut_6(
    level: int = logging.INFO,
    to_file: str | None = None,
    max_bytes: int = 5_000_000,
    backup_count: int = 3,
):
    logger = logging.getLogger()
    logger.setLevel(level)
    if to_file:
        fh = RotatingFileHandler(None, maxBytes=max_bytes, backupCount=backup_count)
        logger.addHandler(fh)
    ch = logging.StreamHandler()
    logger.addHandler(ch)
    return logger


def x_configure_logging__mutmut_7(
    level: int = logging.INFO,
    to_file: str | None = None,
    max_bytes: int = 5_000_000,
    backup_count: int = 3,
):
    logger = logging.getLogger()
    logger.setLevel(level)
    if to_file:
        fh = RotatingFileHandler(to_file, maxBytes=None, backupCount=backup_count)
        logger.addHandler(fh)
    ch = logging.StreamHandler()
    logger.addHandler(ch)
    return logger


def x_configure_logging__mutmut_8(
    level: int = logging.INFO,
    to_file: str | None = None,
    max_bytes: int = 5_000_000,
    backup_count: int = 3,
):
    logger = logging.getLogger()
    logger.setLevel(level)
    if to_file:
        fh = RotatingFileHandler(to_file, maxBytes=max_bytes, backupCount=None)
        logger.addHandler(fh)
    ch = logging.StreamHandler()
    logger.addHandler(ch)
    return logger


def x_configure_logging__mutmut_9(
    level: int = logging.INFO,
    to_file: str | None = None,
    max_bytes: int = 5_000_000,
    backup_count: int = 3,
):
    logger = logging.getLogger()
    logger.setLevel(level)
    if to_file:
        fh = RotatingFileHandler(maxBytes=max_bytes, backupCount=backup_count)
        logger.addHandler(fh)
    ch = logging.StreamHandler()
    logger.addHandler(ch)
    return logger


def x_configure_logging__mutmut_10(
    level: int = logging.INFO,
    to_file: str | None = None,
    max_bytes: int = 5_000_000,
    backup_count: int = 3,
):
    logger = logging.getLogger()
    logger.setLevel(level)
    if to_file:
        fh = RotatingFileHandler(to_file, backupCount=backup_count)
        logger.addHandler(fh)
    ch = logging.StreamHandler()
    logger.addHandler(ch)
    return logger


def x_configure_logging__mutmut_11(
    level: int = logging.INFO,
    to_file: str | None = None,
    max_bytes: int = 5_000_000,
    backup_count: int = 3,
):
    logger = logging.getLogger()
    logger.setLevel(level)
    if to_file:
        fh = RotatingFileHandler(to_file, maxBytes=max_bytes, )
        logger.addHandler(fh)
    ch = logging.StreamHandler()
    logger.addHandler(ch)
    return logger


def x_configure_logging__mutmut_12(
    level: int = logging.INFO,
    to_file: str | None = None,
    max_bytes: int = 5_000_000,
    backup_count: int = 3,
):
    logger = logging.getLogger()
    logger.setLevel(level)
    if to_file:
        fh = RotatingFileHandler(to_file, maxBytes=max_bytes, backupCount=backup_count)
        logger.addHandler(None)
    ch = logging.StreamHandler()
    logger.addHandler(ch)
    return logger


def x_configure_logging__mutmut_13(
    level: int = logging.INFO,
    to_file: str | None = None,
    max_bytes: int = 5_000_000,
    backup_count: int = 3,
):
    logger = logging.getLogger()
    logger.setLevel(level)
    if to_file:
        fh = RotatingFileHandler(to_file, maxBytes=max_bytes, backupCount=backup_count)
        logger.addHandler(fh)
    ch = None
    logger.addHandler(ch)
    return logger


def x_configure_logging__mutmut_14(
    level: int = logging.INFO,
    to_file: str | None = None,
    max_bytes: int = 5_000_000,
    backup_count: int = 3,
):
    logger = logging.getLogger()
    logger.setLevel(level)
    if to_file:
        fh = RotatingFileHandler(to_file, maxBytes=max_bytes, backupCount=backup_count)
        logger.addHandler(fh)
    ch = logging.StreamHandler()
    logger.addHandler(None)
    return logger

x_configure_logging__mutmut_mutants : ClassVar[MutantDict] = {
'x_configure_logging__mutmut_1': x_configure_logging__mutmut_1, 
    'x_configure_logging__mutmut_2': x_configure_logging__mutmut_2, 
    'x_configure_logging__mutmut_3': x_configure_logging__mutmut_3, 
    'x_configure_logging__mutmut_4': x_configure_logging__mutmut_4, 
    'x_configure_logging__mutmut_5': x_configure_logging__mutmut_5, 
    'x_configure_logging__mutmut_6': x_configure_logging__mutmut_6, 
    'x_configure_logging__mutmut_7': x_configure_logging__mutmut_7, 
    'x_configure_logging__mutmut_8': x_configure_logging__mutmut_8, 
    'x_configure_logging__mutmut_9': x_configure_logging__mutmut_9, 
    'x_configure_logging__mutmut_10': x_configure_logging__mutmut_10, 
    'x_configure_logging__mutmut_11': x_configure_logging__mutmut_11, 
    'x_configure_logging__mutmut_12': x_configure_logging__mutmut_12, 
    'x_configure_logging__mutmut_13': x_configure_logging__mutmut_13, 
    'x_configure_logging__mutmut_14': x_configure_logging__mutmut_14
}

def configure_logging(*args, **kwargs):
    result = _mutmut_trampoline(x_configure_logging__mutmut_orig, x_configure_logging__mutmut_mutants, args, kwargs)
    return result 

configure_logging.__signature__ = _mutmut_signature(x_configure_logging__mutmut_orig)
x_configure_logging__mutmut_orig.__name__ = 'x_configure_logging'
