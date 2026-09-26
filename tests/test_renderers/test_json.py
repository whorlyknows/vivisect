import json
import sys
from datetime import datetime, timezone
from io import StringIO

from vivisect.models import ProcessSnapshot
from vivisect.renderers.json_export import render_json


def test_render_json_valid(monkeypatch):
    snapshot = ProcessSnapshot(
        timestamp=datetime.now(timezone.utc),
        pid=12345,
        name="test_process",
        status="running",
    )

    fake_out = StringIO()
    monkeypatch.setattr(sys, "stdout", fake_out)

    render_json(snapshot)
    output = fake_out.getvalue()

    parsed = json.loads(output)
    assert parsed["pid"] == 12345
    assert parsed["name"] == "test_process"
