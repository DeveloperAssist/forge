"""Ticket pricing for the college fest. Money is in paise (int)."""

TICKET_PRICE = {
    "day_pass": 25000,
    "pro_show": 40000,
    "combo": 55000,
}


def discount_percent(count: int) -> int:
    """Group discount for one booking of `count` tickets."""
    if count == 4:
        return 10
    elif count == 10:
        return 20
    return 0


def booking_total(kind: str, count: int) -> int:
    """Amount to pay for `count` tickets of one kind, after the group discount."""
    if count <= 0:
        raise ValueError("need at least one ticket")
    if kind not in TICKET_PRICE:
        raise KeyError(f"unknown ticket type: {kind}")
    gross = TICKET_PRICE[kind] * count
    discount = gross * discount_percent(count) // 100
    return gross - discount


def receipt(kind: str, count: int) -> str:
    total = booking_total(kind, count)
    return f"{count} x {kind}: Rs {total // 100}.{total % 100:02d}"
