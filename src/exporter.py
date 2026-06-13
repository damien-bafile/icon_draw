from __future__ import annotations

import tkinter as tk


def matrix_to_hex(matrix: list[list[bool]]) -> str:
    bytes_out: list[str] = []
    for col in range(5):
        val = 0
        for row in range(7):
            if matrix[row][col]:
                val |= 1 << row
        bytes_out.append(f"0x{val:02x}")
    return ",".join(bytes_out)


def export_line(matrix: list[list[bool]], comment: str) -> str:
    hex_str = matrix_to_hex(matrix)
    return f"{hex_str}, /* {comment} */"


def copy_to_clipboard(text: str) -> None:
    root = tk.Tk()
    root.withdraw()
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()
    root.destroy()
