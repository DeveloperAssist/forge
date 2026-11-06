from points_table import points


def test_points():
    ms = [{"team1": "CSK", "team2": "MI", "winner": "CSK"}, {"team1": "CSK", "team2": "RR", "winner": None}]
    assert points(ms, "CSK") == 3
    assert points(ms, "MI") == 0
    assert points(ms, "RR") == 1
