from pathlib import Path

from orders import load_orders

CSV = Path(__file__).resolve().parent.parent / "orders.csv"


def test_load():
    orders = load_orders(CSV)
    assert len(orders) == 5
    assert orders[0]["restaurant"] == "Behrouz Biryani"
