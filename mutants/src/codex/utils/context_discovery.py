"""
Context discovery utilities for Codex session initialization.

Purpose:
  Automatically detect or prompt for required session context
  (PR number, branch name, user, commit hash) at session start.

References:
  - Analysis finding: CODEX-008 - PR number guessing mid-session
  - Best practice: Gather critical inputs upfront

Functions:
  - get_pr_number(): Attempt detection or prompt user
  - get_session_info(): Gather all context
  - discover_git_context(): Parse git state
"""

from __future__ import annotations

import logging
import os
import re
import shlex
import subprocess
from typing import Any, Optional

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


def x_run_git_command__mutmut_orig(cmd: str) -> Optional[str]:
    """Execute git command and return output. Returns None on error.

    Args:
        cmd: Git command string (e.g., "git rev-parse --abbrev-ref HEAD")

    Returns:
        Command stdout stripped, or None on error/non-zero exit.
    """
    try:
        # Parse the command string into a list to avoid shell=False
        cmd_list = shlex.split(cmd)
        result = subprocess.run(
            cmd_list,
            shell=False,  # Explicitly disable shell for security
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.warning(f"Git command failed: {cmd} - {e}")
        return None


def x_run_git_command__mutmut_1(cmd: str) -> Optional[str]:
    """Execute git command and return output. Returns None on error.

    Args:
        cmd: Git command string (e.g., "git rev-parse --abbrev-ref HEAD")

    Returns:
        Command stdout stripped, or None on error/non-zero exit.
    """
    try:
        # Parse the command string into a list to avoid shell=False
        cmd_list = None
        result = subprocess.run(
            cmd_list,
            shell=False,  # Explicitly disable shell for security
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.warning(f"Git command failed: {cmd} - {e}")
        return None


def x_run_git_command__mutmut_2(cmd: str) -> Optional[str]:
    """Execute git command and return output. Returns None on error.

    Args:
        cmd: Git command string (e.g., "git rev-parse --abbrev-ref HEAD")

    Returns:
        Command stdout stripped, or None on error/non-zero exit.
    """
    try:
        # Parse the command string into a list to avoid shell=False
        cmd_list = shlex.split(None)
        result = subprocess.run(
            cmd_list,
            shell=False,  # Explicitly disable shell for security
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.warning(f"Git command failed: {cmd} - {e}")
        return None


def x_run_git_command__mutmut_3(cmd: str) -> Optional[str]:
    """Execute git command and return output. Returns None on error.

    Args:
        cmd: Git command string (e.g., "git rev-parse --abbrev-ref HEAD")

    Returns:
        Command stdout stripped, or None on error/non-zero exit.
    """
    try:
        # Parse the command string into a list to avoid shell=False
        cmd_list = shlex.split(cmd)
        result = None
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.warning(f"Git command failed: {cmd} - {e}")
        return None


def x_run_git_command__mutmut_4(cmd: str) -> Optional[str]:
    """Execute git command and return output. Returns None on error.

    Args:
        cmd: Git command string (e.g., "git rev-parse --abbrev-ref HEAD")

    Returns:
        Command stdout stripped, or None on error/non-zero exit.
    """
    try:
        # Parse the command string into a list to avoid shell=False
        cmd_list = shlex.split(cmd)
        result = subprocess.run(
            None,
            shell=False,  # Explicitly disable shell for security
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.warning(f"Git command failed: {cmd} - {e}")
        return None


def x_run_git_command__mutmut_5(cmd: str) -> Optional[str]:
    """Execute git command and return output. Returns None on error.

    Args:
        cmd: Git command string (e.g., "git rev-parse --abbrev-ref HEAD")

    Returns:
        Command stdout stripped, or None on error/non-zero exit.
    """
    try:
        # Parse the command string into a list to avoid shell=False
        cmd_list = shlex.split(cmd)
        result = subprocess.run(
            cmd_list,
            shell=None,  # Explicitly disable shell for security
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.warning(f"Git command failed: {cmd} - {e}")
        return None


def x_run_git_command__mutmut_6(cmd: str) -> Optional[str]:
    """Execute git command and return output. Returns None on error.

    Args:
        cmd: Git command string (e.g., "git rev-parse --abbrev-ref HEAD")

    Returns:
        Command stdout stripped, or None on error/non-zero exit.
    """
    try:
        # Parse the command string into a list to avoid shell=False
        cmd_list = shlex.split(cmd)
        result = subprocess.run(
            cmd_list,
            shell=False,  # Explicitly disable shell for security
            capture_output=None,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.warning(f"Git command failed: {cmd} - {e}")
        return None


def x_run_git_command__mutmut_7(cmd: str) -> Optional[str]:
    """Execute git command and return output. Returns None on error.

    Args:
        cmd: Git command string (e.g., "git rev-parse --abbrev-ref HEAD")

    Returns:
        Command stdout stripped, or None on error/non-zero exit.
    """
    try:
        # Parse the command string into a list to avoid shell=False
        cmd_list = shlex.split(cmd)
        result = subprocess.run(
            cmd_list,
            shell=False,  # Explicitly disable shell for security
            capture_output=True,
            text=None,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.warning(f"Git command failed: {cmd} - {e}")
        return None


def x_run_git_command__mutmut_8(cmd: str) -> Optional[str]:
    """Execute git command and return output. Returns None on error.

    Args:
        cmd: Git command string (e.g., "git rev-parse --abbrev-ref HEAD")

    Returns:
        Command stdout stripped, or None on error/non-zero exit.
    """
    try:
        # Parse the command string into a list to avoid shell=False
        cmd_list = shlex.split(cmd)
        result = subprocess.run(
            cmd_list,
            shell=False,  # Explicitly disable shell for security
            capture_output=True,
            text=True,
            timeout=None,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.warning(f"Git command failed: {cmd} - {e}")
        return None


def x_run_git_command__mutmut_9(cmd: str) -> Optional[str]:
    """Execute git command and return output. Returns None on error.

    Args:
        cmd: Git command string (e.g., "git rev-parse --abbrev-ref HEAD")

    Returns:
        Command stdout stripped, or None on error/non-zero exit.
    """
    try:
        # Parse the command string into a list to avoid shell=False
        cmd_list = shlex.split(cmd)
        result = subprocess.run(
            shell=False,  # Explicitly disable shell for security
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.warning(f"Git command failed: {cmd} - {e}")
        return None


def x_run_git_command__mutmut_10(cmd: str) -> Optional[str]:
    """Execute git command and return output. Returns None on error.

    Args:
        cmd: Git command string (e.g., "git rev-parse --abbrev-ref HEAD")

    Returns:
        Command stdout stripped, or None on error/non-zero exit.
    """
    try:
        # Parse the command string into a list to avoid shell=False
        cmd_list = shlex.split(cmd)
        result = subprocess.run(
            cmd_list,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.warning(f"Git command failed: {cmd} - {e}")
        return None


def x_run_git_command__mutmut_11(cmd: str) -> Optional[str]:
    """Execute git command and return output. Returns None on error.

    Args:
        cmd: Git command string (e.g., "git rev-parse --abbrev-ref HEAD")

    Returns:
        Command stdout stripped, or None on error/non-zero exit.
    """
    try:
        # Parse the command string into a list to avoid shell=False
        cmd_list = shlex.split(cmd)
        result = subprocess.run(
            cmd_list,
            shell=False,  # Explicitly disable shell for security
            text=True,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.warning(f"Git command failed: {cmd} - {e}")
        return None


def x_run_git_command__mutmut_12(cmd: str) -> Optional[str]:
    """Execute git command and return output. Returns None on error.

    Args:
        cmd: Git command string (e.g., "git rev-parse --abbrev-ref HEAD")

    Returns:
        Command stdout stripped, or None on error/non-zero exit.
    """
    try:
        # Parse the command string into a list to avoid shell=False
        cmd_list = shlex.split(cmd)
        result = subprocess.run(
            cmd_list,
            shell=False,  # Explicitly disable shell for security
            capture_output=True,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.warning(f"Git command failed: {cmd} - {e}")
        return None


def x_run_git_command__mutmut_13(cmd: str) -> Optional[str]:
    """Execute git command and return output. Returns None on error.

    Args:
        cmd: Git command string (e.g., "git rev-parse --abbrev-ref HEAD")

    Returns:
        Command stdout stripped, or None on error/non-zero exit.
    """
    try:
        # Parse the command string into a list to avoid shell=False
        cmd_list = shlex.split(cmd)
        result = subprocess.run(
            cmd_list,
            shell=False,  # Explicitly disable shell for security
            capture_output=True,
            text=True,
            )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.warning(f"Git command failed: {cmd} - {e}")
        return None


def x_run_git_command__mutmut_14(cmd: str) -> Optional[str]:
    """Execute git command and return output. Returns None on error.

    Args:
        cmd: Git command string (e.g., "git rev-parse --abbrev-ref HEAD")

    Returns:
        Command stdout stripped, or None on error/non-zero exit.
    """
    try:
        # Parse the command string into a list to avoid shell=False
        cmd_list = shlex.split(cmd)
        result = subprocess.run(
            cmd_list,
            shell=True,  # Explicitly disable shell for security
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.warning(f"Git command failed: {cmd} - {e}")
        return None


def x_run_git_command__mutmut_15(cmd: str) -> Optional[str]:
    """Execute git command and return output. Returns None on error.

    Args:
        cmd: Git command string (e.g., "git rev-parse --abbrev-ref HEAD")

    Returns:
        Command stdout stripped, or None on error/non-zero exit.
    """
    try:
        # Parse the command string into a list to avoid shell=False
        cmd_list = shlex.split(cmd)
        result = subprocess.run(
            cmd_list,
            shell=False,  # Explicitly disable shell for security
            capture_output=False,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.warning(f"Git command failed: {cmd} - {e}")
        return None


def x_run_git_command__mutmut_16(cmd: str) -> Optional[str]:
    """Execute git command and return output. Returns None on error.

    Args:
        cmd: Git command string (e.g., "git rev-parse --abbrev-ref HEAD")

    Returns:
        Command stdout stripped, or None on error/non-zero exit.
    """
    try:
        # Parse the command string into a list to avoid shell=False
        cmd_list = shlex.split(cmd)
        result = subprocess.run(
            cmd_list,
            shell=False,  # Explicitly disable shell for security
            capture_output=True,
            text=False,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.warning(f"Git command failed: {cmd} - {e}")
        return None


def x_run_git_command__mutmut_17(cmd: str) -> Optional[str]:
    """Execute git command and return output. Returns None on error.

    Args:
        cmd: Git command string (e.g., "git rev-parse --abbrev-ref HEAD")

    Returns:
        Command stdout stripped, or None on error/non-zero exit.
    """
    try:
        # Parse the command string into a list to avoid shell=False
        cmd_list = shlex.split(cmd)
        result = subprocess.run(
            cmd_list,
            shell=False,  # Explicitly disable shell for security
            capture_output=True,
            text=True,
            timeout=6,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.warning(f"Git command failed: {cmd} - {e}")
        return None


def x_run_git_command__mutmut_18(cmd: str) -> Optional[str]:
    """Execute git command and return output. Returns None on error.

    Args:
        cmd: Git command string (e.g., "git rev-parse --abbrev-ref HEAD")

    Returns:
        Command stdout stripped, or None on error/non-zero exit.
    """
    try:
        # Parse the command string into a list to avoid shell=False
        cmd_list = shlex.split(cmd)
        result = subprocess.run(
            cmd_list,
            shell=False,  # Explicitly disable shell for security
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode != 0 else None
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.warning(f"Git command failed: {cmd} - {e}")
        return None


def x_run_git_command__mutmut_19(cmd: str) -> Optional[str]:
    """Execute git command and return output. Returns None on error.

    Args:
        cmd: Git command string (e.g., "git rev-parse --abbrev-ref HEAD")

    Returns:
        Command stdout stripped, or None on error/non-zero exit.
    """
    try:
        # Parse the command string into a list to avoid shell=False
        cmd_list = shlex.split(cmd)
        result = subprocess.run(
            cmd_list,
            shell=False,  # Explicitly disable shell for security
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 1 else None
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.warning(f"Git command failed: {cmd} - {e}")
        return None


def x_run_git_command__mutmut_20(cmd: str) -> Optional[str]:
    """Execute git command and return output. Returns None on error.

    Args:
        cmd: Git command string (e.g., "git rev-parse --abbrev-ref HEAD")

    Returns:
        Command stdout stripped, or None on error/non-zero exit.
    """
    try:
        # Parse the command string into a list to avoid shell=False
        cmd_list = shlex.split(cmd)
        result = subprocess.run(
            cmd_list,
            shell=False,  # Explicitly disable shell for security
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception as e:
        logger.debug(None)
        logger.warning(f"Git command failed: {cmd} - {e}")
        return None


def x_run_git_command__mutmut_21(cmd: str) -> Optional[str]:
    """Execute git command and return output. Returns None on error.

    Args:
        cmd: Git command string (e.g., "git rev-parse --abbrev-ref HEAD")

    Returns:
        Command stdout stripped, or None on error/non-zero exit.
    """
    try:
        # Parse the command string into a list to avoid shell=False
        cmd_list = shlex.split(cmd)
        result = subprocess.run(
            cmd_list,
            shell=False,  # Explicitly disable shell for security
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.warning(None)
        return None

x_run_git_command__mutmut_mutants : ClassVar[MutantDict] = {
'x_run_git_command__mutmut_1': x_run_git_command__mutmut_1, 
    'x_run_git_command__mutmut_2': x_run_git_command__mutmut_2, 
    'x_run_git_command__mutmut_3': x_run_git_command__mutmut_3, 
    'x_run_git_command__mutmut_4': x_run_git_command__mutmut_4, 
    'x_run_git_command__mutmut_5': x_run_git_command__mutmut_5, 
    'x_run_git_command__mutmut_6': x_run_git_command__mutmut_6, 
    'x_run_git_command__mutmut_7': x_run_git_command__mutmut_7, 
    'x_run_git_command__mutmut_8': x_run_git_command__mutmut_8, 
    'x_run_git_command__mutmut_9': x_run_git_command__mutmut_9, 
    'x_run_git_command__mutmut_10': x_run_git_command__mutmut_10, 
    'x_run_git_command__mutmut_11': x_run_git_command__mutmut_11, 
    'x_run_git_command__mutmut_12': x_run_git_command__mutmut_12, 
    'x_run_git_command__mutmut_13': x_run_git_command__mutmut_13, 
    'x_run_git_command__mutmut_14': x_run_git_command__mutmut_14, 
    'x_run_git_command__mutmut_15': x_run_git_command__mutmut_15, 
    'x_run_git_command__mutmut_16': x_run_git_command__mutmut_16, 
    'x_run_git_command__mutmut_17': x_run_git_command__mutmut_17, 
    'x_run_git_command__mutmut_18': x_run_git_command__mutmut_18, 
    'x_run_git_command__mutmut_19': x_run_git_command__mutmut_19, 
    'x_run_git_command__mutmut_20': x_run_git_command__mutmut_20, 
    'x_run_git_command__mutmut_21': x_run_git_command__mutmut_21
}

def run_git_command(*args, **kwargs):
    result = _mutmut_trampoline(x_run_git_command__mutmut_orig, x_run_git_command__mutmut_mutants, args, kwargs)
    return result 

run_git_command.__signature__ = _mutmut_signature(x_run_git_command__mutmut_orig)
x_run_git_command__mutmut_orig.__name__ = 'x_run_git_command'


def x_get_pr_number__mutmut_orig(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_1(interactive: bool = False) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_2(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["XXCODEX_PRXX", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_3(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["codex_pr", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_4(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "XXCI_MERGE_REQUEST_IIDXX", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_5(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "ci_merge_request_iid", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_6(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "XXGITHUB_PR_NUMBERXX"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_7(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "github_pr_number"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_8(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = None
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_9(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(None)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_10(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(None)
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_11(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = None
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_12(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command(None)
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_13(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("XXgit rev-parse --abbrev-ref HEADXX")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_14(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref head")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_15(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("GIT REV-PARSE --ABBREV-REF HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_16(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = None
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_17(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(None, branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_18(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", None)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_19(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_20(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", )
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_21(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"XX[/-]?(?:pr|PR)?-?(\d+)XX", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_22(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|pr)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_23(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:PR|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_24(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = None
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_25(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(None)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_26(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(2)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_27(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(None)
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_28(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = None
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_29(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command(None)
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_30(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("XXgit log -1 --pretty=%BXX")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_31(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%b")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_32(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("GIT LOG -1 --PRETTY=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_33(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = None  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_34(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(None, commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_35(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", None)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_36(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_37(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", )  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_38(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"XX#(\d{4,})XX", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_39(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = None
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_40(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(None)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_41(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(2)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_42(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(None)
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_43(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive or os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_44(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(None):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_45(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(1):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_46(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = None
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_47(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input(None).strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_48(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("XX📋 PR number (or 'N/A' if unknown): XX").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_49(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 pr number (or 'n/a' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_50(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR NUMBER (OR 'N/A' IF UNKNOWN): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_51(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = None
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_52(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "XXN/AXX"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_53(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "n/a"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_54(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(None)
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_55(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(None)
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_56(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(None, exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_57(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=None)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_58(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_59(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", )
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_60(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=False)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_61(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning(None)
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_62(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("XXCannot prompt (no TTY), using N/AXX")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_63(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("cannot prompt (no tty), using n/a")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_64(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("CANNOT PROMPT (NO TTY), USING N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_65(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "XXN/AXX"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_66(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "n/a"
    else:
        logger.info("No interactive mode, using N/A")
        return "N/A"


def x_get_pr_number__mutmut_67(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info(None)
        return "N/A"


def x_get_pr_number__mutmut_68(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("XXNo interactive mode, using N/AXX")
        return "N/A"


def x_get_pr_number__mutmut_69(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("no interactive mode, using n/a")
        return "N/A"


def x_get_pr_number__mutmut_70(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("NO INTERACTIVE MODE, USING N/A")
        return "N/A"


def x_get_pr_number__mutmut_71(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "XXN/AXX"


def x_get_pr_number__mutmut_72(interactive: bool = True) -> str:
    """
    Attempt to discover PR number via:
      1. Environment variables (CODEX_PR, CI_MERGE_REQUEST_IID)
      2. Git branch name parsing (pr-1926, feature/PR-1926, etc.)
      3. Recent commit message parsing
      4. User prompt (if interactive)

    Returns: PR number as string, or "N/A" if not found
    """
    # 1. Check environment variables
    for env_var in ["CODEX_PR", "CI_MERGE_REQUEST_IID", "GITHUB_PR_NUMBER"]:
        value = os.getenv(env_var)
        if value:
            logger.info(f"PR number discovered from env: {env_var}={value}")
            return value

    # 2. Parse git branch name
    branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if branch:
        # Match patterns: pr-1926, feature/PR-1926, feature/1926, etc.
        match = re.search(r"[/-]?(?:pr|PR)?-?(\d+)", branch)
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from branch: {branch} → {pr_num}")
            return pr_num

    # 3. Parse recent commit message
    commit_msg = run_git_command("git log -1 --pretty=%B")
    if commit_msg:
        match = re.search(r"#(\d{4,})", commit_msg)  # Look for #1926 pattern
        if match:
            pr_num = match.group(1)
            logger.info(f"PR number extracted from commit: {pr_num}")
            return pr_num

    # 4. Prompt user if interactive
    if interactive and os.isatty(0):  # Check if stdin is TTY
        try:
            user_input = input("📋 PR number (or 'N/A' if unknown): ").strip()
            pr_num = user_input if user_input else "N/A"
            logger.info(f"PR number provided by user: {pr_num}")
            return pr_num
        except EOFError as e:
            logger.debug(f"EOFError: {e}")
            logger.warning(f"EOFError: {e}", exc_info=True)
            logger.warning("Cannot prompt (no TTY), using N/A")
            return "N/A"
    else:
        logger.info("No interactive mode, using N/A")
        return "n/a"

x_get_pr_number__mutmut_mutants : ClassVar[MutantDict] = {
'x_get_pr_number__mutmut_1': x_get_pr_number__mutmut_1, 
    'x_get_pr_number__mutmut_2': x_get_pr_number__mutmut_2, 
    'x_get_pr_number__mutmut_3': x_get_pr_number__mutmut_3, 
    'x_get_pr_number__mutmut_4': x_get_pr_number__mutmut_4, 
    'x_get_pr_number__mutmut_5': x_get_pr_number__mutmut_5, 
    'x_get_pr_number__mutmut_6': x_get_pr_number__mutmut_6, 
    'x_get_pr_number__mutmut_7': x_get_pr_number__mutmut_7, 
    'x_get_pr_number__mutmut_8': x_get_pr_number__mutmut_8, 
    'x_get_pr_number__mutmut_9': x_get_pr_number__mutmut_9, 
    'x_get_pr_number__mutmut_10': x_get_pr_number__mutmut_10, 
    'x_get_pr_number__mutmut_11': x_get_pr_number__mutmut_11, 
    'x_get_pr_number__mutmut_12': x_get_pr_number__mutmut_12, 
    'x_get_pr_number__mutmut_13': x_get_pr_number__mutmut_13, 
    'x_get_pr_number__mutmut_14': x_get_pr_number__mutmut_14, 
    'x_get_pr_number__mutmut_15': x_get_pr_number__mutmut_15, 
    'x_get_pr_number__mutmut_16': x_get_pr_number__mutmut_16, 
    'x_get_pr_number__mutmut_17': x_get_pr_number__mutmut_17, 
    'x_get_pr_number__mutmut_18': x_get_pr_number__mutmut_18, 
    'x_get_pr_number__mutmut_19': x_get_pr_number__mutmut_19, 
    'x_get_pr_number__mutmut_20': x_get_pr_number__mutmut_20, 
    'x_get_pr_number__mutmut_21': x_get_pr_number__mutmut_21, 
    'x_get_pr_number__mutmut_22': x_get_pr_number__mutmut_22, 
    'x_get_pr_number__mutmut_23': x_get_pr_number__mutmut_23, 
    'x_get_pr_number__mutmut_24': x_get_pr_number__mutmut_24, 
    'x_get_pr_number__mutmut_25': x_get_pr_number__mutmut_25, 
    'x_get_pr_number__mutmut_26': x_get_pr_number__mutmut_26, 
    'x_get_pr_number__mutmut_27': x_get_pr_number__mutmut_27, 
    'x_get_pr_number__mutmut_28': x_get_pr_number__mutmut_28, 
    'x_get_pr_number__mutmut_29': x_get_pr_number__mutmut_29, 
    'x_get_pr_number__mutmut_30': x_get_pr_number__mutmut_30, 
    'x_get_pr_number__mutmut_31': x_get_pr_number__mutmut_31, 
    'x_get_pr_number__mutmut_32': x_get_pr_number__mutmut_32, 
    'x_get_pr_number__mutmut_33': x_get_pr_number__mutmut_33, 
    'x_get_pr_number__mutmut_34': x_get_pr_number__mutmut_34, 
    'x_get_pr_number__mutmut_35': x_get_pr_number__mutmut_35, 
    'x_get_pr_number__mutmut_36': x_get_pr_number__mutmut_36, 
    'x_get_pr_number__mutmut_37': x_get_pr_number__mutmut_37, 
    'x_get_pr_number__mutmut_38': x_get_pr_number__mutmut_38, 
    'x_get_pr_number__mutmut_39': x_get_pr_number__mutmut_39, 
    'x_get_pr_number__mutmut_40': x_get_pr_number__mutmut_40, 
    'x_get_pr_number__mutmut_41': x_get_pr_number__mutmut_41, 
    'x_get_pr_number__mutmut_42': x_get_pr_number__mutmut_42, 
    'x_get_pr_number__mutmut_43': x_get_pr_number__mutmut_43, 
    'x_get_pr_number__mutmut_44': x_get_pr_number__mutmut_44, 
    'x_get_pr_number__mutmut_45': x_get_pr_number__mutmut_45, 
    'x_get_pr_number__mutmut_46': x_get_pr_number__mutmut_46, 
    'x_get_pr_number__mutmut_47': x_get_pr_number__mutmut_47, 
    'x_get_pr_number__mutmut_48': x_get_pr_number__mutmut_48, 
    'x_get_pr_number__mutmut_49': x_get_pr_number__mutmut_49, 
    'x_get_pr_number__mutmut_50': x_get_pr_number__mutmut_50, 
    'x_get_pr_number__mutmut_51': x_get_pr_number__mutmut_51, 
    'x_get_pr_number__mutmut_52': x_get_pr_number__mutmut_52, 
    'x_get_pr_number__mutmut_53': x_get_pr_number__mutmut_53, 
    'x_get_pr_number__mutmut_54': x_get_pr_number__mutmut_54, 
    'x_get_pr_number__mutmut_55': x_get_pr_number__mutmut_55, 
    'x_get_pr_number__mutmut_56': x_get_pr_number__mutmut_56, 
    'x_get_pr_number__mutmut_57': x_get_pr_number__mutmut_57, 
    'x_get_pr_number__mutmut_58': x_get_pr_number__mutmut_58, 
    'x_get_pr_number__mutmut_59': x_get_pr_number__mutmut_59, 
    'x_get_pr_number__mutmut_60': x_get_pr_number__mutmut_60, 
    'x_get_pr_number__mutmut_61': x_get_pr_number__mutmut_61, 
    'x_get_pr_number__mutmut_62': x_get_pr_number__mutmut_62, 
    'x_get_pr_number__mutmut_63': x_get_pr_number__mutmut_63, 
    'x_get_pr_number__mutmut_64': x_get_pr_number__mutmut_64, 
    'x_get_pr_number__mutmut_65': x_get_pr_number__mutmut_65, 
    'x_get_pr_number__mutmut_66': x_get_pr_number__mutmut_66, 
    'x_get_pr_number__mutmut_67': x_get_pr_number__mutmut_67, 
    'x_get_pr_number__mutmut_68': x_get_pr_number__mutmut_68, 
    'x_get_pr_number__mutmut_69': x_get_pr_number__mutmut_69, 
    'x_get_pr_number__mutmut_70': x_get_pr_number__mutmut_70, 
    'x_get_pr_number__mutmut_71': x_get_pr_number__mutmut_71, 
    'x_get_pr_number__mutmut_72': x_get_pr_number__mutmut_72
}

def get_pr_number(*args, **kwargs):
    result = _mutmut_trampoline(x_get_pr_number__mutmut_orig, x_get_pr_number__mutmut_mutants, args, kwargs)
    return result 

get_pr_number.__signature__ = _mutmut_signature(x_get_pr_number__mutmut_orig)
x_get_pr_number__mutmut_orig.__name__ = 'x_get_pr_number'


def x_discover_git_context__mutmut_orig() -> dict[str, Optional[str]]:
    """Discover git context: branch, commit hash, short hash, commit author."""
    return {
        "branch": run_git_command("git rev-parse --abbrev-ref HEAD"),
        "commit": run_git_command("git rev-parse HEAD"),
        "short_commit": run_git_command("git rev-parse --short HEAD"),
        "author": run_git_command("git config user.name"),
        "email": run_git_command("git config user.email"),
    }


def x_discover_git_context__mutmut_1() -> dict[str, Optional[str]]:
    """Discover git context: branch, commit hash, short hash, commit author."""
    return {
        "XXbranchXX": run_git_command("git rev-parse --abbrev-ref HEAD"),
        "commit": run_git_command("git rev-parse HEAD"),
        "short_commit": run_git_command("git rev-parse --short HEAD"),
        "author": run_git_command("git config user.name"),
        "email": run_git_command("git config user.email"),
    }


def x_discover_git_context__mutmut_2() -> dict[str, Optional[str]]:
    """Discover git context: branch, commit hash, short hash, commit author."""
    return {
        "BRANCH": run_git_command("git rev-parse --abbrev-ref HEAD"),
        "commit": run_git_command("git rev-parse HEAD"),
        "short_commit": run_git_command("git rev-parse --short HEAD"),
        "author": run_git_command("git config user.name"),
        "email": run_git_command("git config user.email"),
    }


def x_discover_git_context__mutmut_3() -> dict[str, Optional[str]]:
    """Discover git context: branch, commit hash, short hash, commit author."""
    return {
        "branch": run_git_command(None),
        "commit": run_git_command("git rev-parse HEAD"),
        "short_commit": run_git_command("git rev-parse --short HEAD"),
        "author": run_git_command("git config user.name"),
        "email": run_git_command("git config user.email"),
    }


def x_discover_git_context__mutmut_4() -> dict[str, Optional[str]]:
    """Discover git context: branch, commit hash, short hash, commit author."""
    return {
        "branch": run_git_command("XXgit rev-parse --abbrev-ref HEADXX"),
        "commit": run_git_command("git rev-parse HEAD"),
        "short_commit": run_git_command("git rev-parse --short HEAD"),
        "author": run_git_command("git config user.name"),
        "email": run_git_command("git config user.email"),
    }


def x_discover_git_context__mutmut_5() -> dict[str, Optional[str]]:
    """Discover git context: branch, commit hash, short hash, commit author."""
    return {
        "branch": run_git_command("git rev-parse --abbrev-ref head"),
        "commit": run_git_command("git rev-parse HEAD"),
        "short_commit": run_git_command("git rev-parse --short HEAD"),
        "author": run_git_command("git config user.name"),
        "email": run_git_command("git config user.email"),
    }


def x_discover_git_context__mutmut_6() -> dict[str, Optional[str]]:
    """Discover git context: branch, commit hash, short hash, commit author."""
    return {
        "branch": run_git_command("GIT REV-PARSE --ABBREV-REF HEAD"),
        "commit": run_git_command("git rev-parse HEAD"),
        "short_commit": run_git_command("git rev-parse --short HEAD"),
        "author": run_git_command("git config user.name"),
        "email": run_git_command("git config user.email"),
    }


def x_discover_git_context__mutmut_7() -> dict[str, Optional[str]]:
    """Discover git context: branch, commit hash, short hash, commit author."""
    return {
        "branch": run_git_command("git rev-parse --abbrev-ref HEAD"),
        "XXcommitXX": run_git_command("git rev-parse HEAD"),
        "short_commit": run_git_command("git rev-parse --short HEAD"),
        "author": run_git_command("git config user.name"),
        "email": run_git_command("git config user.email"),
    }


def x_discover_git_context__mutmut_8() -> dict[str, Optional[str]]:
    """Discover git context: branch, commit hash, short hash, commit author."""
    return {
        "branch": run_git_command("git rev-parse --abbrev-ref HEAD"),
        "COMMIT": run_git_command("git rev-parse HEAD"),
        "short_commit": run_git_command("git rev-parse --short HEAD"),
        "author": run_git_command("git config user.name"),
        "email": run_git_command("git config user.email"),
    }


def x_discover_git_context__mutmut_9() -> dict[str, Optional[str]]:
    """Discover git context: branch, commit hash, short hash, commit author."""
    return {
        "branch": run_git_command("git rev-parse --abbrev-ref HEAD"),
        "commit": run_git_command(None),
        "short_commit": run_git_command("git rev-parse --short HEAD"),
        "author": run_git_command("git config user.name"),
        "email": run_git_command("git config user.email"),
    }


def x_discover_git_context__mutmut_10() -> dict[str, Optional[str]]:
    """Discover git context: branch, commit hash, short hash, commit author."""
    return {
        "branch": run_git_command("git rev-parse --abbrev-ref HEAD"),
        "commit": run_git_command("XXgit rev-parse HEADXX"),
        "short_commit": run_git_command("git rev-parse --short HEAD"),
        "author": run_git_command("git config user.name"),
        "email": run_git_command("git config user.email"),
    }


def x_discover_git_context__mutmut_11() -> dict[str, Optional[str]]:
    """Discover git context: branch, commit hash, short hash, commit author."""
    return {
        "branch": run_git_command("git rev-parse --abbrev-ref HEAD"),
        "commit": run_git_command("git rev-parse head"),
        "short_commit": run_git_command("git rev-parse --short HEAD"),
        "author": run_git_command("git config user.name"),
        "email": run_git_command("git config user.email"),
    }


def x_discover_git_context__mutmut_12() -> dict[str, Optional[str]]:
    """Discover git context: branch, commit hash, short hash, commit author."""
    return {
        "branch": run_git_command("git rev-parse --abbrev-ref HEAD"),
        "commit": run_git_command("GIT REV-PARSE HEAD"),
        "short_commit": run_git_command("git rev-parse --short HEAD"),
        "author": run_git_command("git config user.name"),
        "email": run_git_command("git config user.email"),
    }


def x_discover_git_context__mutmut_13() -> dict[str, Optional[str]]:
    """Discover git context: branch, commit hash, short hash, commit author."""
    return {
        "branch": run_git_command("git rev-parse --abbrev-ref HEAD"),
        "commit": run_git_command("git rev-parse HEAD"),
        "XXshort_commitXX": run_git_command("git rev-parse --short HEAD"),
        "author": run_git_command("git config user.name"),
        "email": run_git_command("git config user.email"),
    }


def x_discover_git_context__mutmut_14() -> dict[str, Optional[str]]:
    """Discover git context: branch, commit hash, short hash, commit author."""
    return {
        "branch": run_git_command("git rev-parse --abbrev-ref HEAD"),
        "commit": run_git_command("git rev-parse HEAD"),
        "SHORT_COMMIT": run_git_command("git rev-parse --short HEAD"),
        "author": run_git_command("git config user.name"),
        "email": run_git_command("git config user.email"),
    }


def x_discover_git_context__mutmut_15() -> dict[str, Optional[str]]:
    """Discover git context: branch, commit hash, short hash, commit author."""
    return {
        "branch": run_git_command("git rev-parse --abbrev-ref HEAD"),
        "commit": run_git_command("git rev-parse HEAD"),
        "short_commit": run_git_command(None),
        "author": run_git_command("git config user.name"),
        "email": run_git_command("git config user.email"),
    }


def x_discover_git_context__mutmut_16() -> dict[str, Optional[str]]:
    """Discover git context: branch, commit hash, short hash, commit author."""
    return {
        "branch": run_git_command("git rev-parse --abbrev-ref HEAD"),
        "commit": run_git_command("git rev-parse HEAD"),
        "short_commit": run_git_command("XXgit rev-parse --short HEADXX"),
        "author": run_git_command("git config user.name"),
        "email": run_git_command("git config user.email"),
    }


def x_discover_git_context__mutmut_17() -> dict[str, Optional[str]]:
    """Discover git context: branch, commit hash, short hash, commit author."""
    return {
        "branch": run_git_command("git rev-parse --abbrev-ref HEAD"),
        "commit": run_git_command("git rev-parse HEAD"),
        "short_commit": run_git_command("git rev-parse --short head"),
        "author": run_git_command("git config user.name"),
        "email": run_git_command("git config user.email"),
    }


def x_discover_git_context__mutmut_18() -> dict[str, Optional[str]]:
    """Discover git context: branch, commit hash, short hash, commit author."""
    return {
        "branch": run_git_command("git rev-parse --abbrev-ref HEAD"),
        "commit": run_git_command("git rev-parse HEAD"),
        "short_commit": run_git_command("GIT REV-PARSE --SHORT HEAD"),
        "author": run_git_command("git config user.name"),
        "email": run_git_command("git config user.email"),
    }


def x_discover_git_context__mutmut_19() -> dict[str, Optional[str]]:
    """Discover git context: branch, commit hash, short hash, commit author."""
    return {
        "branch": run_git_command("git rev-parse --abbrev-ref HEAD"),
        "commit": run_git_command("git rev-parse HEAD"),
        "short_commit": run_git_command("git rev-parse --short HEAD"),
        "XXauthorXX": run_git_command("git config user.name"),
        "email": run_git_command("git config user.email"),
    }


def x_discover_git_context__mutmut_20() -> dict[str, Optional[str]]:
    """Discover git context: branch, commit hash, short hash, commit author."""
    return {
        "branch": run_git_command("git rev-parse --abbrev-ref HEAD"),
        "commit": run_git_command("git rev-parse HEAD"),
        "short_commit": run_git_command("git rev-parse --short HEAD"),
        "AUTHOR": run_git_command("git config user.name"),
        "email": run_git_command("git config user.email"),
    }


def x_discover_git_context__mutmut_21() -> dict[str, Optional[str]]:
    """Discover git context: branch, commit hash, short hash, commit author."""
    return {
        "branch": run_git_command("git rev-parse --abbrev-ref HEAD"),
        "commit": run_git_command("git rev-parse HEAD"),
        "short_commit": run_git_command("git rev-parse --short HEAD"),
        "author": run_git_command(None),
        "email": run_git_command("git config user.email"),
    }


def x_discover_git_context__mutmut_22() -> dict[str, Optional[str]]:
    """Discover git context: branch, commit hash, short hash, commit author."""
    return {
        "branch": run_git_command("git rev-parse --abbrev-ref HEAD"),
        "commit": run_git_command("git rev-parse HEAD"),
        "short_commit": run_git_command("git rev-parse --short HEAD"),
        "author": run_git_command("XXgit config user.nameXX"),
        "email": run_git_command("git config user.email"),
    }


def x_discover_git_context__mutmut_23() -> dict[str, Optional[str]]:
    """Discover git context: branch, commit hash, short hash, commit author."""
    return {
        "branch": run_git_command("git rev-parse --abbrev-ref HEAD"),
        "commit": run_git_command("git rev-parse HEAD"),
        "short_commit": run_git_command("git rev-parse --short HEAD"),
        "author": run_git_command("GIT CONFIG USER.NAME"),
        "email": run_git_command("git config user.email"),
    }


def x_discover_git_context__mutmut_24() -> dict[str, Optional[str]]:
    """Discover git context: branch, commit hash, short hash, commit author."""
    return {
        "branch": run_git_command("git rev-parse --abbrev-ref HEAD"),
        "commit": run_git_command("git rev-parse HEAD"),
        "short_commit": run_git_command("git rev-parse --short HEAD"),
        "author": run_git_command("git config user.name"),
        "XXemailXX": run_git_command("git config user.email"),
    }


def x_discover_git_context__mutmut_25() -> dict[str, Optional[str]]:
    """Discover git context: branch, commit hash, short hash, commit author."""
    return {
        "branch": run_git_command("git rev-parse --abbrev-ref HEAD"),
        "commit": run_git_command("git rev-parse HEAD"),
        "short_commit": run_git_command("git rev-parse --short HEAD"),
        "author": run_git_command("git config user.name"),
        "EMAIL": run_git_command("git config user.email"),
    }


def x_discover_git_context__mutmut_26() -> dict[str, Optional[str]]:
    """Discover git context: branch, commit hash, short hash, commit author."""
    return {
        "branch": run_git_command("git rev-parse --abbrev-ref HEAD"),
        "commit": run_git_command("git rev-parse HEAD"),
        "short_commit": run_git_command("git rev-parse --short HEAD"),
        "author": run_git_command("git config user.name"),
        "email": run_git_command(None),
    }


def x_discover_git_context__mutmut_27() -> dict[str, Optional[str]]:
    """Discover git context: branch, commit hash, short hash, commit author."""
    return {
        "branch": run_git_command("git rev-parse --abbrev-ref HEAD"),
        "commit": run_git_command("git rev-parse HEAD"),
        "short_commit": run_git_command("git rev-parse --short HEAD"),
        "author": run_git_command("git config user.name"),
        "email": run_git_command("XXgit config user.emailXX"),
    }


def x_discover_git_context__mutmut_28() -> dict[str, Optional[str]]:
    """Discover git context: branch, commit hash, short hash, commit author."""
    return {
        "branch": run_git_command("git rev-parse --abbrev-ref HEAD"),
        "commit": run_git_command("git rev-parse HEAD"),
        "short_commit": run_git_command("git rev-parse --short HEAD"),
        "author": run_git_command("git config user.name"),
        "email": run_git_command("GIT CONFIG USER.EMAIL"),
    }

x_discover_git_context__mutmut_mutants : ClassVar[MutantDict] = {
'x_discover_git_context__mutmut_1': x_discover_git_context__mutmut_1, 
    'x_discover_git_context__mutmut_2': x_discover_git_context__mutmut_2, 
    'x_discover_git_context__mutmut_3': x_discover_git_context__mutmut_3, 
    'x_discover_git_context__mutmut_4': x_discover_git_context__mutmut_4, 
    'x_discover_git_context__mutmut_5': x_discover_git_context__mutmut_5, 
    'x_discover_git_context__mutmut_6': x_discover_git_context__mutmut_6, 
    'x_discover_git_context__mutmut_7': x_discover_git_context__mutmut_7, 
    'x_discover_git_context__mutmut_8': x_discover_git_context__mutmut_8, 
    'x_discover_git_context__mutmut_9': x_discover_git_context__mutmut_9, 
    'x_discover_git_context__mutmut_10': x_discover_git_context__mutmut_10, 
    'x_discover_git_context__mutmut_11': x_discover_git_context__mutmut_11, 
    'x_discover_git_context__mutmut_12': x_discover_git_context__mutmut_12, 
    'x_discover_git_context__mutmut_13': x_discover_git_context__mutmut_13, 
    'x_discover_git_context__mutmut_14': x_discover_git_context__mutmut_14, 
    'x_discover_git_context__mutmut_15': x_discover_git_context__mutmut_15, 
    'x_discover_git_context__mutmut_16': x_discover_git_context__mutmut_16, 
    'x_discover_git_context__mutmut_17': x_discover_git_context__mutmut_17, 
    'x_discover_git_context__mutmut_18': x_discover_git_context__mutmut_18, 
    'x_discover_git_context__mutmut_19': x_discover_git_context__mutmut_19, 
    'x_discover_git_context__mutmut_20': x_discover_git_context__mutmut_20, 
    'x_discover_git_context__mutmut_21': x_discover_git_context__mutmut_21, 
    'x_discover_git_context__mutmut_22': x_discover_git_context__mutmut_22, 
    'x_discover_git_context__mutmut_23': x_discover_git_context__mutmut_23, 
    'x_discover_git_context__mutmut_24': x_discover_git_context__mutmut_24, 
    'x_discover_git_context__mutmut_25': x_discover_git_context__mutmut_25, 
    'x_discover_git_context__mutmut_26': x_discover_git_context__mutmut_26, 
    'x_discover_git_context__mutmut_27': x_discover_git_context__mutmut_27, 
    'x_discover_git_context__mutmut_28': x_discover_git_context__mutmut_28
}

def discover_git_context(*args, **kwargs):
    result = _mutmut_trampoline(x_discover_git_context__mutmut_orig, x_discover_git_context__mutmut_mutants, args, kwargs)
    return result 

discover_git_context.__signature__ = _mutmut_signature(x_discover_git_context__mutmut_orig)
x_discover_git_context__mutmut_orig.__name__ = 'x_discover_git_context'


def x_get_session_info__mutmut_orig(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_1(interactive: bool = False) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_2(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = None
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_3(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = None

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_4(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=None)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_5(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = None

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_6(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "XXpr_numberXX": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_7(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "PR_NUMBER": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_8(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "XXbranchXX": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_9(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "BRANCH": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_10(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] and "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_11(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["XXbranchXX"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_12(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["BRANCH"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_13(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "XXunknownXX",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_14(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "UNKNOWN",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_15(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "XXcommitXX": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_16(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "COMMIT": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_17(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] and "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_18(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["XXcommitXX"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_19(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["COMMIT"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_20(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "XXunknownXX",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_21(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "UNKNOWN",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_22(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "XXshort_commitXX": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_23(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "SHORT_COMMIT": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_24(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] and "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_25(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["XXshort_commitXX"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_26(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["SHORT_COMMIT"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_27(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "XXunknownXX",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_28(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "UNKNOWN",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_29(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "XXauthorXX": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_30(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "AUTHOR": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_31(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] and "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_32(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["XXauthorXX"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_33(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["AUTHOR"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_34(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "XXunknownXX",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_35(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "UNKNOWN",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_36(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "XXemailXX": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_37(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "EMAIL": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_38(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] and "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_39(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["XXemailXX"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_40(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["EMAIL"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_41(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "XXunknownXX",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_42(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "UNKNOWN",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_43(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "XXtimestampXX": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_44(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "TIMESTAMP": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_45(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(None).isoformat(),
    }

    logger.info(f"Session context discovered: {session_info}")
    return session_info


def x_get_session_info__mutmut_46(interactive: bool = True) -> dict[str, Any]:
    """
    Gather comprehensive session context upfront.

    Returns:
        Dict with keys:
          - pr_number: Discovered or user-provided PR number
          - branch: Git branch name
          - commit: Full commit hash
          - short_commit: Short commit hash
          - author: User name
          - email: User email
          - timestamp: Session timestamp (ISO format)
    """
    import datetime

    git_context = discover_git_context()
    pr_number = get_pr_number(interactive=interactive)

    session_info = {
        "pr_number": pr_number,
        "branch": git_context["branch"] or "unknown",
        "commit": git_context["commit"] or "unknown",
        "short_commit": git_context["short_commit"] or "unknown",
        "author": git_context["author"] or "unknown",
        "email": git_context["email"] or "unknown",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    logger.info(None)
    return session_info

x_get_session_info__mutmut_mutants : ClassVar[MutantDict] = {
'x_get_session_info__mutmut_1': x_get_session_info__mutmut_1, 
    'x_get_session_info__mutmut_2': x_get_session_info__mutmut_2, 
    'x_get_session_info__mutmut_3': x_get_session_info__mutmut_3, 
    'x_get_session_info__mutmut_4': x_get_session_info__mutmut_4, 
    'x_get_session_info__mutmut_5': x_get_session_info__mutmut_5, 
    'x_get_session_info__mutmut_6': x_get_session_info__mutmut_6, 
    'x_get_session_info__mutmut_7': x_get_session_info__mutmut_7, 
    'x_get_session_info__mutmut_8': x_get_session_info__mutmut_8, 
    'x_get_session_info__mutmut_9': x_get_session_info__mutmut_9, 
    'x_get_session_info__mutmut_10': x_get_session_info__mutmut_10, 
    'x_get_session_info__mutmut_11': x_get_session_info__mutmut_11, 
    'x_get_session_info__mutmut_12': x_get_session_info__mutmut_12, 
    'x_get_session_info__mutmut_13': x_get_session_info__mutmut_13, 
    'x_get_session_info__mutmut_14': x_get_session_info__mutmut_14, 
    'x_get_session_info__mutmut_15': x_get_session_info__mutmut_15, 
    'x_get_session_info__mutmut_16': x_get_session_info__mutmut_16, 
    'x_get_session_info__mutmut_17': x_get_session_info__mutmut_17, 
    'x_get_session_info__mutmut_18': x_get_session_info__mutmut_18, 
    'x_get_session_info__mutmut_19': x_get_session_info__mutmut_19, 
    'x_get_session_info__mutmut_20': x_get_session_info__mutmut_20, 
    'x_get_session_info__mutmut_21': x_get_session_info__mutmut_21, 
    'x_get_session_info__mutmut_22': x_get_session_info__mutmut_22, 
    'x_get_session_info__mutmut_23': x_get_session_info__mutmut_23, 
    'x_get_session_info__mutmut_24': x_get_session_info__mutmut_24, 
    'x_get_session_info__mutmut_25': x_get_session_info__mutmut_25, 
    'x_get_session_info__mutmut_26': x_get_session_info__mutmut_26, 
    'x_get_session_info__mutmut_27': x_get_session_info__mutmut_27, 
    'x_get_session_info__mutmut_28': x_get_session_info__mutmut_28, 
    'x_get_session_info__mutmut_29': x_get_session_info__mutmut_29, 
    'x_get_session_info__mutmut_30': x_get_session_info__mutmut_30, 
    'x_get_session_info__mutmut_31': x_get_session_info__mutmut_31, 
    'x_get_session_info__mutmut_32': x_get_session_info__mutmut_32, 
    'x_get_session_info__mutmut_33': x_get_session_info__mutmut_33, 
    'x_get_session_info__mutmut_34': x_get_session_info__mutmut_34, 
    'x_get_session_info__mutmut_35': x_get_session_info__mutmut_35, 
    'x_get_session_info__mutmut_36': x_get_session_info__mutmut_36, 
    'x_get_session_info__mutmut_37': x_get_session_info__mutmut_37, 
    'x_get_session_info__mutmut_38': x_get_session_info__mutmut_38, 
    'x_get_session_info__mutmut_39': x_get_session_info__mutmut_39, 
    'x_get_session_info__mutmut_40': x_get_session_info__mutmut_40, 
    'x_get_session_info__mutmut_41': x_get_session_info__mutmut_41, 
    'x_get_session_info__mutmut_42': x_get_session_info__mutmut_42, 
    'x_get_session_info__mutmut_43': x_get_session_info__mutmut_43, 
    'x_get_session_info__mutmut_44': x_get_session_info__mutmut_44, 
    'x_get_session_info__mutmut_45': x_get_session_info__mutmut_45, 
    'x_get_session_info__mutmut_46': x_get_session_info__mutmut_46
}

def get_session_info(*args, **kwargs):
    result = _mutmut_trampoline(x_get_session_info__mutmut_orig, x_get_session_info__mutmut_mutants, args, kwargs)
    return result 

get_session_info.__signature__ = _mutmut_signature(x_get_session_info__mutmut_orig)
x_get_session_info__mutmut_orig.__name__ = 'x_get_session_info'


if __name__ == "__main__":
    # Demo usage
    import json

    info = get_session_info()
    print(json.dumps(info, indent=2))
