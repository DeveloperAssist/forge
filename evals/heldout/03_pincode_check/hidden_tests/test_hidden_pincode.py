import pytest

import pincode


@pytest.mark.parametrize("pin", ["110001", "834001", " 560034 ", "999999", "400076\n"])
def test_valid(pin):
    assert pincode.is_valid_pin(pin)


@pytest.mark.parametrize(
    "pin",
    ["000000", "012345", "099999", "0834001", "83400", "8340011", "83 001", "83400a", "", "\u0968\u0966\u0966\u0966\u0966\u0967", "\u0661\u0661\u0660\u0660\u0660\u0661"],
)
def test_invalid(pin):
    assert not pincode.is_valid_pin(pin)


def test_zone_rejects_leading_zero():
    with pytest.raises(ValueError):
        pincode.zone_of("012345")
    assert pincode.zone_of("834001").startswith("Bihar")


def test_clean_addresses():
    rows = [{"name": "A", "pin": "056001"}, {"name": "B", "pin": " 560001"}, {"name": "C"}]
    assert pincode.clean_addresses(rows) == [{"name": "B", "pin": "560001"}]
