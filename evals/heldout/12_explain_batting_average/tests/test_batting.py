from batting import Innings, batting_average, highest


def test_average_all_out():
    innings = [Innings(40, 30), Innings(20, 25)]
    assert batting_average(innings) == 30.0


def test_average_with_not_out():
    innings = [Innings(50, 40), Innings(30, 20, out=False)]
    assert batting_average(innings) == 40.0


def test_highest_not_out():
    assert highest([Innings(30, 20, out=False), Innings(12, 10)]) == "30*"
