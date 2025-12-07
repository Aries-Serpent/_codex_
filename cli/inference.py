#!/usr/bin/env python3
"""
Small CLI wrapper for invoking inference. Prompts are sanitized before any
rendering or echoing. Model invocation (if any) receives the original prompt
so model behavior is unchanged; sanitized output is used when the prompt might
be rendered to a user-facing HTML or log.
"""
import argparse
import sys
from pathlib import Path

# Add src to path for imports
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from codex_ml.safety import PromptSanitizer  # noqa: E402 - path must be modified first
from utils.sanitize import sanitize_prompt  # noqa: E402 - path must be modified first


def run_inference(prompt: str, sanitize: bool = True, strict: bool = True) -> tuple[str, str]:
    """
    Placeholder inference function. Replace or extend to call the real model.
    For safety, CLI will print sanitized prompt when echoing.

    Args:
        prompt: The user-provided prompt
        sanitize: Whether to sanitize the prompt
        strict: Whether to use strict mode (raise on unsafe) or redact

    Returns:
        Tuple of (safe_preview, result)
    """
    # Example: echo a safe preview, then "process" the original prompt
    safe_preview = sanitize_prompt(prompt)

    if sanitize:
        sanitizer = PromptSanitizer(strict=strict)
        try:
            prompt = sanitizer.sanitize(prompt)
        except ValueError as e:
            # In strict mode, unsafe prompts raise ValueError
            return f"ERROR: {e}", ""

    # Replace this with the real model call; keep original prompt to preserve semantics
    # result = model.generate(prompt)
    result = f"<processed>{prompt}</processed>"  # placeholder
    # If result might be rendered into HTML pages, ensure it is escaped there too.
    return safe_preview, result


def main(argv=None):
    parser = argparse.ArgumentParser(prog="inference.py", description="Run inference")
    parser.add_argument("--prompt", "-p", type=str, default="", help="User prompt")
    parser.add_argument(
        "--sanitize",
        action="store_true",
        default=True,
        help="Enable prompt sanitization (default: True)",
    )
    parser.add_argument(
        "--no-sanitize",
        action="store_false",
        dest="sanitize",
        help="Disable prompt sanitization (not recommended)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=True,
        help="Use strict sanitization mode (reject unsafe prompts)",
    )
    parser.add_argument(
        "--non-strict",
        action="store_false",
        dest="strict",
        help="Use non-strict mode (redact unsafe patterns)",
    )

    args = parser.parse_args(argv)

    safe_preview, result = run_inference(args.prompt, sanitize=args.sanitize, strict=args.strict)
    # Print sanitized preview to stdout for CI tests that check for sanitization
    print(safe_preview)
    if result:
        # Also print model result on separate line to avoid confusion in tests
        print(result)


if __name__ == "__main__":
    main(sys.argv[1:])
