"""Create UPI payment requests. Amounts are in paise."""

UPI_LIMIT_PAISE = 1_00_000 * 100  # ₹1 lakh per transaction


def create_payment(vpa: str, amount_paise: int, note: str = "") -> dict:
    return {"vpa": vpa, "amount_paise": amount_paise, "note": note, "status": "PENDING"}


def upi_link(payment: dict) -> str:
    rupees = payment["amount_paise"] / 100
    return f"upi://pay?pa={payment['vpa']}&am={rupees:.2f}&tn={payment['note']}"
