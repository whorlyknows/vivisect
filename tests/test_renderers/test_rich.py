from datetime import datetime, timezone

from vivisect.models import ProcessSnapshot, ThreadInfo
from vivisect.renderers.rich_console import render_rich


def test_render_rich_no_crash():
    snapshot = ProcessSnapshot(
        timestamp=datetime.now(timezone.utc),
        pid=12345,
        name="test_process",
        status="running",
        threads=[ThreadInfo(id=1, status="running")],
    )
    # Should run without raising any exceptions
    render_rich(snapshot, show_all=True, no_color=True)
