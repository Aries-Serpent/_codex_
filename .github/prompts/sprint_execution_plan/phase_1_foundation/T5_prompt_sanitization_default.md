# T5: Prompt Sanitization Default - Autonomous Copilot Prompt

🎯 **COPILOT INSTRUCTION:** @workspace Execute with security focus

## Metadata
```yaml
task_id: T5
priority: P0
phase: phase_1_foundation
effort: 1-2 days
dependencies: []
```

## Context
- **Gap:** No prompt sanitization by default (injection risk)
- **Target:** Default --sanitize=True in inference CLI
- **Impact:** +15% security score

## Implementation

### 1. Create Sanitizer Module
**File:** `src/codex_ml/safety/prompt_sanitizer.py`
```python
"""Prompt sanitization for injection prevention."""
import re

class PromptSanitizer:
    # Common injection patterns
    INJECTION_PATTERNS = [
        r"<script",
        r"javascript:",
        r"onerror=",
        r"onclick=",
        r"eval\(",
        r"exec\(",
        r"__import__",
        r"subprocess",
        r"os\.system",
    ]
    
    def __init__(self, strict=True):
        self.strict = strict
        self.patterns = [re.compile(p, re.IGNORECASE) for p in self.INJECTION_PATTERNS]
    
    def sanitize(self, prompt: str) -> str:
        """Sanitize prompt by removing/escaping dangerous patterns."""
        original = prompt
        
        for pattern in self.patterns:
            if pattern.search(prompt):
                if self.strict:
                    # Raise error in strict mode
                    raise ValueError(
                        f"Unsafe prompt detected (pattern: {pattern.pattern}). "
                        f"Prompt rejected for security."
                    )
                else:
                    # Remove pattern in non-strict mode
                    prompt = pattern.sub("[REDACTED]", prompt)
        
        if prompt != original:
            print(f"⚠️ Prompt sanitized: {len(original) - len(prompt)} chars removed")
        
        return prompt
    
    def is_safe(self, prompt: str) -> bool:
        """Check if prompt is safe without modifying."""
        try:
            self.sanitize(prompt)
            return True
        except ValueError:
            return False
```

### 2. Integrate into Inference CLI
**File:** `cli/inference.py` or `src/codex_ml/cli/inference.py`
```python
from codex_ml.safety.prompt_sanitizer import PromptSanitizer

parser.add_argument(
    "--sanitize",
    action="store_true",
    default=True,  # DEFAULT TO TRUE
    help="Enable prompt sanitization (default: True)"
)

parser.add_argument(
    "--no-sanitize",
    action="store_false",
    dest="sanitize",
    help="Disable prompt sanitization (not recommended)"
)

def run_inference(prompt, model, sanitize=True):
    if sanitize:
        sanitizer = PromptSanitizer(strict=True)
        prompt = sanitizer.sanitize(prompt)
    
    # Run inference
    output = model.generate(prompt)
    return output
```

### 3. Add Policy Configuration
**File:** `configs/safety_policy.yaml`
```yaml
prompt_sanitization:
  enabled: true
  strict_mode: true
  log_violations: true
  allowed_patterns: []
  blocked_patterns:
    - "<script"
    - "javascript:"
    - "eval("
    - "exec("
```

## Testing
```python
def test_sanitizer_blocks_injection():
    sanitizer = PromptSanitizer(strict=True)
    
    with pytest.raises(ValueError, match="Unsafe prompt"):
        sanitizer.sanitize("<script>alert('xss')</script>")

def test_sanitizer_non_strict_redacts():
    sanitizer = PromptSanitizer(strict=False)
    result = sanitizer.sanitize("Run <script>alert()</script> this")
    assert "[REDACTED]" in result
    assert "<script>" not in result

def test_cli_sanitizes_by_default(tmp_path):
    # CLI should sanitize unless --no-sanitize
    result = subprocess.run(
        ["python", "cli/inference.py", "--prompt", "<script>test</script>"],
        capture_output=True
    )
    assert "Unsafe prompt" in result.stderr.decode()

def test_safe_prompts_pass_through():
    sanitizer = PromptSanitizer()
    safe_prompt = "What is the capital of France?"
    assert sanitizer.sanitize(safe_prompt) == safe_prompt
```

## Validation
```bash
# Should fail (sanitized)
python cli/inference.py --prompt "<script>alert('test')</script>"
# Expected: ValueError or redaction

# Should succeed
python cli/inference.py --prompt "Normal safe prompt"

# Explicitly disable (not recommended)
python cli/inference.py --prompt "<script>test</script>" --no-sanitize
# Should work but log warning
```

## Acceptance
- [ ] PromptSanitizer class created with injection patterns
- [ ] CLI defaults to --sanitize=True
- [ ] --no-sanitize flag available (with warning)
- [ ] Strict mode raises errors on unsafe prompts
- [ ] Non-strict mode redacts patterns
- [ ] Tests cover common injection vectors
- [ ] SECURITY.md updated

## Audit Reference
- `reports/_codex_task_sequences-20251206.md` lines 37-43
- `workbench/exhaustive_audit/security_scorecard.md` → prompt sanitization gap
- Expected: security score 0.61 → 0.76

🤖 **Self-validate:** Test against OWASP Top 10 injection patterns
