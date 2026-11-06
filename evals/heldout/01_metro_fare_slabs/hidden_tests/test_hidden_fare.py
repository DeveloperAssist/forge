import pytest

import fare


@pytest.mark.parametrize(
    "km,expected",
    [
        (0.5, 10), (2, 10), (2.01, 20), (5, 20), (5.5, 30),
        (12, 30), (12.1, 40), (21, 40), (21.5, 50), (32, 50), (32.01, 60), (80, 60),
    ],
)
def test_fare_edges(km, expected):
    assert fare.fare(km) == expected


def test_card_fare_on_edge():
    assert fare.card_fare(12) == 27
    assert fare.card_fare(2) == 9


def test_day_total_with_edges():
    assert fare.day_total([2, 5, 21]) == 10 + 20 + 40
    assert fare.day_total([32, 33], card=True) == 45 + 54


def test_zero_distance_still_rejected():
    with pytest.raises(ValueError):
        fare.fare(0)
