"""Scan the X-Plane Custom Scenery folder."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from rules import classify_folder


@dataclass(frozen=True)
class SceneryEntry:
    """One scenery folder found inside Custom Scenery."""

    name: str
    path: Path
    category: str


def scan_custom_scenery(custom_scenery_folder: Path) -> list[SceneryEntry]:
    """Return all scenery folders found inside the selected Custom Scenery folder."""

    custom_scenery_folder = Path(custom_scenery_folder).expanduser()

    if not custom_scenery_folder.exists():
        raise FileNotFoundError(f"Folder does not exist: {custom_scenery_folder}")

    if not custom_scenery_folder.is_dir():
        raise NotADirectoryError(f"Not a folder: {custom_scenery_folder}")

    entries: list[SceneryEntry] = []

    for item in sorted(custom_scenery_folder.iterdir(), key=lambda path: path.name.casefold()):
        if not item.is_dir():
            continue

        category = classify_folder(item)
        entries.append(
            SceneryEntry(
                name=item.name,
                path=item,
                category=category,
            )
        )

    return entries
