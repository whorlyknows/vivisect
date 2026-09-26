"""Python-specific information collector."""

from __future__ import annotations

import psutil

from vivisect.models import PythonInfo


def collect_python_info(proc: psutil.Process) -> PythonInfo | None:
    """Attempt to collect Python-specific runtime information.

    This uses heuristics based on the process command line and name.
    For deep introspection (sys.path, loaded modules), we parse /proc/<pid>/maps
    on Linux or fall back to cmdline-based heuristics.

    Returns:
        PythonInfo if the process appears to be Python, None otherwise.
    """
    try:
        name = (proc.name() or "").lower()
        cmdline = proc.cmdline() or []
        cmdline_str = " ".join(cmdline).lower()
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        return None

    if "python" not in name and "python" not in cmdline_str:
        return None

    # Extract Python version from the executable name (e.g., "python3.13")
    version = _extract_python_version(name, cmdline)

    # Get the executable path
    try:
        executable = proc.exe()
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        executable = cmdline[0] if cmdline else "unknown"

    # Attempt to find loaded modules by scanning memory maps
    loaded_modules = _scan_loaded_modules(proc)

    return PythonInfo(
        version=version,
        executable=executable,
        sys_path=[],  # Cannot reliably get without code injection
        loaded_modules=loaded_modules,
        gc_enabled=True,  # Assume default
        gc_counts=None,  # Cannot get without code injection
    )


def _extract_python_version(name: str, cmdline: list[str]) -> str:
    """Try to extract Python version string from process info."""
    import re

    # Try executable name: python3.13, python3.12, etc.
    for source in [name] + cmdline:
        match = re.search(r"python(\d+\.\d+(?:\.\d+)?)", source)
        if match:
            return match.group(1)

    # Fallback
    if "python3" in name:
        return "3.x"
    return "unknown"


def _scan_loaded_modules(proc: psutil.Process) -> list[str]:
    """Scan process memory maps for loaded Python packages.

    On Linux, reads /proc/<pid>/maps for .so files and .py files.
    On other platforms, returns an empty list.
    """
    modules: set[str] = set()
    try:
        for mmap in proc.memory_maps(grouped=False):
            path = mmap.path.replace("\\", "/")
            if "site-packages" in path:
                # Extract package name from path like:
                # /venv/lib/python3.13/site-packages/flask/app.py
                parts = path.split("site-packages/")
                if len(parts) > 1:
                    pkg = parts[1].split("/")[0].split(".")[0]
                    if pkg and pkg not in ("__pycache__",):
                        modules.add(pkg)
    except (psutil.AccessDenied, psutil.NoSuchProcess, AttributeError):
        pass

    return sorted(modules)
