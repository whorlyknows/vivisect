"""Collector orchestrator — assembles a complete ProcessSnapshot."""

from __future__ import annotations

import time
from datetime import datetime, timezone

import psutil

from vivisect.collectors.environment import collect_environment
from vivisect.collectors.filesystem import collect_open_files
from vivisect.collectors.network import collect_connections
from vivisect.collectors.process import collect_process_info
from vivisect.collectors.python_info import collect_python_info
from vivisect.collectors.threads import collect_threads
from vivisect.models import ProcessSnapshot


def collect_snapshot(pid: int, redact_env: bool = True) -> ProcessSnapshot:
    """Collect a complete process snapshot.

    Args:
        pid: The process ID to inspect.
        redact_env: If True, redact values of env vars that look like secrets.

    Returns:
        A fully populated ProcessSnapshot.
    """
    start = time.monotonic()
    proc = psutil.Process(pid)

    # Collect all data
    process_data = collect_process_info(proc)
    threads = collect_threads(proc)
    open_files = collect_open_files(proc)
    connections = collect_connections(proc)
    env_data = collect_environment(proc, redact=redact_env)
    python_info = collect_python_info(proc)

    elapsed_ms = (time.monotonic() - start) * 1000

    return ProcessSnapshot(
        timestamp=datetime.now(timezone.utc),
        collection_time_ms=round(elapsed_ms, 2),
        pid=pid,
        **process_data,
        threads=threads,
        open_files=open_files,
        connections=connections,
        **env_data,
        python=python_info,
    )
