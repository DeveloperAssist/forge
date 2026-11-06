"""Zomato-style order total. All money in paise."""

DELIVERY_FEE = 4000          # ₹40
FREE_DELIVERY_ABOVE = 19900  # food subtotal of ₹199 or more -> free delivery
PLATFORM_FEE = 500           # ₹5


def subtotal(items):
    """items: list of (name, price_paise, qty)"""
    return sum(price * qty for _, price, qty in items)


def order_total(items):
    sub = subtotal(items)
    delivery = 0 if sub >= FREE_DELIVERY_ABOVE else DELIVERY_FEE
    return sub + delivery + PLATFORM_FEE
