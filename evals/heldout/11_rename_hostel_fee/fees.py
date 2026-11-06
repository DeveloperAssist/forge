"""Hostel fee rules (sample rates, not any real college's)."""

MONTHLY_RENT = {"single": 6000, "double": 4500, "triple": 3500}  # rupees
AC_EXTRA = 1500          # per month
MESS_PER_MONTH = 3200
CAUTION_DEPOSIT = 5000   # once, refundable


def calc(room_type: str, n: int, ac: bool = False, mess: bool = True) -> int:
    """Total rupees for `n` months in a room of `room_type`."""
    if room_type not in MONTHLY_RENT:
        raise ValueError(f"unknown room type {room_type!r}")
    if n <= 0:
        raise ValueError("months must be positive")
    per_month = MONTHLY_RENT[room_type] + (AC_EXTRA if ac else 0) + (MESS_PER_MONTH if mess else 0)
    total = per_month * n
    if n >= 10:
        total -= per_month  # one month free for a full-year booking
    return total + CAUTION_DEPOSIT
