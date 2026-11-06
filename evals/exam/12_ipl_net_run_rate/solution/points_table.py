"""IPL points table.

A match record looks like:
    {"team1": "CSK", "team2": "MI",
     "team1_runs": 180, "team1_overs": "20.0", "team1_all_out": False,
     "team2_runs": 176, "team2_overs": "19.4", "team2_all_out": True,
     "winner": "CSK"}          # winner is None for a no-result
Overs use cricket notation: "19.4" means 19 overs and 4 balls.
"""


def points(matches, team):
    pts = 0
    for m in matches:
        if team not in (m["team1"], m["team2"]):
            continue
        if m["winner"] == team:
            pts += 2
        elif m["winner"] is None:
            pts += 1
    return pts


def _balls(overs: str) -> int:
    o, _, b = overs.partition(".")
    return int(o) * 6 + int(b or 0)


def net_run_rate(matches, team):
    scored = faced = conceded = bowled = 0  # runs and balls
    for m in matches:
        if m["winner"] is None:
            continue
        if m["team1"] == team:
            us, them = "team1", "team2"
        elif m["team2"] == team:
            us, them = "team2", "team1"
        else:
            continue
        scored += m[us + "_runs"]
        faced += 120 if m[us + "_all_out"] else _balls(m[us + "_overs"])
        conceded += m[them + "_runs"]
        bowled += 120 if m[them + "_all_out"] else _balls(m[them + "_overs"])
    if not faced or not bowled:
        return 0.0
    return round(scored * 6 / faced - conceded * 6 / bowled, 3)


def table(matches):
    teams = sorted({m["team1"] for m in matches} | {m["team2"] for m in matches})
    rows = [(t, points(matches, t), net_run_rate(matches, t)) for t in teams]
    return sorted(rows, key=lambda r: (-r[1], -r[2], r[0]))
