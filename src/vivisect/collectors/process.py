"""Core process info collector (CPU, memory, status)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import psutil


def collect_process_info(proc: psutil.Process) -> dict[str, Any]:
    """Collect core process metrics.

    Returns a dict suitable for unpacking into ProcessSnapshot fields.
    """
    with proc.oneshot():
        mem = proc.memory_info()
        try:
            create_time = datetime.fromtimestamp(proc.create_time(), tz=timezone.utc)
        except (OSError, psutil.AccessDenied):
            create_time = None

        try:
            username = proc.username()
        except psutil.AccessDenied:
            username = "unknown"

        try:
            num_fds = proc.num_fds()
        except AttributeError:
            # num_fds() not available on Windows
            try:
                num_fds = len(proc.open_files())
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                num_fds = 0

        return {
            "name": proc.name(),
            "status": proc.status(),
            "username": username,
            "create_time": create_time,
            "cpu_percent": proc.cpu_percent(interval=0.1),
            "memory_rss": mem.rss,
            "memory_vms": mem.vms,
            "memory_percent": round(proc.memory_percent(), 2),
            "num_threads": proc.num_threads(),
            "num_fds": num_fds,
            "command_line": proc.cmdline(),
        }
