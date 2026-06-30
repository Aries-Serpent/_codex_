#!/usr/bin/env python3
"""
Verify secrets baseline - ensures no secrets are committed to repository.
"""
import subprocess
import sys

def verify_secrets():
    """Run git-secrets scan on the repository."""
    try:
        # Use git grep to check for common secret patterns
        result = subprocess.run(
            ["git", "grep", "-E", r"(password|secret|token|key)\s*=\s*['\"]", "HEAD"],
            cwd="/home/runner/work/_codex_/_codex_",
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:  # Found matches
            print("❌ FAIL: Found potential secrets in repository")
            print(result.stdout)
            return False
        
        # returncode=1 means no matches found (which is good)
        print("✅ PASS: Secrets baseline verified - no obvious secrets found")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: Error during secrets verification: {e}")
        return False

if __name__ == "__main__":
    success = verify_secrets()
    sys.exit(0 if success else 1)
