# X-Plane 12 Scenery Organizer

A simple Python + Tkinter desktop app for sorting X-Plane 12 `Custom Scenery`
folders and generating a clean `scenery_packs.ini` file.

The app scans a selected X-Plane 12 `Custom Scenery` folder, classifies scenery
packages, previews the sorted order, backs up the existing `scenery_packs.ini`,
and writes a new sorted file only after the user clicks **Apply**.

## Features

- Select an X-Plane 12 `Custom Scenery` folder.
- Scan all folders inside `Custom Scenery`.
- Classify scenery into:
  - Custom Airports
  - Global Airports
  - Landmarks / City Scenery
  - Regional Enhancements
  - Libraries
  - Ortho / Photo Scenery
  - Overlays
  - Mesh
  - Unknown
- Preview the generated order before writing files.
- Manually change a folder's category in the preview table before applying.
- Back up the existing `scenery_packs.ini` before applying changes.
- Generate lines in this format:

```text
SCENERY_PACK Custom Scenery/Folder Name/
```

Unknown folders are never deleted. They are included at the bottom of the
generated file and can be manually assigned to a category in the UI.

## Classification Logic

The classifier does not rely only on folder names. It checks folders in this
order:

1. Official fixed names:
   - `Global Airports`
   - folders starting with `X-Plane Landmarks`
2. Internal structure:
   - `library.txt`
   - `Earth nav data/apt.dat`
   - overlay folder names
   - DSF files plus `textures` or `terrain`
   - DSF files without airport data
3. Keyword fallback:
   - used only when structure checks are inconclusive

If no confident match is found, the folder is classified as `Unknown`.

## Sorting Order

The generated `scenery_packs.ini` is sorted in this priority order:

1. Custom Airports
2. Global Airports
3. Landmarks / City Scenery
4. Regional Enhancements
5. Libraries
6. Ortho / Photo Scenery
7. Overlays
8. Mesh
9. Unknown

Folders inside each category are sorted alphabetically.

## Requirements

- Python 3.8 or newer
- Tkinter

Tkinter is included with most standard Python installations.

## How to Run

From this project folder:

```bash
python3 main.py
```

Then:

1. Click **Select Custom Scenery Folder**.
2. Choose your X-Plane 12 `Custom Scenery` folder.
3. Review the preview table.
4. Select any row and use **Set Selected Category** if a category needs fixing.
5. Click **Apply** to back up the old file and write the new one.

## Project Structure

```text
.
├── main.py
├── scanner.py
├── sorter.py
├── writer.py
├── backup.py
├── rules.py
└── ui/
    ├── __init__.py
    └── tkinter_ui.py
```

## Safety Notes

- The app does not modify anything until **Apply** is clicked.
- The existing `scenery_packs.ini` is backed up before writing a new one.
- Scenery folders are not moved, edited, or deleted.
- Unknown folders are still included in the generated file.

## Customizing Rules

Classification logic is stored in `rules.py`.

You can edit the keyword lists in that file if you want to improve detection
for your own scenery collection.
