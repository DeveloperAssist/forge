import subprocess
import sys
from pathlib import Path

from orders import load_orders, spent_per_restaurant, total_spent

ROOT = Path(__file__).resolve().parent.parent


def test_total():
    assert total_spent(load_orders(ROOT / "orders.csv")) == 157000


def test_per_restaurant():
    assert spent_per_restaurant(load_orders(ROOT / "orders.csv")) == {
        "Behrouz Biryani": 54700, "Domino's": 91800, "Chai Point": 10500}


def test_other_csv(tmp_path):
    p = tmp_path / "o.csv"
    p.write_text("order_id,restaurant,item,price_paise,qty\n1,Haldiram's,Thali,25000,3\n2,Haldiram's,Lassi,8000, 1\n",
                 encoding="utf-8")
    orders = load_orders(p)
    assert total_spent(orders) == 83000
    assert spent_per_restaurant(orders) == {"Haldiram's": 83000}


def test_report_runs():
    out = subprocess.run([sys.executable, "report.py"], cwd=ROOT, capture_output=True, text=True,
                         encoding="utf-8", env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
    assert out.returncode == 0, out.stderr
    assert "Total: ₹1,570.00" in out.stdout
