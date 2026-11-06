import mess


def test_bills_are_independent():
    a = mess.MessBill("Aman")
    p = mess.MessBill("Priya")
    a.add_extra("paneer", 6000)
    assert p.extras == []
    assert p.total() == 350000
    assert a.total() == 356000


def test_bills_for_independent():
    bills = mess.bills_for(["Aman", "Priya", "Rohit"])
    bills["Aman"].add_extra("egg", 1500)
    bills["Rohit"].add_extra("lassi", 3000)
    assert bills["Priya"].total() == 350000
    assert bills["Aman"].total() == 351500
    assert bills["Rohit"].total() == 353000


def test_fresh_bill_after_others_used():
    for _ in range(3):
        b = mess.MessBill("x")
        b.add_extra("maggi", 2500)
    assert mess.MessBill("y").total(base_paise=0) == 0


def test_explicit_extras_still_work():
    b = mess.MessBill("Neha", [("curd", 1000)])
    b.add_extra("sweet", 2000)
    assert b.total(base_paise=100000) == 103000
