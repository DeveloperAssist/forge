"""EMI due-date schedule."""
from datetime import date, timedelta


def due_dates(first_due: date, months: int) -> list[date]:
    """Due dates for an EMI: the same day of the month as first_due, every month.
    If a month is too short (e.g. the 31st in February), use that month's last day."""
    return [first_due + timedelta(days=30 * i) for i in range(months)]


def is_late(first_due: date, months: int, paid_on: date, instalment: int) -> bool:
    """instalment is 1-based."""
    return paid_on > due_dates(first_due, months)[instalment - 1]
