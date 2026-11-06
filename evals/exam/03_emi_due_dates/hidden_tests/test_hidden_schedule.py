from datetime import date

import emi_schedule as es


def test_fifth_for_a_year():
    got = es.due_dates(date(2027, 1, 5), 12)
    assert got == [date(2027, m, 5) for m in range(1, 13)]


def test_month_end_clamps_but_does_not_drift():
    assert es.due_dates(date(2027, 1, 31), 4) == [
        date(2027, 1, 31), date(2027, 2, 28), date(2027, 3, 31), date(2027, 4, 30)]


def test_year_rollover_and_leap_year():
    assert es.due_dates(date(2027, 11, 30), 4) == [
        date(2027, 11, 30), date(2027, 12, 30), date(2028, 1, 30), date(2028, 2, 29)]


def test_long_schedule():
    got = es.due_dates(date(2026, 8, 29), 24)
    assert len(got) == 24
    assert got[6] == date(2027, 2, 28)
    assert got[18] == date(2028, 2, 29)
    assert got[23] == date(2028, 7, 29)


def test_is_late():
    assert es.is_late(date(2027, 1, 31), 3, date(2027, 3, 31), 3) is False
    assert es.is_late(date(2027, 1, 31), 3, date(2027, 4, 1), 3) is True
    assert es.is_late(date(2027, 1, 31), 3, date(2027, 3, 1), 2) is True
