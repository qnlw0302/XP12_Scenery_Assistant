"""Simple Tkinter UI for the X-Plane 12 scenery organizer."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from backup import backup_scenery_packs_ini
from rules import CATEGORY_ORDER
from scanner import SceneryEntry, scan_custom_scenery
from sorter import sort_entries
from writer import format_scenery_pack_line, write_scenery_packs_ini


class SceneryOrganizerApp:
    """Small desktop app for previewing and writing scenery_packs.ini."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("X-Plane 12 Scenery Organizer")
        self.root.geometry("950x600")
        self.root.minsize(750, 450)

        self.custom_scenery_folder: Path | None = None
        self.sorted_entries: list[SceneryEntry] = []

        self.folder_var = tk.StringVar(value="No folder selected")
        self.status_var = tk.StringVar(value="Select your X-Plane 12 Custom Scenery folder.")
        self.manual_category_var = tk.StringVar(value=CATEGORY_ORDER[0])

        self._build_ui()

    def _build_ui(self) -> None:
        main_frame = ttk.Frame(self.root, padding=12)
        main_frame.pack(fill=tk.BOTH, expand=True)

        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X)

        select_button = ttk.Button(
            top_frame,
            text="Select Custom Scenery Folder",
            command=self.select_folder,
        )
        select_button.pack(side=tk.LEFT)

        rescan_button = ttk.Button(
            top_frame,
            text="Rescan",
            command=self.scan_and_preview,
        )
        rescan_button.pack(side=tk.LEFT, padx=(8, 0))

        self.apply_button = ttk.Button(
            top_frame,
            text="Apply",
            command=self.apply_changes,
            state=tk.DISABLED,
        )
        self.apply_button.pack(side=tk.RIGHT)

        folder_label = ttk.Label(
            main_frame,
            textvariable=self.folder_var,
            wraplength=900,
        )
        folder_label.pack(fill=tk.X, pady=(10, 8))

        manual_frame = ttk.Frame(main_frame)
        manual_frame.pack(fill=tk.X, pady=(0, 8))

        manual_label = ttk.Label(manual_frame, text="Selected folder category:")
        manual_label.pack(side=tk.LEFT)

        self.manual_category_combo = ttk.Combobox(
            manual_frame,
            textvariable=self.manual_category_var,
            values=CATEGORY_ORDER,
            state="readonly",
            width=28,
        )
        self.manual_category_combo.pack(side=tk.LEFT, padx=(8, 0))

        set_category_button = ttk.Button(
            manual_frame,
            text="Set Selected Category",
            command=self.set_selected_category,
        )
        set_category_button.pack(side=tk.LEFT, padx=(8, 0))

        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("priority", "category", "folder", "line")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=20,
        )

        self.tree.heading("priority", text="Priority")
        self.tree.heading("category", text="Category")
        self.tree.heading("folder", text="Folder")
        self.tree.heading("line", text="Generated Line")

        self.tree.column("priority", width=70, anchor=tk.CENTER, stretch=False)
        self.tree.column("category", width=210, stretch=False)
        self.tree.column("folder", width=240)
        self.tree.column("line", width=420)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_selection_changed)

        y_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        x_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scrollbar.grid(row=0, column=1, sticky="ns")
        x_scrollbar.grid(row=1, column=0, sticky="ew")

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        status_label = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            anchor=tk.W,
        )
        status_label.pack(fill=tk.X, pady=(8, 0))

    def select_folder(self) -> None:
        selected_folder = filedialog.askdirectory(
            title="Select X-Plane 12 Custom Scenery Folder"
        )

        if not selected_folder:
            return

        self.custom_scenery_folder = Path(selected_folder)
        self.folder_var.set(str(self.custom_scenery_folder))
        self.scan_and_preview()

    def scan_and_preview(self) -> None:
        if self.custom_scenery_folder is None:
            messagebox.showinfo(
                "No folder selected",
                "Please select your X-Plane 12 Custom Scenery folder first.",
            )
            return

        try:
            entries = scan_custom_scenery(self.custom_scenery_folder)
            self.sorted_entries = sort_entries(entries)
            self._populate_preview(self.sorted_entries)

            if self.sorted_entries:
                self.apply_button.configure(state=tk.NORMAL)
                self.status_var.set(f"Found {len(self.sorted_entries)} scenery folders. Review the preview, then click Apply.")
            else:
                self.apply_button.configure(state=tk.DISABLED)
                self.status_var.set("No scenery folders found in the selected folder.")

        except Exception as exc:
            self.sorted_entries = []
            self.apply_button.configure(state=tk.DISABLED)
            self._clear_preview()
            messagebox.showerror("Scan failed", str(exc))
            self.status_var.set("Scan failed.")

    def set_selected_category(self) -> None:
        selected_index = self._get_selected_entry_index()

        if selected_index is None:
            messagebox.showinfo(
                "No folder selected",
                "Select a folder in the preview table before setting its category.",
            )
            return

        selected_category = self.manual_category_var.get()

        if selected_category not in CATEGORY_ORDER:
            messagebox.showerror("Invalid category", "Please choose a valid category.")
            return

        old_entry = self.sorted_entries[selected_index]
        updated_entries = list(self.sorted_entries)
        updated_entries[selected_index] = replace(old_entry, category=selected_category)
        self.sorted_entries = sort_entries(updated_entries)
        self._populate_preview(self.sorted_entries)
        self._select_entry_by_path(old_entry.path)
        self.status_var.set(f"Updated {old_entry.name} to {selected_category}.")

    def apply_changes(self) -> None:
        if self.custom_scenery_folder is None or not self.sorted_entries:
            messagebox.showinfo(
                "Nothing to apply",
                "Select a Custom Scenery folder and scan it before applying.",
            )
            return

        confirm = messagebox.askyesno(
            "Apply changes",
            "This will back up the existing scenery_packs.ini and write a new sorted file. Continue?",
        )

        if not confirm:
            return

        try:
            backup_path = backup_scenery_packs_ini(self.custom_scenery_folder)
            output_path = write_scenery_packs_ini(
                self.custom_scenery_folder,
                self.sorted_entries,
            )

            if backup_path is None:
                message = f"Created {output_path}\n\nNo existing scenery_packs.ini was found, so no backup was needed."
            else:
                message = f"Created {output_path}\n\nBackup saved as:\n{backup_path}"

            messagebox.showinfo("Success", message)
            self.status_var.set("scenery_packs.ini was written successfully.")

        except Exception as exc:
            messagebox.showerror("Apply failed", str(exc))
            self.status_var.set("Apply failed.")

    def _populate_preview(self, entries: list[SceneryEntry]) -> None:
        self._clear_preview()

        for index, entry in enumerate(entries):
            self.tree.insert(
                "",
                tk.END,
                iid=str(index),
                values=(
                    index + 1,
                    entry.category,
                    entry.name,
                    format_scenery_pack_line(entry),
                ),
            )

    def _clear_preview(self) -> None:
        for row_id in self.tree.get_children():
            self.tree.delete(row_id)

    def on_tree_selection_changed(self, _event: tk.Event | None = None) -> None:
        selected_index = self._get_selected_entry_index()

        if selected_index is None:
            return

        self.manual_category_var.set(self.sorted_entries[selected_index].category)

    def _get_selected_entry_index(self) -> int | None:
        selected_rows = self.tree.selection()

        if not selected_rows:
            return None

        try:
            selected_index = int(selected_rows[0])
        except ValueError:
            return None

        if selected_index < 0 or selected_index >= len(self.sorted_entries):
            return None

        return selected_index

    def _select_entry_by_path(self, path: Path) -> None:
        for index, entry in enumerate(self.sorted_entries):
            if entry.path == path:
                row_id = str(index)
                self.tree.selection_set(row_id)
                self.tree.focus(row_id)
                self.tree.see(row_id)
                self.manual_category_var.set(entry.category)
                return


def run_app() -> None:
    root = tk.Tk()
    app = SceneryOrganizerApp(root)
    root.mainloop()
