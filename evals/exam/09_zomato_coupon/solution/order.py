"""Zomato-style order total. All money in paise."""

DELIVERY_FEE = 4000          # ₹40
FREE_DELIVERY_ABOVE = 19900  # food subtotal of ₹199 or more -> free delivery
PLATFORM_FEE = 500           # ₹5


def subtotal(items):
    """items: list of (name, price_paise, qty)"""
    return sum(price * qty for _, price, qty in items)


def discount(sub, coupon):
    if coupon is None:
        return 0
    code = coupon.strip().upper()
    if code == "FLAT100":
        if sub < 49900:
            raise ValueError("FLAT100 needs a subtotal of at least ₹499")
        return 10000
    if code == "SAVE20":
        return min(sub * 20 // 100, 12000)
    raise ValueError(f"unknown coupon: {coupon}")


def order_total(items, coupon=None):
    sub = subtotal(items)
    delivery = 0 if sub >= FREE_DELIVERY_ABOVE else DELIVERY_FEE
    return sub - discount(sub, coupon) + delivery + PLATFORM_FEE
