import canteen
from canteen import Order


def test_empty_morning_board():
    assert canteen.now_serving([]) is None
    assert canteen.avg_wait([]) == 0.0
    text = canteen.board_text([])
    assert "Now serving: -" in text
    assert "Waiting: 0" in text


def test_all_waiting_no_ready_yet():
    orders = [Order(1, "chai", 0, None), Order(2, "samosa", 1, None)]
    assert canteen.avg_wait(orders) == 0.0
    assert "Now serving: 1" in canteen.board_text(orders)


def test_all_ready_nothing_waiting():
    orders = [Order(1, "chai", 0, 4), Order(2, "samosa", 1, 8)]
    assert canteen.now_serving(orders) is None
    assert canteen.avg_wait(orders) == 5.5
    text = canteen.board_text(orders)
    assert "Now serving: -" in text
    assert "Avg wait: 5.5 min" in text
