"""Batter stats from IPL ball-by-ball data.

Each delivery is a dict like:
    {"over": 3, "ball": 2, "batter": "V Kohli", "bowler": "J Bumrah",
     "runs_batter": 4, "runs_extras": 0, "runs_total": 4, "extra_type": None}
extra_type is one of None, "wides", "noballs", "byes", "legbyes".
"""


def batter_stats(deliveries, batter):
    runs = 0
    balls = 0
    fours = sixes = 0
    for d in deliveries:
        if d["batter"] != batter:
            continue
        runs += d["runs_total"]
        if d["extra_type"] != "wides":
            balls += 1
        if d["runs_batter"] == 4:
            fours += 1
        elif d["runs_batter"] == 6:
            sixes += 1
    strike_rate = round(runs * 100 / balls, 2) if balls else 0.0
    return {"runs": runs, "balls": balls, "fours": fours, "sixes": sixes, "strike_rate": strike_rate}
