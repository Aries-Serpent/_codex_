"""
Golden Harness Status Module

This module provides functionality for golden harness status.

Usage:
    from codex_harness.golden_harness_status import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_STATUS_PASS = {"pass", "passed", "ok", "success", "green", "approved", "true", "1", "yes"}
_STATUS_FAIL = {"fail", "failed", "block", "blocked", "reject", "red", "false", "0", "no"}
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
class HarnessSignal:
    name: str
    status: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "status": self.status, "detail": self.detail}


def x__utc_now__mutmut_orig() -> str:
    return datetime.now(timezone.utc).isoformat()


def x__utc_now__mutmut_1() -> str:
    return datetime.now(None).isoformat()

x__utc_now__mutmut_mutants : ClassVar[MutantDict] = {
'x__utc_now__mutmut_1': x__utc_now__mutmut_1
}

def _utc_now(*args, **kwargs):
    result = _mutmut_trampoline(x__utc_now__mutmut_orig, x__utc_now__mutmut_mutants, args, kwargs)
    return result 

_utc_now.__signature__ = _mutmut_signature(x__utc_now__mutmut_orig)
x__utc_now__mutmut_orig.__name__ = 'x__utc_now'


def x__normalize_status__mutmut_orig(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    lowered = str(value).lower()
    if lowered in _STATUS_PASS:
        return True
    if lowered in _STATUS_FAIL:
        return False
    return None


def x__normalize_status__mutmut_1(value: Any) -> bool | None:
    if value is not None:
        return None
    if isinstance(value, bool):
        return value
    lowered = str(value).lower()
    if lowered in _STATUS_PASS:
        return True
    if lowered in _STATUS_FAIL:
        return False
    return None


def x__normalize_status__mutmut_2(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    lowered = None
    if lowered in _STATUS_PASS:
        return True
    if lowered in _STATUS_FAIL:
        return False
    return None


def x__normalize_status__mutmut_3(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    lowered = str(value).upper()
    if lowered in _STATUS_PASS:
        return True
    if lowered in _STATUS_FAIL:
        return False
    return None


def x__normalize_status__mutmut_4(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    lowered = str(None).lower()
    if lowered in _STATUS_PASS:
        return True
    if lowered in _STATUS_FAIL:
        return False
    return None


def x__normalize_status__mutmut_5(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    lowered = str(value).lower()
    if lowered not in _STATUS_PASS:
        return True
    if lowered in _STATUS_FAIL:
        return False
    return None


def x__normalize_status__mutmut_6(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    lowered = str(value).lower()
    if lowered in _STATUS_PASS:
        return False
    if lowered in _STATUS_FAIL:
        return False
    return None


def x__normalize_status__mutmut_7(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    lowered = str(value).lower()
    if lowered in _STATUS_PASS:
        return True
    if lowered not in _STATUS_FAIL:
        return False
    return None


def x__normalize_status__mutmut_8(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    lowered = str(value).lower()
    if lowered in _STATUS_PASS:
        return True
    if lowered in _STATUS_FAIL:
        return True
    return None

x__normalize_status__mutmut_mutants : ClassVar[MutantDict] = {
'x__normalize_status__mutmut_1': x__normalize_status__mutmut_1, 
    'x__normalize_status__mutmut_2': x__normalize_status__mutmut_2, 
    'x__normalize_status__mutmut_3': x__normalize_status__mutmut_3, 
    'x__normalize_status__mutmut_4': x__normalize_status__mutmut_4, 
    'x__normalize_status__mutmut_5': x__normalize_status__mutmut_5, 
    'x__normalize_status__mutmut_6': x__normalize_status__mutmut_6, 
    'x__normalize_status__mutmut_7': x__normalize_status__mutmut_7, 
    'x__normalize_status__mutmut_8': x__normalize_status__mutmut_8
}

def _normalize_status(*args, **kwargs):
    result = _mutmut_trampoline(x__normalize_status__mutmut_orig, x__normalize_status__mutmut_mutants, args, kwargs)
    return result 

_normalize_status.__signature__ = _mutmut_signature(x__normalize_status__mutmut_orig)
x__normalize_status__mutmut_orig.__name__ = 'x__normalize_status'


def x__load_json_if_exists__mutmut_orig(path: Path) -> Any:
    if not path or not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def x__load_json_if_exists__mutmut_1(path: Path) -> Any:
    if not path and not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def x__load_json_if_exists__mutmut_2(path: Path) -> Any:
    if path or not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def x__load_json_if_exists__mutmut_3(path: Path) -> Any:
    if not path or path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def x__load_json_if_exists__mutmut_4(path: Path) -> Any:
    if not path or not path.exists():
        return None
    with path.open(None, encoding="utf-8") as handle:
        return json.load(handle)


def x__load_json_if_exists__mutmut_5(path: Path) -> Any:
    if not path or not path.exists():
        return None
    with path.open("r", encoding=None) as handle:
        return json.load(handle)


def x__load_json_if_exists__mutmut_6(path: Path) -> Any:
    if not path or not path.exists():
        return None
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def x__load_json_if_exists__mutmut_7(path: Path) -> Any:
    if not path or not path.exists():
        return None
    with path.open("r", ) as handle:
        return json.load(handle)


def x__load_json_if_exists__mutmut_8(path: Path) -> Any:
    if not path or not path.exists():
        return None
    with path.open("XXrXX", encoding="utf-8") as handle:
        return json.load(handle)


def x__load_json_if_exists__mutmut_9(path: Path) -> Any:
    if not path or not path.exists():
        return None
    with path.open("R", encoding="utf-8") as handle:
        return json.load(handle)


def x__load_json_if_exists__mutmut_10(path: Path) -> Any:
    if not path or not path.exists():
        return None
    with path.open("r", encoding="XXutf-8XX") as handle:
        return json.load(handle)


def x__load_json_if_exists__mutmut_11(path: Path) -> Any:
    if not path or not path.exists():
        return None
    with path.open("r", encoding="UTF-8") as handle:
        return json.load(handle)


def x__load_json_if_exists__mutmut_12(path: Path) -> Any:
    if not path or not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(None)

x__load_json_if_exists__mutmut_mutants : ClassVar[MutantDict] = {
'x__load_json_if_exists__mutmut_1': x__load_json_if_exists__mutmut_1, 
    'x__load_json_if_exists__mutmut_2': x__load_json_if_exists__mutmut_2, 
    'x__load_json_if_exists__mutmut_3': x__load_json_if_exists__mutmut_3, 
    'x__load_json_if_exists__mutmut_4': x__load_json_if_exists__mutmut_4, 
    'x__load_json_if_exists__mutmut_5': x__load_json_if_exists__mutmut_5, 
    'x__load_json_if_exists__mutmut_6': x__load_json_if_exists__mutmut_6, 
    'x__load_json_if_exists__mutmut_7': x__load_json_if_exists__mutmut_7, 
    'x__load_json_if_exists__mutmut_8': x__load_json_if_exists__mutmut_8, 
    'x__load_json_if_exists__mutmut_9': x__load_json_if_exists__mutmut_9, 
    'x__load_json_if_exists__mutmut_10': x__load_json_if_exists__mutmut_10, 
    'x__load_json_if_exists__mutmut_11': x__load_json_if_exists__mutmut_11, 
    'x__load_json_if_exists__mutmut_12': x__load_json_if_exists__mutmut_12
}

def _load_json_if_exists(*args, **kwargs):
    result = _mutmut_trampoline(x__load_json_if_exists__mutmut_orig, x__load_json_if_exists__mutmut_mutants, args, kwargs)
    return result 

_load_json_if_exists.__signature__ = _mutmut_signature(x__load_json_if_exists__mutmut_orig)
x__load_json_if_exists__mutmut_orig.__name__ = 'x__load_json_if_exists'


def x__evaluate_ra_policy__mutmut_orig(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_1(policy: Any) -> HarnessSignal:
    if policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_2(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name=None,
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_3(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status=None,
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_4(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail=None,
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_5(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_6(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_7(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_8(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="XXra_policyXX",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_9(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="RA_POLICY",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_10(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="XXyellowXX",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_11(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="YELLOW",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_12(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="XXResponsible AI policy outcomes missing; defaulting to caution.XX",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_13(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="responsible ai policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_14(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="RESPONSIBLE AI POLICY OUTCOMES MISSING; DEFAULTING TO CAUTION.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_15(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = None
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_16(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "XXpoliciesXX" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_17(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "POLICIES" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_18(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" not in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_19(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                None
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_20(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(None) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_21(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get(None)) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_22(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("XXstatusXX")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_23(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("STATUS")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_24(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get(None, [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_25(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", None)]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_26(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get([])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_27(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", )]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_28(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("XXpoliciesXX", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_29(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("POLICIES", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_30(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "XXresultsXX" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_31(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "RESULTS" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_32(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" not in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_33(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend(None)
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_34(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(None) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_35(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get(None)) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_36(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("XXstatusXX")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_37(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("STATUS")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_38(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get(None, [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_39(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", None)])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_40(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get([])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_41(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", )])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_42(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("XXresultsXX", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_43(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("RESULTS", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_44(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "XXstatusXX" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_45(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "STATUS" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_46(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" not in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_47(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(None)
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_48(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(None))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_49(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get(None)))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_50(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("XXstatusXX")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_51(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("STATUS")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_52(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_53(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                None
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_54(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(None) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_55(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_56(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_57(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name=None,
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_58(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status=None,
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_59(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail=None,
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_60(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_61(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_62(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_63(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="XXra_policyXX",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_64(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="RA_POLICY",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_65(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="XXyellowXX",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_66(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="YELLOW",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_67(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="XXNo normalized policy statuses found; treating as partial coverage.XX",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_68(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="no normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_69(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="NO NORMALIZED POLICY STATUSES FOUND; TREATING AS PARTIAL COVERAGE.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_70(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = None
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_71(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is not False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_72(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is True]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_73(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name=None,
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_74(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status=None,
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_75(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail=None,
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_76(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_77(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_78(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_79(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="XXra_policyXX",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_80(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="RA_POLICY",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_81(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="XXredXX",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_82(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="RED",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_83(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="XXAt least one RA gate failed.XX",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_84(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="at least one ra gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_85(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="AT LEAST ONE RA GATE FAILED.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_86(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name=None, status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_87(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status=None, detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_88(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail=None
    )


def x__evaluate_ra_policy__mutmut_89(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_90(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_91(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", )


def x__evaluate_ra_policy__mutmut_92(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="XXra_policyXX", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_93(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="RA_POLICY", status="green", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_94(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="XXgreenXX", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_95(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="GREEN", detail="RA policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_96(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="XXRA policies reported pass states.XX"
    )


def x__evaluate_ra_policy__mutmut_97(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="ra policies reported pass states."
    )


def x__evaluate_ra_policy__mutmut_98(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA POLICIES REPORTED PASS STATES."
    )

x__evaluate_ra_policy__mutmut_mutants : ClassVar[MutantDict] = {
'x__evaluate_ra_policy__mutmut_1': x__evaluate_ra_policy__mutmut_1, 
    'x__evaluate_ra_policy__mutmut_2': x__evaluate_ra_policy__mutmut_2, 
    'x__evaluate_ra_policy__mutmut_3': x__evaluate_ra_policy__mutmut_3, 
    'x__evaluate_ra_policy__mutmut_4': x__evaluate_ra_policy__mutmut_4, 
    'x__evaluate_ra_policy__mutmut_5': x__evaluate_ra_policy__mutmut_5, 
    'x__evaluate_ra_policy__mutmut_6': x__evaluate_ra_policy__mutmut_6, 
    'x__evaluate_ra_policy__mutmut_7': x__evaluate_ra_policy__mutmut_7, 
    'x__evaluate_ra_policy__mutmut_8': x__evaluate_ra_policy__mutmut_8, 
    'x__evaluate_ra_policy__mutmut_9': x__evaluate_ra_policy__mutmut_9, 
    'x__evaluate_ra_policy__mutmut_10': x__evaluate_ra_policy__mutmut_10, 
    'x__evaluate_ra_policy__mutmut_11': x__evaluate_ra_policy__mutmut_11, 
    'x__evaluate_ra_policy__mutmut_12': x__evaluate_ra_policy__mutmut_12, 
    'x__evaluate_ra_policy__mutmut_13': x__evaluate_ra_policy__mutmut_13, 
    'x__evaluate_ra_policy__mutmut_14': x__evaluate_ra_policy__mutmut_14, 
    'x__evaluate_ra_policy__mutmut_15': x__evaluate_ra_policy__mutmut_15, 
    'x__evaluate_ra_policy__mutmut_16': x__evaluate_ra_policy__mutmut_16, 
    'x__evaluate_ra_policy__mutmut_17': x__evaluate_ra_policy__mutmut_17, 
    'x__evaluate_ra_policy__mutmut_18': x__evaluate_ra_policy__mutmut_18, 
    'x__evaluate_ra_policy__mutmut_19': x__evaluate_ra_policy__mutmut_19, 
    'x__evaluate_ra_policy__mutmut_20': x__evaluate_ra_policy__mutmut_20, 
    'x__evaluate_ra_policy__mutmut_21': x__evaluate_ra_policy__mutmut_21, 
    'x__evaluate_ra_policy__mutmut_22': x__evaluate_ra_policy__mutmut_22, 
    'x__evaluate_ra_policy__mutmut_23': x__evaluate_ra_policy__mutmut_23, 
    'x__evaluate_ra_policy__mutmut_24': x__evaluate_ra_policy__mutmut_24, 
    'x__evaluate_ra_policy__mutmut_25': x__evaluate_ra_policy__mutmut_25, 
    'x__evaluate_ra_policy__mutmut_26': x__evaluate_ra_policy__mutmut_26, 
    'x__evaluate_ra_policy__mutmut_27': x__evaluate_ra_policy__mutmut_27, 
    'x__evaluate_ra_policy__mutmut_28': x__evaluate_ra_policy__mutmut_28, 
    'x__evaluate_ra_policy__mutmut_29': x__evaluate_ra_policy__mutmut_29, 
    'x__evaluate_ra_policy__mutmut_30': x__evaluate_ra_policy__mutmut_30, 
    'x__evaluate_ra_policy__mutmut_31': x__evaluate_ra_policy__mutmut_31, 
    'x__evaluate_ra_policy__mutmut_32': x__evaluate_ra_policy__mutmut_32, 
    'x__evaluate_ra_policy__mutmut_33': x__evaluate_ra_policy__mutmut_33, 
    'x__evaluate_ra_policy__mutmut_34': x__evaluate_ra_policy__mutmut_34, 
    'x__evaluate_ra_policy__mutmut_35': x__evaluate_ra_policy__mutmut_35, 
    'x__evaluate_ra_policy__mutmut_36': x__evaluate_ra_policy__mutmut_36, 
    'x__evaluate_ra_policy__mutmut_37': x__evaluate_ra_policy__mutmut_37, 
    'x__evaluate_ra_policy__mutmut_38': x__evaluate_ra_policy__mutmut_38, 
    'x__evaluate_ra_policy__mutmut_39': x__evaluate_ra_policy__mutmut_39, 
    'x__evaluate_ra_policy__mutmut_40': x__evaluate_ra_policy__mutmut_40, 
    'x__evaluate_ra_policy__mutmut_41': x__evaluate_ra_policy__mutmut_41, 
    'x__evaluate_ra_policy__mutmut_42': x__evaluate_ra_policy__mutmut_42, 
    'x__evaluate_ra_policy__mutmut_43': x__evaluate_ra_policy__mutmut_43, 
    'x__evaluate_ra_policy__mutmut_44': x__evaluate_ra_policy__mutmut_44, 
    'x__evaluate_ra_policy__mutmut_45': x__evaluate_ra_policy__mutmut_45, 
    'x__evaluate_ra_policy__mutmut_46': x__evaluate_ra_policy__mutmut_46, 
    'x__evaluate_ra_policy__mutmut_47': x__evaluate_ra_policy__mutmut_47, 
    'x__evaluate_ra_policy__mutmut_48': x__evaluate_ra_policy__mutmut_48, 
    'x__evaluate_ra_policy__mutmut_49': x__evaluate_ra_policy__mutmut_49, 
    'x__evaluate_ra_policy__mutmut_50': x__evaluate_ra_policy__mutmut_50, 
    'x__evaluate_ra_policy__mutmut_51': x__evaluate_ra_policy__mutmut_51, 
    'x__evaluate_ra_policy__mutmut_52': x__evaluate_ra_policy__mutmut_52, 
    'x__evaluate_ra_policy__mutmut_53': x__evaluate_ra_policy__mutmut_53, 
    'x__evaluate_ra_policy__mutmut_54': x__evaluate_ra_policy__mutmut_54, 
    'x__evaluate_ra_policy__mutmut_55': x__evaluate_ra_policy__mutmut_55, 
    'x__evaluate_ra_policy__mutmut_56': x__evaluate_ra_policy__mutmut_56, 
    'x__evaluate_ra_policy__mutmut_57': x__evaluate_ra_policy__mutmut_57, 
    'x__evaluate_ra_policy__mutmut_58': x__evaluate_ra_policy__mutmut_58, 
    'x__evaluate_ra_policy__mutmut_59': x__evaluate_ra_policy__mutmut_59, 
    'x__evaluate_ra_policy__mutmut_60': x__evaluate_ra_policy__mutmut_60, 
    'x__evaluate_ra_policy__mutmut_61': x__evaluate_ra_policy__mutmut_61, 
    'x__evaluate_ra_policy__mutmut_62': x__evaluate_ra_policy__mutmut_62, 
    'x__evaluate_ra_policy__mutmut_63': x__evaluate_ra_policy__mutmut_63, 
    'x__evaluate_ra_policy__mutmut_64': x__evaluate_ra_policy__mutmut_64, 
    'x__evaluate_ra_policy__mutmut_65': x__evaluate_ra_policy__mutmut_65, 
    'x__evaluate_ra_policy__mutmut_66': x__evaluate_ra_policy__mutmut_66, 
    'x__evaluate_ra_policy__mutmut_67': x__evaluate_ra_policy__mutmut_67, 
    'x__evaluate_ra_policy__mutmut_68': x__evaluate_ra_policy__mutmut_68, 
    'x__evaluate_ra_policy__mutmut_69': x__evaluate_ra_policy__mutmut_69, 
    'x__evaluate_ra_policy__mutmut_70': x__evaluate_ra_policy__mutmut_70, 
    'x__evaluate_ra_policy__mutmut_71': x__evaluate_ra_policy__mutmut_71, 
    'x__evaluate_ra_policy__mutmut_72': x__evaluate_ra_policy__mutmut_72, 
    'x__evaluate_ra_policy__mutmut_73': x__evaluate_ra_policy__mutmut_73, 
    'x__evaluate_ra_policy__mutmut_74': x__evaluate_ra_policy__mutmut_74, 
    'x__evaluate_ra_policy__mutmut_75': x__evaluate_ra_policy__mutmut_75, 
    'x__evaluate_ra_policy__mutmut_76': x__evaluate_ra_policy__mutmut_76, 
    'x__evaluate_ra_policy__mutmut_77': x__evaluate_ra_policy__mutmut_77, 
    'x__evaluate_ra_policy__mutmut_78': x__evaluate_ra_policy__mutmut_78, 
    'x__evaluate_ra_policy__mutmut_79': x__evaluate_ra_policy__mutmut_79, 
    'x__evaluate_ra_policy__mutmut_80': x__evaluate_ra_policy__mutmut_80, 
    'x__evaluate_ra_policy__mutmut_81': x__evaluate_ra_policy__mutmut_81, 
    'x__evaluate_ra_policy__mutmut_82': x__evaluate_ra_policy__mutmut_82, 
    'x__evaluate_ra_policy__mutmut_83': x__evaluate_ra_policy__mutmut_83, 
    'x__evaluate_ra_policy__mutmut_84': x__evaluate_ra_policy__mutmut_84, 
    'x__evaluate_ra_policy__mutmut_85': x__evaluate_ra_policy__mutmut_85, 
    'x__evaluate_ra_policy__mutmut_86': x__evaluate_ra_policy__mutmut_86, 
    'x__evaluate_ra_policy__mutmut_87': x__evaluate_ra_policy__mutmut_87, 
    'x__evaluate_ra_policy__mutmut_88': x__evaluate_ra_policy__mutmut_88, 
    'x__evaluate_ra_policy__mutmut_89': x__evaluate_ra_policy__mutmut_89, 
    'x__evaluate_ra_policy__mutmut_90': x__evaluate_ra_policy__mutmut_90, 
    'x__evaluate_ra_policy__mutmut_91': x__evaluate_ra_policy__mutmut_91, 
    'x__evaluate_ra_policy__mutmut_92': x__evaluate_ra_policy__mutmut_92, 
    'x__evaluate_ra_policy__mutmut_93': x__evaluate_ra_policy__mutmut_93, 
    'x__evaluate_ra_policy__mutmut_94': x__evaluate_ra_policy__mutmut_94, 
    'x__evaluate_ra_policy__mutmut_95': x__evaluate_ra_policy__mutmut_95, 
    'x__evaluate_ra_policy__mutmut_96': x__evaluate_ra_policy__mutmut_96, 
    'x__evaluate_ra_policy__mutmut_97': x__evaluate_ra_policy__mutmut_97, 
    'x__evaluate_ra_policy__mutmut_98': x__evaluate_ra_policy__mutmut_98
}

def _evaluate_ra_policy(*args, **kwargs):
    result = _mutmut_trampoline(x__evaluate_ra_policy__mutmut_orig, x__evaluate_ra_policy__mutmut_mutants, args, kwargs)
    return result 

_evaluate_ra_policy.__signature__ = _mutmut_signature(x__evaluate_ra_policy__mutmut_orig)
x__evaluate_ra_policy__mutmut_orig.__name__ = 'x__evaluate_ra_policy'


def x__extract_gate_mapping__mutmut_orig(payload: Any) -> dict[str, bool | None]:
    mapping: dict[str, bool | None] = {}
    if isinstance(payload, dict) and "gates" in payload:
        for entry in payload.get("gates", []):
            if not isinstance(entry, dict) or "tool" not in entry:
                continue
            mapping[entry["tool"]] = _normalize_status(entry.get("status") or entry.get("result"))
    elif isinstance(payload, dict):
        mapping = {k: _normalize_status(v) for k, v in payload.items()}
    return mapping


def x__extract_gate_mapping__mutmut_1(payload: Any) -> dict[str, bool | None]:
    mapping: dict[str, bool | None] = None
    if isinstance(payload, dict) and "gates" in payload:
        for entry in payload.get("gates", []):
            if not isinstance(entry, dict) or "tool" not in entry:
                continue
            mapping[entry["tool"]] = _normalize_status(entry.get("status") or entry.get("result"))
    elif isinstance(payload, dict):
        mapping = {k: _normalize_status(v) for k, v in payload.items()}
    return mapping


def x__extract_gate_mapping__mutmut_2(payload: Any) -> dict[str, bool | None]:
    mapping: dict[str, bool | None] = {}
    if isinstance(payload, dict) or "gates" in payload:
        for entry in payload.get("gates", []):
            if not isinstance(entry, dict) or "tool" not in entry:
                continue
            mapping[entry["tool"]] = _normalize_status(entry.get("status") or entry.get("result"))
    elif isinstance(payload, dict):
        mapping = {k: _normalize_status(v) for k, v in payload.items()}
    return mapping


def x__extract_gate_mapping__mutmut_3(payload: Any) -> dict[str, bool | None]:
    mapping: dict[str, bool | None] = {}
    if isinstance(payload, dict) and "XXgatesXX" in payload:
        for entry in payload.get("gates", []):
            if not isinstance(entry, dict) or "tool" not in entry:
                continue
            mapping[entry["tool"]] = _normalize_status(entry.get("status") or entry.get("result"))
    elif isinstance(payload, dict):
        mapping = {k: _normalize_status(v) for k, v in payload.items()}
    return mapping


def x__extract_gate_mapping__mutmut_4(payload: Any) -> dict[str, bool | None]:
    mapping: dict[str, bool | None] = {}
    if isinstance(payload, dict) and "GATES" in payload:
        for entry in payload.get("gates", []):
            if not isinstance(entry, dict) or "tool" not in entry:
                continue
            mapping[entry["tool"]] = _normalize_status(entry.get("status") or entry.get("result"))
    elif isinstance(payload, dict):
        mapping = {k: _normalize_status(v) for k, v in payload.items()}
    return mapping


def x__extract_gate_mapping__mutmut_5(payload: Any) -> dict[str, bool | None]:
    mapping: dict[str, bool | None] = {}
    if isinstance(payload, dict) and "gates" not in payload:
        for entry in payload.get("gates", []):
            if not isinstance(entry, dict) or "tool" not in entry:
                continue
            mapping[entry["tool"]] = _normalize_status(entry.get("status") or entry.get("result"))
    elif isinstance(payload, dict):
        mapping = {k: _normalize_status(v) for k, v in payload.items()}
    return mapping


def x__extract_gate_mapping__mutmut_6(payload: Any) -> dict[str, bool | None]:
    mapping: dict[str, bool | None] = {}
    if isinstance(payload, dict) and "gates" in payload:
        for entry in payload.get(None, []):
            if not isinstance(entry, dict) or "tool" not in entry:
                continue
            mapping[entry["tool"]] = _normalize_status(entry.get("status") or entry.get("result"))
    elif isinstance(payload, dict):
        mapping = {k: _normalize_status(v) for k, v in payload.items()}
    return mapping


def x__extract_gate_mapping__mutmut_7(payload: Any) -> dict[str, bool | None]:
    mapping: dict[str, bool | None] = {}
    if isinstance(payload, dict) and "gates" in payload:
        for entry in payload.get("gates", None):
            if not isinstance(entry, dict) or "tool" not in entry:
                continue
            mapping[entry["tool"]] = _normalize_status(entry.get("status") or entry.get("result"))
    elif isinstance(payload, dict):
        mapping = {k: _normalize_status(v) for k, v in payload.items()}
    return mapping


def x__extract_gate_mapping__mutmut_8(payload: Any) -> dict[str, bool | None]:
    mapping: dict[str, bool | None] = {}
    if isinstance(payload, dict) and "gates" in payload:
        for entry in payload.get([]):
            if not isinstance(entry, dict) or "tool" not in entry:
                continue
            mapping[entry["tool"]] = _normalize_status(entry.get("status") or entry.get("result"))
    elif isinstance(payload, dict):
        mapping = {k: _normalize_status(v) for k, v in payload.items()}
    return mapping


def x__extract_gate_mapping__mutmut_9(payload: Any) -> dict[str, bool | None]:
    mapping: dict[str, bool | None] = {}
    if isinstance(payload, dict) and "gates" in payload:
        for entry in payload.get("gates", ):
            if not isinstance(entry, dict) or "tool" not in entry:
                continue
            mapping[entry["tool"]] = _normalize_status(entry.get("status") or entry.get("result"))
    elif isinstance(payload, dict):
        mapping = {k: _normalize_status(v) for k, v in payload.items()}
    return mapping


def x__extract_gate_mapping__mutmut_10(payload: Any) -> dict[str, bool | None]:
    mapping: dict[str, bool | None] = {}
    if isinstance(payload, dict) and "gates" in payload:
        for entry in payload.get("XXgatesXX", []):
            if not isinstance(entry, dict) or "tool" not in entry:
                continue
            mapping[entry["tool"]] = _normalize_status(entry.get("status") or entry.get("result"))
    elif isinstance(payload, dict):
        mapping = {k: _normalize_status(v) for k, v in payload.items()}
    return mapping


def x__extract_gate_mapping__mutmut_11(payload: Any) -> dict[str, bool | None]:
    mapping: dict[str, bool | None] = {}
    if isinstance(payload, dict) and "gates" in payload:
        for entry in payload.get("GATES", []):
            if not isinstance(entry, dict) or "tool" not in entry:
                continue
            mapping[entry["tool"]] = _normalize_status(entry.get("status") or entry.get("result"))
    elif isinstance(payload, dict):
        mapping = {k: _normalize_status(v) for k, v in payload.items()}
    return mapping


def x__extract_gate_mapping__mutmut_12(payload: Any) -> dict[str, bool | None]:
    mapping: dict[str, bool | None] = {}
    if isinstance(payload, dict) and "gates" in payload:
        for entry in payload.get("gates", []):
            if not isinstance(entry, dict) and "tool" not in entry:
                continue
            mapping[entry["tool"]] = _normalize_status(entry.get("status") or entry.get("result"))
    elif isinstance(payload, dict):
        mapping = {k: _normalize_status(v) for k, v in payload.items()}
    return mapping


def x__extract_gate_mapping__mutmut_13(payload: Any) -> dict[str, bool | None]:
    mapping: dict[str, bool | None] = {}
    if isinstance(payload, dict) and "gates" in payload:
        for entry in payload.get("gates", []):
            if isinstance(entry, dict) or "tool" not in entry:
                continue
            mapping[entry["tool"]] = _normalize_status(entry.get("status") or entry.get("result"))
    elif isinstance(payload, dict):
        mapping = {k: _normalize_status(v) for k, v in payload.items()}
    return mapping


def x__extract_gate_mapping__mutmut_14(payload: Any) -> dict[str, bool | None]:
    mapping: dict[str, bool | None] = {}
    if isinstance(payload, dict) and "gates" in payload:
        for entry in payload.get("gates", []):
            if not isinstance(entry, dict) or "XXtoolXX" not in entry:
                continue
            mapping[entry["tool"]] = _normalize_status(entry.get("status") or entry.get("result"))
    elif isinstance(payload, dict):
        mapping = {k: _normalize_status(v) for k, v in payload.items()}
    return mapping


def x__extract_gate_mapping__mutmut_15(payload: Any) -> dict[str, bool | None]:
    mapping: dict[str, bool | None] = {}
    if isinstance(payload, dict) and "gates" in payload:
        for entry in payload.get("gates", []):
            if not isinstance(entry, dict) or "TOOL" not in entry:
                continue
            mapping[entry["tool"]] = _normalize_status(entry.get("status") or entry.get("result"))
    elif isinstance(payload, dict):
        mapping = {k: _normalize_status(v) for k, v in payload.items()}
    return mapping


def x__extract_gate_mapping__mutmut_16(payload: Any) -> dict[str, bool | None]:
    mapping: dict[str, bool | None] = {}
    if isinstance(payload, dict) and "gates" in payload:
        for entry in payload.get("gates", []):
            if not isinstance(entry, dict) or "tool" in entry:
                continue
            mapping[entry["tool"]] = _normalize_status(entry.get("status") or entry.get("result"))
    elif isinstance(payload, dict):
        mapping = {k: _normalize_status(v) for k, v in payload.items()}
    return mapping


def x__extract_gate_mapping__mutmut_17(payload: Any) -> dict[str, bool | None]:
    mapping: dict[str, bool | None] = {}
    if isinstance(payload, dict) and "gates" in payload:
        for entry in payload.get("gates", []):
            if not isinstance(entry, dict) or "tool" not in entry:
                break
            mapping[entry["tool"]] = _normalize_status(entry.get("status") or entry.get("result"))
    elif isinstance(payload, dict):
        mapping = {k: _normalize_status(v) for k, v in payload.items()}
    return mapping


def x__extract_gate_mapping__mutmut_18(payload: Any) -> dict[str, bool | None]:
    mapping: dict[str, bool | None] = {}
    if isinstance(payload, dict) and "gates" in payload:
        for entry in payload.get("gates", []):
            if not isinstance(entry, dict) or "tool" not in entry:
                continue
            mapping[entry["tool"]] = None
    elif isinstance(payload, dict):
        mapping = {k: _normalize_status(v) for k, v in payload.items()}
    return mapping


def x__extract_gate_mapping__mutmut_19(payload: Any) -> dict[str, bool | None]:
    mapping: dict[str, bool | None] = {}
    if isinstance(payload, dict) and "gates" in payload:
        for entry in payload.get("gates", []):
            if not isinstance(entry, dict) or "tool" not in entry:
                continue
            mapping[entry["XXtoolXX"]] = _normalize_status(entry.get("status") or entry.get("result"))
    elif isinstance(payload, dict):
        mapping = {k: _normalize_status(v) for k, v in payload.items()}
    return mapping


def x__extract_gate_mapping__mutmut_20(payload: Any) -> dict[str, bool | None]:
    mapping: dict[str, bool | None] = {}
    if isinstance(payload, dict) and "gates" in payload:
        for entry in payload.get("gates", []):
            if not isinstance(entry, dict) or "tool" not in entry:
                continue
            mapping[entry["TOOL"]] = _normalize_status(entry.get("status") or entry.get("result"))
    elif isinstance(payload, dict):
        mapping = {k: _normalize_status(v) for k, v in payload.items()}
    return mapping


def x__extract_gate_mapping__mutmut_21(payload: Any) -> dict[str, bool | None]:
    mapping: dict[str, bool | None] = {}
    if isinstance(payload, dict) and "gates" in payload:
        for entry in payload.get("gates", []):
            if not isinstance(entry, dict) or "tool" not in entry:
                continue
            mapping[entry["tool"]] = _normalize_status(None)
    elif isinstance(payload, dict):
        mapping = {k: _normalize_status(v) for k, v in payload.items()}
    return mapping


def x__extract_gate_mapping__mutmut_22(payload: Any) -> dict[str, bool | None]:
    mapping: dict[str, bool | None] = {}
    if isinstance(payload, dict) and "gates" in payload:
        for entry in payload.get("gates", []):
            if not isinstance(entry, dict) or "tool" not in entry:
                continue
            mapping[entry["tool"]] = _normalize_status(entry.get("status") and entry.get("result"))
    elif isinstance(payload, dict):
        mapping = {k: _normalize_status(v) for k, v in payload.items()}
    return mapping


def x__extract_gate_mapping__mutmut_23(payload: Any) -> dict[str, bool | None]:
    mapping: dict[str, bool | None] = {}
    if isinstance(payload, dict) and "gates" in payload:
        for entry in payload.get("gates", []):
            if not isinstance(entry, dict) or "tool" not in entry:
                continue
            mapping[entry["tool"]] = _normalize_status(entry.get(None) or entry.get("result"))
    elif isinstance(payload, dict):
        mapping = {k: _normalize_status(v) for k, v in payload.items()}
    return mapping


def x__extract_gate_mapping__mutmut_24(payload: Any) -> dict[str, bool | None]:
    mapping: dict[str, bool | None] = {}
    if isinstance(payload, dict) and "gates" in payload:
        for entry in payload.get("gates", []):
            if not isinstance(entry, dict) or "tool" not in entry:
                continue
            mapping[entry["tool"]] = _normalize_status(entry.get("XXstatusXX") or entry.get("result"))
    elif isinstance(payload, dict):
        mapping = {k: _normalize_status(v) for k, v in payload.items()}
    return mapping


def x__extract_gate_mapping__mutmut_25(payload: Any) -> dict[str, bool | None]:
    mapping: dict[str, bool | None] = {}
    if isinstance(payload, dict) and "gates" in payload:
        for entry in payload.get("gates", []):
            if not isinstance(entry, dict) or "tool" not in entry:
                continue
            mapping[entry["tool"]] = _normalize_status(entry.get("STATUS") or entry.get("result"))
    elif isinstance(payload, dict):
        mapping = {k: _normalize_status(v) for k, v in payload.items()}
    return mapping


def x__extract_gate_mapping__mutmut_26(payload: Any) -> dict[str, bool | None]:
    mapping: dict[str, bool | None] = {}
    if isinstance(payload, dict) and "gates" in payload:
        for entry in payload.get("gates", []):
            if not isinstance(entry, dict) or "tool" not in entry:
                continue
            mapping[entry["tool"]] = _normalize_status(entry.get("status") or entry.get(None))
    elif isinstance(payload, dict):
        mapping = {k: _normalize_status(v) for k, v in payload.items()}
    return mapping


def x__extract_gate_mapping__mutmut_27(payload: Any) -> dict[str, bool | None]:
    mapping: dict[str, bool | None] = {}
    if isinstance(payload, dict) and "gates" in payload:
        for entry in payload.get("gates", []):
            if not isinstance(entry, dict) or "tool" not in entry:
                continue
            mapping[entry["tool"]] = _normalize_status(entry.get("status") or entry.get("XXresultXX"))
    elif isinstance(payload, dict):
        mapping = {k: _normalize_status(v) for k, v in payload.items()}
    return mapping


def x__extract_gate_mapping__mutmut_28(payload: Any) -> dict[str, bool | None]:
    mapping: dict[str, bool | None] = {}
    if isinstance(payload, dict) and "gates" in payload:
        for entry in payload.get("gates", []):
            if not isinstance(entry, dict) or "tool" not in entry:
                continue
            mapping[entry["tool"]] = _normalize_status(entry.get("status") or entry.get("RESULT"))
    elif isinstance(payload, dict):
        mapping = {k: _normalize_status(v) for k, v in payload.items()}
    return mapping


def x__extract_gate_mapping__mutmut_29(payload: Any) -> dict[str, bool | None]:
    mapping: dict[str, bool | None] = {}
    if isinstance(payload, dict) and "gates" in payload:
        for entry in payload.get("gates", []):
            if not isinstance(entry, dict) or "tool" not in entry:
                continue
            mapping[entry["tool"]] = _normalize_status(entry.get("status") or entry.get("result"))
    elif isinstance(payload, dict):
        mapping = None
    return mapping


def x__extract_gate_mapping__mutmut_30(payload: Any) -> dict[str, bool | None]:
    mapping: dict[str, bool | None] = {}
    if isinstance(payload, dict) and "gates" in payload:
        for entry in payload.get("gates", []):
            if not isinstance(entry, dict) or "tool" not in entry:
                continue
            mapping[entry["tool"]] = _normalize_status(entry.get("status") or entry.get("result"))
    elif isinstance(payload, dict):
        mapping = {k: _normalize_status(None) for k, v in payload.items()}
    return mapping

x__extract_gate_mapping__mutmut_mutants : ClassVar[MutantDict] = {
'x__extract_gate_mapping__mutmut_1': x__extract_gate_mapping__mutmut_1, 
    'x__extract_gate_mapping__mutmut_2': x__extract_gate_mapping__mutmut_2, 
    'x__extract_gate_mapping__mutmut_3': x__extract_gate_mapping__mutmut_3, 
    'x__extract_gate_mapping__mutmut_4': x__extract_gate_mapping__mutmut_4, 
    'x__extract_gate_mapping__mutmut_5': x__extract_gate_mapping__mutmut_5, 
    'x__extract_gate_mapping__mutmut_6': x__extract_gate_mapping__mutmut_6, 
    'x__extract_gate_mapping__mutmut_7': x__extract_gate_mapping__mutmut_7, 
    'x__extract_gate_mapping__mutmut_8': x__extract_gate_mapping__mutmut_8, 
    'x__extract_gate_mapping__mutmut_9': x__extract_gate_mapping__mutmut_9, 
    'x__extract_gate_mapping__mutmut_10': x__extract_gate_mapping__mutmut_10, 
    'x__extract_gate_mapping__mutmut_11': x__extract_gate_mapping__mutmut_11, 
    'x__extract_gate_mapping__mutmut_12': x__extract_gate_mapping__mutmut_12, 
    'x__extract_gate_mapping__mutmut_13': x__extract_gate_mapping__mutmut_13, 
    'x__extract_gate_mapping__mutmut_14': x__extract_gate_mapping__mutmut_14, 
    'x__extract_gate_mapping__mutmut_15': x__extract_gate_mapping__mutmut_15, 
    'x__extract_gate_mapping__mutmut_16': x__extract_gate_mapping__mutmut_16, 
    'x__extract_gate_mapping__mutmut_17': x__extract_gate_mapping__mutmut_17, 
    'x__extract_gate_mapping__mutmut_18': x__extract_gate_mapping__mutmut_18, 
    'x__extract_gate_mapping__mutmut_19': x__extract_gate_mapping__mutmut_19, 
    'x__extract_gate_mapping__mutmut_20': x__extract_gate_mapping__mutmut_20, 
    'x__extract_gate_mapping__mutmut_21': x__extract_gate_mapping__mutmut_21, 
    'x__extract_gate_mapping__mutmut_22': x__extract_gate_mapping__mutmut_22, 
    'x__extract_gate_mapping__mutmut_23': x__extract_gate_mapping__mutmut_23, 
    'x__extract_gate_mapping__mutmut_24': x__extract_gate_mapping__mutmut_24, 
    'x__extract_gate_mapping__mutmut_25': x__extract_gate_mapping__mutmut_25, 
    'x__extract_gate_mapping__mutmut_26': x__extract_gate_mapping__mutmut_26, 
    'x__extract_gate_mapping__mutmut_27': x__extract_gate_mapping__mutmut_27, 
    'x__extract_gate_mapping__mutmut_28': x__extract_gate_mapping__mutmut_28, 
    'x__extract_gate_mapping__mutmut_29': x__extract_gate_mapping__mutmut_29, 
    'x__extract_gate_mapping__mutmut_30': x__extract_gate_mapping__mutmut_30
}

def _extract_gate_mapping(*args, **kwargs):
    result = _mutmut_trampoline(x__extract_gate_mapping__mutmut_orig, x__extract_gate_mapping__mutmut_mutants, args, kwargs)
    return result 

_extract_gate_mapping.__signature__ = _mutmut_signature(x__extract_gate_mapping__mutmut_orig)
x__extract_gate_mapping__mutmut_orig.__name__ = 'x__extract_gate_mapping'


def x__evaluate_honesty__mutmut_orig(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_1(path: Path) -> HarnessSignal:
    data = None
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_2(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(None)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_3(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_4(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name=None,
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_5(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status=None,
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_6(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail=None,
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_7(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_8(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_9(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_10(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="XXhonesty_metadataXX",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_11(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="HONESTY_METADATA",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_12(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="XXyellowXX",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_13(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="YELLOW",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_14(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="XXHonesty metadata not found; unable to confirm workflow statements.XX",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_15(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_16(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="HONESTY METADATA NOT FOUND; UNABLE TO CONFIRM WORKFLOW STATEMENTS.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_17(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = None
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_18(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") and []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_19(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get(None) or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_20(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("XXstatementsXX") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_21(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("STATEMENTS") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_22(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) and not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_23(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_24(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_25(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name=None,
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_26(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status=None,
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_27(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail=None,
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_28(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_29(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_30(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_31(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="XXhonesty_metadataXX",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_32(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="HONESTY_METADATA",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_33(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="XXyellowXX",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_34(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="YELLOW",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_35(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="XXHonesty metadata present but contains no statements.XX",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_36(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_37(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="HONESTY METADATA PRESENT BUT CONTAINS NO STATEMENTS.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_38(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = None
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_39(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(None)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_40(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None and "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_41(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") and stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_42(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_43(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get(None) or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_44(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("XXcontentXX") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_45(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("CONTENT") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_46(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get(None) is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_47(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("XXcategoryXX") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_48(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("CATEGORY") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_49(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is not None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_50(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "XXverifiedXX" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_51(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "VERIFIED" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_52(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_53(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name=None,
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_54(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status=None,
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_55(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail=None,
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_56(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_57(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_58(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_59(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="XXhonesty_metadataXX",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_60(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="HONESTY_METADATA",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_61(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="XXyellowXX",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_62(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="YELLOW",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_63(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="XXSome honesty statements are incomplete; review required.XX",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_64(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_65(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="SOME HONESTY STATEMENTS ARE INCOMPLETE; REVIEW REQUIRED.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_66(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name=None, status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_67(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status=None, detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_68(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail=None
    )


def x__evaluate_honesty__mutmut_69(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_70(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_71(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", )


def x__evaluate_honesty__mutmut_72(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="XXhonesty_metadataXX", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_73(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="HONESTY_METADATA", status="green", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_74(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="XXgreenXX", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_75(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="GREEN", detail="Honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_76(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="XXHonesty statements recorded and complete.XX"
    )


def x__evaluate_honesty__mutmut_77(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="honesty statements recorded and complete."
    )


def x__evaluate_honesty__mutmut_78(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata", status="green", detail="HONESTY STATEMENTS RECORDED AND COMPLETE."
    )

x__evaluate_honesty__mutmut_mutants : ClassVar[MutantDict] = {
'x__evaluate_honesty__mutmut_1': x__evaluate_honesty__mutmut_1, 
    'x__evaluate_honesty__mutmut_2': x__evaluate_honesty__mutmut_2, 
    'x__evaluate_honesty__mutmut_3': x__evaluate_honesty__mutmut_3, 
    'x__evaluate_honesty__mutmut_4': x__evaluate_honesty__mutmut_4, 
    'x__evaluate_honesty__mutmut_5': x__evaluate_honesty__mutmut_5, 
    'x__evaluate_honesty__mutmut_6': x__evaluate_honesty__mutmut_6, 
    'x__evaluate_honesty__mutmut_7': x__evaluate_honesty__mutmut_7, 
    'x__evaluate_honesty__mutmut_8': x__evaluate_honesty__mutmut_8, 
    'x__evaluate_honesty__mutmut_9': x__evaluate_honesty__mutmut_9, 
    'x__evaluate_honesty__mutmut_10': x__evaluate_honesty__mutmut_10, 
    'x__evaluate_honesty__mutmut_11': x__evaluate_honesty__mutmut_11, 
    'x__evaluate_honesty__mutmut_12': x__evaluate_honesty__mutmut_12, 
    'x__evaluate_honesty__mutmut_13': x__evaluate_honesty__mutmut_13, 
    'x__evaluate_honesty__mutmut_14': x__evaluate_honesty__mutmut_14, 
    'x__evaluate_honesty__mutmut_15': x__evaluate_honesty__mutmut_15, 
    'x__evaluate_honesty__mutmut_16': x__evaluate_honesty__mutmut_16, 
    'x__evaluate_honesty__mutmut_17': x__evaluate_honesty__mutmut_17, 
    'x__evaluate_honesty__mutmut_18': x__evaluate_honesty__mutmut_18, 
    'x__evaluate_honesty__mutmut_19': x__evaluate_honesty__mutmut_19, 
    'x__evaluate_honesty__mutmut_20': x__evaluate_honesty__mutmut_20, 
    'x__evaluate_honesty__mutmut_21': x__evaluate_honesty__mutmut_21, 
    'x__evaluate_honesty__mutmut_22': x__evaluate_honesty__mutmut_22, 
    'x__evaluate_honesty__mutmut_23': x__evaluate_honesty__mutmut_23, 
    'x__evaluate_honesty__mutmut_24': x__evaluate_honesty__mutmut_24, 
    'x__evaluate_honesty__mutmut_25': x__evaluate_honesty__mutmut_25, 
    'x__evaluate_honesty__mutmut_26': x__evaluate_honesty__mutmut_26, 
    'x__evaluate_honesty__mutmut_27': x__evaluate_honesty__mutmut_27, 
    'x__evaluate_honesty__mutmut_28': x__evaluate_honesty__mutmut_28, 
    'x__evaluate_honesty__mutmut_29': x__evaluate_honesty__mutmut_29, 
    'x__evaluate_honesty__mutmut_30': x__evaluate_honesty__mutmut_30, 
    'x__evaluate_honesty__mutmut_31': x__evaluate_honesty__mutmut_31, 
    'x__evaluate_honesty__mutmut_32': x__evaluate_honesty__mutmut_32, 
    'x__evaluate_honesty__mutmut_33': x__evaluate_honesty__mutmut_33, 
    'x__evaluate_honesty__mutmut_34': x__evaluate_honesty__mutmut_34, 
    'x__evaluate_honesty__mutmut_35': x__evaluate_honesty__mutmut_35, 
    'x__evaluate_honesty__mutmut_36': x__evaluate_honesty__mutmut_36, 
    'x__evaluate_honesty__mutmut_37': x__evaluate_honesty__mutmut_37, 
    'x__evaluate_honesty__mutmut_38': x__evaluate_honesty__mutmut_38, 
    'x__evaluate_honesty__mutmut_39': x__evaluate_honesty__mutmut_39, 
    'x__evaluate_honesty__mutmut_40': x__evaluate_honesty__mutmut_40, 
    'x__evaluate_honesty__mutmut_41': x__evaluate_honesty__mutmut_41, 
    'x__evaluate_honesty__mutmut_42': x__evaluate_honesty__mutmut_42, 
    'x__evaluate_honesty__mutmut_43': x__evaluate_honesty__mutmut_43, 
    'x__evaluate_honesty__mutmut_44': x__evaluate_honesty__mutmut_44, 
    'x__evaluate_honesty__mutmut_45': x__evaluate_honesty__mutmut_45, 
    'x__evaluate_honesty__mutmut_46': x__evaluate_honesty__mutmut_46, 
    'x__evaluate_honesty__mutmut_47': x__evaluate_honesty__mutmut_47, 
    'x__evaluate_honesty__mutmut_48': x__evaluate_honesty__mutmut_48, 
    'x__evaluate_honesty__mutmut_49': x__evaluate_honesty__mutmut_49, 
    'x__evaluate_honesty__mutmut_50': x__evaluate_honesty__mutmut_50, 
    'x__evaluate_honesty__mutmut_51': x__evaluate_honesty__mutmut_51, 
    'x__evaluate_honesty__mutmut_52': x__evaluate_honesty__mutmut_52, 
    'x__evaluate_honesty__mutmut_53': x__evaluate_honesty__mutmut_53, 
    'x__evaluate_honesty__mutmut_54': x__evaluate_honesty__mutmut_54, 
    'x__evaluate_honesty__mutmut_55': x__evaluate_honesty__mutmut_55, 
    'x__evaluate_honesty__mutmut_56': x__evaluate_honesty__mutmut_56, 
    'x__evaluate_honesty__mutmut_57': x__evaluate_honesty__mutmut_57, 
    'x__evaluate_honesty__mutmut_58': x__evaluate_honesty__mutmut_58, 
    'x__evaluate_honesty__mutmut_59': x__evaluate_honesty__mutmut_59, 
    'x__evaluate_honesty__mutmut_60': x__evaluate_honesty__mutmut_60, 
    'x__evaluate_honesty__mutmut_61': x__evaluate_honesty__mutmut_61, 
    'x__evaluate_honesty__mutmut_62': x__evaluate_honesty__mutmut_62, 
    'x__evaluate_honesty__mutmut_63': x__evaluate_honesty__mutmut_63, 
    'x__evaluate_honesty__mutmut_64': x__evaluate_honesty__mutmut_64, 
    'x__evaluate_honesty__mutmut_65': x__evaluate_honesty__mutmut_65, 
    'x__evaluate_honesty__mutmut_66': x__evaluate_honesty__mutmut_66, 
    'x__evaluate_honesty__mutmut_67': x__evaluate_honesty__mutmut_67, 
    'x__evaluate_honesty__mutmut_68': x__evaluate_honesty__mutmut_68, 
    'x__evaluate_honesty__mutmut_69': x__evaluate_honesty__mutmut_69, 
    'x__evaluate_honesty__mutmut_70': x__evaluate_honesty__mutmut_70, 
    'x__evaluate_honesty__mutmut_71': x__evaluate_honesty__mutmut_71, 
    'x__evaluate_honesty__mutmut_72': x__evaluate_honesty__mutmut_72, 
    'x__evaluate_honesty__mutmut_73': x__evaluate_honesty__mutmut_73, 
    'x__evaluate_honesty__mutmut_74': x__evaluate_honesty__mutmut_74, 
    'x__evaluate_honesty__mutmut_75': x__evaluate_honesty__mutmut_75, 
    'x__evaluate_honesty__mutmut_76': x__evaluate_honesty__mutmut_76, 
    'x__evaluate_honesty__mutmut_77': x__evaluate_honesty__mutmut_77, 
    'x__evaluate_honesty__mutmut_78': x__evaluate_honesty__mutmut_78
}

def _evaluate_honesty(*args, **kwargs):
    result = _mutmut_trampoline(x__evaluate_honesty__mutmut_orig, x__evaluate_honesty__mutmut_mutants, args, kwargs)
    return result 

_evaluate_honesty.__signature__ = _mutmut_signature(x__evaluate_honesty__mutmut_orig)
x__evaluate_honesty__mutmut_orig.__name__ = 'x__evaluate_honesty'


def x__evaluate_tool_trace__mutmut_orig(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_1(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_2(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name=None,
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_3(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status=None,
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_4(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=None,
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_5(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_6(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_7(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_8(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="XXtool_traceXX",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_9(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="TOOL_TRACE",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_10(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="XXyellowXX",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_11(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="YELLOW",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_12(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="XXTool trace not found; cannot confirm local tool coverage.XX",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_13(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_14(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="TOOL TRACE NOT FOUND; CANNOT CONFIRM LOCAL TOOL COVERAGE.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_15(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = None
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_16(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding=None).splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_17(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="XXutf-8XX").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_18(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="UTF-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_19(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = None
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_20(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_21(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            break
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_22(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(None)
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_23(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(None))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_24(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_25(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name=None, status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_26(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status=None, detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_27(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail=None)

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_28(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_29(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_30(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", )

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_31(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="XXtool_traceXX", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_32(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="TOOL_TRACE", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_33(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="XXyellowXX", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_34(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="YELLOW", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_35(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="XXTool trace is empty.XX")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_36(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_37(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="TOOL TRACE IS EMPTY.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_38(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = None
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_39(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path or gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_40(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = None
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_41(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(None)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_42(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = None

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_43(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(None)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_44(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = None
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_45(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get(None) is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_46(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("XXra_gate_matchXX") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_47(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("RA_GATE_MATCH") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_48(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is not False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_49(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is True]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_50(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = None
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_51(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = None
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_52(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get(None) for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_53(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("XXtoolXX") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_54(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("TOOL") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_55(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = None

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_56(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted(None)

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_57(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_58(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name=None,
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_59(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status=None,
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_60(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail=None,
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_61(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_62(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_63(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_64(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="XXtool_traceXX",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_65(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="TOOL_TRACE",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_66(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="XXredXX",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_67(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="RED",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_68(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="XXRA gate mismatch detected in tool trace entries.XX",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_69(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="ra gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_70(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA GATE MISMATCH DETECTED IN TOOL TRACE ENTRIES.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_71(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name=None,
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_72(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status=None,
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_73(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=None,
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_74(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_75(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_76(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_77(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="XXtool_traceXX",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_78(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="TOOL_TRACE",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_79(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="XXyellowXX",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_80(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="YELLOW",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_81(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(None)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_82(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {'XX, XX'.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_83(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name=None, status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_84(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status=None, detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_85(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail=None)


def x__evaluate_tool_trace__mutmut_86(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_87(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_88(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", )


def x__evaluate_tool_trace__mutmut_89(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="XXtool_traceXX", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_90(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="TOOL_TRACE", status="green", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_91(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="XXgreenXX", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_92(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="GREEN", detail="Tool invocations captured.")


def x__evaluate_tool_trace__mutmut_93(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="XXTool invocations captured.XX")


def x__evaluate_tool_trace__mutmut_94(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="tool invocations captured.")


def x__evaluate_tool_trace__mutmut_95(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="TOOL INVOCATIONS CAPTURED.")

x__evaluate_tool_trace__mutmut_mutants : ClassVar[MutantDict] = {
'x__evaluate_tool_trace__mutmut_1': x__evaluate_tool_trace__mutmut_1, 
    'x__evaluate_tool_trace__mutmut_2': x__evaluate_tool_trace__mutmut_2, 
    'x__evaluate_tool_trace__mutmut_3': x__evaluate_tool_trace__mutmut_3, 
    'x__evaluate_tool_trace__mutmut_4': x__evaluate_tool_trace__mutmut_4, 
    'x__evaluate_tool_trace__mutmut_5': x__evaluate_tool_trace__mutmut_5, 
    'x__evaluate_tool_trace__mutmut_6': x__evaluate_tool_trace__mutmut_6, 
    'x__evaluate_tool_trace__mutmut_7': x__evaluate_tool_trace__mutmut_7, 
    'x__evaluate_tool_trace__mutmut_8': x__evaluate_tool_trace__mutmut_8, 
    'x__evaluate_tool_trace__mutmut_9': x__evaluate_tool_trace__mutmut_9, 
    'x__evaluate_tool_trace__mutmut_10': x__evaluate_tool_trace__mutmut_10, 
    'x__evaluate_tool_trace__mutmut_11': x__evaluate_tool_trace__mutmut_11, 
    'x__evaluate_tool_trace__mutmut_12': x__evaluate_tool_trace__mutmut_12, 
    'x__evaluate_tool_trace__mutmut_13': x__evaluate_tool_trace__mutmut_13, 
    'x__evaluate_tool_trace__mutmut_14': x__evaluate_tool_trace__mutmut_14, 
    'x__evaluate_tool_trace__mutmut_15': x__evaluate_tool_trace__mutmut_15, 
    'x__evaluate_tool_trace__mutmut_16': x__evaluate_tool_trace__mutmut_16, 
    'x__evaluate_tool_trace__mutmut_17': x__evaluate_tool_trace__mutmut_17, 
    'x__evaluate_tool_trace__mutmut_18': x__evaluate_tool_trace__mutmut_18, 
    'x__evaluate_tool_trace__mutmut_19': x__evaluate_tool_trace__mutmut_19, 
    'x__evaluate_tool_trace__mutmut_20': x__evaluate_tool_trace__mutmut_20, 
    'x__evaluate_tool_trace__mutmut_21': x__evaluate_tool_trace__mutmut_21, 
    'x__evaluate_tool_trace__mutmut_22': x__evaluate_tool_trace__mutmut_22, 
    'x__evaluate_tool_trace__mutmut_23': x__evaluate_tool_trace__mutmut_23, 
    'x__evaluate_tool_trace__mutmut_24': x__evaluate_tool_trace__mutmut_24, 
    'x__evaluate_tool_trace__mutmut_25': x__evaluate_tool_trace__mutmut_25, 
    'x__evaluate_tool_trace__mutmut_26': x__evaluate_tool_trace__mutmut_26, 
    'x__evaluate_tool_trace__mutmut_27': x__evaluate_tool_trace__mutmut_27, 
    'x__evaluate_tool_trace__mutmut_28': x__evaluate_tool_trace__mutmut_28, 
    'x__evaluate_tool_trace__mutmut_29': x__evaluate_tool_trace__mutmut_29, 
    'x__evaluate_tool_trace__mutmut_30': x__evaluate_tool_trace__mutmut_30, 
    'x__evaluate_tool_trace__mutmut_31': x__evaluate_tool_trace__mutmut_31, 
    'x__evaluate_tool_trace__mutmut_32': x__evaluate_tool_trace__mutmut_32, 
    'x__evaluate_tool_trace__mutmut_33': x__evaluate_tool_trace__mutmut_33, 
    'x__evaluate_tool_trace__mutmut_34': x__evaluate_tool_trace__mutmut_34, 
    'x__evaluate_tool_trace__mutmut_35': x__evaluate_tool_trace__mutmut_35, 
    'x__evaluate_tool_trace__mutmut_36': x__evaluate_tool_trace__mutmut_36, 
    'x__evaluate_tool_trace__mutmut_37': x__evaluate_tool_trace__mutmut_37, 
    'x__evaluate_tool_trace__mutmut_38': x__evaluate_tool_trace__mutmut_38, 
    'x__evaluate_tool_trace__mutmut_39': x__evaluate_tool_trace__mutmut_39, 
    'x__evaluate_tool_trace__mutmut_40': x__evaluate_tool_trace__mutmut_40, 
    'x__evaluate_tool_trace__mutmut_41': x__evaluate_tool_trace__mutmut_41, 
    'x__evaluate_tool_trace__mutmut_42': x__evaluate_tool_trace__mutmut_42, 
    'x__evaluate_tool_trace__mutmut_43': x__evaluate_tool_trace__mutmut_43, 
    'x__evaluate_tool_trace__mutmut_44': x__evaluate_tool_trace__mutmut_44, 
    'x__evaluate_tool_trace__mutmut_45': x__evaluate_tool_trace__mutmut_45, 
    'x__evaluate_tool_trace__mutmut_46': x__evaluate_tool_trace__mutmut_46, 
    'x__evaluate_tool_trace__mutmut_47': x__evaluate_tool_trace__mutmut_47, 
    'x__evaluate_tool_trace__mutmut_48': x__evaluate_tool_trace__mutmut_48, 
    'x__evaluate_tool_trace__mutmut_49': x__evaluate_tool_trace__mutmut_49, 
    'x__evaluate_tool_trace__mutmut_50': x__evaluate_tool_trace__mutmut_50, 
    'x__evaluate_tool_trace__mutmut_51': x__evaluate_tool_trace__mutmut_51, 
    'x__evaluate_tool_trace__mutmut_52': x__evaluate_tool_trace__mutmut_52, 
    'x__evaluate_tool_trace__mutmut_53': x__evaluate_tool_trace__mutmut_53, 
    'x__evaluate_tool_trace__mutmut_54': x__evaluate_tool_trace__mutmut_54, 
    'x__evaluate_tool_trace__mutmut_55': x__evaluate_tool_trace__mutmut_55, 
    'x__evaluate_tool_trace__mutmut_56': x__evaluate_tool_trace__mutmut_56, 
    'x__evaluate_tool_trace__mutmut_57': x__evaluate_tool_trace__mutmut_57, 
    'x__evaluate_tool_trace__mutmut_58': x__evaluate_tool_trace__mutmut_58, 
    'x__evaluate_tool_trace__mutmut_59': x__evaluate_tool_trace__mutmut_59, 
    'x__evaluate_tool_trace__mutmut_60': x__evaluate_tool_trace__mutmut_60, 
    'x__evaluate_tool_trace__mutmut_61': x__evaluate_tool_trace__mutmut_61, 
    'x__evaluate_tool_trace__mutmut_62': x__evaluate_tool_trace__mutmut_62, 
    'x__evaluate_tool_trace__mutmut_63': x__evaluate_tool_trace__mutmut_63, 
    'x__evaluate_tool_trace__mutmut_64': x__evaluate_tool_trace__mutmut_64, 
    'x__evaluate_tool_trace__mutmut_65': x__evaluate_tool_trace__mutmut_65, 
    'x__evaluate_tool_trace__mutmut_66': x__evaluate_tool_trace__mutmut_66, 
    'x__evaluate_tool_trace__mutmut_67': x__evaluate_tool_trace__mutmut_67, 
    'x__evaluate_tool_trace__mutmut_68': x__evaluate_tool_trace__mutmut_68, 
    'x__evaluate_tool_trace__mutmut_69': x__evaluate_tool_trace__mutmut_69, 
    'x__evaluate_tool_trace__mutmut_70': x__evaluate_tool_trace__mutmut_70, 
    'x__evaluate_tool_trace__mutmut_71': x__evaluate_tool_trace__mutmut_71, 
    'x__evaluate_tool_trace__mutmut_72': x__evaluate_tool_trace__mutmut_72, 
    'x__evaluate_tool_trace__mutmut_73': x__evaluate_tool_trace__mutmut_73, 
    'x__evaluate_tool_trace__mutmut_74': x__evaluate_tool_trace__mutmut_74, 
    'x__evaluate_tool_trace__mutmut_75': x__evaluate_tool_trace__mutmut_75, 
    'x__evaluate_tool_trace__mutmut_76': x__evaluate_tool_trace__mutmut_76, 
    'x__evaluate_tool_trace__mutmut_77': x__evaluate_tool_trace__mutmut_77, 
    'x__evaluate_tool_trace__mutmut_78': x__evaluate_tool_trace__mutmut_78, 
    'x__evaluate_tool_trace__mutmut_79': x__evaluate_tool_trace__mutmut_79, 
    'x__evaluate_tool_trace__mutmut_80': x__evaluate_tool_trace__mutmut_80, 
    'x__evaluate_tool_trace__mutmut_81': x__evaluate_tool_trace__mutmut_81, 
    'x__evaluate_tool_trace__mutmut_82': x__evaluate_tool_trace__mutmut_82, 
    'x__evaluate_tool_trace__mutmut_83': x__evaluate_tool_trace__mutmut_83, 
    'x__evaluate_tool_trace__mutmut_84': x__evaluate_tool_trace__mutmut_84, 
    'x__evaluate_tool_trace__mutmut_85': x__evaluate_tool_trace__mutmut_85, 
    'x__evaluate_tool_trace__mutmut_86': x__evaluate_tool_trace__mutmut_86, 
    'x__evaluate_tool_trace__mutmut_87': x__evaluate_tool_trace__mutmut_87, 
    'x__evaluate_tool_trace__mutmut_88': x__evaluate_tool_trace__mutmut_88, 
    'x__evaluate_tool_trace__mutmut_89': x__evaluate_tool_trace__mutmut_89, 
    'x__evaluate_tool_trace__mutmut_90': x__evaluate_tool_trace__mutmut_90, 
    'x__evaluate_tool_trace__mutmut_91': x__evaluate_tool_trace__mutmut_91, 
    'x__evaluate_tool_trace__mutmut_92': x__evaluate_tool_trace__mutmut_92, 
    'x__evaluate_tool_trace__mutmut_93': x__evaluate_tool_trace__mutmut_93, 
    'x__evaluate_tool_trace__mutmut_94': x__evaluate_tool_trace__mutmut_94, 
    'x__evaluate_tool_trace__mutmut_95': x__evaluate_tool_trace__mutmut_95
}

def _evaluate_tool_trace(*args, **kwargs):
    result = _mutmut_trampoline(x__evaluate_tool_trace__mutmut_orig, x__evaluate_tool_trace__mutmut_mutants, args, kwargs)
    return result 

_evaluate_tool_trace.__signature__ = _mutmut_signature(x__evaluate_tool_trace__mutmut_orig)
x__evaluate_tool_trace__mutmut_orig.__name__ = 'x__evaluate_tool_trace'


def x_compute_golden_harness_status__mutmut_orig(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_1(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_2(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(None) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_3(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = None
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_4(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(None),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_5(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(None),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_6(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(None, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_7(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, None),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_8(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_9(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_10(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = None
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_11(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "XXgreenXX"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_12(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "GREEN"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_13(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(None):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_14(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status != "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_15(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "XXredXX" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_16(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "RED" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_17(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = None
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_18(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "XXredXX"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_19(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "RED"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_20(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(None):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_21(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status != "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_22(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "XXyellowXX" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_23(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "YELLOW" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_24(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = None
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_25(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "XXyellowXX"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_26(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "YELLOW"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_27(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = None
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_28(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "XXgenerated_atXX": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_29(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "GENERATED_AT": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_30(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "XXoverall_statusXX": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_31(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "OVERALL_STATUS": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_32(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "XXsignalsXX": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_33(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "SIGNALS": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_34(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "XXinputsXX": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_35(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "INPUTS": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_36(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "XXra_policy_pathXX": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_37(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "RA_POLICY_PATH": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_38(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(None) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_39(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "XXhonesty_pathXX": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_40(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "HONESTY_PATH": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_41(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(None),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_42(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "XXtool_trace_pathXX": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_43(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "TOOL_TRACE_PATH": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_44(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(None),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_45(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "XXra_gate_pathXX": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_46(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "RA_GATE_PATH": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_47(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(None) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_48(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=None, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_49(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=None)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_50(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_51(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, )
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_52(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=False, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_53(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=False)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_54(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(None, encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_55(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding=None)
    return payload


def x_compute_golden_harness_status__mutmut_56(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_57(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), )
    return payload


def x_compute_golden_harness_status__mutmut_58(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(None, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_59(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=None, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_60(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=None), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_61(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(indent=2, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_62(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_63(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_64(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=3, sort_keys=True), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_65(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=False), encoding="utf-8")
    return payload


def x_compute_golden_harness_status__mutmut_66(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="XXutf-8XX")
    return payload


def x_compute_golden_harness_status__mutmut_67(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="UTF-8")
    return payload

x_compute_golden_harness_status__mutmut_mutants : ClassVar[MutantDict] = {
'x_compute_golden_harness_status__mutmut_1': x_compute_golden_harness_status__mutmut_1, 
    'x_compute_golden_harness_status__mutmut_2': x_compute_golden_harness_status__mutmut_2, 
    'x_compute_golden_harness_status__mutmut_3': x_compute_golden_harness_status__mutmut_3, 
    'x_compute_golden_harness_status__mutmut_4': x_compute_golden_harness_status__mutmut_4, 
    'x_compute_golden_harness_status__mutmut_5': x_compute_golden_harness_status__mutmut_5, 
    'x_compute_golden_harness_status__mutmut_6': x_compute_golden_harness_status__mutmut_6, 
    'x_compute_golden_harness_status__mutmut_7': x_compute_golden_harness_status__mutmut_7, 
    'x_compute_golden_harness_status__mutmut_8': x_compute_golden_harness_status__mutmut_8, 
    'x_compute_golden_harness_status__mutmut_9': x_compute_golden_harness_status__mutmut_9, 
    'x_compute_golden_harness_status__mutmut_10': x_compute_golden_harness_status__mutmut_10, 
    'x_compute_golden_harness_status__mutmut_11': x_compute_golden_harness_status__mutmut_11, 
    'x_compute_golden_harness_status__mutmut_12': x_compute_golden_harness_status__mutmut_12, 
    'x_compute_golden_harness_status__mutmut_13': x_compute_golden_harness_status__mutmut_13, 
    'x_compute_golden_harness_status__mutmut_14': x_compute_golden_harness_status__mutmut_14, 
    'x_compute_golden_harness_status__mutmut_15': x_compute_golden_harness_status__mutmut_15, 
    'x_compute_golden_harness_status__mutmut_16': x_compute_golden_harness_status__mutmut_16, 
    'x_compute_golden_harness_status__mutmut_17': x_compute_golden_harness_status__mutmut_17, 
    'x_compute_golden_harness_status__mutmut_18': x_compute_golden_harness_status__mutmut_18, 
    'x_compute_golden_harness_status__mutmut_19': x_compute_golden_harness_status__mutmut_19, 
    'x_compute_golden_harness_status__mutmut_20': x_compute_golden_harness_status__mutmut_20, 
    'x_compute_golden_harness_status__mutmut_21': x_compute_golden_harness_status__mutmut_21, 
    'x_compute_golden_harness_status__mutmut_22': x_compute_golden_harness_status__mutmut_22, 
    'x_compute_golden_harness_status__mutmut_23': x_compute_golden_harness_status__mutmut_23, 
    'x_compute_golden_harness_status__mutmut_24': x_compute_golden_harness_status__mutmut_24, 
    'x_compute_golden_harness_status__mutmut_25': x_compute_golden_harness_status__mutmut_25, 
    'x_compute_golden_harness_status__mutmut_26': x_compute_golden_harness_status__mutmut_26, 
    'x_compute_golden_harness_status__mutmut_27': x_compute_golden_harness_status__mutmut_27, 
    'x_compute_golden_harness_status__mutmut_28': x_compute_golden_harness_status__mutmut_28, 
    'x_compute_golden_harness_status__mutmut_29': x_compute_golden_harness_status__mutmut_29, 
    'x_compute_golden_harness_status__mutmut_30': x_compute_golden_harness_status__mutmut_30, 
    'x_compute_golden_harness_status__mutmut_31': x_compute_golden_harness_status__mutmut_31, 
    'x_compute_golden_harness_status__mutmut_32': x_compute_golden_harness_status__mutmut_32, 
    'x_compute_golden_harness_status__mutmut_33': x_compute_golden_harness_status__mutmut_33, 
    'x_compute_golden_harness_status__mutmut_34': x_compute_golden_harness_status__mutmut_34, 
    'x_compute_golden_harness_status__mutmut_35': x_compute_golden_harness_status__mutmut_35, 
    'x_compute_golden_harness_status__mutmut_36': x_compute_golden_harness_status__mutmut_36, 
    'x_compute_golden_harness_status__mutmut_37': x_compute_golden_harness_status__mutmut_37, 
    'x_compute_golden_harness_status__mutmut_38': x_compute_golden_harness_status__mutmut_38, 
    'x_compute_golden_harness_status__mutmut_39': x_compute_golden_harness_status__mutmut_39, 
    'x_compute_golden_harness_status__mutmut_40': x_compute_golden_harness_status__mutmut_40, 
    'x_compute_golden_harness_status__mutmut_41': x_compute_golden_harness_status__mutmut_41, 
    'x_compute_golden_harness_status__mutmut_42': x_compute_golden_harness_status__mutmut_42, 
    'x_compute_golden_harness_status__mutmut_43': x_compute_golden_harness_status__mutmut_43, 
    'x_compute_golden_harness_status__mutmut_44': x_compute_golden_harness_status__mutmut_44, 
    'x_compute_golden_harness_status__mutmut_45': x_compute_golden_harness_status__mutmut_45, 
    'x_compute_golden_harness_status__mutmut_46': x_compute_golden_harness_status__mutmut_46, 
    'x_compute_golden_harness_status__mutmut_47': x_compute_golden_harness_status__mutmut_47, 
    'x_compute_golden_harness_status__mutmut_48': x_compute_golden_harness_status__mutmut_48, 
    'x_compute_golden_harness_status__mutmut_49': x_compute_golden_harness_status__mutmut_49, 
    'x_compute_golden_harness_status__mutmut_50': x_compute_golden_harness_status__mutmut_50, 
    'x_compute_golden_harness_status__mutmut_51': x_compute_golden_harness_status__mutmut_51, 
    'x_compute_golden_harness_status__mutmut_52': x_compute_golden_harness_status__mutmut_52, 
    'x_compute_golden_harness_status__mutmut_53': x_compute_golden_harness_status__mutmut_53, 
    'x_compute_golden_harness_status__mutmut_54': x_compute_golden_harness_status__mutmut_54, 
    'x_compute_golden_harness_status__mutmut_55': x_compute_golden_harness_status__mutmut_55, 
    'x_compute_golden_harness_status__mutmut_56': x_compute_golden_harness_status__mutmut_56, 
    'x_compute_golden_harness_status__mutmut_57': x_compute_golden_harness_status__mutmut_57, 
    'x_compute_golden_harness_status__mutmut_58': x_compute_golden_harness_status__mutmut_58, 
    'x_compute_golden_harness_status__mutmut_59': x_compute_golden_harness_status__mutmut_59, 
    'x_compute_golden_harness_status__mutmut_60': x_compute_golden_harness_status__mutmut_60, 
    'x_compute_golden_harness_status__mutmut_61': x_compute_golden_harness_status__mutmut_61, 
    'x_compute_golden_harness_status__mutmut_62': x_compute_golden_harness_status__mutmut_62, 
    'x_compute_golden_harness_status__mutmut_63': x_compute_golden_harness_status__mutmut_63, 
    'x_compute_golden_harness_status__mutmut_64': x_compute_golden_harness_status__mutmut_64, 
    'x_compute_golden_harness_status__mutmut_65': x_compute_golden_harness_status__mutmut_65, 
    'x_compute_golden_harness_status__mutmut_66': x_compute_golden_harness_status__mutmut_66, 
    'x_compute_golden_harness_status__mutmut_67': x_compute_golden_harness_status__mutmut_67
}

def compute_golden_harness_status(*args, **kwargs):
    result = _mutmut_trampoline(x_compute_golden_harness_status__mutmut_orig, x_compute_golden_harness_status__mutmut_mutants, args, kwargs)
    return result 

compute_golden_harness_status.__signature__ = _mutmut_signature(x_compute_golden_harness_status__mutmut_orig)
x_compute_golden_harness_status__mutmut_orig.__name__ = 'x_compute_golden_harness_status'


__all__ = ["compute_golden_harness_status", "HarnessSignal"]
