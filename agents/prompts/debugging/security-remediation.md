# Security Vulnerability Remediation

This prompt guides AI Agents through identifying and fixing security vulnerabilities.

## Context

Use this prompt when security scans (CodeQL, Bandit, etc.) identify vulnerabilities or for proactive security reviews.

## Prompt Template

```
I need help remediating a security vulnerability in the Codex repository.

**Vulnerability Information:**
- Type: [SQL Injection / XSS / Path Traversal / etc.]
- Severity: [Critical / High / Medium / Low]
- Location: [file:line]
- Scanner: [CodeQL / Bandit / Manual Review]
- Description: [vulnerability description]

**Remediation Steps:**

1. **Understand the Vulnerability**
   - Read the security alert details
   - Understand the attack vector
   - Identify affected code paths
   - Assess potential impact

2. **Common Vulnerabilities and Fixes**

   **SQL Injection:**
   ```python
   # ❌ Vulnerable
   query = f"SELECT * FROM users WHERE name = '{user_input}'"
   cursor.execute(query)
   
   # ✅ Fixed: Use parameterized queries
   query = "SELECT * FROM users WHERE name = ?"
   cursor.execute(query, (user_input,))
   ```

   **Cross-Site Scripting (XSS):**
   ```python
   # ❌ Vulnerable
   html = f"<div>{user_input}</div>"
   
   # ✅ Fixed: Escape user input
   import html
   safe_html = f"<div>{html.escape(user_input)}</div>"
   
   # ✅ Better: Use template engine with auto-escaping
   from jinja2 import Template
   template = Template("<div>{{ user_input }}</div>")
   safe_html = template.render(user_input=user_input)
   ```

   **Path Traversal:**
   ```python
   # ❌ Vulnerable
   file_path = os.path.join(base_dir, user_input)
   with open(file_path) as f:
       data = f.read()
   
   # ✅ Fixed: Validate and sanitize path using robust containment check
   import os
   from pathlib import Path
   
   file_path = os.path.join(base_dir, user_input)
   real_base = os.path.realpath(base_dir)
   real_path = os.path.realpath(file_path)
   
   # Use commonpath for robust containment - prevents /safe/dir_evil bypassing /safe/dir
   try:
       if os.path.commonpath([real_base, real_path]) != real_base:
           raise ValueError("Invalid path - path traversal attempt detected")
   except ValueError:
       # commonpath raises ValueError if paths are on different drives (Windows)
       # or have no common prefix - treat as invalid path
       raise ValueError("Invalid path - path traversal attempt detected")
   
   with open(real_path) as f:
       data = f.read()
   ```

   **Command Injection:**
   ```python
   # ❌ Vulnerable
   os.system(f"ls {user_input}")
   
   # ✅ Fixed: Use subprocess with list
   import subprocess
   subprocess.run(["ls", user_input], check=True)
   
   # ✅ Better: Validate input first
   if not user_input.isalnum():
       raise ValueError("Invalid input")
   subprocess.run(["ls", user_input], check=True)
   ```

   **Insecure Deserialization:**
   ```python
   # ❌ Vulnerable
   import pickle
   data = pickle.loads(user_data)
   
   # ✅ Fixed: Use safe formats
   import json
   data = json.loads(user_data)
   
   # ✅ Or validate source
   if not is_trusted_source(source):
       raise SecurityError("Untrusted data")
   ```

   **Hardcoded Secrets:**
   ```python
   # ❌ Vulnerable
   API_KEY = "sk_live_abc123..."
   
   # ✅ Fixed: Use environment variables
   import os
   API_KEY = os.getenv("API_KEY")
   if not API_KEY:
       raise ValueError("API_KEY not set")
   ```

   **Weak Cryptography:**
   ```python
   # ❌ Vulnerable: MD5 for passwords
   import hashlib
   password_hash = hashlib.md5(password.encode()).hexdigest()
   
   # ✅ Fixed: Use proper password hashing
   from passlib.hash import bcrypt
   password_hash = bcrypt.hash(password)
   ```

3. **Codex-Specific Security**

   **HTML Generation (planning_components.py):**
   ```python
   # ✅ Already implemented
   def sanitizeHTML(text):
       """Escape HTML to prevent XSS."""
       import html
       return html.escape(text)
   ```

   **File Operations (connectors/base.py):**
   ```python
   # ✅ Already implemented
   def _resolve(self, relative_path: str) -> Path:
       """Validate path to prevent traversal."""
       candidate = (self.root.joinpath(*clean_parts)).resolve()
       if not os.path.commonpath([self.root, candidate]) == str(self.root):
           raise ConnectorError(f"refusing to access path outside root")
       return candidate
   ```

4. **Verification and Testing**

   **Security Tests:**
   ```python
   def test_no_path_traversal():
       """Ensure path traversal is prevented."""
       connector = LocalConnector(root="/safe/dir")
       with pytest.raises(ConnectorError):
           connector.read_file("../../etc/passwd")
   
   def test_xss_prevention():
       """Ensure XSS is prevented."""
       malicious = "<script>alert('XSS')</script>"
       safe = sanitize_html(malicious)
       assert "<script>" not in safe
       assert "&lt;script&gt;" in safe
   ```

   **Run Security Scanners:**
   ```bash
   # CodeQL
   codeql database create --language=python db
   codeql database analyze db --format=sarif-latest --output=results.sarif
   
   # Bandit
   bandit -r src/ -f json -o bandit-report.json
   
   # Safety (dependencies)
   safety check --json
   
   # detect-secrets
   detect-secrets scan --baseline .secrets.baseline
   ```

5. **Fix Implementation**
   - Apply minimal fix for vulnerability
   - Don't introduce new functionality
   - Maintain backward compatibility if possible
   - Add security tests
   - Document security considerations

6. **Post-Fix Validation**
   ```bash
   # Re-run security scanner
   codeql database analyze db --format=sarif-latest
   
   # Run tests
   pytest tests/ -v
   
   # Check for regressions
   pytest tests/security/ -v
   
   # Manual verification
   # Try to exploit the vulnerability
   ```

7. **Documentation**
   ```python
   def process_user_input(data: str) -> str:
       """
       Process user input safely.
       
       Security: Input is sanitized to prevent XSS attacks.
       - HTML entities are escaped
       - Script tags are neutralized
       - All user input is treated as untrusted
       
       See: SECURITY.md for security guidelines
       """
       return html.escape(data)
   ```

**Security Checklist:**

- [ ] Understood the vulnerability and attack vector
- [ ] Identified all affected code paths
- [ ] Applied appropriate fix
- [ ] Added security tests
- [ ] Verified fix with scanner
- [ ] Checked for similar issues elsewhere
- [ ] Documented security considerations
- [ ] Reviewed related code for vulnerabilities

**Prevention Best Practices:**

1. **Input Validation**: Always validate and sanitize user input
2. **Least Privilege**: Run with minimum required permissions
3. **Defense in Depth**: Multiple layers of security
4. **Secure Defaults**: Fail securely by default
5. **Keep Dependencies Updated**: Regular security updates

**Codex Repository Security:**

- Use CodeQL for static analysis
- Run Bandit for Python-specific issues
- Check `.secrets.baseline` for secret scanning
- Follow SECURITY.md guidelines
- Use security allowlist when appropriate
- Document security decisions

**Warning: False Positives**

Some security alerts may be false positives:
- Review context carefully
- Understand the code flow
- Document why it's safe if applicable
- Add to allowlist if verified safe

**Escalation:**

If unsure about security fix:
- Consult SECURITY.md
- Review similar CVEs
- Ask security team
- Don't guess on critical vulnerabilities
```

## Examples

### Example 1: XSS in HTML Generation

```
File: scripts/planning_components.py:309
Issue: User input directly inserted into HTML
Severity: High

Fix:
- Added sanitizeHTML() function
- Escape all user inputs before HTML insertion
- Use data attributes instead of IDs for safety
```

### Example 2: Path Traversal in Connector

```
File: src/codex_ml/connectors/base.py:94
Issue: Path not validated for traversal
Severity: Critical

Fix:
- Added _resolve() method with path validation
- Check if resolved path is within root
- Raise ConnectorError for invalid paths
```

### Example 3: Hardcoded Secret

```
File: config/api_keys.py:10
Issue: API key hardcoded in source
Severity: Critical

Fix:
- Remove hardcoded key
- Use environment variable
- Add to .env.example
- Update documentation
```

## Related Prompts


- [Test Failure Debugging](./test-failure-debugging.md)

## Automation

Security scanning is integrated into CI/CD:

```yaml
# .github/workflows/security.yml
- name: Run CodeQL
  uses: github/codeql-action/analyze@v2
  
- name: Run Bandit
  run: bandit -r src/ -f json
```

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [Codex Security Policy](../../../SECURITY.md)
- [CodeQL Documentation](https://codeql.github.com/docs/)
