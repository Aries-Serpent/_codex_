"""Offline apply stubs that emit append-only evidence JSONL."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from codex.evidence import append_evidence, utc_now

__all__ = ["apply_routing_stub", "apply_slas_stub"]
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


def x__normalize_operations__mutmut_orig(plan: Any) -> list[dict[str, Any]]:
    if isinstance(plan, dict):
        ops = plan.get("operations", [])
        return ops if isinstance(ops, list) else []
    if isinstance(plan, list):
        return plan
    return []


def x__normalize_operations__mutmut_1(plan: Any) -> list[dict[str, Any]]:
    if isinstance(plan, dict):
        ops = None
        return ops if isinstance(ops, list) else []
    if isinstance(plan, list):
        return plan
    return []


def x__normalize_operations__mutmut_2(plan: Any) -> list[dict[str, Any]]:
    if isinstance(plan, dict):
        ops = plan.get(None, [])
        return ops if isinstance(ops, list) else []
    if isinstance(plan, list):
        return plan
    return []


def x__normalize_operations__mutmut_3(plan: Any) -> list[dict[str, Any]]:
    if isinstance(plan, dict):
        ops = plan.get("operations", None)
        return ops if isinstance(ops, list) else []
    if isinstance(plan, list):
        return plan
    return []


def x__normalize_operations__mutmut_4(plan: Any) -> list[dict[str, Any]]:
    if isinstance(plan, dict):
        ops = plan.get([])
        return ops if isinstance(ops, list) else []
    if isinstance(plan, list):
        return plan
    return []


def x__normalize_operations__mutmut_5(plan: Any) -> list[dict[str, Any]]:
    if isinstance(plan, dict):
        ops = plan.get("operations", )
        return ops if isinstance(ops, list) else []
    if isinstance(plan, list):
        return plan
    return []


def x__normalize_operations__mutmut_6(plan: Any) -> list[dict[str, Any]]:
    if isinstance(plan, dict):
        ops = plan.get("XXoperationsXX", [])
        return ops if isinstance(ops, list) else []
    if isinstance(plan, list):
        return plan
    return []


def x__normalize_operations__mutmut_7(plan: Any) -> list[dict[str, Any]]:
    if isinstance(plan, dict):
        ops = plan.get("OPERATIONS", [])
        return ops if isinstance(ops, list) else []
    if isinstance(plan, list):
        return plan
    return []

x__normalize_operations__mutmut_mutants : ClassVar[MutantDict] = {
'x__normalize_operations__mutmut_1': x__normalize_operations__mutmut_1, 
    'x__normalize_operations__mutmut_2': x__normalize_operations__mutmut_2, 
    'x__normalize_operations__mutmut_3': x__normalize_operations__mutmut_3, 
    'x__normalize_operations__mutmut_4': x__normalize_operations__mutmut_4, 
    'x__normalize_operations__mutmut_5': x__normalize_operations__mutmut_5, 
    'x__normalize_operations__mutmut_6': x__normalize_operations__mutmut_6, 
    'x__normalize_operations__mutmut_7': x__normalize_operations__mutmut_7
}

def _normalize_operations(*args, **kwargs):
    result = _mutmut_trampoline(x__normalize_operations__mutmut_orig, x__normalize_operations__mutmut_mutants, args, kwargs)
    return result 

_normalize_operations.__signature__ = _mutmut_signature(x__normalize_operations__mutmut_orig)
x__normalize_operations__mutmut_orig.__name__ = 'x__normalize_operations'


def x__operation_action__mutmut_orig(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "update": "Update",
        "patch": "Update",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_1(value: str | None) -> str:
    mapping = None
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_2(value: str | None) -> str:
    mapping = {
        "XXaddXX": "Create",
        "create": "Create",
        "update": "Update",
        "patch": "Update",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_3(value: str | None) -> str:
    mapping = {
        "ADD": "Create",
        "create": "Create",
        "update": "Update",
        "patch": "Update",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_4(value: str | None) -> str:
    mapping = {
        "add": "XXCreateXX",
        "create": "Create",
        "update": "Update",
        "patch": "Update",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_5(value: str | None) -> str:
    mapping = {
        "add": "create",
        "create": "Create",
        "update": "Update",
        "patch": "Update",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_6(value: str | None) -> str:
    mapping = {
        "add": "CREATE",
        "create": "Create",
        "update": "Update",
        "patch": "Update",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_7(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "XXcreateXX": "Create",
        "update": "Update",
        "patch": "Update",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_8(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "CREATE": "Create",
        "update": "Update",
        "patch": "Update",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_9(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "XXCreateXX",
        "update": "Update",
        "patch": "Update",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_10(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "create",
        "update": "Update",
        "patch": "Update",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_11(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "CREATE",
        "update": "Update",
        "patch": "Update",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_12(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "XXupdateXX": "Update",
        "patch": "Update",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_13(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "UPDATE": "Update",
        "patch": "Update",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_14(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "update": "XXUpdateXX",
        "patch": "Update",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_15(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "update": "update",
        "patch": "Update",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_16(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "update": "UPDATE",
        "patch": "Update",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_17(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "update": "Update",
        "XXpatchXX": "Update",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_18(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "update": "Update",
        "PATCH": "Update",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_19(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "update": "Update",
        "patch": "XXUpdateXX",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_20(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "update": "Update",
        "patch": "update",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_21(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "update": "Update",
        "patch": "UPDATE",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_22(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "update": "Update",
        "patch": "Update",
        "XXremoveXX": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_23(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "update": "Update",
        "patch": "Update",
        "REMOVE": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_24(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "update": "Update",
        "patch": "Update",
        "remove": "XXDeleteXX",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_25(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "update": "Update",
        "patch": "Update",
        "remove": "delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_26(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "update": "Update",
        "patch": "Update",
        "remove": "DELETE",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_27(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "update": "Update",
        "patch": "Update",
        "remove": "Delete",
        "XXdeleteXX": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_28(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "update": "Update",
        "patch": "Update",
        "remove": "Delete",
        "DELETE": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_29(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "update": "Update",
        "patch": "Update",
        "remove": "Delete",
        "delete": "XXDeleteXX",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_30(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "update": "Update",
        "patch": "Update",
        "remove": "Delete",
        "delete": "delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_31(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "update": "Update",
        "patch": "Update",
        "remove": "Delete",
        "delete": "DELETE",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_32(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "update": "Update",
        "patch": "Update",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is not None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_33(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "update": "Update",
        "patch": "Update",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "XXUnknownXX"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_34(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "update": "Update",
        "patch": "Update",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "unknown"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_35(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "update": "Update",
        "patch": "Update",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "UNKNOWN"
    return mapping.get(value.lower(), "Unknown")


def x__operation_action__mutmut_36(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "update": "Update",
        "patch": "Update",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(None, "Unknown")


def x__operation_action__mutmut_37(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "update": "Update",
        "patch": "Update",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), None)


def x__operation_action__mutmut_38(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "update": "Update",
        "patch": "Update",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get("Unknown")


def x__operation_action__mutmut_39(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "update": "Update",
        "patch": "Update",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), )


def x__operation_action__mutmut_40(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "update": "Update",
        "patch": "Update",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.upper(), "Unknown")


def x__operation_action__mutmut_41(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "update": "Update",
        "patch": "Update",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "XXUnknownXX")


def x__operation_action__mutmut_42(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "update": "Update",
        "patch": "Update",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "unknown")


def x__operation_action__mutmut_43(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "update": "Update",
        "patch": "Update",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "UNKNOWN")

x__operation_action__mutmut_mutants : ClassVar[MutantDict] = {
'x__operation_action__mutmut_1': x__operation_action__mutmut_1, 
    'x__operation_action__mutmut_2': x__operation_action__mutmut_2, 
    'x__operation_action__mutmut_3': x__operation_action__mutmut_3, 
    'x__operation_action__mutmut_4': x__operation_action__mutmut_4, 
    'x__operation_action__mutmut_5': x__operation_action__mutmut_5, 
    'x__operation_action__mutmut_6': x__operation_action__mutmut_6, 
    'x__operation_action__mutmut_7': x__operation_action__mutmut_7, 
    'x__operation_action__mutmut_8': x__operation_action__mutmut_8, 
    'x__operation_action__mutmut_9': x__operation_action__mutmut_9, 
    'x__operation_action__mutmut_10': x__operation_action__mutmut_10, 
    'x__operation_action__mutmut_11': x__operation_action__mutmut_11, 
    'x__operation_action__mutmut_12': x__operation_action__mutmut_12, 
    'x__operation_action__mutmut_13': x__operation_action__mutmut_13, 
    'x__operation_action__mutmut_14': x__operation_action__mutmut_14, 
    'x__operation_action__mutmut_15': x__operation_action__mutmut_15, 
    'x__operation_action__mutmut_16': x__operation_action__mutmut_16, 
    'x__operation_action__mutmut_17': x__operation_action__mutmut_17, 
    'x__operation_action__mutmut_18': x__operation_action__mutmut_18, 
    'x__operation_action__mutmut_19': x__operation_action__mutmut_19, 
    'x__operation_action__mutmut_20': x__operation_action__mutmut_20, 
    'x__operation_action__mutmut_21': x__operation_action__mutmut_21, 
    'x__operation_action__mutmut_22': x__operation_action__mutmut_22, 
    'x__operation_action__mutmut_23': x__operation_action__mutmut_23, 
    'x__operation_action__mutmut_24': x__operation_action__mutmut_24, 
    'x__operation_action__mutmut_25': x__operation_action__mutmut_25, 
    'x__operation_action__mutmut_26': x__operation_action__mutmut_26, 
    'x__operation_action__mutmut_27': x__operation_action__mutmut_27, 
    'x__operation_action__mutmut_28': x__operation_action__mutmut_28, 
    'x__operation_action__mutmut_29': x__operation_action__mutmut_29, 
    'x__operation_action__mutmut_30': x__operation_action__mutmut_30, 
    'x__operation_action__mutmut_31': x__operation_action__mutmut_31, 
    'x__operation_action__mutmut_32': x__operation_action__mutmut_32, 
    'x__operation_action__mutmut_33': x__operation_action__mutmut_33, 
    'x__operation_action__mutmut_34': x__operation_action__mutmut_34, 
    'x__operation_action__mutmut_35': x__operation_action__mutmut_35, 
    'x__operation_action__mutmut_36': x__operation_action__mutmut_36, 
    'x__operation_action__mutmut_37': x__operation_action__mutmut_37, 
    'x__operation_action__mutmut_38': x__operation_action__mutmut_38, 
    'x__operation_action__mutmut_39': x__operation_action__mutmut_39, 
    'x__operation_action__mutmut_40': x__operation_action__mutmut_40, 
    'x__operation_action__mutmut_41': x__operation_action__mutmut_41, 
    'x__operation_action__mutmut_42': x__operation_action__mutmut_42, 
    'x__operation_action__mutmut_43': x__operation_action__mutmut_43
}

def _operation_action(*args, **kwargs):
    result = _mutmut_trampoline(x__operation_action__mutmut_orig, x__operation_action__mutmut_mutants, args, kwargs)
    return result 

_operation_action.__signature__ = _mutmut_signature(x__operation_action__mutmut_orig)
x__operation_action__mutmut_orig.__name__ = 'x__operation_action'


def x__append_record__mutmut_orig(filename: str, record: dict[str, Any]) -> None:
    append_evidence(
        filename,
        {
            "ts": utc_now(),
            **record,
        },
    )


def x__append_record__mutmut_1(filename: str, record: dict[str, Any]) -> None:
    append_evidence(
        None,
        {
            "ts": utc_now(),
            **record,
        },
    )


def x__append_record__mutmut_2(filename: str, record: dict[str, Any]) -> None:
    append_evidence(
        filename,
        None,
    )


def x__append_record__mutmut_3(filename: str, record: dict[str, Any]) -> None:
    append_evidence(
        {
            "ts": utc_now(),
            **record,
        },
    )


def x__append_record__mutmut_4(filename: str, record: dict[str, Any]) -> None:
    append_evidence(
        filename,
        )


def x__append_record__mutmut_5(filename: str, record: dict[str, Any]) -> None:
    append_evidence(
        filename,
        {
            "XXtsXX": utc_now(),
            **record,
        },
    )


def x__append_record__mutmut_6(filename: str, record: dict[str, Any]) -> None:
    append_evidence(
        filename,
        {
            "TS": utc_now(),
            **record,
        },
    )

x__append_record__mutmut_mutants : ClassVar[MutantDict] = {
'x__append_record__mutmut_1': x__append_record__mutmut_1, 
    'x__append_record__mutmut_2': x__append_record__mutmut_2, 
    'x__append_record__mutmut_3': x__append_record__mutmut_3, 
    'x__append_record__mutmut_4': x__append_record__mutmut_4, 
    'x__append_record__mutmut_5': x__append_record__mutmut_5, 
    'x__append_record__mutmut_6': x__append_record__mutmut_6
}

def _append_record(*args, **kwargs):
    result = _mutmut_trampoline(x__append_record__mutmut_orig, x__append_record__mutmut_mutants, args, kwargs)
    return result 

_append_record.__signature__ = _mutmut_signature(x__append_record__mutmut_orig)
x__append_record__mutmut_orig.__name__ = 'x__append_record'


def x_apply_slas_stub__mutmut_orig(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_1(plan: Any, dry_run: bool = False) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_2(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = None
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_3(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(None)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_4(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = None
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_5(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "XXresourceXX": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_6(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "RESOURCE": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_7(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "XXslaXX",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_8(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "SLA",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_9(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "XXprocessedXX": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_10(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "PROCESSED": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_11(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 1,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_12(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "XXcreatedXX": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_13(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "CREATED": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_14(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 1,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_15(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "XXupdatedXX": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_16(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "UPDATED": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_17(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 1,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_18(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "XXdeletedXX": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_19(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "DELETED": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_20(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 1,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_21(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "XXdry_runXX": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_22(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "DRY_RUN": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_23(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = None
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_24(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(None)
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_25(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") and entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_26(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get(None) or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_27(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("XXactionXX") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_28(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("ACTION") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_29(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get(None))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_30(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("XXopXX"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_31(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("OP"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_32(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = None
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_33(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") and {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_34(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") and entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_35(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get(None) or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_36(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("XXdataXX") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_37(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("DATA") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_38(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get(None) or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_39(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("XXvalueXX") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_40(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("VALUE") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_41(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = None
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_42(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") and _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_43(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get(None) or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_44(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("XXnameXX") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_45(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("NAME") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_46(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(None)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_47(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            None,
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_48(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            None,
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_49(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_50(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_51(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "XXd365_slas.jsonlXX",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_52(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "D365_SLAS.JSONL",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_53(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "XXresourceXX": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_54(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "RESOURCE": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_55(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "XXslaXX",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_56(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "SLA",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_57(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "XXactionXX": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_58(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "ACTION": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_59(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "XXtargetXX": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_60(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "TARGET": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_61(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "XXnameXX": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_62(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "NAME": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_63(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "XXlogical_entityXX": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_64(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "LOGICAL_ENTITY": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_65(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "XXslaXX",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_66(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "SLA",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_67(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "XXdry_runXX": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_68(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "DRY_RUN": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_69(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "XXdataXX": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_70(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "DATA": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_71(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] = 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_72(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] -= 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_73(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["XXprocessedXX"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_74(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["PROCESSED"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_75(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 2
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_76(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action != "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_77(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "XXCreateXX":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_78(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_79(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "CREATE":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_80(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] = 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_81(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] -= 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_82(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["XXcreatedXX"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_83(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["CREATED"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_84(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 2
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_85(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action != "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_86(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "XXUpdateXX":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_87(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_88(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "UPDATE":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_89(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] = 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_90(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] -= 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_91(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["XXupdatedXX"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_92(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["UPDATED"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_93(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 2
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_94(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action != "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_95(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "XXDeleteXX":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_96(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "delete":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_97(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "DELETE":
            summary["deleted"] += 1
    return summary


def x_apply_slas_stub__mutmut_98(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] = 1
    return summary


def x_apply_slas_stub__mutmut_99(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] -= 1
    return summary


def x_apply_slas_stub__mutmut_100(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["XXdeletedXX"] += 1
    return summary


def x_apply_slas_stub__mutmut_101(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["DELETED"] += 1
    return summary


def x_apply_slas_stub__mutmut_102(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 2
    return summary

x_apply_slas_stub__mutmut_mutants : ClassVar[MutantDict] = {
'x_apply_slas_stub__mutmut_1': x_apply_slas_stub__mutmut_1, 
    'x_apply_slas_stub__mutmut_2': x_apply_slas_stub__mutmut_2, 
    'x_apply_slas_stub__mutmut_3': x_apply_slas_stub__mutmut_3, 
    'x_apply_slas_stub__mutmut_4': x_apply_slas_stub__mutmut_4, 
    'x_apply_slas_stub__mutmut_5': x_apply_slas_stub__mutmut_5, 
    'x_apply_slas_stub__mutmut_6': x_apply_slas_stub__mutmut_6, 
    'x_apply_slas_stub__mutmut_7': x_apply_slas_stub__mutmut_7, 
    'x_apply_slas_stub__mutmut_8': x_apply_slas_stub__mutmut_8, 
    'x_apply_slas_stub__mutmut_9': x_apply_slas_stub__mutmut_9, 
    'x_apply_slas_stub__mutmut_10': x_apply_slas_stub__mutmut_10, 
    'x_apply_slas_stub__mutmut_11': x_apply_slas_stub__mutmut_11, 
    'x_apply_slas_stub__mutmut_12': x_apply_slas_stub__mutmut_12, 
    'x_apply_slas_stub__mutmut_13': x_apply_slas_stub__mutmut_13, 
    'x_apply_slas_stub__mutmut_14': x_apply_slas_stub__mutmut_14, 
    'x_apply_slas_stub__mutmut_15': x_apply_slas_stub__mutmut_15, 
    'x_apply_slas_stub__mutmut_16': x_apply_slas_stub__mutmut_16, 
    'x_apply_slas_stub__mutmut_17': x_apply_slas_stub__mutmut_17, 
    'x_apply_slas_stub__mutmut_18': x_apply_slas_stub__mutmut_18, 
    'x_apply_slas_stub__mutmut_19': x_apply_slas_stub__mutmut_19, 
    'x_apply_slas_stub__mutmut_20': x_apply_slas_stub__mutmut_20, 
    'x_apply_slas_stub__mutmut_21': x_apply_slas_stub__mutmut_21, 
    'x_apply_slas_stub__mutmut_22': x_apply_slas_stub__mutmut_22, 
    'x_apply_slas_stub__mutmut_23': x_apply_slas_stub__mutmut_23, 
    'x_apply_slas_stub__mutmut_24': x_apply_slas_stub__mutmut_24, 
    'x_apply_slas_stub__mutmut_25': x_apply_slas_stub__mutmut_25, 
    'x_apply_slas_stub__mutmut_26': x_apply_slas_stub__mutmut_26, 
    'x_apply_slas_stub__mutmut_27': x_apply_slas_stub__mutmut_27, 
    'x_apply_slas_stub__mutmut_28': x_apply_slas_stub__mutmut_28, 
    'x_apply_slas_stub__mutmut_29': x_apply_slas_stub__mutmut_29, 
    'x_apply_slas_stub__mutmut_30': x_apply_slas_stub__mutmut_30, 
    'x_apply_slas_stub__mutmut_31': x_apply_slas_stub__mutmut_31, 
    'x_apply_slas_stub__mutmut_32': x_apply_slas_stub__mutmut_32, 
    'x_apply_slas_stub__mutmut_33': x_apply_slas_stub__mutmut_33, 
    'x_apply_slas_stub__mutmut_34': x_apply_slas_stub__mutmut_34, 
    'x_apply_slas_stub__mutmut_35': x_apply_slas_stub__mutmut_35, 
    'x_apply_slas_stub__mutmut_36': x_apply_slas_stub__mutmut_36, 
    'x_apply_slas_stub__mutmut_37': x_apply_slas_stub__mutmut_37, 
    'x_apply_slas_stub__mutmut_38': x_apply_slas_stub__mutmut_38, 
    'x_apply_slas_stub__mutmut_39': x_apply_slas_stub__mutmut_39, 
    'x_apply_slas_stub__mutmut_40': x_apply_slas_stub__mutmut_40, 
    'x_apply_slas_stub__mutmut_41': x_apply_slas_stub__mutmut_41, 
    'x_apply_slas_stub__mutmut_42': x_apply_slas_stub__mutmut_42, 
    'x_apply_slas_stub__mutmut_43': x_apply_slas_stub__mutmut_43, 
    'x_apply_slas_stub__mutmut_44': x_apply_slas_stub__mutmut_44, 
    'x_apply_slas_stub__mutmut_45': x_apply_slas_stub__mutmut_45, 
    'x_apply_slas_stub__mutmut_46': x_apply_slas_stub__mutmut_46, 
    'x_apply_slas_stub__mutmut_47': x_apply_slas_stub__mutmut_47, 
    'x_apply_slas_stub__mutmut_48': x_apply_slas_stub__mutmut_48, 
    'x_apply_slas_stub__mutmut_49': x_apply_slas_stub__mutmut_49, 
    'x_apply_slas_stub__mutmut_50': x_apply_slas_stub__mutmut_50, 
    'x_apply_slas_stub__mutmut_51': x_apply_slas_stub__mutmut_51, 
    'x_apply_slas_stub__mutmut_52': x_apply_slas_stub__mutmut_52, 
    'x_apply_slas_stub__mutmut_53': x_apply_slas_stub__mutmut_53, 
    'x_apply_slas_stub__mutmut_54': x_apply_slas_stub__mutmut_54, 
    'x_apply_slas_stub__mutmut_55': x_apply_slas_stub__mutmut_55, 
    'x_apply_slas_stub__mutmut_56': x_apply_slas_stub__mutmut_56, 
    'x_apply_slas_stub__mutmut_57': x_apply_slas_stub__mutmut_57, 
    'x_apply_slas_stub__mutmut_58': x_apply_slas_stub__mutmut_58, 
    'x_apply_slas_stub__mutmut_59': x_apply_slas_stub__mutmut_59, 
    'x_apply_slas_stub__mutmut_60': x_apply_slas_stub__mutmut_60, 
    'x_apply_slas_stub__mutmut_61': x_apply_slas_stub__mutmut_61, 
    'x_apply_slas_stub__mutmut_62': x_apply_slas_stub__mutmut_62, 
    'x_apply_slas_stub__mutmut_63': x_apply_slas_stub__mutmut_63, 
    'x_apply_slas_stub__mutmut_64': x_apply_slas_stub__mutmut_64, 
    'x_apply_slas_stub__mutmut_65': x_apply_slas_stub__mutmut_65, 
    'x_apply_slas_stub__mutmut_66': x_apply_slas_stub__mutmut_66, 
    'x_apply_slas_stub__mutmut_67': x_apply_slas_stub__mutmut_67, 
    'x_apply_slas_stub__mutmut_68': x_apply_slas_stub__mutmut_68, 
    'x_apply_slas_stub__mutmut_69': x_apply_slas_stub__mutmut_69, 
    'x_apply_slas_stub__mutmut_70': x_apply_slas_stub__mutmut_70, 
    'x_apply_slas_stub__mutmut_71': x_apply_slas_stub__mutmut_71, 
    'x_apply_slas_stub__mutmut_72': x_apply_slas_stub__mutmut_72, 
    'x_apply_slas_stub__mutmut_73': x_apply_slas_stub__mutmut_73, 
    'x_apply_slas_stub__mutmut_74': x_apply_slas_stub__mutmut_74, 
    'x_apply_slas_stub__mutmut_75': x_apply_slas_stub__mutmut_75, 
    'x_apply_slas_stub__mutmut_76': x_apply_slas_stub__mutmut_76, 
    'x_apply_slas_stub__mutmut_77': x_apply_slas_stub__mutmut_77, 
    'x_apply_slas_stub__mutmut_78': x_apply_slas_stub__mutmut_78, 
    'x_apply_slas_stub__mutmut_79': x_apply_slas_stub__mutmut_79, 
    'x_apply_slas_stub__mutmut_80': x_apply_slas_stub__mutmut_80, 
    'x_apply_slas_stub__mutmut_81': x_apply_slas_stub__mutmut_81, 
    'x_apply_slas_stub__mutmut_82': x_apply_slas_stub__mutmut_82, 
    'x_apply_slas_stub__mutmut_83': x_apply_slas_stub__mutmut_83, 
    'x_apply_slas_stub__mutmut_84': x_apply_slas_stub__mutmut_84, 
    'x_apply_slas_stub__mutmut_85': x_apply_slas_stub__mutmut_85, 
    'x_apply_slas_stub__mutmut_86': x_apply_slas_stub__mutmut_86, 
    'x_apply_slas_stub__mutmut_87': x_apply_slas_stub__mutmut_87, 
    'x_apply_slas_stub__mutmut_88': x_apply_slas_stub__mutmut_88, 
    'x_apply_slas_stub__mutmut_89': x_apply_slas_stub__mutmut_89, 
    'x_apply_slas_stub__mutmut_90': x_apply_slas_stub__mutmut_90, 
    'x_apply_slas_stub__mutmut_91': x_apply_slas_stub__mutmut_91, 
    'x_apply_slas_stub__mutmut_92': x_apply_slas_stub__mutmut_92, 
    'x_apply_slas_stub__mutmut_93': x_apply_slas_stub__mutmut_93, 
    'x_apply_slas_stub__mutmut_94': x_apply_slas_stub__mutmut_94, 
    'x_apply_slas_stub__mutmut_95': x_apply_slas_stub__mutmut_95, 
    'x_apply_slas_stub__mutmut_96': x_apply_slas_stub__mutmut_96, 
    'x_apply_slas_stub__mutmut_97': x_apply_slas_stub__mutmut_97, 
    'x_apply_slas_stub__mutmut_98': x_apply_slas_stub__mutmut_98, 
    'x_apply_slas_stub__mutmut_99': x_apply_slas_stub__mutmut_99, 
    'x_apply_slas_stub__mutmut_100': x_apply_slas_stub__mutmut_100, 
    'x_apply_slas_stub__mutmut_101': x_apply_slas_stub__mutmut_101, 
    'x_apply_slas_stub__mutmut_102': x_apply_slas_stub__mutmut_102
}

def apply_slas_stub(*args, **kwargs):
    result = _mutmut_trampoline(x_apply_slas_stub__mutmut_orig, x_apply_slas_stub__mutmut_mutants, args, kwargs)
    return result 

apply_slas_stub.__signature__ = _mutmut_signature(x_apply_slas_stub__mutmut_orig)
x_apply_slas_stub__mutmut_orig.__name__ = 'x_apply_slas_stub'


def x_apply_routing_stub__mutmut_orig(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_1(plan: Any, dry_run: bool = False) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_2(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = None
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_3(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(None)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_4(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = None
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_5(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "XXresourceXX": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_6(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "RESOURCE": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_7(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "XXroutingruleXX",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_8(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "ROUTINGRULE",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_9(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "XXprocessedXX": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_10(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "PROCESSED": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_11(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 1,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_12(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "XXcreatedXX": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_13(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "CREATED": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_14(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 1,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_15(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "XXupdatedXX": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_16(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "UPDATED": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_17(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 1,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_18(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "XXdeletedXX": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_19(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "DELETED": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_20(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 1,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_21(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "XXdry_runXX": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_22(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "DRY_RUN": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_23(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = None
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_24(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(None)
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_25(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") and entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_26(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get(None) or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_27(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("XXactionXX") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_28(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("ACTION") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_29(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get(None))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_30(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("XXopXX"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_31(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("OP"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_32(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = None
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_33(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") and {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_34(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") and entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_35(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get(None) or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_36(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("XXdataXX") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_37(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("DATA") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_38(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get(None) or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_39(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("XXvalueXX") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_40(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("VALUE") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_41(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = None
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_42(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") and _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_43(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get(None) or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_44(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("XXnameXX") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_45(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("NAME") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_46(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(None)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_47(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            None,
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_48(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            None,
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_49(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_50(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_51(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "XXd365_routing.jsonlXX",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_52(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "D365_ROUTING.JSONL",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_53(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "XXresourceXX": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_54(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "RESOURCE": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_55(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "XXroutingruleXX",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_56(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "ROUTINGRULE",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_57(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "XXactionXX": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_58(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "ACTION": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_59(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "XXtargetXX": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_60(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "TARGET": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_61(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "XXnameXX": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_62(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "NAME": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_63(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "XXlogical_entityXX": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_64(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "LOGICAL_ENTITY": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_65(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "XXroutingruleXX",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_66(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "ROUTINGRULE",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_67(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "XXdry_runXX": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_68(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "DRY_RUN": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_69(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "XXdataXX": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_70(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "DATA": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_71(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] = 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_72(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] -= 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_73(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["XXprocessedXX"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_74(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["PROCESSED"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_75(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 2
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_76(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action != "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_77(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "XXCreateXX":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_78(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_79(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "CREATE":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_80(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] = 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_81(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] -= 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_82(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["XXcreatedXX"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_83(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["CREATED"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_84(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 2
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_85(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action != "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_86(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "XXUpdateXX":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_87(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_88(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "UPDATE":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_89(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] = 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_90(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] -= 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_91(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["XXupdatedXX"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_92(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["UPDATED"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_93(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 2
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_94(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action != "Delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_95(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "XXDeleteXX":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_96(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "delete":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_97(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "DELETE":
            summary["deleted"] += 1
    return summary


def x_apply_routing_stub__mutmut_98(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] = 1
    return summary


def x_apply_routing_stub__mutmut_99(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] -= 1
    return summary


def x_apply_routing_stub__mutmut_100(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["XXdeletedXX"] += 1
    return summary


def x_apply_routing_stub__mutmut_101(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["DELETED"] += 1
    return summary


def x_apply_routing_stub__mutmut_102(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 2
    return summary

x_apply_routing_stub__mutmut_mutants : ClassVar[MutantDict] = {
'x_apply_routing_stub__mutmut_1': x_apply_routing_stub__mutmut_1, 
    'x_apply_routing_stub__mutmut_2': x_apply_routing_stub__mutmut_2, 
    'x_apply_routing_stub__mutmut_3': x_apply_routing_stub__mutmut_3, 
    'x_apply_routing_stub__mutmut_4': x_apply_routing_stub__mutmut_4, 
    'x_apply_routing_stub__mutmut_5': x_apply_routing_stub__mutmut_5, 
    'x_apply_routing_stub__mutmut_6': x_apply_routing_stub__mutmut_6, 
    'x_apply_routing_stub__mutmut_7': x_apply_routing_stub__mutmut_7, 
    'x_apply_routing_stub__mutmut_8': x_apply_routing_stub__mutmut_8, 
    'x_apply_routing_stub__mutmut_9': x_apply_routing_stub__mutmut_9, 
    'x_apply_routing_stub__mutmut_10': x_apply_routing_stub__mutmut_10, 
    'x_apply_routing_stub__mutmut_11': x_apply_routing_stub__mutmut_11, 
    'x_apply_routing_stub__mutmut_12': x_apply_routing_stub__mutmut_12, 
    'x_apply_routing_stub__mutmut_13': x_apply_routing_stub__mutmut_13, 
    'x_apply_routing_stub__mutmut_14': x_apply_routing_stub__mutmut_14, 
    'x_apply_routing_stub__mutmut_15': x_apply_routing_stub__mutmut_15, 
    'x_apply_routing_stub__mutmut_16': x_apply_routing_stub__mutmut_16, 
    'x_apply_routing_stub__mutmut_17': x_apply_routing_stub__mutmut_17, 
    'x_apply_routing_stub__mutmut_18': x_apply_routing_stub__mutmut_18, 
    'x_apply_routing_stub__mutmut_19': x_apply_routing_stub__mutmut_19, 
    'x_apply_routing_stub__mutmut_20': x_apply_routing_stub__mutmut_20, 
    'x_apply_routing_stub__mutmut_21': x_apply_routing_stub__mutmut_21, 
    'x_apply_routing_stub__mutmut_22': x_apply_routing_stub__mutmut_22, 
    'x_apply_routing_stub__mutmut_23': x_apply_routing_stub__mutmut_23, 
    'x_apply_routing_stub__mutmut_24': x_apply_routing_stub__mutmut_24, 
    'x_apply_routing_stub__mutmut_25': x_apply_routing_stub__mutmut_25, 
    'x_apply_routing_stub__mutmut_26': x_apply_routing_stub__mutmut_26, 
    'x_apply_routing_stub__mutmut_27': x_apply_routing_stub__mutmut_27, 
    'x_apply_routing_stub__mutmut_28': x_apply_routing_stub__mutmut_28, 
    'x_apply_routing_stub__mutmut_29': x_apply_routing_stub__mutmut_29, 
    'x_apply_routing_stub__mutmut_30': x_apply_routing_stub__mutmut_30, 
    'x_apply_routing_stub__mutmut_31': x_apply_routing_stub__mutmut_31, 
    'x_apply_routing_stub__mutmut_32': x_apply_routing_stub__mutmut_32, 
    'x_apply_routing_stub__mutmut_33': x_apply_routing_stub__mutmut_33, 
    'x_apply_routing_stub__mutmut_34': x_apply_routing_stub__mutmut_34, 
    'x_apply_routing_stub__mutmut_35': x_apply_routing_stub__mutmut_35, 
    'x_apply_routing_stub__mutmut_36': x_apply_routing_stub__mutmut_36, 
    'x_apply_routing_stub__mutmut_37': x_apply_routing_stub__mutmut_37, 
    'x_apply_routing_stub__mutmut_38': x_apply_routing_stub__mutmut_38, 
    'x_apply_routing_stub__mutmut_39': x_apply_routing_stub__mutmut_39, 
    'x_apply_routing_stub__mutmut_40': x_apply_routing_stub__mutmut_40, 
    'x_apply_routing_stub__mutmut_41': x_apply_routing_stub__mutmut_41, 
    'x_apply_routing_stub__mutmut_42': x_apply_routing_stub__mutmut_42, 
    'x_apply_routing_stub__mutmut_43': x_apply_routing_stub__mutmut_43, 
    'x_apply_routing_stub__mutmut_44': x_apply_routing_stub__mutmut_44, 
    'x_apply_routing_stub__mutmut_45': x_apply_routing_stub__mutmut_45, 
    'x_apply_routing_stub__mutmut_46': x_apply_routing_stub__mutmut_46, 
    'x_apply_routing_stub__mutmut_47': x_apply_routing_stub__mutmut_47, 
    'x_apply_routing_stub__mutmut_48': x_apply_routing_stub__mutmut_48, 
    'x_apply_routing_stub__mutmut_49': x_apply_routing_stub__mutmut_49, 
    'x_apply_routing_stub__mutmut_50': x_apply_routing_stub__mutmut_50, 
    'x_apply_routing_stub__mutmut_51': x_apply_routing_stub__mutmut_51, 
    'x_apply_routing_stub__mutmut_52': x_apply_routing_stub__mutmut_52, 
    'x_apply_routing_stub__mutmut_53': x_apply_routing_stub__mutmut_53, 
    'x_apply_routing_stub__mutmut_54': x_apply_routing_stub__mutmut_54, 
    'x_apply_routing_stub__mutmut_55': x_apply_routing_stub__mutmut_55, 
    'x_apply_routing_stub__mutmut_56': x_apply_routing_stub__mutmut_56, 
    'x_apply_routing_stub__mutmut_57': x_apply_routing_stub__mutmut_57, 
    'x_apply_routing_stub__mutmut_58': x_apply_routing_stub__mutmut_58, 
    'x_apply_routing_stub__mutmut_59': x_apply_routing_stub__mutmut_59, 
    'x_apply_routing_stub__mutmut_60': x_apply_routing_stub__mutmut_60, 
    'x_apply_routing_stub__mutmut_61': x_apply_routing_stub__mutmut_61, 
    'x_apply_routing_stub__mutmut_62': x_apply_routing_stub__mutmut_62, 
    'x_apply_routing_stub__mutmut_63': x_apply_routing_stub__mutmut_63, 
    'x_apply_routing_stub__mutmut_64': x_apply_routing_stub__mutmut_64, 
    'x_apply_routing_stub__mutmut_65': x_apply_routing_stub__mutmut_65, 
    'x_apply_routing_stub__mutmut_66': x_apply_routing_stub__mutmut_66, 
    'x_apply_routing_stub__mutmut_67': x_apply_routing_stub__mutmut_67, 
    'x_apply_routing_stub__mutmut_68': x_apply_routing_stub__mutmut_68, 
    'x_apply_routing_stub__mutmut_69': x_apply_routing_stub__mutmut_69, 
    'x_apply_routing_stub__mutmut_70': x_apply_routing_stub__mutmut_70, 
    'x_apply_routing_stub__mutmut_71': x_apply_routing_stub__mutmut_71, 
    'x_apply_routing_stub__mutmut_72': x_apply_routing_stub__mutmut_72, 
    'x_apply_routing_stub__mutmut_73': x_apply_routing_stub__mutmut_73, 
    'x_apply_routing_stub__mutmut_74': x_apply_routing_stub__mutmut_74, 
    'x_apply_routing_stub__mutmut_75': x_apply_routing_stub__mutmut_75, 
    'x_apply_routing_stub__mutmut_76': x_apply_routing_stub__mutmut_76, 
    'x_apply_routing_stub__mutmut_77': x_apply_routing_stub__mutmut_77, 
    'x_apply_routing_stub__mutmut_78': x_apply_routing_stub__mutmut_78, 
    'x_apply_routing_stub__mutmut_79': x_apply_routing_stub__mutmut_79, 
    'x_apply_routing_stub__mutmut_80': x_apply_routing_stub__mutmut_80, 
    'x_apply_routing_stub__mutmut_81': x_apply_routing_stub__mutmut_81, 
    'x_apply_routing_stub__mutmut_82': x_apply_routing_stub__mutmut_82, 
    'x_apply_routing_stub__mutmut_83': x_apply_routing_stub__mutmut_83, 
    'x_apply_routing_stub__mutmut_84': x_apply_routing_stub__mutmut_84, 
    'x_apply_routing_stub__mutmut_85': x_apply_routing_stub__mutmut_85, 
    'x_apply_routing_stub__mutmut_86': x_apply_routing_stub__mutmut_86, 
    'x_apply_routing_stub__mutmut_87': x_apply_routing_stub__mutmut_87, 
    'x_apply_routing_stub__mutmut_88': x_apply_routing_stub__mutmut_88, 
    'x_apply_routing_stub__mutmut_89': x_apply_routing_stub__mutmut_89, 
    'x_apply_routing_stub__mutmut_90': x_apply_routing_stub__mutmut_90, 
    'x_apply_routing_stub__mutmut_91': x_apply_routing_stub__mutmut_91, 
    'x_apply_routing_stub__mutmut_92': x_apply_routing_stub__mutmut_92, 
    'x_apply_routing_stub__mutmut_93': x_apply_routing_stub__mutmut_93, 
    'x_apply_routing_stub__mutmut_94': x_apply_routing_stub__mutmut_94, 
    'x_apply_routing_stub__mutmut_95': x_apply_routing_stub__mutmut_95, 
    'x_apply_routing_stub__mutmut_96': x_apply_routing_stub__mutmut_96, 
    'x_apply_routing_stub__mutmut_97': x_apply_routing_stub__mutmut_97, 
    'x_apply_routing_stub__mutmut_98': x_apply_routing_stub__mutmut_98, 
    'x_apply_routing_stub__mutmut_99': x_apply_routing_stub__mutmut_99, 
    'x_apply_routing_stub__mutmut_100': x_apply_routing_stub__mutmut_100, 
    'x_apply_routing_stub__mutmut_101': x_apply_routing_stub__mutmut_101, 
    'x_apply_routing_stub__mutmut_102': x_apply_routing_stub__mutmut_102
}

def apply_routing_stub(*args, **kwargs):
    result = _mutmut_trampoline(x_apply_routing_stub__mutmut_orig, x_apply_routing_stub__mutmut_mutants, args, kwargs)
    return result 

apply_routing_stub.__signature__ = _mutmut_signature(x_apply_routing_stub__mutmut_orig)
x_apply_routing_stub__mutmut_orig.__name__ = 'x_apply_routing_stub'


def x__extract_target_name__mutmut_orig(entry: Mapping[str, Any]) -> str:
    path = entry.get("path") if isinstance(entry, Mapping) else None
    if isinstance(path, str) and path:
        segment = path.rstrip("/").split("/")[-1]
        if segment:
            return segment
    return ""


def x__extract_target_name__mutmut_1(entry: Mapping[str, Any]) -> str:
    path = None
    if isinstance(path, str) and path:
        segment = path.rstrip("/").split("/")[-1]
        if segment:
            return segment
    return ""


def x__extract_target_name__mutmut_2(entry: Mapping[str, Any]) -> str:
    path = entry.get(None) if isinstance(entry, Mapping) else None
    if isinstance(path, str) and path:
        segment = path.rstrip("/").split("/")[-1]
        if segment:
            return segment
    return ""


def x__extract_target_name__mutmut_3(entry: Mapping[str, Any]) -> str:
    path = entry.get("XXpathXX") if isinstance(entry, Mapping) else None
    if isinstance(path, str) and path:
        segment = path.rstrip("/").split("/")[-1]
        if segment:
            return segment
    return ""


def x__extract_target_name__mutmut_4(entry: Mapping[str, Any]) -> str:
    path = entry.get("PATH") if isinstance(entry, Mapping) else None
    if isinstance(path, str) and path:
        segment = path.rstrip("/").split("/")[-1]
        if segment:
            return segment
    return ""


def x__extract_target_name__mutmut_5(entry: Mapping[str, Any]) -> str:
    path = entry.get("path") if isinstance(entry, Mapping) else None
    if isinstance(path, str) or path:
        segment = path.rstrip("/").split("/")[-1]
        if segment:
            return segment
    return ""


def x__extract_target_name__mutmut_6(entry: Mapping[str, Any]) -> str:
    path = entry.get("path") if isinstance(entry, Mapping) else None
    if isinstance(path, str) and path:
        segment = None
        if segment:
            return segment
    return ""


def x__extract_target_name__mutmut_7(entry: Mapping[str, Any]) -> str:
    path = entry.get("path") if isinstance(entry, Mapping) else None
    if isinstance(path, str) and path:
        segment = path.rstrip("/").split(None)[-1]
        if segment:
            return segment
    return ""


def x__extract_target_name__mutmut_8(entry: Mapping[str, Any]) -> str:
    path = entry.get("path") if isinstance(entry, Mapping) else None
    if isinstance(path, str) and path:
        segment = path.rstrip(None).split("/")[-1]
        if segment:
            return segment
    return ""


def x__extract_target_name__mutmut_9(entry: Mapping[str, Any]) -> str:
    path = entry.get("path") if isinstance(entry, Mapping) else None
    if isinstance(path, str) and path:
        segment = path.lstrip("/").split("/")[-1]
        if segment:
            return segment
    return ""


def x__extract_target_name__mutmut_10(entry: Mapping[str, Any]) -> str:
    path = entry.get("path") if isinstance(entry, Mapping) else None
    if isinstance(path, str) and path:
        segment = path.rstrip("XX/XX").split("/")[-1]
        if segment:
            return segment
    return ""


def x__extract_target_name__mutmut_11(entry: Mapping[str, Any]) -> str:
    path = entry.get("path") if isinstance(entry, Mapping) else None
    if isinstance(path, str) and path:
        segment = path.rstrip("/").split("XX/XX")[-1]
        if segment:
            return segment
    return ""


def x__extract_target_name__mutmut_12(entry: Mapping[str, Any]) -> str:
    path = entry.get("path") if isinstance(entry, Mapping) else None
    if isinstance(path, str) and path:
        segment = path.rstrip("/").split("/")[+1]
        if segment:
            return segment
    return ""


def x__extract_target_name__mutmut_13(entry: Mapping[str, Any]) -> str:
    path = entry.get("path") if isinstance(entry, Mapping) else None
    if isinstance(path, str) and path:
        segment = path.rstrip("/").split("/")[-2]
        if segment:
            return segment
    return ""


def x__extract_target_name__mutmut_14(entry: Mapping[str, Any]) -> str:
    path = entry.get("path") if isinstance(entry, Mapping) else None
    if isinstance(path, str) and path:
        segment = path.rstrip("/").split("/")[-1]
        if segment:
            return segment
    return "XXXX"

x__extract_target_name__mutmut_mutants : ClassVar[MutantDict] = {
'x__extract_target_name__mutmut_1': x__extract_target_name__mutmut_1, 
    'x__extract_target_name__mutmut_2': x__extract_target_name__mutmut_2, 
    'x__extract_target_name__mutmut_3': x__extract_target_name__mutmut_3, 
    'x__extract_target_name__mutmut_4': x__extract_target_name__mutmut_4, 
    'x__extract_target_name__mutmut_5': x__extract_target_name__mutmut_5, 
    'x__extract_target_name__mutmut_6': x__extract_target_name__mutmut_6, 
    'x__extract_target_name__mutmut_7': x__extract_target_name__mutmut_7, 
    'x__extract_target_name__mutmut_8': x__extract_target_name__mutmut_8, 
    'x__extract_target_name__mutmut_9': x__extract_target_name__mutmut_9, 
    'x__extract_target_name__mutmut_10': x__extract_target_name__mutmut_10, 
    'x__extract_target_name__mutmut_11': x__extract_target_name__mutmut_11, 
    'x__extract_target_name__mutmut_12': x__extract_target_name__mutmut_12, 
    'x__extract_target_name__mutmut_13': x__extract_target_name__mutmut_13, 
    'x__extract_target_name__mutmut_14': x__extract_target_name__mutmut_14
}

def _extract_target_name(*args, **kwargs):
    result = _mutmut_trampoline(x__extract_target_name__mutmut_orig, x__extract_target_name__mutmut_mutants, args, kwargs)
    return result 

_extract_target_name.__signature__ = _mutmut_signature(x__extract_target_name__mutmut_orig)
x__extract_target_name__mutmut_orig.__name__ = 'x__extract_target_name'
