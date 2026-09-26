"""HTML report renderer — generates a self-contained HTML file."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from vivisect.utils import format_bytes, format_duration

if TYPE_CHECKING:
    from vivisect.models import ProcessSnapshot


def render_html(snapshot: ProcessSnapshot, output_path: str) -> None:
    """Generate a self-contained HTML report.

    The HTML uses inline CSS (no external dependencies) and is styled
    as a dark-themed dashboard.

    Args:
        snapshot: The process snapshot data.
        output_path: Path to write the HTML file.
    """
    try:
        import jinja2
    except ImportError:
        raise ImportError(
            "HTML reports require jinja2. Install with: pip install vivisect[html]"
        ) from None

    # Load the template
    template_path = Path(__file__).parent.parent / "templates" / "report.html.j2"
    template_str = template_path.read_text(encoding="utf-8")

    env = jinja2.Environment(
        autoescape=jinja2.select_autoescape(["html"]),
        undefined=jinja2.StrictUndefined,
    )
    env.filters["format_bytes"] = format_bytes
    env.filters["format_duration"] = format_duration

    template = env.from_string(template_str)

    html = template.render(
        snapshot=snapshot,
        snapshot_json=snapshot.model_dump_json(indent=2),
    )

    Path(output_path).write_text(html, encoding="utf-8")

    # Print confirmation
    from rich.console import Console

    console = Console()
    console.print(f"[green]✓[/] HTML report saved to [bold]{output_path}[/]")
