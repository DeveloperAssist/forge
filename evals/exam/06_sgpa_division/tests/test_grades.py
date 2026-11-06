from grades import cgpa_to_percentage, sgpa


def test_all_o():
    assert sgpa([(4, "O"), (3, "O")]) == 10


def test_mixed():
    assert sgpa([(4, "A+"), (3, "A"), (3, "B+")]) == 8.1


def test_percentage():
    assert cgpa_to_percentage(8.1) == 73.5
