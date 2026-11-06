import pytest

import gstin
from invoice import make_invoice

PUNE = "27ABCDE1234F1Z5"
MUMBAI = "27LMNOP4321Q1Z9"
BENGALURU = "29PQRST5678K1Z2"
DELHI = "07AAACD1111E1Z1"
NOIDA = "09AAACN2222F1Z3"
RANCHI = "20AAACR3333G1Z5"
PATNA = "10AAACP4444H1Z7"


def test_inter_state_igst():
    inv = make_invoice(PUNE, BENGALURU, [("Laptop bag", 149900, 18), ("Notebook", 5000, 12)])
    assert inv["intra_state"] is False
    t = inv["totals"]
    assert t["cgst"] == 0 and t["sgst"] == 0
    assert t["igst"] == 26982 + 600
    assert t["grand_total"] == 154900 + 27582


@pytest.mark.parametrize(
    "a,b,intra",
    [(PUNE, MUMBAI, True), (PUNE, BENGALURU, False), (DELHI, NOIDA, False), (NOIDA, NOIDA, True),
     (RANCHI, PATNA, False), (BENGALURU, " 29zzzzz9999z1z1 ", True)],
)
def test_same_state(a, b, intra):
    assert gstin.same_state(a, b) is intra
    assert make_invoice(a, b, [("x", 1000, 5)])["intra_state"] is intra


def test_state_code():
    assert gstin.state_code(BENGALURU) == "29"
    assert gstin.state_code(DELHI) == "07"


def test_bad_length():
    with pytest.raises(ValueError):
        gstin.state_code("27ABC")
