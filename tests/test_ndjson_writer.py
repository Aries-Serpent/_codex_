import json
import json
import pathlib
import tempfile

from codex_ml.metrics.writers import NDJSONMetricsWriter


def test_writer_appends_lines():
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / "m.ndjson"
        w = NDJSONMetricsWriter(str(p))
        w.write({"step": 1})
        w.write({"step": 2})
        lines = p.read_text().strip().splitlines()
        assert [json.loads(x)["step"] for x in lines] == [1, 2]
