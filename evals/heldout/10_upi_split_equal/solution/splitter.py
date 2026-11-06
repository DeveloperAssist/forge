"""Bill splitting for UPI collect requests. Money is in paise (int)."""


def rupees(paise: int) -> str:
    """12345 -> 'Rs 123.45'."""
    sign = "-" if paise < 0 else ""
    paise = abs(paise)
    return f"{sign}Rs {paise // 100}.{paise % 100:02d}"


def who_owes(paid_by: str, shares: dict[str, int]) -> list[tuple[str, str, int]]:
    """Everyone except the payer owes the payer their share: [(from, to, paise), ...]."""
    return [(name, paid_by, amount) for name, amount in shares.items() if name != paid_by and amount > 0]


def request_lines(paid_by: str, shares: dict[str, int]) -> list[str]:
    """Text for each UPI collect request."""
    return [f"{debtor} -> {creditor}: {rupees(amount)}" for debtor, creditor, amount in who_owes(paid_by, shares)]


def total_due(paid_by: str, shares: dict[str, int]) -> int:
    """Paise the payer will get back once every request is paid."""
    return sum(amount for _debtor, _creditor, amount in who_owes(paid_by, shares))


def split_equal(total_paise: int, names: list[str]) -> dict[str, int]:
    """Split `total_paise` equally; leftover paise go to the first names."""
    if not names:
        raise ValueError("need at least one person")
    if len(set(names)) != len(names):
        raise ValueError("duplicate name")
    if total_paise < 0:
        raise ValueError("total cannot be negative")
    base, extra = divmod(total_paise, len(names))
    return {name: base + (1 if i < extra else 0) for i, name in enumerate(names)}
