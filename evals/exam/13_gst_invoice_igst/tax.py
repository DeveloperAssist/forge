"""GST maths. Money in paise."""


def gst(amount_paise: int, rate_percent: int) -> int:
    return (amount_paise * rate_percent + 50) // 100


def split_tax(amount_paise: int, rate_percent: int, intra_state: bool) -> dict:
    """Intra-state: half CGST + half SGST. Inter-state: all IGST."""
    tax = gst(amount_paise, rate_percent)
    if intra_state:
        cgst = tax // 2
        return {"cgst": cgst, "sgst": tax - cgst, "igst": 0}
    return {"cgst": 0, "sgst": 0, "igst": tax}
