from money import format_inr


def test_small():
    assert format_inr(500) == "₹5.00"


def test_thousands():
    assert format_inr(123456) == "₹1,234.56"


def test_lakh():
    assert format_inr(12345678) == "₹1,23,456.78"


def test_negative():
    assert format_inr(-24900) == "-₹249.00"


def test_big_amount():
    assert format_inr(98765432100) == "₹987,654,321.00"
