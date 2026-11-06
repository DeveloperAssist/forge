"""Money formatting for Indian users. Amounts are int paise."""


def format_inr(paise: int) -> str:
    """Format paise as rupees with Indian digit grouping (lakh, crore):
    12345678 -> '₹1,23,456.78'."""
    sign = "-" if paise < 0 else ""
    rupees, p = divmod(abs(paise), 100)
    digits = str(rupees)
    if len(digits) > 3:
        head, tail = digits[:-3], digits[-3:]
        groups = []
        while len(head) > 2:
            groups.insert(0, head[-2:])
            head = head[:-2]
        if head:
            groups.insert(0, head)
        digits = ",".join(groups) + "," + tail
    return f"{sign}₹{digits}.{p:02d}"
