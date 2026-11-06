import pytest

from payments import create_payment, upi_link


def test_valid():
    p = create_payment("rahul@okaxis", 24900, "Zomato")
    assert p["status"] == "PENDING"
    assert upi_link(p) == "upi://pay?pa=rahul@okaxis&am=249.00&tn=Zomato"


def test_missing_at():
    with pytest.raises(ValueError):
        create_payment("rahul.okaxis", 24900)
