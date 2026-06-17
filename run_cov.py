import coverage
import sys

cov = coverage.Coverage(source=['src.codex_ml.utils.stub_cleanup'])
cov.start()

import tempfile
from pathlib import Path
from tests.integration.test_stub_cleanup import test_integration_stub_cleanup

with tempfile.TemporaryDirectory() as d:
    test_integration_stub_cleanup(Path(d))

cov.stop()
cov.save()
cov.report(show_missing=True)
