"""Split a group bill (trip, mess, Zomato order) between friends. Money in paise."""


def split_equal(total_paise, people):
    if not isinstance(total_paise, int):
        raise TypeError("amount must be in paise (int)")
    if total_paise <= 0:
        raise ValueError("amount must be positive")
    if people <= 0:
        raise ValueError("need at least one person")
    base, extra = divmod(total_paise, people)
    return [base + 1 if i < extra else base for i in range(people)]


def split_by_shares(total_paise, shares):
    """shares: list of ints, e.g. [2, 1, 1] -> the first person pays half."""
    if not isinstance(total_paise, int):
        raise TypeError("amount must be in paise (int)")
    if total_paise <= 0:
        raise ValueError("amount must be positive")
    if not shares or any(s <= 0 for s in shares):
        raise ValueError("shares must be positive")
    whole = sum(shares)
    parts = [total_paise * s // whole for s in shares]
    for i in range(total_paise - sum(parts)):
        parts[i] += 1
    return parts


def split_custom(total_paise, amounts):
    if not isinstance(total_paise, int):
        raise TypeError("amount must be in paise (int)")
    if total_paise <= 0:
        raise ValueError("amount must be positive")
    if sum(amounts) != total_paise:
        raise ValueError(f"amounts add up to {sum(amounts)}, not {total_paise}")
    return list(amounts)
