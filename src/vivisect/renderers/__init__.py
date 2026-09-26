"""Renderer dispatcher."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vivisect.models import ProcessSnapshot


def render(
    snapshot: ProcessSnapshot,
    output_format: str = "rich",
    html_path: str | None = None,
    show_all: bool = False,
    no_color: bool = False,
) -> None:
    """Dispatch rendering to the appropriate backend.

    Args:
        snapshot: The collected process snapshot.
        output_format: One of "rich", "json", "html".
        html_path: File path for HTML output (required when format is "html").
        show_all: If True, don't truncate long lists.
        no_color: Disable colored output (rich only).
    """
    match output_format:
        case "json":
            from vivisect.renderers.json_export import render_json

            render_json(snapshot)
        case "html":
            from vivisect.renderers.html_report import render_html

            assert html_path is not None, "--html requires an output path"
            render_html(snapshot, html_path)
        case "rich" | _:
            from vivisect.renderers.rich_console import render_rich

            render_rich(snapshot, show_all=show_all, no_color=no_color)
