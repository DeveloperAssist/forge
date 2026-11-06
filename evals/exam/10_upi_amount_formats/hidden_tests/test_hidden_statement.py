import pytest

from statement import parse_amount, total_spent


@pytest.mark.parametrize(
    "text,paise",
    [
        ("249.00", 24900),
        ("-249.5", -24950),
        ("500", 50000),
        ("₹1,24,999.50", 12499950),
        ("Rs. 499", 49900),
        ("Rs.499", 49900),
        ("INR 75.5", 7550),
        ("-₹249", -24900),
        ("₹ 0.29", 29),
        ("1.15", 115),
        ("-Rs. 1,000", -100000),
        ("₹4.35", 435),
        ("  ₹12,34,567.89 ", 123456789),
    ],
)
def test_parse_amount(text, paise):
    got = parse_amount(text)
    assert got == paise
    assert isinstance(got, int)


def test_total_mixed_formats():
    lines = [
        "05-01-2027 | ZOMATO | -₹249",
        "06-01-2027 | From Rahul | ₹500",
        "07-01-2027 | IRCTC | -Rs. 1,145.15",
        "08-01-2027 | Chai | -INR 0.29",
    ]
    assert total_spent(lines) == 24900 + 114515 + 29
