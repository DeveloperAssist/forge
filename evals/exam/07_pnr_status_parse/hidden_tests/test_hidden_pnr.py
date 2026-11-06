import pytest

from pnr import is_confirmed, parse_status


def wl(n):
    return {"status": "WL", "coach": None, "seat": None, "berth": None, "position": n}


def rac(n):
    return {"status": "RAC", "coach": None, "seat": None, "berth": None, "position": n}


@pytest.mark.parametrize(
    "text,expected",
    [
        ("CNF/B2/45", {"status": "CNF", "coach": "B2", "seat": 45, "berth": None, "position": None}),
        ("CNF/S4/33/UB", {"status": "CNF", "coach": "S4", "seat": 33, "berth": "UB", "position": None}),
        (" cnf/b2/45/lb ", {"status": "CNF", "coach": "B2", "seat": 45, "berth": "LB", "position": None}),
        ("RAC 23", rac(23)),
        ("RAC/23", rac(23)),
        ("rac 7", rac(7)),
        ("WL 12", wl(12)),
        ("wl 12", wl(12)),
        ("WL/3", wl(3)),
        ("GNWL/24", wl(24)),
        ("PQWL 5", wl(5)),
        ("rlwl/7", wl(7)),
        ("  GNWL 110  ", wl(110)),
    ],
)
def test_formats(text, expected):
    assert parse_status(text) == expected


@pytest.mark.parametrize("text", ["XYZ 4", "", "CONFIRMED"])
def test_garbage_raises(text):
    with pytest.raises(ValueError):
        parse_status(text)


def test_is_confirmed_variants():
    assert is_confirmed("cnf/s4/33/ub")
    assert not is_confirmed("GNWL/24")
