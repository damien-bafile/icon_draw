from __future__ import annotations

import tkinter as tk
from typing import Any, Optional

CELL_SIZE = 40
COLS = 5
ROWS = 7
MARGIN = 4

FILL_OFF = "#ffffff"
FILL_ON = "#1a1a2e"
OUTLINE_OFF = "#cccccc"
OUTLINE_ON = "#333355"

BLANK_ROW: list[bool] = [False] * COLS


def blank_matrix() -> list[list[bool]]:
    return [BLANK_ROW[:] for _ in range(ROWS)]


class FontGrid(tk.Canvas):
    def __init__(self, master: Optional[tk.Misc] = None, **kwargs: Any) -> None:
        w = COLS * CELL_SIZE + MARGIN * 2
        h = ROWS * CELL_SIZE + MARGIN * 2
        super().__init__(
            master,
            width=w,
            height=h,
            highlightthickness=0,
            bg="#e8e8e8",
            cursor="cross",
            **kwargs,
        )

        self._matrix: list[list[bool]] = blank_matrix()
        self._last_cell: Optional[tuple[int, int]] = None

        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", self._on_release)

        self.draw()

    def _cell_from_xy(self, x: int, y: int) -> Optional[tuple[int, int]]:
        col = (x - MARGIN) // CELL_SIZE
        row = (y - MARGIN) // CELL_SIZE
        if 0 <= col < COLS and 0 <= row < ROWS:
            return row, col
        return None

    def _on_click(self, event: tk.Event[tk.Canvas]) -> None:
        self._last_cell = None
        self._toggle_at(event.x, event.y)

    def _on_drag(self, event: tk.Event[tk.Canvas]) -> None:
        self._toggle_at(event.x, event.y)

    def _on_release(self, event: tk.Event[tk.Canvas]) -> None:
        self._last_cell = None

    def _toggle_at(self, x: int, y: int) -> None:
        cell = self._cell_from_xy(x, y)
        if cell is None or cell == self._last_cell:
            return
        self._last_cell = cell
        row, col = cell
        self._matrix[row][col] = not self._matrix[row][col]
        self.draw()

    def clear(self) -> None:
        self._matrix = blank_matrix()
        self.draw()

    def get_matrix(self) -> list[list[bool]]:
        return [row[:] for row in self._matrix]

    def set_matrix(self, matrix: list[list[bool]]) -> None:
        self._matrix = [row[:] for row in matrix]
        self.draw()

    def draw(self) -> None:
        self.delete("cell")
        for row in range(ROWS):
            for col in range(COLS):
                x1 = col * CELL_SIZE + MARGIN
                y1 = row * CELL_SIZE + MARGIN
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                on = self._matrix[row][col]
                fill = FILL_ON if on else FILL_OFF
                outline = OUTLINE_ON if on else OUTLINE_OFF
                self.create_rectangle(
                    x1, y1, x2, y2, fill=fill, outline=outline, tags="cell", width=1
                )
