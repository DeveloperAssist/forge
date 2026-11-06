import pytest

from splitter import split_by_shares, split_custom, split_equal


def test_equal():
    assert split_equal(1000, 3) == [334, 333, 333]


def test_shares():
    assert split_by_shares(1000, [2, 1, 1]) == [500, 250, 250]


def test_custom_mismatch():
    with pytest.raises(ValueError):
        split_custom(1000, [500, 400])


def test_bad_total():
    with pytest.raises(ValueError):
        split_equal(0, 2)
