import pytest

import splitter


def test_example_from_task():
    assert splitter.split_equal(1000, ["A", "B", "C"]) == {"A": 334, "B": 333, "C": 333}


@pytest.mark.parametrize("total,n", [(1000, 3), (99999, 7), (5, 8), (60000, 4), (1, 1), (0, 3), (123457, 6)])
def test_sum_and_fairness(total, n):
    names = [f"p{i}" for i in range(n)]
    shares = splitter.split_equal(total, names)
    assert list(shares) == names
    assert sum(shares.values()) == total
    assert max(shares.values()) - min(shares.values()) <= 1
    assert all(isinstance(v, int) for v in shares.values())
    # leftovers go to the earliest people
    values = list(shares.values())
    assert values == sorted(values, reverse=True)


def test_order_follows_names():
    shares = splitter.split_equal(1001, ["Zoya", "Aman"])
    assert list(shares.items()) == [("Zoya", 501), ("Aman", 500)]


@pytest.mark.parametrize("total,names", [(100, []), (100, ["A", "B", "A"]), (-5, ["A"])])
def test_bad_input(total, names):
    with pytest.raises(ValueError):
        splitter.split_equal(total, names)
