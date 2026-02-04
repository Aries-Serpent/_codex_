"""Helpers for writing consolidation shims and pointers."""

from __future__ import annotations

from pathlib import Path

_PY_WARN = (
    "import warnings as _warnings\n"
    '_warnings.warn("Deprecated shim: re-export from canonical module", '
    "DeprecationWarning, stacklevel=2)\n"
)
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


def x_write_python_shim__mutmut_orig(duplicate: Path, canonical_import_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        "# AUTO-GENERATED SHIM — DO NOT EDIT\n"
        f"{_PY_WARN}"
        f"from {canonical_import_path} import *  # noqa: F401,F403\n",
        encoding="utf-8",
    )


def x_write_python_shim__mutmut_1(duplicate: Path, canonical_import_path: str) -> None:
    duplicate.parent.mkdir(parents=None, exist_ok=True)
    duplicate.write_text(
        "# AUTO-GENERATED SHIM — DO NOT EDIT\n"
        f"{_PY_WARN}"
        f"from {canonical_import_path} import *  # noqa: F401,F403\n",
        encoding="utf-8",
    )


def x_write_python_shim__mutmut_2(duplicate: Path, canonical_import_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=None)
    duplicate.write_text(
        "# AUTO-GENERATED SHIM — DO NOT EDIT\n"
        f"{_PY_WARN}"
        f"from {canonical_import_path} import *  # noqa: F401,F403\n",
        encoding="utf-8",
    )


def x_write_python_shim__mutmut_3(duplicate: Path, canonical_import_path: str) -> None:
    duplicate.parent.mkdir(exist_ok=True)
    duplicate.write_text(
        "# AUTO-GENERATED SHIM — DO NOT EDIT\n"
        f"{_PY_WARN}"
        f"from {canonical_import_path} import *  # noqa: F401,F403\n",
        encoding="utf-8",
    )


def x_write_python_shim__mutmut_4(duplicate: Path, canonical_import_path: str) -> None:
    duplicate.parent.mkdir(parents=True, )
    duplicate.write_text(
        "# AUTO-GENERATED SHIM — DO NOT EDIT\n"
        f"{_PY_WARN}"
        f"from {canonical_import_path} import *  # noqa: F401,F403\n",
        encoding="utf-8",
    )


def x_write_python_shim__mutmut_5(duplicate: Path, canonical_import_path: str) -> None:
    duplicate.parent.mkdir(parents=False, exist_ok=True)
    duplicate.write_text(
        "# AUTO-GENERATED SHIM — DO NOT EDIT\n"
        f"{_PY_WARN}"
        f"from {canonical_import_path} import *  # noqa: F401,F403\n",
        encoding="utf-8",
    )


def x_write_python_shim__mutmut_6(duplicate: Path, canonical_import_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=False)
    duplicate.write_text(
        "# AUTO-GENERATED SHIM — DO NOT EDIT\n"
        f"{_PY_WARN}"
        f"from {canonical_import_path} import *  # noqa: F401,F403\n",
        encoding="utf-8",
    )


def x_write_python_shim__mutmut_7(duplicate: Path, canonical_import_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        None,
        encoding="utf-8",
    )


def x_write_python_shim__mutmut_8(duplicate: Path, canonical_import_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        "# AUTO-GENERATED SHIM — DO NOT EDIT\n"
        f"{_PY_WARN}"
        f"from {canonical_import_path} import *  # noqa: F401,F403\n",
        encoding=None,
    )


def x_write_python_shim__mutmut_9(duplicate: Path, canonical_import_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        encoding="utf-8",
    )


def x_write_python_shim__mutmut_10(duplicate: Path, canonical_import_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        "# AUTO-GENERATED SHIM — DO NOT EDIT\n"
        f"{_PY_WARN}"
        f"from {canonical_import_path} import *  # noqa: F401,F403\n",
        )


def x_write_python_shim__mutmut_11(duplicate: Path, canonical_import_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        "XX# AUTO-GENERATED SHIM — DO NOT EDIT\nXX"
        f"{_PY_WARN}"
        f"from {canonical_import_path} import *  # noqa: F401,F403\n",
        encoding="utf-8",
    )


def x_write_python_shim__mutmut_12(duplicate: Path, canonical_import_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        "# auto-generated shim — do not edit\n"
        f"{_PY_WARN}"
        f"from {canonical_import_path} import *  # noqa: F401,F403\n",
        encoding="utf-8",
    )


