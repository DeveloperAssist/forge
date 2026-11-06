"""Create UPI payment requests. Amounts are in paise."""

UPI_LIMIT_PAISE = 1_00_000 * 100  # ₹1 lakh per transaction


def create_payment(vpa: str, amount_paise: int, note: str = "") -> dict:
    name, at, bank = vpa.partition("@")
    if not at or not name or not bank or "@" in bank or any(c.isspace() for c in vpa):
        raise ValueError(f"invalid UPI ID: {vpa!r}")
    if amount_paise <= 0:
        raise ValueError("amount must be positive")
    if amount_paise > UPI_LIMIT_PAISE:
        raise ValueError("amount is above the UPI limit")
    return {"vpa": vpa, "amount_paise": amount_paise, "note": note, "status": "PENDING"}


def upi_link(payment: dict) -> str:
    rupees = payment["amount_paise"] / 100
    return f"upi://pay?pa={payment['vpa']}&am={rupees:.2f}&tn={payment['note']}"
