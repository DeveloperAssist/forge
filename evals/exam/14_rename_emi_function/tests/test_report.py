from loan_report import report


def test_report():
    text = report("Aman", 50000000, 10.5, 36)
    assert "EMI: ₹16,251.22" in text
