from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .grid import FontGrid, blank_matrix
from .exporter import export_string, copy_to_clipboard


def main() -> None:
    root = tk.Tk()
    root.title("5x7 Font Draw")
    root.resizable(False, False)

    style = ttk.Style()
    style.theme_use("clam")

    frame = ttk.Frame(root, padding=12)
    frame.grid(row=0, column=0, sticky="nsew")

    # --- state ---
    string_var = tk.StringVar(value="!")
    matrices: dict[int, list[list[bool]]] = {}
    position = 0
    pos_label_var = tk.StringVar()

    # --- string entry ---
    ttk.Label(frame, text="String:").grid(row=0, column=0, sticky="w", pady=(0, 2))
    string_entry = ttk.Entry(
        frame, textvariable=string_var, width=24, font=("Monaco", 14)
    )
    string_entry.grid(row=0, column=1, sticky="w", pady=(0, 2))
    string_entry.selection_range(0, tk.END)

    # --- position nav ---
    nav_frame = ttk.Frame(frame)
    nav_frame.grid(row=1, column=0, columnspan=2, pady=(0, 4))

    def _save_current() -> None:
        matrices[position] = grid.get_matrix()

    def _clamp_position() -> None:
        nonlocal position
        text = string_var.get()
        if not text:
            position = 0
        elif position >= len(text):
            position = len(text) - 1

    def _load_position() -> None:
        nonlocal position
        text = string_var.get()
        if not text:
            grid.clear()
            pos_label_var.set("(empty)")
        else:
            if position >= len(text):
                position = len(text) - 1
            m = matrices.get(position, blank_matrix())
            grid.set_matrix(m)
            ch = text[position]
            pos_label_var.set(f"Char {position + 1}/{len(text)}: '{ch}'")

    def _refresh_nav() -> None:
        _load_position()
        _update_output()

    def go_prev() -> None:
        nonlocal position
        text = string_var.get()
        if not text:
            return
        _save_current()
        position = max(0, position - 1)
        _refresh_nav()

    def go_next() -> None:
        nonlocal position
        text = string_var.get()
        if not text:
            return
        _save_current()
        position = min(len(text) - 1, position + 1)
        _refresh_nav()

    ttk.Button(nav_frame, text="<", width=3, command=go_prev).pack(
        side=tk.LEFT, padx=(0, 6)
    )
    ttk.Label(nav_frame, textvariable=pos_label_var, font=("Monaco", 12)).pack(
        side=tk.LEFT
    )
    ttk.Button(nav_frame, text=">", width=3, command=go_next).pack(
        side=tk.LEFT, padx=(6, 0)
    )

    def on_string_change(*_args: object) -> None:
        nonlocal position
        _save_current()
        _clamp_position()
        _refresh_nav()

    string_var.trace_add("write", on_string_change)

    # --- grid ---
    grid = FontGrid(frame)
    grid.grid(row=2, column=0, columnspan=2, pady=8)

    # --- buttons ---
    btn_frame = ttk.Frame(frame)
    btn_frame.grid(row=3, column=0, columnspan=2, pady=(0, 8))

    ttk.Button(btn_frame, text="Clear Char", command=grid.clear).pack(
        side=tk.LEFT, padx=(0, 8)
    )

    # --- output ---
    output_text = tk.Text(
        frame,
        width=42,
        height=6,
        font=("Monaco", 12),
        state=tk.DISABLED,
        bg="#f5f5f5",
        relief="solid",
        borderwidth=1,
    )
    output_text.grid(row=4, column=0, columnspan=2)

    def _update_output() -> None:
        text = string_var.get()
        if not text:
            output_text.configure(state=tk.NORMAL)
            output_text.delete("1.0", tk.END)
            output_text.configure(state=tk.DISABLED)
            return
        lines = export_string(matrices, text)
        output_text.configure(state=tk.NORMAL)
        output_text.delete("1.0", tk.END)
        output_text.insert("1.0", lines)
        output_text.configure(state=tk.DISABLED)

    def do_export() -> None:
        _save_current()
        text = string_var.get()
        if text:
            copy_to_clipboard(export_string(matrices, text))

    ttk.Button(btn_frame, text="Export to Clipboard", command=do_export).pack(
        side=tk.LEFT
    )

    ttk.Label(frame, text="Output:").grid(row=4, column=0, sticky="nw", pady=(0, 2))

    # --- init ---
    _load_position()
    _update_output()

    root.mainloop()


if __name__ == "__main__":
    main()
