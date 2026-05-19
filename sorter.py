"""Sort scenery entries into X-Plane-friendly priority order."""

from __future__ import annotations

from scanner import SceneryEntry
from rules import CATEGORY_PRIORITY, UNKNOWN


def sort_entries(entries: list[SceneryEntry]) -> list[SceneryEntry]:
    """Sort entries by category priority, then alphabetically inside each category."""

    unknown_priority = CATEGORY_PRIORITY[UNKNOWN]

    return sorted(
        entries,
        key=lambda entry: (
            CATEGORY_PRIORITY.get(entry.category, unknown_priority),
            entry.name.casefold(),
        ),
    )
