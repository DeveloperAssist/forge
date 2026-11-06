"""Zomato order history from the CSV export. Money in paise."""
import csv


def load_orders(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def order_amount(order):
    return int(order["price_paise"]) * int(order["qty"])


def total_spent(orders):
    return sum(order_amount(o) for o in orders)


def spent_per_restaurant(orders):
    out = {}
    for o in orders:
        out[o["restaurant"]] = out.get(o["restaurant"], 0) + order_amount(o)
    return out
