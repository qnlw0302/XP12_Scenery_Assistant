from __future__ import annotations

from pathlib import Path
import re


CUSTOM_AIRPORTS = "Custom Airports"
GLOBAL_AIRPORTS = "Global Airports"
LANDMARKS_CITY = "Landmarks / City Scenery"
REGIONAL_ENHANCEMENTS = "Regional Enhancements"
LIBRARIES = "Libraries"
ORTHO_PHOTOREAL = "Ortho / Photo Scenery"
OVERLAYS = "Overlays"
MESH = "Mesh"
UNKNOWN = "Unknown"


CATEGORY_ORDER = [
    CUSTOM_AIRPORTS,
    GLOBAL_AIRPORTS,
    LANDMARKS_CITY,
    REGIONAL_ENHANCEMENTS,
    LIBRARIES,
    ORTHO_PHOTOREAL,
    OVERLAYS,
    MESH,
    UNKNOWN,
]

CATEGORY_PRIORITY = {
    category: index
    for index, category in enumerate(CATEGORY_ORDER, start=1)
}


REGIONAL_KEYWORDS = [
    "simheaven",
    "x-world",
    "xworld",
    "x-europe",
    "xeurope",
    "x-america",
    "xamerica",
    "x-asia",
    "xasia",
    "x-africa",
    "xafrica",
    "regional",
    "region",
    "osm",
    "w2xp",
    "autogen",
    "forests",
    "forest",
]

LANDMARK_KEYWORDS = [
    "landmark",
    "landmarks",
    "city",
    "cities",
    "skyline",
    "downtown",
    "monument",
    "monuments",
]

LIBRARY_KEYWORDS = [
    "library",
    "lib",
    "MisterX",
    "OpenSceneryX",
    "SAM",
    "RA_Library",
    "CDB-Library",
    "The_Handy_Objects_Library",
    "BS2001",
    "JB_Library",
    "NAPS",
    "R2_Library",
    "ruscenery",
    "ff_library",
    "world-models",
]

OVERLAY_KEYWORDS = [
    "overlay",
    "overlays",
    "yortho4xp_overlays",
    "yortho4xp overlays",
    "roads",
    "xroads",
]

ORTHO_KEYWORDS = [
    "ortho",
    "orthophoto",
    "ortho4xp",
    "zortho4xp",
    "photoreal",
    "photo scenery",
    "photoscenery",
    "zonephoto",
]

MESH_KEYWORDS = [
    "mesh",
    "hd mesh",
    "uhd mesh",
    "hd global scenery",
    "uhd global scenery",
    "zzz_hd_global_scenery",
    "zzz_uhd_global_scenery",
    "alpilotx",
]

AIRPORT_KEYWORDS = [
    "airport",
    "airports",
    "airfield",
    "aerodrome",
    "international",
    "intl",
]

ORTHO_TILE_PATTERN = re.compile(r"[+-]\d{2}[+-]\d{3}")
ICAO_CODE_PATTERN = re.compile(r"\b[A-Z]{4}\b")


def classify_folder(folder_path: Path) -> str:
    """Classify one scenery folder into a priority category."""

    name = folder_path.name
    name_lower = name.casefold()

    # 1. Official fixed names. These are intentionally strict.
    if is_global_airports_folder(name):
        return GLOBAL_AIRPORTS

    if is_xplane_landmarks_folder(name):
        return LANDMARKS_CITY

    # 2. Internal structure. These checks are preferred over naming guesses.
    if has_library_txt(folder_path):
        return LIBRARIES

    if has_apt_dat(folder_path):
        return CUSTOM_AIRPORTS

    # Overlay packages do not have one universal file marker, so the overlay
    # name check is kept here before DSF-only folders fall through to mesh.
    if "overlay" in name_lower:
        return OVERLAYS

    has_dsf = has_dsf_files(folder_path)
    has_ortho_assets = has_folder(folder_path, "textures") or has_folder(folder_path, "terrain")

    if has_dsf and has_ortho_assets:
        return ORTHO_PHOTOREAL

    if has_dsf:
        return MESH

    # 3. Keyword fallback. This is only used after structure checks fail.
    if looks_like_airport_name(name, name_lower):
        return CUSTOM_AIRPORTS

    if contains_keyword(name_lower, LANDMARK_KEYWORDS):
        return LANDMARKS_CITY

    if contains_keyword(name_lower, REGIONAL_KEYWORDS):
        return REGIONAL_ENHANCEMENTS

    if looks_like_library_name(name):
        return LIBRARIES

    if contains_keyword(name_lower, ORTHO_KEYWORDS) or ORTHO_TILE_PATTERN.search(name):
        return ORTHO_PHOTOREAL

    if contains_keyword(name_lower, OVERLAY_KEYWORDS):
        return OVERLAYS

    if contains_keyword(name_lower, MESH_KEYWORDS):
        return MESH

    return UNKNOWN


