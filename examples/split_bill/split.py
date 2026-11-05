"""Split a restaurant bill between friends, the way a UPI group-pay app does."""


def split_bill(total: float, people: int, tip_percent: float = 0) -> list[float]:
    """Return what each person pays, in rupees, rounded to paise. The shares must add up to the total."""
    with_tip = total + total * tip_percent / 100
    share = round(with_tip / people, 2)
    return [share] * people


def who_owes(paid: dict[str, float], total: float) -> dict[str, float]:
    """How much each friend still owes (negative = they get money back)."""
    share = total / len(paid)
    return {name: round(share - amount, 2) for name, amount in paid.items()}
