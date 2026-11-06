import batting
from batting import Innings


def test_not_out_runs_count_but_not_as_dismissal():
    innings = [Innings(50, 40), Innings(30, 20, out=False)]
    assert batting.batting_average(innings) == 80.0


def test_never_out_has_no_average():
    assert batting.batting_average([Innings(12, 9, out=False), Innings(7, 4, out=False)]) is None


def test_mixed_season():
    innings = [Innings(10, 12), Innings(0, 3), Innings(45, 30, out=False), Innings(25, 20)]
    assert batting.batting_average(innings) == 26.67


def test_other_stats_unchanged():
    innings = [Innings(50, 40), Innings(30, 20, out=False)]
    assert batting.strike_rate(innings) == 133.33
    assert batting.highest(innings) == "50"