def is_global_airports_folder(name: str) -> bool:
    """Return True only for the official Global Airports folder name."""

    return name == "Global Airports"


def is_xplane_landmarks_folder(name: str) -> bool:
    """Return True for official X-Plane landmark packages."""

    return name.startswith("X-Plane Landmarks")


def has_file(folder: Path, relative_path: str | Path) -> bool:
    """Return True if a file exists at folder/relative_path."""

    return (folder / relative_path).is_file()


def has_library_txt(folder: Path) -> bool:
    """Return True when the package exposes X-Plane library objects."""

    return has_file(folder, "library.txt")


def has_apt_dat(folder: Path) -> bool:
    """Return True when the package contains airport data."""

    return has_file(folder, Path("Earth nav data") / "apt.dat")


def has_dsf_files(folder: Path) -> bool:
    """Return True if Earth nav data contains one or more .dsf scenery files."""

    earth_nav_data = folder / "Earth nav data"

    if not earth_nav_data.is_dir():
        return False

    try:
        for item in earth_nav_data.rglob("*"):
            if item.is_file() and item.suffix.casefold() == ".dsf":
                return True
    except OSError:
        return False

    return False


def has_folder(folder: Path, folder_name: str) -> bool:
    """Return True if the package has a direct child folder with this name."""

    try:
        for item in folder.iterdir():
            if item.is_dir() and item.name.casefold() == folder_name.casefold():
                return True
    except OSError:
        return False

    return False


def looks_like_airport_name(name: str, name_lower: str) -> bool:
    """Use folder-name hints as a fallback for custom airport packages."""

    if contains_keyword(name_lower, AIRPORT_KEYWORDS):
        return True

    # Many airport folders start with an ICAO code, for example "KJFK - New York".
    if ICAO_CODE_PATTERN.search(name) and not ORTHO_TILE_PATTERN.search(name):
        return True

    return False


def looks_like_library_name(name: str) -> bool:
    """Detect common library names without treating every SAM-like word as a library."""

    name_lower = name.casefold()
    words = set(re.findall(r"[a-z0-9]+", name_lower))
    normalized_name = normalize_name(name)

    if "library" in words or "lib" in words:
        return True

    for keyword in LIBRARY_KEYWORDS:
        keyword_lower = keyword.casefold()
        normalized_keyword = normalize_name(keyword)

        # Short names such as SAM and NAPS should match as words or exact names.
        if len(normalized_keyword) <= 4:
            if keyword_lower in words or normalized_name == normalized_keyword:
                return True
            continue

        if keyword_lower in name_lower or normalized_keyword in normalized_name:
            return True

    return False


def has_airport_data(folder_path: Path) -> bool:
    """Backward-compatible alias for the newer has_apt_dat helper."""

    return has_apt_dat(folder_path)


def contains_keyword(name_lower: str, keywords: list[str]) -> bool:
    """Return True if any keyword appears in a folder name."""

    return any(keyword.casefold() in name_lower for keyword in keywords)


def normalize_name(name: str) -> str:
    """Normalize a folder name for forgiving comparisons."""

    return re.sub(r"[^a-z0-9]+", "", name.casefold())
