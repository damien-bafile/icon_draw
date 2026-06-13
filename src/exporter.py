import tkinter as tk


def matrix_to_hex(matrix):
    bytes_out = []
    for col in range(5):
        val = 0
        for row in range(7):
            if matrix[row][col]:
                val |= (1 << row)
        bytes_out.append(f"0x{val:02x}")
    return ",".join(bytes_out)


def export_line(matrix, char):
    hex_str = matrix_to_hex(matrix)
    return f"{hex_str}, /* {char} */"


def copy_to_clipboard(text):
    root = tk.Tk()
    root.withdraw()
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()
    root.destroy()
