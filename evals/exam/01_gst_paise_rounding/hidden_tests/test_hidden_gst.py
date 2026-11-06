import pytest

import gst


@pytest.mark.parametrize(
    "amount,rate,expected",
    [
        (10000, 18, 1800),
        (1999, 18, 360),   # 359.82
        (1050, 5, 53),     # 52.5 -> half up
        (2450, 5, 123),    # 122.5 -> half up (banker's rounding would give 122)
        (2550, 5, 128),    # 127.5
        (1000, 12, 120),
        (1, 5, 0),         # 0.05
        (10, 5, 1),        # 0.5 -> 1
        (333, 28, 93),     # 93.24
        (0, 18, 0),
    ],
)
def test_gst_amount(amount, rate, expected):
    assert gst.gst_amount(amount, rate) == expected
    assert isinstance(gst.gst_amount(amount, rate), int)


def test_bill_total():
    assert gst.bill_total([(1999, 18), (1050, 5)]) == 1999 + 360 + 1050 + 53
