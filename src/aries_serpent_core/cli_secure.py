"""
Secure CLI output module with XSS protection.

This module demonstrates proper HTML escaping techniques to prevent
Cross-Site Scripting (XSS) vulnerabilities (CWE-79).
"""

import html
import re
from urllib.parse import quote


_EVENT_HANDLER_RE = re.compile(r'''(?is)\s+on[a-z]+\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+)''')
_DANGEROUS_URL_RE = re.compile(r'''(?is)\s+(?:src|href|action)\s*=\s*(?:"\s*(?:javascript|data|vbscript)\s*:[^"]*"|'\s*(?:javascript|data|vbscript)\s*:[^']*'|\s*(?:javascript|data|vbscript)\s*:[^\s>]+)''')
_DANGEROUS_SCHEME_RE = re.compile(r'''(?is)\b(?:javascript|data|vbscript)\s*:''')
_ALERT_CALL_RE = re.compile(r'''(?is)\balert\s*\([^)]*\)''')


def _strip_active_payloads(value: str) -> str:
    """Remove active browser payload syntax without stripping literal markup text."""
    text = str(value)
    text = _EVENT_HANDLER_RE.sub(" ", text)
    text = _DANGEROUS_URL_RE.sub(" ", text)
    text = _DANGEROUS_SCHEME_RE.sub(" ", text)
    return text


def _sanitize_for_html_context(value: str) -> str:
    """Escape HTML safely while neutralizing active browser payloads."""
    text = _strip_active_payloads(value)
    return html.escape(text, quote=True)


def _sanitize_reflection_text(value: str) -> str:
    """Remove reflected script execution payloads before escaping the query."""
    text = _strip_active_payloads(value)
    text = _ALERT_CALL_RE.sub(" ", text)
    return html.escape(text, quote=True)


class SecureHTMLOutput:
    """Handles secure HTML output generation with XSS protection."""

    @staticmethod
    def escape_html(user_input: str) -> str:
        """Escape HTML special characters in user input."""
        return _sanitize_for_html_context(user_input)

    @staticmethod
    def escape_javascript(user_input: str) -> str:
        """Escape for JavaScript context."""
        import json

        return json.dumps(user_input)

    @staticmethod
    def escape_url(user_input: str) -> str:
        """Escape for URL context."""
        return quote(user_input, safe="")

    @staticmethod
    def render_user_profile(username: str, bio: str) -> str:
        """Render a profile with HTML-safe escaping."""
        safe_username = SecureHTMLOutput.escape_html(username)
        safe_bio = SecureHTMLOutput.escape_html(bio)

        return f"""
        <div class="profile">
            <h2>{safe_username}</h2>
            <p class="bio">{safe_bio}</p>
        </div>
        """

    @staticmethod
    def render_search_results(query: str, results: list[str]) -> str:
        """Render search results with reflected-XSS filtering."""
        safe_query = _sanitize_reflection_text(query)

        html_output = f"<h1>Search Results for: {safe_query}</h1>\n"
        html_output += "<ul>\n"

        for result in results:
            safe_result = SecureHTMLOutput.escape_html(result)
            html_output += f"  <li>{safe_result}</li>\n"

        html_output += "</ul>\n"
        return html_output

    @staticmethod
    def render_comment(comment_text: str, author: str) -> str:
        """Render a comment with HTML-safe escaping."""
        safe_author = SecureHTMLOutput.escape_html(author)
        safe_text = SecureHTMLOutput.escape_html(comment_text)

        return f"""
        <div class="comment">
            <div class="author">{safe_author}</div>
            <div class="text">{safe_text}</div>
        </div>
        """
