"""Fee receipt text for a student."""
from fees import hostel_fee


def make_receipt(name: str, room_type: str, n: int, ac: bool = False) -> str:
    amount = hostel_fee(room_type, n, ac=ac)
    ac_text = " AC" if ac else ""
    return "\n".join([
        "HOSTEL FEE RECEIPT",
        f"Name   : {name}",
        f"Room   : {room_type}{ac_text} x {n} months",
        f"Amount : Rs {amount:,}",
    ])
