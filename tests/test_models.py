from datetime import datetime, timezone

from vivisect.models import ProcessSnapshot


def test_process_snapshot_creation():
    snapshot = ProcessSnapshot(
        timestamp=datetime.now(timezone.utc),
        pid=12345,
        name="test_process",
        status="running",
    )
    assert snapshot.pid == 12345
    assert snapshot.name == "test_process"

    # JSON round-trip
    json_data = snapshot.model_dump_json()
    reloaded = ProcessSnapshot.model_validate_json(json_data)
    assert reloaded.pid == snapshot.pid
    assert reloaded.timestamp == snapshot.timestamp
