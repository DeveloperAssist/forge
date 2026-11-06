import pytest

import payments


@pytest.mark.parametrize("vpa", ["rahul@okaxis", "rahul.k-99@ybl", "9876543210@paytm", "priya_s@oksbi"])
def test_valid_ids(vpa):
    p = payments.create_payment(vpa, 50000, "rent")
    assert p == {"vpa": vpa, "amount_paise": 50000, "note": "rent", "status": "PENDING"}


@pytest.mark.parametrize("vpa", ["rahul.okaxis", "rahul@@ybl", "@ybl", "rahul@", "rah ul@ybl", "rahul@ok axis",
                                 "", "a@b@c"])
def test_bad_ids(vpa):
    with pytest.raises(ValueError):
        payments.create_payment(vpa, 50000)


@pytest.mark.parametrize("amount", [0, -1, -50000, 10_000_001, 50_000_000])
def test_bad_amounts(amount):
    with pytest.raises(ValueError):
        payments.create_payment("rahul@okaxis", amount)


def test_limits_inclusive():
    assert payments.create_payment("rahul@okaxis", 10_000_000)["amount_paise"] == 10_000_000
    assert payments.create_payment("rahul@okaxis", 1)["amount_paise"] == 1