def x_write_python_shim__mutmut_13(duplicate: Path, canonical_import_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        "# AUTO-GENERATED SHIM — DO NOT EDIT\n"
        f"{_PY_WARN}"
        f"from {canonical_import_path} import *  # noqa: F401,F403\n",
        encoding="XXutf-8XX",
    )


def x_write_python_shim__mutmut_14(duplicate: Path, canonical_import_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        "# AUTO-GENERATED SHIM — DO NOT EDIT\n"
        f"{_PY_WARN}"
        f"from {canonical_import_path} import *  # noqa: F401,F403\n",
        encoding="UTF-8",
    )

x_write_python_shim__mutmut_mutants : ClassVar[MutantDict] = {
'x_write_python_shim__mutmut_1': x_write_python_shim__mutmut_1, 
    'x_write_python_shim__mutmut_2': x_write_python_shim__mutmut_2, 
    'x_write_python_shim__mutmut_3': x_write_python_shim__mutmut_3, 
    'x_write_python_shim__mutmut_4': x_write_python_shim__mutmut_4, 
    'x_write_python_shim__mutmut_5': x_write_python_shim__mutmut_5, 
    'x_write_python_shim__mutmut_6': x_write_python_shim__mutmut_6, 
    'x_write_python_shim__mutmut_7': x_write_python_shim__mutmut_7, 
    'x_write_python_shim__mutmut_8': x_write_python_shim__mutmut_8, 
    'x_write_python_shim__mutmut_9': x_write_python_shim__mutmut_9, 
    'x_write_python_shim__mutmut_10': x_write_python_shim__mutmut_10, 
    'x_write_python_shim__mutmut_11': x_write_python_shim__mutmut_11, 
    'x_write_python_shim__mutmut_12': x_write_python_shim__mutmut_12, 
    'x_write_python_shim__mutmut_13': x_write_python_shim__mutmut_13, 
    'x_write_python_shim__mutmut_14': x_write_python_shim__mutmut_14
}

def write_python_shim(*args, **kwargs):
    result = _mutmut_trampoline(x_write_python_shim__mutmut_orig, x_write_python_shim__mutmut_mutants, args, kwargs)
    return result 

write_python_shim.__signature__ = _mutmut_signature(x_write_python_shim__mutmut_orig)
x_write_python_shim__mutmut_orig.__name__ = 'x_write_python_shim'


def x_write_markdown_pointer__mutmut_orig(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        f"**This document has been consolidated.** See canonical: `{canonical_rel_path}`.\n",
        encoding="utf-8",
    )


def x_write_markdown_pointer__mutmut_1(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=None, exist_ok=True)
    duplicate.write_text(
        f"**This document has been consolidated.** See canonical: `{canonical_rel_path}`.\n",
        encoding="utf-8",
    )


def x_write_markdown_pointer__mutmut_2(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=None)
    duplicate.write_text(
        f"**This document has been consolidated.** See canonical: `{canonical_rel_path}`.\n",
        encoding="utf-8",
    )


