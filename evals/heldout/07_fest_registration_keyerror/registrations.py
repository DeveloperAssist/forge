"""Registration report for the college fest (sample entries only)."""
import json
from collections import Counter


def load(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def contact_list(rows: list[dict]) -> list[str]:
    """One line per person: 'Name (College) - phone'."""
    out = []
    for r in rows:
        out.append(f"{r['name']} ({r['college']}) - {r['phone']}")
    return out


def per_event(rows: list[dict]) -> dict[str, int]:
    return dict(Counter(r["event"] for r in rows))


def team_count(rows: list[dict]) -> int:
    """Number of teams; a person with no team is a team of one."""
    teams = set()
    for r in rows:
        teams.add((r["event"], r["team"]))
    return len(teams)


def report(rows: list[dict]) -> str:
    lines = contact_list(rows)
    events = per_event(rows)
    header = f"{len(rows)} people, {team_count(rows)} teams, {len(events)} events"
    return "\n".join([header, *lines])


if __name__ == "__main__":
    print(report(load("export.json")))
