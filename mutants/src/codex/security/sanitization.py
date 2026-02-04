"""
Security input sanitization utilities.
Provides functions to sanitize user input and prevent XSS, injection attacks.
"""
import re
from typing import Union
import logging

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


def x_sanitize_html__mutmut_orig(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_1(content: str, allow_tags: bool = True) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_2(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_3(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return "XXXX"
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_4(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = None
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_5(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'XXjavascript:XX',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_6(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'JAVASCRIPT:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_7(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'XXdata:XX',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_8(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'DATA:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_9(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'XXvbscript:XX',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_10(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'VBSCRIPT:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_11(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'XXfile:XX',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_12(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'FILE:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_13(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'XXabout:XX'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_14(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'ABOUT:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_15(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = None
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_16(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(None, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_17(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, None, content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_18(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', None, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_19(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=None)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_20(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub('', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_21(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_22(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_23(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, )
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_24(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, 'XXXX', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_25(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = None
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_26(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        None,
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_27(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        None,
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_28(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        None,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_29(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=None
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_30(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_31(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_32(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_33(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_34(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'XX\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?XX',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_35(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*ON\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_36(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        'XXXX',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_37(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = None
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_38(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'XX<script[^>]*>.*?</script>XX',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_39(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<SCRIPT[^>]*>.*?</SCRIPT>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_40(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'XX<iframe[^>]*>.*?</iframe>XX',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_41(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<IFRAME[^>]*>.*?</IFRAME>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_42(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'XX<object[^>]*>.*?</object>XX',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_43(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<OBJECT[^>]*>.*?</OBJECT>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_44(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'XX<embed[^>]*>.*?</embed>XX',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_45(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<EMBED[^>]*>.*?</EMBED>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_46(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'XX<applet[^>]*>.*?</applet>XX',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_47(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<APPLET[^>]*>.*?</APPLET>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_48(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'XX<meta[^>]*>XX',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_49(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<META[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_50(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'XX<link[^>]*>XX',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_51(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<LINK[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_52(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'XX<style[^>]*>.*?</style>XX',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_53(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<STYLE[^>]*>.*?</STYLE>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_54(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = None
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_55(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(None, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_56(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, None, content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_57(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', None, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_58(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=None)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_59(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub('', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_60(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_61(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_62(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, )
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_63(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, 'XXXX', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_64(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE & re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_65(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_66(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = None
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_67(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(None, '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_68(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', None, content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_69(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', None)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_70(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub('', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_71(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_72(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', )
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_73(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'XX<[^>]+>XX', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_74(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', 'XXXX', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(f"Sanitized HTML: {len(content)} chars")
    return content.strip()


def x_sanitize_html__mutmut_75(content: str, allow_tags: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes:
    - javascript: protocol
    - data: protocol  
    - vbscript: protocol
    - Event handlers (onclick, onerror, onload, etc.)
    - Dangerous tags (<script>, <iframe>, <object>, <embed>)
    
    Args:
        content: HTML string to sanitize
        allow_tags: If False, strip all HTML tags
        
    Returns:
        Sanitized string safe for display
    """
    if not isinstance(content, str):
        return ""
    
    # Step 1: Remove dangerous protocols (case-insensitive)
    dangerous_protocols = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:'
    ]
    for protocol in dangerous_protocols:
        content = re.sub(protocol, '', content, flags=re.IGNORECASE)
    
    # Step 2: Remove event handlers (onclick, onerror, onload, etc.)
    # Using raw string to properly handle \s for whitespace
    content = re.sub(
        r'\s*on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
        '',
        content,
        flags=re.IGNORECASE
    )
    
    # Step 3: Remove dangerous tags
    dangerous_tags = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<applet[^>]*>.*?</applet>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    for tag_pattern in dangerous_tags:
        content = re.sub(tag_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 4: Strip all HTML tags if not allowed
    if not allow_tags:
        content = re.sub(r'<[^>]+>', '', content)
    
    # Note: HTML encoding of special characters is not performed here.
    # Tests expect tag/protocol removal rather than entity encoding.
    # For production use in HTML contexts, consider additional encoding.
    
    logger.debug(None)
    return content.strip()

x_sanitize_html__mutmut_mutants : ClassVar[MutantDict] = {
'x_sanitize_html__mutmut_1': x_sanitize_html__mutmut_1, 
    'x_sanitize_html__mutmut_2': x_sanitize_html__mutmut_2, 
    'x_sanitize_html__mutmut_3': x_sanitize_html__mutmut_3, 
    'x_sanitize_html__mutmut_4': x_sanitize_html__mutmut_4, 
    'x_sanitize_html__mutmut_5': x_sanitize_html__mutmut_5, 
    'x_sanitize_html__mutmut_6': x_sanitize_html__mutmut_6, 
    'x_sanitize_html__mutmut_7': x_sanitize_html__mutmut_7, 
    'x_sanitize_html__mutmut_8': x_sanitize_html__mutmut_8, 
    'x_sanitize_html__mutmut_9': x_sanitize_html__mutmut_9, 
    'x_sanitize_html__mutmut_10': x_sanitize_html__mutmut_10, 
    'x_sanitize_html__mutmut_11': x_sanitize_html__mutmut_11, 
    'x_sanitize_html__mutmut_12': x_sanitize_html__mutmut_12, 
    'x_sanitize_html__mutmut_13': x_sanitize_html__mutmut_13, 
    'x_sanitize_html__mutmut_14': x_sanitize_html__mutmut_14, 
    'x_sanitize_html__mutmut_15': x_sanitize_html__mutmut_15, 
    'x_sanitize_html__mutmut_16': x_sanitize_html__mutmut_16, 
    'x_sanitize_html__mutmut_17': x_sanitize_html__mutmut_17, 
    'x_sanitize_html__mutmut_18': x_sanitize_html__mutmut_18, 
    'x_sanitize_html__mutmut_19': x_sanitize_html__mutmut_19, 
    'x_sanitize_html__mutmut_20': x_sanitize_html__mutmut_20, 
    'x_sanitize_html__mutmut_21': x_sanitize_html__mutmut_21, 
    'x_sanitize_html__mutmut_22': x_sanitize_html__mutmut_22, 
    'x_sanitize_html__mutmut_23': x_sanitize_html__mutmut_23, 
    'x_sanitize_html__mutmut_24': x_sanitize_html__mutmut_24, 
    'x_sanitize_html__mutmut_25': x_sanitize_html__mutmut_25, 
    'x_sanitize_html__mutmut_26': x_sanitize_html__mutmut_26, 
    'x_sanitize_html__mutmut_27': x_sanitize_html__mutmut_27, 
    'x_sanitize_html__mutmut_28': x_sanitize_html__mutmut_28, 
    'x_sanitize_html__mutmut_29': x_sanitize_html__mutmut_29, 
    'x_sanitize_html__mutmut_30': x_sanitize_html__mutmut_30, 
    'x_sanitize_html__mutmut_31': x_sanitize_html__mutmut_31, 
    'x_sanitize_html__mutmut_32': x_sanitize_html__mutmut_32, 
    'x_sanitize_html__mutmut_33': x_sanitize_html__mutmut_33, 
    'x_sanitize_html__mutmut_34': x_sanitize_html__mutmut_34, 
    'x_sanitize_html__mutmut_35': x_sanitize_html__mutmut_35, 
    'x_sanitize_html__mutmut_36': x_sanitize_html__mutmut_36, 
    'x_sanitize_html__mutmut_37': x_sanitize_html__mutmut_37, 
    'x_sanitize_html__mutmut_38': x_sanitize_html__mutmut_38, 
    'x_sanitize_html__mutmut_39': x_sanitize_html__mutmut_39, 
    'x_sanitize_html__mutmut_40': x_sanitize_html__mutmut_40, 
    'x_sanitize_html__mutmut_41': x_sanitize_html__mutmut_41, 
    'x_sanitize_html__mutmut_42': x_sanitize_html__mutmut_42, 
    'x_sanitize_html__mutmut_43': x_sanitize_html__mutmut_43, 
    'x_sanitize_html__mutmut_44': x_sanitize_html__mutmut_44, 
    'x_sanitize_html__mutmut_45': x_sanitize_html__mutmut_45, 
    'x_sanitize_html__mutmut_46': x_sanitize_html__mutmut_46, 
    'x_sanitize_html__mutmut_47': x_sanitize_html__mutmut_47, 
    'x_sanitize_html__mutmut_48': x_sanitize_html__mutmut_48, 
    'x_sanitize_html__mutmut_49': x_sanitize_html__mutmut_49, 
    'x_sanitize_html__mutmut_50': x_sanitize_html__mutmut_50, 
    'x_sanitize_html__mutmut_51': x_sanitize_html__mutmut_51, 
    'x_sanitize_html__mutmut_52': x_sanitize_html__mutmut_52, 
    'x_sanitize_html__mutmut_53': x_sanitize_html__mutmut_53, 
    'x_sanitize_html__mutmut_54': x_sanitize_html__mutmut_54, 
    'x_sanitize_html__mutmut_55': x_sanitize_html__mutmut_55, 
    'x_sanitize_html__mutmut_56': x_sanitize_html__mutmut_56, 
    'x_sanitize_html__mutmut_57': x_sanitize_html__mutmut_57, 
    'x_sanitize_html__mutmut_58': x_sanitize_html__mutmut_58, 
    'x_sanitize_html__mutmut_59': x_sanitize_html__mutmut_59, 
    'x_sanitize_html__mutmut_60': x_sanitize_html__mutmut_60, 
    'x_sanitize_html__mutmut_61': x_sanitize_html__mutmut_61, 
    'x_sanitize_html__mutmut_62': x_sanitize_html__mutmut_62, 
    'x_sanitize_html__mutmut_63': x_sanitize_html__mutmut_63, 
    'x_sanitize_html__mutmut_64': x_sanitize_html__mutmut_64, 
    'x_sanitize_html__mutmut_65': x_sanitize_html__mutmut_65, 
    'x_sanitize_html__mutmut_66': x_sanitize_html__mutmut_66, 
    'x_sanitize_html__mutmut_67': x_sanitize_html__mutmut_67, 
    'x_sanitize_html__mutmut_68': x_sanitize_html__mutmut_68, 
    'x_sanitize_html__mutmut_69': x_sanitize_html__mutmut_69, 
    'x_sanitize_html__mutmut_70': x_sanitize_html__mutmut_70, 
    'x_sanitize_html__mutmut_71': x_sanitize_html__mutmut_71, 
    'x_sanitize_html__mutmut_72': x_sanitize_html__mutmut_72, 
    'x_sanitize_html__mutmut_73': x_sanitize_html__mutmut_73, 
    'x_sanitize_html__mutmut_74': x_sanitize_html__mutmut_74, 
    'x_sanitize_html__mutmut_75': x_sanitize_html__mutmut_75
}

def sanitize_html(*args, **kwargs):
    result = _mutmut_trampoline(x_sanitize_html__mutmut_orig, x_sanitize_html__mutmut_mutants, args, kwargs)
    return result 

sanitize_html.__signature__ = _mutmut_signature(x_sanitize_html__mutmut_orig)
x_sanitize_html__mutmut_orig.__name__ = 'x_sanitize_html'


def x_sanitize_integer__mutmut_orig(
    value: Union[str, int, float],
    default: int = 0,
    min_value: int = None,
    max_value: int = None
) -> int:
    """
    Safely convert input to integer.
    
    Handles:
    - String representations of integers ("42")
    - String representations of floats ("42.7" → 42)
    - Already-integer values
    - Invalid inputs (returns default)
    
    Args:
        value: Input to convert
        default: Value to return if conversion fails
        min_value: Minimum allowed value (None = no limit)
        max_value: Maximum allowed value (None = no limit)
        
    Returns:
        Integer value or default
    """
    try:
        # Handle None
        if value is None:
            return default
        
        # If already int, validate and return
        if isinstance(value, int):
            result = value
        # If float, truncate to int
        elif isinstance(value, float):
            result = int(value)
        # If string, parse as float first (handles "42.7"), then truncate
        elif isinstance(value, str):
            result = int(float(value.strip()))
        else:
            logger.warning(f"Cannot convert {type(value)} to integer: {value}")
            return default
        
        # Apply bounds if specified
        if min_value is not None and result < min_value:
            logger.warning(f"Value {result} below minimum {min_value}, clamping")
            return min_value
        if max_value is not None and result > max_value:
            logger.warning(f"Value {result} above maximum {max_value}, clamping")
            return max_value
        
        return result
        
    except (ValueError, TypeError, AttributeError) as e:
        logger.debug(f"Integer sanitization failed for '{value}': {e}")
        return default


def x_sanitize_integer__mutmut_1(
    value: Union[str, int, float],
    default: int = 1,
    min_value: int = None,
    max_value: int = None
) -> int:
    """
    Safely convert input to integer.
    
    Handles:
    - String representations of integers ("42")
    - String representations of floats ("42.7" → 42)
    - Already-integer values
    - Invalid inputs (returns default)
    
    Args:
        value: Input to convert
        default: Value to return if conversion fails
        min_value: Minimum allowed value (None = no limit)
        max_value: Maximum allowed value (None = no limit)
        
    Returns:
        Integer value or default
    """
    try:
        # Handle None
        if value is None:
            return default
        
        # If already int, validate and return
        if isinstance(value, int):
            result = value
        # If float, truncate to int
        elif isinstance(value, float):
            result = int(value)
        # If string, parse as float first (handles "42.7"), then truncate
        elif isinstance(value, str):
            result = int(float(value.strip()))
        else:
            logger.warning(f"Cannot convert {type(value)} to integer: {value}")
            return default
        
        # Apply bounds if specified
        if min_value is not None and result < min_value:
            logger.warning(f"Value {result} below minimum {min_value}, clamping")
            return min_value
        if max_value is not None and result > max_value:
            logger.warning(f"Value {result} above maximum {max_value}, clamping")
            return max_value
        
        return result
        
    except (ValueError, TypeError, AttributeError) as e:
        logger.debug(f"Integer sanitization failed for '{value}': {e}")
        return default


def x_sanitize_integer__mutmut_2(
    value: Union[str, int, float],
    default: int = 0,
    min_value: int = None,
    max_value: int = None
) -> int:
    """
    Safely convert input to integer.
    
    Handles:
    - String representations of integers ("42")
    - String representations of floats ("42.7" → 42)
    - Already-integer values
    - Invalid inputs (returns default)
    
    Args:
        value: Input to convert
        default: Value to return if conversion fails
        min_value: Minimum allowed value (None = no limit)
        max_value: Maximum allowed value (None = no limit)
        
    Returns:
        Integer value or default
    """
    try:
        # Handle None
        if value is not None:
            return default
        
        # If already int, validate and return
        if isinstance(value, int):
            result = value
        # If float, truncate to int
        elif isinstance(value, float):
            result = int(value)
        # If string, parse as float first (handles "42.7"), then truncate
        elif isinstance(value, str):
            result = int(float(value.strip()))
        else:
            logger.warning(f"Cannot convert {type(value)} to integer: {value}")
            return default
        
        # Apply bounds if specified
        if min_value is not None and result < min_value:
            logger.warning(f"Value {result} below minimum {min_value}, clamping")
            return min_value
        if max_value is not None and result > max_value:
            logger.warning(f"Value {result} above maximum {max_value}, clamping")
            return max_value
        
        return result
        
    except (ValueError, TypeError, AttributeError) as e:
        logger.debug(f"Integer sanitization failed for '{value}': {e}")
        return default


def x_sanitize_integer__mutmut_3(
    value: Union[str, int, float],
    default: int = 0,
    min_value: int = None,
    max_value: int = None
) -> int:
    """
    Safely convert input to integer.
    
    Handles:
    - String representations of integers ("42")
    - String representations of floats ("42.7" → 42)
    - Already-integer values
    - Invalid inputs (returns default)
    
    Args:
        value: Input to convert
        default: Value to return if conversion fails
        min_value: Minimum allowed value (None = no limit)
        max_value: Maximum allowed value (None = no limit)
        
    Returns:
        Integer value or default
    """
    try:
        # Handle None
        if value is None:
            return default
        
        # If already int, validate and return
        if isinstance(value, int):
            result = None
        # If float, truncate to int
        elif isinstance(value, float):
            result = int(value)
        # If string, parse as float first (handles "42.7"), then truncate
        elif isinstance(value, str):
            result = int(float(value.strip()))
        else:
            logger.warning(f"Cannot convert {type(value)} to integer: {value}")
            return default
        
        # Apply bounds if specified
        if min_value is not None and result < min_value:
            logger.warning(f"Value {result} below minimum {min_value}, clamping")
            return min_value
        if max_value is not None and result > max_value:
            logger.warning(f"Value {result} above maximum {max_value}, clamping")
            return max_value
        
        return result
        
    except (ValueError, TypeError, AttributeError) as e:
        logger.debug(f"Integer sanitization failed for '{value}': {e}")
        return default


def x_sanitize_integer__mutmut_4(
    value: Union[str, int, float],
    default: int = 0,
    min_value: int = None,
    max_value: int = None
) -> int:
    """
    Safely convert input to integer.
    
    Handles:
    - String representations of integers ("42")
    - String representations of floats ("42.7" → 42)
    - Already-integer values
    - Invalid inputs (returns default)
    
    Args:
        value: Input to convert
        default: Value to return if conversion fails
        min_value: Minimum allowed value (None = no limit)
        max_value: Maximum allowed value (None = no limit)
        
    Returns:
        Integer value or default
    """
    try:
        # Handle None
        if value is None:
            return default
        
        # If already int, validate and return
        if isinstance(value, int):
            result = value
        # If float, truncate to int
        elif isinstance(value, float):
            result = None
        # If string, parse as float first (handles "42.7"), then truncate
        elif isinstance(value, str):
            result = int(float(value.strip()))
        else:
            logger.warning(f"Cannot convert {type(value)} to integer: {value}")
            return default
        
        # Apply bounds if specified
        if min_value is not None and result < min_value:
            logger.warning(f"Value {result} below minimum {min_value}, clamping")
            return min_value
        if max_value is not None and result > max_value:
            logger.warning(f"Value {result} above maximum {max_value}, clamping")
            return max_value
        
        return result
        
    except (ValueError, TypeError, AttributeError) as e:
        logger.debug(f"Integer sanitization failed for '{value}': {e}")
        return default


def x_sanitize_integer__mutmut_5(
    value: Union[str, int, float],
    default: int = 0,
    min_value: int = None,
    max_value: int = None
) -> int:
    """
    Safely convert input to integer.
    
    Handles:
    - String representations of integers ("42")
    - String representations of floats ("42.7" → 42)
    - Already-integer values
    - Invalid inputs (returns default)
    
    Args:
        value: Input to convert
        default: Value to return if conversion fails
        min_value: Minimum allowed value (None = no limit)
        max_value: Maximum allowed value (None = no limit)
        
    Returns:
        Integer value or default
    """
    try:
        # Handle None
        if value is None:
            return default
        
        # If already int, validate and return
        if isinstance(value, int):
            result = value
        # If float, truncate to int
        elif isinstance(value, float):
            result = int(None)
        # If string, parse as float first (handles "42.7"), then truncate
        elif isinstance(value, str):
            result = int(float(value.strip()))
        else:
            logger.warning(f"Cannot convert {type(value)} to integer: {value}")
            return default
        
        # Apply bounds if specified
        if min_value is not None and result < min_value:
            logger.warning(f"Value {result} below minimum {min_value}, clamping")
            return min_value
        if max_value is not None and result > max_value:
            logger.warning(f"Value {result} above maximum {max_value}, clamping")
            return max_value
        
        return result
        
    except (ValueError, TypeError, AttributeError) as e:
        logger.debug(f"Integer sanitization failed for '{value}': {e}")
        return default


def x_sanitize_integer__mutmut_6(
    value: Union[str, int, float],
    default: int = 0,
    min_value: int = None,
    max_value: int = None
) -> int:
    """
    Safely convert input to integer.
    
    Handles:
    - String representations of integers ("42")
    - String representations of floats ("42.7" → 42)
    - Already-integer values
    - Invalid inputs (returns default)
    
    Args:
        value: Input to convert
        default: Value to return if conversion fails
        min_value: Minimum allowed value (None = no limit)
        max_value: Maximum allowed value (None = no limit)
        
    Returns:
        Integer value or default
    """
    try:
        # Handle None
        if value is None:
            return default
        
        # If already int, validate and return
        if isinstance(value, int):
            result = value
        # If float, truncate to int
        elif isinstance(value, float):
            result = int(value)
        # If string, parse as float first (handles "42.7"), then truncate
        elif isinstance(value, str):
            result = None
        else:
            logger.warning(f"Cannot convert {type(value)} to integer: {value}")
            return default
        
        # Apply bounds if specified
        if min_value is not None and result < min_value:
            logger.warning(f"Value {result} below minimum {min_value}, clamping")
            return min_value
        if max_value is not None and result > max_value:
            logger.warning(f"Value {result} above maximum {max_value}, clamping")
            return max_value
        
        return result
        
    except (ValueError, TypeError, AttributeError) as e:
        logger.debug(f"Integer sanitization failed for '{value}': {e}")
        return default


def x_sanitize_integer__mutmut_7(
    value: Union[str, int, float],
    default: int = 0,
    min_value: int = None,
    max_value: int = None
) -> int:
    """
    Safely convert input to integer.
    
    Handles:
    - String representations of integers ("42")
    - String representations of floats ("42.7" → 42)
    - Already-integer values
    - Invalid inputs (returns default)
    
    Args:
        value: Input to convert
        default: Value to return if conversion fails
        min_value: Minimum allowed value (None = no limit)
        max_value: Maximum allowed value (None = no limit)
        
    Returns:
        Integer value or default
    """
    try:
        # Handle None
        if value is None:
            return default
        
        # If already int, validate and return
        if isinstance(value, int):
            result = value
        # If float, truncate to int
        elif isinstance(value, float):
            result = int(value)
        # If string, parse as float first (handles "42.7"), then truncate
        elif isinstance(value, str):
            result = int(None)
        else:
            logger.warning(f"Cannot convert {type(value)} to integer: {value}")
            return default
        
        # Apply bounds if specified
        if min_value is not None and result < min_value:
            logger.warning(f"Value {result} below minimum {min_value}, clamping")
            return min_value
        if max_value is not None and result > max_value:
            logger.warning(f"Value {result} above maximum {max_value}, clamping")
            return max_value
        
        return result
        
    except (ValueError, TypeError, AttributeError) as e:
        logger.debug(f"Integer sanitization failed for '{value}': {e}")
        return default


def x_sanitize_integer__mutmut_8(
    value: Union[str, int, float],
    default: int = 0,
    min_value: int = None,
    max_value: int = None
) -> int:
    """
    Safely convert input to integer.
    
    Handles:
    - String representations of integers ("42")
    - String representations of floats ("42.7" → 42)
    - Already-integer values
    - Invalid inputs (returns default)
    
    Args:
        value: Input to convert
        default: Value to return if conversion fails
        min_value: Minimum allowed value (None = no limit)
        max_value: Maximum allowed value (None = no limit)
        
    Returns:
        Integer value or default
    """
    try:
        # Handle None
        if value is None:
            return default
        
        # If already int, validate and return
        if isinstance(value, int):
            result = value
        # If float, truncate to int
        elif isinstance(value, float):
            result = int(value)
        # If string, parse as float first (handles "42.7"), then truncate
        elif isinstance(value, str):
            result = int(float(None))
        else:
            logger.warning(f"Cannot convert {type(value)} to integer: {value}")
            return default
        
        # Apply bounds if specified
        if min_value is not None and result < min_value:
            logger.warning(f"Value {result} below minimum {min_value}, clamping")
            return min_value
        if max_value is not None and result > max_value:
            logger.warning(f"Value {result} above maximum {max_value}, clamping")
            return max_value
        
        return result
        
    except (ValueError, TypeError, AttributeError) as e:
        logger.debug(f"Integer sanitization failed for '{value}': {e}")
        return default


def x_sanitize_integer__mutmut_9(
    value: Union[str, int, float],
    default: int = 0,
    min_value: int = None,
    max_value: int = None
) -> int:
    """
    Safely convert input to integer.
    
    Handles:
    - String representations of integers ("42")
    - String representations of floats ("42.7" → 42)
    - Already-integer values
    - Invalid inputs (returns default)
    
    Args:
        value: Input to convert
        default: Value to return if conversion fails
        min_value: Minimum allowed value (None = no limit)
        max_value: Maximum allowed value (None = no limit)
        
    Returns:
        Integer value or default
    """
    try:
        # Handle None
        if value is None:
            return default
        
        # If already int, validate and return
        if isinstance(value, int):
            result = value
        # If float, truncate to int
        elif isinstance(value, float):
            result = int(value)
        # If string, parse as float first (handles "42.7"), then truncate
        elif isinstance(value, str):
            result = int(float(value.strip()))
        else:
            logger.warning(None)
            return default
        
        # Apply bounds if specified
        if min_value is not None and result < min_value:
            logger.warning(f"Value {result} below minimum {min_value}, clamping")
            return min_value
        if max_value is not None and result > max_value:
            logger.warning(f"Value {result} above maximum {max_value}, clamping")
            return max_value
        
        return result
        
    except (ValueError, TypeError, AttributeError) as e:
        logger.debug(f"Integer sanitization failed for '{value}': {e}")
        return default


def x_sanitize_integer__mutmut_10(
    value: Union[str, int, float],
    default: int = 0,
    min_value: int = None,
    max_value: int = None
) -> int:
    """
    Safely convert input to integer.
    
    Handles:
    - String representations of integers ("42")
    - String representations of floats ("42.7" → 42)
    - Already-integer values
    - Invalid inputs (returns default)
    
    Args:
        value: Input to convert
        default: Value to return if conversion fails
        min_value: Minimum allowed value (None = no limit)
        max_value: Maximum allowed value (None = no limit)
        
    Returns:
        Integer value or default
    """
    try:
        # Handle None
        if value is None:
            return default
        
        # If already int, validate and return
        if isinstance(value, int):
            result = value
        # If float, truncate to int
        elif isinstance(value, float):
            result = int(value)
        # If string, parse as float first (handles "42.7"), then truncate
        elif isinstance(value, str):
            result = int(float(value.strip()))
        else:
            logger.warning(f"Cannot convert {type(None)} to integer: {value}")
            return default
        
        # Apply bounds if specified
        if min_value is not None and result < min_value:
            logger.warning(f"Value {result} below minimum {min_value}, clamping")
            return min_value
        if max_value is not None and result > max_value:
            logger.warning(f"Value {result} above maximum {max_value}, clamping")
            return max_value
        
        return result
        
    except (ValueError, TypeError, AttributeError) as e:
        logger.debug(f"Integer sanitization failed for '{value}': {e}")
        return default


def x_sanitize_integer__mutmut_11(
    value: Union[str, int, float],
    default: int = 0,
    min_value: int = None,
    max_value: int = None
) -> int:
    """
    Safely convert input to integer.
    
    Handles:
    - String representations of integers ("42")
    - String representations of floats ("42.7" → 42)
    - Already-integer values
    - Invalid inputs (returns default)
    
    Args:
        value: Input to convert
        default: Value to return if conversion fails
        min_value: Minimum allowed value (None = no limit)
        max_value: Maximum allowed value (None = no limit)
        
    Returns:
        Integer value or default
    """
    try:
        # Handle None
        if value is None:
            return default
        
        # If already int, validate and return
        if isinstance(value, int):
            result = value
        # If float, truncate to int
        elif isinstance(value, float):
            result = int(value)
        # If string, parse as float first (handles "42.7"), then truncate
        elif isinstance(value, str):
            result = int(float(value.strip()))
        else:
            logger.warning(f"Cannot convert {type(value)} to integer: {value}")
            return default
        
        # Apply bounds if specified
        if min_value is not None or result < min_value:
            logger.warning(f"Value {result} below minimum {min_value}, clamping")
            return min_value
        if max_value is not None and result > max_value:
            logger.warning(f"Value {result} above maximum {max_value}, clamping")
            return max_value
        
        return result
        
    except (ValueError, TypeError, AttributeError) as e:
        logger.debug(f"Integer sanitization failed for '{value}': {e}")
        return default


def x_sanitize_integer__mutmut_12(
    value: Union[str, int, float],
    default: int = 0,
    min_value: int = None,
    max_value: int = None
) -> int:
    """
    Safely convert input to integer.
    
    Handles:
    - String representations of integers ("42")
    - String representations of floats ("42.7" → 42)
    - Already-integer values
    - Invalid inputs (returns default)
    
    Args:
        value: Input to convert
        default: Value to return if conversion fails
        min_value: Minimum allowed value (None = no limit)
        max_value: Maximum allowed value (None = no limit)
        
    Returns:
        Integer value or default
    """
    try:
        # Handle None
        if value is None:
            return default
        
        # If already int, validate and return
        if isinstance(value, int):
            result = value
        # If float, truncate to int
        elif isinstance(value, float):
            result = int(value)
        # If string, parse as float first (handles "42.7"), then truncate
        elif isinstance(value, str):
            result = int(float(value.strip()))
        else:
            logger.warning(f"Cannot convert {type(value)} to integer: {value}")
            return default
        
        # Apply bounds if specified
        if min_value is None and result < min_value:
            logger.warning(f"Value {result} below minimum {min_value}, clamping")
            return min_value
        if max_value is not None and result > max_value:
            logger.warning(f"Value {result} above maximum {max_value}, clamping")
            return max_value
        
        return result
        
    except (ValueError, TypeError, AttributeError) as e:
        logger.debug(f"Integer sanitization failed for '{value}': {e}")
        return default


def x_sanitize_integer__mutmut_13(
    value: Union[str, int, float],
    default: int = 0,
    min_value: int = None,
    max_value: int = None
) -> int:
    """
    Safely convert input to integer.
    
    Handles:
    - String representations of integers ("42")
    - String representations of floats ("42.7" → 42)
    - Already-integer values
    - Invalid inputs (returns default)
    
    Args:
        value: Input to convert
        default: Value to return if conversion fails
        min_value: Minimum allowed value (None = no limit)
        max_value: Maximum allowed value (None = no limit)
        
    Returns:
        Integer value or default
    """
    try:
        # Handle None
        if value is None:
            return default
        
        # If already int, validate and return
        if isinstance(value, int):
            result = value
        # If float, truncate to int
        elif isinstance(value, float):
            result = int(value)
        # If string, parse as float first (handles "42.7"), then truncate
        elif isinstance(value, str):
            result = int(float(value.strip()))
        else:
            logger.warning(f"Cannot convert {type(value)} to integer: {value}")
            return default
        
        # Apply bounds if specified
        if min_value is not None and result <= min_value:
            logger.warning(f"Value {result} below minimum {min_value}, clamping")
            return min_value
        if max_value is not None and result > max_value:
            logger.warning(f"Value {result} above maximum {max_value}, clamping")
            return max_value
        
        return result
        
    except (ValueError, TypeError, AttributeError) as e:
        logger.debug(f"Integer sanitization failed for '{value}': {e}")
        return default


def x_sanitize_integer__mutmut_14(
    value: Union[str, int, float],
    default: int = 0,
    min_value: int = None,
    max_value: int = None
) -> int:
    """
    Safely convert input to integer.
    
    Handles:
    - String representations of integers ("42")
    - String representations of floats ("42.7" → 42)
    - Already-integer values
    - Invalid inputs (returns default)
    
    Args:
        value: Input to convert
        default: Value to return if conversion fails
        min_value: Minimum allowed value (None = no limit)
        max_value: Maximum allowed value (None = no limit)
        
    Returns:
        Integer value or default
    """
    try:
        # Handle None
        if value is None:
            return default
        
        # If already int, validate and return
        if isinstance(value, int):
            result = value
        # If float, truncate to int
        elif isinstance(value, float):
            result = int(value)
        # If string, parse as float first (handles "42.7"), then truncate
        elif isinstance(value, str):
            result = int(float(value.strip()))
        else:
            logger.warning(f"Cannot convert {type(value)} to integer: {value}")
            return default
        
        # Apply bounds if specified
        if min_value is not None and result < min_value:
            logger.warning(None)
            return min_value
        if max_value is not None and result > max_value:
            logger.warning(f"Value {result} above maximum {max_value}, clamping")
            return max_value
        
        return result
        
    except (ValueError, TypeError, AttributeError) as e:
        logger.debug(f"Integer sanitization failed for '{value}': {e}")
        return default


def x_sanitize_integer__mutmut_15(
    value: Union[str, int, float],
    default: int = 0,
    min_value: int = None,
    max_value: int = None
) -> int:
    """
    Safely convert input to integer.
    
    Handles:
    - String representations of integers ("42")
    - String representations of floats ("42.7" → 42)
    - Already-integer values
    - Invalid inputs (returns default)
    
    Args:
        value: Input to convert
        default: Value to return if conversion fails
        min_value: Minimum allowed value (None = no limit)
        max_value: Maximum allowed value (None = no limit)
        
    Returns:
        Integer value or default
    """
    try:
        # Handle None
        if value is None:
            return default
        
        # If already int, validate and return
        if isinstance(value, int):
            result = value
        # If float, truncate to int
        elif isinstance(value, float):
            result = int(value)
        # If string, parse as float first (handles "42.7"), then truncate
        elif isinstance(value, str):
            result = int(float(value.strip()))
        else:
            logger.warning(f"Cannot convert {type(value)} to integer: {value}")
            return default
        
        # Apply bounds if specified
        if min_value is not None and result < min_value:
            logger.warning(f"Value {result} below minimum {min_value}, clamping")
            return min_value
        if max_value is not None or result > max_value:
            logger.warning(f"Value {result} above maximum {max_value}, clamping")
            return max_value
        
        return result
        
    except (ValueError, TypeError, AttributeError) as e:
        logger.debug(f"Integer sanitization failed for '{value}': {e}")
        return default


def x_sanitize_integer__mutmut_16(
    value: Union[str, int, float],
    default: int = 0,
    min_value: int = None,
    max_value: int = None
) -> int:
    """
    Safely convert input to integer.
    
    Handles:
    - String representations of integers ("42")
    - String representations of floats ("42.7" → 42)
    - Already-integer values
    - Invalid inputs (returns default)
    
    Args:
        value: Input to convert
        default: Value to return if conversion fails
        min_value: Minimum allowed value (None = no limit)
        max_value: Maximum allowed value (None = no limit)
        
    Returns:
        Integer value or default
    """
    try:
        # Handle None
        if value is None:
            return default
        
        # If already int, validate and return
        if isinstance(value, int):
            result = value
        # If float, truncate to int
        elif isinstance(value, float):
            result = int(value)
        # If string, parse as float first (handles "42.7"), then truncate
        elif isinstance(value, str):
            result = int(float(value.strip()))
        else:
            logger.warning(f"Cannot convert {type(value)} to integer: {value}")
            return default
        
        # Apply bounds if specified
        if min_value is not None and result < min_value:
            logger.warning(f"Value {result} below minimum {min_value}, clamping")
            return min_value
        if max_value is None and result > max_value:
            logger.warning(f"Value {result} above maximum {max_value}, clamping")
            return max_value
        
        return result
        
    except (ValueError, TypeError, AttributeError) as e:
        logger.debug(f"Integer sanitization failed for '{value}': {e}")
        return default


def x_sanitize_integer__mutmut_17(
    value: Union[str, int, float],
    default: int = 0,
    min_value: int = None,
    max_value: int = None
) -> int:
    """
    Safely convert input to integer.
    
    Handles:
    - String representations of integers ("42")
    - String representations of floats ("42.7" → 42)
    - Already-integer values
    - Invalid inputs (returns default)
    
    Args:
        value: Input to convert
        default: Value to return if conversion fails
        min_value: Minimum allowed value (None = no limit)
        max_value: Maximum allowed value (None = no limit)
        
    Returns:
        Integer value or default
    """
    try:
        # Handle None
        if value is None:
            return default
        
        # If already int, validate and return
        if isinstance(value, int):
            result = value
        # If float, truncate to int
        elif isinstance(value, float):
            result = int(value)
        # If string, parse as float first (handles "42.7"), then truncate
        elif isinstance(value, str):
            result = int(float(value.strip()))
        else:
            logger.warning(f"Cannot convert {type(value)} to integer: {value}")
            return default
        
        # Apply bounds if specified
        if min_value is not None and result < min_value:
            logger.warning(f"Value {result} below minimum {min_value}, clamping")
            return min_value
        if max_value is not None and result >= max_value:
            logger.warning(f"Value {result} above maximum {max_value}, clamping")
            return max_value
        
        return result
        
    except (ValueError, TypeError, AttributeError) as e:
        logger.debug(f"Integer sanitization failed for '{value}': {e}")
        return default


def x_sanitize_integer__mutmut_18(
    value: Union[str, int, float],
    default: int = 0,
    min_value: int = None,
    max_value: int = None
) -> int:
    """
    Safely convert input to integer.
    
    Handles:
    - String representations of integers ("42")
    - String representations of floats ("42.7" → 42)
    - Already-integer values
    - Invalid inputs (returns default)
    
    Args:
        value: Input to convert
        default: Value to return if conversion fails
        min_value: Minimum allowed value (None = no limit)
        max_value: Maximum allowed value (None = no limit)
        
    Returns:
        Integer value or default
    """
    try:
        # Handle None
        if value is None:
            return default
        
        # If already int, validate and return
        if isinstance(value, int):
            result = value
        # If float, truncate to int
        elif isinstance(value, float):
            result = int(value)
        # If string, parse as float first (handles "42.7"), then truncate
        elif isinstance(value, str):
            result = int(float(value.strip()))
        else:
            logger.warning(f"Cannot convert {type(value)} to integer: {value}")
            return default
        
        # Apply bounds if specified
        if min_value is not None and result < min_value:
            logger.warning(f"Value {result} below minimum {min_value}, clamping")
            return min_value
        if max_value is not None and result > max_value:
            logger.warning(None)
            return max_value
        
        return result
        
    except (ValueError, TypeError, AttributeError) as e:
        logger.debug(f"Integer sanitization failed for '{value}': {e}")
        return default


def x_sanitize_integer__mutmut_19(
    value: Union[str, int, float],
    default: int = 0,
    min_value: int = None,
    max_value: int = None
) -> int:
    """
    Safely convert input to integer.
    
    Handles:
    - String representations of integers ("42")
    - String representations of floats ("42.7" → 42)
    - Already-integer values
    - Invalid inputs (returns default)
    
    Args:
        value: Input to convert
        default: Value to return if conversion fails
        min_value: Minimum allowed value (None = no limit)
        max_value: Maximum allowed value (None = no limit)
        
    Returns:
        Integer value or default
    """
    try:
        # Handle None
        if value is None:
            return default
        
        # If already int, validate and return
        if isinstance(value, int):
            result = value
        # If float, truncate to int
        elif isinstance(value, float):
            result = int(value)
        # If string, parse as float first (handles "42.7"), then truncate
        elif isinstance(value, str):
            result = int(float(value.strip()))
        else:
            logger.warning(f"Cannot convert {type(value)} to integer: {value}")
            return default
        
        # Apply bounds if specified
        if min_value is not None and result < min_value:
            logger.warning(f"Value {result} below minimum {min_value}, clamping")
            return min_value
        if max_value is not None and result > max_value:
            logger.warning(f"Value {result} above maximum {max_value}, clamping")
            return max_value
        
        return result
        
    except (ValueError, TypeError, AttributeError) as e:
        logger.debug(None)
        return default

x_sanitize_integer__mutmut_mutants : ClassVar[MutantDict] = {
'x_sanitize_integer__mutmut_1': x_sanitize_integer__mutmut_1, 
    'x_sanitize_integer__mutmut_2': x_sanitize_integer__mutmut_2, 
    'x_sanitize_integer__mutmut_3': x_sanitize_integer__mutmut_3, 
    'x_sanitize_integer__mutmut_4': x_sanitize_integer__mutmut_4, 
    'x_sanitize_integer__mutmut_5': x_sanitize_integer__mutmut_5, 
    'x_sanitize_integer__mutmut_6': x_sanitize_integer__mutmut_6, 
    'x_sanitize_integer__mutmut_7': x_sanitize_integer__mutmut_7, 
    'x_sanitize_integer__mutmut_8': x_sanitize_integer__mutmut_8, 
    'x_sanitize_integer__mutmut_9': x_sanitize_integer__mutmut_9, 
    'x_sanitize_integer__mutmut_10': x_sanitize_integer__mutmut_10, 
    'x_sanitize_integer__mutmut_11': x_sanitize_integer__mutmut_11, 
    'x_sanitize_integer__mutmut_12': x_sanitize_integer__mutmut_12, 
    'x_sanitize_integer__mutmut_13': x_sanitize_integer__mutmut_13, 
    'x_sanitize_integer__mutmut_14': x_sanitize_integer__mutmut_14, 
    'x_sanitize_integer__mutmut_15': x_sanitize_integer__mutmut_15, 
    'x_sanitize_integer__mutmut_16': x_sanitize_integer__mutmut_16, 
    'x_sanitize_integer__mutmut_17': x_sanitize_integer__mutmut_17, 
    'x_sanitize_integer__mutmut_18': x_sanitize_integer__mutmut_18, 
    'x_sanitize_integer__mutmut_19': x_sanitize_integer__mutmut_19
}

def sanitize_integer(*args, **kwargs):
    result = _mutmut_trampoline(x_sanitize_integer__mutmut_orig, x_sanitize_integer__mutmut_mutants, args, kwargs)
    return result 

sanitize_integer.__signature__ = _mutmut_signature(x_sanitize_integer__mutmut_orig)
x_sanitize_integer__mutmut_orig.__name__ = 'x_sanitize_integer'


def x_sanitize_string__mutmut_orig(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, allow_tags=False)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace('\n', ' ').replace('\r', ' ')
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_1(
    value: str,
    max_length: int = 1001,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, allow_tags=False)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace('\n', ' ').replace('\r', ' ')
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_2(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = False,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, allow_tags=False)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace('\n', ' ').replace('\r', ' ')
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_3(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = False
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, allow_tags=False)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace('\n', ' ').replace('\r', ' ')
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_4(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, allow_tags=False)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace('\n', ' ').replace('\r', ' ')
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_5(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return "XXXX"
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, allow_tags=False)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace('\n', ' ').replace('\r', ' ')
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_6(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = None
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, allow_tags=False)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace('\n', ' ').replace('\r', ' ')
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_7(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace(None, '')
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, allow_tags=False)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace('\n', ' ').replace('\r', ' ')
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_8(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', None)
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, allow_tags=False)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace('\n', ' ').replace('\r', ' ')
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_9(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('')
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, allow_tags=False)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace('\n', ' ').replace('\r', ' ')
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_10(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', )
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, allow_tags=False)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace('\n', ' ').replace('\r', ' ')
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_11(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('XX\x00XX', '')
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, allow_tags=False)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace('\n', ' ').replace('\r', ' ')
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_12(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', 'XXXX')
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, allow_tags=False)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace('\n', ' ').replace('\r', ' ')
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_13(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip HTML if requested
    if strip_html:
        value = None
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace('\n', ' ').replace('\r', ' ')
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_14(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(None, allow_tags=False)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace('\n', ' ').replace('\r', ' ')
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_15(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, allow_tags=None)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace('\n', ' ').replace('\r', ' ')
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_16(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(allow_tags=False)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace('\n', ' ').replace('\r', ' ')
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_17(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, )
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace('\n', ' ').replace('\r', ' ')
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_18(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, allow_tags=True)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace('\n', ' ').replace('\r', ' ')
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_19(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, allow_tags=False)
    
    # Remove/replace newlines if not allowed
    if allow_newlines:
        value = value.replace('\n', ' ').replace('\r', ' ')
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_20(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, allow_tags=False)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = None
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_21(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, allow_tags=False)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace('\n', ' ').replace(None, ' ')
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_22(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, allow_tags=False)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace('\n', ' ').replace('\r', None)
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_23(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, allow_tags=False)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace('\n', ' ').replace(' ')
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_24(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, allow_tags=False)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace('\n', ' ').replace('\r', )
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_25(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, allow_tags=False)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace(None, ' ').replace('\r', ' ')
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_26(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, allow_tags=False)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace('\n', None).replace('\r', ' ')
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_27(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, allow_tags=False)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace(' ').replace('\r', ' ')
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_28(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, allow_tags=False)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace('\n', ).replace('\r', ' ')
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_29(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, allow_tags=False)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace('XX\nXX', ' ').replace('\r', ' ')
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_30(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, allow_tags=False)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace('\n', 'XX XX').replace('\r', ' ')
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_31(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, allow_tags=False)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace('\n', ' ').replace('XX\rXX', ' ')
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_32(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, allow_tags=False)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace('\n', ' ').replace('\r', 'XX XX')
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_33(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, allow_tags=False)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace('\n', ' ').replace('\r', ' ')
    
    # Truncate to max length
    if len(value) >= max_length:
        value = value[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_34(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, allow_tags=False)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace('\n', ' ').replace('\r', ' ')
    
    # Truncate to max length
    if len(value) > max_length:
        value = None
        logger.warning(f"String truncated to {max_length} characters")
    
    return value.strip()


def x_sanitize_string__mutmut_35(
    value: str,
    max_length: int = 1000,
    allow_newlines: bool = True,
    strip_html: bool = True
) -> str:
    """
    Sanitize string input for safe storage/display.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newline characters
        strip_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip HTML if requested
    if strip_html:
        value = sanitize_html(value, allow_tags=False)
    
    # Remove/replace newlines if not allowed
    if not allow_newlines:
        value = value.replace('\n', ' ').replace('\r', ' ')
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(None)
    
    return value.strip()

x_sanitize_string__mutmut_mutants : ClassVar[MutantDict] = {
'x_sanitize_string__mutmut_1': x_sanitize_string__mutmut_1, 
    'x_sanitize_string__mutmut_2': x_sanitize_string__mutmut_2, 
    'x_sanitize_string__mutmut_3': x_sanitize_string__mutmut_3, 
    'x_sanitize_string__mutmut_4': x_sanitize_string__mutmut_4, 
    'x_sanitize_string__mutmut_5': x_sanitize_string__mutmut_5, 
    'x_sanitize_string__mutmut_6': x_sanitize_string__mutmut_6, 
    'x_sanitize_string__mutmut_7': x_sanitize_string__mutmut_7, 
    'x_sanitize_string__mutmut_8': x_sanitize_string__mutmut_8, 
    'x_sanitize_string__mutmut_9': x_sanitize_string__mutmut_9, 
    'x_sanitize_string__mutmut_10': x_sanitize_string__mutmut_10, 
    'x_sanitize_string__mutmut_11': x_sanitize_string__mutmut_11, 
    'x_sanitize_string__mutmut_12': x_sanitize_string__mutmut_12, 
    'x_sanitize_string__mutmut_13': x_sanitize_string__mutmut_13, 
    'x_sanitize_string__mutmut_14': x_sanitize_string__mutmut_14, 
    'x_sanitize_string__mutmut_15': x_sanitize_string__mutmut_15, 
    'x_sanitize_string__mutmut_16': x_sanitize_string__mutmut_16, 
    'x_sanitize_string__mutmut_17': x_sanitize_string__mutmut_17, 
    'x_sanitize_string__mutmut_18': x_sanitize_string__mutmut_18, 
    'x_sanitize_string__mutmut_19': x_sanitize_string__mutmut_19, 
    'x_sanitize_string__mutmut_20': x_sanitize_string__mutmut_20, 
    'x_sanitize_string__mutmut_21': x_sanitize_string__mutmut_21, 
    'x_sanitize_string__mutmut_22': x_sanitize_string__mutmut_22, 
    'x_sanitize_string__mutmut_23': x_sanitize_string__mutmut_23, 
    'x_sanitize_string__mutmut_24': x_sanitize_string__mutmut_24, 
    'x_sanitize_string__mutmut_25': x_sanitize_string__mutmut_25, 
    'x_sanitize_string__mutmut_26': x_sanitize_string__mutmut_26, 
    'x_sanitize_string__mutmut_27': x_sanitize_string__mutmut_27, 
    'x_sanitize_string__mutmut_28': x_sanitize_string__mutmut_28, 
    'x_sanitize_string__mutmut_29': x_sanitize_string__mutmut_29, 
    'x_sanitize_string__mutmut_30': x_sanitize_string__mutmut_30, 
    'x_sanitize_string__mutmut_31': x_sanitize_string__mutmut_31, 
    'x_sanitize_string__mutmut_32': x_sanitize_string__mutmut_32, 
    'x_sanitize_string__mutmut_33': x_sanitize_string__mutmut_33, 
    'x_sanitize_string__mutmut_34': x_sanitize_string__mutmut_34, 
    'x_sanitize_string__mutmut_35': x_sanitize_string__mutmut_35
}

def sanitize_string(*args, **kwargs):
    result = _mutmut_trampoline(x_sanitize_string__mutmut_orig, x_sanitize_string__mutmut_mutants, args, kwargs)
    return result 

sanitize_string.__signature__ = _mutmut_signature(x_sanitize_string__mutmut_orig)
x_sanitize_string__mutmut_orig.__name__ = 'x_sanitize_string'
