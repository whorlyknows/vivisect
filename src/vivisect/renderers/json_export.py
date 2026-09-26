"""JSON export renderer."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vivisect.models import ProcessSnapshot


def render_json(snapshot: ProcessSnapshot) -> None:
    """Print the snapshot as formatted JSON to stdout."""
    sys.stdout.write(snapshot.model_dump_json(indent=2))
    sys.stdout.write("\n")
