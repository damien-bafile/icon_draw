from __future__ import annotations

import math
import sys
import tkinter as tk
import tkinter.font as tkfont
from collections.abc import Callable
from tkinter import ttk

from . import theme
from .grid import FontGrid
from .exporter import export_line, sanitize_comment, copy_to_clipboard


def _apply_theme(root: tk.Tk) -> None:
    root.configure(bg=theme.BASE)

    style = ttk.Style()
    style.theme_use("clam")

    style.configure(".", background=theme.BASE, foreground=theme.TEXT)

    style.configure(
        "TFrame",
        background=theme.BASE,
    )
    style.configure(
        "TLabel",
        background=theme.BASE,
        foreground=theme.TEXT,
    )
    style.configure(
        "TButton",
        background=theme.SURFACE1,
        foreground=theme.TEXT,
        borderwidth=0,
        padding=(14, 4),
        focusthickness=1,
        focuscolor=theme.BLUE,
    )
    style.map(
        "TButton",
        background=[
            ("active", theme.SURFACE2),
            ("pressed", theme.SURFACE0),
            ("disabled", theme.SURFACE0),
        ],
        foreground=[
            ("active", theme.TEXT),
            ("pressed", theme.TEXT),
            ("disabled", theme.SUBTEXT0),
        ],
    )
    style.configure(
        "Accent.TButton",
        background=theme.LAVENDER,
        foreground=theme.BASE,
        borderwidth=0,
        padding=(14, 4),
        focusthickness=1,
        focuscolor=theme.BLUE,
    )
    style.map(
        "Accent.TButton",
        background=[
            ("active", theme.BLUE),
            ("pressed", theme.BLUE),
            ("disabled", theme.SURFACE0),
        ],
        foreground=[
            ("active", theme.BASE),
            ("pressed", theme.BASE),
            ("disabled", theme.SUBTEXT0),
        ],
    )
    style.configure(
        "TEntry",
        fieldbackground=theme.SURFACE0,
        foreground=theme.TEXT,
        insertcolor=theme.TEXT,
        borderwidth=0,
        padding=6,
    )
    style.map(
        "TEntry",
        fieldbackground=[
            ("readonly", theme.MANTLE),
        ],
        foreground=[
            ("readonly", theme.SUBTEXT0),
        ],
    )
    style.configure(
        "Code.TEntry",
        fieldbackground=theme.SURFACE1,
        foreground=theme.TEXT,
        insertcolor=theme.TEXT,
        borderwidth=1,
        relief="solid",
        padding=6,
    )
    style.map(
        "Code.TEntry",
        fieldbackground=[
            ("readonly", theme.SURFACE1),
        ],
        foreground=[
            ("readonly", theme.TEXT),
        ],
    )

    style.configure(
        "Header.TLabel",
        background=theme.BASE,
        foreground=theme.TEXT,
        font=(theme.mono_family(root), 11, "bold"),
    )


