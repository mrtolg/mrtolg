"""Name card. One line, typed once, then it stays still."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "wordmark.svg"

WIDTH = 640
HEIGHT = 400


def render():
    static = os.environ.get("STATIC") == "1"
    name_class = "name" if static else "name wipe"
    sub_class = "sub" if static else "sub fade"
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img">',
        "<title>Mert Olgun</title>",
        "<style>",
        "  text { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }",
        "  .prompt { fill:#8b949e; font-size:16px; }",
        "  .name { fill:#e6edf3; font-size:40px; }",
        "  .sub { fill:#8b949e; font-size:16px; }",
    ]
    if not static:
        parts.extend(
            [
                "  .wipe { animation:wipe 0.9s steps(12,end) both; }",
                "  .fade { opacity:0; animation:fade 0.4s ease-out 0.95s both; }",
                "  @keyframes wipe { from { clip-path: inset(0 100% 0 0); } to { clip-path: inset(0 0 0 0); } }",
                "  @keyframes fade { from { opacity:0; } to { opacity:1; } }",
                "  @media (prefers-reduced-motion: reduce) {",
                "    .wipe,.fade { animation:none !important; opacity:1 !important; clip-path:none !important; }",
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
            f'<text class="{name_class}" x="320" y="200" text-anchor="middle">Mert Olgun</text>',
            f'<text class="{sub_class}" x="320" y="242" text-anchor="middle">University of York</text>',
            "</svg>",
        ]
    )
    return "".join(parts)


def main():
    svg = render()
    OUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT.name}")


if __name__ == "__main__":
    main()
