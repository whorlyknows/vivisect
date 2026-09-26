"""CLI entry point using Click."""

from __future__ import annotations

import contextlib
import sys

import click

from vivisect import __version__


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("target")
@click.option(
    "--json",
    "output_format",
    flag_value="json",
    default=None,
    help="Output snapshot as JSON to stdout.",
)
@click.option(
    "--html",
    "html_path",
    type=click.Path(dir_okay=False, writable=True),
    default=None,
    help="Export snapshot as a self-contained HTML report.",
)
@click.option(
    "--find",
    is_flag=True,
    default=False,
    help="Treat TARGET as a process name to search for (instead of a PID).",
)
@click.option(
    "--all",
    "show_all",
    is_flag=True,
    default=False,
    help="Show all items (threads, files, connections) without truncation.",
)
@click.option(
    "--no-redact",
    is_flag=True,
    default=False,
    help="Show all environment variable values (by default, secrets are redacted).",
)
@click.option(
    "--no-color",
    is_flag=True,
    default=False,
    help="Disable colored terminal output.",
)
@click.version_option(version=__version__, prog_name="vivisect")
def main(
    target: str,
    output_format: str | None,
    html_path: str | None,
    find: bool,
    show_all: bool,
    no_redact: bool,
    no_color: bool,
) -> None:
    """🔬 Vivisect — Attach to a running Python process and perform a live autopsy.

    TARGET is a PID (e.g., 12345) or a process name with --find (e.g., --find gunicorn).

    \b
    Examples:
        vivisect 12345              Snapshot PID 12345
        vivisect 12345 --json       Export as JSON
        vivisect 12345 --html out.html  Generate HTML report
        vivisect --find gunicorn    Find process by name
    """
    if hasattr(sys.stdout, "reconfigure"):
        with contextlib.suppress(Exception):
            sys.stdout.reconfigure(encoding="utf-8")

    from vivisect.attacher import NotPythonError, ProcessNotFoundError, resolve_pid
    from vivisect.collectors import collect_snapshot
    from vivisect.renderers import render

    try:
        pid = resolve_pid(target, by_name=find)
    except ProcessNotFoundError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)
    except NotPythonError as e:
        click.secho(f"Warning: {e}", fg="yellow", err=True)
        # Continue anyway — still useful for non-Python processes

    try:
        snapshot = collect_snapshot(pid, redact_env=not no_redact)
    except PermissionError:
        click.secho(
            f"Error: Permission denied for PID {pid}. Try running with elevated privileges.",
            fg="red",
            err=True,
        )
        sys.exit(1)

    render(
        snapshot,
        output_format="html" if html_path else (output_format or "rich"),
        html_path=html_path,
        show_all=show_all,
        no_color=no_color,
    )
