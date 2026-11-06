"""EMI due-date schedule."""
import calendar
from datetime import date


def _shift(first_due: date, n: int) -> date:
    y, m = divmod(first_due.month - 1 + n, 12)
    year, month = first_due.year + y, m + 1
    last = calendar.monthrange(year, month)[1]
    return date(year, month, min(first_due.day, last))


def due_dates(first_due: date, months: int) -> list[date]:
    """Due dates for an EMI: the same day of the month as first_due, every month.
    If a month is too short (e.g. the 31st in February), use that month's last day."""
    return [_shift(first_due, i) for i in range(months)]


def is_late(first_due: date, months: int, paid_on: date, instalment: int) -> bool:
    """instalment is 1-based."""
    return paid_on > due_dates(first_due, months)[instalment - 1]
