import tkinter as tk
from tkinter import ttk

from src.grid import FontGrid
from src.exporter import export_line, copy_to_clipboard


def main():
    root = tk.Tk()
    root.title("5x7 Font Draw")
    root.resizable(False, False)

    style = ttk.Style()
    style.theme_use("clam")

    frame = ttk.Frame(root, padding=12)
    frame.grid(row=0, column=0, sticky="nsew")

    char_var = tk.StringVar(value="!")

    def on_char_change(*_args):
        v = char_var.get()
        if len(v) > 1:
            char_var.set(v[-1])
        update_output()

    char_var.trace_add("write", on_char_change)

    ttk.Label(frame, text="Character:").grid(row=0, column=0, sticky="w",
                                              pady=(0, 2))
    char_entry = ttk.Entry(frame, textvariable=char_var, width=4,
                           font=("Monaco", 14), justify="center")
    char_entry.grid(row=0, column=1, sticky="w", pady=(0, 2))
    char_entry.selection_range(0, tk.END)

    grid = FontGrid(frame)
    grid.grid(row=1, column=0, columnspan=2, pady=8)

    btn_frame = ttk.Frame(frame)
    btn_frame.grid(row=2, column=0, columnspan=2, pady=(0, 8))

    ttk.Button(btn_frame, text="Clear", command=grid.clear).pack(
        side=tk.LEFT, padx=(0, 8))

    output_var = tk.StringVar()

    def update_output():
        char = char_var.get() or " "
        line = export_line(grid.get_matrix(), char)
        output_var.set(line)

    def do_export():
        update_output()
        copy_to_clipboard(output_var.get())

    ttk.Button(btn_frame, text="Export to Clipboard",
               command=do_export).pack(side=tk.LEFT)

    ttk.Label(frame, text="Output:").grid(row=3, column=0, sticky="w",
                                           pady=(0, 2))

    output_entry = ttk.Entry(frame, textvariable=output_var, width=42,
                             font=("Monaco", 12), state="readonly")
    output_entry.grid(row=4, column=0, columnspan=2)

    update_output()

    root.mainloop()


if __name__ == "__main__":
    main()
