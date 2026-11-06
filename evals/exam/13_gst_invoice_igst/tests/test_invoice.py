from invoice import make_invoice

PUNE = "27ABCDE1234F1Z5"
MUMBAI = "27LMNOP4321Q1Z9"


def test_same_state():
    inv = make_invoice(PUNE, MUMBAI, [("Laptop bag", 149900, 18)])
    assert inv["intra_state"] is True
    assert inv["totals"]["cgst"] == 13491
    assert inv["totals"]["sgst"] == 13491
    assert inv["totals"]["grand_total"] == 176882
