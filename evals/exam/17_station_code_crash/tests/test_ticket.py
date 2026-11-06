from ticket import route_line, ticket_card


def test_route():
    assert route_line("NDLS", "HWH") == "NEW DELHI -> HOWRAH"


def test_card():
    assert ticket_card("4521873690", "RNC", "NDLS", "12-01-2027").splitlines()[1] == "RANCHI -> NEW DELHI"
