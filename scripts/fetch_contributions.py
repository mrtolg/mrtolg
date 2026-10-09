"""Fetch the public contribution calendar. No token, no GraphQL."""

import json
import re
from datetime import date, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USER = "mrtolg"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "contributions.json"

COUNT_RE = re.compile(r"^(\d+)\s+contributions?\b", re.IGNORECASE)
TOTAL_RE = re.compile(r"([\d,]+)\s+contributions?\b", re.IGNORECASE)


def count_from_tooltip(text):
    cleaned = " ".join(text.split())
    if cleaned.lower().startswith("no contribution"):
        return 0
    match = COUNT_RE.match(cleaned)
    if match:
        return int(match.group(1))
    return 0


def sunday_on_or_before(day):
    return day - timedelta(days=(day.weekday() + 1) % 7)


def parse_contributions(html):
    soup = BeautifulSoup(html, "html.parser")
    tips = {}
    for tip in soup.find_all("tool-tip"):
        target = tip.get("for")
        if target:
            tips[target] = tip.get_text(" ", strip=True)

    by_date = {}
    for cell in soup.select("td.ContributionCalendar-day"):
        raw = cell.get("data-date")
        if not raw:
            continue
        level = int(cell.get("data-level") or 0)
        count = count_from_tooltip(tips.get(cell.get("id"), ""))
        if count == 0 and level > 0:
            count = 1
        by_date[date.fromisoformat(raw)] = {
            "date": raw,
            "count": count,
            "level": max(0, min(level, 4)),
        }

    if not by_date:
        raise ValueError("contribution calendar had no day cells")

    ordered = [by_date[key] for key in sorted(by_date)]
    start = sunday_on_or_before(date.fromisoformat(ordered[0]["date"]))
    end = sunday_on_or_before(date.fromisoformat(ordered[-1]["date"]))
    weeks = []
    cursor = start
    while cursor <= end:
        week = []
        for offset in range(7):
            day = cursor + timedelta(days=offset)
            week.append(by_date.get(day))
        weeks.append(week)
        cursor += timedelta(days=7)

    total_match = None
    heading = soup.select_one("h2")
    if heading:
        total_match = TOTAL_RE.search(heading.get_text(" ", strip=True))
    heading_total = int(total_match.group(1).replace(",", "")) if total_match else None
    counted = sum(day["count"] for day in ordered)

    return {
        "user": USER,
        "total": counted,
        "heading_total": heading_total,
        "days": ordered,
        "weeks": [
            [cell["date"] if cell else None for cell in week] for week in weeks
        ],
        "current_streak": current_streak(ordered),
        "longest_streak": longest_streak(ordered),
    }


def longest_streak(days):
    best = run = 0
    for day in days:
        if day["count"] > 0:
            run += 1
            best = max(best, run)
        else:
            run = 0
    return best


def current_streak(days):
    """Count back from the latest day. An empty today does not break the run."""
    if not days:
        return 0
    index = len(days) - 1
    if days[index]["count"] == 0 and index > 0:
        index -= 1
    run = 0
    while index >= 0 and days[index]["count"] > 0:
        run += 1
        index -= 1
    return run


def main():
    response = requests.get(
        f"https://github.com/users/{USER}/contributions",
        headers={"User-Agent": "mrtolg-profile-readme"},
        timeout=30,
    )
    response.raise_for_status()
    payload = parse_contributions(response.text)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"{payload['total']} contributions across {len(payload['days'])} days")


if __name__ == "__main__":
    main()
