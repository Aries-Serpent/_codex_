"""CLI module with XSS protection - SECURE VERSION.

This module provides CLI functions with proper HTML escaping
to prevent Cross-Site Scripting (XSS) vulnerabilities (CWE-79).

Security Model:
- All user input is HTML-escaped before output
- Uses html.escape() for automatic escaping
- Alternative: Use templating engines with auto-escaping enabled
"""

import html
from typing import Optional


def display_user_info(user_input: str) -> str:
    """Display user information with XSS protection.

    Escapes HTML special characters to prevent XSS attacks.
    User input that contains HTML tags will be safely escaped.

    Args:
        user_input: Untrusted user-provided text

    Returns:
        Safely escaped string suitable for HTML output

    Example:
        >>> display_user_info("<script>alert('xss')</script>")
        "User said: &lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"
    """
    # SECURE: html.escape() converts HTML special characters
    # < becomes &lt;, > becomes &gt;, & becomes &amp;, etc.
    escaped = html.escape(user_input)
    return f"User said: {escaped}"


def render_html_template(title: str, content: str) -> str:
    """Render HTML with escaped user content.

    Uses html.escape() to safely embed user-provided content in HTML.

    Args:
        title: Page title (user-provided, untrusted)
        content: Page content (user-provided, untrusted)

    Returns:
        Safe HTML string with escaped content
    """
    # SECURE: Escape both title and content
    safe_title = html.escape(title)
    safe_content = html.escape(content)

    return f"""<!DOCTYPE html>
<html>
<head>
    <title>{safe_title}</title>
</head>
<body>
    <h1>{safe_title}</h1>
    <div>{safe_content}</div>
</body>
</html>"""


def process_user_comment(comment: str, quote: bool = True) -> str:
    """Process user-provided comment with XSS protection.

    Args:
        comment: User comment (untrusted input)
        quote: Whether to add quotes around the comment

    Returns:
        Safely escaped comment

    Example:
        >>> process_user_comment("Hello <b>world</b>")
        '"Hello &lt;b&gt;world&lt;/b&gt;"'
    """
    # SECURE: Escape the comment before processing
    escaped_comment = html.escape(comment)

    if quote:
        return f'"{escaped_comment}"'
    return escaped_comment


def safe_print_to_html(message: Optional[str] = None) -> str:
    """Safely print a message to HTML with XSS protection.

    Args:
        message: Message to print (user-provided, may be None)

    Returns:
        Safe HTML representation

    Raises:
        ValueError: If message is not a string or None
    """
    if message is None:
        return "<p>No message</p>"

    if not isinstance(message, str):
        raise ValueError(f"message must be a string or None, got {type(message)}")

    # SECURE: Escape before HTML output
    safe_message = html.escape(message)
    return f"<p>{safe_message}</p>"
