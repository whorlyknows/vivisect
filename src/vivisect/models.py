"""Pydantic data models for process snapshots."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ThreadInfo(BaseModel):
    """Information about a single thread."""

    id: int
    name: str | None = None
    status: str = "unknown"
    cpu_user_time: float = 0.0
    cpu_system_time: float = 0.0


class FileDescriptor(BaseModel):
    """An open file descriptor."""

    fd: int | None = None
    path: str
    mode: str = "unknown"  # "read", "write", "read-write", "unknown"


class NetworkConnection(BaseModel):
    """An open network connection."""

    fd: int | None = None
    family: str  # "AF_INET", "AF_INET6", "AF_UNIX"
    type: str  # "SOCK_STREAM", "SOCK_DGRAM"
    local_addr: str = ""
    remote_addr: str | None = None
    status: str = "NONE"


class PythonInfo(BaseModel):
    """Python-specific runtime information."""

    version: str = "unknown"
    executable: str = "unknown"
    sys_path: list[str] = Field(default_factory=list)
    loaded_modules: list[str] = Field(default_factory=list)
    gc_enabled: bool = True
    gc_counts: tuple[int, int, int] | None = None


class ProcessSnapshot(BaseModel):
    """Complete point-in-time autopsy of a running process."""

    # Metadata
    timestamp: datetime
    collection_time_ms: float = 0.0
    vivisect_version: str = "0.1.0"

    # Core process info
    pid: int
    name: str
    status: str
    username: str = "unknown"
    create_time: datetime | None = None

    # Resource usage
    cpu_percent: float = 0.0
    memory_rss: int = 0  # bytes
    memory_vms: int = 0  # bytes
    memory_percent: float = 0.0
    num_threads: int = 0
    num_fds: int = 0

    # Detail collections
    command_line: list[str] = Field(default_factory=list)
    cwd: str = ""
    environment: dict[str, str] = Field(default_factory=dict)
    threads: list[ThreadInfo] = Field(default_factory=list)
    open_files: list[FileDescriptor] = Field(default_factory=list)
    connections: list[NetworkConnection] = Field(default_factory=list)

    # Python-specific
    python: PythonInfo | None = None


ProcessSnapshot.model_rebuild()
