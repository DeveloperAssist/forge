import pytest

import tickets


@pytest.mark.parametrize(
    "count,percent",
    [(1, 0), (3, 0), (4, 10), (5, 10), (7, 10), (9, 10), (10, 20), (11, 20), (25, 20)],
)
def test_discount_percent(count, percent):
    assert tickets.discount_percent(count) == percent


@pytest.mark.parametrize(
    "kind,count,expected",
    [
        ("pro_show", 3, 120000),
        ("pro_show", 6, 216000),
        ("combo", 12, 528000),
        ("day_pass", 10, 200000),
    ],
)
def test_booking_total(kind, count, expected):
    assert tickets.booking_total(kind, count) == expected


def test_rounds_down_to_paise():
    tickets.TICKET_PRICE["odd"] = 10001
    try:
        # 4 x 100.01 = 400.04 -> 10% = 40.004 -> 4000 paise discount
        assert tickets.booking_total("odd", 4) == 40004 - 4000
    finally:
        del tickets.TICKET_PRICE["odd"]
