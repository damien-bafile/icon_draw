# Product

<!-- impeccable:product-schema 1 -->

## Platform

desktop — native Tkinter/Python app, cross-platform (macOS/Linux/Windows). No web version planned.

## Users

Embedded/firmware developers drawing glyphs for 5x7 OLED/LCD displays (Arduino, ESP32, STM32 character-set libraries). Their job: produce correct C glyph-table bytes for a font without hand-packing bits or using error-prone converters.

## Product Purpose

Draw one 5x7 bitmap glyph on a grid and get copy-paste-ready C source: five bytes (one per column, bit 0 = top row) plus an inline comment. Success means a correct glyph reaches the user's font table in seconds, with the output trustworthy at a glance.

## Positioning

The fast path from grid to C source. The entire tool is the export: draw a glyph, and the hex bytes with comment are one click from the clipboard. No manual bit-packing, no mistakes, no friction for a one-glyph job.

## Operating Context

- The user is mid-firmware-project, tool window open beside their code editor, shaping one glyph at a time.
- Draw by clicking to toggle a cell or dragging to paint ON over the 5x7 grid; right-drag erases. Drag never destroys an already-lit cell.
- An optional "Comment:" field becomes the `/* ... */` comment in the export; `*/` and newlines are cleaned to keep the generated C valid.
- "Copy" copies `0x00,0x1c,... /* A */` to the clipboard; the output preview updates live on every grid change. Undo/Redo buttons (plus Cmd/Ctrl+Z/Y) backstop mistakes; Cmd/Ctrl+Return copies.
- Run with `just run` (`uv run python -m src.main`).

## Capabilities and Constraints

Confirmed:
- Fixed 5x7 grid (5 columns × 7 rows), 40px cells, click-toggles / drag-paints / right-drag-erases, Undo/Redo, Clear button.
- Column-major export: one byte per column, bit `row` set when a cell is lit; rendered as `0x{val:02x}`.
- Export format: `0xHH,..., /* comment */`; empty comment exports as a single space.
- Copy via the live window's clipboard (no throwaway Tk root); an all-off grid copies `0x00,0x00,0x00,0x00,0x00` and is flagged as an empty glyph.
- Catppuccin Mocha dark theme (src/theme.py) is a deliberate, binding choice.
- Desktop-only (Tkinter); no web version planned.

Undecided:
- Whether multi-glyph editing (whole font tables / character sets) is on the roadmap. Earlier git history shows multi-character experiments that were later simplified away.

## Brand Commitments

- Window title "5x7 Font Draw"; package `icon-draw`.
- Catppuccin Mocha dark palette is an explicit, binding visual constraint (commit "Add Catppuccin Mocha dark theme").

## Evidence on Hand

- The repository itself: a working Tkinter app with live-updating output.
- No user testimonials, benchmarks, or deployment evidence exist; nothing to fabricate.

## Product Principles

1. Export is the product — every interaction reduces friction between drawing a glyph and holding correct C bytes.
2. One glyph at a time, dead simple — no configuration or ceremony; the tool stays out of the way of the embedded workflow.
3. Correctness by construction — byte packing is exact and live-previewed, so the developer trusts the output.
4. Dark and calm by default — a focused palette that reads clearly beside a code editor.
5. The comment is part of the output — glyphs in font tables get meaningful names.

## Accessibility & Inclusion

- No product-specific accessibility standard was established.
- Keyboard path exists for the grid: arrows move the cell cursor, Space/Return toggles the focused cell, `C` clears, Cmd/Ctrl+Z/Y undo/redo, Cmd/Ctrl+Return copies, and all controls (grid, comment field, Undo/Redo/Clear/Copy) are reachable by Tab with visible focus rings. Grid cells still distinguish on/off by fill and outline color within a dark-on-dark palette, with no screen-reader path into the canvas.
