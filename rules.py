"""Classification rules for X-Plane 12 scenery folders.

These rules are intentionally simple and beginner-friendly. They use folder
names and a few common X-Plane folder structures to make a best-effort guess.
You can adjust the keyword lists below as you learn more about your scenery.
"""

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

    if is_global_airports(name):
        return GLOBAL_AIRPORTS

    # Mesh stays near the bottom, so detect it before broader ortho rules.
    if contains_keyword(name_lower, MESH_KEYWORDS):
        return MESH

    # Overlay names can contain "Ortho4XP", so check overlays before ortho.
    if contains_keyword(name_lower, OVERLAY_KEYWORDS):
        return OVERLAYS

    if looks_like_library(name):
        return LIBRARIES

    if looks_like_airport(folder_path, name, name_lower):
        return CUSTOM_AIRPORTS

    if contains_keyword(name_lower, LANDMARK_KEYWORDS):
        return LANDMARKS_CITY

    if contains_keyword(name_lower, REGIONAL_KEYWORDS):
        return REGIONAL_ENHANCEMENTS

    if contains_keyword(name_lower, ORTHO_KEYWORDS) or ORTHO_TILE_PATTERN.search(name):
        return ORTHO_PHOTOREAL

    return UNKNOWN


def is_global_airports(name: str) -> bool:
    """Detect the default Global Airports package exactly or nearly exactly."""

    normalized = normalize_name(name)
    exact_names = {
        "globalairports",
        "xplaneglobalairports",
        "xplane12globalairports",
    }

    if normalized in exact_names:
        return True

    # Near-exact examples: "Global Airports XP12", "X-Plane Global Airports".
    words = set(re.findall(r"[a-z0-9]+", name.casefold()))
    return "global" in words and "airports" in words


def looks_like_airport(folder_path: Path, name: str, name_lower: str) -> bool:
    """Detect custom airport packages."""

    if has_airport_data(folder_path):
        return True

    if contains_keyword(name_lower, AIRPORT_KEYWORDS):
        return True

    # Many airport folders start with an ICAO code, for example "KJFK - New York".
    if ICAO_CODE_PATTERN.search(name) and not ORTHO_TILE_PATTERN.search(name):
        return True

    return False


def looks_like_library(name: str) -> bool:
    """Detect common library packages without treating every SAM-like word as a library."""

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
    """Check for the standard X-Plane airport data file."""

    apt_dat_path = folder_path / "Earth nav data" / "apt.dat"
    return apt_dat_path.is_file()


def contains_keyword(name_lower: str, keywords: list[str]) -> bool:
    """Return True if any keyword appears in a folder name."""

    return any(keyword.casefold() in name_lower for keyword in keywords)


def normalize_name(name: str) -> str:
    """Normalize a folder name for forgiving comparisons."""

    return re.sub(r"[^a-z0-9]+", "", name.casefold())
