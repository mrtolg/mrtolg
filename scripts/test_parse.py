"""Parser checks. Run: py -3 scripts/test_parse.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fetch_contributions import current_streak, longest_streak, parse_contributions

FIXTURE = """
<div class="js-yearly-contributions">
  <h2>3 contributions in the last year</h2>
  <table>
    <tbody>
      <tr>
        <td class="ContributionCalendar-day" data-date="2026-10-04" data-level="0" id="d0"></td>
        <tool-tip for="d0">No contributions on October 4th.</tool-tip>
        <td class="ContributionCalendar-day" data-date="2026-10-05" data-level="2" id="d1"></td>
        <tool-tip for="d1">1 contribution on October 5th.</tool-tip>
        <td class="ContributionCalendar-day" data-date="2026-10-06" data-level="3" id="d2"></td>
        <tool-tip for="d2">2 contributions on October 6th.</tool-tip>
      </tr>
    </tbody>
  </table>
</div>
"""


def main():
    payload = parse_contributions(FIXTURE)
    assert payload["total"] == 3, payload["total"]
    assert payload["heading_total"] == 3
    assert payload["days"][0]["count"] == 0
    assert payload["days"][1]["count"] == 1
    assert payload["days"][2]["level"] == 3
    assert longest_streak(payload["days"]) == 2
    assert current_streak(payload["days"]) == 2
    assert current_streak(
        [
            {"count": 1},
            {"count": 1},
            {"count": 0},
        ]
    ) == 2
    # 2026-10-04 is a Sunday, so the three days share one column.
    assert len(payload["weeks"]) == 1
    assert payload["weeks"][0][0] == "2026-10-04"
    print("ok")


if __name__ == "__main__":
    main()
