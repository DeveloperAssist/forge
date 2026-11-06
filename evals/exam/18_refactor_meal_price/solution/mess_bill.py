"""Hostel mess billing. Prices in paise."""

PRICES = {"breakfast": 3000, "lunch": 6000, "snacks": 2000, "dinner": 6000}
GUEST_MARKUP_PERCENT = 50
SUNDAY_SPECIAL_EXTRA = 2500  # Sunday dinner is a special thali


def meal_price(meal, day, guest=False):
    if meal not in PRICES:
        raise ValueError(f"unknown meal: {meal}")
    price = PRICES[meal]
    if meal == "dinner" and day == "Sun":
        price += SUNDAY_SPECIAL_EXTRA
    if guest:
        price = price + price * GUEST_MARKUP_PERCENT // 100
    return price


def student_bill(meals):
    """meals: list of (meal, day), e.g. ("dinner", "Sun")."""
    return sum(meal_price(meal, day) for meal, day in meals)


def guest_bill(meals):
    """Same as student_bill, but guests pay a markup on every meal."""
    return sum(meal_price(meal, day, guest=True) for meal, day in meals)
