"""Loan EMI maths. Money in paise."""


def monthly_emi(principal: int, annual_rate_percent: float, months: int) -> int:
    """Monthly EMI in paise (reducing balance), rounded to the nearest paisa."""
    r = annual_rate_percent / 12 / 100
    if r == 0:
        return round(principal / months)
    f = (1 + r) ** months
    return round(principal * r * f / (f - 1))


def total_interest(principal: int, annual_rate_percent: float, months: int) -> int:
    return monthly_emi(principal, annual_rate_percent, months) * months - principal
