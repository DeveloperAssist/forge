from order import order_total


def test_no_coupon_small_order():
    assert order_total([("Masala Dosa", 12000, 1)]) == 12000 + 4000 + 500


def test_no_coupon_free_delivery():
    assert order_total([("Veg Biryani", 25000, 1)]) == 25000 + 500


def test_flat100():
    assert order_total([("Paneer Thali", 29900, 2)], coupon="FLAT100") == 59800 - 10000 + 500
