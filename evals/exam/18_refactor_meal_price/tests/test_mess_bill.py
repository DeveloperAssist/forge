import pytest

from mess_bill import guest_bill, student_bill

WEEK = [("breakfast", "Mon"), ("lunch", "Mon"), ("dinner", "Sun"), ("snacks", "Sat")]


def test_student():
    assert student_bill(WEEK) == 3000 + 6000 + 8500 + 2000


def test_guest():
    assert guest_bill(WEEK) == 4500 + 9000 + 12750 + 3000


def test_unknown():
    with pytest.raises(ValueError):
        student_bill([("brunch", "Sun")])
