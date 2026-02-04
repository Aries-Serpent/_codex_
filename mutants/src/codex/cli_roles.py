"""Typer CLI to export cross-platform role matrices."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from codex.dynamics.model.role import DynamicsRole
from codex.dynamics.role_matrix import build_role_matrix
from codex.zendesk.model.role import Role as ZendeskRole

app = typer.Typer(help="Role matrix and permission harmonization.")
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


def x__load_jsonl_or_json__mutmut_orig(path: Path):
    if path.suffix.lower() == ".jsonl":
        with path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
    return json.loads(path.read_text(encoding="utf-8"))


def x__load_jsonl_or_json__mutmut_1(path: Path):
    if path.suffix.upper() == ".jsonl":
        with path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
    return json.loads(path.read_text(encoding="utf-8"))


def x__load_jsonl_or_json__mutmut_2(path: Path):
    if path.suffix.lower() != ".jsonl":
        with path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
    return json.loads(path.read_text(encoding="utf-8"))


def x__load_jsonl_or_json__mutmut_3(path: Path):
    if path.suffix.lower() == "XX.jsonlXX":
        with path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
    return json.loads(path.read_text(encoding="utf-8"))


def x__load_jsonl_or_json__mutmut_4(path: Path):
    if path.suffix.lower() == ".JSONL":
        with path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
    return json.loads(path.read_text(encoding="utf-8"))


def x__load_jsonl_or_json__mutmut_5(path: Path):
    if path.suffix.lower() == ".jsonl":
        with path.open(None, encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
    return json.loads(path.read_text(encoding="utf-8"))


def x__load_jsonl_or_json__mutmut_6(path: Path):
    if path.suffix.lower() == ".jsonl":
        with path.open("r", encoding=None) as handle:
            return [json.loads(line) for line in handle if line.strip()]
    return json.loads(path.read_text(encoding="utf-8"))


def x__load_jsonl_or_json__mutmut_7(path: Path):
    if path.suffix.lower() == ".jsonl":
        with path.open(encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
    return json.loads(path.read_text(encoding="utf-8"))


def x__load_jsonl_or_json__mutmut_8(path: Path):
    if path.suffix.lower() == ".jsonl":
        with path.open("r", ) as handle:
            return [json.loads(line) for line in handle if line.strip()]
    return json.loads(path.read_text(encoding="utf-8"))


def x__load_jsonl_or_json__mutmut_9(path: Path):
    if path.suffix.lower() == ".jsonl":
        with path.open("XXrXX", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
    return json.loads(path.read_text(encoding="utf-8"))


def x__load_jsonl_or_json__mutmut_10(path: Path):
    if path.suffix.lower() == ".jsonl":
        with path.open("R", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
    return json.loads(path.read_text(encoding="utf-8"))


def x__load_jsonl_or_json__mutmut_11(path: Path):
    if path.suffix.lower() == ".jsonl":
        with path.open("r", encoding="XXutf-8XX") as handle:
            return [json.loads(line) for line in handle if line.strip()]
    return json.loads(path.read_text(encoding="utf-8"))


def x__load_jsonl_or_json__mutmut_12(path: Path):
    if path.suffix.lower() == ".jsonl":
        with path.open("r", encoding="UTF-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
    return json.loads(path.read_text(encoding="utf-8"))


def x__load_jsonl_or_json__mutmut_13(path: Path):
    if path.suffix.lower() == ".jsonl":
        with path.open("r", encoding="utf-8") as handle:
            return [json.loads(None) for line in handle if line.strip()]
    return json.loads(path.read_text(encoding="utf-8"))


def x__load_jsonl_or_json__mutmut_14(path: Path):
    if path.suffix.lower() == ".jsonl":
        with path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
    return json.loads(None)


def x__load_jsonl_or_json__mutmut_15(path: Path):
    if path.suffix.lower() == ".jsonl":
        with path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
    return json.loads(path.read_text(encoding=None))


def x__load_jsonl_or_json__mutmut_16(path: Path):
    if path.suffix.lower() == ".jsonl":
        with path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
    return json.loads(path.read_text(encoding="XXutf-8XX"))


def x__load_jsonl_or_json__mutmut_17(path: Path):
    if path.suffix.lower() == ".jsonl":
        with path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
    return json.loads(path.read_text(encoding="UTF-8"))

x__load_jsonl_or_json__mutmut_mutants : ClassVar[MutantDict] = {
'x__load_jsonl_or_json__mutmut_1': x__load_jsonl_or_json__mutmut_1, 
    'x__load_jsonl_or_json__mutmut_2': x__load_jsonl_or_json__mutmut_2, 
    'x__load_jsonl_or_json__mutmut_3': x__load_jsonl_or_json__mutmut_3, 
    'x__load_jsonl_or_json__mutmut_4': x__load_jsonl_or_json__mutmut_4, 
    'x__load_jsonl_or_json__mutmut_5': x__load_jsonl_or_json__mutmut_5, 
    'x__load_jsonl_or_json__mutmut_6': x__load_jsonl_or_json__mutmut_6, 
    'x__load_jsonl_or_json__mutmut_7': x__load_jsonl_or_json__mutmut_7, 
    'x__load_jsonl_or_json__mutmut_8': x__load_jsonl_or_json__mutmut_8, 
    'x__load_jsonl_or_json__mutmut_9': x__load_jsonl_or_json__mutmut_9, 
    'x__load_jsonl_or_json__mutmut_10': x__load_jsonl_or_json__mutmut_10, 
    'x__load_jsonl_or_json__mutmut_11': x__load_jsonl_or_json__mutmut_11, 
    'x__load_jsonl_or_json__mutmut_12': x__load_jsonl_or_json__mutmut_12, 
    'x__load_jsonl_or_json__mutmut_13': x__load_jsonl_or_json__mutmut_13, 
    'x__load_jsonl_or_json__mutmut_14': x__load_jsonl_or_json__mutmut_14, 
    'x__load_jsonl_or_json__mutmut_15': x__load_jsonl_or_json__mutmut_15, 
    'x__load_jsonl_or_json__mutmut_16': x__load_jsonl_or_json__mutmut_16, 
    'x__load_jsonl_or_json__mutmut_17': x__load_jsonl_or_json__mutmut_17
}

def _load_jsonl_or_json(*args, **kwargs):
    result = _mutmut_trampoline(x__load_jsonl_or_json__mutmut_orig, x__load_jsonl_or_json__mutmut_mutants, args, kwargs)
    return result 

_load_jsonl_or_json.__signature__ = _mutmut_signature(x__load_jsonl_or_json__mutmut_orig)
x__load_jsonl_or_json__mutmut_orig.__name__ = 'x__load_jsonl_or_json'


InputArg = Annotated[Path, typer.Argument(..., exists=True, readable=True)]
OutputArg = Annotated[Path, typer.Argument(...)]


@app.command("export-matrix")
def export_matrix(
    zendesk_roles_file: InputArg,
    dynamics_roles_file: InputArg,
    output_json: OutputArg,
) -> None:
    zendesk_raw = _load_jsonl_or_json(zendesk_roles_file)
    dynamics_raw = _load_jsonl_or_json(dynamics_roles_file)

    zendesk_roles = [ZendeskRole.model_validate(item) for item in zendesk_raw]
    dynamics_roles = [DynamicsRole.model_validate(item) for item in dynamics_raw]

    matrix = build_role_matrix(zendesk_roles, dynamics_roles)
    output_json.write_text(json.dumps(matrix, indent=2), encoding="utf-8")
    typer.echo(output_json.as_posix())
