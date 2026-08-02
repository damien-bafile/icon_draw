from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from typing import Any, Optional

from . import theme

CELL_SIZE = 40
COLS = 5
ROWS = 7
MARGIN = 4
GUTTER_X = 18
GUTTER_Y = 18
MAX_HISTORY = 50

EXAMPLE_GLYPH: list[list[int]] = [
    [0, 1, 0, 1, 0],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1],
]


class FontGrid(tk.Canvas):
    def __init__(
        self,
        master: Optional[tk.Misc] = None,
        on_change: Optional[Callable[[], None]] = None,
        on_cursor: Optional[Callable[[], None]] = None,
        **kwargs: Any,
    ) -> None:
        w = GUTTER_X + COLS * CELL_SIZE + MARGIN
        h = GUTTER_Y + ROWS * CELL_SIZE + MARGIN
        super().__init__(
            master,
            width=w,
            height=h,
            highlightthickness=0,
            bg=theme.MANTLE,
            cursor="cross",
            takefocus=1,
            **kwargs,
        )

        self._on_change = on_change
        self._on_cursor = on_cursor
        self._matrix: list[list[bool]] = [[False] * COLS for _ in range(ROWS)]
        self._last_cell: Optional[tuple[int, int]] = None
        self._press_cell: Optional[tuple[int, int]] = None
        self._dragged = False
        self._history_pushed = False
        self._erase_history_pushed = False
        self._cursor: tuple[int, int] = (0, 0)
        self._focused = False
        self._undo: list[list[list[bool]]] = []
        self._redo: list[list[list[bool]]] = []
        self._index_font = (theme.mono_family(self), 8)

        self.bind("<Button-1>", self._on_press)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", self._on_release_left)
        self.bind("<Button-3>", self._on_erase_click)
        self.bind("<B3-Motion>", self._on_erase_drag)
        self.bind("<ButtonRelease-3>", self._on_release_erase)
        self.bind("<Up>", self._on_arrow(-1, 0))
        self.bind("<Down>", self._on_arrow(1, 0))
        self.bind("<Left>", self._on_arrow(0, -1))
        self.bind("<Right>", self._on_arrow(0, 1))
        self.bind("<space>", self._on_toggle_cursor)
        self.bind("<Return>", self._on_toggle_cursor)
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)

        self.draw()

    def _cell_from_xy(self, x: int, y: int) -> Optional[tuple[int, int]]:
        col = (x - GUTTER_X - MARGIN) // CELL_SIZE
        row = (y - GUTTER_Y - MARGIN) // CELL_SIZE
        if 0 <= col < COLS and 0 <= row < ROWS:
            return row, col
        return None

    def _snapshot(self) -> list[list[bool]]:
        return [row[:] for row in self._matrix]

    def _push_history(self) -> None:
        self._undo.append(self._snapshot())
        if len(self._undo) > MAX_HISTORY:
            self._undo.pop(0)
        self._redo.clear()

    def _cancel_active_press(self) -> None:
        self._press_cell = None
        self._last_cell = None
        self._dragged = False

    def _restore(self, state: list[list[bool]]) -> None:
        self._matrix = [row[:] for row in state]
        self._cancel_active_press()
        self.draw()
        self._notify()

    def undo(self) -> None:
        if not self._undo:
            return
        self._redo.append(self._snapshot())
        self._restore(self._undo.pop())

    def redo(self) -> None:
        if not self._redo:
            return
        self._undo.append(self._snapshot())
        self._restore(self._redo.pop())

    def can_undo(self) -> bool:
        return bool(self._undo)

    def can_redo(self) -> bool:
        return bool(self._redo)

    def _on_press(self, event: tk.Event[tk.Canvas]) -> None:
        self._last_cell = None
        self._dragged = False
        self._history_pushed = False
        self.focus_set()
        cell = self._cell_from_xy(event.x, event.y)
        if cell is None:
            self._press_cell = None
            return
        self._press_cell = cell
        self._cursor = cell

    def _on_drag(self, event: tk.Event[tk.Canvas]) -> None:
        if self._press_cell is None:
            return
        self._dragged = True
        if self._last_cell is None and self._press_cell is not None:
            self._last_cell = self._press_cell
            self._paint_cell(self._press_cell)
        self._paint_at(event.x, event.y)

    def _on_release_left(self, _event: tk.Event[tk.Canvas]) -> None:
        if self._press_cell is not None and not self._dragged:
            self._cursor = self._press_cell
            self._push_history()
            self._toggle_cell(self._press_cell)
        self._press_cell = None
        self._last_cell = None

    def _on_release_erase(self, _event: tk.Event[tk.Canvas]) -> None:
        self._last_cell = None

    def _paint_at(self, x: int, y: int) -> None:
        cell = self._cell_from_xy(x, y)
        if cell is None or cell == self._last_cell:
            return
        self._last_cell = cell
        self._cursor = cell
        if not self._matrix[cell[0]][cell[1]]:
            self._paint_cell(cell)

    def _paint_cell(self, cell: tuple[int, int]) -> None:
        row, col = cell
        if self._matrix[row][col]:
            return
        if not self._history_pushed:
            self._push_history()
            self._history_pushed = True
        self._matrix[row][col] = True
        self.draw()
        self._notify()

    def _on_erase_click(self, event: tk.Event[tk.Canvas]) -> None:
        self._last_cell = None
        self._erase_history_pushed = False
        self.focus_set()
        cell = self._cell_from_xy(event.x, event.y)
        if cell is None:
            return
        self._cursor = cell
        self._erase_cell(cell)

    def _on_erase_drag(self, event: tk.Event[tk.Canvas]) -> None:
        self._erase_at(event.x, event.y)

    def _erase_at(self, x: int, y: int) -> None:
        cell = self._cell_from_xy(x, y)
        if cell is None or cell == self._last_cell:
            return
        self._last_cell = cell
        self._cursor = cell
        self._erase_cell(cell)

    def _erase_cell(self, cell: tuple[int, int]) -> None:
        row, col = cell
        if not self._matrix[row][col]:
            return
        if not self._erase_history_pushed:
            self._push_history()
            self._erase_history_pushed = True
        self._matrix[row][col] = False
        self.draw()
        self._notify()

    def _toggle_cell(self, cell: tuple[int, int]) -> None:
        row, col = cell
        self._matrix[row][col] = not self._matrix[row][col]
        self.draw()
        self._notify()

    def _on_arrow(self, dr: int, dc: int) -> Callable[[tk.Event[tk.Canvas]], str]:
        def handler(_event: tk.Event[tk.Canvas]) -> str:
            self.move_cursor(dr, dc)
            return "break"

        return handler

    def move_cursor(self, dr: int, dc: int) -> None:
        row, col = self._cursor
        nr = min(max(row + dr, 0), ROWS - 1)
        nc = min(max(col + dc, 0), COLS - 1)
        if (nr, nc) != self._cursor:
            self._cursor = (nr, nc)
            self.draw()
        if self._on_cursor is not None:
            self._on_cursor()

    def _on_toggle_cursor(self, _event: tk.Event[tk.Canvas]) -> str:
        self.toggle_cursor()
        return "break"

    def toggle_cursor(self) -> None:
        self._push_history()
        self._toggle_cell(self._cursor)

    def load_example(self) -> None:
        self._push_history()
        self._matrix = [[bool(v) for v in row] for row in EXAMPLE_GLYPH]
        self._cursor = (0, 0)
        self._cancel_active_press()
        self.draw()
        self._notify()

    def _on_focus_in(self, _event: tk.Event[tk.Canvas]) -> None:
        self._focused = True
        self.draw()

    def _on_focus_out(self, _event: tk.Event[tk.Canvas]) -> None:
        self._focused = False
        self.draw()

    def clear(self) -> bool:
        self._cancel_active_press()
        if not any(any(row) for row in self._matrix):
            return False
        self._push_history()
        for row in range(ROWS):
            for col in range(COLS):
                self._matrix[row][col] = False
        self.draw()
        self._notify()
        return True

    def _notify(self) -> None:
        if self._on_change is not None:
            self._on_change()

    def get_matrix(self) -> list[list[bool]]:
        return [row[:] for row in self._matrix]

    def get_cursor(self) -> tuple[int, int]:
        return self._cursor

    def draw(self) -> None:
        self.delete("cell")
        self.delete("cursor")
        self.delete("index")
        for row in range(ROWS):
            for col in range(COLS):
                x1 = GUTTER_X + col * CELL_SIZE + MARGIN
                y1 = GUTTER_Y + row * CELL_SIZE + MARGIN
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                on = self._matrix[row][col]
                fill = theme.LAVENDER if on else theme.SURFACE0
                outline = theme.BLUE if on else theme.SURFACE2
                self.create_rectangle(
                    x1, y1, x2, y2, fill=fill, outline=outline, tags="cell", width=1
                )
        for col in range(COLS):
            cx = GUTTER_X + col * CELL_SIZE + CELL_SIZE // 2
            self.create_text(
                cx,
                GUTTER_Y // 2,
                text=str(col),
                fill=theme.SUBTEXT0,
                font=self._index_font,
                tags="index",
            )
        for row in range(ROWS):
            cy = GUTTER_Y + row * CELL_SIZE + CELL_SIZE // 2
            self.create_text(
                GUTTER_X // 2,
                cy,
                text=str(row),
                fill=theme.SUBTEXT0,
                font=self._index_font,
                tags="index",
            )
        crow, ccol = self._cursor
        cx1 = GUTTER_X + ccol * CELL_SIZE + MARGIN
        cy1 = GUTTER_Y + crow * CELL_SIZE + MARGIN
        cursor_outline = theme.TEXT if self._focused else theme.SUBTEXT0
        cursor_width = 2 if self._focused else 1
        self.create_rectangle(
            cx1,
            cy1,
            cx1 + CELL_SIZE,
            cy1 + CELL_SIZE,
            outline=cursor_outline,
            width=cursor_width,
            tags="cursor",
        )
