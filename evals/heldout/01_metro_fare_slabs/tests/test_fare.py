from fare import fare


def test_short_ride():
    assert fare(1.5) == 10


def test_five_km_is_twenty():
    assert fare(5) == 20
