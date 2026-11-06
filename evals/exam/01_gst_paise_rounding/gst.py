"""GST helpers for shop bills. All money is in paise (int)."""


def gst_amount(amount_paise: int, rate_percent: int) -> int:
    """GST on an amount, rounded to the nearest paisa (half a paisa rounds up)."""
    return amount_paise * rate_percent // 100


def bill_total(lines: list[tuple[int, int]]) -> int:
    """lines = [(amount_paise, rate_percent), ...]; returns amount + GST for every line."""
    total = 0
    for amount, rate in lines:
        total += amount + gst_amount(amount, rate)
    return total
