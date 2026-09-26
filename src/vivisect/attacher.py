"""Process resolution and validation."""

from __future__ import annotations

import psutil


class ProcessNotFoundError(Exception):
    """Raised when the target process cannot be found."""


class NotPythonError(Exception):
    """Raised when the target process doesn't appear to be Python."""


def resolve_pid(target: str, by_name: bool = False) -> int:
    """Resolve a target (PID string or process name) to a validated PID.

    Args:
        target: Either a numeric PID string or a process name (if by_name=True).
        by_name: If True, search running processes by name.

    Returns:
        The resolved PID as an integer.

    Raises:
        ProcessNotFoundError: If the process cannot be found.
        NotPythonError: If the process doesn't appear to be a Python process.
    """
    if by_name:
        return _find_by_name(target)
    else:
        return _validate_pid(target)


def _validate_pid(target: str) -> int:
    """Validate that a PID string refers to a running process."""
    try:
        pid = int(target)
    except ValueError:
        raise ProcessNotFoundError(
            f"'{target}' is not a valid PID. Use --find to search by process name."
        ) from None

    if not psutil.pid_exists(pid):
        raise ProcessNotFoundError(f"No process found with PID {pid}.")

    proc = psutil.Process(pid)
    _check_if_python(proc)
    return pid


def _find_by_name(name: str) -> int:
    """Search for a running process by name."""
    matches: list[psutil.Process] = []

    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            proc_name = (proc.info["name"] or "").lower()
            cmdline = " ".join(proc.info["cmdline"] or []).lower()
            if name.lower() in proc_name or name.lower() in cmdline:
                matches.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if not matches:
        raise ProcessNotFoundError(f"No running process found matching '{name}'.")

    if len(matches) > 1:
        # Return the one with highest CPU usage (most likely the main process)
        matches.sort(key=lambda p: p.cpu_percent(), reverse=True)

    result = matches[0]
    _check_if_python(result)
    return result.pid


def _check_if_python(proc: psutil.Process) -> None:
    """Warn if the process doesn't appear to be Python."""
    try:
        name = (proc.name() or "").lower()
        cmdline = " ".join(proc.cmdline() or []).lower()
        if "python" not in name and "python" not in cmdline:
            raise NotPythonError(
                f"PID {proc.pid} ({proc.name()}) doesn't appear to be a Python process. "
                "Continuing anyway — some Python-specific fields will be empty."
            )
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
