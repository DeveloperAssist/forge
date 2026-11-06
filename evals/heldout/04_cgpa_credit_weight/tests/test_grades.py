from grades import sgpa


def test_marksheet_example():
    assert sgpa([("O", 4), ("B", 2)]) == 8.67
