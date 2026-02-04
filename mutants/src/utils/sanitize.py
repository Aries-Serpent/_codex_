#!/usr/bin/env python3
"""
Minimal, safe sanitization helpers for user-provided prompts.

This module provides an explicit html-escaping function to be used for any
context that may render prompts to HTML or untrusted viewers.

If later you need richer sanitization (strip tags, allowlist), replace these
helpers with a vetted library such as 'bleach' and add focused tests.
"""
import html
import re
from typing import Optional
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


def x_sanitize_prompt__mutmut_orig(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_1(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is not None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_2(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return "XXXX"
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_3(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_4(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = None
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_5(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(None)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_6(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = None
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_7(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(None, '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_8(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', None, prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_9(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', None)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_10(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub('', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_11(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_12(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', )
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_13(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'XX[\x00-\x1F\x7F]XX', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_14(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1f\x7f]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_15(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', 'XXXX', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_16(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = None
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_17(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(None, '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_18(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', None, prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_19(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', None)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_20(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub('', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_21(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_22(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', )
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_23(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'XX\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])XX', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_24(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1b(?:[@-z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_25(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', 'XXXX', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_26(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_27(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) and max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_28(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_29(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length <= 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_30(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 1:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_31(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(None)
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_32(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = None
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_33(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = None
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_34(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(None, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_35(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=None)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_36(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_37(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, )
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_38(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=False)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_39(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = None
    
    return escaped


def x_sanitize_prompt__mutmut_40(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace(None, "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_41(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", None)
    
    return escaped


def x_sanitize_prompt__mutmut_42(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_43(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", )
    
    return escaped


def x_sanitize_prompt__mutmut_44(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("XX'XX", "&#x27;")
    
    return escaped


def x_sanitize_prompt__mutmut_45(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "XX&#x27;XX")
    
    return escaped


def x_sanitize_prompt__mutmut_46(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.
    
    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode
    
    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized prompt string safe for downstream processing
        
    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages
        
    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10
        
        >>> sanitize_prompt("Normal text")
        'Normal text'
        
        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)
    
    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r'[\x00-\x1F\x7F]', '', prompt)
    
    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt)
    
    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]
    
    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#X27;")
    
    return escaped

x_sanitize_prompt__mutmut_mutants : ClassVar[MutantDict] = {
'x_sanitize_prompt__mutmut_1': x_sanitize_prompt__mutmut_1, 
    'x_sanitize_prompt__mutmut_2': x_sanitize_prompt__mutmut_2, 
    'x_sanitize_prompt__mutmut_3': x_sanitize_prompt__mutmut_3, 
    'x_sanitize_prompt__mutmut_4': x_sanitize_prompt__mutmut_4, 
    'x_sanitize_prompt__mutmut_5': x_sanitize_prompt__mutmut_5, 
    'x_sanitize_prompt__mutmut_6': x_sanitize_prompt__mutmut_6, 
    'x_sanitize_prompt__mutmut_7': x_sanitize_prompt__mutmut_7, 
    'x_sanitize_prompt__mutmut_8': x_sanitize_prompt__mutmut_8, 
    'x_sanitize_prompt__mutmut_9': x_sanitize_prompt__mutmut_9, 
    'x_sanitize_prompt__mutmut_10': x_sanitize_prompt__mutmut_10, 
    'x_sanitize_prompt__mutmut_11': x_sanitize_prompt__mutmut_11, 
    'x_sanitize_prompt__mutmut_12': x_sanitize_prompt__mutmut_12, 
    'x_sanitize_prompt__mutmut_13': x_sanitize_prompt__mutmut_13, 
    'x_sanitize_prompt__mutmut_14': x_sanitize_prompt__mutmut_14, 
    'x_sanitize_prompt__mutmut_15': x_sanitize_prompt__mutmut_15, 
    'x_sanitize_prompt__mutmut_16': x_sanitize_prompt__mutmut_16, 
    'x_sanitize_prompt__mutmut_17': x_sanitize_prompt__mutmut_17, 
    'x_sanitize_prompt__mutmut_18': x_sanitize_prompt__mutmut_18, 
    'x_sanitize_prompt__mutmut_19': x_sanitize_prompt__mutmut_19, 
    'x_sanitize_prompt__mutmut_20': x_sanitize_prompt__mutmut_20, 
    'x_sanitize_prompt__mutmut_21': x_sanitize_prompt__mutmut_21, 
    'x_sanitize_prompt__mutmut_22': x_sanitize_prompt__mutmut_22, 
    'x_sanitize_prompt__mutmut_23': x_sanitize_prompt__mutmut_23, 
    'x_sanitize_prompt__mutmut_24': x_sanitize_prompt__mutmut_24, 
    'x_sanitize_prompt__mutmut_25': x_sanitize_prompt__mutmut_25, 
    'x_sanitize_prompt__mutmut_26': x_sanitize_prompt__mutmut_26, 
    'x_sanitize_prompt__mutmut_27': x_sanitize_prompt__mutmut_27, 
    'x_sanitize_prompt__mutmut_28': x_sanitize_prompt__mutmut_28, 
    'x_sanitize_prompt__mutmut_29': x_sanitize_prompt__mutmut_29, 
    'x_sanitize_prompt__mutmut_30': x_sanitize_prompt__mutmut_30, 
    'x_sanitize_prompt__mutmut_31': x_sanitize_prompt__mutmut_31, 
    'x_sanitize_prompt__mutmut_32': x_sanitize_prompt__mutmut_32, 
    'x_sanitize_prompt__mutmut_33': x_sanitize_prompt__mutmut_33, 
    'x_sanitize_prompt__mutmut_34': x_sanitize_prompt__mutmut_34, 
    'x_sanitize_prompt__mutmut_35': x_sanitize_prompt__mutmut_35, 
    'x_sanitize_prompt__mutmut_36': x_sanitize_prompt__mutmut_36, 
    'x_sanitize_prompt__mutmut_37': x_sanitize_prompt__mutmut_37, 
    'x_sanitize_prompt__mutmut_38': x_sanitize_prompt__mutmut_38, 
    'x_sanitize_prompt__mutmut_39': x_sanitize_prompt__mutmut_39, 
    'x_sanitize_prompt__mutmut_40': x_sanitize_prompt__mutmut_40, 
    'x_sanitize_prompt__mutmut_41': x_sanitize_prompt__mutmut_41, 
    'x_sanitize_prompt__mutmut_42': x_sanitize_prompt__mutmut_42, 
    'x_sanitize_prompt__mutmut_43': x_sanitize_prompt__mutmut_43, 
    'x_sanitize_prompt__mutmut_44': x_sanitize_prompt__mutmut_44, 
    'x_sanitize_prompt__mutmut_45': x_sanitize_prompt__mutmut_45, 
    'x_sanitize_prompt__mutmut_46': x_sanitize_prompt__mutmut_46
}

def sanitize_prompt(*args, **kwargs):
    result = _mutmut_trampoline(x_sanitize_prompt__mutmut_orig, x_sanitize_prompt__mutmut_mutants, args, kwargs)
    return result 

sanitize_prompt.__signature__ = _mutmut_signature(x_sanitize_prompt__mutmut_orig)
x_sanitize_prompt__mutmut_orig.__name__ = 'x_sanitize_prompt'
