"""Back up the existing scenery_packs.ini file before writing changes."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil

from writer import SCENERY_PACKS_FILENAME


def backup_scenery_packs_ini(custom_scenery_folder: Path) -> Path | None:
    """Create a timestamped backup of scenery_packs.ini if it exists."""

    custom_scenery_folder = Path(custom_scenery_folder)
    source_path = custom_scenery_folder / SCENERY_PACKS_FILENAME

    if not source_path.exists():
        return None

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = custom_scenery_folder / f"{SCENERY_PACKS_FILENAME}.backup-{timestamp}"

    # Avoid overwriting a backup if the user applies more than once in the same second.
    counter = 2
    while backup_path.exists():
        backup_path = custom_scenery_folder / f"{SCENERY_PACKS_FILENAME}.backup-{timestamp}-{counter}"
        counter += 1

    shutil.copy2(source_path, backup_path)
    return backup_path
