"""Neofetch-style identity card. Story, not contribution counts."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "info-card.svg"

WIDTH = 640
HEIGHT = 400
ROWS = [
    ("now", "Year 2 of 3"),
    ("degree", "BSc CS with AI"),
    ("school", "University of York"),
    ("seeking", "Summer 2027 internship"),
    ("focus", "Explain it, then test it"),
]


def render():
    static = os.environ.get("STATIC") == "1"
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img">',
        "<title>Year 2, BSc Computer Science with AI, University of York. Seeking a summer 2027 internship.</title>",
        "<style>",
        "  text { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }",
        "  .prompt { fill:#8b949e; font-size:16px; }",
        "  .key { fill:#7ee787; font-size:22px; }",
        "  .val { fill:#e6edf3; font-size:22px; }",
    ]
    if not static:
        parts.extend(
            [
                "  .line { opacity:0; animation:slide 0.45s ease-out both; }",
                "  @keyframes slide { from { opacity:0; transform: translateY(8px); } to { opacity:1; transform: translateY(0); } }",
                "  @media (prefers-reduced-motion: reduce) { .line { opacity:1 !important; animation:none !important; transform:none !important; } }",
            ]
        )
    parts.extend(
        [
            "</style>",
            f'<rect width="{WIDTH}" height="{HEIGHT}" rx="16" fill="#0d1117" stroke="#30363d"/>',
            '<circle cx="28" cy="28" r="6" fill="#f85149"/>',
            '<circle cx="48" cy="28" r="6" fill="#d29922"/>',
            '<circle cx="68" cy="28" r="6" fill="#3fb950"/>',
            '<text class="prompt" x="92" y="34">mert@york : ~/profile</text>',
        ]
    )
    for index, (key, value) in enumerate(ROWS):
        y = 118 + index * 48
        delay = 0.2 + index * 0.12
        attrs = "" if static else f' class="line" style="animation-delay:{delay:.2f}s"'
        parts.append(f"<g{attrs}>")
        parts.append(f'<text class="key" x="48" y="{y}">{key}</text>')
        parts.append(f'<text class="val" x="220" y="{y}">{value}</text>')
        parts.append("</g>")
    parts.append("</svg>")
    return "".join(parts)


def main():
    svg = render()
    OUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT.name}")


if __name__ == "__main__":
    main()
