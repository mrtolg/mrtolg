"""Monochrome wordmark that types itself once. No photo, no looping glow."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "wordmark.svg"

FONT = {
    "M": ["10001", "11011", "10101", "10001", "10001", "10001", "10001"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
}

WIDTH = 640
HEIGHT = 400
CELL = 16
STEP = 20
LETTER_GAP = 24
TOP = 118


def layout():
    rows = [[] for _ in range(7)]
    x = 0
    for char in "MERT":
        glyph = FONT[char]
        for col in range(5):
            for row in range(7):
                if glyph[row][col] == "1":
                    rows[row].append(x + col * STEP)
        x += 5 * STEP + LETTER_GAP
    span = x - LETTER_GAP
    origin = (WIDTH - span) // 2
    return origin, span, rows


def render():
    static = os.environ.get("STATIC") == "1"
    origin, span, rows = layout()
    travel = f"{span}px"
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img">',
        "<title>Mert Olgun</title>",
        "<style>",
        "  text { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }",
        "  .prompt { fill:#8b949e; font-size:16px; }",
        "  .sub { fill:#8b949e; font-size:18px; }",
    ]
    if not static:
        parts.extend(
            [
                "  .row { transform-box:view-box; transform-origin:left center; animation:type 0.55s steps(16,end) both; }",
                "  .fade { opacity:0; animation:fade 0.4s ease-out both; }",
                "  .cur { opacity:0; animation:ride 0.55s linear both; }",
                "  @keyframes type { from { transform: scaleX(0); } to { transform: scaleX(1); } }",
                "  @keyframes fade { from { opacity:0; } to { opacity:1; } }",
                f"  @keyframes ride {{ 0% {{ opacity:1; transform: translateX(0); }} 88% {{ opacity:1; }} 100% {{ opacity:0; transform: translateX({travel}); }} }}",
                "  @media (prefers-reduced-motion: reduce) {",
                "    .row,.fade { animation:none !important; opacity:1 !important; transform:none !important; }",
                "    .cur { opacity:0 !important; }",
                "  }",
            ]
        )
    parts.extend(
        [
            "</style>",
            f'<rect width="{WIDTH}" height="{HEIGHT}" rx="16" fill="#0d1117" stroke="#30363d"/>',
            '<circle cx="28" cy="28" r="6" fill="#f85149"/>',
            '<circle cx="48" cy="28" r="6" fill="#d29922"/>',
            '<circle cx="68" cy="28" r="6" fill="#3fb950"/>',
            '<text class="prompt" x="92" y="34">mert@york : ~/whoami</text>',
        ]
    )
    for index, xs in enumerate(rows):
        delay = 0.15 + index * 0.12
        y = TOP + index * STEP
        attrs = "" if static else f' class="row" style="animation-delay:{delay:.2f}s"'
        parts.append(f"<g{attrs}>")
        for x in xs:
            parts.append(
                f'<rect x="{origin + x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="#d0d7de"/>'
            )
        parts.append("</g>")
        if not static:
            parts.append(
                f'<rect class="cur" x="{origin - 2}" y="{y}" width="8" height="{CELL}" rx="1" fill="#7ee787" '
                f'style="animation-delay:{delay:.2f}s"/>'
            )
    sub_class = "sub" if static else "sub fade"
    sub_style = "" if static else ' style="animation-delay:1.05s"'
    parts.append(
        f'<text class="{sub_class}"{sub_style} x="320" y="320" text-anchor="middle">Olgun  ·  University of York</text>'
    )
    parts.append("</svg>")
    return "".join(parts)


def main():
    svg = render()
    OUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT.name}")


if __name__ == "__main__":
    main()
