"""Print my Zomato spend summary."""
from pathlib import Path

from orders import load_orders, spent_per_restaurant, total_spent


def main():
    orders = load_orders(Path(__file__).with_name("orders.csv"))
    print(f"Total: ₹{total_spent(orders) / 100:,.2f}")
    for name, paise in sorted(spent_per_restaurant(orders).items()):
        print(f"  {name}: ₹{paise / 100:,.2f}")


if __name__ == "__main__":
    main()
