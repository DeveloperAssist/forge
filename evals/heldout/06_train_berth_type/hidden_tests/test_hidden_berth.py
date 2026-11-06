import pytest

import berth


@pytest.mark.parametrize("coach,seat", [("SL", 0), ("SL", -3), ("SL", 73), ("3A", 0), ("3A", 73), ("2A", 0), ("2A", 49)])
def test_out_of_range(coach, seat):
    with pytest.raises(ValueError):
        berth.berth_type(coach, seat)


@pytest.mark.parametrize(
    "coach,seat,expected",
    [("SL", 72, "SU"), ("3A", 72, "SU"), ("3A", 71, "SL"), ("2A", 48, "SU"), ("2A", 47, "SL"), ("2A", 1, "LB"), ("SL", 11, "UB")],
)
def test_edges(coach, seat, expected):
    assert berth.berth_type(coach, seat) == expected


def test_lower_berths_include_last_bay():
    assert berth.lower_berths("SL", [1, 2, 70, 71, 72]) == [1, 71]


def test_unknown_class():
    with pytest.raises(ValueError):
        berth.berth_type("1A", 1)
