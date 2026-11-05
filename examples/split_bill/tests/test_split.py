from split import split_bill, who_owes


def test_even_split():
    assert split_bill(900, 3) == [300.0, 300.0, 300.0]


def test_shares_add_up_to_the_total():
    shares = split_bill(1000, 3)
    assert round(sum(shares), 2) == 1000.0


def test_tip():
    assert sum(split_bill(1000, 4, tip_percent=10)) == 1100.0


def test_zero_people_is_an_error():
    import pytest

    with pytest.raises(ValueError):
        split_bill(500, 0)


def test_who_owes():
    assert who_owes({"Aman": 600, "Riya": 0, "Kabir": 0}, 600) == {"Aman": -400.0, "Riya": 200.0, "Kabir": 200.0}
