# Safety & Security Modules

The safety subsystem now consolidates validation, filtering, and secret management in `src/security`.

## Core Utilities
- `validate_input(value, input_type="text")` – Guards against SQL injection, XSS, and path traversal.
- `sanitize_user_content(value)` – HTML escapes and redacts flagged content.
- `rate_limiter(calls, period)` – Decorator to throttle endpoints or critical functions.
- `verify_csrf_token` / `verify_session_integrity` – Enforce session protections for web clients.

```python
from src.security import validate_input, rate_limiter

@rate_limiter(calls=10, period=60)
def process_prompt(prompt: str) -> str:
    safe_prompt = validate_input(prompt, input_type="html")
    return safe_prompt
```

## Content Filters
`src/security/content_filters.py` provides profanity, PII, and malware detection helpers.

```python
from src.security import detect_personal_data

payload = "Contact jane@example.com with SSN 123-45-6789"
flags = detect_personal_data(payload)
if flags["pii"]:
    raise RuntimeError("PII detected")
```

## Secret Management
- `check_secret_entropy` rejects weak credentials.
- `rotate_secret` implements policy-aware rotation with history tracking.
- Encryption helpers (`generate_key`, `encrypt`, `decrypt`) protect stored secrets when the optional
  `cryptography` dependency is available.

See [docs/security/SECURITY_POLICY.md](../security/SECURITY_POLICY.md) for policies and runbooks.
