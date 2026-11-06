import ast
import inspect
from pathlib import Path

import pytest

import mess_bill

WEEK = [("breakfast", "Mon"), ("lunch", "Mon"), ("dinner", "Sun"), ("snacks", "Sat"), ("dinner", "Tue"),
        ("lunch", "Sun")]


def test_bills_unchanged():
    assert mess_bill.student_bill(WEEK) == 3000 + 6000 + 8500 + 2000 + 6000 + 6000
    assert mess_bill.guest_bill(WEEK) == 4500 + 9000 + 12750 + 3000 + 9000 + 9000
    assert mess_bill.student_bill([]) == 0
    assert mess_bill.guest_bill([("snacks", "Mon")]) == 3000


def test_unknown_meal_both():
    for fn in (mess_bill.student_bill, mess_bill.guest_bill):
        with pytest.raises(ValueError, match="unknown meal: brunch"):
            fn([("lunch", "Mon"), ("brunch", "Sun")])


def test_meal_price():
    mp = mess_bill.meal_price
    assert list(inspect.signature(mp).parameters) == ["meal", "day", "guest"]
    assert inspect.signature(mp).parameters["guest"].default is False
    assert mp("dinner", "Sun") == 8500
    assert mp("dinner", "Sun", guest=True) == 12750
    assert mp("dinner", "Mon") == 6000
    assert mp("breakfast", "Sun", True) == 4500
    with pytest.raises(ValueError):
        mp("brunch", "Mon")


def _func(tree, name):
    return next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)


def test_no_duplication():
    tree = ast.parse(Path(mess_bill.__file__).read_text(encoding="utf-8"))
    for name in ("student_bill", "guest_bill"):
        fn = _func(tree, name)
        names = {n.id for n in ast.walk(fn) if isinstance(n, ast.Name)}
        assert "meal_price" in names, name
        assert not names & {"PRICES", "SUNDAY_SPECIAL_EXTRA", "GUEST_MARKUP_PERCENT"}, name
