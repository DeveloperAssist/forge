from tickets import booking_total


def test_single_ticket_full_price():
    assert booking_total("day_pass", 1) == 25000


def test_group_of_five_gets_ten_percent():
    assert booking_total("day_pass", 5) == 112500
