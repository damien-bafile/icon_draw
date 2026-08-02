from __future__ import annotations

import tkinter as tk

from .grid import COLS, ROWS


def matrix_to_hex(matrix: list[list[bool]]) -> str:
    bytes_out: list[str] = []
    for col in range(COLS):
        val = 0
        for row in range(ROWS):
            if matrix[row][col]:
                val |= 1 << row
        bytes_out.append(f"0x{val:02x}")
    return ",".join(bytes_out)


def sanitize_comment(comment: str) -> str:
    comment = comment.replace("*/", "* /").replace("\n", " ").replace("\r", " ")
    return comment.strip()


def export_line(matrix: list[list[bool]], comment: str) -> str:
    hex_str = matrix_to_hex(matrix)
    comment = sanitize_comment(comment)
    if not comment:
        return hex_str
    return f"{hex_str}, /* {comment} */"


def copy_to_clipboard(text: str, root: tk.Misc) -> None:
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()
