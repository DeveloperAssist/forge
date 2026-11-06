"""Import a UPI statement exported as text lines:  DATE | DESCRIPTION | AMOUNT"""
from datetime import datetime


def parse_amount(text: str) -> int:
    """'249.00' -> 24900 paise, '-249.5' -> -24950."""
    s = text.strip().replace(",", "").replace(" ", "")
    sign = 1
    if s.startswith("-"):
        sign, s = -1, s[1:]
    for prefix in ("₹", "Rs.", "Rs", "INR"):
        if s.startswith(prefix):
            s = s[len(prefix):]
            break
    if s.startswith("-"):
        sign, s = -sign, s[1:]
    rupees, _, frac = s.partition(".")
    if not rupees.isdigit() or (frac and not frac.isdigit()) or len(frac) > 2:
        raise ValueError(f"bad amount: {text!r}")
    return sign * (int(rupees) * 100 + int(frac.ljust(2, "0") or 0))


def parse_line(line: str) -> dict:
    date_s, desc, amount_s = (part.strip() for part in line.split("|"))
    return {
        "date": datetime.strptime(date_s, "%d-%m-%Y").date(),
        "desc": desc,
        "paise": parse_amount(amount_s),
    }


def total_spent(lines) -> int:
    """Sum of debits (negative amounts) as a positive number of paise."""
    return -sum(p for p in (parse_line(line)["paise"] for line in lines) if p < 0)