class _ToolTip:
    def __init__(
        self,
        widget: tk.Misc,
        text: str,
        font: tuple[str, int] | tuple[str, int, str] = ("Helvetica", 10),
        delay_ms: int = 450,
    ) -> None:
        self._widget = widget
        self._text = text
        self._font = font
        self._delay_ms = delay_ms
        self._tip: tk.Toplevel | None = None
        self._after: str | None = None
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")

    def _schedule(self, _event: tk.Event[tk.Misc]) -> None:
        self._cancel()
        self._after = self._widget.after(self._delay_ms, self._show)

    def _show(self) -> None:
        if self._tip is not None:
            return
        self._after = None
        self._tip = tk.Toplevel(self._widget)
        self._tip.wm_overrideredirect(True)
        tk.Label(
            self._tip,
            text=self._text,
            font=self._font,
            bg=theme.SURFACE1,
            fg=theme.TEXT,
            relief="solid",
            borderwidth=1,
            padx=6,
            pady=3,
        ).pack()
        self._tip.update_idletasks()
        w = self._tip.winfo_reqwidth()
        h = self._tip.winfo_reqheight()
        wx = self._widget.winfo_rootx()
        wy = self._widget.winfo_rooty()
        ww = self._widget.winfo_width()
        wh = self._widget.winfo_height()
        sw = self._widget.winfo_screenwidth()
        sh = self._widget.winfo_screenheight()
        x = min(max(wx + ww // 2 - w // 2, 0), max(sw - w, 0))
        y = wy - h - 6
        if y < 0:
            y = wy + wh + 6
        y = min(y, max(sh - h, 0))
        self._tip.wm_geometry(f"+{x}+{y}")

    def _cancel(self) -> None:
        if self._after is not None:
            self._widget.after_cancel(self._after)
            self._after = None

    def _hide(self, _event: tk.Event[tk.Misc]) -> None:
        self._cancel()
        if self._tip is not None:
            self._tip.destroy()
            self._tip = None


def main() -> None:
    root = tk.Tk()
    root.title("5x7 Font Draw")
    root.minsize(220, 300)
    root.geometry("220x300")
    root.resizable(True, True)

    _apply_theme(root)

    mono = theme.mono_family(root)

    frame = ttk.Frame(root, padding=12)
    frame.grid(row=0, column=0, sticky="nsew")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    comment_var = tk.StringVar(value="")
    output_var = tk.StringVar()
    output_font = tkfont.Font(font=(mono, 12))

    btn_frame = ttk.Frame(frame)
    btn_frame.grid(row=5, column=0, columnspan=2, pady=(10, 8))

    status_var = tk.StringVar(value="")
    status_label = ttk.Label(
        btn_frame, textvariable=status_var, foreground=theme.SUBTEXT0
    )
    _flash_after: str | None = None
    _sticky_active = False

    def flash_status(text: str, color: str, ms: int | None = 1800) -> None:
        nonlocal _flash_after, _sticky_active
        if _flash_after is not None:
            root.after_cancel(_flash_after)
            _flash_after = None
        status_var.set(text)
        status_label.configure(foreground=color)
        if ms is None:
            _sticky_active = True
        else:
            _sticky_active = False
            _flash_after = root.after(ms, lambda: status_var.set(""))

    def on_comment_change(*_args: object) -> None:
        update_output()
        raw = comment_var.get()
        if raw and raw != sanitize_comment(raw):
            flash_status("Comment cleaned for C", theme.SAPPHIRE)

    comment_var.trace_add("write", on_comment_change)

    ttk.Label(frame, text="Comment:").grid(row=0, column=0, sticky="w", pady=(0, 2))
    comment_entry = tk.Entry(
        frame,
        textvariable=comment_var,
        width=24,
        font=(mono, 14),
        bg=theme.SURFACE0,
        fg=theme.TEXT,
        insertbackground=theme.TEXT,
        selectbackground=theme.SURFACE2,
        selectforeground=theme.TEXT,
        relief=tk.FLAT,
        borderwidth=0,
        highlightthickness=1,
        highlightbackground=theme.SURFACE0,
        highlightcolor=theme.BLUE,
    )
    comment_entry.grid(row=0, column=1, sticky="w", pady=(0, 2))

    undo_btn = ttk.Button(btn_frame, text="Undo", command=lambda: grid.undo())
    redo_btn = ttk.Button(btn_frame, text="Redo", command=lambda: grid.redo())
    undo_btn.state(["disabled"])
    redo_btn.state(["disabled"])
    undo_btn.pack(side=tk.LEFT, padx=(0, 8))
    redo_btn.pack(side=tk.LEFT, padx=(0, 8))

    def _refresh_actions() -> None:
        undo_btn.state(["!disabled"] if grid.can_undo() else ["disabled"])
        redo_btn.state(["!disabled"] if grid.can_redo() else ["disabled"])

    def fit_output() -> None:
        line = output_var.get()
        px = output_font.measure(line)
        char_w = output_font.measure("0")
        desired = max(24, math.ceil(px / char_w) + 2)
        screen_chars = max(24, int((root.winfo_screenwidth() - 80) / char_w))
        output_entry.configure(width=min(desired, screen_chars))

    def refresh_grid_info() -> None:
        row, col = grid.get_cursor()
        on = grid.get_matrix()[row][col]
        lit = sum(1 for r in grid.get_matrix() for v in r if v)
        grid_info_var.set(
            f"cursor ({row},{col}) \u00b7 cell {'on' if on else 'off'} \u00b7 {lit}/35 lit"
        )

    def update_output() -> None:
        nonlocal _sticky_active
        line = export_line(grid.get_matrix(), comment_var.get())
        if output_var.get() != line and _sticky_active:
            _sticky_active = False
            status_var.set("")
        output_var.set(line)
        fit_output()
        _refresh_actions()
        refresh_grid_info()

    output_entry = ttk.Entry(
        frame,
        textvariable=output_var,
        font=(mono, 12),
        state="readonly",
        style="Code.TEntry",
    )

    grid = FontGrid(frame, on_change=update_output, on_cursor=refresh_grid_info)
    grid.grid(row=1, column=0, columnspan=2, pady=(8, 2))

    grid_info_var = tk.StringVar(value="")
    ttk.Label(
        frame,
        textvariable=grid_info_var,
        foreground=theme.SUBTEXT0,
    ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 2))

    ttk.Label(
        frame,
        text="click toggles \u00b7 drag paints \u00b7 right-drag erases",
        foreground=theme.SUBTEXT0,
    ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 2))

    mod_name = "Command" if sys.platform == "darwin" else "Control"
    mod_sym = "\u2318" if sys.platform == "darwin" else "Ctrl+"
    redo_label = "\u2318Shift+Z" if sys.platform == "darwin" else "Ctrl+Y"
    ttk.Label(
        frame,
        text=(
            "\u2190\u2192\u2191\u2193 move \u00b7 space toggles \u00b7 "
            f"c clears \u00b7 {mod_sym}Z undo \u00b7 {redo_label} redo \u00b7 "
            f"{mod_sym}Return copy"
        ),
        foreground=theme.SUBTEXT0,
    ).grid(row=4, column=0, columnspan=2, sticky="w")

    def do_clear() -> None:
        if grid.clear():
            flash_status(f"Cleared \u2014 {mod_sym}Z undoes", theme.GREEN)
        else:
            flash_status("Nothing to clear", theme.SUBTEXT0)

    clear_btn = ttk.Button(btn_frame, text="Clear", command=do_clear)
    clear_btn.pack(side=tk.LEFT, padx=(0, 8))

    def do_example() -> None:
        grid.load_example()
        flash_status(f"Loaded example \u2014 {mod_sym}Z undoes", theme.BLUE)

    example_btn = ttk.Button(btn_frame, text="Example", command=do_example)
    example_btn.pack(side=tk.LEFT, padx=(0, 8))

    def do_export() -> None:
        update_output()
        try:
            copy_to_clipboard(output_var.get(), root)
        except tk.TclError:
            flash_status(
                "Copy failed \u2014 select the C source line below and copy manually",
                theme.RED,
                ms=None,
            )
            return
        if not any(any(row) for row in grid.get_matrix()):
            flash_status(
                "Copied \u2014 empty glyph, all bytes 0x00", theme.SAPPHIRE, ms=None
            )
        else:
            flash_status("Copied to clipboard", theme.GREEN, ms=None)

    copy_btn = ttk.Button(
        btn_frame, text="Copy", style="Accent.TButton", command=do_export
    )
    copy_btn.pack(side=tk.LEFT)
    status_label.pack(side=tk.LEFT, padx=(10, 0))

    _ToolTip(undo_btn, f"Undo last change ({mod_sym}Z)", font=(mono, 10))
    _ToolTip(redo_btn, f"Redo ({redo_label})", font=(mono, 10))
    _ToolTip(clear_btn, "Clear all cells (c)", font=(mono, 10))
    _ToolTip(example_btn, "Load a sample glyph", font=(mono, 10))
    _ToolTip(copy_btn, f"Copy the C source line ({mod_sym}Return)", font=(mono, 10))

    ttk.Label(frame, text="C source:", style="Header.TLabel").grid(
        row=6, column=0, sticky="w", pady=(0, 2)
    )
    ttk.Label(
        frame,
        text="bit 0 = top row \u00b7 one byte per column \u00b7 byte 0 = left column",
        foreground=theme.SUBTEXT0,
    ).grid(row=6, column=1, sticky="w", pady=(0, 2))

    frame.columnconfigure(1, weight=1)
    output_entry.grid(row=7, column=0, columnspan=2, sticky="ew")

    root.bind(f"<{mod_name}-z>", lambda _e: grid.undo())
    root.bind(f"<{mod_name}-y>", lambda _e: grid.redo())
    root.bind(f"<{mod_name}-Shift-z>", lambda _e: grid.redo())
    root.bind(f"<{mod_name}-Return>", lambda _e: do_export())

    def _grid_key(
        handler: Callable[[], None],
    ) -> Callable[[tk.Event[tk.Misc]], str | None]:
        def _wrapper(_event: tk.Event[tk.Misc]) -> str | None:
            if isinstance(root.focus_get(), (tk.Entry, ttk.Entry, ttk.Button)):
                return None
            handler()
            return "break"

        return _wrapper

    def _move(dr: int, dc: int) -> None:
        grid.move_cursor(dr, dc)

    root.bind("<Up>", _grid_key(lambda: _move(-1, 0)))
    root.bind("<Down>", _grid_key(lambda: _move(1, 0)))
    root.bind("<Left>", _grid_key(lambda: _move(0, -1)))
    root.bind("<Right>", _grid_key(lambda: _move(0, 1)))
    root.bind("<space>", _grid_key(grid.toggle_cursor))
    root.bind("<Return>", _grid_key(grid.toggle_cursor))
    root.bind("c", _grid_key(do_clear))
    root.bind("C", _grid_key(do_clear))

    update_output()

    root.mainloop()


if __name__ == "__main__":
    main()
