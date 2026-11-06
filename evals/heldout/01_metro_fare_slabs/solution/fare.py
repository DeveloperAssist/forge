"""Metro fare calculator (sample fare chart, not an official one)."""

# (upper limit in km, fare in rupees)
SLABS = [
    (2, 10),
    (5, 20),
    (12, 30),
    (21, 40),
    (32, 50),
]
MAX_FARE = 60
CARD_DISCOUNT_PERCENT = 10


def fare(km: float) -> int:
    """Token fare in rupees for a ride of `km` kilometres."""
    if km <= 0:
        raise ValueError("distance must be positive")
    for limit, price in SLABS:
        if km <= limit:
            return price
    return MAX_FARE


def card_fare(km: float) -> int:
    """Smart-card fare: 10% off the token fare, rounded down to a rupee."""
    return fare(km) * (100 - CARD_DISCOUNT_PERCENT) // 100


def day_total(rides: list[float], card: bool = False) -> int:
    """Total for a day of rides."""
    pay = card_fare if card else fare
    return sum(pay(km) for km in rides)
