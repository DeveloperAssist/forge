import hashlib
from pathlib import Path

import money

EXPECTED_SHA256 = "16ff4273021551644b1b5b835f301bb767d7e03b06643db2b0e2de184704f307"


def test_source_unchanged():
    text = (Path(__file__).resolve().parent.parent / "money.py").read_bytes().decode("utf-8")
    text = text.replace("\r\n", "\n")
    assert hashlib.sha256(text.encode("utf-8")).hexdigest() == EXPECTED_SHA256


def test_still_indian_grouping():
    assert money.format_inr(98765432100) == "₹98,76,54,321.00"
    assert money.format_inr(1000000000) == "₹1,00,00,000.00"
    assert money.format_inr(12345678) == "₹1,23,456.78"
