from pathlib import Path

import emi
import loan_report

ROOT = Path(__file__).resolve().parent.parent


def ref(p, rate, n):
    r = rate / 12 / 100
    if r == 0:
        return round(p / n)
    f = (1 + r) ** n
    return round(p * r * f / (f - 1))


def test_new_name_works():
    for p, rate, n in [(50000000, 10.5, 36), (1200000, 0, 12), (8999900, 14, 9), (250000000, 8.65, 240)]:
        assert emi.monthly_emi(p, rate, n) == ref(p, rate, n)
        assert emi.total_interest(p, rate, n) == ref(p, rate, n) * n - p


def test_old_name_gone():
    assert not hasattr(emi, "calc_emi")
    for path in [ROOT / "emi.py", ROOT / "loan_report.py", *sorted((ROOT / "tests").glob("*.py"))]:
        assert "calc_emi" not in path.read_text(encoding="utf-8"), path.name


def test_report_still_works():
    text = loan_report.report("Aman", 50000000, 10.5, 36)
    assert "EMI: ₹16,251.22" in text
    assert "Total interest:" in text
