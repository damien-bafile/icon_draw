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


def export_line(matrix: list[list[bool]], char: str) -> str:
    hex_str = matrix_to_hex(matrix)
    return f"{hex_str}, /* {char} */"


def export_string(matrices: dict[int, list[list[bool]]], text: str) -> str:
    lines: list[str] = []
    for i, ch in enumerate(text):
        m = matrices.get(i)
        if m is None:
            m = [[False] * 5 for _ in range(7)]
        lines.append(export_line(m, ch))
    return "\n".join(lines)


def copy_to_clipboard(text: str) -> None:
    root = tk.Tk()
    root.withdraw()
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()
    root.destroy()
