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
        phone = r.get("phone") or "-"
        out.append(f"{r['name']} ({r['college']}) - {phone}")
    return out


def per_event(rows: list[dict]) -> dict[str, int]:
    return dict(Counter(r["event"] for r in rows))


def team_count(rows: list[dict]) -> int:
    """Number of teams; a person with no team is a team of one."""
    teams = set()
    solo = 0
    for r in rows:
        if r.get("team"):
            teams.add((r["event"], r["team"]))
        else:
            solo += 1
    return len(teams) + solo


def report(rows: list[dict]) -> str:
    lines = contact_list(rows)
    events = per_event(rows)
    header = f"{len(rows)} people, {team_count(rows)} teams, {len(events)} events"
    return "\n".join([header, *lines])


if __name__ == "__main__":
    print(report(load("export.json")))
