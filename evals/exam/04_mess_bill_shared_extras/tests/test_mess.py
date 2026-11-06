from mess import MessBill


def test_total_with_extra():
    b = MessBill("Aman")
    b.add_extra("paneer", 6000)
    assert b.total() == 356000
