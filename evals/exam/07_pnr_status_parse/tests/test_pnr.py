from pnr import is_confirmed, parse_status


def test_cnf():
    assert parse_status("CNF/B2/45") == {"status": "CNF", "coach": "B2", "seat": 45, "berth": None, "position": None}


def test_wl():
    assert parse_status("WL 12")["position"] == 12


def test_cnf_with_berth():
    assert parse_status("CNF/S4/33/UB")["berth"] == "UB"


def test_is_confirmed():
    assert is_confirmed("CNF/B2/45")
    assert not is_confirmed("RAC 23")