def x_write_markdown_pointer__mutmut_3(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(exist_ok=True)
    duplicate.write_text(
        f"**This document has been consolidated.** See canonical: `{canonical_rel_path}`.\n",
        encoding="utf-8",
    )


def x_write_markdown_pointer__mutmut_4(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, )
    duplicate.write_text(
        f"**This document has been consolidated.** See canonical: `{canonical_rel_path}`.\n",
        encoding="utf-8",
    )


def x_write_markdown_pointer__mutmut_5(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=False, exist_ok=True)
    duplicate.write_text(
        f"**This document has been consolidated.** See canonical: `{canonical_rel_path}`.\n",
        encoding="utf-8",
    )


def x_write_markdown_pointer__mutmut_6(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=False)
    duplicate.write_text(
        f"**This document has been consolidated.** See canonical: `{canonical_rel_path}`.\n",
        encoding="utf-8",
    )


def x_write_markdown_pointer__mutmut_7(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        None,
        encoding="utf-8",
    )


def x_write_markdown_pointer__mutmut_8(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        f"**This document has been consolidated.** See canonical: `{canonical_rel_path}`.\n",
        encoding=None,
    )


def x_write_markdown_pointer__mutmut_9(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        encoding="utf-8",
    )


def x_write_markdown_pointer__mutmut_10(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        f"**This document has been consolidated.** See canonical: `{canonical_rel_path}`.\n",
        )


def x_write_markdown_pointer__mutmut_11(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        f"**This document has been consolidated.** See canonical: `{canonical_rel_path}`.\n",
        encoding="XXutf-8XX",
    )


def x_write_markdown_pointer__mutmut_12(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        f"**This document has been consolidated.** See canonical: `{canonical_rel_path}`.\n",
        encoding="UTF-8",
    )

x_write_markdown_pointer__mutmut_mutants : ClassVar[MutantDict] = {
'x_write_markdown_pointer__mutmut_1': x_write_markdown_pointer__mutmut_1, 
    'x_write_markdown_pointer__mutmut_2': x_write_markdown_pointer__mutmut_2, 
    'x_write_markdown_pointer__mutmut_3': x_write_markdown_pointer__mutmut_3, 
    'x_write_markdown_pointer__mutmut_4': x_write_markdown_pointer__mutmut_4, 
    'x_write_markdown_pointer__mutmut_5': x_write_markdown_pointer__mutmut_5, 
    'x_write_markdown_pointer__mutmut_6': x_write_markdown_pointer__mutmut_6, 
    'x_write_markdown_pointer__mutmut_7': x_write_markdown_pointer__mutmut_7, 
    'x_write_markdown_pointer__mutmut_8': x_write_markdown_pointer__mutmut_8, 
    'x_write_markdown_pointer__mutmut_9': x_write_markdown_pointer__mutmut_9, 
    'x_write_markdown_pointer__mutmut_10': x_write_markdown_pointer__mutmut_10, 
    'x_write_markdown_pointer__mutmut_11': x_write_markdown_pointer__mutmut_11, 
    'x_write_markdown_pointer__mutmut_12': x_write_markdown_pointer__mutmut_12
}

def write_markdown_pointer(*args, **kwargs):
    result = _mutmut_trampoline(x_write_markdown_pointer__mutmut_orig, x_write_markdown_pointer__mutmut_mutants, args, kwargs)
    return result 

write_markdown_pointer.__signature__ = _mutmut_signature(x_write_markdown_pointer__mutmut_orig)
x_write_markdown_pointer__mutmut_orig.__name__ = 'x_write_markdown_pointer'


def x_write_json_pointer__mutmut_orig(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        '{ "$ref": "' + canonical_rel_path.replace("\\", "/") + '" }\n',
        encoding="utf-8",
    )


def x_write_json_pointer__mutmut_1(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=None, exist_ok=True)
    duplicate.write_text(
        '{ "$ref": "' + canonical_rel_path.replace("\\", "/") + '" }\n',
        encoding="utf-8",
    )


def x_write_json_pointer__mutmut_2(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=None)
    duplicate.write_text(
        '{ "$ref": "' + canonical_rel_path.replace("\\", "/") + '" }\n',
        encoding="utf-8",
    )


def x_write_json_pointer__mutmut_3(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(exist_ok=True)
    duplicate.write_text(
        '{ "$ref": "' + canonical_rel_path.replace("\\", "/") + '" }\n',
        encoding="utf-8",
    )


def x_write_json_pointer__mutmut_4(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, )
    duplicate.write_text(
        '{ "$ref": "' + canonical_rel_path.replace("\\", "/") + '" }\n',
        encoding="utf-8",
    )


def x_write_json_pointer__mutmut_5(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=False, exist_ok=True)
    duplicate.write_text(
        '{ "$ref": "' + canonical_rel_path.replace("\\", "/") + '" }\n',
        encoding="utf-8",
    )


def x_write_json_pointer__mutmut_6(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=False)
    duplicate.write_text(
        '{ "$ref": "' + canonical_rel_path.replace("\\", "/") + '" }\n',
        encoding="utf-8",
    )


def x_write_json_pointer__mutmut_7(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        None,
        encoding="utf-8",
    )


def x_write_json_pointer__mutmut_8(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        '{ "$ref": "' + canonical_rel_path.replace("\\", "/") + '" }\n',
        encoding=None,
    )


def x_write_json_pointer__mutmut_9(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        encoding="utf-8",
    )


def x_write_json_pointer__mutmut_10(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        '{ "$ref": "' + canonical_rel_path.replace("\\", "/") + '" }\n',
        )


def x_write_json_pointer__mutmut_11(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        '{ "$ref": "' + canonical_rel_path.replace("\\", "/") - '" }\n',
        encoding="utf-8",
    )


def x_write_json_pointer__mutmut_12(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        '{ "$ref": "' - canonical_rel_path.replace("\\", "/") + '" }\n',
        encoding="utf-8",
    )


def x_write_json_pointer__mutmut_13(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        'XX{ "$ref": "XX' + canonical_rel_path.replace("\\", "/") + '" }\n',
        encoding="utf-8",
    )


def x_write_json_pointer__mutmut_14(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        '{ "$REF": "' + canonical_rel_path.replace("\\", "/") + '" }\n',
        encoding="utf-8",
    )


def x_write_json_pointer__mutmut_15(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        '{ "$ref": "' + canonical_rel_path.replace(None, "/") + '" }\n',
        encoding="utf-8",
    )


def x_write_json_pointer__mutmut_16(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        '{ "$ref": "' + canonical_rel_path.replace("\\", None) + '" }\n',
        encoding="utf-8",
    )


def x_write_json_pointer__mutmut_17(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        '{ "$ref": "' + canonical_rel_path.replace("/") + '" }\n',
        encoding="utf-8",
    )


def x_write_json_pointer__mutmut_18(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        '{ "$ref": "' + canonical_rel_path.replace("\\", ) + '" }\n',
        encoding="utf-8",
    )


def x_write_json_pointer__mutmut_19(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        '{ "$ref": "' + canonical_rel_path.replace("XX\\XX", "/") + '" }\n',
        encoding="utf-8",
    )


def x_write_json_pointer__mutmut_20(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        '{ "$ref": "' + canonical_rel_path.replace("\\", "XX/XX") + '" }\n',
        encoding="utf-8",
    )


def x_write_json_pointer__mutmut_21(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        '{ "$ref": "' + canonical_rel_path.replace("\\", "/") + 'XX" }\nXX',
        encoding="utf-8",
    )


def x_write_json_pointer__mutmut_22(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        '{ "$ref": "' + canonical_rel_path.replace("\\", "/") + '" }\n',
        encoding="XXutf-8XX",
    )


def x_write_json_pointer__mutmut_23(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        '{ "$ref": "' + canonical_rel_path.replace("\\", "/") + '" }\n',
        encoding="UTF-8",
    )

x_write_json_pointer__mutmut_mutants : ClassVar[MutantDict] = {
'x_write_json_pointer__mutmut_1': x_write_json_pointer__mutmut_1, 
    'x_write_json_pointer__mutmut_2': x_write_json_pointer__mutmut_2, 
    'x_write_json_pointer__mutmut_3': x_write_json_pointer__mutmut_3, 
    'x_write_json_pointer__mutmut_4': x_write_json_pointer__mutmut_4, 
    'x_write_json_pointer__mutmut_5': x_write_json_pointer__mutmut_5, 
    'x_write_json_pointer__mutmut_6': x_write_json_pointer__mutmut_6, 
    'x_write_json_pointer__mutmut_7': x_write_json_pointer__mutmut_7, 
    'x_write_json_pointer__mutmut_8': x_write_json_pointer__mutmut_8, 
    'x_write_json_pointer__mutmut_9': x_write_json_pointer__mutmut_9, 
    'x_write_json_pointer__mutmut_10': x_write_json_pointer__mutmut_10, 
    'x_write_json_pointer__mutmut_11': x_write_json_pointer__mutmut_11, 
    'x_write_json_pointer__mutmut_12': x_write_json_pointer__mutmut_12, 
    'x_write_json_pointer__mutmut_13': x_write_json_pointer__mutmut_13, 
    'x_write_json_pointer__mutmut_14': x_write_json_pointer__mutmut_14, 
    'x_write_json_pointer__mutmut_15': x_write_json_pointer__mutmut_15, 
    'x_write_json_pointer__mutmut_16': x_write_json_pointer__mutmut_16, 
    'x_write_json_pointer__mutmut_17': x_write_json_pointer__mutmut_17, 
    'x_write_json_pointer__mutmut_18': x_write_json_pointer__mutmut_18, 
    'x_write_json_pointer__mutmut_19': x_write_json_pointer__mutmut_19, 
    'x_write_json_pointer__mutmut_20': x_write_json_pointer__mutmut_20, 
    'x_write_json_pointer__mutmut_21': x_write_json_pointer__mutmut_21, 
    'x_write_json_pointer__mutmut_22': x_write_json_pointer__mutmut_22, 
    'x_write_json_pointer__mutmut_23': x_write_json_pointer__mutmut_23
}

def write_json_pointer(*args, **kwargs):
    result = _mutmut_trampoline(x_write_json_pointer__mutmut_orig, x_write_json_pointer__mutmut_mutants, args, kwargs)
    return result 

write_json_pointer.__signature__ = _mutmut_signature(x_write_json_pointer__mutmut_orig)
x_write_json_pointer__mutmut_orig.__name__ = 'x_write_json_pointer'


def x_write_csv_pointer__mutmut_orig(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        f"# Consolidated; see canonical: {canonical_rel_path}\n",
        encoding="utf-8",
    )


def x_write_csv_pointer__mutmut_1(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=None, exist_ok=True)
    duplicate.write_text(
        f"# Consolidated; see canonical: {canonical_rel_path}\n",
        encoding="utf-8",
    )


def x_write_csv_pointer__mutmut_2(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=None)
    duplicate.write_text(
        f"# Consolidated; see canonical: {canonical_rel_path}\n",
        encoding="utf-8",
    )


def x_write_csv_pointer__mutmut_3(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(exist_ok=True)
    duplicate.write_text(
        f"# Consolidated; see canonical: {canonical_rel_path}\n",
        encoding="utf-8",
    )


def x_write_csv_pointer__mutmut_4(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, )
    duplicate.write_text(
        f"# Consolidated; see canonical: {canonical_rel_path}\n",
        encoding="utf-8",
    )


def x_write_csv_pointer__mutmut_5(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=False, exist_ok=True)
    duplicate.write_text(
        f"# Consolidated; see canonical: {canonical_rel_path}\n",
        encoding="utf-8",
    )


def x_write_csv_pointer__mutmut_6(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=False)
    duplicate.write_text(
        f"# Consolidated; see canonical: {canonical_rel_path}\n",
        encoding="utf-8",
    )


def x_write_csv_pointer__mutmut_7(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        None,
        encoding="utf-8",
    )


def x_write_csv_pointer__mutmut_8(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        f"# Consolidated; see canonical: {canonical_rel_path}\n",
        encoding=None,
    )


def x_write_csv_pointer__mutmut_9(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        encoding="utf-8",
    )


def x_write_csv_pointer__mutmut_10(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        f"# Consolidated; see canonical: {canonical_rel_path}\n",
        )


def x_write_csv_pointer__mutmut_11(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        f"# Consolidated; see canonical: {canonical_rel_path}\n",
        encoding="XXutf-8XX",
    )


def x_write_csv_pointer__mutmut_12(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        f"# Consolidated; see canonical: {canonical_rel_path}\n",
        encoding="UTF-8",
    )

x_write_csv_pointer__mutmut_mutants : ClassVar[MutantDict] = {
'x_write_csv_pointer__mutmut_1': x_write_csv_pointer__mutmut_1, 
    'x_write_csv_pointer__mutmut_2': x_write_csv_pointer__mutmut_2, 
    'x_write_csv_pointer__mutmut_3': x_write_csv_pointer__mutmut_3, 
    'x_write_csv_pointer__mutmut_4': x_write_csv_pointer__mutmut_4, 
    'x_write_csv_pointer__mutmut_5': x_write_csv_pointer__mutmut_5, 
    'x_write_csv_pointer__mutmut_6': x_write_csv_pointer__mutmut_6, 
    'x_write_csv_pointer__mutmut_7': x_write_csv_pointer__mutmut_7, 
    'x_write_csv_pointer__mutmut_8': x_write_csv_pointer__mutmut_8, 
    'x_write_csv_pointer__mutmut_9': x_write_csv_pointer__mutmut_9, 
    'x_write_csv_pointer__mutmut_10': x_write_csv_pointer__mutmut_10, 
    'x_write_csv_pointer__mutmut_11': x_write_csv_pointer__mutmut_11, 
    'x_write_csv_pointer__mutmut_12': x_write_csv_pointer__mutmut_12
}

def write_csv_pointer(*args, **kwargs):
    result = _mutmut_trampoline(x_write_csv_pointer__mutmut_orig, x_write_csv_pointer__mutmut_mutants, args, kwargs)
    return result 

write_csv_pointer.__signature__ = _mutmut_signature(x_write_csv_pointer__mutmut_orig)
x_write_csv_pointer__mutmut_orig.__name__ = 'x_write_csv_pointer'
