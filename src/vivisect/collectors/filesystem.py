"""Open files collector."""

from __future__ import annotations

import psutil

from vivisect.models import FileDescriptor


def collect_open_files(proc: psutil.Process) -> list[FileDescriptor]:
    """Collect all open file descriptors for the process."""
    files: list[FileDescriptor] = []

    try:
        for f in proc.open_files():
            mode = _parse_mode(f.mode) if hasattr(f, "mode") else "unknown"  # type: ignore
            files.append(
                FileDescriptor(
                    fd=f.fd if hasattr(f, "fd") else None,
                    path=f.path,
                    mode=mode,
                )
            )
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        pass

    return files


def _parse_mode(mode: str) -> str:
    """Convert psutil file mode flags to human-readable strings."""
    mode_lower = mode.lower()
    if "w" in mode_lower and "r" in mode_lower:
        return "read-write"
    elif "w" in mode_lower or "a" in mode_lower:
        return "write"
    elif "r" in mode_lower:
        return "read"
    return "unknown"
