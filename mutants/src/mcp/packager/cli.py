"""
Cli Module

This module provides functionality for cli.

Usage:
    from packager.cli import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import argparse

from src.mcp.packager.generator import generate_package, load_config
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


def x_main__mutmut_orig() -> None:
    parser = argparse.ArgumentParser(description="Generate MCP package skeleton")
    parser.add_argument("--config", required=True, help="Path to MCP packager YAML config")
    parser.add_argument("--output", help="Override output directory")
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(config, output_dir=args.output)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_1() -> None:
    parser = None
    parser.add_argument("--config", required=True, help="Path to MCP packager YAML config")
    parser.add_argument("--output", help="Override output directory")
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(config, output_dir=args.output)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_2() -> None:
    parser = argparse.ArgumentParser(description=None)
    parser.add_argument("--config", required=True, help="Path to MCP packager YAML config")
    parser.add_argument("--output", help="Override output directory")
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(config, output_dir=args.output)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_3() -> None:
    parser = argparse.ArgumentParser(description="XXGenerate MCP package skeletonXX")
    parser.add_argument("--config", required=True, help="Path to MCP packager YAML config")
    parser.add_argument("--output", help="Override output directory")
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(config, output_dir=args.output)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_4() -> None:
    parser = argparse.ArgumentParser(description="generate mcp package skeleton")
    parser.add_argument("--config", required=True, help="Path to MCP packager YAML config")
    parser.add_argument("--output", help="Override output directory")
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(config, output_dir=args.output)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_5() -> None:
    parser = argparse.ArgumentParser(description="GENERATE MCP PACKAGE SKELETON")
    parser.add_argument("--config", required=True, help="Path to MCP packager YAML config")
    parser.add_argument("--output", help="Override output directory")
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(config, output_dir=args.output)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_6() -> None:
    parser = argparse.ArgumentParser(description="Generate MCP package skeleton")
    parser.add_argument(None, required=True, help="Path to MCP packager YAML config")
    parser.add_argument("--output", help="Override output directory")
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(config, output_dir=args.output)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_7() -> None:
    parser = argparse.ArgumentParser(description="Generate MCP package skeleton")
    parser.add_argument("--config", required=None, help="Path to MCP packager YAML config")
    parser.add_argument("--output", help="Override output directory")
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(config, output_dir=args.output)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_8() -> None:
    parser = argparse.ArgumentParser(description="Generate MCP package skeleton")
    parser.add_argument("--config", required=True, help=None)
    parser.add_argument("--output", help="Override output directory")
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(config, output_dir=args.output)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_9() -> None:
    parser = argparse.ArgumentParser(description="Generate MCP package skeleton")
    parser.add_argument(required=True, help="Path to MCP packager YAML config")
    parser.add_argument("--output", help="Override output directory")
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(config, output_dir=args.output)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_10() -> None:
    parser = argparse.ArgumentParser(description="Generate MCP package skeleton")
    parser.add_argument("--config", help="Path to MCP packager YAML config")
    parser.add_argument("--output", help="Override output directory")
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(config, output_dir=args.output)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_11() -> None:
    parser = argparse.ArgumentParser(description="Generate MCP package skeleton")
    parser.add_argument("--config", required=True, )
    parser.add_argument("--output", help="Override output directory")
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(config, output_dir=args.output)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_12() -> None:
    parser = argparse.ArgumentParser(description="Generate MCP package skeleton")
    parser.add_argument("XX--configXX", required=True, help="Path to MCP packager YAML config")
    parser.add_argument("--output", help="Override output directory")
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(config, output_dir=args.output)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_13() -> None:
    parser = argparse.ArgumentParser(description="Generate MCP package skeleton")
    parser.add_argument("--CONFIG", required=True, help="Path to MCP packager YAML config")
    parser.add_argument("--output", help="Override output directory")
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(config, output_dir=args.output)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_14() -> None:
    parser = argparse.ArgumentParser(description="Generate MCP package skeleton")
    parser.add_argument("--config", required=False, help="Path to MCP packager YAML config")
    parser.add_argument("--output", help="Override output directory")
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(config, output_dir=args.output)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_15() -> None:
    parser = argparse.ArgumentParser(description="Generate MCP package skeleton")
    parser.add_argument("--config", required=True, help="XXPath to MCP packager YAML configXX")
    parser.add_argument("--output", help="Override output directory")
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(config, output_dir=args.output)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_16() -> None:
    parser = argparse.ArgumentParser(description="Generate MCP package skeleton")
    parser.add_argument("--config", required=True, help="path to mcp packager yaml config")
    parser.add_argument("--output", help="Override output directory")
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(config, output_dir=args.output)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_17() -> None:
    parser = argparse.ArgumentParser(description="Generate MCP package skeleton")
    parser.add_argument("--config", required=True, help="PATH TO MCP PACKAGER YAML CONFIG")
    parser.add_argument("--output", help="Override output directory")
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(config, output_dir=args.output)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_18() -> None:
    parser = argparse.ArgumentParser(description="Generate MCP package skeleton")
    parser.add_argument("--config", required=True, help="Path to MCP packager YAML config")
    parser.add_argument(None, help="Override output directory")
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(config, output_dir=args.output)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_19() -> None:
    parser = argparse.ArgumentParser(description="Generate MCP package skeleton")
    parser.add_argument("--config", required=True, help="Path to MCP packager YAML config")
    parser.add_argument("--output", help=None)
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(config, output_dir=args.output)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_20() -> None:
    parser = argparse.ArgumentParser(description="Generate MCP package skeleton")
    parser.add_argument("--config", required=True, help="Path to MCP packager YAML config")
    parser.add_argument(help="Override output directory")
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(config, output_dir=args.output)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_21() -> None:
    parser = argparse.ArgumentParser(description="Generate MCP package skeleton")
    parser.add_argument("--config", required=True, help="Path to MCP packager YAML config")
    parser.add_argument("--output", )
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(config, output_dir=args.output)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_22() -> None:
    parser = argparse.ArgumentParser(description="Generate MCP package skeleton")
    parser.add_argument("--config", required=True, help="Path to MCP packager YAML config")
    parser.add_argument("XX--outputXX", help="Override output directory")
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(config, output_dir=args.output)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_23() -> None:
    parser = argparse.ArgumentParser(description="Generate MCP package skeleton")
    parser.add_argument("--config", required=True, help="Path to MCP packager YAML config")
    parser.add_argument("--OUTPUT", help="Override output directory")
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(config, output_dir=args.output)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_24() -> None:
    parser = argparse.ArgumentParser(description="Generate MCP package skeleton")
    parser.add_argument("--config", required=True, help="Path to MCP packager YAML config")
    parser.add_argument("--output", help="XXOverride output directoryXX")
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(config, output_dir=args.output)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_25() -> None:
    parser = argparse.ArgumentParser(description="Generate MCP package skeleton")
    parser.add_argument("--config", required=True, help="Path to MCP packager YAML config")
    parser.add_argument("--output", help="override output directory")
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(config, output_dir=args.output)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_26() -> None:
    parser = argparse.ArgumentParser(description="Generate MCP package skeleton")
    parser.add_argument("--config", required=True, help="Path to MCP packager YAML config")
    parser.add_argument("--output", help="OVERRIDE OUTPUT DIRECTORY")
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(config, output_dir=args.output)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_27() -> None:
    parser = argparse.ArgumentParser(description="Generate MCP package skeleton")
    parser.add_argument("--config", required=True, help="Path to MCP packager YAML config")
    parser.add_argument("--output", help="Override output directory")
    args = None

    config = load_config(args.config)
    output = generate_package(config, output_dir=args.output)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_28() -> None:
    parser = argparse.ArgumentParser(description="Generate MCP package skeleton")
    parser.add_argument("--config", required=True, help="Path to MCP packager YAML config")
    parser.add_argument("--output", help="Override output directory")
    args = parser.parse_args()

    config = None
    output = generate_package(config, output_dir=args.output)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_29() -> None:
    parser = argparse.ArgumentParser(description="Generate MCP package skeleton")
    parser.add_argument("--config", required=True, help="Path to MCP packager YAML config")
    parser.add_argument("--output", help="Override output directory")
    args = parser.parse_args()

    config = load_config(None)
    output = generate_package(config, output_dir=args.output)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_30() -> None:
    parser = argparse.ArgumentParser(description="Generate MCP package skeleton")
    parser.add_argument("--config", required=True, help="Path to MCP packager YAML config")
    parser.add_argument("--output", help="Override output directory")
    args = parser.parse_args()

    config = load_config(args.config)
    output = None
    print(f"Generated MCP package at {output}")


def x_main__mutmut_31() -> None:
    parser = argparse.ArgumentParser(description="Generate MCP package skeleton")
    parser.add_argument("--config", required=True, help="Path to MCP packager YAML config")
    parser.add_argument("--output", help="Override output directory")
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(None, output_dir=args.output)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_32() -> None:
    parser = argparse.ArgumentParser(description="Generate MCP package skeleton")
    parser.add_argument("--config", required=True, help="Path to MCP packager YAML config")
    parser.add_argument("--output", help="Override output directory")
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(config, output_dir=None)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_33() -> None:
    parser = argparse.ArgumentParser(description="Generate MCP package skeleton")
    parser.add_argument("--config", required=True, help="Path to MCP packager YAML config")
    parser.add_argument("--output", help="Override output directory")
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(output_dir=args.output)
    print(f"Generated MCP package at {output}")


def x_main__mutmut_34() -> None:
    parser = argparse.ArgumentParser(description="Generate MCP package skeleton")
    parser.add_argument("--config", required=True, help="Path to MCP packager YAML config")
    parser.add_argument("--output", help="Override output directory")
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(config, )
    print(f"Generated MCP package at {output}")


def x_main__mutmut_35() -> None:
    parser = argparse.ArgumentParser(description="Generate MCP package skeleton")
    parser.add_argument("--config", required=True, help="Path to MCP packager YAML config")
    parser.add_argument("--output", help="Override output directory")
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(config, output_dir=args.output)
    print(None)

x_main__mutmut_mutants : ClassVar[MutantDict] = {
'x_main__mutmut_1': x_main__mutmut_1, 
    'x_main__mutmut_2': x_main__mutmut_2, 
    'x_main__mutmut_3': x_main__mutmut_3, 
    'x_main__mutmut_4': x_main__mutmut_4, 
    'x_main__mutmut_5': x_main__mutmut_5, 
    'x_main__mutmut_6': x_main__mutmut_6, 
    'x_main__mutmut_7': x_main__mutmut_7, 
    'x_main__mutmut_8': x_main__mutmut_8, 
    'x_main__mutmut_9': x_main__mutmut_9, 
    'x_main__mutmut_10': x_main__mutmut_10, 
    'x_main__mutmut_11': x_main__mutmut_11, 
    'x_main__mutmut_12': x_main__mutmut_12, 
    'x_main__mutmut_13': x_main__mutmut_13, 
    'x_main__mutmut_14': x_main__mutmut_14, 
    'x_main__mutmut_15': x_main__mutmut_15, 
    'x_main__mutmut_16': x_main__mutmut_16, 
    'x_main__mutmut_17': x_main__mutmut_17, 
    'x_main__mutmut_18': x_main__mutmut_18, 
    'x_main__mutmut_19': x_main__mutmut_19, 
    'x_main__mutmut_20': x_main__mutmut_20, 
    'x_main__mutmut_21': x_main__mutmut_21, 
    'x_main__mutmut_22': x_main__mutmut_22, 
    'x_main__mutmut_23': x_main__mutmut_23, 
    'x_main__mutmut_24': x_main__mutmut_24, 
    'x_main__mutmut_25': x_main__mutmut_25, 
    'x_main__mutmut_26': x_main__mutmut_26, 
    'x_main__mutmut_27': x_main__mutmut_27, 
    'x_main__mutmut_28': x_main__mutmut_28, 
    'x_main__mutmut_29': x_main__mutmut_29, 
    'x_main__mutmut_30': x_main__mutmut_30, 
    'x_main__mutmut_31': x_main__mutmut_31, 
    'x_main__mutmut_32': x_main__mutmut_32, 
    'x_main__mutmut_33': x_main__mutmut_33, 
    'x_main__mutmut_34': x_main__mutmut_34, 
    'x_main__mutmut_35': x_main__mutmut_35
}

def main(*args, **kwargs):
    result = _mutmut_trampoline(x_main__mutmut_orig, x_main__mutmut_mutants, args, kwargs)
    return result 

main.__signature__ = _mutmut_signature(x_main__mutmut_orig)
x_main__mutmut_orig.__name__ = 'x_main'


if __name__ == "__main__":
    main()
