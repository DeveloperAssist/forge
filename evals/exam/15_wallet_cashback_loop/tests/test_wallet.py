from wallet import Wallet


def test_receive_no_cashback():
    w = Wallet("Aman")
    w.receive(100000)
    assert w.balance == 100000
    assert w.cashback_earned() == 0


def test_pay_500():
    w = Wallet("Aman", 100000)
    w.pay(50000)
    assert w.cashback_earned() == 500
