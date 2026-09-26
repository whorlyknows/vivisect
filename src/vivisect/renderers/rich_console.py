"""Rich terminal renderer — the main visual output."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from vivisect.utils import format_bytes, format_duration

if TYPE_CHECKING:
    from vivisect.models import ProcessSnapshot

# How many items to show in truncated mode
_TRUNCATE_THREADS = 5
_TRUNCATE_FILES = 5
_TRUNCATE_CONNECTIONS = 10


def render_rich(
    snapshot: ProcessSnapshot,
    show_all: bool = False,
    no_color: bool = False,
) -> None:
    """Render a ProcessSnapshot as beautiful terminal output."""
    console = Console(no_color=no_color)

    _render_header(console, snapshot)
    _render_resources(console, snapshot)
    _render_threads(console, snapshot, show_all)
    _render_connections(console, snapshot, show_all)
    _render_files(console, snapshot, show_all)
    _render_python(console, snapshot)
    _render_environment(console, snapshot, show_all)
    _render_footer(console, snapshot)


def _render_header(console: Console, snap: ProcessSnapshot) -> None:
    """Render the header panel with process identity."""
    uptime = ""
    if snap.create_time:
        delta = datetime.now(timezone.utc) - snap.create_time
        uptime = f" • uptime: {format_duration(delta.total_seconds())}"

    console.print(
        Panel(
            Text.from_markup(
                f"[bold cyan]🔬 VIVISECT[/] [dim]— Process Autopsy[/]\n"
                f"[dim]PID[/] [yellow]{snap.pid}[/]"
                f" [dim]•[/] [bold]{snap.name}[/]"
                f" [dim]•[/] [green]● {snap.status}[/]"
                f" [dim]•[/] [dim]user:[/] {snap.username}"
                f"{uptime}"
            ),
            border_style="cyan",
            padding=(1, 2),
        )
    )


def _render_resources(console: Console, snap: ProcessSnapshot) -> None:
    """Render resource usage section with metrics."""
    table = Table(
        title="📊 Resources",
        show_header=True,
        border_style="blue",
        title_style="bold blue",
        padding=(0, 2),
    )
    table.add_column("Metric", style="bold", min_width=16)
    table.add_column("Value", justify="right", min_width=20)

    # CPU with visual bar
    cpu_bar = _make_bar(snap.cpu_percent, 100)
    table.add_row("CPU", f"{cpu_bar} {snap.cpu_percent:.1f}%")

    # Memory with visual bar
    mem_bar = _make_bar(snap.memory_percent, 100)
    table.add_row(
        "Memory (RSS)",
        f"{mem_bar} {format_bytes(snap.memory_rss)} ({snap.memory_percent:.1f}%)",
    )
    table.add_row("Memory (VMS)", format_bytes(snap.memory_vms))
    table.add_row("Threads", str(snap.num_threads))
    table.add_row("Open Files", str(len(snap.open_files)))
    table.add_row("Connections", str(len(snap.connections)))

    if snap.cwd:
        table.add_row("Working Dir", snap.cwd)

    console.print(table)
    console.print()


def _render_threads(console: Console, snap: ProcessSnapshot, show_all: bool) -> None:
    """Render thread listing."""
    if not snap.threads:
        return

    table = Table(
        title=f"🧵 Threads ({len(snap.threads)})",
        border_style="yellow",
        title_style="bold yellow",
    )
    table.add_column("TID", style="dim")
    table.add_column("Status")
    table.add_column("User Time", justify="right")
    table.add_column("Sys Time", justify="right")

    display = snap.threads if show_all else snap.threads[:_TRUNCATE_THREADS]

    for t in display:
        table.add_row(
            str(t.id),
            f"[green]{t.status}[/]",
            f"{t.cpu_user_time:.3f}s",
            f"{t.cpu_system_time:.3f}s",
        )

    console.print(table)

    remaining = len(snap.threads) - len(display)
    if remaining > 0:
        console.print(f"  [dim]+ {remaining} more threads (use --all to show)[/]")

    console.print()


def _render_connections(console: Console, snap: ProcessSnapshot, show_all: bool) -> None:
    """Render network connections table."""
    if not snap.connections:
        return

    table = Table(
        title=f"🌐 Network Connections ({len(snap.connections)})",
        border_style="green",
        title_style="bold green",
    )
    table.add_column("Proto", style="bold magenta")
    table.add_column("Local Address")
    table.add_column("Remote Address")
    table.add_column("Status", style="bold")

    display = snap.connections if show_all else snap.connections[:_TRUNCATE_CONNECTIONS]

    for conn in display:
        status_style = {
            "LISTEN": "green",
            "ESTABLISHED": "cyan",
            "TIME_WAIT": "yellow",
            "CLOSE_WAIT": "red",
        }.get(conn.status, "dim")

        table.add_row(
            conn.type,
            conn.local_addr,
            conn.remote_addr or "—",
            f"[{status_style}]{conn.status}[/]",
        )

    console.print(table)

    remaining = len(snap.connections) - len(display)
    if remaining > 0:
        console.print(f"  [dim]+ {remaining} more connections (use --all to show)[/]")

    console.print()


def _render_files(console: Console, snap: ProcessSnapshot, show_all: bool) -> None:
    """Render open files list."""
    if not snap.open_files:
        return

    table = Table(
        title=f"📁 Open Files ({len(snap.open_files)})",
        border_style="yellow",
        title_style="bold #ffb86c",
    )
    table.add_column("FD", style="dim", width=6)
    table.add_column("Path")
    table.add_column("Mode", justify="right")

    display = snap.open_files if show_all else snap.open_files[:_TRUNCATE_FILES]

    mode_colors = {"read": "cyan", "write": "yellow", "read-write": "green"}

    for f in display:
        color = mode_colors.get(f.mode, "dim")
        table.add_row(
            str(f.fd) if f.fd is not None else "?",
            f.path,
            f"[{color}]{f.mode}[/]",
        )

    console.print(table)

    remaining = len(snap.open_files) - len(display)
    if remaining > 0:
        console.print(f"  [dim]+ {remaining} more files (use --all to show)[/]")

    console.print()


def _render_python(console: Console, snap: ProcessSnapshot) -> None:
    """Render Python runtime info."""
    if not snap.python:
        return

    table = Table(
        title="🐍 Python Runtime",
        border_style="magenta",
        title_style="bold magenta",
    )
    table.add_column("Property", style="dim")
    table.add_column("Value")

    table.add_row("Version", f"[green]{snap.python.version}[/]")
    table.add_row("Executable", snap.python.executable)
    table.add_row("GC Enabled", "[green]✓ Yes[/]" if snap.python.gc_enabled else "[red]✗ No[/]")
    if snap.python.gc_counts:
        table.add_row("GC Counts", str(snap.python.gc_counts))

    console.print(table)

    # Loaded modules as tags
    if snap.python.loaded_modules:
        mods = snap.python.loaded_modules[:20]  # Cap display
        tags = " ".join(f"[bold magenta]{m}[/]" for m in mods)
        remaining = len(snap.python.loaded_modules) - 20
        suffix = f" [dim]+ {remaining} more[/]" if remaining > 0 else ""
        console.print(f"  Modules: {tags}{suffix}")

    console.print()


def _render_environment(console: Console, snap: ProcessSnapshot, show_all: bool) -> None:
    """Render environment variables."""
    if not snap.environment:
        return

    console.print(
        Panel(
            f"[bold #ff79c6]🔒 Environment Variables ({len(snap.environment)})[/]",
            border_style="#ff79c6",
        )
    )

    items = list(snap.environment.items())
    display = items if show_all else items[:5]

    for key, value in display:
        if "REDACTED" in value:
            console.print(f"  [dim]{key}[/] = [red]{value}[/]")
        else:
            console.print(f"  [dim]{key}[/] = {value}")

    remaining = len(items) - len(display)
    if remaining > 0:
        console.print(
            f"  [dim]+ {remaining} more (use --all to show, --no-redact to reveal secrets)[/]"
        )

    console.print()


def _render_footer(console: Console, snap: ProcessSnapshot) -> None:
    """Render footer with timestamp and collection time."""
    console.print(
        f"[dim]Snapshot at {snap.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}"
        f" • Collection time: [green]{snap.collection_time_ms:.0f}ms[/]"
        f" • vivisect v{snap.vivisect_version}[/]",
        justify="center",
    )


def _make_bar(value: float, max_value: float, width: int = 20) -> str:
    """Create a simple text-based progress bar."""
    filled = int(width * min(value, max_value) / max_value) if max_value > 0 else 0
    empty = width - filled

    if value < 50:
        color = "green"
    elif value < 80:
        color = "yellow"
    else:
        color = "red"

    return f"[{color}]{'█' * filled}[/][dim]{'░' * empty}[/]"
