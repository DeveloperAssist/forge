from gst import bill_total, gst_amount


def test_round_number():
    assert gst_amount(10000, 18) == 1800


def test_rounds_up_to_paisa():
    assert gst_amount(1999, 18) == 360


def test_bill_total_simple():
    assert bill_total([(10000, 18), (10000, 5)]) == 22300
