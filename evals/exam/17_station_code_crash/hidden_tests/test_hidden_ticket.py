import pytest

from stations import station_name
from ticket import route_line, ticket_card


def test_lowercase_and_spaces():
    assert ticket_card("4521873690", "rnc", "NDLS", "12-01-2027") == (
        "PNR 4521873690\nRANCHI -> NEW DELHI\nDate: 12-01-2027")
    assert route_line(" ndls", "Hwh ") == "NEW DELHI -> HOWRAH"
    assert station_name(" pnbe ") == "Patna"
    assert station_name("BCT") == "Mumbai Central"


def test_unknown_code_is_value_error():
    with pytest.raises(ValueError, match="XYZ"):
        route_line("NDLS", "XYZ")
    with pytest.raises(ValueError, match="QQQ"):
        ticket_card("1", "QQQ", "NDLS", "x")
    with pytest.raises(ValueError):
        station_name("ABCD")
