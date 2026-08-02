import tkinter as tk
import tkinter.font as tkfont

# Catppuccin Mocha <https://github.com/catppuccin>

BASE = "#1e1e2e"
MANTLE = "#181825"
CRUST = "#11111b"

SURFACE0 = "#313244"
SURFACE1 = "#45475a"
SURFACE2 = "#585b70"

OVERLAY0 = "#6c7086"
OVERLAY1 = "#7f849c"
OVERLAY2 = "#9399b2"

SUBTEXT0 = "#a6adc8"
SUBTEXT1 = "#bac2de"
TEXT = "#cdd6f4"

LAVENDER = "#b4befe"
BLUE = "#89b4fa"
SAPPHIRE = "#74c7ec"
GREEN = "#a6e3a1"
RED = "#f38ba8"

MONO_FAMILIES = (
    "Monaco",
    "Menlo",
    "Consolas",
    "Courier New",
    "DejaVu Sans Mono",
    "Liberation Mono",
    "Courier",
)


def mono_family(root: tk.Misc) -> str:
    available = set(tkfont.families(root))
    for fam in MONO_FAMILIES:
        if fam in available:
            return fam
    return "Courier"
