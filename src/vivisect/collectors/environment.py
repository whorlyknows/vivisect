"""Environment variables and CWD collector."""

from __future__ import annotations

import re
from typing import Any

import psutil

# Patterns that suggest a value is a secret
_SECRET_PATTERNS = re.compile(
    r"(password|secret|key|token|api_key|apikey|auth|credential|private)",
    re.IGNORECASE,
)


def collect_environment(proc: psutil.Process, redact: bool = True) -> dict[str, Any]:
    """Collect environment variables and CWD.

    Args:
        proc: The psutil Process object.
        redact: If True, replace values of secret-looking vars with "****REDACTED****".

    Returns:
        Dict with 'cwd' and 'environment' keys.
    """
    try:
        cwd = proc.cwd()
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        cwd = "unknown"

    env: dict[str, str] = {}
    try:
        raw_env = proc.environ()
        for key, value in sorted(raw_env.items()):
            if redact and _SECRET_PATTERNS.search(key):
                env[key] = "****REDACTED****"
            else:
                env[key] = value
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        pass

    return {"cwd": cwd, "environment": env}
