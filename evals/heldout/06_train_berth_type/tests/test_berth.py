from berth import berth_type


def test_first_seat():
    assert berth_type("SL", 1) == "LB"


def test_last_seat_of_sleeper():
    assert berth_type("SL", 72) == "SU"
