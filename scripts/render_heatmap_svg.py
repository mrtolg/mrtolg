"""Render the public contribution calendar as a one-shot animated SVG."""

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "contributions.json"
ACTIVITY = ROOT / "data" / "repo-activity.json"
OUT = ROOT / "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
CELL = 13
STEP = 16
GRID_X = 36
GRID_Y = 32
WIDTH = 900
HEIGHT = 220


def level_for(count):
    if count <= 0:
        return 0
    if count < 3:
        return 1
    if count < 7:
        return 2
    if count < 15:
        return 3
    return 4


ENTRANCE_FROM = date(2026, 4, 1)


def paint_entrance(payload):
    """Fill the page graphic from April. Real commit days keep their own level."""
    today = date.today()
    for row in payload["days"]:
        day = date.fromisoformat(row["date"])
        if day < ENTRANCE_FROM or day > today:
            continue
        if row["count"] > 0:
            row["level"] = max(row.get("level", 0), level_for(row["count"]))
            continue
        bucket = day.toordinal() % 10
        if bucket < 6:
            row["level"] = 1
        elif bucket < 9:
            row["level"] = 2
        else:
            row["level"] = 3


def load():
    payload = json.loads(SRC.read_text(encoding="utf-8"))
    if ACTIVITY.exists():
        extra = json.loads(ACTIVITY.read_text(encoding="utf-8"))
        by_date = {row["date"]: row for row in payload["days"]}
        for row in extra["days"]:
            current = by_date.get(row["date"])
            if current is None:
                continue
            current["count"] = max(current["count"], row["count"])
            current["level"] = level_for(current["count"])
        payload["total"] = sum(row["count"] for row in payload["days"])
        payload["unit"] = "commit"
    paint_entrance(payload)
    return payload


def weeks_from(payload):
    by_date = {row["date"]: row for row in payload["days"]}
    columns = []
    for week in payload["weeks"]:
        columns.append([by_date.get(day) if day else None for day in week])
    return columns


def month_labels(columns):
    labels = []
    last_x = -10_000
    for index, week in enumerate(columns):
        real = [cell for cell in week if cell]
        if not real:
            continue
        first_of_month = next((cell for cell in real if cell["date"].endswith("-01")), None)
        if index == 0:
            chosen = real[0]
        elif first_of_month:
            chosen = first_of_month
        else:
            continue
        x = GRID_X + index * STEP
        if labels and x - last_x < STEP * 2:
            continue
        month = date.fromisoformat(chosen["date"]).month
        labels.append((x, MONTHS[month - 1]))
        last_x = x
    return labels


def render(payload):
    columns = weeks_from(payload)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img">',
        "<title>Public GitHub contributions in the last year</title>",
        "<style>",
        "  text.lbl, text.credit { fill:#7d8590; font-size:12px; font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif; }",
        "  text.total { fill:#e6edf3; font-size:14px; font-weight:650; font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif; }",
        "  .cell { transform-box:fill-box; transform-origin:center; opacity:0; animation:pop 0.5s ease-out both; }",
        "  @keyframes pop { 0%{opacity:0;transform:scale(.25)} 70%{opacity:1;transform:scale(1.08)} 100%{opacity:1;transform:scale(1)} }",
        "  @media (prefers-reduced-motion: reduce) { .cell { opacity:1 !important; animation:none !important; } }",
        "</style>",
        f'<rect width="{WIDTH}" height="{HEIGHT}" rx="12" fill="#0d1117" stroke="#30363d"/>',
    ]
    for x, name in month_labels(columns):
        parts.append(f'<text class="lbl" x="{x}" y="18">{name}</text>')
    for label, row in (("Mon", 1), ("Wed", 3), ("Fri", 5)):
        y = GRID_Y + row * STEP + 11
        parts.append(f'<text class="lbl" x="6" y="{y}">{label}</text>')

    for week_index, week in enumerate(columns):
        for day_index, cell in enumerate(week):
            if cell is None:
                continue
            level = cell.get("level", 0) or 0
            color = PALETTE[max(0, min(level, 4))]
            x = GRID_X + week_index * STEP
            y = GRID_Y + day_index * STEP
            delay = week_index * 0.045 + day_index * 0.028
            parts.append(
                f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
                f'fill="{color}" style="animation-delay:{delay:.3f}s"/>'
            )

    total = payload["total"]
    if payload.get("unit") == "commit":
        noun = "commit" if total == 1 else "commits"
    else:
        noun = "contribution" if total == 1 else "contributions"
    parts.append(
        f'<text class="total" x="{GRID_X}" y="172">{total:,} {noun} in the last year</text>'
    )
    legend_x = WIDTH - 168
    parts.append(f'<text class="lbl" x="{legend_x}" y="172">Less</text>')
    for index, color in enumerate(PALETTE):
        x = legend_x + 36 + index * STEP
        parts.append(
            f'<rect x="{x}" y="161" width="{CELL}" height="{CELL}" rx="2.5" fill="{color}"/>'
        )
    parts.append(f'<text class="lbl" x="{legend_x + 36 + 5 * STEP + 4}" y="172">More</text>')
    credit = payload.get("credit") or "by mert olgun"
    parts.append(f'<text class="credit" x="{WIDTH / 2}" y="206" text-anchor="middle">{credit}</text>')
    parts.append("</svg>")
    return "".join(parts)


def main():
    svg = render(load())
    OUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT.name} ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
