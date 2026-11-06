from emi import calc_emi, total_interest


def test_zero_rate():
    assert calc_emi(1200000, 0, 12) == 100000


def test_education_loan():
    assert calc_emi(50000000, 10.5, 36) == 1625122


def test_interest():
    assert total_interest(1200000, 0, 12) == 0
