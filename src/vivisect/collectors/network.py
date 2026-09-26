"""Network connections collector."""

from __future__ import annotations

import socket
from typing import Any

import psutil

from vivisect.models import NetworkConnection

# Map psutil socket constants to readable strings
_FAMILY_MAP = {
    socket.AF_INET: "AF_INET",
    socket.AF_INET6: "AF_INET6",
}
_TYPE_MAP = {
    socket.SOCK_STREAM: "TCP",
    socket.SOCK_DGRAM: "UDP",
}

# Add AF_UNIX on platforms that support it
if hasattr(socket, "AF_UNIX"):
    _FAMILY_MAP[socket.AF_UNIX] = "AF_UNIX"


def collect_connections(proc: psutil.Process) -> list[NetworkConnection]:
    """Collect all network connections for the process."""
    connections: list[NetworkConnection] = []

    try:
        for conn in proc.net_connections(kind="all"):
            local = _format_addr(conn.laddr)
            remote = _format_addr(conn.raddr) if conn.raddr else None

            connections.append(
                NetworkConnection(
                    fd=conn.fd if conn.fd != -1 else None,
                    family=_FAMILY_MAP.get(conn.family, str(conn.family)),
                    type=_TYPE_MAP.get(conn.type, str(conn.type)),
                    local_addr=local,
                    remote_addr=remote,
                    status=conn.status if conn.status != "NONE" else "NONE",
                )
            )
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        pass

    # Sort: LISTEN first, then ESTABLISHED, then others
    status_order = {"LISTEN": 0, "ESTABLISHED": 1}
    connections.sort(key=lambda c: status_order.get(c.status, 99))

    return connections


def _format_addr(addr: Any) -> str:
    """Format a psutil address tuple as ip:port string."""
    if not addr:
        return ""
    if isinstance(addr, tuple) and len(addr) == 2:
        ip, port = addr
        if ":" in str(ip):
            return f"[{ip}]:{port}"
        return f"{ip}:{port}"
    return str(addr)
