import pytest

import order

BIRYANI = ("Chicken Biryani", 34900, 1)
THALI = ("Paneer Thali", 29900, 1)
CHAI = ("Cutting Chai", 1500, 1)


def test_default_unchanged():
    assert order.order_total([BIRYANI]) == 34900 + 500
    assert order.order_total([CHAI]) == 1500 + 4000 + 500
    assert order.order_total([BIRYANI], coupon=None) == 34900 + 500


def test_flat100_exact_threshold():
    assert order.order_total([("Combo", 49900, 1)], coupon="FLAT100") == 49900 - 10000 + 500


def test_flat100_below_threshold():
    with pytest.raises(ValueError):
        order.order_total([BIRYANI], coupon="FLAT100")


def test_save20():
    assert order.order_total([("Pizza", 30000, 1)], coupon="SAVE20") == 30000 - 6000 + 500


def test_save20_cap():
    assert order.order_total([BIRYANI, THALI], coupon="SAVE20") == 64800 - 12000 + 500


def test_save20_rounds_down_and_keeps_delivery_fee():
    # 20% of 14999 = 2999.8 -> 2999
    assert order.order_total([("Momos", 14999, 1)], coupon="SAVE20") == 14999 - 2999 + 4000 + 500


def test_case_insensitive():
    assert order.order_total([("Pizza", 30000, 1)], coupon="save20") == 30000 - 6000 + 500
    assert order.order_total([("Combo", 60000, 1)], coupon="Flat100") == 60000 - 10000 + 500


def test_unknown_code():
    with pytest.raises(ValueError):
        order.order_total([BIRYANI], coupon="FREEFOOD")
