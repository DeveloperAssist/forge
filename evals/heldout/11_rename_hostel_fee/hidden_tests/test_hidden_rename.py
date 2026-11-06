import re
from pathlib import Path

import pytest

import defaulters
import fees
import receipt

ROOT = Path(__file__).resolve().parent.parent


def test_new_name_with_keyword():
    assert fees.hostel_fee("double", months=6) == (4500 + 3200) * 6 + 5000
    assert fees.hostel_fee("triple", months=12, ac=True, mess=False) == (3500 + 1500) * 11 + 5000
    assert fees.hostel_fee(room_type="single", months=1) == 6000 + 3200 + 5000


def test_validation_kept():
    with pytest.raises(ValueError):
        fees.hostel_fee("double", months=0)
    with pytest.raises(ValueError):
        fees.hostel_fee("suite", months=3)


def test_old_name_gone():
    assert not hasattr(fees, "calc")
    for name in ("fees.py", "receipt.py", "defaulters.py", "tests/test_fees.py"):
        text = (ROOT / name).read_text(encoding="utf-8")
        assert not re.search(r"\bcalc\b", text), name


def test_callers_still_work():
    text = receipt.make_receipt("Asha", "double", 6)
    assert "Rs 51,200" in text
    students = [
        {"name": "Asha", "room": "double", "months": 6, "paid": 46200},
        {"name": "Ravi", "room": "single", "months": 10, "ac": True, "paid": 0},
        {"name": "Om", "room": "triple", "months": 2, "paid": 99999},
    ]
    assert defaulters.defaulters(students) == [("Ravi", 101300), ("Asha", 5000)]
