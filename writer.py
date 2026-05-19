"""Write the generated scenery_packs.ini file."""

from __future__ import annotations

from pathlib import Path

from scanner import SceneryEntry


SCENERY_PACKS_FILENAME = "scenery_packs.ini"


def format_scenery_pack_line(entry: SceneryEntry) -> str:
    """Create one scenery_packs.ini line for a scenery entry."""

    return f"SCENERY_PACK Custom Scenery/{entry.name}/"


def build_scenery_packs_content(entries: list[SceneryEntry]) -> str:
    """Create the complete file content for scenery_packs.ini."""

    lines = [format_scenery_pack_line(entry) for entry in entries]
    return "\n".join(lines) + ("\n" if lines else "")


def write_scenery_packs_ini(
    custom_scenery_folder: Path,
    entries: list[SceneryEntry],
) -> Path:
    """Write a new scenery_packs.ini file and return its path."""

    custom_scenery_folder = Path(custom_scenery_folder)
    output_path = custom_scenery_folder / SCENERY_PACKS_FILENAME
    output_path.write_text(build_scenery_packs_content(entries), encoding="utf-8")
    return output_path
