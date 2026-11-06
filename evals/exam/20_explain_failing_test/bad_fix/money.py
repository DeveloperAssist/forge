"""Money formatting for Indian users. Amounts are int paise."""


def format_inr(paise: int) -> str:
    """Format paise as rupees with digit grouping."""
    sign = "-" if paise < 0 else ""
    rupees, p = divmod(abs(paise), 100)
    return f"{sign}₹{rupees:,}.{p:02d}"
