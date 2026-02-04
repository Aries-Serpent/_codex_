"""
Codeowners Validate Module

This module provides functionality for codeowners validate.

Usage:
    from tools.codeowners_validate import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

OWNER_RX = re.compile(r"^@([A-Za-z0-9_.-]+)(/[A-Za-z0-9_.-]+)?$")
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
class CodeownersRule:
    pattern: str
    owners: list[str]
    line_no: int


@dataclass
class CodeownersReport:
    exists: bool
    default_rule: bool
    owners_ok: bool
    coverage: dict[str, bool]
    errors: list[str]
    warnings: list[str]
    rules: list[dict[str, Any]]


def x_parse_codeowners__mutmut_orig(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[0], owners=[], line_no=i))
            continue
        pat, owners = parts[0], parts[1:]
        rules.append(CodeownersRule(pattern=pat, owners=owners, line_no=i))
    return rules


def x_parse_codeowners__mutmut_1(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = None
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[0], owners=[], line_no=i))
            continue
        pat, owners = parts[0], parts[1:]
        rules.append(CodeownersRule(pattern=pat, owners=owners, line_no=i))
    return rules


def x_parse_codeowners__mutmut_2(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(None, start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[0], owners=[], line_no=i))
            continue
        pat, owners = parts[0], parts[1:]
        rules.append(CodeownersRule(pattern=pat, owners=owners, line_no=i))
    return rules


def x_parse_codeowners__mutmut_3(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), start=None):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[0], owners=[], line_no=i))
            continue
        pat, owners = parts[0], parts[1:]
        rules.append(CodeownersRule(pattern=pat, owners=owners, line_no=i))
    return rules


def x_parse_codeowners__mutmut_4(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[0], owners=[], line_no=i))
            continue
        pat, owners = parts[0], parts[1:]
        rules.append(CodeownersRule(pattern=pat, owners=owners, line_no=i))
    return rules


def x_parse_codeowners__mutmut_5(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), ):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[0], owners=[], line_no=i))
            continue
        pat, owners = parts[0], parts[1:]
        rules.append(CodeownersRule(pattern=pat, owners=owners, line_no=i))
    return rules


def x_parse_codeowners__mutmut_6(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), start=2):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[0], owners=[], line_no=i))
            continue
        pat, owners = parts[0], parts[1:]
        rules.append(CodeownersRule(pattern=pat, owners=owners, line_no=i))
    return rules


def x_parse_codeowners__mutmut_7(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), start=1):
        line = None
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[0], owners=[], line_no=i))
            continue
        pat, owners = parts[0], parts[1:]
        rules.append(CodeownersRule(pattern=pat, owners=owners, line_no=i))
    return rules


def x_parse_codeowners__mutmut_8(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line and line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[0], owners=[], line_no=i))
            continue
        pat, owners = parts[0], parts[1:]
        rules.append(CodeownersRule(pattern=pat, owners=owners, line_no=i))
    return rules


def x_parse_codeowners__mutmut_9(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[0], owners=[], line_no=i))
            continue
        pat, owners = parts[0], parts[1:]
        rules.append(CodeownersRule(pattern=pat, owners=owners, line_no=i))
    return rules


def x_parse_codeowners__mutmut_10(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith(None):
            continue
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[0], owners=[], line_no=i))
            continue
        pat, owners = parts[0], parts[1:]
        rules.append(CodeownersRule(pattern=pat, owners=owners, line_no=i))
    return rules


def x_parse_codeowners__mutmut_11(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("XX#XX"):
            continue
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[0], owners=[], line_no=i))
            continue
        pat, owners = parts[0], parts[1:]
        rules.append(CodeownersRule(pattern=pat, owners=owners, line_no=i))
    return rules


def x_parse_codeowners__mutmut_12(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            break
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[0], owners=[], line_no=i))
            continue
        pat, owners = parts[0], parts[1:]
        rules.append(CodeownersRule(pattern=pat, owners=owners, line_no=i))
    return rules


def x_parse_codeowners__mutmut_13(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = None
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[0], owners=[], line_no=i))
            continue
        pat, owners = parts[0], parts[1:]
        rules.append(CodeownersRule(pattern=pat, owners=owners, line_no=i))
    return rules


def x_parse_codeowners__mutmut_14(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) <= 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[0], owners=[], line_no=i))
            continue
        pat, owners = parts[0], parts[1:]
        rules.append(CodeownersRule(pattern=pat, owners=owners, line_no=i))
    return rules


def x_parse_codeowners__mutmut_15(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 3:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[0], owners=[], line_no=i))
            continue
        pat, owners = parts[0], parts[1:]
        rules.append(CodeownersRule(pattern=pat, owners=owners, line_no=i))
    return rules


def x_parse_codeowners__mutmut_16(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(None)
            continue
        pat, owners = parts[0], parts[1:]
        rules.append(CodeownersRule(pattern=pat, owners=owners, line_no=i))
    return rules


def x_parse_codeowners__mutmut_17(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=None, owners=[], line_no=i))
            continue
        pat, owners = parts[0], parts[1:]
        rules.append(CodeownersRule(pattern=pat, owners=owners, line_no=i))
    return rules


def x_parse_codeowners__mutmut_18(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[0], owners=None, line_no=i))
            continue
        pat, owners = parts[0], parts[1:]
        rules.append(CodeownersRule(pattern=pat, owners=owners, line_no=i))
    return rules


def x_parse_codeowners__mutmut_19(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[0], owners=[], line_no=None))
            continue
        pat, owners = parts[0], parts[1:]
        rules.append(CodeownersRule(pattern=pat, owners=owners, line_no=i))
    return rules


def x_parse_codeowners__mutmut_20(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(owners=[], line_no=i))
            continue
        pat, owners = parts[0], parts[1:]
        rules.append(CodeownersRule(pattern=pat, owners=owners, line_no=i))
    return rules


def x_parse_codeowners__mutmut_21(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[0], line_no=i))
            continue
        pat, owners = parts[0], parts[1:]
        rules.append(CodeownersRule(pattern=pat, owners=owners, line_no=i))
    return rules


def x_parse_codeowners__mutmut_22(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[0], owners=[], ))
            continue
        pat, owners = parts[0], parts[1:]
        rules.append(CodeownersRule(pattern=pat, owners=owners, line_no=i))
    return rules


def x_parse_codeowners__mutmut_23(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[1], owners=[], line_no=i))
            continue
        pat, owners = parts[0], parts[1:]
        rules.append(CodeownersRule(pattern=pat, owners=owners, line_no=i))
    return rules


def x_parse_codeowners__mutmut_24(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[0], owners=[], line_no=i))
            break
        pat, owners = parts[0], parts[1:]
        rules.append(CodeownersRule(pattern=pat, owners=owners, line_no=i))
    return rules


def x_parse_codeowners__mutmut_25(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[0], owners=[], line_no=i))
            continue
        pat, owners = None
        rules.append(CodeownersRule(pattern=pat, owners=owners, line_no=i))
    return rules


def x_parse_codeowners__mutmut_26(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[0], owners=[], line_no=i))
            continue
        pat, owners = parts[1], parts[1:]
        rules.append(CodeownersRule(pattern=pat, owners=owners, line_no=i))
    return rules


def x_parse_codeowners__mutmut_27(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[0], owners=[], line_no=i))
            continue
        pat, owners = parts[0], parts[2:]
        rules.append(CodeownersRule(pattern=pat, owners=owners, line_no=i))
    return rules


def x_parse_codeowners__mutmut_28(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[0], owners=[], line_no=i))
            continue
        pat, owners = parts[0], parts[1:]
        rules.append(None)
    return rules


def x_parse_codeowners__mutmut_29(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[0], owners=[], line_no=i))
            continue
        pat, owners = parts[0], parts[1:]
        rules.append(CodeownersRule(pattern=None, owners=owners, line_no=i))
    return rules


def x_parse_codeowners__mutmut_30(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[0], owners=[], line_no=i))
            continue
        pat, owners = parts[0], parts[1:]
        rules.append(CodeownersRule(pattern=pat, owners=None, line_no=i))
    return rules


def x_parse_codeowners__mutmut_31(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[0], owners=[], line_no=i))
            continue
        pat, owners = parts[0], parts[1:]
        rules.append(CodeownersRule(pattern=pat, owners=owners, line_no=None))
    return rules


def x_parse_codeowners__mutmut_32(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[0], owners=[], line_no=i))
            continue
        pat, owners = parts[0], parts[1:]
        rules.append(CodeownersRule(owners=owners, line_no=i))
    return rules


def x_parse_codeowners__mutmut_33(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[0], owners=[], line_no=i))
            continue
        pat, owners = parts[0], parts[1:]
        rules.append(CodeownersRule(pattern=pat, line_no=i))
    return rules


def x_parse_codeowners__mutmut_34(text: str) -> list[CodeownersRule]:
    rules: list[CodeownersRule] = []
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            # pattern without owners: skip but record warning upstream
            rules.append(CodeownersRule(pattern=parts[0], owners=[], line_no=i))
            continue
        pat, owners = parts[0], parts[1:]
        rules.append(CodeownersRule(pattern=pat, owners=owners, ))
    return rules

x_parse_codeowners__mutmut_mutants : ClassVar[MutantDict] = {
'x_parse_codeowners__mutmut_1': x_parse_codeowners__mutmut_1, 
    'x_parse_codeowners__mutmut_2': x_parse_codeowners__mutmut_2, 
    'x_parse_codeowners__mutmut_3': x_parse_codeowners__mutmut_3, 
    'x_parse_codeowners__mutmut_4': x_parse_codeowners__mutmut_4, 
    'x_parse_codeowners__mutmut_5': x_parse_codeowners__mutmut_5, 
    'x_parse_codeowners__mutmut_6': x_parse_codeowners__mutmut_6, 
    'x_parse_codeowners__mutmut_7': x_parse_codeowners__mutmut_7, 
    'x_parse_codeowners__mutmut_8': x_parse_codeowners__mutmut_8, 
    'x_parse_codeowners__mutmut_9': x_parse_codeowners__mutmut_9, 
    'x_parse_codeowners__mutmut_10': x_parse_codeowners__mutmut_10, 
    'x_parse_codeowners__mutmut_11': x_parse_codeowners__mutmut_11, 
    'x_parse_codeowners__mutmut_12': x_parse_codeowners__mutmut_12, 
    'x_parse_codeowners__mutmut_13': x_parse_codeowners__mutmut_13, 
    'x_parse_codeowners__mutmut_14': x_parse_codeowners__mutmut_14, 
    'x_parse_codeowners__mutmut_15': x_parse_codeowners__mutmut_15, 
    'x_parse_codeowners__mutmut_16': x_parse_codeowners__mutmut_16, 
    'x_parse_codeowners__mutmut_17': x_parse_codeowners__mutmut_17, 
    'x_parse_codeowners__mutmut_18': x_parse_codeowners__mutmut_18, 
    'x_parse_codeowners__mutmut_19': x_parse_codeowners__mutmut_19, 
    'x_parse_codeowners__mutmut_20': x_parse_codeowners__mutmut_20, 
    'x_parse_codeowners__mutmut_21': x_parse_codeowners__mutmut_21, 
    'x_parse_codeowners__mutmut_22': x_parse_codeowners__mutmut_22, 
    'x_parse_codeowners__mutmut_23': x_parse_codeowners__mutmut_23, 
    'x_parse_codeowners__mutmut_24': x_parse_codeowners__mutmut_24, 
    'x_parse_codeowners__mutmut_25': x_parse_codeowners__mutmut_25, 
    'x_parse_codeowners__mutmut_26': x_parse_codeowners__mutmut_26, 
    'x_parse_codeowners__mutmut_27': x_parse_codeowners__mutmut_27, 
    'x_parse_codeowners__mutmut_28': x_parse_codeowners__mutmut_28, 
    'x_parse_codeowners__mutmut_29': x_parse_codeowners__mutmut_29, 
    'x_parse_codeowners__mutmut_30': x_parse_codeowners__mutmut_30, 
    'x_parse_codeowners__mutmut_31': x_parse_codeowners__mutmut_31, 
    'x_parse_codeowners__mutmut_32': x_parse_codeowners__mutmut_32, 
    'x_parse_codeowners__mutmut_33': x_parse_codeowners__mutmut_33, 
    'x_parse_codeowners__mutmut_34': x_parse_codeowners__mutmut_34
}

def parse_codeowners(*args, **kwargs):
    result = _mutmut_trampoline(x_parse_codeowners__mutmut_orig, x_parse_codeowners__mutmut_mutants, args, kwargs)
    return result 

parse_codeowners.__signature__ = _mutmut_signature(x_parse_codeowners__mutmut_orig)
x_parse_codeowners__mutmut_orig.__name__ = 'x_parse_codeowners'


def x_validate_owners__mutmut_orig(rules: list[CodeownersRule]) -> bool:
    ok = True
    for r in rules:
        for o in r.owners:
            if not OWNER_RX.match(o):
                ok = False
    return ok


def x_validate_owners__mutmut_1(rules: list[CodeownersRule]) -> bool:
    ok = None
    for r in rules:
        for o in r.owners:
            if not OWNER_RX.match(o):
                ok = False
    return ok


def x_validate_owners__mutmut_2(rules: list[CodeownersRule]) -> bool:
    ok = False
    for r in rules:
        for o in r.owners:
            if not OWNER_RX.match(o):
                ok = False
    return ok


def x_validate_owners__mutmut_3(rules: list[CodeownersRule]) -> bool:
    ok = True
    for r in rules:
        for o in r.owners:
            if OWNER_RX.match(o):
                ok = False
    return ok


def x_validate_owners__mutmut_4(rules: list[CodeownersRule]) -> bool:
    ok = True
    for r in rules:
        for o in r.owners:
            if not OWNER_RX.match(None):
                ok = False
    return ok


def x_validate_owners__mutmut_5(rules: list[CodeownersRule]) -> bool:
    ok = True
    for r in rules:
        for o in r.owners:
            if not OWNER_RX.match(o):
                ok = None
    return ok


def x_validate_owners__mutmut_6(rules: list[CodeownersRule]) -> bool:
    ok = True
    for r in rules:
        for o in r.owners:
            if not OWNER_RX.match(o):
                ok = True
    return ok

x_validate_owners__mutmut_mutants : ClassVar[MutantDict] = {
'x_validate_owners__mutmut_1': x_validate_owners__mutmut_1, 
    'x_validate_owners__mutmut_2': x_validate_owners__mutmut_2, 
    'x_validate_owners__mutmut_3': x_validate_owners__mutmut_3, 
    'x_validate_owners__mutmut_4': x_validate_owners__mutmut_4, 
    'x_validate_owners__mutmut_5': x_validate_owners__mutmut_5, 
    'x_validate_owners__mutmut_6': x_validate_owners__mutmut_6
}

def validate_owners(*args, **kwargs):
    result = _mutmut_trampoline(x_validate_owners__mutmut_orig, x_validate_owners__mutmut_mutants, args, kwargs)
    return result 

validate_owners.__signature__ = _mutmut_signature(x_validate_owners__mutmut_orig)
x_validate_owners__mutmut_orig.__name__ = 'x_validate_owners'


def x_has_default_rule__mutmut_orig(rules: list[CodeownersRule]) -> bool:
    for r in rules:
        if r.pattern == "*":
            return True
    return False


def x_has_default_rule__mutmut_1(rules: list[CodeownersRule]) -> bool:
    for r in rules:
        if r.pattern != "*":
            return True
    return False


def x_has_default_rule__mutmut_2(rules: list[CodeownersRule]) -> bool:
    for r in rules:
        if r.pattern == "XX*XX":
            return True
    return False


def x_has_default_rule__mutmut_3(rules: list[CodeownersRule]) -> bool:
    for r in rules:
        if r.pattern == "*":
            return False
    return False


def x_has_default_rule__mutmut_4(rules: list[CodeownersRule]) -> bool:
    for r in rules:
        if r.pattern == "*":
            return True
    return True

x_has_default_rule__mutmut_mutants : ClassVar[MutantDict] = {
'x_has_default_rule__mutmut_1': x_has_default_rule__mutmut_1, 
    'x_has_default_rule__mutmut_2': x_has_default_rule__mutmut_2, 
    'x_has_default_rule__mutmut_3': x_has_default_rule__mutmut_3, 
    'x_has_default_rule__mutmut_4': x_has_default_rule__mutmut_4
}

def has_default_rule(*args, **kwargs):
    result = _mutmut_trampoline(x_has_default_rule__mutmut_orig, x_has_default_rule__mutmut_mutants, args, kwargs)
    return result 

has_default_rule.__signature__ = _mutmut_signature(x_has_default_rule__mutmut_orig)
x_has_default_rule__mutmut_orig.__name__ = 'x_has_default_rule'


def x_heuristic_coverage__mutmut_orig(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith("src") or p.startswith("/src") for p in pats),
        "tests": any(p.startswith("tests") or p.startswith("/tests") for p in pats),
        "docs": any(
            p.startswith("docs") or p.startswith("/docs") or p.startswith(".github")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_1(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = None
    return {
        "src": any(p.startswith("src") or p.startswith("/src") for p in pats),
        "tests": any(p.startswith("tests") or p.startswith("/tests") for p in pats),
        "docs": any(
            p.startswith("docs") or p.startswith("/docs") or p.startswith(".github")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_2(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "XXsrcXX": any(p.startswith("src") or p.startswith("/src") for p in pats),
        "tests": any(p.startswith("tests") or p.startswith("/tests") for p in pats),
        "docs": any(
            p.startswith("docs") or p.startswith("/docs") or p.startswith(".github")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_3(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "SRC": any(p.startswith("src") or p.startswith("/src") for p in pats),
        "tests": any(p.startswith("tests") or p.startswith("/tests") for p in pats),
        "docs": any(
            p.startswith("docs") or p.startswith("/docs") or p.startswith(".github")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_4(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(None),
        "tests": any(p.startswith("tests") or p.startswith("/tests") for p in pats),
        "docs": any(
            p.startswith("docs") or p.startswith("/docs") or p.startswith(".github")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_5(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith("src") and p.startswith("/src") for p in pats),
        "tests": any(p.startswith("tests") or p.startswith("/tests") for p in pats),
        "docs": any(
            p.startswith("docs") or p.startswith("/docs") or p.startswith(".github")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_6(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith(None) or p.startswith("/src") for p in pats),
        "tests": any(p.startswith("tests") or p.startswith("/tests") for p in pats),
        "docs": any(
            p.startswith("docs") or p.startswith("/docs") or p.startswith(".github")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_7(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith("XXsrcXX") or p.startswith("/src") for p in pats),
        "tests": any(p.startswith("tests") or p.startswith("/tests") for p in pats),
        "docs": any(
            p.startswith("docs") or p.startswith("/docs") or p.startswith(".github")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_8(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith("SRC") or p.startswith("/src") for p in pats),
        "tests": any(p.startswith("tests") or p.startswith("/tests") for p in pats),
        "docs": any(
            p.startswith("docs") or p.startswith("/docs") or p.startswith(".github")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_9(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith("src") or p.startswith(None) for p in pats),
        "tests": any(p.startswith("tests") or p.startswith("/tests") for p in pats),
        "docs": any(
            p.startswith("docs") or p.startswith("/docs") or p.startswith(".github")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_10(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith("src") or p.startswith("XX/srcXX") for p in pats),
        "tests": any(p.startswith("tests") or p.startswith("/tests") for p in pats),
        "docs": any(
            p.startswith("docs") or p.startswith("/docs") or p.startswith(".github")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_11(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith("src") or p.startswith("/SRC") for p in pats),
        "tests": any(p.startswith("tests") or p.startswith("/tests") for p in pats),
        "docs": any(
            p.startswith("docs") or p.startswith("/docs") or p.startswith(".github")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_12(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith("src") or p.startswith("/src") for p in pats),
        "XXtestsXX": any(p.startswith("tests") or p.startswith("/tests") for p in pats),
        "docs": any(
            p.startswith("docs") or p.startswith("/docs") or p.startswith(".github")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_13(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith("src") or p.startswith("/src") for p in pats),
        "TESTS": any(p.startswith("tests") or p.startswith("/tests") for p in pats),
        "docs": any(
            p.startswith("docs") or p.startswith("/docs") or p.startswith(".github")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_14(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith("src") or p.startswith("/src") for p in pats),
        "tests": any(None),
        "docs": any(
            p.startswith("docs") or p.startswith("/docs") or p.startswith(".github")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_15(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith("src") or p.startswith("/src") for p in pats),
        "tests": any(p.startswith("tests") and p.startswith("/tests") for p in pats),
        "docs": any(
            p.startswith("docs") or p.startswith("/docs") or p.startswith(".github")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_16(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith("src") or p.startswith("/src") for p in pats),
        "tests": any(p.startswith(None) or p.startswith("/tests") for p in pats),
        "docs": any(
            p.startswith("docs") or p.startswith("/docs") or p.startswith(".github")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_17(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith("src") or p.startswith("/src") for p in pats),
        "tests": any(p.startswith("XXtestsXX") or p.startswith("/tests") for p in pats),
        "docs": any(
            p.startswith("docs") or p.startswith("/docs") or p.startswith(".github")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_18(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith("src") or p.startswith("/src") for p in pats),
        "tests": any(p.startswith("TESTS") or p.startswith("/tests") for p in pats),
        "docs": any(
            p.startswith("docs") or p.startswith("/docs") or p.startswith(".github")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_19(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith("src") or p.startswith("/src") for p in pats),
        "tests": any(p.startswith("tests") or p.startswith(None) for p in pats),
        "docs": any(
            p.startswith("docs") or p.startswith("/docs") or p.startswith(".github")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_20(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith("src") or p.startswith("/src") for p in pats),
        "tests": any(p.startswith("tests") or p.startswith("XX/testsXX") for p in pats),
        "docs": any(
            p.startswith("docs") or p.startswith("/docs") or p.startswith(".github")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_21(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith("src") or p.startswith("/src") for p in pats),
        "tests": any(p.startswith("tests") or p.startswith("/TESTS") for p in pats),
        "docs": any(
            p.startswith("docs") or p.startswith("/docs") or p.startswith(".github")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_22(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith("src") or p.startswith("/src") for p in pats),
        "tests": any(p.startswith("tests") or p.startswith("/tests") for p in pats),
        "XXdocsXX": any(
            p.startswith("docs") or p.startswith("/docs") or p.startswith(".github")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_23(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith("src") or p.startswith("/src") for p in pats),
        "tests": any(p.startswith("tests") or p.startswith("/tests") for p in pats),
        "DOCS": any(
            p.startswith("docs") or p.startswith("/docs") or p.startswith(".github")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_24(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith("src") or p.startswith("/src") for p in pats),
        "tests": any(p.startswith("tests") or p.startswith("/tests") for p in pats),
        "docs": any(
            None
        ),
    }


def x_heuristic_coverage__mutmut_25(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith("src") or p.startswith("/src") for p in pats),
        "tests": any(p.startswith("tests") or p.startswith("/tests") for p in pats),
        "docs": any(
            p.startswith("docs") or p.startswith("/docs") and p.startswith(".github")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_26(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith("src") or p.startswith("/src") for p in pats),
        "tests": any(p.startswith("tests") or p.startswith("/tests") for p in pats),
        "docs": any(
            p.startswith("docs") and p.startswith("/docs") or p.startswith(".github")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_27(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith("src") or p.startswith("/src") for p in pats),
        "tests": any(p.startswith("tests") or p.startswith("/tests") for p in pats),
        "docs": any(
            p.startswith(None) or p.startswith("/docs") or p.startswith(".github")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_28(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith("src") or p.startswith("/src") for p in pats),
        "tests": any(p.startswith("tests") or p.startswith("/tests") for p in pats),
        "docs": any(
            p.startswith("XXdocsXX") or p.startswith("/docs") or p.startswith(".github")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_29(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith("src") or p.startswith("/src") for p in pats),
        "tests": any(p.startswith("tests") or p.startswith("/tests") for p in pats),
        "docs": any(
            p.startswith("DOCS") or p.startswith("/docs") or p.startswith(".github")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_30(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith("src") or p.startswith("/src") for p in pats),
        "tests": any(p.startswith("tests") or p.startswith("/tests") for p in pats),
        "docs": any(
            p.startswith("docs") or p.startswith(None) or p.startswith(".github")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_31(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith("src") or p.startswith("/src") for p in pats),
        "tests": any(p.startswith("tests") or p.startswith("/tests") for p in pats),
        "docs": any(
            p.startswith("docs") or p.startswith("XX/docsXX") or p.startswith(".github")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_32(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith("src") or p.startswith("/src") for p in pats),
        "tests": any(p.startswith("tests") or p.startswith("/tests") for p in pats),
        "docs": any(
            p.startswith("docs") or p.startswith("/DOCS") or p.startswith(".github")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_33(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith("src") or p.startswith("/src") for p in pats),
        "tests": any(p.startswith("tests") or p.startswith("/tests") for p in pats),
        "docs": any(
            p.startswith("docs") or p.startswith("/docs") or p.startswith(None)
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_34(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith("src") or p.startswith("/src") for p in pats),
        "tests": any(p.startswith("tests") or p.startswith("/tests") for p in pats),
        "docs": any(
            p.startswith("docs") or p.startswith("/docs") or p.startswith("XX.githubXX")
            for p in pats
        ),
    }


def x_heuristic_coverage__mutmut_35(rules: list[CodeownersRule]) -> dict[str, bool]:
    pats = {r.pattern for r in rules}
    return {
        "src": any(p.startswith("src") or p.startswith("/src") for p in pats),
        "tests": any(p.startswith("tests") or p.startswith("/tests") for p in pats),
        "docs": any(
            p.startswith("docs") or p.startswith("/docs") or p.startswith(".GITHUB")
            for p in pats
        ),
    }

x_heuristic_coverage__mutmut_mutants : ClassVar[MutantDict] = {
'x_heuristic_coverage__mutmut_1': x_heuristic_coverage__mutmut_1, 
    'x_heuristic_coverage__mutmut_2': x_heuristic_coverage__mutmut_2, 
    'x_heuristic_coverage__mutmut_3': x_heuristic_coverage__mutmut_3, 
    'x_heuristic_coverage__mutmut_4': x_heuristic_coverage__mutmut_4, 
    'x_heuristic_coverage__mutmut_5': x_heuristic_coverage__mutmut_5, 
    'x_heuristic_coverage__mutmut_6': x_heuristic_coverage__mutmut_6, 
    'x_heuristic_coverage__mutmut_7': x_heuristic_coverage__mutmut_7, 
    'x_heuristic_coverage__mutmut_8': x_heuristic_coverage__mutmut_8, 
    'x_heuristic_coverage__mutmut_9': x_heuristic_coverage__mutmut_9, 
    'x_heuristic_coverage__mutmut_10': x_heuristic_coverage__mutmut_10, 
    'x_heuristic_coverage__mutmut_11': x_heuristic_coverage__mutmut_11, 
    'x_heuristic_coverage__mutmut_12': x_heuristic_coverage__mutmut_12, 
    'x_heuristic_coverage__mutmut_13': x_heuristic_coverage__mutmut_13, 
    'x_heuristic_coverage__mutmut_14': x_heuristic_coverage__mutmut_14, 
    'x_heuristic_coverage__mutmut_15': x_heuristic_coverage__mutmut_15, 
    'x_heuristic_coverage__mutmut_16': x_heuristic_coverage__mutmut_16, 
    'x_heuristic_coverage__mutmut_17': x_heuristic_coverage__mutmut_17, 
    'x_heuristic_coverage__mutmut_18': x_heuristic_coverage__mutmut_18, 
    'x_heuristic_coverage__mutmut_19': x_heuristic_coverage__mutmut_19, 
    'x_heuristic_coverage__mutmut_20': x_heuristic_coverage__mutmut_20, 
    'x_heuristic_coverage__mutmut_21': x_heuristic_coverage__mutmut_21, 
    'x_heuristic_coverage__mutmut_22': x_heuristic_coverage__mutmut_22, 
    'x_heuristic_coverage__mutmut_23': x_heuristic_coverage__mutmut_23, 
    'x_heuristic_coverage__mutmut_24': x_heuristic_coverage__mutmut_24, 
    'x_heuristic_coverage__mutmut_25': x_heuristic_coverage__mutmut_25, 
    'x_heuristic_coverage__mutmut_26': x_heuristic_coverage__mutmut_26, 
    'x_heuristic_coverage__mutmut_27': x_heuristic_coverage__mutmut_27, 
    'x_heuristic_coverage__mutmut_28': x_heuristic_coverage__mutmut_28, 
    'x_heuristic_coverage__mutmut_29': x_heuristic_coverage__mutmut_29, 
    'x_heuristic_coverage__mutmut_30': x_heuristic_coverage__mutmut_30, 
    'x_heuristic_coverage__mutmut_31': x_heuristic_coverage__mutmut_31, 
    'x_heuristic_coverage__mutmut_32': x_heuristic_coverage__mutmut_32, 
    'x_heuristic_coverage__mutmut_33': x_heuristic_coverage__mutmut_33, 
    'x_heuristic_coverage__mutmut_34': x_heuristic_coverage__mutmut_34, 
    'x_heuristic_coverage__mutmut_35': x_heuristic_coverage__mutmut_35
}

def heuristic_coverage(*args, **kwargs):
    result = _mutmut_trampoline(x_heuristic_coverage__mutmut_orig, x_heuristic_coverage__mutmut_mutants, args, kwargs)
    return result 

heuristic_coverage.__signature__ = _mutmut_signature(x_heuristic_coverage__mutmut_orig)
x_heuristic_coverage__mutmut_orig.__name__ = 'x_heuristic_coverage'


def x_validate_codeowners_text__mutmut_orig(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_1(text: str) -> CodeownersReport:
    rules = None
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_2(text: str) -> CodeownersReport:
    rules = parse_codeowners(None)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_3(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = None
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_4(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = None
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_5(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_6(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append(None)
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_7(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("XXNo parsable CODEOWNERS rules found.XX")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_8(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("no parsable codeowners rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_9(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("NO PARSABLE CODEOWNERS RULES FOUND.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_10(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = None
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_11(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_12(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            None
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_13(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(None)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_14(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {'XX, XX'.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_15(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(None) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_16(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = None
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_17(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(None)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_18(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_19(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append(None)
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_20(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("XXOne or more owners do not match @user or @org/team format.XX")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_21(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("one or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_22(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("ONE OR MORE OWNERS DO NOT MATCH @USER OR @ORG/TEAM FORMAT.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_23(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = None
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_24(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(None)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_25(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_26(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append(None)
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_27(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("XXDefault '*' rule not found; add a fallback ownership rule.XX")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_28(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_29(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("DEFAULT '*' RULE NOT FOUND; ADD A FALLBACK OWNERSHIP RULE.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_30(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = None
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_31(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(None)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_32(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=None,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_33(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=None,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_34(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=None,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_35(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=None,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_36(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=None,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_37(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=None,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_38(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=None,
    )


def x_validate_codeowners_text__mutmut_39(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_40(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_41(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_42(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_43(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_44(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_45(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        )


def x_validate_codeowners_text__mutmut_46(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=False,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_47(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"XXpatternXX": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_48(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"PATTERN": r.pattern, "owners": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_49(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "XXownersXX": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_50(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "OWNERS": r.owners, "line": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_51(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "XXlineXX": r.line_no} for r in rules
        ],
    )


def x_validate_codeowners_text__mutmut_52(text: str) -> CodeownersReport:
    rules = parse_codeowners(text)
    errs: list[str] = []
    warns: list[str] = []
    if not rules:
        errs.append("No parsable CODEOWNERS rules found.")
    any_missing_owners = [r for r in rules if not r.owners]
    if any_missing_owners:
        warns.append(
            f"{len(any_missing_owners)} rule(s) missing owners (lines: {', '.join(str(r.line_no) for r in any_missing_owners)})"
        )
    owners_ok = validate_owners(rules)
    if not owners_ok:
        errs.append("One or more owners do not match @user or @org/team format.")
    default_ok = has_default_rule(rules)
    if not default_ok:
        warns.append("Default '*' rule not found; add a fallback ownership rule.")
    cov = heuristic_coverage(rules)
    return CodeownersReport(
        exists=True,
        default_rule=default_ok,
        owners_ok=owners_ok,
        coverage=cov,
        errors=errs,
        warnings=warns,
        rules=[
            {"pattern": r.pattern, "owners": r.owners, "LINE": r.line_no} for r in rules
        ],
    )

x_validate_codeowners_text__mutmut_mutants : ClassVar[MutantDict] = {
'x_validate_codeowners_text__mutmut_1': x_validate_codeowners_text__mutmut_1, 
    'x_validate_codeowners_text__mutmut_2': x_validate_codeowners_text__mutmut_2, 
    'x_validate_codeowners_text__mutmut_3': x_validate_codeowners_text__mutmut_3, 
    'x_validate_codeowners_text__mutmut_4': x_validate_codeowners_text__mutmut_4, 
    'x_validate_codeowners_text__mutmut_5': x_validate_codeowners_text__mutmut_5, 
    'x_validate_codeowners_text__mutmut_6': x_validate_codeowners_text__mutmut_6, 
    'x_validate_codeowners_text__mutmut_7': x_validate_codeowners_text__mutmut_7, 
    'x_validate_codeowners_text__mutmut_8': x_validate_codeowners_text__mutmut_8, 
    'x_validate_codeowners_text__mutmut_9': x_validate_codeowners_text__mutmut_9, 
    'x_validate_codeowners_text__mutmut_10': x_validate_codeowners_text__mutmut_10, 
    'x_validate_codeowners_text__mutmut_11': x_validate_codeowners_text__mutmut_11, 
    'x_validate_codeowners_text__mutmut_12': x_validate_codeowners_text__mutmut_12, 
    'x_validate_codeowners_text__mutmut_13': x_validate_codeowners_text__mutmut_13, 
    'x_validate_codeowners_text__mutmut_14': x_validate_codeowners_text__mutmut_14, 
    'x_validate_codeowners_text__mutmut_15': x_validate_codeowners_text__mutmut_15, 
    'x_validate_codeowners_text__mutmut_16': x_validate_codeowners_text__mutmut_16, 
    'x_validate_codeowners_text__mutmut_17': x_validate_codeowners_text__mutmut_17, 
    'x_validate_codeowners_text__mutmut_18': x_validate_codeowners_text__mutmut_18, 
    'x_validate_codeowners_text__mutmut_19': x_validate_codeowners_text__mutmut_19, 
    'x_validate_codeowners_text__mutmut_20': x_validate_codeowners_text__mutmut_20, 
    'x_validate_codeowners_text__mutmut_21': x_validate_codeowners_text__mutmut_21, 
    'x_validate_codeowners_text__mutmut_22': x_validate_codeowners_text__mutmut_22, 
    'x_validate_codeowners_text__mutmut_23': x_validate_codeowners_text__mutmut_23, 
    'x_validate_codeowners_text__mutmut_24': x_validate_codeowners_text__mutmut_24, 
    'x_validate_codeowners_text__mutmut_25': x_validate_codeowners_text__mutmut_25, 
    'x_validate_codeowners_text__mutmut_26': x_validate_codeowners_text__mutmut_26, 
    'x_validate_codeowners_text__mutmut_27': x_validate_codeowners_text__mutmut_27, 
    'x_validate_codeowners_text__mutmut_28': x_validate_codeowners_text__mutmut_28, 
    'x_validate_codeowners_text__mutmut_29': x_validate_codeowners_text__mutmut_29, 
    'x_validate_codeowners_text__mutmut_30': x_validate_codeowners_text__mutmut_30, 
    'x_validate_codeowners_text__mutmut_31': x_validate_codeowners_text__mutmut_31, 
    'x_validate_codeowners_text__mutmut_32': x_validate_codeowners_text__mutmut_32, 
    'x_validate_codeowners_text__mutmut_33': x_validate_codeowners_text__mutmut_33, 
    'x_validate_codeowners_text__mutmut_34': x_validate_codeowners_text__mutmut_34, 
    'x_validate_codeowners_text__mutmut_35': x_validate_codeowners_text__mutmut_35, 
    'x_validate_codeowners_text__mutmut_36': x_validate_codeowners_text__mutmut_36, 
    'x_validate_codeowners_text__mutmut_37': x_validate_codeowners_text__mutmut_37, 
    'x_validate_codeowners_text__mutmut_38': x_validate_codeowners_text__mutmut_38, 
    'x_validate_codeowners_text__mutmut_39': x_validate_codeowners_text__mutmut_39, 
    'x_validate_codeowners_text__mutmut_40': x_validate_codeowners_text__mutmut_40, 
    'x_validate_codeowners_text__mutmut_41': x_validate_codeowners_text__mutmut_41, 
    'x_validate_codeowners_text__mutmut_42': x_validate_codeowners_text__mutmut_42, 
    'x_validate_codeowners_text__mutmut_43': x_validate_codeowners_text__mutmut_43, 
    'x_validate_codeowners_text__mutmut_44': x_validate_codeowners_text__mutmut_44, 
    'x_validate_codeowners_text__mutmut_45': x_validate_codeowners_text__mutmut_45, 
    'x_validate_codeowners_text__mutmut_46': x_validate_codeowners_text__mutmut_46, 
    'x_validate_codeowners_text__mutmut_47': x_validate_codeowners_text__mutmut_47, 
    'x_validate_codeowners_text__mutmut_48': x_validate_codeowners_text__mutmut_48, 
    'x_validate_codeowners_text__mutmut_49': x_validate_codeowners_text__mutmut_49, 
    'x_validate_codeowners_text__mutmut_50': x_validate_codeowners_text__mutmut_50, 
    'x_validate_codeowners_text__mutmut_51': x_validate_codeowners_text__mutmut_51, 
    'x_validate_codeowners_text__mutmut_52': x_validate_codeowners_text__mutmut_52
}

def validate_codeowners_text(*args, **kwargs):
    result = _mutmut_trampoline(x_validate_codeowners_text__mutmut_orig, x_validate_codeowners_text__mutmut_mutants, args, kwargs)
    return result 

validate_codeowners_text.__signature__ = _mutmut_signature(x_validate_codeowners_text__mutmut_orig)
x_validate_codeowners_text__mutmut_orig.__name__ = 'x_validate_codeowners_text'


def x_validate_repo_codeowners__mutmut_orig(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_1(repo_root: str | Path = "XX.XX") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_2(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = None
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_3(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(None)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_4(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = None
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_5(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" * "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_6(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root * ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_7(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / "XX.githubXX" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_8(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".GITHUB" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_9(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "XXCODEOWNERSXX", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_10(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "codeowners", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_11(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root * "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_12(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "XXCODEOWNERSXX"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_13(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "codeowners"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_14(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = None
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_15(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding=None, errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_16(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors=None)
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_17(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_18(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", )
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_19(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="XXutf-8XX", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_20(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="UTF-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_21(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="XXignoreXX")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_22(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="IGNORE")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_23(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(None)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_24(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=None,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_25(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=None,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_26(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=None,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_27(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage=None,
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_28(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=None,
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_29(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=None,
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_30(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=None,
    )


def x_validate_repo_codeowners__mutmut_31(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_32(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_33(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_34(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_35(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_36(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_37(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        )


def x_validate_repo_codeowners__mutmut_38(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=True,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_39(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=True,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_40(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=True,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_41(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"XXsrcXX": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_42(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"SRC": False, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_43(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": True, "tests": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_44(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "XXtestsXX": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_45(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "TESTS": False, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_46(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": True, "docs": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_47(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "XXdocsXX": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_48(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "DOCS": False},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_49(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": True},
        errors=["CODEOWNERS file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_50(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["XXCODEOWNERS file not found.XX"],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_51(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["codeowners file not found."],
        warnings=[],
        rules=[],
    )


def x_validate_repo_codeowners__mutmut_52(repo_root: str | Path = ".") -> CodeownersReport:
    """
    Locate and validate .github/CODEOWNERS. If missing, returns a report with exists=False.
    """
    root = Path(repo_root)
    candidates = [root / ".github" / "CODEOWNERS", root / "CODEOWNERS"]
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8", errors="ignore")
            return validate_codeowners_text(text)
    # Not found
    return CodeownersReport(
        exists=False,
        default_rule=False,
        owners_ok=False,
        coverage={"src": False, "tests": False, "docs": False},
        errors=["CODEOWNERS FILE NOT FOUND."],
        warnings=[],
        rules=[],
    )

x_validate_repo_codeowners__mutmut_mutants : ClassVar[MutantDict] = {
'x_validate_repo_codeowners__mutmut_1': x_validate_repo_codeowners__mutmut_1, 
    'x_validate_repo_codeowners__mutmut_2': x_validate_repo_codeowners__mutmut_2, 
    'x_validate_repo_codeowners__mutmut_3': x_validate_repo_codeowners__mutmut_3, 
    'x_validate_repo_codeowners__mutmut_4': x_validate_repo_codeowners__mutmut_4, 
    'x_validate_repo_codeowners__mutmut_5': x_validate_repo_codeowners__mutmut_5, 
    'x_validate_repo_codeowners__mutmut_6': x_validate_repo_codeowners__mutmut_6, 
    'x_validate_repo_codeowners__mutmut_7': x_validate_repo_codeowners__mutmut_7, 
    'x_validate_repo_codeowners__mutmut_8': x_validate_repo_codeowners__mutmut_8, 
    'x_validate_repo_codeowners__mutmut_9': x_validate_repo_codeowners__mutmut_9, 
    'x_validate_repo_codeowners__mutmut_10': x_validate_repo_codeowners__mutmut_10, 
    'x_validate_repo_codeowners__mutmut_11': x_validate_repo_codeowners__mutmut_11, 
    'x_validate_repo_codeowners__mutmut_12': x_validate_repo_codeowners__mutmut_12, 
    'x_validate_repo_codeowners__mutmut_13': x_validate_repo_codeowners__mutmut_13, 
    'x_validate_repo_codeowners__mutmut_14': x_validate_repo_codeowners__mutmut_14, 
    'x_validate_repo_codeowners__mutmut_15': x_validate_repo_codeowners__mutmut_15, 
    'x_validate_repo_codeowners__mutmut_16': x_validate_repo_codeowners__mutmut_16, 
    'x_validate_repo_codeowners__mutmut_17': x_validate_repo_codeowners__mutmut_17, 
    'x_validate_repo_codeowners__mutmut_18': x_validate_repo_codeowners__mutmut_18, 
    'x_validate_repo_codeowners__mutmut_19': x_validate_repo_codeowners__mutmut_19, 
    'x_validate_repo_codeowners__mutmut_20': x_validate_repo_codeowners__mutmut_20, 
    'x_validate_repo_codeowners__mutmut_21': x_validate_repo_codeowners__mutmut_21, 
    'x_validate_repo_codeowners__mutmut_22': x_validate_repo_codeowners__mutmut_22, 
    'x_validate_repo_codeowners__mutmut_23': x_validate_repo_codeowners__mutmut_23, 
    'x_validate_repo_codeowners__mutmut_24': x_validate_repo_codeowners__mutmut_24, 
    'x_validate_repo_codeowners__mutmut_25': x_validate_repo_codeowners__mutmut_25, 
    'x_validate_repo_codeowners__mutmut_26': x_validate_repo_codeowners__mutmut_26, 
    'x_validate_repo_codeowners__mutmut_27': x_validate_repo_codeowners__mutmut_27, 
    'x_validate_repo_codeowners__mutmut_28': x_validate_repo_codeowners__mutmut_28, 
    'x_validate_repo_codeowners__mutmut_29': x_validate_repo_codeowners__mutmut_29, 
    'x_validate_repo_codeowners__mutmut_30': x_validate_repo_codeowners__mutmut_30, 
    'x_validate_repo_codeowners__mutmut_31': x_validate_repo_codeowners__mutmut_31, 
    'x_validate_repo_codeowners__mutmut_32': x_validate_repo_codeowners__mutmut_32, 
    'x_validate_repo_codeowners__mutmut_33': x_validate_repo_codeowners__mutmut_33, 
    'x_validate_repo_codeowners__mutmut_34': x_validate_repo_codeowners__mutmut_34, 
    'x_validate_repo_codeowners__mutmut_35': x_validate_repo_codeowners__mutmut_35, 
    'x_validate_repo_codeowners__mutmut_36': x_validate_repo_codeowners__mutmut_36, 
    'x_validate_repo_codeowners__mutmut_37': x_validate_repo_codeowners__mutmut_37, 
    'x_validate_repo_codeowners__mutmut_38': x_validate_repo_codeowners__mutmut_38, 
    'x_validate_repo_codeowners__mutmut_39': x_validate_repo_codeowners__mutmut_39, 
    'x_validate_repo_codeowners__mutmut_40': x_validate_repo_codeowners__mutmut_40, 
    'x_validate_repo_codeowners__mutmut_41': x_validate_repo_codeowners__mutmut_41, 
    'x_validate_repo_codeowners__mutmut_42': x_validate_repo_codeowners__mutmut_42, 
    'x_validate_repo_codeowners__mutmut_43': x_validate_repo_codeowners__mutmut_43, 
    'x_validate_repo_codeowners__mutmut_44': x_validate_repo_codeowners__mutmut_44, 
    'x_validate_repo_codeowners__mutmut_45': x_validate_repo_codeowners__mutmut_45, 
    'x_validate_repo_codeowners__mutmut_46': x_validate_repo_codeowners__mutmut_46, 
    'x_validate_repo_codeowners__mutmut_47': x_validate_repo_codeowners__mutmut_47, 
    'x_validate_repo_codeowners__mutmut_48': x_validate_repo_codeowners__mutmut_48, 
    'x_validate_repo_codeowners__mutmut_49': x_validate_repo_codeowners__mutmut_49, 
    'x_validate_repo_codeowners__mutmut_50': x_validate_repo_codeowners__mutmut_50, 
    'x_validate_repo_codeowners__mutmut_51': x_validate_repo_codeowners__mutmut_51, 
    'x_validate_repo_codeowners__mutmut_52': x_validate_repo_codeowners__mutmut_52
}

def validate_repo_codeowners(*args, **kwargs):
    result = _mutmut_trampoline(x_validate_repo_codeowners__mutmut_orig, x_validate_repo_codeowners__mutmut_mutants, args, kwargs)
    return result 

validate_repo_codeowners.__signature__ = _mutmut_signature(x_validate_repo_codeowners__mutmut_orig)
x_validate_repo_codeowners__mutmut_orig.__name__ = 'x_validate_repo_codeowners'
