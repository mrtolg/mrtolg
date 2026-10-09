"""Count real commits per day across this account's repositories."""

import json
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "repo-activity.json"
REPOS = ("qutra-labs", "java-practice", "mrtolg")


def dates_for(repo):
    result = subprocess.run(
        [
            "gh",
            "api",
            "--paginate",
            f"repos/mrtolg/{repo}/commits?per_page=100",
            "--jq",
            ".[].commit.author.date",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"skip {repo}: {result.stderr.strip()}")
        return []
    return [line[:10] for line in result.stdout.splitlines() if len(line) >= 10]


def main():
    counts = Counter()
    for repo in REPOS:
        for day in dates_for(repo):
            counts[day] += 1
    payload = {
        "days": [{"date": day, "count": counts[day]} for day in sorted(counts)]
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"{sum(counts.values())} commits on {len(counts)} days")


if __name__ == "__main__":
    main()
