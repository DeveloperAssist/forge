"""Cashback offer: 1% back on payments, at most ₹50 a month. Money in paise."""

CASHBACK_PERCENT = 1
MONTHLY_CAP_PAISE = 5000   # ₹50
MIN_TXN_PAISE = 100        # transactions under ₹1 earn nothing


def cashback_for(paise: int) -> int:
    return paise * CASHBACK_PERCENT // 100


def on_transaction(wallet, kind: str, paise: int) -> None:
    """Called by the wallet after every transaction it records."""
    if kind != "pay":  # only payments earn cashback (not money received, not cashback itself)
        return
    if paise < MIN_TXN_PAISE:
        return
    room = MONTHLY_CAP_PAISE - wallet.cashback_earned()
    amount = min(cashback_for(paise), room)
    if amount > 0:
        wallet.credit_cashback(amount)
