from fees import calc


def test_double_six_months():
    assert calc("double", 6) == (4500 + 3200) * 6 + 5000


def test_full_year_one_month_free():
    assert calc("single", 10, ac=True) == (6000 + 1500 + 3200) * 9 + 5000
