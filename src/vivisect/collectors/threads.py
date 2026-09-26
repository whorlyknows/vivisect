"""Thread collector."""

from __future__ import annotations

import psutil

from vivisect.models import ThreadInfo


def collect_threads(proc: psutil.Process) -> list[ThreadInfo]:
    """Collect information about all threads in the process."""
    threads: list[ThreadInfo] = []

    try:
        for t in proc.threads():
            threads.append(
                ThreadInfo(
                    id=t.id,
                    name=None,  # psutil doesn't provide thread names cross-platform
                    status="running",
                    cpu_user_time=round(t.user_time, 3),
                    cpu_system_time=round(t.system_time, 3),
                )
            )
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        pass

    # Sort by total CPU time descending (most active first)
    threads.sort(
        key=lambda t: t.cpu_user_time + t.cpu_system_time,
        reverse=True,
    )

    return threads
