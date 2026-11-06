import ast
from pathlib import Path

import pytest

import splitter

SRC = Path(splitter.__file__).read_text(encoding="utf-8")


def test_behaviour():
    assert splitter.split_equal(1000, 3) == [334, 333, 333]
    assert splitter.split_equal(7, 7) == [1] * 7
    assert splitter.split_by_shares(1000, [2, 1, 1]) == [500, 250, 250]
    assert splitter.split_by_shares(100, [1, 1, 1]) == [34, 33, 33]
    assert splitter.split_custom(1000, [600, 400]) == [600, 400]


@pytest.mark.parametrize("fn,arg", [(splitter.split_equal, 2), (splitter.split_by_shares, [1, 1]),
                                    (splitter.split_custom, [0])])
def test_same_errors(fn, arg):
    with pytest.raises(ValueError, match=r"^amount must be positive$"):
        fn(0, arg)
    with pytest.raises(ValueError, match=r"^amount must be positive$"):
        fn(-5, arg)
    with pytest.raises(TypeError, match=r"^amount must be in paise \(int\)$"):
        fn(10.5, arg)


def test_other_errors_kept():
    with pytest.raises(ValueError, match="need at least one person"):
        splitter.split_equal(100, 0)
    with pytest.raises(ValueError, match="shares must be positive"):
        splitter.split_by_shares(100, [1, 0])
    with pytest.raises(ValueError, match="amounts add up to 900, not 1000"):
        splitter.split_custom(1000, [500, 400])


def test_check_amount():
    splitter.check_amount(1)
    with pytest.raises(ValueError, match=r"^amount must be positive$"):
        splitter.check_amount(0)
    with pytest.raises(TypeError, match=r"^amount must be in paise \(int\)$"):
        splitter.check_amount("100")


def test_no_duplication():
    assert SRC.count("amount must be positive") == 1
    assert SRC.count("amount must be in paise (int)") == 1
    tree = ast.parse(SRC)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name.startswith("split_"):
            calls = {n.func.id for n in ast.walk(node) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
            assert "check_amount" in calls, node.name
