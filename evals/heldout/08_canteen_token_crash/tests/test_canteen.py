from canteen import Order, now_serving


def test_smallest_waiting_token():
    orders = [Order(12, "maggi", 5, None), Order(11, "poha", 3, None), Order(10, "chai", 1, 4)]
    assert now_serving(orders) == 11
