from pincode import is_valid_pin


def test_normal_pin():
    assert is_valid_pin("834001")


def test_all_zero_rejected():
    assert not is_valid_pin("000000")
