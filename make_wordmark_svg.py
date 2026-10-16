"""Generate wordmark.svg: extruded ASCII block letters that wipe in left to right.

Usage: python scripts/make_wordmark_svg.py
Edit TEXT to change the word. Letters supported: W I L D A N (add more in FONT).
"""

TEXT = "WILDAN"
OUT = "wordmark.svg"

FONT = {
    "W": ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10101", "10011", "10001", "10001"],
}

CELL_W = 2   # characters per lit cell
GAP = 1      # empty cells between letters
ROWS = 7
FONT_SIZE = 14
CHAR_W = FONT_SIZE * 0.6
LINE_H = 16
PAD = 20

# lit cells
lit = set()
col = 0
for ch in TEXT:
    glyph = FONT[ch]
    for r, line in enumerate(glyph):
        for c, v in enumerate(line):
            if v == "1":
                lit.add((r, col + c))
    col += 5 + GAP
total_cols = col - GAP

grid_rows = ROWS + 1
grid_cols = total_cols * CELL_W + CELL_W

front = [[" "] * grid_cols for _ in range(grid_rows)]
shadow = [[" "] * grid_cols for _ in range(grid_rows)]

for r, c in lit:
    for k in range(CELL_W):
        front[r][c * CELL_W + k] = "#"
for r, c in lit:
    for k in range(CELL_W):
        rr, cc = r + 1, c * CELL_W + k + 1
        if rr < grid_rows and cc < grid_cols and front[rr][cc] == " ":
            shadow[rr][cc] = "%"


def layer(grid, cls):
    out = []
    for i, row in enumerate(grid):
        y = PAD + FONT_SIZE + i * LINE_H
        out.append(
            f'<text class="{cls}" x="{PAD}" y="{y}" xml:space="preserve">{"".join(row)}</text>'
        )
    return "\n    ".join(out)


width = int(PAD * 2 + grid_cols * CHAR_W)
height = PAD * 2 + grid_rows * LINE_H

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <clipPath id="wipe">
      <rect x="0" y="0" width="0" height="{height}">
        <animate attributeName="width" from="0" to="{width}" dur="1.8s" begin="0.2s" fill="freeze" />
      </rect>
    </clipPath>
  </defs>
  <style>
    text {{ font-family: 'Courier New', Courier, monospace; font-size: {FONT_SIZE}px; white-space: pre; }}
    .front {{ fill: #e6edf3; }}
    .shadow {{ fill: #484f58; }}
  </style>
  <rect width="{width}" height="{height}" rx="10" fill="#0d1117" />
  <g clip-path="url(#wipe)">
    {layer(shadow, "shadow")}
    {layer(front, "front")}
  </g>
</svg>
"""

with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"Wrote {OUT} ({width}x{height})")
