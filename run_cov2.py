import coverage
import pytest
import sys
import importlib.util

cov = coverage.Coverage()
cov.start()

# Load scalability.py directly without __init__.py
spec = importlib.util.spec_from_file_location("codex_ml.utils.scalability", "src/codex_ml/utils/scalability.py")
module = importlib.util.module_from_spec(spec)
sys.modules["codex_ml.utils.scalability"] = module
sys.modules["src.codex_ml.utils.scalability"] = module
spec.loader.exec_module(module)

pytest.main(['tests/unit/test_scalability_utils.py', '-q'])

cov.stop()
cov.save()
cov.report(show_missing=True, include="*/scalability.py")
