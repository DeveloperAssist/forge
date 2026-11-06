import pytest

from wallet import Wallet


@pytest.mark.parametrize("pay,cashback", [(50000, 500), (24900, 249), (19999, 199), (150, 1), (99, 0),
                                          (99999, 999)])
def test_one_percent(pay, cashback):
    w = Wallet("Aman", 1_000_000)
    w.pay(pay)
    assert w.cashback_earned() == cashback
    assert w.balance == 1_000_000 - pay + cashback
    assert [k for k, _ in w.history].count("cashback") == (1 if cashback else 0)


def test_monthly_cap_exact():
    w = Wallet("Priya", 10_000_000)
    for _ in range(9):
        w.pay(50000)
    assert w.cashback_earned() == 4500
    w.pay(80000)  # would be 800, only 500 of room left
    assert w.cashback_earned() == 5000
    w.pay(50000)
    assert w.cashback_earned() == 5000


def test_receive_and_pay_mix():
    w = Wallet("Rohit")
    w.receive(200000)
    w.pay(120000)
    w.receive(10000)
    assert w.cashback_earned() == 1200
    assert w.balance == 200000 - 120000 + 1200 + 10000
