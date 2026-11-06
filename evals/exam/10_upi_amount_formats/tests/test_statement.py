from statement import parse_amount, parse_line, total_spent


def test_plain():
    assert parse_amount("249.00") == 24900
    assert parse_amount("-249.5") == -24950


def test_rupee_symbol():
    assert parse_amount("₹1,24,999.50") == 12499950


def test_line():
    row = parse_line("05-01-2027 | ZOMATO | -249.00")
    assert row["desc"] == "ZOMATO" and row["paise"] == -24900


def test_total():
    assert total_spent(["05-01-2027 | ZOMATO | -249.00", "06-01-2027 | From Rahul | 500"]) == 24900
