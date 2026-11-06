from batting import batter_stats


def d(batter, rb, rx=0, kind=None):
    return {"over": 1, "ball": 1, "batter": batter, "bowler": "B", "runs_batter": rb,
            "runs_extras": rx, "runs_total": rb + rx, "extra_type": kind}


def test_clean_overs():
    balls = [d("V Kohli", 4), d("V Kohli", 1), d("V Kohli", 0), d("F du Plessis", 6)]
    s = batter_stats(balls, "V Kohli")
    assert s["runs"] == 5
    assert s["balls"] == 3
    assert s["fours"] == 1
