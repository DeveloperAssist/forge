import batting


def d(batter, rb, rx=0, kind=None):
    return {"over": 1, "ball": 1, "batter": batter, "bowler": "B", "runs_batter": rb,
            "runs_extras": rx, "runs_total": rb + rx, "extra_type": kind}


INNINGS = [
    d("V Kohli", 4),
    d("V Kohli", 0, 1, "wides"),
    d("V Kohli", 1, 1, "noballs"),
    d("V Kohli", 0, 4, "byes"),
    d("V Kohli", 6),
    d("V Kohli", 0, 1, "legbyes"),
    d("R Patidar", 6),
    d("V Kohli", 0, 5, "wides"),
]


def test_extras_not_added_to_batter():
    s = batting.batter_stats(INNINGS, "V Kohli")
    assert s == {"runs": 11, "balls": 5, "fours": 1, "sixes": 1, "strike_rate": 220.0}


def test_other_batter():
    s = batting.batter_stats(INNINGS, "R Patidar")
    assert s["runs"] == 6 and s["balls"] == 1 and s["strike_rate"] == 600.0


def test_no_balls_faced():
    s = batting.batter_stats([d("V Kohli", 0, 1, "wides")], "V Kohli")
    assert s["runs"] == 0 and s["balls"] == 0 and s["strike_rate"] == 0.0
