"""Utility functions."""

from __future__ import annotations

import platform
import sys


def format_bytes(n: int) -> str:
    """Format byte count to human-readable string.

    Examples:
        format_bytes(1024) -> "1.0 KB"
        format_bytes(1073741824) -> "1.0 GB"
    """
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024  # type: ignore[assignment]
    return f"{n:.1f} PB"


def format_duration(seconds: float) -> str:
    """Format seconds to human-readable duration.

    Examples:
        format_duration(3661) -> "1h 1m 1s"
        format_duration(45) -> "45s"
    """
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)

    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")
    return " ".join(parts)


def is_linux() -> bool:
    return sys.platform == "linux"


def is_macos() -> bool:
    return sys.platform == "darwin"


def is_windows() -> bool:
    return sys.platform == "win32"


def get_platform_info() -> str:
    return f"{platform.system()} {platform.release()} ({platform.machine()})"
