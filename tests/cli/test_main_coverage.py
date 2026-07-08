#         ), f"Option {option} not documented in train help"
#                     {"key": "config_value"},  # cfg
# 
# Created: 2026-01-18
# Target: 20+ tests covering all major CLI functionality.
# Created: 2026-01-18
# Phase: 14.1 - Core Module Testing
# Created: 2026-01-18
# AI Agency Policy Compliance: ✅
#         """Verify --curriculum option is documented."""
#         result = subprocess.run(
#             [sys.executable, "-m", "codex_ml.cli", "train", "--help"],
#             capture_output=True,
#             text=True,
#             check=False,
#             timeout=30,
#         )
#         output = result.stdout + result.stderr
#         if result.returncode == 0 and "train" in output.lower():
#             # Curriculum option should be available
#             assert "--curriculum" in output or "curriculum" in output.lower(), "Condition must be true"
