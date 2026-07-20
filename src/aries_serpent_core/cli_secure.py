"""
Secure CLI output module with XSS protection.

This module demonstrates proper HTML escaping techniques to prevent
Cross-Site Scripting (XSS) vulnerabilities (CWE-79).
"""

import html
from typing import Any, Optional
from urllib.parse import quote


class SecureHTMLOutput:
    """
    Handles secure HTML output generation with XSS protection.
    
    SECURITY: Escapes all user input before rendering in HTML context
    to prevent injection of malicious scripts.
    """

    @staticmethod
    def escape_html(user_input: str) -> str:
        """
        Escape HTML special characters in user input.
        
        ✅ VULNERABILITY FIXED: CWE-79 Cross-Site Scripting
        
        Previous vulnerable code:
            html_output = f"<div>{user_input}</div>"  # ❌ UNSAFE
        
        Secure implementation:
            escaped = html.escape(user_input)
            html_output = f"<div>{escaped}</div>"  # ✅ SAFE
        
        Conversion table:
            < becomes &lt;
            > becomes &gt;
            & becomes &amp;
            " becomes &quot;
            ' becomes &#x27;
        
        Args:
            user_input: Untrusted user input
            
        Returns:
            HTML-escaped string safe for HTML context
        """
        # SECURE: Use html.escape() to convert dangerous characters
        return html.escape(user_input)

    @staticmethod
    def escape_javascript(user_input: str) -> str:
        """
        Escape for JavaScript context.
        
        Note: html.escape() is not sufficient for JavaScript context.
        Use JSON encoding or additional escaping.
        
        Args:
            user_input: Untrusted user input
            
        Returns:
            JavaScript-safe escaped string
        """
        # Convert to JSON string (encodes all dangerous characters)
        import json
        return json.dumps(user_input)

    @staticmethod
    def escape_url(user_input: str) -> str:
        """
        Escape for URL context.
        
        Args:
            user_input: Untrusted user input
            
        Returns:
            URL-safe escaped string
        """
        # Use urllib.parse.quote for URL encoding
        return quote(user_input, safe='')

    @staticmethod
    def render_user_profile(username: str, bio: str) -> str:
        """
        Render HTML user profile with XSS protection.
        
        ✅ VULNERABILITY FIXED: CWE-79 Cross-Site Scripting
        
        Example attack:
            username = "<img src=x onerror='alert(1)'>"
            bio = "<script>steal_cookies()</script>"
        
        Without escaping: These scripts would execute!
        With escaping: They render as literal text.
        
        Args:
            username: User-provided username
            bio: User-provided biography
            
        Returns:
            Safe HTML output
        """
        # SECURE: Escape both username and bio
        safe_username = html.escape(username)
        safe_bio = html.escape(bio)
        
        return f"""
        <div class="profile">
            <h2>{safe_username}</h2>
            <p class="bio">{safe_bio}</p>
        </div>
        """

    @staticmethod
    def render_search_results(query: str, results: list[str]) -> str:
        """
        Render search results page with query reflection.
        
        ✅ VULNERABILITY FIXED: CWE-79 Reflected XSS
        
        Dangerous pattern (reflected XSS):
            search_query = request.args.get('q')
            html = f"<p>Search results for: {search_query}</p>"  # ❌ UNSAFE
        
        Attack:
            URL: /search?q=<script>alert('xss')</script>
            Result: JavaScript executes in page
        
        Args:
            query: Search query from user
            results: Search results list
            
        Returns:
            Safe HTML with escaped query reflection
        """
        # SECURE: Escape query before rendering
        safe_query = html.escape(query)
        
        html_output = f"<h1>Search Results for: {safe_query}</h1>\n"
        html_output += "<ul>\n"
        
        for result in results:
            safe_result = html.escape(result)
            html_output += f"  <li>{safe_result}</li>\n"
        
        html_output += "</ul>\n"
        return html_output

    @staticmethod
    def render_comment(comment_text: str, author: str) -> str:
        """
        Render user comment with XSS protection.
        
        ✅ VULNERABILITY FIXED: CWE-79 Stored XSS
        
        Without escaping, malicious comments can:
        - Steal session cookies
        - Redirect users to phishing sites
        - Deface the page
        - Insert keyloggers
        
        Args:
            comment_text: User-provided comment
            author: Comment author name
            
        Returns:
            Safe HTML comment rendering
        """
        # SECURE: Escape both author and comment text
        safe_author = html.escape(author)
        safe_text = html.escape(comment_text)
        
        return f"""
        <div class="comment">
            <div class="author">{safe_author}</div>
            <div class="text">{safe_text}</div>
        </div>
        """


# ============================================================================
# VULNERABILITY ANALYSIS: CWE-79 Cross-Site Scripting (XSS)
# ============================================================================

# VULNERABLE PATTERN (❌ DO NOT USE):
# ----
# user_input = "<script>alert('XSS')</script>"
# html = f"<div>{user_input}</div>"
#
# Result: The <script> tag is parsed as HTML and executes!

# SECURE PATTERN (✅ USE THIS):
# ----
# user_input = "<script>alert('XSS')</script>"
# safe_input = html.escape(user_input)  # Converts to &lt;script&gt;...&lt;/script&gt;
# html = f"<div>{safe_input}</div>"
#
# Result: The < and > are HTML entities, rendered as literal text

# KEY PRINCIPLES:
# 1. Always escape user input before rendering in HTML
# 2. Use context-specific escaping (HTML vs JavaScript vs URL)
# 3. Use auto-escaping template engines when possible (Jinja2)
# 4. Set Content Security Policy (CSP) headers
# 5. Validate input format (email, URL, etc.)

# CONTEXT-SPECIFIC ESCAPING:
# - HTML Context: &lt; &gt; &amp; &quot; &#x27;
# - JavaScript Context: Use JSON encoding
# - URL Context: Use urllib.parse.quote()
# - CSS Context: Use CSS-specific escaping
