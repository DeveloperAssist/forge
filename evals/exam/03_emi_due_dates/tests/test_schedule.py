from datetime import date

from emi_schedule import due_dates


def test_first_date_is_start():
    assert due_dates(date(2027, 1, 5), 1) == [date(2027, 1, 5)]


def test_same_day_each_month():
    assert due_dates(date(2027, 1, 5), 3) == [date(2027, 1, 5), date(2027, 2, 5), date(2027, 3, 5)]
